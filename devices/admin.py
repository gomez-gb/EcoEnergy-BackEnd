from django.contrib import admin
from core.admin_utils import get_user_organization
from core.admin_site import ecoenergy_admin_site
from organizations.models import Zone
from accounts.models import UserProfile
from .models import DeviceCategory, Device, DeviceReading, MaintenanceLog


@admin.register(DeviceCategory, site=ecoenergy_admin_site)
class DeviceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class DeviceReadingInline(admin.TabularInline):
    model = DeviceReading
    extra = 0
    fields = ("recorded_at", "consumption_kwh")


@admin.register(Device, site=ecoenergy_admin_site)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_code", "zone", "category", "is_active")
    search_fields = ("name", "serial_code", "zone__name")
    list_filter = ("category", "is_active", "zone")
    list_select_related = ("zone", "category")
    inlines = [DeviceReadingInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(zone__department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "zone":
            kwargs["queryset"] = Zone.objects.filter(department__organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.zone.department.organization_id == organization.id

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DeviceReading, site=ecoenergy_admin_site)
class DeviceReadingAdmin(admin.ModelAdmin):
    list_display = ("device", "recorded_at", "consumption_kwh")
    search_fields = ("device__name", "device__serial_code")
    list_filter = ("device__zone",)
    list_select_related = ("device",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(device__zone__department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(zone__department__organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.device.zone.department.organization_id == organization.id

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MaintenanceLog, site=ecoenergy_admin_site)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ("device", "performed_by", "performed_at")
    search_fields = ("device__name", "performed_by__user__username")
    list_filter = ("device__zone",)
    list_select_related = ("device", "performed_by")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(device__zone__department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None:
            if db_field.name == "device":
                kwargs["queryset"] = Device.objects.filter(zone__department__organization=organization)
            elif db_field.name == "performed_by":
                kwargs["queryset"] = UserProfile.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.device.zone.department.organization_id == organization.id

    def has_delete_permission(self, request, obj=None):
        return False
