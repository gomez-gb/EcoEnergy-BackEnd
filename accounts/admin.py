from django.contrib import admin
from .models import UserProfile
from organizations.models import Department, Organization
from core.admin_utils import get_user_organization


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "department")
    search_fields = ("user__username", "employee_code", "organization__commercial_name", "department__name")
    list_filter = ("organization", "department")
    list_select_related = ("user", "organization", "department")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(organization=organization)

    def save_model(self, request, obj, form, change):
        organization = get_user_organization(request)
        if organization is not None:
            obj.organization = organization
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "department":
            kwargs["queryset"] = Department.objects.filter(organization=organization)
        if organization is not None and db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(pk=organization.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.organization_id == organization.id

