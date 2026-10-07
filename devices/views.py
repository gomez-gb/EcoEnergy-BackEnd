from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from core.views import OrganizationContextMixin
from .forms import DeviceForm
from .models import Device


ALLOWED_PAGE_SIZES = {5, 15, 30}


class DeviceListView(LoginRequiredMixin, PermissionRequiredMixin, OrganizationContextMixin, ListView):
    permission_required = "devices.view_device"
    raise_exception = True
    model = Device
    template_name = "devices/device_list.html"
    context_object_name = "devices"

    def get_queryset(self):
        return (
            Device.objects
            .filter(zone__department__organization=self.organization, deleted_at__isnull=True)
            .select_related("zone", "category")
            .order_by("name")
        )

    def get_paginate_by(self, queryset):
        raw_size = self.request.GET.get("page_size")
        if raw_size:
            try:
                selected_size = int(raw_size)
            except ValueError:
                selected_size = 15
            if selected_size in ALLOWED_PAGE_SIZES:
                self.request.session["device_page_size"] = selected_size
        page_size = self.request.session.get("device_page_size", 15)
        self.page_size = page_size
        return page_size

    def paginate_queryset(self, queryset, page_size):
        """Si la página pedida ya no existe (ej. se cambió el tamaño de página
        o se volvió con Atrás a una URL vieja), usar la página válida más
        cercana en vez de romper con un 404 — mismo patrón en IncidentListView."""
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
        context["organization"] = self.organization
        context["page_size"] = self.page_size
        return context


class DevicePageContextMixin(OrganizationContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = (
            Device.objects
            .filter(zone__department__organization=self.organization, deleted_at__isnull=True)
            .select_related("zone", "category")
            .order_by("name")
        )
        page_size = self.request.session.get("device_page_size", 15)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(self.request.GET.get("page", 1))

        context["devices"] = page_obj
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["is_paginated"] = page_obj.has_other_pages()
        context["organization"] = self.organization
        context["open_modal"] = True
        context["page_size"] = page_size
        return context


class DeviceCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin,
    DevicePageContextMixin, CreateView,
):
    permission_required = "devices.add_device"
    raise_exception = True
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_list.html"
    success_url = reverse_lazy("devices:device_list")
    success_message = "Dispositivo creado correctamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs


class DeviceUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin,
    DevicePageContextMixin, UpdateView,
):
    permission_required = "devices.change_device"
    raise_exception = True
    model = Device
    form_class = DeviceForm
    template_name = "devices/device_list.html"
    success_url = reverse_lazy("devices:device_list")
    success_message = "Dispositivo actualizado correctamente."

    def get_queryset(self):
        return Device.objects.filter(
            zone__department__organization=self.organization,
            deleted_at__isnull=True,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs


class DeviceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, OrganizationContextMixin, DeleteView):
    permission_required = "devices.delete_device"
    raise_exception = True
    model = Device
    success_url = reverse_lazy("devices:device_list")
    success_message = "Dispositivo archivado correctamente."

    def get(self, request, *args, **kwargs):
        return redirect("devices:device_list")

    def get_queryset(self):
        return Device.objects.filter(
            zone__department__organization=self.organization,
            deleted_at__isnull=True,
        )

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.deleted_at = timezone.now()
        self.object.save(update_fields=["deleted_at"])
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)
