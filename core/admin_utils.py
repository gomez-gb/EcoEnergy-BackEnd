from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse


def get_user_organization(request):
    if request.user.is_superuser:
        return None
    profile = getattr(request.user, "profile", None)
    if profile is None or profile.organization_id is None:
        raise PermissionDenied("El usuario no posee una organización asignada.")
    return profile.organization


def require_organization_filter(queryset, request, filter_field):
    """Para el administrador central (superusuario, sin organización propia):
    una lista plana con los registros de TODAS las organizaciones mezclados
    no le sirve a nadie en la práctica, y crece sin límite a medida que se
    suman organizaciones/dispositivos/lecturas — siempre se termina usando
    con un filtro igual. En vez de mostrar esa lista completa por defecto,
    no se muestra ningún registro hasta que el admin elija una organización
    concreta en el filtro lateral. A un usuario de organización (que ya
    llega acá con su propio queryset scopeado) esto no le aplica.

    Django llama a `get_queryset()` no solo para el listado: también para
    abrir el detalle/edición/borrado de UN objeto puntual (`get_object()`),
    y esas URLs nunca traen el parámetro de filtro (el changelist lo pasa
    como `_changelist_filters` codificado, no con el nombre original). Sin
    este chequeo, el filtro dejaba el queryset vacío y Django reportaba
    "el objeto no existe" aunque sí existiera — pasó justo así al abrir un
    dispositivo real desde una fila ya filtrada. Por eso la restricción
    aplica solo al listado (changelist); abrir un objeto puntual no debe
    exigir el filtro de nuevo, ya se llegó a él desde una lista filtrada."""
    url_name = getattr(request.resolver_match, "url_name", "") or ""
    if not url_name.endswith("_changelist"):
        return queryset
    param = f"{filter_field}__id__exact"
    if param not in request.GET:
        # get_queryset puede llamarse más de una vez por request (conteo +
        # resultados) — la marca en request evita mostrar el mensaje repetido.
        if not getattr(request, "_org_filter_hint_shown", False):
            messages.info(request, "Elige una organización en el filtro de la derecha (\"Por organización\") para ver estos registros.")
            request._org_filter_hint_shown = True
        return queryset.none()
    return queryset


class OrganizationScopedAdminMixin:
    """Para los ModelAdmins que el administrador central navega solo desde
    el hub por organización (/admin/organizaciones/<pk>/), nunca desde el
    listado técnico general — oculta el módulo de ese listado para no tener
    dos caminos distintos al mismo dato.

    Django usa ese mismo listado general como destino por defecto cuando un
    link a un objeto queda roto (`_get_obj_does_not_exist_redirect`: un
    enlace viejo, un registro ya borrado, etc.), redirigiendo siempre a
    /admin/ sin importar en qué organización estabas. Ahí se pierde el
    contexto, porque la portada de /admin/ limpia la organización activa de
    la sesión (ver `EcoEnergyAdminSite.index`) — el menú filtrado del
    sidebar quedaba roto para el resto de la navegación. Se soluciona
    mandando ese caso de vuelta al listado filtrado (preservando los
    filtros aplicados), igual que ya hace Django para los redirects propios
    de guardar/borrar."""

    def has_module_permission(self, request):
        return False

    def _get_obj_does_not_exist_redirect(self, request, opts, object_id):
        msg = f'{opts.verbose_name} con el ID "{object_id}" no existe. Es posible que haya sido eliminado.'
        self.message_user(request, msg, messages.WARNING)
        preserved_filters = self.get_preserved_filters(request)
        url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_changelist",
            current_app=self.admin_site.name,
        )
        url = add_preserved_filters({"preserved_filters": preserved_filters, "opts": opts}, url)
        return HttpResponseRedirect(url)
