# organizations/models.py
from django.db import models
from core.models import BaseModel
from django.core.exceptions import ValidationError

class Organization(BaseModel):

    legal_name = models.CharField(max_length=150)
    tax_id = models.CharField(max_length=20, unique=True)
    commercial_name = models.CharField(max_length=150)
    contact_email = models.EmailField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.commercial_name

class Department(BaseModel):

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="departments")
    jefatura = models.ForeignKey("accounts.UserProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="departments_led")
    name = models.CharField(max_length=150)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.jefatura_id:
            if self.jefatura.organization_id != self.organization_id:
                raise ValidationError({"jefatura": "La jefatura debe pertenecer a la misma organización del departamento."})
            if not self.jefatura.user.is_active:
                raise ValidationError({"jefatura": "La jefatura debe ser un usuario activo."})

    def __str__(self):
        return self.name

class Zone(BaseModel):

    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='zones')
    name = models.CharField(max_length=150)
    zone_type = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
