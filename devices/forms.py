from django import forms
from django.core.exceptions import ValidationError
from organizations.models import Zone
from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["zone", "category", "name", "serial_code", "is_active"]
        widgets = {
            "zone": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "serial_code": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        if organization is not None:
            self.fields["zone"].queryset = Zone.objects.filter(
                department__organization=organization
            )

    def clean_serial_code(self):
        serial_code = self.cleaned_data["serial_code"].strip()
        if len(serial_code) < 3:
            raise ValidationError("Ingrese al menos 3 caracteres.")
        return serial_code
