from bson import ObjectId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import BookSerializer, UserLoginSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from werkzeug.security import check_password_hash
from .utils import create_tokens_for_mongo_user
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination

# Acceso a la colección
book_collection = settings.MONGO_DB['Book']
user_collection = settings.MONGO_DB['User']

class BookPagination(PageNumberPagination):
    page_size = 10  # Tamaño de la página
    page_size_query_param = 'page_size'  # Permite que el usuario pase el tamaño de la página
    max_page_size = 100  # Máximo tamaño de página permitido

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Inicio de sesión de usuario",
        operation_description="Permite a un usuario autenticarse y obtener un token de acceso y uno de refresco.",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                examples={
                    "application/json": {
                        "refresh": "string",
                        "access": "string"
                    }
                }
            ),
            400: "Errores de validación",
            401: "Credenciales inválidas",
        },
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Buscar usuario en MongoDB
            user_collection = settings.MONGO_DB['User']
            user = user_collection.find_one({"email": email})

            if user and check_password_hash(user["password"], password):
                # Generar tokens JWT
                refresh, access_token = create_tokens_for_mongo_user(email)

                return Response({
                    "refresh": str(refresh),
                    "access": str(access_token),
                }, status=status.HTTP_200_OK)

            return Response({"error": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookList(ListAPIView):
    permission_classes = [IsAuthenticated]
    """Listar y crear libros"""
    @swagger_auto_schema(
        operation_summary="Listar libros",
        operation_description="Devuelve una lista de todos los libros disponibles.",
        responses={
            200: openapi.Response(
                description="Lista de libros",
                examples={
                    "application/json": [
                        {
                            "_id": "string",
                            "title": "string",
                            "author": "string",
                            "published_date": "YYYY-MM-DD",
                            "genre": "string",
                            "price": 0.0
                        }
                    ]
                }
            ),
            403: "No autorizado",
        },
    )
    def get(self, request):
        paginator = BookPagination()
        books = list(book_collection.find())
        for book in books:
            book['_id'] = str(book['_id'])  # Convertir ObjectId a string
        result_page = paginator.paginate_queryset(books, request)
        return Response(result_page)
    
    @swagger_auto_schema(
        operation_summary="Crear un libro",
        operation_description="Permite crear un nuevo libro.",
        request_body=BookSerializer,
        responses={
            201: "Libro creado exitosamente",
            400: "Errores de validación",
        },
    )
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book_collection.insert_one(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Refrescar token",
        operation_description="Genera un nuevo token de acceso usando un token de refresco válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={
            200: openapi.Response(
                description="Token refrescado exitosamente",
                examples={"application/json": {"access": "string"}}
            ),
            400: "Refresh token requerido",
            401: "Token inválido o expirado",
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({"access": str(access_token)}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_401_UNAUTHORIZED)

class BookDetail(APIView):
    permission_classes = [IsAuthenticated]
    """Leer, actualizar y eliminar un libro"""
    @swagger_auto_schema(
        operation_summary="Obtener detalles de un libro",
        operation_description="Devuelve los detalles de un libro específico usando su ID.",
        responses={
            200: openapi.Response(
                description="Detalles del libro",
                examples={
                    "application/json": {
                        "_id": "string",
                        "title": "string",
                        "author": "string",
                        "published_date": "YYYY-MM-DD",
                        "genre": "string",
                        "price": 0.0
                    }
                }
            ),
            400: "Formato de ID no válido",
            404: "Libro no encontrado",
        },
    )
    def get(self, request, pk):
        try:
            if not ObjectId.is_valid(pk):
                return Response({"error": "Invalid ID format"}, status=status.HTTP_400_BAD_REQUEST)
            # Convertir el ID de string a ObjectId
            book = book_collection.find_one({"_id": ObjectId(pk)})
            if not book:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
            book['_id'] = str(book['_id'])  # Convertir ObjectId a string para la respuesta
            return Response(book)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Actualizar un libro",
        operation_description="Actualiza los detalles de un libro existente.",
        request_body=BookSerializer,
        responses={
            200: "Libro actualizado exitosamente",
            400: "Errores de validación",
            404: "Libro no encontrado",
        },
    )
    def put(self, request, pk):
        try:
            if not ObjectId.is_valid(pk):
                return Response({"error": "Invalid ID format"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                book_collection.update_one({"_id": ObjectId(pk)}, {"$set": serializer.data})
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Eliminar un libro",
        operation_description="Elimina un libro existente usando su ID.",
        responses={
            204: "Libro eliminado exitosamente",
            400: "Formato de ID no válido",
            404: "Libro no encontrado",
        },
    )
    def delete(self, request, pk):
        try:
            if not ObjectId.is_valid(pk):
                return Response({"error": "Invalid ID format"}, status=status.HTTP_400_BAD_REQUEST)
            result = book_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AveragePriceByYearView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Endpoint para calcular el precio promedio de los libros publicados en un año específico.
    """
    @swagger_auto_schema(
        operation_summary="Obtener precio promedio por año",
        operation_description="Calcula el precio promedio de los libros publicados en un año específico.",
        responses={
            200: openapi.Response(
                description="Precio promedio calculado",
                examples={"application/json": {"average_price": 25.0}},
            ),
            404: "No se encontraron libros para el año dado",
            400: "Errores en el formato de la solicitud",
        },
    )
    def get(self, request, year):
        try:
            # Usar el aggregation pipeline de MongoDB
            pipeline = [
                {"$match": {"published_date": {"$regex": f"^{year}"}}},  # Filtrar por año
                {"$group": {"_id": None, "average_price": {"$avg": "$price"}}}  # Calcular promedio
            ]

            result = list(book_collection.aggregate(pipeline))

            # Verificar si hay resultados
            if not result:
                return Response({"error": "No books found for the given year."}, status=status.HTTP_404_NOT_FOUND)

            # Devolver el precio promedio
            return Response({"average_price": result[0]["average_price"]}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserCreateView(APIView):
    permission_classes = [AllowAny]
    """
    Endpoint para crear usuarios.
    """
    @swagger_auto_schema(
        operation_summary="Crear un usuario",
        operation_description="Permite crear un nuevo usuario.",
        request_body=UserSerializer,
        responses={
            201: "Usuario creado exitosamente",
            400: "Errores de validación o correo ya registrado",
        },
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Verificar si el correo ya existe
            if user_collection.find_one({"email": email}):
                return Response({"error": "El correo ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

            # Guardar usuario en MongoDB
            user_data = serializer.save()
            user_data['_id'] = ObjectId()  # Generar un ObjectId único
            user_collection.insert_one(user_data)

            return Response({"message": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)