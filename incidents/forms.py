# incidents/forms.py
from django import forms
from django.core.exceptions import ValidationError
from organizations.models import Zone
from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["zone", "title", "description", "status", "evidence"]
        widgets = {
            "zone": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        if organization is not None:
            self.fields["zone"].queryset = Zone.objects.filter(
                department__organization=organization
            )

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 5:
            raise ValidationError("Ingrese al menos 5 caracteres.")
        return title
