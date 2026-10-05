from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.core.exceptions import ValidationError


class UserProfile(BaseModel):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT, related_name="user_profiles")
    department = models.ForeignKey("organizations.Department", on_delete=models.PROTECT, null=True, blank=True, related_name="user_profiles")
    rut = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=150)
    employee_code = models.CharField(max_length=150, unique=True)

    def clean(self):
        super().clean()
        if self.department_id and self.department.organization_id != self.organization_id:
            raise ValidationError({
                "department": "El departamento debe pertenecer a la organización seleccionada."
            })

    def __str__(self):
        return self.user.username


class PasswordResetCode(BaseModel):
    """Código temporal de 6 dígitos para recuperación de contraseña (Clase 6,
    actividad complementaria). El código en sí NUNCA se guarda — solo su hash
    (`code_hash`, vía `make_password`) — y se valida con `check_password`."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_codes")
    code_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    failed_attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Código de recuperación para {self.user.username} (creado {self.created_at:%Y-%m-%d %H:%M})"
