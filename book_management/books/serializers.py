from rest_framework import serializers
from werkzeug.security import generate_password_hash
from django.conf import settings

class BookSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    author = serializers.CharField(max_length=255)
    published_date = serializers.CharField(max_length=10)
    genre = serializers.CharField(max_length=100)
    price = serializers.FloatField()

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Verifica si el correo ya existe en la base de datos."""
        user_collection = settings.MONGO_DB['User']
        if user_collection.find_one({"email": value}):
            raise serializers.ValidationError("El correo ya está registrado.")
        return value

    def create(self, validated_data):
        """Hashea la contraseña y devuelve los datos del usuario."""
        validated_data['password'] = generate_password_hash(validated_data['password'])
        return validated_data