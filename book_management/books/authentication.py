from rest_framework_simplejwt.authentication import JWTAuthentication
from bson import ObjectId
from django.conf import settings
from .utils import MongoDBUser

class MongoDBJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Busca al usuario en MongoDB usando el `user_id` del token JWT.
        """
        user_id = validated_token.get("user_id")
        if not user_id:
            raise ValueError("El token JWT no contiene 'user_id'.")

        # Verificar si el user_id es un ObjectId válido
        if not ObjectId.is_valid(user_id):
            raise ValueError("El 'user_id' no es un ObjectId válido.")

        # Buscar el usuario en MongoDB
        user_collection = settings.MONGO_DB['User']
        user = user_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise ValueError("Usuario no encontrado en la base de datos.")

        # Devolver una instancia de MongoDBUser
        return MongoDBUser(email=user["email"], user_id=user["_id"])