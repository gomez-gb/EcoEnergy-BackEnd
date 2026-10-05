from django.contrib.auth.views import LoginView


class AppLoginView(LoginView):
    """LoginView de Django, pero redirige directo si ya hay sesión iniciada en
    vez de mostrar el formulario de nuevo. Por defecto Django NO hace esto —
    es la causa real de que alguien ya logueado viera el login otra vez al
    volver con el botón Atrás (no era un problema de caché del navegador)."""
    redirect_authenticated_user = True
