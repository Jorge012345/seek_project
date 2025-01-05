from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

# Clase para representar un usuario de MongoDB
class MongoDBUser:
    def __init__(self, email, user_id):
        self.email = email
        self.id = str(user_id)  # El atributo `id` es necesario para JWT

    @property
    def is_authenticated(self):
        return True

# Función para generar tokens JWT
def create_tokens_for_mongo_user(email):
    # Acceso a la colección de usuarios
    user_collection = settings.MONGO_DB['User']

    # Buscar al usuario en MongoDB
    user = user_collection.find_one({"email": email})
    if not user:
        raise ValueError("El usuario no existe en la base de datos.")

    # Crear la instancia de MongoDBUser
    mongo_user = MongoDBUser(email=email, user_id=user["_id"])

    # Generar los tokens JWT
    refresh = RefreshToken.for_user(mongo_user)
    return refresh, refresh.access_token