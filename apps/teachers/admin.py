from django.contrib import admin
from .models import Teacher, Subject, TeacherSchoolAssignment

admin.site.register(Subject)
admin.site.register(TeacherSchoolAssignment)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'employee_id', 'is_active']
    list_filter = ['school', 'is_active']
