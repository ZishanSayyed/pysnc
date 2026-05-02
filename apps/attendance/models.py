from django.db import models
from apps.schools.models import School
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.classes.models import Class
from apps.teachers.models import Subject


class AttendanceSession(models.Model):
    """
    Represents a single attendance-taking session.
    One session per class per subject per date.
    Teacher marks this session, then records individual student entries.
    """
    SESSION_TYPE_CHOICES = [
        ("daily", "Daily"),
        ("subject", "Subject-wise"),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="attendance_sessions")
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="attendance_sessions")
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name="attendance_sessions")
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name="attendance_sessions")
    date = models.DateField()
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, default="daily")
    is_finalized = models.BooleanField(default=False)  # once finalized, no edits
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # One session per class per subject per date
        unique_together = ("school", "class_obj", "subject", "date")
        ordering = ["-date"]

    def __str__(self):
        subject_name = self.subject.name if self.subject else "Daily"
        return f"{self.class_obj} | {subject_name} | {self.date}"


class AttendanceRecord(models.Model):
    """
    Individual student attendance record for a session.
    """
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="present")
    remarks = models.CharField(max_length=255, blank=True, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("session", "student")
        ordering = ["student__user__first_name"]

    def __str__(self):
        return f"{self.student} — {self.status} on {self.session.date}"
