from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from organizations.models import Department, Zone
from incidents.models import Incident
from devices.models import Device


@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        # Administrador central de EcoEnergy (superusuario, sin perfil de
        # organización): no tiene dashboard propio, su herramienta de trabajo
        # es directamente /admin/ (multi-organización por diseño).
        return redirect("admin:index")

    organization = profile.organization
    context = {
        "organization": organization,
        "total_departamentos": Department.objects.filter(organization=organization, deleted_at__isnull=True).count(),
        "total_zonas": Zone.objects.filter(department__organization=organization, deleted_at__isnull=True).count(),
        "total_dispositivos": Device.objects.filter(zone__department__organization=organization, deleted_at__isnull=True).count(),
        "total_incidencias_abiertas": Incident.objects.filter(
            zone__department__organization=organization, deleted_at__isnull=True, status=Incident.ESTADO_ABIERTA,
        ).count(),
    }
    return render(request, "dashboard/index.html", context)
