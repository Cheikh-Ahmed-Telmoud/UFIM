from django.contrib import admin
from .models import Institution, Service

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'ussd_code', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'ussd_code', 'slug')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'ussd_code', 'is_active')
        }),
        ('API Configuration', {
            'fields': ('api_base_url', 'encrypted_api_credentials'),
            'description': 'Les identifiants d\'accès seront automatiquement chiffrés en base de données.'
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_code', 'institution', 'is_active')
    search_fields = ('name', 'service_code', 'institution__name')
    list_filter = ('is_active', 'institution')
