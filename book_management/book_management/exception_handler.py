from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

# Configurar logging para registrar los errores
logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Manejador global de excepciones.
    """
    # Llama al manejador por defecto de DRF
    response = exception_handler(exc, context)

    if response is not None:
        # Si DRF pudo manejar el error, lo retornamos
        return response

    # Si es un error no controlado (500), loguear y retornar una respuesta personalizada
    logger.error(f"Error no controlado en {context['view'].__class__.__name__}: {exc}")

    return Response(
        {"error": "Ocurrió un error interno. Por favor, inténtalo nuevamente más tarde."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )