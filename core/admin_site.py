from django.contrib.admin import AdminSite
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse


class EcoEnergyAdminSite(AdminSite):
    """Panel exclusivo del administrador central de EcoEnergy (superusuario).

    A diferencia del AdminSite por defecto de Django (que deja entrar a
    cualquier usuario con is_staff=True), este exige is_superuser — los roles
    de organización (Administrador de Organización/Operador/Consulta) viven
    en las páginas propias de la app (dashboard, incidencias, dispositivos,
    etc.), nunca en este panel.
    """
    site_header = "Administración EcoEnergy"
    site_title = "EcoEnergy"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def login(self, request, extra_context=None):
        """Django Admin llega acá cada vez que `has_permission` falla, tanto si
        hay sesión iniciada como si no. Sin esto, alguien ya logueado (pero sin
        ser superusuario) quedaba viendo el formulario de login de nuevo —
        confuso, porque el navbar de arriba igual muestra su sesión activa.
        Ahora: si ya tiene sesión, directo al Dashboard (sin acceso, sin más);
        si no tiene sesión, al login principal de la app (no al de Django)."""
        if request.user.is_authenticated:
            return redirect("dashboard:dashboard")
        # Django ya redirigió aquí agregando ?next=<destino original> (p.ej.
        # /admin/) antes de llamar a este método — hay que reenviar ESE destino,
        # no request.get_full_path() (que en este punto es la propia URL de
        # login con el next ya adentro, duplicándolo codificado dos veces).
        next_url = request.GET.get("next") or reverse("admin:index")
        return redirect_to_login(next_url, reverse("login"))


ecoenergy_admin_site = EcoEnergyAdminSite(name="admin")
