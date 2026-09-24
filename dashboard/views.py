from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from incidents.models import Incidencia
from django.core.paginator import Paginator


@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)
    if profile is None:
        raise PermissionDenied("La cuenta no posee un perfil habilitado.")
    return render(request, "dashboard/index.html", {"organization": profile.organization})

ALLOWED_PAGE_SIZES = {5, 15, 30}

@login_required
@permission_required("incidents.view_incidencia", raise_exception=True)
def incidencia_list(request):
    profile = getattr(request.user, "profile", None)
    if profile is None:
        raise PermissionDenied("La cuenta no posee un perfil habilitado.")
    organization = profile.organization

    raw_size = request.GET.get("page_size")
    if raw_size:
        try:
            selected_size = int(raw_size)
        except ValueError:
            selected_size = 15
        if selected_size in ALLOWED_PAGE_SIZES:
            request.session["incidencia_page_size"] = selected_size
    page_size = request.session.get("incidencia_page_size", 15)

    incidencias = (Incidencia.objects
                    .filter(zone__department__organization=organization)
                    .select_related("zone", "reported_by")
                    .order_by("-created_at"))
    page_obj = Paginator(incidencias, page_size).get_page(request.GET.get("page"))

    return render(request, "dashboard/incidencias.html", {
        "page_obj": page_obj,
        "page_size": page_size,
        "organization": organization,
    })
