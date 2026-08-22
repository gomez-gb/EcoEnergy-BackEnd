from django.urls import path
from . import views

app_name = "dispositivos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path(
        "zonas/<int:zona_id>/dispositivos/",
        views.dispositivos_zona,
        name="por_zona",
    ),
    path(
        "alertas/<int:alerta_id>/detalle/",
        views.detalle_alerta,
        name="por_alerta"
    ),
    path(
        "dispositivos/",
        views.catalogo,
        name="catalogo"
    ),
    path(
        "medidores/",
        views.lectura_medidor,
        name="medidores"
    ),
    path(
        "paneles/",
        views.paneles_solares,
        name="paneles"
    )
]
