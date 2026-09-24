from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("incidencias/", views.incidencia_list, name="incidencia_list"),
]
