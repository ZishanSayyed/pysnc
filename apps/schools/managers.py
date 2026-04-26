from django.db import models

class SchoolManager(models.Manager):
    def for_school(self, school):
        return self.filter(school=school)