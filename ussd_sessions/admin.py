from django.contrib import admin
from .models import USSDSession

@admin.register(USSDSession)
class USSDSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'phone_number', 'preferred_language', 'current_institution', 'current_service', 'is_completed', 'created_at', 'updated_at')
    list_filter = ('is_completed', 'preferred_language', 'current_institution', 'created_at')
    search_fields = ('session_id', 'phone_number')
    readonly_fields = ('session_id', 'phone_number', 'created_at', 'updated_at')
