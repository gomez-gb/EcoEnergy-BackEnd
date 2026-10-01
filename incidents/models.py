from django.db import models
from core.models import BaseModel
from django.core.exceptions import ValidationError
from .validators import validate_evidence_file


class Incidencia(BaseModel):
    ESTADO_ABIERTA = "ABIERTA"
    ESTADO_EN_PROCESO = "EN_PROCESO"
    ESTADO_RESUELTA = "RESUELTA"
    ESTADO_CHOICES = [
        (ESTADO_ABIERTA, "Abierta"),
        (ESTADO_EN_PROCESO, "En proceso"),
        (ESTADO_RESUELTA, "Resuelta"),
    ]

    zone = models.ForeignKey(
        "organizations.Zone", on_delete=models.PROTECT, related_name="incidencias",
        verbose_name="Zona",
    )
    reported_by = models.ForeignKey(
        "accounts.UserProfile", on_delete=models.PROTECT, related_name="incidencias_reportadas",
        verbose_name="Reportado por",
    )
    title = models.CharField(max_length=150, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ABIERTA, verbose_name="Estado")
    evidence = models.ImageField(
        upload_to="incidencias/%Y/%m/",
        blank=True,
        validators=[validate_evidence_file],
        verbose_name="Evidencia",
    )

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        if self.zone_id and self.reported_by_id:
            if self.zone.department.organization_id != self.reported_by.organization_id:
                raise ValidationError({
                    "reported_by": "Quien reporta debe pertenecer a la misma organización de la zona."
                })



class IncidenciaSeguimiento(BaseModel):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name="seguimientos")
    author = models.ForeignKey(
        "accounts.UserProfile", on_delete=models.PROTECT, related_name="seguimientos_realizados",
    )
    note = models.TextField()

    def clean(self):
        super().clean()
        if self.incidencia_id and self.author_id:
            if self.author.organization_id != self.incidencia.zone.department.organization_id:
                raise ValidationError({
                    "author": "El autor del seguimiento debe pertenecer a la misma organización de la incidencia."
                })


    def __str__(self):
        return f"Seguimiento de {self.incidencia.title} por {self.author.user.username}"

