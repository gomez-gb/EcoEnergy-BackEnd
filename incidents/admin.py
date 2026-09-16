from django.contrib import admin
from core.admin_utils import get_user_organization
from organizations.models import Zone
from .models import Incidencia, IncidenciaSeguimiento
from accounts.models import UserProfile


class IncidenciaSeguimientoInline(admin.TabularInline):
    model = IncidenciaSeguimiento
    extra = 0
    fields = ("author", "note")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        organization = get_user_organization(request)
        if organization is not None and db_field.name == "author":
            kwargs["queryset"] = UserProfile.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.action(description="Marcar como resueltas", permissions=["change"])
def marcar_resueltas(modeladmin, request, queryset):
    actualizadas = queryset.update(status=Incidencia.ESTADO_RESUELTA)
    modeladmin.message_user(request, f"{actualizadas} incidencia(s) marcada(s) como resuelta(s).")


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ("title", "zone", "reported_by", "status")
    search_fields = ("title", "zone__name", "reported_by__user__username")
    list_filter = ("status", "zone")
    list_select_related = ("zone", "reported_by")
    inlines = [IncidenciaSeguimientoInline]
    actions = [marcar_resueltas]

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

@admin.register(IncidenciaSeguimiento)
class IncidenciaSeguimientoAdmin(admin.ModelAdmin):
    list_display = ("incidencia", "author", "note")
    search_fields = ("incidencia__title", "author__user__username")
    list_filter = ("incidencia",)
    list_select_related = ("incidencia", "author")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        organization = get_user_organization(request)
        if organization is None:
            return qs
        return qs.filter(incidencia__zone__department__organization=organization)


