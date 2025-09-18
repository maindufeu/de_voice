from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from schemas.chat import ChatRequest
from schemas.call import SpeechRequest, SpeechResponse
from services.chat.agent_manager import process_user_message
from services.chat.messages import create_message
from services.speech.speech import text_to_speech, stream_text_to_speech
from core.logger import logger
import base64
import uuid
from typing import Optional
from pydantic import BaseModel
import json
router = APIRouter()

class SessionInfo(BaseModel):
    """Model for session information"""
    session_id: str

async def get_session_id(session_id: Optional[str] = None) -> str:
    """Get or create a session ID
    
    Args:
        session_id (str, optional): Existing session ID
        
    Returns:
        str: Session ID (existing or new)
    """
    if not session_id:
        Session = SessionInfo(session_id=str(uuid.uuid4()))
        return Session.session_id
    return SessionInfo(session_id=session_id).session_id



@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    session: SessionInfo = Depends(get_session_id)
):
    """
    Endpoint for text chat with intelligent agent routing and memory
    
    The endpoint streams the response as it's generated, handling both
    regular LLM responses and data analysis responses appropriately.
    """
    logger.info(f"Received chat request with session_id={session}")
    
    async def generate_response():
        async for token in process_user_message(session, request.message):
            # SSE format
            if isinstance(token, dict):
                # If the token is a dictionary, convert it to JSON string
                token = json.dumps(token)
            
            yield f"data: {token}\n\n"
        
        # End signal
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        content=generate_response(),
        media_type="text/event-stream"
    )

@router.post("/chat/reset")
async def reset_chat(session: SessionInfo = Depends(get_session_id)):
    """Reset the chat conversation history"""
    from services.chat.memory import memory_service
    
    try:
        memory_service.clear_conversation(session.session_id)
        return {"status": "success", "message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error resetting chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")

@router.post("/text-to-speech", response_model=SpeechResponse)
async def tts_endpoint(request: SpeechRequest):
    """Endpoint to convert text to speech audio"""
    logger.info(f"Received TTS request for text: {request.text[:30]}...")
    
    try:
        # Usar la implementación compatible con el cliente anterior
        audio_data = await text_to_speech(request.text, request.voice_name or "es-ES-ElviraNeural")
        
        if not audio_data:
            logger.warning("No audio data generated")
            return SpeechResponse(error="No se pudo sintetizar el audio")
        
        # Return base64 encoded audio
        return SpeechResponse(audio=base64.b64encode(audio_data).decode("utf-8"))
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        return SpeechResponse(error=str(e))

@router.post("/stream-text-to-speech")
async def stream_tts_endpoint(request: SpeechRequest):
    """Endpoint to stream text to speech audio in chunks"""
    logger.info(f"Received streaming TTS request for text: {request.text[:30]}...")
    
    async def generate_audio_stream():
        try:
            # Return audio chunks as they become available
            async for chunk in stream_text_to_speech(
                request.text, 
                request.voice_name or "es-ES-ElviraNeural",
                request.language or "medium"
            ):
                # Convertir cada chunk a base64 para streaming
                chunk_b64 = base64.b64encode(chunk).decode("utf-8")
                yield f'data: {{"chunk": "{chunk_b64}"}}\n\n'
                
            # Señalizar fin de stream
            yield 'data: {"done": true}\n\n'
        except Exception as e:
            logger.error(f"Error in stream_text_to_speech: {e}")
            yield f'data: {{"error": "{str(e)}"}}\n\n'
    
    return StreamingResponse(
        content=generate_audio_stream(),
        media_type="text/event-stream"
    )
