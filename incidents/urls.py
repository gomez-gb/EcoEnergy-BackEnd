from django.urls import path
from . import views

app_name = "incidents"

urlpatterns = [
    path("", views.IncidenciaListView.as_view(), name="incidencia_list"),
    path("new/", views.IncidenciaCreateView.as_view(), name="incidencia_create"),
    path("<int:pk>/edit/", views.IncidenciaUpdateView.as_view(), name="incidencia_update"),
    path("<int:pk>/delete/", views.IncidenciaDeleteView.as_view(), name="incidencia_delete"),
]
