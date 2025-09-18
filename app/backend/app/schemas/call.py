from pydantic import BaseModel, Field
from typing import Optional

class SpeechRequest(BaseModel):
    text: str
    voice_name: Optional[str] = None
    language: Optional[str] = "es-ES"
    speed: Optional[str] = "medium"  # Nueva opción para controlar la velocidad

class SpeechResponse(BaseModel):
    audio: Optional[str] = None
    error: Optional[str] = None
    
class SpeechChunkResponse(BaseModel):
    chunk: Optional[str] = None
    done: bool = False
    error: Optional[str] = None