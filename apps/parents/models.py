from django.db import models
from apps.schools.models import School
from apps.accounts.models import SchoolUser
from apps.schools.managers import SchoolManager


class Parent(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='parents')
    user   = models.OneToOneField(SchoolUser, on_delete=models.CASCADE, related_name='parent_profile')

    phone  = models.CharField(max_length=20, blank=True, default='')
    occupation   = models.CharField(max_length=100, null=True, blank=True)
    relationship = models.CharField(
        max_length=20,
        choices=[('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian')],
        default='guardian',
    )

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SchoolManager()

    def __str__(self):
        return self.user.get_full_name()
