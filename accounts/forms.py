from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")


class PasswordResetVerifyForm(forms.Form):
    code = forms.CharField(
        label="Código de verificación",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code"}),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise ValidationError("El código debe ser numérico.")
        return code


class PasswordResetConfirmForm(forms.Form):
    new_password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirma la nueva contraseña", widget=forms.PasswordInput)

    def clean_new_password1(self):
        password = self.cleaned_data["new_password1"]
        password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
