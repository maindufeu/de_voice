# API de Streaming con FastAPI para Modelos de Lenguaje

Esta API permite interactuar con modelos de lenguaje de Azure OpenAI con capacidades de streaming y procesamiento especial para análisis de datos y búsqueda web.

## Estructura del Proyecto

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── chat.py
│           └── status.py
├── core/
│   └── config.py
├── schemas/
│   ├── chat.py
│   └── status.py
├── services/
│   ├── DataAnalytics/
│   │   └── DataAnalytics.py
│   └── WebSearch/
└── main.py
```

## Características

- Respuestas en streaming para modelos de lenguaje
- Capacidad para realizar procesamiento adicional (análisis de datos, búsqueda web)
- Integración con Azure OpenAI
- Endpoints para monitoreo del estado de la API

## Configuración

1. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`.

## Documentación API

Una vez iniciada la aplicación, puedes acceder a la documentación interactiva en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Ejemplo de Uso

### Solicitud de Chat con Streaming

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/chat' \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Hola, ¿cómo estás?"}
    ],
    "model": "gpt-4",
    "stream": true
  }'
```

## Servicios Adicionales

### Análisis de Datos
(Próximamente)

### Búsqueda Web
(Próximamente)

## Requisitos

- Python 3.8+
- FastAPI
- Pydantic
- Azure OpenAI SDK
- SSE-Starlette


