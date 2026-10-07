from django.urls import path
from . import views

app_name = "organizations"

urlpatterns = [
    path("departamentos/", views.DepartmentListView.as_view(), name="department_list"),
    path("zonas/", views.ZoneListView.as_view(), name="zone_list"),
]
