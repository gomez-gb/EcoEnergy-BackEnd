from django.shortcuts import render
from .services import cargar_dispositivos, cargar_zonas, dispositivos_por_zona, zona_por_id, cargar_categorias, categoria_por_id, resumen_zona
from django.http import Http404

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

def listado_zonas(request):
    zonas = cargar_zonas()
    dispositivos = cargar_dispositivos()

    zonas_con_resumen = []
    for zona in zonas:
        dispositivos_zona = dispositivos_por_zona(zona["id"], dispositivos)
        zonas_con_resumen.append({
            **zona,
            "cantidad_dispositivos": len(dispositivos_zona),
        })

    contexto = {
        "zonas": zonas_con_resumen,
    }

    return render(
        request, "dispositivos/listado_zonas.html", contexto
    )

def detalle_zona(request, zona_id):
    zonas = cargar_zonas()
    dispositivos = cargar_dispositivos()
    categorias = cargar_categorias()

    zona = zona_por_id(zona_id, zonas)
    if zona is None:
        raise Http404("Zona no encontrada")

    dispositivos_zona = dispositivos_por_zona(zona_id, dispositivos)

    consumo_total = sum(
            item["consumo_kwh"] for item in dispositivos_zona
        )

    if consumo_total > zona["limite_kwh"]:
        estado = "ALERTA"

    else:
        estado = "NORMAL"

    dispositivos_con_categoria = []
    for d in dispositivos_zona:
        categoria = categoria_por_id(d["categoria_id"], categorias)
        dispositivos_con_categoria.append({
            **d,
            "categoria": categoria["nombre"] if categoria else "Desconocida",
        })

    contexto = {
        "zona": zona,
        "consumo_total": consumo_total,
        "estado": estado,
        "dispositivos": dispositivos_con_categoria,
        "cantidad_dispositivos": len(dispositivos_zona),
    }

    return render(request, "dispositivos/detalle_zona.html", contexto)

def resumen_zonas(request):
    zonas = cargar_zonas()
    dispositivos = cargar_dispositivos()

    resumen_por_zona = []
    for zona in zonas:
        dispositivos_zona = dispositivos_por_zona(zona["id"], dispositivos)
        resumen = resumen_zona(zona, dispositivos_zona)
        resumen_por_zona.append({**zona, **resumen})

    total_zonas = len(zonas)
    total_dispositivos = len(dispositivos)
    consumo_total_general = sum(item["consumo_kwh"] for item in dispositivos)

    contexto = {
        "resumen_por_zona": resumen_por_zona,
        "total_zonas": total_zonas,
        "total_dispositivos": total_dispositivos,
        "consumo_total_general": consumo_total_general,
    }

    return render(request, "dispositivos/resumen_zonas.html", contexto)

