"""
students/utils.py
-----------------
CSV bulk-student import.

Each CSV row upserts a SchoolUser (role=student) AND the Student profile.
Because we call user.save() individually (not bulk_create), the post_save
signal fires and the Student row is created automatically — we then update
it with the real CSV data.
"""

import datetime
import pandas as pd
from django.contrib.auth import get_user_model
from apps.students.models import Student

User = get_user_model()

REQUIRED_COLUMNS = [
    'email', 'first_name', 'last_name',
    'student_id', 'date_of_birth',
    'gender', 'address', 'admission_date',
]


def parse_student_csv(file, school):
    try:
        df = pd.read_csv(file.file, encoding='utf-8')
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

    if df.empty:
        return {'status': 'error', 'message': 'CSV file is empty'}

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return {'status': 'error', 'message': f'Missing columns: {missing}'}

    created = updated = errors = 0
    error_rows = []

    existing_users    = {u.email: u for u in User.objects.filter(school=school)}
    existing_students = {s.student_id: s for s in Student.objects.filter(school=school)}

    for idx, row in df.iterrows():
        try:
            email      = str(row['email']).strip().lower()
            student_id = str(row['student_id']).strip()

            if not email:
                raise ValueError("Email is required")
            if not student_id:
                raise ValueError("student_id is required")

            # ── USER upsert ──────────────────────────────────────────────
            user = existing_users.get(email)
            if user:
                user.first_name = str(row['first_name']).strip()
                user.last_name  = str(row['last_name']).strip()
                user.role       = 'student'
                user.save()          # signal fires → ensures Student row exists
            else:
                user = User.objects.create(
                    email=email,
                    username=email,
                    first_name=str(row['first_name']).strip(),
                    last_name=str(row['last_name']).strip(),
                    role='student',
                    school=school,
                )
                user.set_password('default123')
                user.save()          # signal fires → creates Student placeholder
                existing_users[email] = user

            # ── STUDENT upsert ───────────────────────────────────────────
            # Signal may have already created a placeholder with student_id=STU-<pk>;
            # look up by both the real student_id and the placeholder.
            student = (
                existing_students.get(student_id)
                or Student.objects.filter(user=user, school=school).first()
            )

            dob            = _parse_date(row['date_of_birth'])
            admission_date = _parse_date(row['admission_date'])

            if student:
                student.student_id      = student_id
                student.user            = user
                student.date_of_birth   = dob
                student.gender          = str(row['gender']).strip()
                student.address         = str(row['address']).strip()
                student.admission_date  = admission_date
                student.blood_group     = str(row.get('blood_group', '') or '').strip() or None
                student.emergency_contact = str(row.get('emergency_contact', '') or '').strip()
                student.save()
                existing_students[student_id] = student
                updated += 1
            else:
                student = Student.objects.create(
                    school=school,
                    student_id=student_id,
                    user=user,
                    date_of_birth=dob,
                    gender=str(row['gender']).strip(),
                    address=str(row['address']).strip(),
                    admission_date=admission_date,
                    blood_group=str(row.get('blood_group', '') or '').strip() or None,
                    emergency_contact=str(row.get('emergency_contact', '') or '').strip(),
                )
                existing_students[student_id] = student
                created += 1

        except Exception as e:
            errors += 1
            error_rows.append({
                "row": int(idx),
                "email": row.get('email'),
                "error": str(e),
            })

    return {
        "created": created,
        "updated": updated,
        "errors": errors,
        "error_rows": error_rows,
    }


def _parse_date(value):
    """Parse a date string or return None."""
    if pd.isna(value):
        return None
    try:
        return datetime.datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except ValueError:
        return None
