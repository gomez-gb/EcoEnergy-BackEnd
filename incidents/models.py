from django.db import models
from core.models import BaseModel
from django.core.exceptions import ValidationError
from .validators import validate_evidence_file


class Incident(BaseModel):
    ESTADO_ABIERTA = "ABIERTA"
    ESTADO_EN_PROCESO = "EN_PROCESO"
    ESTADO_RESUELTA = "RESUELTA"
    ESTADO_CHOICES = [
        (ESTADO_ABIERTA, "Abierta"),
        (ESTADO_EN_PROCESO, "En proceso"),
        (ESTADO_RESUELTA, "Resuelta"),
    ]

    zone = models.ForeignKey(
        "organizations.Zone", on_delete=models.PROTECT, related_name="incidents",
        verbose_name="Zona",
    )
    reported_by = models.ForeignKey(
        "accounts.UserProfile", on_delete=models.PROTECT, related_name="reported_incidents",
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

    class Meta:
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        if self.zone_id and self.reported_by_id:
            if self.zone.department.organization_id != self.reported_by.organization_id:
                raise ValidationError({
                    "reported_by": "Quien reporta debe pertenecer a la misma organización de la zona."
                })



class IncidentFollowUp(BaseModel):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="followups")
    author = models.ForeignKey(
        "accounts.UserProfile", on_delete=models.PROTECT, related_name="authored_followups",
    )
    note = models.TextField()

    class Meta:
        verbose_name = "Seguimiento de incidencia"
        verbose_name_plural = "Seguimientos de incidencia"

    def clean(self):
        super().clean()
        if self.incident_id and self.author_id:
            if self.author.organization_id != self.incident.zone.department.organization_id:
                raise ValidationError({
                    "author": "El autor del seguimiento debe pertenecer a la misma organización de la incidencia."
                })


    def __str__(self):
        return f"Seguimiento de {self.incident.title} por {self.author.user.username}"
