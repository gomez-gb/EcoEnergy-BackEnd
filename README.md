# EcoEnergy - Backend

## Descripción y objetivo

Backend del proyecto **EcoEnergy**, desarrollado con **Python y Django**. El objetivo previsto del sistema es la gestión de zonas y dispositivos energéticos.

> **Estado real del código:** el proyecto ya cuenta con la app `dispositivos`, con vistas basadas en `render()` y Templates (con herencia de `base.html` y paso de contexto). Todavía no existen modelos de base de datos: los datos que muestran las plantillas son listas y diccionarios definidos directamente en `dispositivos/views.py`. Ver la sección [Templates, herencia y contexto](#templates-herencia-y-contexto) y [Estado actual y próximos pasos](#estado-actual-y-próximos-pasos).

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

| Paquete  | Versión |
|----------|---------|
| Django   | 6.1     |
| asgiref  | 3.12.1  |
| sqlparse | 0.6.0   |

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

## Endpoints disponibles

Según lo definido en [config/urls.py](config/urls.py) y [dispositivos/urls.py](dispositivos/urls.py) (namespace `dispositivos`, montado en la raíz `/`):

| Método | Ruta                                    | `name`                    | Vista                        | Respuesta                                    |
|--------|------------------------------------------|----------------------------|-------------------------------|-----------------------------------------------|
| GET    | `/admin/`                                 | —                          | `admin.site.urls`             | Panel de administración de Django              |
| GET    | `/`                                       | `dispositivos:inicio`      | `views.inicio`                | Template (`dispositivos/inicio.html`)          |
| GET    | `/dispositivos/`                          | `dispositivos:catalogo`    | `views.catalogo`              | Template (`dispositivos/catalogo.html`)        |
| GET    | `/medidores/`                             | `dispositivos:medidores`   | `views.lectura_medidor`       | Template (`dispositivos/medidores.html`)       |
| GET    | `/paneles/`                               | `dispositivos:paneles`     | `views.paneles_solares`       | Template (`dispositivos/paneles.html`)         |
| GET    | `/zonas/<zona_id>/dispositivos/`          | `dispositivos:por_zona`    | `views.dispositivos_zona`     | `HttpResponse` (texto plano, sin template)     |
| GET    | `/alertas/<alerta_id>/detalle/`           | `dispositivos:por_alerta`  | `views.detalle_alerta`        | `HttpResponse` (texto plano, sin template)     |

Todos los `name` usados en las etiquetas `{% url 'dispositivos:...' %}` de los templates coinciden exactamente con los definidos en `dispositivos/urls.py`.

> **Nota de control de versiones:** al momento de escribir esto, las rutas `medidores` y `paneles` (vistas, urls y los enlaces de navegación correspondientes en `base.html`) están en el árbol de trabajo pero aún no se han commiteado. El último commit registrado (`Avance clase 4`) sólo incluye `inicio` y `catalogo`.

## Templates, herencia y contexto

En la Clase 4 se migraron las vistas que devolvían HTML embebido en `HttpResponse` a vistas que usan `render()` con Templates, aplicando herencia (`base.html` + páginas hijas) y contexto para pasar datos desde las Views.

### Configuración

En [config/settings.py](config/settings.py), `TEMPLATES["DIRS"]` apunta a la carpeta `templates/` en la raíz del proyecto:

```python
'DIRS': [BASE_DIR / "templates"],
```

### Estructura de carpetas de templates

```
templates/
├── base.html
└── dispositivos/
    ├── inicio.html
    ├── catalogo.html
    ├── medidores.html
    └── paneles.html
```

### Plantilla base (`templates/base.html`)

Define dos bloques que las plantillas hijas sobreescriben:

- `{% block title %}` (dentro de `<title>`, con `EcoEnergy` como valor por defecto)
- `{% block content %}` (dentro de `<main>`)

Y una barra de navegación con enlaces generados con `{% url %}` al namespace `dispositivos`:

```html
<a href="{% url 'dispositivos:inicio' %}">Inicio</a>
<a href="{% url 'dispositivos:catalogo' %}">Dispositivos</a>
<a href="{% url 'dispositivos:medidores' %}">Medidores</a>
<a href="{% url 'dispositivos:paneles' %}">Paneles</a>
```

### Templates hijos

Los cuatro heredan de `base.html` con `{% extends "base.html" %}` y sobreescriben `title` y `content`:

| Template                                   | Variables de contexto usadas (`{{ }}`)                          |
|---------------------------------------------|-------------------------------------------------------------------|
| `templates/dispositivos/inicio.html`         | `sistema`, `mensaje`, `asignatura`                                 |
| `templates/dispositivos/catalogo.html`       | `dispositivos` (lista; itera `dispositivo.nombre`, `dispositivo.estado`) |
| `templates/dispositivos/medidores.html`      | `medidores` (lista; itera `medidor.nombre`, `medidor.estado`)      |
| `templates/dispositivos/paneles.html`        | `paneles` (lista; itera `panel.zona`, `panel.capacidad`, `panel.estado`) |

### Views y contexto (`dispositivos/views.py`)

De las vistas de la app, estas cuatro usan `render()`:

| Función             | Template renderizado                | Claves del contexto                          |
|----------------------|---------------------------------------|-----------------------------------------------|
| `inicio`             | `dispositivos/inicio.html`            | `sistema`, `mensaje`, `asignatura`             |
| `catalogo`            | `dispositivos/catalogo.html`          | `dispositivos`                                 |
| `lectura_medidor`     | `dispositivos/medidores.html`         | `medidores`                                    |
| `paneles_solares`     | `dispositivos/paneles.html`           | `paneles`                                      |

Las otras dos vistas de la app (`dispositivos_zona` y `detalle_alerta`) todavía devuelven `HttpResponse` con texto plano y no usan Templates.

### Ejemplo del patrón View → Contexto → Template (laboratorio Clase 4)

El ejercicio de laboratorio de la Clase 4 es la ruta **Medidores** (`/medidores/`), separada de la demo de catálogo vista en clase:

1. **View** ([dispositivos/views.py](dispositivos/views.py)) — `lectura_medidor(request)` arma una lista de diccionarios y la pasa como contexto bajo la clave `medidores`:

    ```python
    def lectura_medidor(request):
        medidores = [
            {"nombre": "Medidor de voltaje", "estado": "Rango dentro de lo normal: 42 kwh"},
            {"nombre": "Medidor de temperatura", "estado": "Rango por encima del normal: 100ºC"},
        ]
        return render(request, "dispositivos/medidores.html", {"medidores": medidores})
    ```

2. **Contexto** — el diccionario `{"medidores": medidores}` viaja de la view al template.
3. **Template** ([templates/dispositivos/medidores.html](templates/dispositivos/medidores.html)) — extiende `base.html`, sobreescribe `content` y recorre `medidores` con `{% for %}` mostrando `medidor.nombre` y `medidor.estado`.

Como práctica adicional para reforzar el mismo patrón, se agregó también la ruta **Paneles** (`/paneles/`, vista `paneles_solares`), que sigue exactamente la misma estructura View → Contexto → Template pero con la clave de contexto `paneles`.

### Cómo comprobar la navegación entre páginas

Con el servidor corriendo (`python manage.py runserver`), visita `http://127.0.0.1:8000/` y usa los enlaces del `<nav>` de `base.html` para moverte entre **Inicio**, **Dispositivos**, **Medidores** y **Paneles**; cada uno debe cargar su template propio conservando el mismo encabezado y estructura heredados de `base.html`, y el `<title>` de la pestaña debe cambiar según el bloque `title` de cada página.

## Estado actual y próximos pasos

El proyecto ya tiene:

- Proyecto `config` configurado (settings, urls, wsgi, asgi), con `TEMPLATES["DIRS"]` apuntando a `templates/`.
- Base de datos SQLite por defecto (`db.sqlite3`), aún sin modelos propios.
- App `dispositivos` con vistas, urls y templates (ver sección [Templates, herencia y contexto](#templates-herencia-y-contexto)).
- Solo las apps internas de Django instaladas además de `dispositivos` (`admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`).
- Ningún modelo de base de datos propio: los datos mostrados en las plantillas están hardcodeados en las views.

**Próximos pasos:**

- Definir modelos para zonas, dispositivos, medidores y paneles, y reemplazar los datos hardcodeados de las views por consultas reales.
- Completar las vistas `dispositivos_zona` y `detalle_alerta` para que usen `render()` con Templates en vez de `HttpResponse` plano.
- Commitear los avances pendientes de `medidores` y `paneles` (vistas, urls y navegación en `base.html`).
