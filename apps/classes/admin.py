from django.contrib import admin
from .models import Class, ClassSubject, StudentSubjectEnrollment


class ClassSubjectInline(admin.TabularInline):
    model = ClassSubject
    extra = 5  # shows 5 empty rows at once


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display  = ['name', 'section', 'school', 'academic_year', 'capacity', 'student_count', 'is_active']
    list_filter   = ['school', 'academic_year', 'is_active']
    search_fields = ['name', 'section']
    inlines       = [ClassSubjectInline]  # add subjects directly from Class page

    def student_count(self, obj): return obj.student_count()
    student_count.short_description = 'Students'


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'subject', 'is_active']
    list_filter  = ['class_obj__school', 'is_active']


@admin.register(StudentSubjectEnrollment)
class StudentSubjectEnrollmentAdmin(admin.ModelAdmin):
    list_display  = ['student', 'subject', 'class_obj', 'is_active']
    list_filter   = ['class_obj__school', 'is_active', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name']