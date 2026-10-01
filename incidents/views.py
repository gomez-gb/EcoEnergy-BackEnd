from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import IncidenciaForm
from .models import Incidencia
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages


ALLOWED_PAGE_SIZES = {5, 15, 30}


class IncidenciaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "incidents.view_incidencia"
    raise_exception = True
    model = Incidencia
    template_name = "incidents/incidencia_list.html"
    context_object_name = "incidencias"

    def get_organization(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("La cuenta no posee un perfil habilitado.")
        return profile.organization

    def get_queryset(self):
        organization = self.get_organization()
        return (
            Incidencia.objects
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.get_organization()
        context["page_size"] = self.page_size
        return context


class IncidenciaPageContextMixin:
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
            Incidencia.objects
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


class IncidenciaCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin,
    IncidenciaPageContextMixin, CreateView,
):
    permission_required = "incidents.add_incidencia"
    raise_exception = True
    model = Incidencia
    form_class = IncidenciaForm
    template_name = "incidents/incidencia_list.html"
    success_url = reverse_lazy("incidents:incidencia_list")
    success_message = "Incidencia creada correctamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs

    def form_valid(self, form):
        form.instance.reported_by = self.get_profile()
        return super().form_valid(form)


class IncidenciaUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin,
    IncidenciaPageContextMixin, UpdateView,
):
    permission_required = "incidents.change_incidencia"
    raise_exception = True
    model = Incidencia
    form_class = IncidenciaForm
    template_name = "incidents/incidencia_list.html"
    success_url = reverse_lazy("incidents:incidencia_list")
    success_message = "Incidencia actualizada correctamente."

    def get_queryset(self):
        return Incidencia.objects.filter(
            zone__department__organization=self.get_organization(),
            deleted_at__isnull=True,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.get_organization()
        return kwargs


class IncidenciaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "incidents.delete_incidencia"
    raise_exception = True
    model = Incidencia
    success_url = reverse_lazy("incidents:incidencia_list")
    success_message = "Incidencia archivada correctamente."

    def get(self, request, *args, **kwargs):
        return redirect("incidents:incidencia_list")

    def get_queryset(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("La cuenta no posee un perfil habilitado.")
        return Incidencia.objects.filter(
            zone__department__organization=profile.organization,
            deleted_at__isnull=True,
        )

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.deleted_at = timezone.now()
        self.object.save(update_fields=["deleted_at"])
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

