from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def inicio(request):
    return HttpResponse(
        "<h1>EcoEnergy</h1>"
        "<p>Back End en funcionamiento</p>"
    )

def dispositivos_zona(request, zona_id):
    if zona_id !=3:
        return HttpResponse(
            "Zona no encontrada", status = 404
        )
    return HttpResponse(
        f"Dispositivos de la zona {zona_id}"
    )

def lectura_medidor(request, medidor_id):
    if medidor_id != 6:
        return HttpResponse(
            "Medidor no encontrado", status = 404
        )
    return HttpResponse(
        f"Lectura del medidor {medidor_id}: 42 kwh"
    )

def detalle_alerta(request, alerta_id):
    if alerta_id != 9:
        return HttpResponse(
            "No hay alerta", status = 404
        )
    return HttpResponse(
        f"Alerta #{alerta_id}: sistema saturado, riesgo alto"
    )
