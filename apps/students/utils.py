"""
students/utils.py
-----------------
CSV bulk-student import with optional parent linking.

If parent columns are present in the CSV, for each row this will:
  1. Find or create the parent SchoolUser
  2. Find or create the Parent profile
  3. Link Student.parent → Parent
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

# Optional parent columns — all must be present together if any one is used
PARENT_COLUMNS = [
    'parent_email', 'parent_first_name', 'parent_last_name', 'parent_phone'
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

    # Detect if parent columns are included in this CSV
    has_parent_data = all(c in df.columns for c in PARENT_COLUMNS)

    created = updated = errors = 0
    error_rows = []

    # Cache existing users and students for performance
    existing_users    = {u.email: u for u in User.objects.filter(school=school)}
    existing_students = {s.student_id: s for s in Student.objects.filter(school=school)}

    for idx, row in df.iterrows():
        try:
            email      = str(row['email']).strip().lower()
            student_id = str(row['student_id']).strip()

            if not email:
                raise ValueError("Student email is required")
            if not student_id:
                raise ValueError("student_id is required")

            # ── STUDENT USER upsert ──────────────────────────────────────
            user = existing_users.get(email)
            if user:
                user.first_name = str(row['first_name']).strip()
                user.last_name  = str(row['last_name']).strip()
                user.role       = 'student'
                user.save()
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
                user.save()
                existing_users[email] = user

            # ── PARENT upsert (if parent columns present) ────────────────
            parent_obj = None
            if has_parent_data:
                parent_email = str(row.get('parent_email', '') or '').strip().lower()
                if parent_email:
                    parent_obj = _upsert_parent(
                        school=school,
                        email=parent_email,
                        first_name=str(row.get('parent_first_name', '') or '').strip(),
                        last_name=str(row.get('parent_last_name', '') or '').strip(),
                        phone=str(row.get('parent_phone', '') or '').strip(),
                        relationship=str(row.get('parent_relationship', '') or 'guardian').strip(),
                        occupation=str(row.get('parent_occupation', '') or '').strip() or None,
                        existing_users=existing_users,
                    )

            # ── STUDENT upsert ───────────────────────────────────────────
            student = (
                existing_students.get(student_id)
                or Student.objects.filter(user=user, school=school).first()
            )

            dob            = _parse_date(row['date_of_birth'])
            admission_date = _parse_date(row['admission_date'])

            if student:
                student.student_id        = student_id
                student.user              = user
                student.date_of_birth     = dob
                student.gender            = str(row['gender']).strip()
                student.address           = str(row['address']).strip()
                student.admission_date    = admission_date
                student.blood_group       = str(row.get('blood_group', '') or '').strip() or None
                student.emergency_contact = str(row.get('emergency_contact', '') or '').strip()
                if parent_obj:
                    student.parent = parent_obj
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
                    parent=parent_obj,
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


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _upsert_parent(school, email, first_name, last_name, phone,
                   relationship, occupation, existing_users):
    """
    Find or create the parent SchoolUser + Parent profile.
    Returns the Parent instance.
    """
    from apps.parents.models import Parent

    # User upsert
    user = existing_users.get(email)
    if user:
        user.first_name = first_name
        user.last_name  = last_name
        user.role       = 'parent'
        user.save()
    else:
        user = User.objects.create(
            email=email,
            username=email,
            first_name=first_name,
            last_name=last_name,
            role='parent',
            school=school,
        )
        user.set_password('default123')
        user.save()
        existing_users[email] = user

    # Parent profile upsert
    parent, _ = Parent.objects.update_or_create(
        user=user,
        defaults={
            'school':       school,
            'phone':        phone,
            'relationship': relationship or 'guardian',
            'occupation':   occupation,
        }
    )
    return parent


def _parse_date(value):
    if pd.isna(value):
        return None
    try:
        return datetime.datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except ValueError:
        return None