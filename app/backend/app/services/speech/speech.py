import asyncio
import azure.cognitiveservices.speech as speechsdk
from core.config import settings
from core.logger import logger
from concurrent.futures import ThreadPoolExecutor
from services.speech.client import SpeechClient

# Thread pool executor for speech synthesis
speech_executor = ThreadPoolExecutor(max_workers=4)

async def text_to_speech(text: str, voice_name: str = "es-ES-ElviraNeural"):
    """
    Convert text to speech using Azure Speech Services.
    This is an async wrapper around the streaming speech client.
    
    Args:
        text: The text to convert to speech
        voice_name: The voice to use (e.g., "es-ES-ElviraNeural")
        
    Returns:
        Audio data (bytes) or None if synthesis fails
    """
    logger.info(f"Starting TTS for: '{text[:30]}...' with voice {voice_name}")
    
    try:
        # Get speech client instance
        client = SpeechClient.get_instance(settings.SPEECH_SYNTHESIS_POOL_SIZE)
        
        # Use thread pool to process the streaming output and collect all chunks
        loop = asyncio.get_event_loop()
        
        # Use a function to collect all audio chunks into a single byte array
        def collect_audio_data():
            audio_chunks = []
            
            # Collect all chunks from the iterator
            for chunk in client.text_to_speech(text, voice_name):
                audio_chunks.append(chunk)
                
            # Combine all chunks
            if audio_chunks:
                return b''.join(audio_chunks)
            else:
                return None
        
        # Execute in thread pool
        audio_data = await loop.run_in_executor(speech_executor, collect_audio_data)
        
        if audio_data and len(audio_data) > 0:
            logger.info(f"Successfully collected {len(audio_data)} bytes of audio data")
            return audio_data
        else:
            logger.warning("No audio data generated")
            return None
            
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        return None

async def stream_text_to_speech(text: str, voice_name: str = "es-ES-ElviraNeural", speed: str = "medium"):
    """
    Stream text to speech using Azure Speech Services.
    With the updated client, this now returns a complete WAV file to maintain compatibility.
    
    Args:
        text: The text to convert to speech
        voice_name: The voice to use (e.g., "es-ES-ElviraNeural")
        speed: The speed of speech ("slow", "medium", "fast")
        
    Yields:
        Audio data as a complete WAV file (bytes)
    """
    logger.info(f"Starting streaming TTS for: '{text[:30]}...' with voice {voice_name}")
    
    try:
        # Get speech client instance
        client = SpeechClient.get_instance(settings.SPEECH_SYNTHESIS_POOL_SIZE)
        
        # Execute in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def get_audio_data():
            # The client now returns a single complete WAV file
            for audio_data in client.text_to_speech(text, voice_name, speed):
                return audio_data  # Return the first (and only) chunk
            return None
            
        # Get the audio data
        audio_data = await loop.run_in_executor(speech_executor, get_audio_data)
        
        if audio_data:
            # Log the header for debugging
            if len(audio_data) > 10:
                try:
                    header = audio_data[:4].decode('utf-8', errors='ignore')
                    logger.info(f"Audio streaming - WAV header check: {header}")
                except Exception as e:
                    logger.error(f"Error checking streamed WAV header: {e}")
            
            # Yield the complete audio file
            yield audio_data
    except Exception as e:
        logger.error(f"Error in stream_text_to_speech: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in stream_text_to_speech: {str(e)}")
        
        
# import asyncio
# import azure.cognitiveservices.speech as speechsdk
# from core.config import get_speech_config
# from core.logger import logger
# from concurrent.futures import ThreadPoolExecutor

# # Thread pool executor for speech synthesis
# speech_executor = ThreadPoolExecutor(max_workers=4)

# async def text_to_speech(text: str, voice_name: str = "es-ES-ElviraNeural"):
#     """Convert text to speech using Azure Speech Services"""
#     logger.info(f"Starting TTS for: '{text[:30]}...' with voice {voice_name}")
    
#     try:
#         speech_config = get_speech_config()
#         speech_config.speech_synthesis_voice_name = voice_name
        
#         # Configure for direct audio data output
#         speech_config.set_speech_synthesis_output_format(
#             speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
        
#         # Create synthesizer with no audio output config
#         synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        
#         # Execute synthesis in thread pool
#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(
#             speech_executor, 
#             lambda: synthesizer.speak_text_async(text).get()
#         )
        
#         if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
#             logger.error(f"Synthesis error: {result.reason}")
#             if result.reason == speechsdk.ResultReason.Canceled:
#                 cancellation = result.cancellation_details
#                 logger.error(f"Cancellation error: {cancellation.reason}")
#                 logger.error(f"Details: {cancellation.error_details}")
#             return None
        
#         # Access audio data directly from the result
#         audio_data = result.audio_data
        
#         if audio_data and len(audio_data) > 0:
#             logger.info(f"Successfully generated {len(audio_data)} bytes of audio data")
#             return audio_data
#         else:
#             logger.warning("No audio data generated")
#             return None
        
#     except Exception as e:
#         logger.error(f"Error in text_to_speech: {str(e)}")
#         return None