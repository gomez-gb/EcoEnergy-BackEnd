import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from organizations.models import Organization, Department, Zone
from accounts.models import UserProfile
from incidents.models import Incident, IncidentFollowUp
from devices.models import DeviceCategory, Device, DeviceReading, MaintenanceLog

READINGS_PER_DEVICE = 100
INCIDENTS_PER_ORG = 40
FOLLOWUPS_PER_ORG = 25
MAINTENANCE_PER_ORG = 40
READING_INTERVAL_HOURS = 6

INCIDENT_TITLES = [
    "Corte de energía intermitente", "Consumo anómalo detectado", "Ruido inusual en equipo",
    "Fuga de refrigerante", "Sobrecarga en circuito", "Falla de sensor de medición",
]
INCIDENT_DESCRIPTIONS = [
    "Reportado durante la ronda de inspección habitual.",
    "Detectado por el sistema de monitoreo automático.",
    "Informado directamente por personal de la zona.",
]
FOLLOWUP_NOTES = [
    "Se realizó inspección visual, pendiente de repuesto.",
    "Contactado proveedor para revisión técnica.",
    "Resuelto tras reemplazo de componente.",
    "En seguimiento, se reagenda visita técnica.",
]
MAINTENANCE_DESCRIPTIONS = [
    "Mantenimiento preventivo programado.", "Calibración de sensores.",
    "Limpieza y revisión general del equipo.", "Reemplazo de piezas desgastadas.",
]


