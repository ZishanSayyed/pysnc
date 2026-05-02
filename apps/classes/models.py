from django.db import models
from apps.schools.models import School
from apps.schools.managers import SchoolManager


class Class(models.Model):
    school        = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name          = models.CharField(max_length=50)
    section       = models.CharField(max_length=10, blank=True, default='')
    academic_year = models.CharField(max_length=10, blank=True, default='')
    capacity      = models.PositiveIntegerField(default=40)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True, null=True)

    objects = SchoolManager()

    class Meta:
        unique_together = [['school', 'name', 'section', 'academic_year']]
        ordering = ['name', 'section']

    def __str__(self):
        if self.section:
            return f"{self.name} - {self.section}"
        return self.name

    def student_count(self):
        return self.students.filter(is_active=True).count()


class ClassSubject(models.Model):
    """
    Subjects offered in a class.
    e.g. Class 10 → [Maths I, Maths II, Science I, English ...]
    When a student is assigned to this class they are auto-enrolled
    in ALL active ClassSubjects for that class.
    """
    class_obj  = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject    = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE, related_name='class_subjects')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['class_obj', 'subject']]
        ordering = ['subject__name']

    def __str__(self):
        return f"{self.class_obj} -> {self.subject.name}"


class StudentSubjectEnrollment(models.Model):
    """
    Which subjects a student is enrolled in within their class.
    Auto-created when student is assigned to a class (all class subjects).
    Can be individually toggled on/off later (is_active=False to remove a subject).
    """
    student    = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='subject_enrollments')
    subject    = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE, related_name='student_enrollments')
    class_obj  = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['student', 'subject', 'class_obj']]
        ordering = ['subject__name']

    def __str__(self):
        return f"{self.student} | {self.subject.name} | {self.class_obj}"
