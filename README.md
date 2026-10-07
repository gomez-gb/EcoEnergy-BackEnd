# EcoEnergy - Backend

Backend del proyecto **EcoEnergy**, desarrollado con **Python y Django**, con conexión a **PostgreSQL**. Modela la estructura de una organización cliente (organizaciones, departamentos, zonas), sus usuarios (perfiles con rol/departamento), un catálogo de dispositivos con lecturas de consumo y mantenimientos, y la gestión de incidencias operativas — con scoping por organización en toda la aplicación (cada usuario no-superusuario solo ve y edita los datos de su propia organización) y recuperación de contraseña por código temporal.

Este documento cubre la puesta en marcha completa del proyecto desde cero.

### Arranque rápido con Docker (recomendado)

1. Clonar el repo y copiar `.env.example` a `.env`.
2. `docker compose up -d --build`
3. `docker compose exec web python manage.py migrate`
4. `docker compose exec web python manage.py seed_demo_data`
5. `docker compose exec web python manage.py createsuperuser`
6. Ir a `http://localhost:8000`

> Tras modificar `.env`, el contenedor `web` necesita recrearse (`docker compose up -d --force-recreate`) para que los cambios se apliquen.

El resto de esta sección (`## 1` a `## 9`) documenta el camino alternativo sin Docker, con entorno virtual y PostgreSQL instalados a mano.

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

Esto instala Django, `psycopg2-binary` (driver de PostgreSQL), `python-dotenv` (carga de variables de entorno desde `.env`), `django-bootstrap5` (estilos de formularios/templates), `pillow` (validación real de imágenes subidas) y `openpyxl` (exportación a Excel).

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

`.env` debe quedar con esta forma como mínimo (los valores son ejemplos, no los reutilices tal cual):

```
DB_NAME=ecoenergy_db
DB_USER=ecoenergy_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=5432
DJANGO_SECRET_KEY=una-clave-larga-y-aleatoria-solo-para-tu-entorno
```

`.env` está en `.gitignore` y nunca debe subirse al repositorio; `.env.example` sí se versiona, como plantilla sin datos reales.

Variables adicionales que también acepta `.env` (ya vienen con un valor por defecto seguro/funcional si no se definen):

- `COOKIE_SECURE` — controla la flag `Secure` de las cookies de sesión.
- `DJANGO_DEBUG` — controla `DEBUG` de Django.
- `EMAIL_BACKEND`/`EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`/`EMAIL_USE_TLS`/`DEFAULT_FROM_EMAIL` — envío del correo de recuperación de contraseña. Sin configurar, usa el backend de consola (el correo se imprime en la terminal del servidor, no se envía de verdad) — útil para desarrollo. Con credenciales SMTP reales (por ejemplo Mailtrap) se envía como correo real.
- `PASSWORD_RESET_CODE_TTL` — segundos de vigencia del código de recuperación (por defecto 120).
- `PASSWORD_RESET_MAX_ATTEMPTS` — intentos fallidos permitidos antes de bloquear un código (por defecto 5).

## 6. Aplicar las migraciones

```bash
python manage.py migrate
```

Esto crea todas las tablas del proyecto (`organizations`, `accounts`, `incidents`, `devices`, más las de Django: `auth`, `admin`, `contenttypes`, `sessions`).

## 7. Cargar datos de prueba

```bash
python manage.py seed_demo_data
```

Es idempotente (usa `get_or_create`/regeneración controlada en todo), así que se puede correr más de una vez sin duplicar datos de catálogo ni fallar si ya existen. Crea:

**3 grupos con permisos distintos** (Groups/Permissions de Django, scopeados por app/modelo):

| Grupo | Puede |
|---|---|
| `Administrador de Organización` | CRUD completo (salvo borrado físico) sobre Organization/Department/Zone/UserProfile/Incident/IncidentFollowUp/Device/DeviceCategory/DeviceReading/MaintenanceLog de su organización |
| `Operador` | Ver zonas y dispositivos; crear/editar incidencias y sus seguimientos; crear lecturas de consumo y registros de mantenimiento |
| `Consulta` | Solo lectura (`view_*`) sobre todo lo anterior, incluida la exportación a Excel de incidencias |

**2 organizaciones de prueba completas**, cada una con 2 departamentos y 2 zonas:

| Organización | Departamentos / Zonas |
|---|---|
| Organización Norte | Operaciones → Bodega Norte · Mantenimiento → Planta Norte |
| Organización Sur | Mantenimiento → Bodega Sur · Logística → Planta Sur |

**6 usuarios de prueba** (3 por organización, mismos 3 roles), todos con contraseña **`Test1234!`**. Ninguno es `is_staff` — el Django Admin (`/admin/`) es exclusivo del administrador central (superusuario), estos 6 usuarios viven en las páginas propias de la app:

| Usuario | Organización | Grupo asignado |
|---|---|---|
| `admin_org` | Norte | Administrador de Organización |
| `operador1` | Norte | Operador |
| `consulta1` | Norte | Consulta |
| `admin_sur` | Sur | Administrador de Organización |
| `operador2` | Sur | Operador |
| `consulta2` | Sur | Consulta |

