"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core.admin_site import ecoenergy_admin_site
from accounts.views import AppLoginView

urlpatterns = [
    # EcoEnergyAdminSite.login() (core/admin_site.py) decide a dónde mandar a
    # quien no tiene permiso para /admin/ — al login principal si es anónimo,
    # al Dashboard si ya tiene sesión iniciada pero no es superusuario.
    path('admin/', ecoenergy_admin_site.urls),
    path("", RedirectView.as_view(pattern_name="dashboard:dashboard", permanent=False)),
    # Login propio (redirect_authenticated_user=True) ANTES del include, para
    # que tome precedencia sobre el login genérico de django.contrib.auth.urls.
    path("accounts/login/", AppLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("incidencias/", include("incidents.urls")),
    path("dispositivos/", include("devices.urls")),
    path("organizacion/", include("organizations.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
