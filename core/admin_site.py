from django.contrib.admin import AdminSite
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse


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
    index_template = "admin/organization_index.html"

    # Clave de sesión con la organización que el administrador central está
    # "viendo" en este momento — así el menú filtrado sobrevive a cualquier
    # navegación dentro del admin (listados, formularios, confirmaciones),
    # no solo a la página de entrada al hub. Se limpia al volver a Inicio.
    SESSION_ORG_KEY = "admin_active_organization_id"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def get_urls(self):
        custom_urls = [
            path(
                "organizaciones/<int:pk>/",
                self.admin_view(self.organization_hub),
                name="organization_hub",
            ),
        ]
        return custom_urls + super().get_urls()

    def index(self, request, extra_context=None):
        """La portada del Admin ya muestra, arriba del listado técnico de
        modelos, las organizaciones existentes — entrar a una lleva al hub
        con sus Departamentos/Zonas/Dispositivos/Incidencias/Cuentas ya
        filtrados. Nada de páginas intermedias fuera de /admin/: esto es
        simplemente lo primero que se ve al entrar.

        Volver a Inicio es también la forma de "salir" de una organización:
        limpia la sesión para que el menú vuelva a ser el listado completo."""
        request.session.pop(self.SESSION_ORG_KEY, None)
        from organizations.models import Organization
        extra_context = extra_context or {}
        extra_context["organizations"] = Organization.objects.filter(is_active=True).order_by("commercial_name")
        return super().index(request, extra_context=extra_context)

    def _organization_app_list(self, organization):
        """Arma `available_apps` filtrado por organización, en el mismo
        formato que usa `admin/app_list.html` (visto en el código fuente de
        Django) — se puede usar tanto para la página del hub como para
        reemplazar el sidebar de cualquier otra página del admin vía
        `each_context`. Reemplaza por completo la lista real de apps: lo
        "general" (catálogo compartido, códigos de recuperación) no
        pertenece a la vista de una organización puntual, ya tiene su
        propio lugar en la portada de /admin/."""
        def link(name, object_name, admin_url):
            return {"name": name, "object_name": object_name, "admin_url": admin_url, "add_url": None}

        org_qs = f"organization__id__exact={organization.pk}"
        dept_org_qs = f"department__organization__id__exact={organization.pk}"
        zone_dept_org_qs = f"zone__department__organization__id__exact={organization.pk}"
        device_zone_qs = f"device__zone__department__organization__id__exact={organization.pk}"
        incident_zone_qs = f"incident__zone__department__organization__id__exact={organization.pk}"

        return [
            {
                "app_label": "org-info", "app_url": "#", "name": "Organización",
                "models": [
                    link("Información de la organización", "organization",
                         reverse("admin:organizations_organization_change", args=[organization.pk])),
                ],
            },
            {
                "app_label": "org-estructura", "app_url": "#", "name": "Estructura",
                "models": [
                    link("Departamentos", "department", f"{reverse('admin:organizations_department_changelist')}?{org_qs}"),
                    link("Zonas", "zone", f"{reverse('admin:organizations_zone_changelist')}?{dept_org_qs}"),
                ],
            },
            {
                "app_label": "org-dispositivos", "app_url": "#", "name": "Dispositivos",
                "models": [
                    link("Dispositivos", "device", f"{reverse('admin:devices_device_changelist')}?{zone_dept_org_qs}"),
                    link("Lecturas de consumo", "devicereading", f"{reverse('admin:devices_devicereading_changelist')}?{device_zone_qs}"),
                    link("Mantenimientos", "maintenancelog", f"{reverse('admin:devices_maintenancelog_changelist')}?{device_zone_qs}"),
                ],
            },
            {
                "app_label": "org-incidencias", "app_url": "#", "name": "Incidencias",
                "models": [
                    link("Incidencias", "incident", f"{reverse('admin:incidents_incident_changelist')}?{zone_dept_org_qs}"),
                    link("Seguimientos de incidencia", "incidentfollowup", f"{reverse('admin:incidents_incidentfollowup_changelist')}?{incident_zone_qs}"),
                ],
            },
            {
                "app_label": "org-usuarios", "app_url": "#", "name": "Usuarios",
                "models": [
                    link("Cuentas", "userprofile", f"{reverse('admin:accounts_userprofile_changelist')}?{org_qs}"),
                ],
            },
        ]

    def each_context(self, request):
        """Django llama a esto en TODA página del admin (listados,
        formularios, confirmaciones de borrado, historial, etc.) para armar
        el contexto común — es el único lugar que garantiza que el menú
        filtrado se mantenga sin importar qué camino tome el administrador
        central dentro de una organización, no solo en la página de
        entrada al hub."""
        context = super().each_context(request)
        org_id = request.session.get(self.SESSION_ORG_KEY)
        if org_id:
            from organizations.models import Organization
            organization = Organization.objects.filter(pk=org_id).first()
            if organization is not None:
                context["available_apps"] = self._organization_app_list(organization)
                context["current_organization"] = organization
            else:
                request.session.pop(self.SESSION_ORG_KEY, None)
        return context

    def organization_hub(self, request, pk):
        """Hub de una organización: Información + el menú filtrado (armado
        por `_organization_app_list`) queda activo en la barra lateral para
        el resto de la navegación — en vez de que el administrador central
        tenga que aplicar el filtro a mano cada vez."""
        from organizations.models import Organization
        organization = get_object_or_404(Organization, pk=pk)
        request.session[self.SESSION_ORG_KEY] = organization.pk

        context = {
            **self.each_context(request),
            "title": organization.commercial_name,
            "organization": organization,
        }
        return render(request, "admin/organization_hub.html", context)

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
