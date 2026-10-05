class NoCacheMiddleware:
    """Evita que el navegador sirva páginas desde su caché o bfcache (la "foto"
    que guarda para el botón Atrás) sin volver a pedirlas al servidor.

    Sin esto, el botón Atrás del navegador puede mostrar una pantalla de login
    vieja después de haber iniciado sesión, o datos de una sesión ya cerrada
    después de hacer logout — en ambos casos es contenido obsoleto que nunca
    pasó por la verificación real de sesión/permisos del servidor."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        return response
