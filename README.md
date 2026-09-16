# EcoEnergy - Backend

Backend del proyecto **EcoEnergy**, desarrollado con **Python y Django**, con conexión a **PostgreSQL**. Modela la estructura de una organización cliente (organizaciones, departamentos, zonas), sus usuarios (perfiles con rol/departamento) y la gestión de incidencias operativas sobre esas zonas, todo administrado desde el Django Admin con scoping por organización (cada usuario no-superusuario solo ve y edita los datos de su propia organización).

Este documento cubre la puesta en marcha completa del proyecto desde cero. Fue verificado clonando el repositorio en una carpeta aparte, con un entorno virtual y una base de datos PostgreSQL nuevos, siguiendo estos mismos pasos.

## Requisitos previos

- **Python 3.14** (o superior, compatible con Django 6.1)
- **PostgreSQL** instalado y corriendo localmente (verificado con PostgreSQL 18; cualquier versión reciente sirve)
- **Git**

## 1. Clonar el repositorio

```bash
git clone https://github.com/gomez-gb/EcoEnergy-BackEnd.git
cd EcoEnergy-BackEnd
```

## 2. Crear y activar el entorno virtual

```bash
python3 -m venv .venv
```

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

## 3. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

Esto instala Django, `psycopg2-binary` (driver de PostgreSQL), `python-dotenv` (carga de variables de entorno desde `.env`) y `django-bootstrap5` (usado por el módulo legacy `dispositivos`, ver más abajo).

## 4. Crear la base de datos y el usuario en PostgreSQL

Entra a la consola de PostgreSQL (ajusta según tu instalación/SO):

```bash
sudo -u postgres psql
```

Dentro de `psql`, crea el usuario y la base de datos (usa una contraseña propia en vez de `tu_password_segura`):

```sql
CREATE USER ecoenergy_user WITH PASSWORD 'tu_password_segura';
CREATE DATABASE ecoenergy_db OWNER ecoenergy_user;
GRANT ALL PRIVILEGES ON DATABASE ecoenergy_db TO ecoenergy_user;
\q
```

> Importante: crear la base de datos con `OWNER ecoenergy_user` (no solo con `GRANT`) evita problemas de permisos sobre el esquema `public` en PostgreSQL 15+.

## 5. Configurar variables de entorno

Copia el archivo de ejemplo y complétalo con los datos reales que usaste en el paso anterior:

```bash
cp .env.example .env
```

`.env` debe quedar con esta forma (los valores son ejemplos, no los reutilices tal cual):

```
DB_NAME=ecoenergy_db
DB_USER=ecoenergy_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=5432
DJANGO_SECRET_KEY=una-clave-larga-y-aleatoria-solo-para-tu-entorno
```

`.env` está en `.gitignore` y nunca debe subirse al repositorio; `.env.example` sí se versiona, como plantilla sin datos reales.

## 6. Aplicar las migraciones

```bash
python manage.py migrate
```

Esto crea todas las tablas del proyecto (`organizations`, `accounts`, `incidents`, más las de Django: `auth`, `admin`, `contenttypes`, `sessions`).

## 7. Cargar datos de prueba

```bash
python manage.py seed_demo_data
```

Es idempotente (usa `get_or_create` en todo), así que se puede correr más de una vez sin duplicar datos ni fallar si ya existen. Crea:

**3 grupos con permisos distintos** (Groups/Permissions de Django, scopeados por app/modelo):

| Grupo | Puede |
|---|---|
| `Administrador de Organización` | Ver/editar Organization, Department, Zone, UserProfile e Incidencia/Seguimiento de su organización; borrar Department y Zone |
| `Operador` | Ver zonas, crear y editar Incidencias y sus seguimientos |
| `Consulta` | Solo lectura (`view_*`) sobre todo lo anterior |

**1 organización de prueba** ("Organización Norte", con un departamento "Operaciones" y una zona "Bodega Norte").

**3 usuarios de prueba**, todos con contraseña **`Test1234!`**, staff (pueden entrar a `/admin/`) pero **no superusuarios** (quedan scopeados a "Organización Norte", que es justamente lo que permite probar el scoping por organización en vivo):

| Usuario | Grupo asignado |
|---|---|
| `admin_org` | Administrador de Organización |
| `operador1` | Operador |
| `consulta1` | Consulta |

## 8. Crear tu propio superusuario (opcional pero recomendado)

Un superusuario ve **todas** las organizaciones sin restricción de scoping, útil para administrar el sistema completo:

```bash
python manage.py createsuperuser
```

## 9. Levantar el servidor

```bash
python manage.py runserver
```

- `http://127.0.0.1:8000/admin/` — Django Admin. Entra con tu superusuario o con cualquiera de los 3 usuarios de prueba (`admin_org` / `operador1` / `consulta1`, contraseña `Test1234!`) para ver el scoping por organización en acción.
- `http://127.0.0.1:8000/` — módulo `dispositivos` (ver más abajo).

## Módulos del proyecto

- **`core`** — `BaseModel` abstracto (`created_at`, `updated_at`, `deleted_at`, este último usado para soft-delete de Zonas) y `core/admin_utils.get_user_organization`, la función que resuelve la organización del usuario logueado y que usan todos los `ModelAdmin` del proyecto para hacer scoping. También vive aquí el management command `seed_demo_data`.
- **`organizations`** — `Organization` → `Department` → `Zone`, la jerarquía estructural de una organización cliente. `Department` valida en `clean()` que su jefatura pertenezca a la misma organización y sea un usuario activo. El Admin de `Zone` incluye la acción personalizada "Archivar zonas seleccionadas" (soft-delete vía `deleted_at`, sin borrado real).
- **`accounts`** — `UserProfile`, que extiende `auth.User` (uno a uno) con organización, departamento, RUT, teléfono, dirección y código de empleado. Valida en `clean()` que su departamento pertenezca a su misma organización.
- **`incidents`** — `Incidencia` (con estados Abierta/En proceso/Resuelta, la acción personalizada "Marcar como resueltas", y una validación `clean()` que exige que quien reporta pertenezca a la misma organización que la zona afectada) e `IncidenciaSeguimiento` (notas de seguimiento, gestionadas como **Inline** dentro del formulario de `Incidencia`, no como tabla independiente).
- **`dispositivos`** — módulo previo (Unidad 1) sin relación con la base de datos PostgreSQL ni con los modelos anteriores: lee zonas/categorías/dispositivos de prueba desde JSON en `data/` y expone rutas de solo lectura (`/`, `/zonas/`, `/zonas/<id>/`) calculando consumo y estado en cada request. Detalle completo de esas rutas y relaciones en [ANALISIS.md](ANALISIS.md).

## Comandos de verificación

```bash
python manage.py check                              # errores de configuración
python manage.py makemigrations --check --dry-run    # confirma que no faltan migraciones
python manage.py migrate --check                     # confirma que la BD está al día
```
