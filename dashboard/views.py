from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from organizations.models import Organization, Department, Zone
from incidents.models import Incident
from devices.models import Device


@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        # Administrador central de EcoEnergy (superusuario, sin perfil de
        # organización): ve un resumen cruzando TODAS las organizaciones.
        # Su herramienta de trabajo real es /admin/, no esta app por-organización.
        context = {
            "es_admin_central": True,
            "total_organizaciones": Organization.objects.count(),
            "total_departamentos": Department.objects.filter(deleted_at__isnull=True).count(),
            "total_zonas": Zone.objects.filter(deleted_at__isnull=True).count(),
            "total_dispositivos": Device.objects.filter(deleted_at__isnull=True).count(),
            "total_incidencias_abiertas": Incident.objects.filter(
                deleted_at__isnull=True, status=Incident.ESTADO_ABIERTA,
            ).count(),
        }
        return render(request, "dashboard/index.html", context)

    organization = profile.organization
    context = {
        "es_admin_central": False,
        "organization": organization,
        "total_departamentos": Department.objects.filter(organization=organization, deleted_at__isnull=True).count(),
        "total_zonas": Zone.objects.filter(department__organization=organization, deleted_at__isnull=True).count(),
        "total_dispositivos": Device.objects.filter(zone__department__organization=organization, deleted_at__isnull=True).count(),
        "total_incidencias_abiertas": Incident.objects.filter(
            zone__department__organization=organization, deleted_at__isnull=True, status=Incident.ESTADO_ABIERTA,
        ).count(),
    }
    return render(request, "dashboard/index.html", context)
