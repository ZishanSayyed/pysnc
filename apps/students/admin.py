from django.contrib import admin
from .models import Student
# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'get_full_name',
        'school',
        'current_class',
        'is_active',
        'created_at'
    )

    list_filter = ('school', 'current_class', 'is_active')

    search_fields = (
        'student_id',
        'user__first_name',
        'user__last_name',
        'user__email'
    )

    readonly_fields = ('created_at',)

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = 'Full Name'