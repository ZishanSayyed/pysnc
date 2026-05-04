from django.contrib import admin
from .models import TimeSlot, TimetableEntry, TimetableSubstitution, CalendarEvent


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["school", "slot_number", "name", "start_time", "end_time", "is_break"]
    list_filter = ["school", "is_break"]
    ordering = ["school", "slot_number"]


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ["school", "class_obj", "day_of_week", "time_slot", "subject", "teacher", "room", "academic_year", "is_active"]
    list_filter = ["school", "day_of_week", "academic_year", "is_active"]
    search_fields = ["class_obj__name", "teacher__user__first_name", "subject__name"]


@admin.register(TimetableSubstitution)
class TimetableSubstitutionAdmin(admin.ModelAdmin):
    list_display = ["timetable_entry", "date", "substitute_teacher", "reason", "created_by"]
    list_filter = ["date"]


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "scope", "class_obj", "start_date", "end_date", "academic_year", "is_active"]
    list_filter = ["school", "event_type", "scope", "academic_year", "is_active"]
    search_fields = ["title"]
