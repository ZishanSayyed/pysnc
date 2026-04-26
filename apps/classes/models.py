# Create your models here.
from django.db import models
from apps.schools.models import School

class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name   = models.CharField(max_length=50)

    def __str__(self):
        return self.name