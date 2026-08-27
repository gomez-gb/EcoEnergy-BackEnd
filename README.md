# EcoEnergy - Backend

## Descripción y objetivo

Backend del proyecto **EcoEnergy**, desarrollado con **Python y Django**. El sistema permite listar zonas de consumo energético y consultar el detalle de cada una: sus dispositivos, la categoría de cada dispositivo, el consumo total de la zona y su estado (`NORMAL` o `ALERTA`) según el límite definido para esa zona.

> **Estado real del código:** no hay Models, migraciones, ORM, CRUD ni formularios. Los datos viven en tres archivos JSON dentro de `data/` (`zonas.json`, `categorias.json`, `dispositivos.json`) y las relaciones entre ellos se resuelven a mano por `id`, en Python puro, dentro de `dispositivos/services.py`. Las vistas de `dispositivos/views.py` cargan esos JSON en cada request, calculan el consumo total y el estado de cada zona, y pasan el resultado ya calculado a los templates — ningún número está escrito directamente en el HTML. Ver la sección [Estructura de datos y relaciones](#estructura-de-datos-y-relaciones) y [Rutas disponibles](#rutas-disponibles).

## Requisitos previos

- **Python 3.14.7** (versión verificada dentro del entorno virtual del proyecto)
- **pip 26.2.1** (o superior, compatible con la versión de Python anterior)
- Git

## Clonación del repositorio

```bash
git clone https://github.com/gomez-gb/EcoEnergy-BackEnd.git
cd EcoEnergy-BackEnd
```

## Creación y activación del entorno virtual (.venv)

Crea el entorno virtual:

```bash
python3 -m venv .venv
```

Actívalo según tu sistema operativo y shell:

**Linux/macOS con fish:**
```fish
source .venv/bin/activate.fish
```

**Linux/macOS con bash/zsh:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Git Bash:**
```bash
source .venv/Scripts/activate
```

## Instalación de dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Dependencias actuales del proyecto ([requirements.txt](requirements.txt)):

| Paquete          | Versión | Motivo |
|------------------|---------|--------|
| Django           | 6.1     | Framework base del proyecto |
| asgiref          | 3.12.1  | Dependencia interna de Django |
| sqlparse         | 0.6.0   | Dependencia interna de Django |
| django-bootstrap5 | 26.2   | Ver justificación abajo |

### Justificación de `django-bootstrap5`

- **Necesidad:** el enunciado pide una interfaz con Bootstrap (tablas con scroll en contenedor adaptable, layout responsive) sin reinventar CSS propio ni depender de copiar archivos estáticos de Bootstrap a mano.
- **Uso:** se agregó `django_bootstrap5` a `INSTALLED_APPS` en [config/settings.py](config/settings.py). En [templates/base.html](templates/base.html) se carga con `{% load django_bootstrap5 %}` al inicio del archivo, y se insertan los estilos y el JS de Bootstrap con `{% bootstrap_css %}` (en el `<head>`) y `{% bootstrap_javascript %}` (antes de cerrar `<body>`). Como todos los templates de la app heredan de `base.html`, cualquier página nueva recibe Bootstrap automáticamente.
- **Comprobación:** al levantar el servidor y visitar cualquier ruta, las clases de Bootstrap usadas en los templates (`row`, `col-md-*`, `card`, `table`, `table-responsive`, `badge`, `btn`) se ven aplicadas — tarjetas con bordes y sombra, tabla con scroll horizontal en pantallas angostas, badges de color para el estado de cada zona.

## Comandos de verificación

Verificar que el proyecto no tiene errores de configuración:

```bash
python manage.py check
```

Levantar el servidor de desarrollo:

```bash
python manage.py runserver
```

Por defecto, el servidor queda disponible en `http://127.0.0.1:8000/`.

## Estructura de datos y relaciones

Los datos de prueba viven en `data/`:

```
data/
├── zonas.json         # id, nombre, limite_kwh
├── categorias.json    # id, nombre, descripcion
└── dispositivos.json  # id, nombre, consumo_kwh, zona_id, categoria_id
```

Cada dispositivo pertenece a una única zona (`zona_id`) y a una única categoría (`categoria_id`); ambas relaciones se resuelven por búsqueda manual de `id` en `dispositivos/services.py` (funciones `zona_por_id`, `categoria_por_id`, `dispositivos_por_zona`), sin ORM ni claves foráneas de base de datos. El detalle completo de relaciones y multiplicidades está en [ANALISIS.md](ANALISIS.md).

## Rutas disponibles

Definidas en [config/urls.py](config/urls.py) y [dispositivos/urls.py](dispositivos/urls.py) (namespace `dispositivos`, montado en la raíz `/`):

| Método | Ruta            | `name`                        | Vista                | Qué hace |
|--------|-----------------|--------------------------------|-----------------------|----------|
| GET    | `/admin/`        | —                              | `admin.site.urls`     | Panel de administración de Django (no se usa para el caso EcoEnergy) |
| GET    | `/`              | `dispositivos:inicio`          | `views.inicio`        | Página de bienvenida del sistema |
| GET    | `/zonas/`        | `dispositivos:listado_zonas`   | `views.listado_zonas` | Lista todas las zonas con su nombre, límite y cantidad de dispositivos, con acceso al detalle de cada una |
| GET    | `/zonas/<id>/`   | `dispositivos:detalle_zona`    | `views.detalle_zona`  | Detalle de una zona: sus dispositivos con categoría, consumo total calculado y estado (`ALERTA` si el consumo total supera el límite, `NORMAL` en caso contrario). Si la zona no tiene dispositivos, muestra un mensaje en vez de una tabla vacía. Si el `id` no existe, responde 404 |

Todos los `name` usados en las etiquetas `{% url 'dispositivos:...' %}` de los templates coinciden con los definidos en `dispositivos/urls.py`.

## Templates y herencia

```
templates/
├── base.html
└── dispositivos/
    ├── inicio.html
    ├── listado_zonas.html
    └── detalle_zona.html
```

`base.html` define `{% block title %}` y `{% block content %}`, carga Bootstrap y contiene la barra de navegación (`Inicio`, `Zonas`). Los tres templates hijos extienden `base.html` con `{% extends "base.html" %}` y sobreescriben esos bloques; ninguno tiene valores numéricos ni de estado escritos a mano — todo llega desde el contexto que arma la vista correspondiente en `dispositivos/views.py`.

## Pruebas

Con el servidor corriendo (`python manage.py runserver`), visita:

- `/zonas/` — listado de las 4 zonas registradas en `data/zonas.json`.
- `/zonas/1/` — Bodega Principal, consumo 510.5 kWh > límite 500 kWh → estado **ALERTA**.
- `/zonas/2/` o `/zonas/3/` — consumo dentro del límite → estado **NORMAL**.
- `/zonas/4/` — Patio de Carga, sin dispositivos registrados → mensaje "Esta zona no tiene dispositivos".
- `/zonas/99/` — id inexistente → respuesta 404 controlada.

Para comprobar que los datos se procesan dinámicamente, agrega un dispositivo
válido a `data/dispositivos.json` (con un `id` único y un `zona_id`/`categoria_id`
existentes) y recarga `/zonas/` o el detalle de esa zona sin reiniciar el
servidor ni modificar ningún archivo de código.

## Estado actual

- App `dispositivos` con las rutas de zonas funcionando end-to-end: listado, detalle, cálculo dinámico de consumo/estado, caso de zona vacía y 404 controlado para id inexistente.
- Sin Models, sin migraciones propias, sin base de datos relacional para el dominio del proyecto — todo el estado vive en `data/*.json` y se lee en cada request.
- Bootstrap integrado vía `django-bootstrap5` en toda la app a través de la herencia de `base.html`.
