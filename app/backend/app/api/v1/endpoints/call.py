import asyncio
import re
import json
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.chat.agent_manager import process_user_message
from services.speech.speech import stream_text_to_speech
from services.chat.messages import create_message
from services.chat.memory import memory_service
from core.logger import logger
from typing import List, Dict, Optional, AsyncGenerator, Tuple, Set
from collections import deque

router = APIRouter()

# WebSocket connections registry
active_connections = {}

class TextFragment:
    """Representa un fragmento de texto para síntesis"""
    def __init__(self, text: str, sequence_id: int, is_final: bool = False):
        self.text = text
        self.sequence_id = sequence_id
        self.is_final = is_final
        self.processed = False

class AudioFragment:
    """Representa un fragmento de audio sintetizado"""
    def __init__(self, audio_data: bytes, text: str, sequence_id: int, is_final: bool = False):
        self.audio_data = audio_data
        self.text = text
        self.sequence_id = sequence_id
        self.is_final = is_final
        self.sent = False

class StreamingSpeechManager:
    """Administra la síntesis de voz en streaming con procesamiento paralelo"""
    
    # Patrones para identificar puntos de segmentación del texto
    SEGMENT_PATTERNS = [
        r'[.!?;](\s|$)',  # Puntuación seguida de espacio o fin
        r'\n',            # Saltos de línea
        r', ',            # Comas con espacio
        r': ',            # Dos puntos con espacio
    ]
    
    def __init__(self, websocket: WebSocket, voice_preference: str = "es-ES-ElviraNeural"):
        self.websocket = websocket
        self.voice_preference = voice_preference
        self.text_buffer = ""
        self.text_queue = asyncio.Queue()
        self.audio_queue = asyncio.Queue()
        self.min_segment_length = 10  # Caracteres mínimos para un segmento
        self.optimal_segment_length = 50  # Longitud óptima para un segmento
        self.max_segment_length = 150  # Longitud máxima antes de forzar segmentación
        self.next_sequence_id = 0
        self.synthesizer_tasks = set()
        self.is_running = True
        self.processing_complete = asyncio.Event()
        
    async def start(self, num_workers: int = 2):
        """Inicia los procesos de síntesis y envío de audio"""
        # Crear tareas para procesar texto y enviar audio
        text_processor = asyncio.create_task(self.process_text_buffer())
        audio_sender = asyncio.create_task(self.send_audio_fragments())
        
        # Crear workers de síntesis
        workers = []
        for _ in range(num_workers):
            worker = asyncio.create_task(self.synthesis_worker())
            workers.append(worker)
            self.synthesizer_tasks.add(worker)
        
        # Guardar todas las tareas para referencia
        self.tasks = [text_processor, audio_sender] + workers
        
    async def stop(self):
        """Detiene todos los procesos y libera recursos"""
        self.is_running = False
        
        # Procesar cualquier texto restante
        if self.text_buffer:
            await self.segment_and_queue_text(self.text_buffer, is_final=True)
            self.text_buffer = ""
        
        # Marcar fin de cola para que los workers terminen
        await self.text_queue.put(None)
        
        # Esperar a que terminen los workers
        if self.synthesizer_tasks:
            await asyncio.wait(self.synthesizer_tasks)
        
        # Esperar a que se vacíe la cola de audio
        self.processing_complete.set()
        
        # Cancelar tareas restantes
        for task in self.tasks:
            if not task.done():
                task.cancel()
    
    def add_text(self, text: str):
        """Añade texto al buffer de procesamiento"""
        self.text_buffer += text
    
    async def process_text_buffer(self):
        """Procesa el buffer de texto continuamente, segmentándolo en fragmentos coherentes"""
        try:
            while self.is_running:
                if len(self.text_buffer) >= self.min_segment_length:
                    # Buscar un punto de segmentación adecuado
                    segment_text, remaining = self.find_segment(self.text_buffer)
                    
                    if segment_text:
                        # Encolar el segmento para síntesis
                        await self.segment_and_queue_text(segment_text)
                        self.text_buffer = remaining
                
                # Pausa breve para permitir que se acumule más texto
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            logger.info("Procesador de texto cancelado")
        except Exception as e:
            logger.error(f"Error en process_text_buffer: {e}")
    
    def find_segment(self, text: str) -> Tuple[str, str]:
        """
        Encuentra un segmento coherente en el texto.
        Retorna una tupla (segmento, texto_restante)
        """
        # Si el texto es muy corto, no segmentar
        if len(text) < self.min_segment_length:
            return "", text
        
        # Si el texto es muy largo, segmentar en el punto máximo
        if len(text) > self.max_segment_length:
            # Buscar un punto natural de segmentación dentro del límite
            for pattern in self.SEGMENT_PATTERNS:
                matches = list(re.finditer(pattern, text[:self.max_segment_length]))
                if matches:
                    # Usar el último match encontrado
                    last_match = matches[-1]
                    end_pos = last_match.end()
                    return text[:end_pos], text[end_pos:]
            
            # Si no hay puntos naturales, segmentar en un espacio cercano al límite
            space_pos = text[:self.max_segment_length].rfind(' ', self.min_segment_length)
            if space_pos > self.min_segment_length:
                return text[:space_pos+1], text[space_pos+1:]
            
            # Si todo falla, segmentar en el límite máximo
            return text[:self.max_segment_length], text[self.max_segment_length:]
        
        # Buscar puntos naturales de segmentación
        best_end = -1
        
        # Revisar cada patrón para encontrar un buen punto de corte
        for pattern in self.SEGMENT_PATTERNS:
            matches = list(re.finditer(pattern, text))
            if matches:
                for match in matches:
                    end_pos = match.end()
                    # Verificar si está en un rango óptimo
                    if end_pos >= self.min_segment_length and (
                        best_end == -1 or 
                        abs(end_pos - self.optimal_segment_length) < abs(best_end - self.optimal_segment_length)
                    ):
                        best_end = end_pos
        
        # Si encontramos un buen punto de segmentación
        if best_end > 0:
            return text[:best_end], text[best_end:]
        
        # Si no hay suficiente texto o no encontramos un buen punto, no segmentar
        return "", text
    
    async def segment_and_queue_text(self, text: str, is_final: bool = False):
        """Segmenta y encola el texto para síntesis"""
        # Ignorar texto vacío
        if not text.strip():
            return
            
        fragment = TextFragment(
            text=text.strip(),
            sequence_id=self.next_sequence_id,
            is_final=is_final
        )
        self.next_sequence_id += 1
        
        await self.text_queue.put(fragment)
        logger.debug(f"Texto encolado para síntesis: '{text[:30]}...' (seq: {fragment.sequence_id})")
    
    async def synthesis_worker(self):
        """Worker que toma fragmentos de texto y los convierte en audio"""
        try:
            while self.is_running:
                # Obtener siguiente fragmento de texto
                fragment = await self.text_queue.get()
                
                # None marca el fin de la cola
                if fragment is None:
                    # Reencolar None para el siguiente worker
                    await self.text_queue.put(None)
                    break
                
                try:
                    logger.info(f"Sintetizando fragmento: '{fragment.text[:30]}...' (seq: {fragment.sequence_id})")
                    
                    # Usar el servicio de streaming para la síntesis
                    audio_chunks = []
                    async for chunk in stream_text_to_speech(fragment.text, self.voice_preference):
                        audio_chunks.append(chunk)
                    
                    # Si obtuvimos audio, encolar para envío
                    if audio_chunks:
                        audio_data = b''.join(audio_chunks)
                        audio_fragment = AudioFragment(
                            audio_data=audio_data,
                            text=fragment.text,
                            sequence_id=fragment.sequence_id,
                            is_final=fragment.is_final
                        )
                        await self.audio_queue.put(audio_fragment)
                        logger.info(f"Audio sintetizado: {len(audio_data)} bytes (seq: {fragment.sequence_id})")
                    else:
                        logger.warning(f"No se generó audio para: '{fragment.text[:30]}...' (seq: {fragment.sequence_id})")
                
                except Exception as e:
                    logger.error(f"Error sintetizando fragmento {fragment.sequence_id}: {e}")
                
                finally:
                    # Marcar como procesado
                    fragment.processed = True
                    self.text_queue.task_done()
        
        except asyncio.CancelledError:
            logger.info("Worker de síntesis cancelado")
        except Exception as e:
            logger.error(f"Error en synthesis_worker: {e}")
    
    async def send_audio_fragments(self):
        """Envía fragmentos de audio al cliente en orden secuencial"""
        try:
            next_sequence_id = 0
            pending_fragments = {}
            
            while True:
                # Verificar si debemos terminar
                if not self.is_running and self.processing_complete.is_set() and self.audio_queue.empty():
                    break
                
                try:
                    # Obtener próximo fragmento
                    fragment = await asyncio.wait_for(
                        self.audio_queue.get(), 
                        timeout=0.5
                    )
                    
                    # Almacenar en pendientes si no es el siguiente en secuencia
                    if fragment.sequence_id != next_sequence_id:
                        pending_fragments[fragment.sequence_id] = fragment
                        continue
                    
                    # Enviar el fragmento actual
                    await self._send_audio_fragment(fragment)
                    next_sequence_id += 1
                    
                    # Enviar fragmentos pendientes que están en secuencia
                    while next_sequence_id in pending_fragments:
                        await self._send_audio_fragment(pending_fragments[next_sequence_id])
                        del pending_fragments[next_sequence_id]
                        next_sequence_id += 1
                    
                except asyncio.TimeoutError:
                    # Timeout es normal, seguimos esperando o verificamos terminación
                    pass
        
        except asyncio.CancelledError:
            logger.info("Enviador de audio cancelado")
        except Exception as e:
            logger.error(f"Error en send_audio_fragments: {e}")
    
    async def _send_audio_fragment(self, fragment: AudioFragment):
        """Envía un fragmento de audio al cliente"""
        if fragment.sent:
            return
            
        try:
            audio_base64 = base64.b64encode(fragment.audio_data).decode("utf-8")
            await self.websocket.send_json({
                "type": "audio", 
                "content": audio_base64,
                "text": fragment.text,
                "final": fragment.is_final
            })
            fragment.sent = True
            logger.info(f"Audio enviado: {len(fragment.audio_data)} bytes (seq: {fragment.sequence_id})")
        except Exception as e:
            logger.error(f"Error enviando audio {fragment.sequence_id}: {e}")
        finally:
            self.audio_queue.task_done()

