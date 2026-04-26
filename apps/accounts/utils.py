"""
accounts/utils.py
-----------------
CSV bulk-user import.

After bulk_create (which bypasses signals), we explicitly create the
matching Student / Teacher / Parent profile rows so all tables stay in sync.
"""

import csv
from io import TextIOWrapper
from django.contrib.auth import get_user_model

User = get_user_model()


def parse_user_csv(csv_file, school):
    decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
    reader = csv.DictReader(decoded_file)

    users_to_create = []
    errors = []
    success_count = 0

    existing_usernames = set(
        User.objects.filter(school=school).values_list('username', flat=True)
    )

    file_usernames = set()

    for i, row in enumerate(reader, start=1):
        try:
            username = (row.get('username') or '').strip()
            email    = (row.get('email') or '').strip()
            password = (row.get('password') or '').strip()
            role     = (row.get('role') or '').strip()

            if not username or not password:
                raise ValueError("username and password required")

            if username in file_usernames:
                raise ValueError("Duplicate username in file")

            if username in existing_usernames:
                raise ValueError("Username already exists")

            file_usernames.add(username)

            user = User(
                username=username,
                email=email if email else None,
                role=role if role else None,
                school=school,
                first_name=(row.get('first_name') or '').strip(),
                last_name=(row.get('last_name') or '').strip(),
                phone=(row.get('phone') or '').strip() or None,
            )
            user.set_password(password)
            users_to_create.append(user)
            success_count += 1

        except Exception as e:
            errors.append({
                "row": i,
                "username": row.get('username'),
                "error": str(e)
            })

    # bulk_create skips signals, so we call _create_profiles_bulk() manually
    if users_to_create:
        created_users = User.objects.bulk_create(users_to_create, batch_size=500)
        _create_profiles_bulk(created_users, school)

    return {
        "created": success_count,
        "errors": len(errors),
        "error_details": errors
    }


def _create_profiles_bulk(users, school):
    """
    After bulk_create (which bypasses post_save signals), manually create
    Student / Teacher / Parent profile rows for each user that needs one.
    """
    import datetime
    from apps.students.models import Student
    from apps.teachers.models import Teacher
    from apps.parents.models import Parent

    students_to_create = []
    teachers_to_create = []
    parents_to_create  = []

    for user in users:
        if user.role == 'student':
            students_to_create.append(Student(
                school=school,
                user=user,
                student_id=f"STU-{user.pk}",
                date_of_birth=datetime.date(2000, 1, 1),
                gender='',
                address='',
                admission_date=datetime.date.today(),
                emergency_contact='',
            ))
        elif user.role == 'teacher':
            teachers_to_create.append(Teacher(
                user=user,
                school=school,
            ))
        elif user.role == 'parent':
            parents_to_create.append(Parent(
                school=school,
                user=user,
                phone=user.phone or '',
            ))

    if students_to_create:
        Student.objects.bulk_create(students_to_create, batch_size=500, ignore_conflicts=True)
    if teachers_to_create:
        Teacher.objects.bulk_create(teachers_to_create, batch_size=500, ignore_conflicts=True)
    if parents_to_create:
        Parent.objects.bulk_create(parents_to_create, batch_size=500, ignore_conflicts=True)
