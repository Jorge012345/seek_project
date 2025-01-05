from django.core.management.base import BaseCommand
from django.conf import settings
from bson import ObjectId

class Command(BaseCommand):
    help = "Poblar la colección de libros con datos iniciales"

    def handle(self, *args, **kwargs):
        book_collection = settings.MONGO_DB['Book']

        # Datos iniciales de ejemplo
        books = [
            {
                "_id": ObjectId(),
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "published_date": "2008-08-01",
                "genre": "Software Engineering",
                "price": 30.5
            },
            {
                "_id": ObjectId(),
                "title": "The Pragmatic Programmer",
                "author": "Andrew Hunt",
                "published_date": "1999-10-30",
                "genre": "Programming",
                "price": 40.0
            },
            {
                "_id": ObjectId(),
                "title": "Introduction to Algorithms",
                "author": "Thomas H. Cormen",
                "published_date": "2009-07-31",
                "genre": "Algorithms",
                "price": 70.0
            },
            {
                "_id": ObjectId(),
                "title": "Design Patterns",
                "author": "Erich Gamma",
                "published_date": "1994-11-10",
                "genre": "Software Design",
                "price": 50.0
            },
            {
                "_id": ObjectId(),
                "title": "The Mythical Man-Month",
                "author": "Frederick P. Brooks Jr.",
                "published_date": "1975-01-01",
                "genre": "Software Project Management",
                "price": 25.0
            }
        ]

        # Insertar datos en la colección
        result = book_collection.insert_many(books)
        self.stdout.write(self.style.SUCCESS(f"{len(result.inserted_ids)} libros añadidos a la colección."))