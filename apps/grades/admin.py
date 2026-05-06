from django.contrib import admin
from .models import Exam, ExamSubject, StudentResult


class ExamSubjectInline(admin.TabularInline):
    model = ExamSubject
    extra = 0
    fields = ["subject", "max_marks", "passing_marks"]


class StudentResultInline(admin.TabularInline):
    model = StudentResult
    extra = 0
    fields = ["student", "marks_obtained", "is_absent", "remarks"]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["name", "exam_type", "class_obj", "school", "exam_date", "is_published"]
    list_filter = ["exam_type", "is_published", "school"]
    search_fields = ["name"]
    inlines = [ExamSubjectInline]


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ["exam", "subject", "max_marks", "passing_marks"]
    inlines = [StudentResultInline]


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ["student", "exam_subject", "marks_obtained", "is_absent"]
    list_filter = ["is_absent", "exam_subject__exam"]
    search_fields = ["student__user__first_name", "student__student_id"]
