from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def inicio(request):

    contexto = {
        "sistema": "EcoEnergy",
        "mensaje": "Monitoreo energético responsable",
        "asignatura": "Programación Back End",
    }

    return render(
        request,
        "dispositivos/inicio.html",
        contexto,
    )

def dispositivos_zona(request, zona_id):
    if zona_id !=3:
        return HttpResponse(
            "Zona no encontrada", status = 404
        )
    return HttpResponse(
        f"Dispositivos de la zona {zona_id}"
    )

def detalle_alerta(request, alerta_id):
    if alerta_id != 9:
        return HttpResponse(
            "No hay alerta", status = 404
        )
    return HttpResponse(
        f"Alerta #{alerta_id}: sistema saturado, riesgo alto"
    )

def catalogo(request):
    dispositivos = [
        {"nombre": "Medidor inteligente", "estado": "Activo"},
        {"nombre": "Sensor de temperatura", "estado": "Activo"},
        {"nombre": "Climatizador", "estado": "Revisión"},
    ]
    return render(
        request,
        "dispositivos/catalogo.html",
        {"dispositivos": dispositivos},
    )

def lectura_medidor(request):
    medidores = [
        {"nombre": "Medidor de voltaje", "estado": "Rango dentro de lo normal: 42 kwh"},
        {"nombre": "Medidor de temperatura", "estado": "Rango por encima del normal: 100ºC"},
    ]
    return render(
        request,
        "dispositivos/medidores.html",
        {"medidores": medidores},
    )

def paneles_solares(request):
    paneles = [
        {"zona": "Planta solar Norte", "capacidad": "45kw", "estado": "Operativo"},
        {"zona": "Planta solar Norte", "capacidad": "45kw", "estado": "Defectuoso"},
        {"zona": "Planta solar Sur", "capacidad": "45kw", "estado": "Mantenimiento programado"},
    ]
    return render(
        request,
        "dispositivos/paneles.html",
        {"paneles": paneles}
    )
