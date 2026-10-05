from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from .models import Department, Zone


class OrganizationScopedListMixin:
    def get_organization(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            raise PermissionDenied("La cuenta no posee un perfil habilitado.")
        return profile.organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.get_organization()
        return context


class DepartmentListView(LoginRequiredMixin, PermissionRequiredMixin, OrganizationScopedListMixin, ListView):
    permission_required = "organizations.view_department"
    raise_exception = True
    model = Department
    template_name = "organizations/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        return (
            Department.objects
            .filter(organization=self.get_organization(), deleted_at__isnull=True)
            .select_related("jefatura")
            .order_by("name")
        )


class ZoneListView(LoginRequiredMixin, PermissionRequiredMixin, OrganizationScopedListMixin, ListView):
    permission_required = "organizations.view_zone"
    raise_exception = True
    model = Zone
    template_name = "organizations/zone_list.html"
    context_object_name = "zones"

    def get_queryset(self):
        return (
            Zone.objects
            .filter(department__organization=self.get_organization(), deleted_at__isnull=True)
            .select_related("department")
            .order_by("department__name", "name")
        )
