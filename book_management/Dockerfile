# Usar una imagen oficial de Python 3.12 como base
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app/

# Copiar el archivo .env al contenedor
COPY .env /app/.env

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Gunicorn
RUN pip install gunicorn

# Exponer el puerto 80 para que el balanceador de carga pueda conectarse
EXPOSE 80

# Ejecutar collectstatic antes de iniciar Gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:80 book_management.wsgi:application"]