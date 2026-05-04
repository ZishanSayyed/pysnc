from django.db import models
from django.conf import settings


DAY_CHOICES = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
]

SESSION_TYPE_CHOICES = [
    ("daily", "Daily"),
    ("subject", "Subject"),
]

EVENT_TYPE_CHOICES = [
    ("holiday", "Holiday"),
    ("exam", "Exam"),
    ("event", "Event"),
    ("announcement", "Announcement"),
]

SCOPE_CHOICES = [
    ("school", "School-wide"),
    ("class", "Class-level"),
]


class TimeSlot(models.Model):
    school = models.ForeignKey(
        "schools.School", on_delete=models.CASCADE, related_name="time_slots"
    )
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_number = models.PositiveIntegerField()
    is_break = models.BooleanField(default=False)

    class Meta:
        ordering = ["slot_number"]
        unique_together = ("school", "slot_number")

    def __str__(self):
        return f"{self.name} ({self.start_time}–{self.end_time})"


class TimetableEntry(models.Model):
    school = models.ForeignKey(
        "schools.School", on_delete=models.CASCADE, related_name="timetable_entries"
    )
    class_obj = models.ForeignKey(
        "classes.Class", on_delete=models.CASCADE, related_name="timetable_entries"
    )
    subject = models.ForeignKey(
        "teachers.Subject", on_delete=models.CASCADE, related_name="timetable_entries"
    )
    teacher = models.ForeignKey(
        "teachers.Teacher", on_delete=models.CASCADE, related_name="timetable_entries"
    )
    time_slot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, related_name="entries"
    )
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    room = models.CharField(max_length=100, blank=True, null=True)
    academic_year = models.CharField(max_length=20)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("school", "class_obj", "time_slot", "day_of_week", "academic_year")

    def __str__(self):
        return f"{self.class_obj} | {self.day_of_week} | {self.time_slot}"


class TimetableSubstitution(models.Model):
    timetable_entry = models.ForeignKey(
        TimetableEntry, on_delete=models.CASCADE, related_name="substitutions"
    )
    date = models.DateField()
    substitute_teacher = models.ForeignKey(
        "teachers.Teacher", on_delete=models.CASCADE, related_name="substitutions"
    )
    reason = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("timetable_entry", "date")

    def __str__(self):
        return f"Sub on {self.date} for {self.timetable_entry}"


class CalendarEvent(models.Model):
    school = models.ForeignKey(
        "schools.School", on_delete=models.CASCADE, related_name="calendar_events"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default="school")
    class_obj = models.ForeignKey(
        "classes.Class",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="calendar_events",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    academic_year = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date", "start_time"]

    def __str__(self):
        return f"{self.title} ({self.event_type}) — {self.start_date}"
