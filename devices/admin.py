from django.contrib import admin
from core.admin_utils import get_user_organization, require_organization_filter, OrganizationScopedAdminMixin
from core.admin_site import ecoenergy_admin_site
from organizations.models import Zone
from accounts.models import UserProfile
from .models import DeviceCategory, Device, DeviceReading, MaintenanceLog


@admin.register(DeviceCategory, site=ecoenergy_admin_site)
class DeviceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        return False


class DeviceReadingAddInline(admin.TabularInline):
    """Un inline aparte, separado del histórico, SOLO con la fila en blanco
    para registrar una lectura nueva — Django siempre ordena primero las
    filas existentes y al final las nuevas, así que mezclarla en la misma
    tabla que el histórico (con datos de semilla, ~100 filas por
    dispositivo) la entierra al fondo. Con un segundo inline del mismo
    modelo, filtrado para no traer ninguna fila existente (`get_queryset`
    con `.none()`), la fila en blanco queda arriba del todo, antes del
    histórico — mismo modelo, dos secciones con un propósito cada una."""
    model = DeviceReading
    verbose_name = "lectura nueva"
    verbose_name_plural = "Agregar lectura"
    extra = 1
    max_num = 1
    fields = ("recorded_at", "consumption_kwh")

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def has_delete_permission(self, request, obj=None):
        return False


class DeviceReadingInline(admin.TabularInline):
    """Solo para CONSULTAR un vistazo rápido al dispositivo desde su propia
    ficha — mismo criterio de solo lectura que DeviceReadingAdmin (ver ahí
    el porqué). Agregar una lectura nueva se hace en DeviceReadingAddInline,
    arriba de esta sección.

    Muestra solo las últimas RECENT_LIMIT lecturas, no el histórico
    completo (puede haber cientos por dispositivo): listarlas todas acá
    obliga a bajar esa lista entera incluso para guardar un cambio que no
    tiene nada que ver con las lecturas (ej. renombrar el dispositivo). El
    historial completo, con búsqueda y filtros, ya vive en "Lecturas de
    consumo"."""
    model = DeviceReading
    extra = 0
    fields = ("recorded_at", "consumption_kwh")

    RECENT_LIMIT = 15

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Device, site=ecoenergy_admin_site)
class DeviceAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "serial_code", "organization", "zone", "category", "is_active")
    search_fields = ("name", "serial_code", "zone__name")
    list_filter = ("zone__department__organization", "category", "is_active", "zone")
    list_select_related = ("zone__department__organization", "category")
    inlines = [DeviceReadingAddInline, DeviceReadingInline]

    @admin.display(description="Organización")
    def organization(self, obj):
        return obj.zone.department.organization

    def get_formset_kwargs(self, request, obj, inline, prefix):
        # El límite a las últimas N lecturas (DeviceReadingInline) no se
        # puede aplicar dentro del propio inline: `InlineModelAdmin.get_
        # queryset(request)` no recibe el dispositivo (`obj`), así que un
        # corte ahí sale sobre TODOS los dispositivos mezclados — y al
        # filtrar después por este dispositivo específico, casi no queda
        # nada. Este hook sí conoce `obj`, así que el corte se hace aquí.
        kwargs = super().get_formset_kwargs(request, obj, inline, prefix)
        if isinstance(inline, DeviceReadingInline) and obj is not None:
            recientes_ids = (
                DeviceReading.objects.filter(device=obj)
                .order_by("-recorded_at")
                .values_list("pk", flat=True)[: inline.RECENT_LIMIT]
            )
            kwargs["queryset"] = DeviceReading.objects.filter(pk__in=list(recientes_ids)).order_by("-recorded_at")
        return kwargs

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return require_organization_filter(qs, request, "zone__department__organization")
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
class DeviceReadingAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
    list_display = ("device", "organization", "recorded_at", "consumption_kwh")
    search_fields = ("device__name", "device__serial_code")
    list_filter = ("device__zone__department__organization", "device__zone")
    list_select_related = ("device__zone__department__organization",)

    @admin.display(description="Organización")
    def organization(self, obj):
        return obj.device.zone.department.organization

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return require_organization_filter(qs, request, "device__zone__department__organization")
        return qs.filter(device__zone__department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(zone__department__organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        # Una lectura es un dato de sensor/medición puntual en el tiempo —
        # igual que PasswordResetCodeAdmin, una vez registrada no debería
        # poder "corregirse" a mano (editar fecha/hora/valor después de que
        # ya se registró rompe la trazabilidad del histórico de consumo).
        # Sigue pudiendo agregarse (has_add_permission por defecto en True)
        # y eliminarse no — ver has_delete_permission.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MaintenanceLog, site=ecoenergy_admin_site)
class MaintenanceLogAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
    list_display = ("device", "organization", "performed_by", "performed_at")
    search_fields = ("device__name", "performed_by__user__username")
    list_filter = ("device__zone__department__organization", "device__zone")
    list_select_related = ("device__zone__department__organization", "performed_by")

    @admin.display(description="Organización")
    def organization(self, obj):
        return obj.device.zone.department.organization

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return require_organization_filter(qs, request, "device__zone__department__organization")
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
        # Registro de un mantenimiento ya realizado — mismo criterio de
        # solo lectura que DeviceReadingAdmin (ver ahí el porqué): una vez
        # registrado no se reescribe.
        return False

    def has_delete_permission(self, request, obj=None):
        return False
