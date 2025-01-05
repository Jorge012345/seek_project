# Book Management API

## Overview
The **Book Management API** is a Django-based server for managing books in a library. This API allows users to perform CRUD operations on books, calculate average prices by year, and manage users with authentication. The API provides interactive documentation using **Swagger UI** and **ReDoc**.

---

## API Endpoints

### Books
- **List Books**: `GET /books/`  
  Retrieves a list of all books in the library.

- **Create Book**: `POST /books/`  
  Adds a new book to the library. Requires authentication.

- **Get Book Details**: `GET /books/{id}/`  
  Retrieves details of a specific book by its ID.

- **Update Book**: `PUT /books/{id}/`  
  Updates an existing book's details by its ID. Requires authentication.

- **Delete Book**: `DELETE /books/{id}/`  
  Deletes a specific book by its ID. Requires authentication.

- **Get Average Price by Year**: `GET /books/average-price/{year}/`  
  Calculates and retrieves the average price of books published in a specific year.

### Login
- **User Login**: `POST /login/`  
  Authenticates a user and returns an access token.

### Token
- **Refresh Token**: `POST /token/refresh/`  
  Refreshes the access token using a valid refresh token.

### Users
- **Create User**: `POST /users/`  
  Creates a new user account in the system.

---

## Requirements
- Python 3.12+
- Django REST Framework
- Docker
- AWS CLI
- Elastic Beanstalk CLI (EB CLI)

---

## Usage

### Local Development
To run the server locally, follow these steps:

1. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the development server:
    ```sh
    python manage.py runserver
    ```

3. Open your browser and navigate to:
    ```
    http://localhost:8000/swagger/
    ```
    Here you can interact with the API documentation using **Swagger UI**.

---

### Running with Docker

To containerize the server and run it in Docker:

1. Build the Docker image:
    ```sh
    docker build -t book-management-api .
    ```

2. Start the Docker container:
    ```sh
    docker run -p 80:80 book-management-api
    ```

3. Open your browser and navigate to:
    ```
    http://localhost/swagger/
    ```

---

### Deployment to AWS

This project uses Elastic Beanstalk to deploy the API.

1. Install the Elastic Beanstalk CLI:
    ```sh
    pip install awsebcli
    ```

2. Initialize the Elastic Beanstalk environment:
    ```sh
    eb init -p docker book-management --region us-east-1
    eb create book-management-env --region us-east-1

    ```

3. Deploy the service:
    ```sh
    eb deploy
    ```

4. The deployment output will provide the URL to access your API. To view the API documentation:
    - Swagger UI: Append `/swagger/` to the URL.

---

## Authentication

The API uses **JWT (JSON Web Tokens)** for authentication. Include the token in the `Authorization` header of your requests as follows:

```http
Authorization: Bearer <access_token>