class Command(BaseCommand):
    help = "Crea grupos, permisos y datos de prueba (2 organizaciones, usuarios, dispositivos, incidencias, mantenimientos y lecturas) para desarrollo/demo."

    def handle(self, *args, **options):
        self.crear_grupos()
        org_norte = self.crear_organizacion_con_usuarios(
            tax_id="76.111.222-3", legal_name="EcoEnergy Test SPA",
            commercial_name="Organización Norte", contact_email="contacto@norte.cl",
            departamentos=[
                ("Operaciones", "Bodega Norte", "Bodega"),
                ("Mantenimiento", "Planta Norte", "Planta"),
            ],
            usuarios=[
                ("admin_org", "Administrador de Organización", "11111111-1", "+56911111111", "Calle Falsa 123", "EMP-ADM-01"),
                ("operador1", "Operador", "22222222-2", "+56922222222", "Calle Falsa 456", "EMP-002"),
                ("consulta1", "Consulta", "33333333-3", "+56933333333", "Calle Falsa 789", "EMP-003"),
            ],
        )
        org_sur = self.crear_organizacion_con_usuarios(
            tax_id="77.222.333-4", legal_name="EcoEnergy Sur SPA",
            commercial_name="Organización Sur", contact_email="contacto@sur.cl",
            departamentos=[
                ("Mantenimiento", "Bodega Sur", "Bodega"),
                ("Logística", "Planta Sur", "Planta"),
            ],
            usuarios=[
                ("admin_sur", "Administrador de Organización", "44444444-4", "+56944444444", "Av. Siempreviva 742", "EMP-ADM-02"),
                ("operador2", "Operador", "55555555-5", "+56955555555", "Av. Siempreviva 743", "EMP-004"),
                ("consulta2", "Consulta", "66666666-6", "+56966666666", "Av. Siempreviva 744", "EMP-005"),
            ],
        )
        random.seed(42)
        self.crear_dispositivos_y_operativos(org_norte)
        self.crear_dispositivos_y_operativos(org_sur)
        self.stdout.write(self.style.SUCCESS("Datos de prueba creados correctamente."))

    def crear_grupos(self):
        """Crea (si no existen) los 3 grupos y siempre sincroniza sus permisos con la
        definición actual — así re-correr el comando aplica permisos nuevos a grupos
        que ya existían de una corrida anterior, no solo a grupos recién creados."""
        admin_org, _ = Group.objects.get_or_create(name="Administrador de Organización")
        permisos = Permission.objects.filter(
            content_type__app_label="organizations",
            codename__in=[
                "view_organization", "change_organization",
                "view_department", "add_department", "change_department", "delete_department",
                "view_zone", "add_zone", "change_zone", "delete_zone",
            ],
        ) | Permission.objects.filter(
            content_type__app_label="accounts",
            codename__in=["view_userprofile", "add_userprofile", "change_userprofile"],
        ) | Permission.objects.filter(
            content_type__app_label="incidents",
            codename__in=[
                "view_incident", "add_incident", "change_incident", "delete_incident",
                "view_incidentfollowup", "add_incidentfollowup", "change_incidentfollowup",
            ],
        ) | Permission.objects.filter(
            content_type__app_label="devices",
            codename__in=[
                "view_devicecategory", "add_devicecategory", "change_devicecategory", "delete_devicecategory",
                "view_device", "add_device", "change_device", "delete_device",
                "view_devicereading", "add_devicereading", "change_devicereading",
                "view_maintenancelog", "add_maintenancelog", "change_maintenancelog",
            ],
        )
        admin_org.permissions.set(permisos)

        operador, _ = Group.objects.get_or_create(name="Operador")
        permisos = Permission.objects.filter(
            content_type__app_label="organizations", codename="view_zone",
        ) | Permission.objects.filter(
            content_type__app_label="incidents",
            codename__in=["view_incident", "add_incident", "change_incident", "view_incidentfollowup", "add_incidentfollowup"],
        ) | Permission.objects.filter(
            content_type__app_label="devices",
            codename__in=["view_devicecategory", "view_device", "add_devicereading", "view_devicereading", "add_maintenancelog", "view_maintenancelog"],
        )
        operador.permissions.set(permisos)

        consulta, _ = Group.objects.get_or_create(name="Consulta")
        permisos = Permission.objects.filter(
            content_type__app_label="organizations",
            codename__in=["view_organization", "view_department", "view_zone"],
        ) | Permission.objects.filter(
            content_type__app_label="accounts", codename="view_userprofile",
        ) | Permission.objects.filter(
            content_type__app_label="incidents",
            codename__in=["view_incident", "view_incidentfollowup"],
        ) | Permission.objects.filter(
            content_type__app_label="devices",
            codename__in=["view_devicecategory", "view_device", "view_devicereading", "view_maintenancelog"],
        )
        consulta.permissions.set(permisos)

    def crear_organizacion_con_usuarios(
        self, *, tax_id, legal_name, commercial_name, contact_email,
        departamentos, usuarios,
    ):
        """Crea una organización completa con **2 departamentos** (cada uno con su
        propia zona) y sus usuarios, y la devuelve con `.zonas_demo`/`.perfiles_demo`
        adjuntos para que `crear_dispositivos_y_operativos` reparta el catálogo entre
        ambas zonas en vez de concentrar todo en una sola.
        `usuarios` es una lista explícita (no con sufijos armados por código) para
        evitar cualquier colisión de unique constraints entre organizaciones."""
        organizacion, _ = Organization.objects.get_or_create(
            tax_id=tax_id,
            defaults={
                "legal_name": legal_name, "commercial_name": commercial_name,
                "contact_email": contact_email,
            },
        )
        zonas = []
        for dept_name, zone_name, zone_type in departamentos:
            departamento, _ = Department.objects.get_or_create(
                organization=organizacion, name=dept_name,
                defaults={"description": f"Departamento de prueba para roles ({commercial_name})"},
            )
            zona, _ = Zone.objects.get_or_create(
                department=departamento, name=zone_name,
                defaults={"zone_type": zone_type},
            )
            zonas.append(zona)

        departamento_principal = zonas[0].department
        perfiles = []
        for username, nombre_grupo, rut, phone, address, employee_code in usuarios:
            grupo = Group.objects.get(name=nombre_grupo)
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("Test1234!")
            # is_staff solo habilita /admin/, reservado al administrador central
            # (superusuario) — estos roles de organización nunca deben entrar ahí.
            if user.is_staff:
                user.is_staff = False
            user.save()
            user.groups.add(grupo)
            perfil, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "organization": organizacion, "department": departamento_principal,
                    "rut": rut, "phone": phone, "address": address, "employee_code": employee_code,
                },
            )
            perfiles.append(perfil)

        organizacion.zonas_demo = zonas
        organizacion.perfiles_demo = perfiles
        return organizacion

    def crear_dispositivos_y_operativos(self, organizacion):
        """Crea el catálogo de categorías (compartido entre organizaciones, es
        información de referencia), 4 dispositivos repartidos entre las 2 zonas de
        `organizacion`, y los datos operativos de las 4 tablas de negocio
        (DeviceReading, Incident, IncidentFollowUp, MaintenanceLog) — repartidos
        entre varios modelos en vez de concentrados en uno solo. Idempotente: borra
        y regenera lo propio de cada dispositivo/organización en cada corrida."""
        categorias = {}
        for nombre, descripcion in [
            ("Medidor de consumo", "Mide el consumo eléctrico de una zona o dispositivo."),
            ("Panel solar", "Genera energía renovable para la organización."),
            ("Climatización", "Equipos de calefacción/refrigeración industrial."),
        ]:
            categoria, _ = DeviceCategory.objects.get_or_create(
                name=nombre, defaults={"description": descripcion},
            )
            categorias[nombre] = categoria

        zonas = organizacion.zonas_demo
        nombres_categorias = list(categorias.keys())
        dispositivos = []
        for i in range(4):
            categoria = categorias[nombres_categorias[i % len(nombres_categorias)]]
            zona = zonas[i % len(zonas)]
            dispositivo, _ = Device.objects.get_or_create(
                serial_code=f"{organizacion.tax_id}-DEV-{i+1:02d}",
                defaults={
                    "zone": zona, "category": categoria,
                    "name": f"{categoria.name} {i+1}",
                },
            )
            dispositivos.append(dispositivo)

        ahora = timezone.now()

        # 1) Lecturas de consumo (el grueso del volumen — es el tipo de dato que
        # realmente acumula miles de registros en un sistema de monitoreo real).
        for dispositivo in dispositivos:
            DeviceReading.objects.filter(device=dispositivo).delete()
            lecturas = [
                DeviceReading(
                    device=dispositivo,
                    recorded_at=ahora - timedelta(hours=READING_INTERVAL_HOURS * i),
                    consumption_kwh=round(random.uniform(1.5, 45.0), 2),
                )
                for i in range(READINGS_PER_DEVICE)
            ]
            DeviceReading.objects.bulk_create(lecturas)

        # 2) Mantenimientos — repartidos entre los dispositivos de la organización.
        MaintenanceLog.objects.filter(device__in=dispositivos).delete()
        mantenimientos = [
            MaintenanceLog(
                device=random.choice(dispositivos),
                performed_by=random.choice(organizacion.perfiles_demo),
                performed_at=ahora - timedelta(days=random.randint(1, 180)),
                description=random.choice(MAINTENANCE_DESCRIPTIONS),
            )
            for _ in range(MAINTENANCE_PER_ORG)
        ]
        MaintenanceLog.objects.bulk_create(mantenimientos)

        # 3) Incidencias — repartidas entre las zonas de la organización.
        Incident.objects.filter(zone__in=zonas).delete()
        incidencias = [
            Incident(
                zone=random.choice(zonas),
                reported_by=random.choice(organizacion.perfiles_demo),
                title=random.choice(INCIDENT_TITLES),
                description=random.choice(INCIDENT_DESCRIPTIONS),
                status=random.choice([c[0] for c in Incident.ESTADO_CHOICES]),
            )
            for _ in range(INCIDENTS_PER_ORG)
        ]
        Incident.objects.bulk_create(incidencias)

        # 4) Seguimientos — sobre un subconjunto de las incidencias recién creadas.
        incidencias_creadas = list(Incident.objects.filter(zone__in=zonas))
        seguimientos = [
            IncidentFollowUp(
                incident=random.choice(incidencias_creadas),
                author=random.choice(organizacion.perfiles_demo),
                note=random.choice(FOLLOWUP_NOTES),
            )
            for _ in range(FOLLOWUPS_PER_ORG)
        ]
        IncidentFollowUp.objects.bulk_create(seguimientos)
