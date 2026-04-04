from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.schools.models import School

def upload_to_profile(instance, filename):
    return f'schools/{instance.school.id}/profiles/{filename}'

class SchoolUser(AbstractUser):
    ROLE_CHOICES = [
        ('management', 'Management'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, null=True, blank=True)
    global_id = models.CharField(max_length=50, null=True, blank=True)
    profile_photo = models.ImageField(upload_to=upload_to_profile, null=True, blank=True)
    is_platform_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username