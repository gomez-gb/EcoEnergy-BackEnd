from urllib.parse import quote

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import IncidentForm
from .models import Incident
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from openpyxl import Workbook
from openpyxl.styles import Font


ALLOWED_PAGE_SIZES = {5, 15, 30}


class IncidentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "incidents.view_incident"
    raise_exception = True
    model = Incident
    template_name = "incidents/incident_list.html"
    context_object_name = "incidencias"

    def get_organization(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("La cuenta no posee un perfil habilitado.")
        return profile.organization

    def get_queryset(self):
        organization = self.get_organization()
        return (
            Incident.objects
            .filter(zone__department__organization=organization, deleted_at__isnull=True)
            .select_related("zone", "reported_by")
            .order_by("-created_at")
        )


    def get_paginate_by(self, queryset):
        raw_size = self.request.GET.get("page_size")
        if raw_size:
            try:
                selected_size = int(raw_size)
            except ValueError:
                selected_size = 15
            if selected_size in ALLOWED_PAGE_SIZES:
                self.request.session["incidencia_page_size"] = selected_size
        page_size = self.request.session.get("incidencia_page_size", 15)
        self.page_size = page_size
        return page_size

    def paginate_queryset(self, queryset, page_size):
        """Si la página pedida ya no existe (ej. se cambió el tamaño de página
        y el total de páginas bajó, o se volvió con el botón Atrás a una URL
        vieja), usar la página válida más cercana en vez de romper con un 404
        — mismo patrón en DeviceListView."""
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        try:
            page_number = int(self.request.GET.get(self.page_kwarg) or 1)
        except (TypeError, ValueError):
            page_number = 1
        page_number = max(1, min(page_number, paginator.num_pages or 1))
        page = paginator.page(page_number)
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.get_organization()
        context["page_size"] = self.page_size
        return context


class IncidentPageContextMixin:
    def get_profile(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("La cuenta no posee un perfil habilitado.")
        return profile

    def get_organization(self):
        return self.get_profile().organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_organization()
        queryset = (
            Incident.objects
            .filter(zone__department__organization=organization, deleted_at__isnull=True)
            .select_related("zone", "reported_by")
            .order_by("-created_at")
        )
        page_size = self.request.session.get("incidencia_page_size", 15)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(self.request.GET.get("page", 1))

        context["incidencias"] = page_obj
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["is_paginated"] = page_obj.has_other_pages()
        context["organization"] = organization
        context["open_modal"] = True
        context["page_size"] = page_size
        return context


class IncidentCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin,
    IncidentPageContextMixin, CreateView,
):
    permission_required = "incidents.add_incident"
    raise_exception = True
    model = Incident
    form_class = IncidentForm
    template_name = "incidents/incident_list.html"
    success_url = reverse_lazy("incidents:incident_list")
    success_message = "Incidencia creada correctamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs

    def form_valid(self, form):
        form.instance.reported_by = self.get_profile()
        return super().form_valid(form)


class IncidentUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin,
    IncidentPageContextMixin, UpdateView,
):
    permission_required = "incidents.change_incident"
    raise_exception = True
    model = Incident
    form_class = IncidentForm
    template_name = "incidents/incident_list.html"
    success_url = reverse_lazy("incidents:incident_list")
    success_message = "Incidencia actualizada correctamente."

    def get_queryset(self):
        return Incident.objects.filter(
            zone__department__organization=self.get_organization(),
            deleted_at__isnull=True,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs


class IncidentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "incidents.delete_incident"
    raise_exception = True
    model = Incident
    success_url = reverse_lazy("incidents:incident_list")
    success_message = "Incidencia archivada correctamente."

    def get(self, request, *args, **kwargs):
        return redirect("incidents:incident_list")

    def get_queryset(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("La cuenta no posee un perfil habilitado.")
        return Incident.objects.filter(
            zone__department__organization=profile.organization,
            deleted_at__isnull=True,
        )

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.deleted_at = timezone.now()
        self.object.save(update_fields=["deleted_at"])
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)


@login_required
@permission_required("incidents.view_incident", raise_exception=True)
def export_incidents_xlsx(request):
    """Exporta las incidencias de la organización del usuario a un .xlsx real
    (no un CSV disfrazado) — reutiliza el MISMO queryset scopeado y filtrado
    por borrado lógico que IncidentListView, así la exportación nunca puede
    mostrar más datos de los que el usuario vería en el listado."""
    profile = getattr(request.user, "profile", None)
    if profile is None:
        raise PermissionDenied("La cuenta no posee un perfil habilitado.")

    incidencias = (
        Incident.objects
        .filter(zone__department__organization=profile.organization, deleted_at__isnull=True)
        .select_related("zone", "reported_by")
        .order_by("-created_at")
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Incidencias"

    headers = ["Zona", "Título", "Descripción", "Reportado por", "Estado", "Fecha de creación"]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for incidencia in incidencias:
        sheet.append([
            incidencia.zone.name,
            incidencia.title,
            incidencia.description,
            incidencia.reported_by.user.username,
            incidencia.get_status_display(),
            timezone.localtime(incidencia.created_at).strftime("%Y-%m-%d %H:%M"),
        ])

    for column_cells in sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    filename = f"incidencias_{profile.organization.commercial_name}_{timezone.localdate():%Y%m%d}.xlsx"
    # Los headers HTTP no aceptan tildes/ñ directo (ej. "Organización") — hay
    # que mandar un nombre ASCII de respaldo + la versión real codificada
    # (RFC 5987) para que los navegadores modernos la muestren bien.
    ascii_filename = filename.encode("ascii", "ignore").decode("ascii") or "incidencias.xlsx"
    response["Content-Disposition"] = (
        f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{quote(filename)}'
    )
    workbook.save(response)
    return response
