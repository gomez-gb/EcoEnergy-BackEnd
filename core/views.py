from django.core.exceptions import PermissionDenied


def get_effective_organization(request):
    """Organización "activa" para esta request: la del perfil del usuario
    (caso normal — el único camino real para los roles de organización, que
    nunca entran a /admin/). El administrador central no usa estas páginas
    en el flujo normal (su herramienta es /admin/, ver core/admin_site.py);
    si de todas formas llegara acá sin perfil, no hay organización que
    resolver."""
    profile = getattr(request.user, "profile", None)
    if profile is not None:
        return profile.organization
    raise PermissionDenied("La cuenta no posee un perfil habilitado.")


class OrganizationContextMixin:
    """Mixin para vistas que necesitan "la organización actual" del usuario
    de organización logueado — reemplaza los `get_organization()`/
    `get_profile()` que antes estaban duplicados en cada app."""

    def dispatch(self, request, *args, **kwargs):
        self.organization = get_effective_organization(request)
        return super().dispatch(request, *args, **kwargs)

    def get_organization(self):
        return self.organization
