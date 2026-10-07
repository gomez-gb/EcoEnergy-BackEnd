from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class DeviceCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría de dispositivo"
        verbose_name_plural = "Categorías de dispositivo"

    def __str__(self):
        return self.name


class Device(BaseModel):
    zone = models.ForeignKey(
        "organizations.Zone", on_delete=models.PROTECT, related_name="devices",
        verbose_name="Zona",
    )
    category = models.ForeignKey(
        DeviceCategory, on_delete=models.PROTECT, related_name="devices",
        verbose_name="Categoría",
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")
    serial_code = models.CharField(max_length=50, unique=True, verbose_name="Código de serie")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"

    def __str__(self):
        return f"{self.name} ({self.serial_code})"


class DeviceReading(BaseModel):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="readings",
        verbose_name="Dispositivo",
    )
    recorded_at = models.DateTimeField(verbose_name="Fecha y hora")
    consumption_kwh = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Consumo (kWh)")

    class Meta:
        verbose_name = "Lectura de consumo"
        verbose_name_plural = "Lecturas de consumo"
        ordering = ["-recorded_at"]

    def clean(self):
        super().clean()
        if self.consumption_kwh is not None and self.consumption_kwh < 0:
            raise ValidationError({"consumption_kwh": "El consumo no puede ser negativo."})

    def __str__(self):
        return f"{self.device} — {self.recorded_at:%Y-%m-%d %H:%M} ({self.consumption_kwh} kWh)"


class MaintenanceLog(BaseModel):
    device = models.ForeignKey(
        Device, on_delete=models.PROTECT, related_name="maintenance_logs",
        verbose_name="Dispositivo",
    )
    performed_by = models.ForeignKey(
        "accounts.UserProfile", on_delete=models.PROTECT, related_name="maintenance_logs",
        verbose_name="Realizado por",
    )
    performed_at = models.DateTimeField(verbose_name="Fecha de mantenimiento")
    description = models.TextField(verbose_name="Descripción")

    class Meta:
        verbose_name = "Registro de mantenimiento"
        verbose_name_plural = "Registros de mantenimiento"
        ordering = ["-performed_at"]

    def clean(self):
        super().clean()
        if self.device_id and self.performed_by_id:
            if self.device.zone.department.organization_id != self.performed_by.organization_id:
                raise ValidationError({
                    "performed_by": "Quien registra el mantenimiento debe pertenecer a la misma organización del dispositivo."
                })

    def __str__(self):
        return f"Mantenimiento de {self.device} — {self.performed_at:%Y-%m-%d}"
