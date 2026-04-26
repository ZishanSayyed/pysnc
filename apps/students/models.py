from django.db import models
from apps.schools.models import School
from apps.schools.managers import SchoolManager
from apps.accounts.models import SchoolUser


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    user   = models.OneToOneField(SchoolUser, on_delete=models.CASCADE, related_name='student_profile')

    student_id = models.CharField(max_length=20)

    date_of_birth  = models.DateField(null=True, blank=True)
    gender         = models.CharField(max_length=10, blank=True, default='')
    blood_group    = models.CharField(max_length=5, null=True, blank=True)

    address        = models.TextField(blank=True, default='')
    admission_date = models.DateField(null=True, blank=True)

    current_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    parent = models.ForeignKey(
        'parents.Parent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Made optional so bulk/signal creation works without full data
    emergency_contact = models.CharField(max_length=20, blank=True, default='')

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SchoolManager()

    class Meta:
        unique_together = [['school', 'student_id']]

    def __str__(self):
        return f'{self.student_id} - {self.user.get_full_name()}'

    def compute_attendance_pct(self):
        return 0
