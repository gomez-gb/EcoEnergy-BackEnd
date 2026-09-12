import json
from django.conf import settings

def cargar_json(nombre_archivo):
    ruta = settings.BASE_DIR / "data" / nombre_archivo

    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, list):
        raise ValueError(f"{nombre_archivo} debía devolver una lista")
    return datos

def cargar_dispositivos():
    datos = cargar_json("dispositivos.json")
    return datos

def cargar_zonas():
    datos = cargar_json("zonas.json")
    return datos

def cargar_categorias():
    datos = cargar_json("categorias.json")
    return datos

def dispositivos_por_zona(zona_id, dispositivos):
    return [d for d in dispositivos if d["zona_id"] == zona_id]

def zona_por_id(zona_id, zonas):
    for zona in zonas:
        if zona["id"] == zona_id:
            return zona
    return None

def categoria_por_id(categoria_id, categorias):
    for categoria in categorias:
        if categoria["id"] == categoria_id:
            return categoria
    return None

def resumen_zona(zona, dispositivos_zona):
    cantidad_dispositivos = len(dispositivos_zona)

    consumo_total = sum(
        item["consumo_kwh"] for item in dispositivos_zona
    )

    if consumo_total > zona["limite_kwh"]:
        estado = "LÍMITE SUPERADO"

    else:
        estado = "DENTRO DEL LÍMITE"

    resumen = {
        "cantidad_dispositivos": cantidad_dispositivos,
        "consumo_total": consumo_total,
        "estado": estado
    }

    return resumen
