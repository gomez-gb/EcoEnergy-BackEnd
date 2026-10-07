from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView
from core.views import OrganizationContextMixin
from .models import Department, Zone


class DepartmentListView(LoginRequiredMixin, PermissionRequiredMixin, OrganizationContextMixin, ListView):
    permission_required = "organizations.view_department"
    raise_exception = True
    model = Department
    template_name = "organizations/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        return (
            Department.objects
            .filter(organization=self.organization, deleted_at__isnull=True)
            .select_related("head")
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        return context


class ZoneListView(LoginRequiredMixin, PermissionRequiredMixin, OrganizationContextMixin, ListView):
    permission_required = "organizations.view_zone"
    raise_exception = True
    model = Zone
    template_name = "organizations/zone_list.html"
    context_object_name = "zones"

    def get_queryset(self):
        return (
            Zone.objects
            .filter(department__organization=self.organization, deleted_at__isnull=True)
            .select_related("department")
            .order_by("department__name", "name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        return context
