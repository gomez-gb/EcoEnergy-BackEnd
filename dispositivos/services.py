import json
from django.conf import settings

def cargar_dispositivos():
    ruta = settings.BASE_DIR / "data" / "dispositivos.json"

    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, list):
        raise ValueError("Se esperaba una lista de dispositivos")
    return datos

def cargar_zonas():
    ruta = settings.BASE_DIR / "data" / "zonas.json"

    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, list):
        raise ValueError("Se esperaba una lista de zonas")
    return datos

def dispositivos_por_zona(zona_id, dispositivos):
    return [d for d in dispositivos if d["zona_id"] == zona_id]

def cargar_categorias():
    ruta = settings.BASE_DIR / "data" / "categorias.json"

    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    if not isinstance(datos, list):
        raise ValueError("Se esperaba una lista de categorías")
    return datos

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

