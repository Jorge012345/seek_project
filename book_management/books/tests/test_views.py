import pytest
from rest_framework.test import APIClient
from django.conf import settings
from werkzeug.security import generate_password_hash
from bson import ObjectId

# Configuración del cliente de pruebas
client = APIClient()

# Colecciones de usuarios y libros en MongoDB
user_collection = settings.MONGO_DB['User']
book_collection = settings.MONGO_DB['Book']

@pytest.fixture(autouse=True)
def cleanup():
    """
    Limpia las colecciones de prueba antes y después de cada prueba.
    """
    user_collection.delete_many({})
    book_collection.delete_many({})
    yield
    user_collection.delete_many({})
    book_collection.delete_many({})

@pytest.fixture
def setup_user():
    """
    Crea un usuario de prueba en la base de datos.
    """
    user = {
        "_id": ObjectId(),
        "email": "testuser@example.com",
        "password": generate_password_hash("mypassword")  # Contraseña hasheada
    }
    user_collection.insert_one(user)
    yield user
    user_collection.delete_one({"_id": user["_id"]})

@pytest.fixture
def setup_auth_token(setup_user):
    """
    Devuelve un token de autenticación para el usuario de prueba.
    """
    response = client.post('/api/login/', {
        "email": setup_user["email"],
        "password": "mypassword"
    })
    assert response.status_code == 200
    return response.data["access"]

def test_create_user_success():
    """
    Prueba que se pueda crear un usuario correctamente.
    """
    response = client.post('/api/users/', {
        "email": "newuser@example.com",
        "password": "mypassword"
    })

    # Verificar que el usuario fue creado exitosamente
    assert response.status_code == 201
    assert response.data["message"] == "Usuario creado exitosamente."

    # Verificar que el usuario esté en la base de datos
    user = user_collection.find_one({"email": "newuser@example.com"})
    assert user is not None
    assert user["email"] == "newuser@example.com"

def test_create_user_duplicate_email():
    """
    Prueba que no se permita crear un usuario con un correo duplicado.
    """
    # Crear un usuario inicial
    user_collection.insert_one({
        "_id": ObjectId(),
        "email": "duplicate@example.com",
        "password": generate_password_hash("mypassword")
    })

    # Intentar crear un usuario con el mismo correo
    response = client.post('/api/users/', {
        "email": "duplicate@example.com",
        "password": "mypassword"
    })

    # Verificar que se retorna un error
    assert response.status_code == 400
    assert response.data["email"][0] == "El correo ya está registrado."

def test_login_success(setup_user):
    """
    Prueba que un usuario pueda iniciar sesión correctamente.
    """
    response = client.post('/api/login/', {
        "email": setup_user["email"],
        "password": "mypassword"
    })

    # Verificar que el login fue exitoso
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

def test_login_invalid_credentials(setup_user):
    """
    Prueba que no se pueda iniciar sesión con credenciales incorrectas.
    """
    response = client.post('/api/login/', {
        "email": setup_user["email"],
        "password": "wrongpassword"
    })

    # Verificar que se retorna un error
    assert response.status_code == 401
    assert response.data["error"] == "Credenciales inválidas."

def test_create_book_success(setup_auth_token):
    """
    Prueba que se pueda crear un libro correctamente.
    """
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {setup_auth_token}')
    response = client.post('/api/books/', {
        "title": "Book Title",
        "author": "Author Name",
        "published_date": "2023-01-01",
        "genre": "Fiction",
        "price": 19.99
    })

    # Verificar que el libro fue creado exitosamente
    assert response.status_code == 201
    assert response.data["title"] == "Book Title"

    # Verificar que el libro esté en la base de datos
    book = book_collection.find_one({"title": "Book Title"})
    assert book is not None
    assert book["author"] == "Author Name"

def test_create_book_unauthorized():
    """
    Prueba que no se pueda crear un libro sin autenticación.
    """
    # Limpiar credenciales del cliente
    client.credentials()  # Esto elimina cualquier token de autenticación configurado

    response = client.post('/api/books/', {
        "title": "Unauthorized Book",
        "author": "Author Name",
        "published_date": "2023-01-01",
        "genre": "Non-Fiction",
        "price": 29.99
    })

    # Verificar que se retorna un error de autenticación
    assert response.status_code == 401
    assert response.data["detail"] == "Authentication credentials were not provided."