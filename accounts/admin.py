from django.contrib import admin
from .models import PasswordResetCode, UserProfile
from organizations.models import Department, Organization
from core.admin_utils import get_user_organization, OrganizationScopedAdminMixin
from core.admin_site import ecoenergy_admin_site


@admin.register(UserProfile, site=ecoenergy_admin_site)
class UserProfileAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
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

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PasswordResetCode, site=ecoenergy_admin_site)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    """Solo lectura para el administrador central — útil para auditar
    intentos de recuperación, nunca para editar (el código ya está
    hasheado, no hay nada que "corregir" a mano)."""
    list_display = ("user", "created_at", "expires_at", "used", "failed_attempts")
    list_filter = ("used",)
    search_fields = ("user__username",)
    list_select_related = ("user",)
    readonly_fields = [f.name for f in PasswordResetCode._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

