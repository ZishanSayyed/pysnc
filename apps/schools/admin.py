from django.contrib import admin
from .models import School, SchoolSettings


class SchoolSettingsInline(admin.StackedInline):
    model = SchoolSettings
    can_delete = False
    verbose_name_plural = "School Settings"
    extra = 1


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "academic_year", "created_at"]
    inlines = [SchoolSettingsInline]