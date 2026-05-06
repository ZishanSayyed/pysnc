from django.db import models
from apps.schools.models import School
from apps.students.models import Student
from apps.classes.models import Class
from apps.teachers.models import Subject


class Exam(models.Model):
    """
    An exam event for a school — e.g. 'Mid-Term 2025', 'Final Exam 2025'
    """
    EXAM_TYPE_CHOICES = [
        ("unit_test", "Unit Test"),
        ("mid_term", "Mid Term"),
        ("final", "Final Exam"),
        ("assignment", "Assignment"),
        ("practical", "Practical"),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exams")
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default="mid_term")
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="exams")
    total_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=35)
    exam_date = models.DateField(null=True, blank=True)
    academic_year = models.CharField(max_length=10, blank=True)
    is_published = models.BooleanField(default=False)  # results visible to students/parents
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-exam_date"]

    def __str__(self):
        return f"{self.name} — {self.class_obj}"


class ExamSubject(models.Model):
    """
    A subject within an exam with its own max marks.
    e.g. Mid-Term → Math (50 marks), English (50 marks)
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exam_subjects")
    max_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=35)

    class Meta:
        unique_together = ("exam", "subject")

    def __str__(self):
        return f"{self.exam.name} — {self.subject.name}"


class StudentResult(models.Model):
    """
    Marks scored by a student in one subject of one exam.
    """
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("exam_subject", "student")

    def __str__(self):
        return f"{self.student} — {self.exam_subject}"

    @property
    def grade(self):
        if self.is_absent or self.marks_obtained is None:
            return "AB"
        pct = (self.marks_obtained / self.exam_subject.max_marks) * 100
        if pct >= 90: return "A+"
        if pct >= 75: return "A"
        if pct >= 60: return "B"
        if pct >= 45: return "C"
        if pct >= 35: return "D"
        return "F"

    @property
    def is_pass(self):
        if self.is_absent or self.marks_obtained is None:
            return False
        return self.marks_obtained >= self.exam_subject.passing_marks
