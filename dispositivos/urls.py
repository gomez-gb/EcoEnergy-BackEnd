from django.urls import path
from . import views

app_name = "dispositivos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("zonas/", views.listado_zonas, name="listado_zonas"),
    path("zonas/<int:zona_id>/", views.detalle_zona, name="detalle_zona"),
]
