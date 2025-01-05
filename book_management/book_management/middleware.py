from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class Handle500Middleware:
    """
    Middleware para capturar errores 500 y retornar una respuesta personalizada.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as exc:
            # Loguear el error
            logger.error(f"Error 500 no controlado: {exc}")
            # Retornar una respuesta personalizada
            return JsonResponse(
                {"error": "Ocurrió un error interno. Por favor, inténtalo nuevamente más tarde."},
                status=500
            )
        return response