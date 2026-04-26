"""
accounts/signals.py
-------------------
When a SchoolUser is saved with role = 'student' | 'teacher' | 'parent',
automatically create (or ensure) the matching profile record.

This keeps the Student / Teacher / Parent tables always in sync with
the accounts table — no manual double-creation needed.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SchoolUser


@receiver(post_save, sender=SchoolUser)
def create_role_profile(sender, instance, created, **kwargs):
    """
    Fires after every SchoolUser save.
    - On CREATE: build the matching profile if role is known.
    - On UPDATE: if role changed to teacher/student/parent and profile
      doesn't exist yet, create it now.
    """
    if not instance.school:
        return  # platform admins have no school; skip

    role = instance.role

    if role == 'student':
        _ensure_student_profile(instance)
    elif role == 'teacher':
        _ensure_teacher_profile(instance)
    elif role == 'parent':
        _ensure_parent_profile(instance)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _ensure_student_profile(user):
    """Create a minimal Student row if one does not exist."""
    from apps.students.models import Student  # late import avoids circular refs
    import datetime

    if not Student.objects.filter(user=user).exists():
        # Auto-generate a placeholder student_id; management can update later.
        placeholder_id = f"STU-{user.pk}"
        Student.objects.create(
            school=user.school,
            user=user,
            student_id=placeholder_id,
            date_of_birth=datetime.date(2000, 1, 1),   # placeholder
            gender='',
            address='',
            admission_date=datetime.date.today(),
            emergency_contact='',
        )


def _ensure_teacher_profile(user):
    """Create a minimal Teacher row if one does not exist."""
    from apps.teachers.models import Teacher  # late import

    if not Teacher.objects.filter(user=user).exists():
        Teacher.objects.create(
            user=user,
            school=user.school,
        )


def _ensure_parent_profile(user):
    """Create a minimal Parent row if one does not exist."""
    from apps.parents.models import Parent  # late import

    if not Parent.objects.filter(user=user).exists():
        Parent.objects.create(
            school=user.school,
            user=user,
            phone=user.phone or '',
        )
