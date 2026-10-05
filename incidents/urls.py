from django.urls import path
from . import views

app_name = "incidents"

urlpatterns = [
    path("", views.IncidentListView.as_view(), name="incident_list"),
    path("new/", views.IncidentCreateView.as_view(), name="incident_create"),
    path("<int:pk>/edit/", views.IncidentUpdateView.as_view(), name="incident_update"),
    path("<int:pk>/delete/", views.IncidentDeleteView.as_view(), name="incident_delete"),
]
