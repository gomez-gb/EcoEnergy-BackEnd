from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from organizations.models import Organization, Department, Zone
from accounts.models import UserProfile


class Command(BaseCommand):
    help = "Crea grupos, permisos y datos de prueba (organizacion, usuarios) para desarrollo/demo."

    def handle(self, *args, **options):
        self.crear_grupos()
        self.crear_datos_prueba()
        self.stdout.write(self.style.SUCCESS("Datos de prueba creados correctamente."))

    def crear_grupos(self):
        admin_org, created = Group.objects.get_or_create(name="Administrador de Organización")
        if created:
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
                    "view_incidencia", "add_incidencia", "change_incidencia",
                    "view_incidenciaseguimiento", "add_incidenciaseguimiento", "change_incidenciaseguimiento",
                ],
            )
            admin_org.permissions.set(permisos)

        operador, created = Group.objects.get_or_create(name="Operador")
        if created:
            permisos = Permission.objects.filter(
                content_type__app_label="organizations", codename="view_zone",
            ) | Permission.objects.filter(
                content_type__app_label="incidents",
                codename__in=["view_incidencia", "add_incidencia", "change_incidencia", "view_incidenciaseguimiento", "add_incidenciaseguimiento"],
            )
            operador.permissions.set(permisos)

        consulta, created = Group.objects.get_or_create(name="Consulta")
        if created:
            permisos = Permission.objects.filter(
                content_type__app_label="organizations",
                codename__in=["view_organization", "view_department", "view_zone"],
            ) | Permission.objects.filter(
                content_type__app_label="accounts", codename="view_userprofile",
            ) | Permission.objects.filter(
                content_type__app_label="incidents",
                codename__in=["view_incidencia", "view_incidenciaseguimiento"],
            )
            consulta.permissions.set(permisos)

    def crear_datos_prueba(self):
        organizacion, _ = Organization.objects.get_or_create(
            tax_id="76.111.222-3",
            defaults={
                "legal_name": "EcoEnergy Test SPA",
                "commercial_name": "Organización Norte",
                "contact_email": "contacto@norte.cl",
            },
        )
        departamento, _ = Department.objects.get_or_create(
            organization=organizacion, name="Operaciones",
            defaults={"description": "Departamento de prueba para roles"},
        )
        Zone.objects.get_or_create(
            department=departamento, name="Bodega Norte",
            defaults={"zone_type": "Bodega"},
        )

        admin_org = Group.objects.get(name="Administrador de Organización")
        operador = Group.objects.get(name="Operador")
        consulta = Group.objects.get(name="Consulta")

        datos_usuarios = [
            ("admin_org", admin_org, "11111111-1", "+56911111111", "Calle Falsa 123", "EMP-ADM-01"),
            ("operador1", operador, "22222222-2", "+56922222222", "Calle Falsa 456", "EMP-002"),
            ("consulta1", consulta, "33333333-3", "+56933333333", "Calle Falsa 789", "EMP-003"),
        ]
        for username, grupo, rut, phone, address, employee_code in datos_usuarios:
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
