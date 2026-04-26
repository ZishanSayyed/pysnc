from django.db import models
from apps.schools.models import School
from apps.accounts.models import SchoolUser
from apps.schools.managers import SchoolManager


class Subject(models.Model):
    """
    Global subject catalogue (e.g. Mathematics, English).
    Schools share subjects; assignments link teacher ↔ school ↔ subject.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """
    Teacher profile.  One SchoolUser → one Teacher profile.
    A teacher can be assigned to MANY schools and MANY subjects via
    TeacherSchoolAssignment.
    """
    user = models.OneToOneField(
        SchoolUser,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    # Primary / home school – kept for backward-compat queries.
    # The real multi-school relationship lives in TeacherSchoolAssignment.
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='teachers'
    )
    employee_id = models.CharField(max_length=30, null=True, blank=True)
    qualification = models.CharField(max_length=200, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SchoolManager()

    class Meta:
        unique_together = [['school', 'employee_id']]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.school.name})"


class TeacherSchoolAssignment(models.Model):
    """
    Allows one teacher to be assigned to multiple schools and multiple
    subjects within each school.

    teacher → school → subject  (all three together must be unique)
    """
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='school_assignments'
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='teacher_assignments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        null=True,
        blank=True
    )
    # Optional: which class this teacher teaches this subject in
    assigned_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_assignments'
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['teacher', 'school', 'subject', 'assigned_class']]
        ordering = ['school', 'subject']

    def __str__(self):
        subj = self.subject.name if self.subject else 'N/A'
        return f"{self.teacher.user.get_full_name()} | {self.school.name} | {subj}"
