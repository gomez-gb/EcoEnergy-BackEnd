from django.contrib.admin import AdminSite


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


ecoenergy_admin_site = EcoEnergyAdminSite(name="admin")
