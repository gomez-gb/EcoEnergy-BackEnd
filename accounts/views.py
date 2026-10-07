import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import PasswordResetConfirmForm, PasswordResetRequestForm, PasswordResetVerifyForm
from .models import PasswordResetCode

User = get_user_model()

GENERIC_RESET_MESSAGE = "Si el correo corresponde a una cuenta registrada, recibirás un código de recuperación."


class AppLoginView(LoginView):
    """LoginView de Django, pero redirige directo si ya hay sesión iniciada en
    vez de mostrar el formulario de nuevo. Por defecto Django NO hace esto —
    es la causa real de que alguien ya logueado viera el login otra vez al
    volver con el botón Atrás (no era un problema de caché del navegador)."""
    redirect_authenticated_user = True


def password_reset_request(request):
    """Paso 1: pide el correo. Respuesta siempre genérica — nunca revela si
    la cuenta existe (mismo principio que el login, ver Clase 6)."""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user is not None:
                # Solicitar un código nuevo invalida los anteriores activos.
                PasswordResetCode.objects.filter(user=user, used=False).update(used=True)
                code = "".join(secrets.choice("0123456789") for _ in range(6))
                reset_code = PasswordResetCode.objects.create(
                    user=user,
                    code_hash=make_password(code),
                    expires_at=timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_CODE_TTL),
                )
                send_mail(
                    subject="Código de recuperación de contraseña — EcoEnergy",
                    message=(
                        f"Tu código de recuperación es: {code}\n"
                        f"Vence en {settings.PASSWORD_RESET_CODE_TTL} segundos y es de un solo uso."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                request.session["password_reset_code_id"] = reset_code.id
            messages.info(request, GENERIC_RESET_MESSAGE)
            return redirect("accounts:password_reset_verify")
    else:
        form = PasswordResetRequestForm()
    return render(request, "registration/password_reset_request.html", {"form": form})


def password_reset_verify(request):
    """Paso 2: valida el código contra el hash guardado — nunca compara el
    código en texto plano porque nunca se guardó en texto plano."""
    code_id = request.session.get("password_reset_code_id")
    form = PasswordResetVerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        submitted_code = form.cleaned_data["code"]
        reset_code = PasswordResetCode.objects.filter(pk=code_id).first() if code_id else None

        if reset_code is None or reset_code.used:
            form.add_error(None, "Código inválido o ya utilizado. Solicita uno nuevo.")
        elif reset_code.failed_attempts >= settings.PASSWORD_RESET_MAX_ATTEMPTS:
            form.add_error(None, "Superaste el máximo de intentos. Solicita un código nuevo.")
        elif reset_code.expires_at < timezone.now():
            form.add_error(None, "El código expiró. Solicita uno nuevo.")
        elif not check_password(submitted_code, reset_code.code_hash):
            reset_code.failed_attempts += 1
            reset_code.save(update_fields=["failed_attempts"])
            form.add_error(None, "Código incorrecto.")
        else:
            request.session["password_reset_verified_id"] = reset_code.id
            return redirect("accounts:password_reset_confirm")
    context = {"form": form, "ttl_seconds": settings.PASSWORD_RESET_CODE_TTL}
    return render(request, "registration/password_reset_verify.html", context)


def password_reset_confirm(request):
    """Paso 3: solo accesible tras verificar el código en el paso anterior
    (vuelve a comprobarlo contra la BD, la sesión apoya pero no reemplaza)."""
    verified_id = request.session.get("password_reset_verified_id")
    reset_code = (
        PasswordResetCode.objects.filter(pk=verified_id, used=False).first()
        if verified_id else None
    )
    if reset_code is None or reset_code.expires_at < timezone.now():
        messages.error(request, "La sesión de recuperación ya no es válida. Solicita un código nuevo.")
        return redirect("accounts:password_reset_request")

    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        reset_code.user.set_password(form.cleaned_data["new_password1"])
        reset_code.user.save()
        reset_code.used = True
        reset_code.save(update_fields=["used"])
        request.session.pop("password_reset_code_id", None)
        request.session.pop("password_reset_verified_id", None)
        messages.success(request, "Contraseña actualizada correctamente. Ya puedes iniciar sesión.")
        return redirect("login")
    return render(request, "registration/password_reset_confirm.html", {"form": form})
