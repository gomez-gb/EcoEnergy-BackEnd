import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from organizations.models import Organization, Department, Zone
from accounts.models import UserProfile
from devices.models import DeviceCategory, Device, DeviceReading

READINGS_PER_DEVICE = 130
READING_INTERVAL_HOURS = 6


class Command(BaseCommand):
    help = "Crea grupos, permisos y datos de prueba (2 organizaciones, usuarios, dispositivos y lecturas) para desarrollo/demo."

    def handle(self, *args, **options):
        self.crear_grupos()
        org_norte = self.crear_organizacion_con_usuarios(
            tax_id="76.111.222-3", legal_name="EcoEnergy Test SPA",
            commercial_name="Organización Norte", contact_email="contacto@norte.cl",
            dept_name="Operaciones", zone_name="Bodega Norte", zone_type="Bodega",
            usuarios=[
                ("admin_org", "Administrador de Organización", "11111111-1", "+56911111111", "Calle Falsa 123", "EMP-ADM-01"),
                ("operador1", "Operador", "22222222-2", "+56922222222", "Calle Falsa 456", "EMP-002"),
                ("consulta1", "Consulta", "33333333-3", "+56933333333", "Calle Falsa 789", "EMP-003"),
            ],
        )
        org_sur = self.crear_organizacion_con_usuarios(
            tax_id="77.222.333-4", legal_name="EcoEnergy Sur SPA",
            commercial_name="Organización Sur", contact_email="contacto@sur.cl",
            dept_name="Mantenimiento", zone_name="Bodega Sur", zone_type="Bodega",
            usuarios=[
                ("admin_sur", "Administrador de Organización", "44444444-4", "+56944444444", "Av. Siempreviva 742", "EMP-ADM-02"),
                ("operador2", "Operador", "55555555-5", "+56955555555", "Av. Siempreviva 743", "EMP-004"),
                ("consulta2", "Consulta", "66666666-6", "+56966666666", "Av. Siempreviva 744", "EMP-005"),
            ],
        )
        self.crear_dispositivos_y_lecturas(org_norte)
        self.crear_dispositivos_y_lecturas(org_sur)
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
        dept_name, zone_name, zone_type, usuarios,
    ):
        """Crea una organización completa (departamento, zona, usuarios con sus
        roles) y la devuelve. `usuarios` es una lista explícita de tuplas
        (username, nombre_de_grupo, rut, phone, address, employee_code) — con
        valores explícitos por organización se evita cualquier colisión de
        unique constraints entre organizaciones distintas."""
        organizacion, _ = Organization.objects.get_or_create(
            tax_id=tax_id,
            defaults={
                "legal_name": legal_name, "commercial_name": commercial_name,
                "contact_email": contact_email,
            },
        )
        departamento, _ = Department.objects.get_or_create(
            organization=organizacion, name=dept_name,
            defaults={"description": f"Departamento de prueba para roles ({commercial_name})"},
        )
        zona, _ = Zone.objects.get_or_create(
            department=departamento, name=zone_name,
            defaults={"zone_type": zone_type},
        )

        for username, nombre_grupo, rut, phone, address, employee_code in usuarios:
            grupo = Group.objects.get(name=nombre_grupo)
            user, created = User.objects.get_or_create(username=username, defaults={"is_staff": True})
            if created:
                user.set_password("Test1234!")
                user.save()
            user.groups.add(grupo)
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "organization": organizacion, "department": departamento,
                    "rut": rut, "phone": phone, "address": address, "employee_code": employee_code,
                },
            )
        organizacion.zona_demo = zona
        return organizacion

    def crear_dispositivos_y_lecturas(self, organizacion):
        """Crea el catálogo de categorías (compartido entre organizaciones, es
        información de referencia, no de una organización en particular), 4
        dispositivos para la zona de prueba de `organizacion`, y >=130 lecturas de
        consumo por dispositivo. Idempotente: si un dispositivo ya tiene lecturas,
        las regenera desde cero para no ir acumulando al re-correr el comando."""
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

        zona = organizacion.zona_demo
        nombres_categorias = list(categorias.keys())
        dispositivos = []
        for i in range(4):
            categoria = categorias[nombres_categorias[i % len(nombres_categorias)]]
            dispositivo, _ = Device.objects.get_or_create(
                serial_code=f"{organizacion.tax_id}-DEV-{i+1:02d}",
                defaults={
                    "zone": zona, "category": categoria,
                    "name": f"{categoria.name} {i+1}",
                },
            )
            dispositivos.append(dispositivo)

        random.seed(42)
        ahora = timezone.now()
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
