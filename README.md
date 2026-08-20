# EcoEnergy - Backend

## Descripción y objetivo

Backend del proyecto **EcoEnergy**, desarrollado con **Python y Django**. El objetivo previsto del sistema es la gestión de zonas y dispositivos energéticos.

> **Estado real del código:** por ahora el repositorio contiene únicamente el esqueleto base generado por `django-admin startproject` (proyecto `config`). Todavía no existen apps Django personalizadas, modelos ni endpoints propios más allá del panel de administración por defecto. Ver la sección [Estado actual y próximos pasos](#estado-actual-y-próximos-pasos).

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

Según lo definido en [config/urls.py](config/urls.py), actualmente el único endpoint implementado es:

| Método      | Ruta      | Descripción                                    |
|-------------|-----------|-------------------------------------------------|
| GET / POST  | `/admin/` | Panel de administración de Django (`admin.site.urls`) |

No hay apps ni endpoints de API propios implementados todavía.

## Estado actual y próximos pasos

El proyecto se encuentra en su fase inicial: es el esqueleto base generado por Django (`django-admin startproject`), con:

- Proyecto `config` configurado (settings, urls, wsgi, asgi).
- Base de datos SQLite por defecto (`db.sqlite3`).
- Solo las apps internas de Django instaladas (`admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`).
- Ningún modelo, app personalizada ni endpoint de API propio desarrollado aún.

**Próximos pasos:**

- Crear las apps de dominio del proyecto (por ejemplo, gestión de zonas y dispositivos energéticos) una vez se definan sus modelos y endpoints.
- La siguiente clase del curso, correspondiente a **Templates**, todavía no ha sido desarrollada.
