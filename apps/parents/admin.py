from django.contrib import admin
from .models import Parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'phone', 'relationship', 'is_active']
    list_filter  = ['school', 'relationship', 'is_active']
