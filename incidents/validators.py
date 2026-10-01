from pathlib import Path
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_EVIDENCE_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_EVIDENCE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_evidence_file(image):
    if image.size > MAX_EVIDENCE_SIZE:
        raise ValidationError("La imagen no puede superar 2 MB.")

    suffix = Path(image.name).suffix.lower()
    if suffix not in ALLOWED_EVIDENCE_EXTENSIONS:
        raise ValidationError("Formato no permitido. Use JPG o PNG.")

    try:
        with Image.open(image) as picture:
            picture.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("El archivo no es una imagen válida.")
    finally:
        image.seek(0)

    return image
