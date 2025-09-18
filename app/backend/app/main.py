from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logger import logger
from api.v1.endpoints import chat, call
from services.temporal_memory.cleanup import scheduled_cleanup

from fastapi import FastAPI
from api.v1.api import api_router
from core.config import settings

app = FastAPI(title=settings.APP_TITLE)
scheduled_cleanup()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)



@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "API de Chat y Voz funcionando. Endpoints disponibles: /chat, /text-to-speech, /ws/speech/{client_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)