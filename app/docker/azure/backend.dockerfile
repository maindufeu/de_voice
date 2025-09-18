FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para PyTorch
RUN apt-get update && \
    apt-get install -y curl unzip ffmpeg wget build-essential && \
    rm -rf /var/lib/apt/lists/*

# Manejar el .env
COPY ./app/backend/.env .env
ENV $(cat .env | xargs)

# Instalar dependencias de Python con configuraciones para PyTorch
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar PyTorch primero
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Instalar el resto de dependencias
COPY ./app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY ./app/backend/app .

# Crear directorio para datos si no existe
RUN mkdir -p data

# Establecer variables de entorno para optimizar el rendimiento
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TOKENIZERS_PARALLELISM=false

# Puerto que expondrá la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]