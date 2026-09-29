from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)
    if profile is None:
        raise PermissionDenied("La cuenta no posee un perfil habilitado.")
    return render(request, "dashboard/index.html", {"organization": profile.organization})

