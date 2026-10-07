from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from core.views import get_effective_organization
from organizations.models import Department, Zone
from incidents.models import Incident
from devices.models import Device


@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        # Administrador central (superusuario, sin perfil de organización):
        # su herramienta de trabajo es directamente /admin/, sin pasos
        # intermedios — el selector de organizaciones vive adentro del
        # propio Admin (ver core/admin_site.py), no acá.
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
