from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    fields = ["student", "status", "remarks"]
    readonly_fields = ["marked_at"]


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ["school", "class_obj", "subject", "date", "session_type", "is_finalized", "created_at"]
    list_filter = ["school", "session_type", "is_finalized", "date"]
    search_fields = ["class_obj__name", "subject__name"]
    inlines = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ["session", "student", "status", "marked_at"]
    list_filter = ["status", "session__date"]
    search_fields = ["student__user__first_name", "student__student_id"]
