from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    voice_enabled: bool = False

class ChatResponse(BaseModel):
    message: str