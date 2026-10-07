from django.contrib import admin
from core.admin_utils import get_user_organization, require_organization_filter, OrganizationScopedAdminMixin
from core.admin_site import ecoenergy_admin_site
from organizations.models import Zone
from .models import Incident, IncidentFollowUp
from accounts.models import UserProfile


class IncidentFollowUpInline(admin.TabularInline):
    """Un seguimiento es una entrada de bitácora de la incidencia en un
    momento dado ("se envió técnico", "esperando repuesto") — igual que
    DeviceReadingAdmin/MaintenanceLogAdmin, una vez registrado no debería
    poder reescribirse. A lo sumo hay 3 seguimientos por incidencia, así
    que a diferencia de las lecturas no hace falta separar "agregar" del
    historial: con extra=0 y has_add_permission en True (por defecto), el
    propio "+ Agregar otro" de Django alcanza para cargar uno nuevo sin
    enterrarlo bajo nada."""
    model = IncidentFollowUp
    extra = 0
    fields = ("author", "note")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "author":
            kwargs["queryset"] = UserProfile.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



@admin.action(description="Marcar como resueltas", permissions=["change"])
def marcar_resueltas(modeladmin, request, queryset):
    actualizadas = queryset.update(status=Incident.ESTADO_RESUELTA)
    modeladmin.message_user(request, f"{actualizadas} incidencia(s) marcada(s) como resuelta(s).")


@admin.register(Incident, site=ecoenergy_admin_site)
class IncidentAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "organization", "zone", "reported_by", "status")
    search_fields = ("title", "zone__name", "reported_by__user__username")
    list_filter = ("zone__department__organization", "status", "zone")
    list_select_related = ("zone__department__organization", "reported_by")
    inlines = [IncidentFollowUpInline]
    actions = [marcar_resueltas]

    @admin.display(description="Organización")
    def organization(self, obj):
        return obj.zone.department.organization

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return require_organization_filter(qs, request, "zone__department__organization")
        return qs.filter(zone__department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None:
            if db_field.name == "zone":
                kwargs["queryset"] = Zone.objects.filter(department__organization=organization)
            elif db_field.name == "reported_by":
                kwargs["queryset"] = UserProfile.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.reported_by = request.user.profile
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj is None or request.user.is_superuser:
            return True
        organization = get_user_organization(request)
        return obj.zone.department.organization_id == organization.id

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(IncidentFollowUp, site=ecoenergy_admin_site)
class IncidentFollowUpAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
    list_display = ("incident", "organization", "author", "note")
    search_fields = ("incident__title", "author__user__username")
    list_filter = ("incident__zone__department__organization", "incident")
    list_select_related = ("incident__zone__department__organization", "author")

    @admin.display(description="Organización")
    def organization(self, obj):
        return obj.incident.zone.department.organization

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return require_organization_filter(qs, request, "incident__zone__department__organization")
        return qs.filter(incident__zone__department__organization=organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None:
            if db_field.name == "author":
                kwargs["queryset"] = UserProfile.objects.filter(organization=organization)
            elif db_field.name == "incident":
                kwargs["queryset"] = Incident.objects.filter(zone__department__organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        # Entrada de bitácora de una incidencia — mismo criterio de solo
        # lectura que DeviceReadingAdmin/MaintenanceLogAdmin (ver ahí el
        # porqué): una vez registrado no se reescribe.
        return False

    def has_delete_permission(self, request, obj=None):
        return False
