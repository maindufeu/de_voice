import logging
import typing

import azure.cognitiveservices.speech as speechsdk
import numpy as np
from core.logger import logger

def calculate_energy(frame_data):
    """Calculate the energy of an audio frame to detect silence"""
    # Convert the byte data to a numpy array for easier processing (assuming 16-bit PCM)
    data = np.frombuffer(frame_data, dtype=np.int16)
    # Calculate the energy as the sum of squares of the samples
    energy = np.sum(data**2) / len(data)
    return energy


class SpeechClient:
    """Azure Speech Client with streaming and silence detection capabilities"""
    _instance = None
    
    @classmethod
    def get_instance(cls, synthesis_pool_size: int = 2):
        """Get the singleton instance of the speech client"""
        if cls._instance is None:
            cls._instance = cls(synthesis_pool_size)
        return cls._instance
    
    def __init__(self, synthesis_pool_size: int = 2):
        """Initialize the speech client with a pool of synthesizers"""
        from core.config import settings
        
        if synthesis_pool_size < 1:
            raise ValueError("synthesis_pool_size must be at least 1")
            
        speech_key = settings.SPEECH_KEY
        speech_region = settings.SPEECH_REGION
        speech_resource_id = settings.SPEECH_RESOURCE_ID
        
        # Validate required configuration
        if not speech_region:
            raise ValueError("SPEECH_REGION must be set")
        if not (speech_key or speech_resource_id):
            raise ValueError("Either SPEECH_KEY or SPEECH_RESOURCE_ID must be set")
        
        # Initialize speech configuration based on available credentials
        if speech_key:
            self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        else:
            raise ValueError("SPEECH_KEY is required for authentication")
        # Configure output format (RIFF WAV format for browser compatibility)
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
        )
        
        # Create a pool of synthesizers for load balancing
        self.speech_synthesizers = [
            speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None) 
            for _ in range(synthesis_pool_size)
        ]
                
        # Counter for round-robin selection of synthesizers
        self._counter = 0
        
        logger.info(f"Speech client initialized with pool size: {synthesis_pool_size}")

    def text_to_speech(self, text: str, voice: str, speed: str = "medium") -> typing.Iterator[bytes]:
        """
        Convert text to speech and yield audio chunks as they become available.
        
        Args:
            text: The text to convert to speech
            voice: The voice to use (e.g., "es-ES-ElviraNeural")
            speed: The speed of speech ("slow", "medium", "fast")
            
        Yields:
            Audio data chunks (bytes)
        """
        logger.info(f"Starting streaming TTS for: '{text[:30]}...' with voice {voice}")
        
        try:
            # Select next synthesizer in the pool using round-robin
            self._counter = (self._counter + 1) % len(self.speech_synthesizers)
            current_synthesizer = self.speech_synthesizers[self._counter]
            
            # Set the voice property
            current_synthesizer.properties.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_SynthVoice, 
                voice
            )
            
            # Create SSML with prosody for speed control
            ssml = f"""
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
                <voice name='{voice}'>
                    <prosody rate='{speed}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Start speaking with SSML - Use speak_ssml_async for WAV format
            result = current_synthesizer.speak_ssml_async(ssml).get()
            stream = speechsdk.AudioDataStream(result)

            # Check for success
            if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.error(f"Speech synthesis failed: {result.reason}")
                return
                
            # Get audio data as a single complete WAV file to ensure headers are correct
            audio_data = result.audio_data
            
            # Debug: Check WAV header
            if len(audio_data) > 10:
                try:
                    header = audio_data[:4].decode('utf-8', errors='ignore')
                    logger.info(f"WAV header check: {header}")
                except Exception as e:
                    logger.error(f"Error checking WAV header: {e}")
                    
            # Yield the entire WAV file as one chunk to preserve headers
            yield audio_data
            
            # Check for errors
            if stream.status != speechsdk.StreamStatus.AllData:
                logger.error(
                    f"Speech synthesis failed: {stream.status}, "
                    f"details: {stream.cancellation_details.error_details if hasattr(stream, 'cancellation_details') else 'Unknown error'}"
                )
                
        except Exception as e:
            logger.error(f"Error in streaming text_to_speech: {str(e)}")