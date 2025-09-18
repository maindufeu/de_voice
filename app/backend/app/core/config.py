import os
from dotenv import load_dotenv
from typing import List
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

class Settings:
    # App settings
    APP_TITLE: str = "Chat API con Azure OpenAI y Azure Speech Services"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Speech settings
    SPEECH_KEY: str = os.getenv("SPEECH_KEY", "")
    SPEECH_REGION: str = os.getenv("SPEECH_REGION", "")
    SPEECH_ENDPOINT: str = os.getenv("SPEECH_ENDPOINT", "")
    # Nuevas configuraciones para el cliente de voz mejorado
    SPEECH_RESOURCE_ID: str = os.getenv("SPEECH_RESOURCE_ID", "")
    SPEECH_SYNTHESIS_POOL_SIZE: int = int(os.getenv("SPEECH_SYNTHESIS_POOL_SIZE", "2"))
    MAX_CONVERSATION_MEMORY: int = int(os.getenv("MAX_CONVERSATION_MEMORY", "10"))
    # Azure OpenAI settings
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    AZURE_OPENAI_MODEL: str = os.getenv("AZURE_OPENAI_MODEL", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")

    DATA_ANALYSIS_DIRECTORY = os.getenv(
    "DATA_ANALYSIS_DIRECTORY", 
    "services/DataAnalysisFlow/data"
    )
    
    # Validation
    def validate(self):
        if not self.SPEECH_REGION:
            raise ValueError("SPEECH_REGION must be set as environment variable")
        if not (self.SPEECH_KEY or self.SPEECH_RESOURCE_ID):
            raise ValueError("Either SPEECH_KEY or SPEECH_RESOURCE_ID must be set as environment variable")
        if not self.AZURE_OPENAI_DEPLOYMENT_NAME or not self.AZURE_OPENAI_MODEL:
            raise ValueError("Azure OpenAI environment variables are not properly configured")

def get_speech_config():
    """Configure Azure Speech Services"""
    if not settings.SPEECH_KEY or not settings.SPEECH_REGION:
        raise ValueError("SPEECH_KEY and SPEECH_REGION must be set as environment variables")
    
    return speechsdk.SpeechConfig(
        subscription=settings.SPEECH_KEY, 
        endpoint=settings.SPEECH_ENDPOINT
    )

# Create global settings instance
settings = Settings()