Además crea un catálogo de 3 categorías de dispositivo, 8 dispositivos (4 por organización) y más de 1.000 registros operativos repartidos entre lecturas de consumo, mantenimientos, incidencias y seguimientos — reproducible corriendo el comando de nuevo.

## 8. Crear tu propio superusuario (recomendado)

El superusuario es el **administrador central de EcoEnergy**: es el único rol que entra a `/admin/`, y ve/administra **todas** las organizaciones sin restricción de scoping.

```bash
python manage.py createsuperuser
```

## 9. Levantar el servidor

```bash
python manage.py runserver
```

- `http://127.0.0.1:8000/` — redirige a `/dashboard/` (requiere sesión iniciada; si no hay sesión, redirige a su vez al login).
- `http://127.0.0.1:8000/accounts/login/` — login. Incluye el link "¿Olvidaste tu contraseña?" (recuperación por código de 6 dígitos). Con tu superusuario, el login te manda directo a `/admin/`; con cualquiera de los 6 usuarios de prueba te manda al Dashboard de su organización.
- `http://127.0.0.1:8000/admin/` — Django Admin, exclusivo del superusuario (cualquier otro usuario autenticado que intente entrar es redirigido al Dashboard sin más).

## Módulos del proyecto

- **`core`** — `BaseModel` abstracto (`created_at`, `updated_at`, `deleted_at`, usado para soft-delete en todos los modelos de negocio) y `core/admin_utils.get_user_organization`, la función que resuelve la organización del usuario logueado y que usan todos los `ModelAdmin` del proyecto para hacer scoping. `core/admin_site.py` define `EcoEnergyAdminSite`, el Admin personalizado que exige `is_superuser` (no solo `is_staff`) para entrar — los roles de organización nunca acceden a `/admin/`. `core/middleware.py` agrega `Cache-Control: no-store` a toda respuesta. También vive aquí el management command `seed_demo_data`.
- **`organizations`** — `Organization` → `Department` → `Zone`, la jerarquía estructural de una organización cliente. `Department` valida en `clean()` que su `head` (jefatura) pertenezca a la misma organización y sea un usuario activo. Listados de solo lectura de Departamentos/Zonas en `/organizacion/departamentos/` y `/organizacion/zonas/` (la creación/edición se gestiona desde el Admin). El Admin de `Zone` incluye la acción personalizada "Archivar zonas seleccionadas" (soft-delete vía `deleted_at`, sin borrado real).
- **`accounts`** — `UserProfile`, que extiende `auth.User` (uno a uno) con organización, departamento, RUT, teléfono, dirección y código de empleado; valida en `clean()` que su departamento pertenezca a su misma organización. `PasswordResetCode` implementa la recuperación de contraseña: código numérico de 6 dígitos generado con el módulo `secrets` (no predecible), hasheado (nunca en texto plano), vigencia configurable, máximo de intentos fallidos, de un solo uso — flujo completo en `/accounts/password-reset/` → `/verify/` → `/confirm/`. `accounts/validators.ComplexPasswordValidator` exige mayúscula+minúscula+número+carácter especial en cualquier contraseña nueva del proyecto (registrado en `AUTH_PASSWORD_VALIDATORS`).
- **`incidents`** — modelos `Incident`/`IncidentFollowUp` con scoping por organización. CRUD web completo en `/incidencias/` (listado paginado 5/15/30 persistido en sesión, crear/editar vía modal, borrado lógico con confirmación SweetAlert2), con evidencia fotográfica opcional (`evidence`, validada por tamaño/extensión/contenido real vía Pillow). Botón "Exportar a Excel" genera un `.xlsx` real con las incidencias activas de la organización del usuario. `IncidentFollowUp` solo gestionable desde el Admin (Inline).
- **`devices`** — catálogo de dispositivos: `DeviceCategory` (categorías, catálogo compartido entre organizaciones), `Device` (dispositivos por zona, CRUD web completo en `/dispositivos/` con el mismo patrón que incidencias), `DeviceReading` (lecturas de consumo) y `MaintenanceLog` (registros de mantenimiento) — estos dos últimos solo gestionables desde el Admin por ahora.
- **`dashboard`** — página de Inicio tras el login (`LOGIN_REDIRECT_URL`): tarjetas de resumen (departamentos/zonas/dispositivos/incidencias abiertas) + accesos directos a cada sección, condicionados por permiso real de cada usuario.
- **Autenticación**: login/logout con las vistas de Django (`django.contrib.auth.urls`), con un `LoginView` propio (`accounts.views.AppLoginView`) que redirige a quien ya tiene sesión iniciada en vez de mostrarle el formulario de nuevo.

## Comandos de verificación

```bash
python manage.py check                              # errores de configuración
python manage.py makemigrations --check --dry-run    # confirma que no faltan migraciones
python manage.py migrate --check                     # confirma que la BD está al día
```
