# incidents/forms.py
from django import forms
from django.core.exceptions import ValidationError
from accounts.models import UserProfile
from organizations.models import Zone
from .models import Incident


class IncidentForm(forms.ModelForm):
    # "reported_by" SIEMPRE declarado en Meta.fields (si no, Django nunca lo
    # guarda en el modelo aunque el campo exista en el form — construct_instance
    # solo aplica los campos listados acá). Para un usuario de organización
    # normal se quita del form en __init__ y se asigna a mano en la vista;
    # para el administrador central (sin perfil propio) se deja visible.
    class Meta:
        model = Incident
        fields = ["zone", "reported_by", "title", "description", "status", "evidence"]
        widgets = {
            "zone": forms.Select(attrs={"class": "form-select"}),
            "reported_by": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, organization=None, require_reported_by=False, **kwargs):
        super().__init__(*args, **kwargs)
        if organization is not None:
            self.fields["zone"].queryset = Zone.objects.filter(
                department__organization=organization
            )
        if require_reported_by and organization is not None:
            # El administrador central no tiene un perfil propio para
            # auto-asignarse como reportante — tiene que elegir a quién de
            # esa organización corresponde la incidencia.
            self.fields["reported_by"].queryset = UserProfile.objects.filter(organization=organization)
            self.fields["reported_by"].label = "Reportado por"
        else:
            # Usuario de organización normal: se asigna solo en la vista
            # (form_valid), nunca lo elige a mano.
            del self.fields["reported_by"]

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 5:
            raise ValidationError("Ingrese al menos 5 caracteres.")
        return title
