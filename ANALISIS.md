## Relaciones y multiplicidades

- Zona (1) — (0..*) Dispositivo: cada dispositivo pertenece a una única zona,
  vía `dispositivos[].zona_id → zonas[].id`.
- Categoria (1) — (0..*) Dispositivo: cada dispositivo pertenece a una única
  categoría, vía `dispositivos[].categoria_id → categorias[].id`.
- Ambas relaciones se resuelven en Python por búsqueda manual de id (sin ORM,
  sin claves foráneas de base de datos) mediante funciones en
  `dispositivos/services.py`: `zona_por_id`, `categoria_por_id` (buscan un
  único elemento o `None`), `dispositivos_por_zona` (filtra varios).

## Matriz Criterio de aceptación | Archivo/Componente | Prueba

| Criterio | Archivo/Componente | Prueba |
|---|---|---|
| CA-01 | `dispositivos/views.py` (`listado_zonas`) + `data/zonas.json` | GET `/zonas/` muestra las 4 zonas |
| CA-02 | `templates/dispositivos/listado_zonas.html` + `listado_zonas` (`cantidad_dispositivos`) | Cada tarjeta muestra nombre, límite, cantidad y botón "Ver detalle" |
| CA-03 | `dispositivos/views.py` (`detalle_zona`) + `templates/dispositivos/detalle_zona.html` | GET `/zonas/1/` muestra dispositivos, categoría, consumo y métricas |
| CA-04 | Todo el cálculo vive en `views.py` (sumas, `len`, comparaciones); ningún valor fijo en templates | Revisar templates: cero números hardcodeados |
| CA-05 | `detalle_zona` (`if consumo_total > zona["limite_kwh"]`) | Zona 1 (510.5 > 500) → ALERTA; Zonas 2 y 3 → NORMAL |
| CA-06 | `services.py` (loaders leen el JSON en cada request, sin caché) | Agregar un dispositivo válido a `dispositivos.json` y recargar sin tocar código |
| CA-07 | `templates/dispositivos/detalle_zona.html` (`{% empty %}`) | GET `/zonas/4/` (Patio de Carga) muestra "Esta zona no tiene dispositivos" |
| CA-08 | `detalle_zona` (`zona_por_id` + `raise Http404`) | GET `/zonas/99/` → 404 |
| CA-09 | Bootstrap grid (`row`/`col-md-4`) en listado | Duplicar registros temporalmente y verificar que la estructura no se rompe |
| CA-10 | `detalle_zona.html` (`<div class="table-responsive">`) | Tabla de dispositivos no desborda la página |
| CA-11 | `templates/base.html` (herencia) + Bootstrap en todos los templates | Revisión visual: header/nav/tarjetas/tabla coherentes |
| CA-12 | `detalle_zona.html` (badge con texto ALERTA/NORMAL + ícono, no solo color) | Confirmar que el estado se lee sin depender del color |
| CA-13 | `requirements.txt`, `README.md`, proyecto completo | `python manage.py check` sin errores |
