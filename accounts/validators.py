import re
from django.core.exceptions import ValidationError


class ComplexPasswordValidator:
    """Exige longitud mínima 10 + mayúscula + minúscula + número + carácter
    especial — especificación concreta de la Evaluación Formativa U2 para la
    contraseña nueva en el flujo de recuperación. Se registra en
    AUTH_PASSWORD_VALIDATORS para aplicar en todo el proyecto, no solo ahí."""

    MIN_LENGTH = 10

    def validate(self, password, user=None):
        if len(password) < self.MIN_LENGTH:
            raise ValidationError(
                f"La contraseña debe tener al menos {self.MIN_LENGTH} caracteres.",
                code="password_too_short_complex",
            )
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "La contraseña debe incluir al menos una letra mayúscula.",
                code="password_no_upper",
            )
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "La contraseña debe incluir al menos una letra minúscula.",
                code="password_no_lower",
            )
        if not re.search(r"\d", password):
            raise ValidationError(
                "La contraseña debe incluir al menos un número.",
                code="password_no_digit",
            )
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError(
                "La contraseña debe incluir al menos un carácter especial.",
                code="password_no_special",
            )

    def get_help_text(self):
        return (
            f"Tu contraseña debe tener al menos {self.MIN_LENGTH} caracteres, "
            "con mayúscula, minúscula, número y carácter especial."
        )
