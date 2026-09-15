from django.contrib import admin
from .models import Organization, Department, Zone

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("commercial_name", "legal_name", "contact_email", "tax_id", "is_active")
    search_fields = ("commercial_name", "legal_name", "tax_id")
    list_filter = ("is_active",)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "jefatura", "is_active")
    search_fields = ("name", "organization__commercial_name")
    list_filter = ("organization", "is_active")
    list_select_related = ("organization", "jefatura")

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "is_active")
    search_fields = ("name", "department__name")
    list_filter = ("department", "is_active")
    list_select_related = ("department",)
