from django.contrib import admin
from .models import Organization, Department, Zone
from core.admin_utils import get_user_organization
from accounts.models import UserProfile
from django.utils import timezone

@admin.action(description="Archivar zonas seleccionadas", permissions=["change"])
def archivar_zonas(modeladmin, request, queryset):
    ahora = timezone.now()
    actualizadas = queryset.filter(deleted_at__isnull=True).update(deleted_at=ahora, updated_at=ahora)
    modeladmin.message_user(request, f"{actualizadas} zona(s) archivada(s).")

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("commercial_name", "legal_name", "contact_email", "tax_id", "is_active")
    search_fields = ("commercial_name", "legal_name", "tax_id")
    list_filter = ("is_active",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(pk=organization.pk)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.pk == organization.pk


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "jefatura", "is_active")
    search_fields = ("name", "organization__commercial_name")
    list_filter = ("organization", "is_active")
    list_select_related = ("organization", "jefatura")

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
        if organization is not None and db_field.name == "jefatura":
            kwargs["queryset"] = UserProfile.objects.filter(organization=organization)
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


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "is_active")
    search_fields = ("name", "department__name")
    list_filter = ("department", "is_active")
    list_select_related = ("department",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(deleted_at__isnull=True)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "department":
            kwargs["queryset"] = Department.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.department.organization_id == organization.id

    actions = [archivar_zonas]

    def has_delete_permission(self, request, obj=None):
        return False

