from django.apps import AppConfig


class DevicesConfig(AppConfig):
    name = 'devices'
    # En el Admin solo queda visible DeviceCategory (lo demás se gestiona
    # desde el hub por organización) — el nombre deja claro que lo que se ve
    # acá es catálogo compartido entre organizaciones, no un olvido.
    verbose_name = "Catálogo compartido"