@router.websocket("/ws/speech/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for voice chat with streaming responses"""
    await websocket.accept()
    active_connections[client_id] = websocket
    logger.info(f"Client connected: {client_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process different message types
            if message_data.get("type") == "chat":
                await handle_chat_message(websocket, client_id, message_data)
            elif message_data.get("type") == "tts":
                await handle_tts_message(websocket, message_data)
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {client_id}")
        active_connections.pop(client_id, None)
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
        active_connections.pop(client_id, None)


async def handle_chat_message(websocket: WebSocket, client_id: str, message_data: dict):
    """Handle chat type messages with AI responses and speech synthesis"""
    logger.info("Processing chat message")
    user_message = message_data.get("message", "")
    voice_preference = message_data.get("voice", "es-ES-ElviraNeural")
    
    if not user_message:
        await websocket.send_json({
            "type": "error", 
            "content": {
                "text": "Mensaje vacío",
                "error": "Empty message"
            }
        })
        return
    
    # Start response
    await websocket.send_json({"type": "start_response"})
    
    # Initialize streaming speech manager with parallel processing
    speech_manager = StreamingSpeechManager(websocket, voice_preference)
    await speech_manager.start(num_workers=2)  # Iniciar con 2 workers paralelos
    
    full_response = ""
    
    # Add the user message to memory
    memory_service.add_message(client_id, "user", user_message)
    
    try:
        # Process messages using process_user_message
        async for message in process_user_message(client_id, user_message):
            # If message is a dictionary, it's already in the standardized format
            if isinstance(message, dict):
                # Send the standardized message to the client
                await websocket.send_json(message)
                
                # Skip break messages
                if message.get("type") == "break_of_message":
                    continue
                
                # Check if this is a text message to be spoken
                if message.get("type") == "text" and message.get("content", {}).get("text"):
                    text_content = message["content"]["text"]
                    full_response += text_content
                    
                    # Add to streaming speech manager
                    speech_manager.add_text(text_content)
                    
                # Handle completion messages
                elif message.get("type") == "completion":
                    # For completions, we append the text to the full response
                    if message.get("content", {}).get("text"):
                        full_response += message["content"]["text"]
            
            # If message is a string, convert it to the standardized format and process
            elif isinstance(message, str):
                # Create a standardized text message
                text_message = create_message("text", text=message)
                
                # Send the standardized message to the client
                await websocket.send_json(text_message)
                
                # Add to streaming manager
                full_response += message
                speech_manager.add_text(message)
        await asyncio.sleep(0.15)  # Small delay to allow for processing
        # Process any remaining text and complete synthesis
        await speech_manager.stop()
        
        # Add the assistant's message to memory
        memory_service.add_message(client_id, "assistant", full_response)
        
        # Send completion message
        await websocket.send_json({
            "type": "completion", 
            "content": {
                "progress": 100
            }
        })
        
        # Then send end_response
        await websocket.send_json({
            "type": "end_response", 
            "content": {
                "status": "completed",
            }
        })
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        await websocket.send_json({
            "type": "error", 
            "content": {
                "text": f"Error: {str(e)}",
                "error": str(e)
            }
        })
    
    finally:
        # Ensure speech manager is stopped
        await speech_manager.stop()


async def handle_tts_message(websocket: WebSocket, message_data: dict):
    """Handle direct text-to-speech requests"""
    logger.info("Processing direct TTS request")
    text = message_data.get("text", "")
    voice = message_data.get("voice", "es-ES-ElviraNeural")
    speed = message_data.get("speed", "medium")
    
    if not text:
        await websocket.send_json({
            "type": "error", 
            "content": {
                "text": "Texto vacío",
                "error": "Empty text"
            }
        })
        return
    
    try:
        # Use the streaming method for direct TTS requests
        audio_chunks = []
        async for chunk in stream_text_to_speech(text, voice, speed):
            audio_chunks.append(chunk)
        
        if audio_chunks:
            audio_data = b''.join(audio_chunks)
            # Send audio to client
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            await websocket.send_json({
                "type": "audio", 
                "content": audio_base64,
                "text": text
            })
        else:
            await websocket.send_json({
                "type": "error", 
                "content": {
                    "text": "No se pudo generar audio",
                    "error": "Failed to generate audio"
                }
            })
    except Exception as e:
        await websocket.send_json({
            "type": "error", 
            "content": {
                "text": f"Error en síntesis: {str(e)}",
                "error": str(e)
            }
        })