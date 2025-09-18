import asyncio
from typing import List, Dict, Union, AsyncGenerator
from langchain_openai import AzureChatOpenAI
from langchain_core.callbacks import CallbackManager
from langchain.callbacks import AsyncIteratorCallbackHandler
from core.config import settings
from core.logger import logger
from concurrent.futures import ThreadPoolExecutor

# Thread pool executor for OpenAI requests
chat_executor = ThreadPoolExecutor(max_workers=4)

async def send_message(message: Union[str, List[Dict[str, str]]],
                        model: str = settings.AZURE_OPENAI_MODEL,
                        deployment_name: str = settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                        azure_endpoint: str = settings.AZURE_OPENAI_ENDPOINT,
                        azure_api_version: str = settings.AZURE_OPENAI_API_VERSION,
                        max_tokens: int = 1000,
                        temperature: float = 0.7,
                       ) -> AsyncGenerator[str, None]:
    """
    Send message to Azure OpenAI and get streaming response
    
    Args:
        message: Either a string message or a list of message objects with role and content keys
        
    Yields:
        Tokens of the response as they are generated
    """
    callback = AsyncIteratorCallbackHandler()
    
    chat_client = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        deployment_name=deployment_name,
        model=model,
        callback_manager=CallbackManager([callback]),
        max_tokens=max_tokens,  # Increased max tokens to handle longer conversations
        api_version=azure_api_version,
        temperature=temperature,
        streaming=True,
        verbose=True,
    )
    
    async def wrap_done(awaitable_future, event):
        try:
            await awaitable_future
        except Exception as e:
            logger.error(f"Error in OpenAI request: {e}")
        finally:
            event.set()
    
    # Format the message appropriately based on input type
    formatted_messages = message
    if isinstance(message, str):
        formatted_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    
    # Execute in task
    task = asyncio.create_task(
        wrap_done(chat_client.ainvoke(formatted_messages), callback.done)
    )

    async for token in callback.aiter():
        yield token
    
    await task



def create_message(message_type, text=None, progress=None, data=None, images=None, error=None, **metadata):
    """
    Create a standardized message for client communication.
    
    Args:
        message_type (str): One of "text", "progress", "data", "completion", "break", "error", "backend_process",
                           "planning_token", "code_token", "planning_start", "planning_complete", etc.
        text (str, optional): Text content
        progress (int, optional): Progress percentage (0-100)
        data (Any, optional): Structured data payload
        images (List[str], optional): List of base64-encoded images
        error (str, optional): Error details for error type messages
        **metadata: Additional metadata fields (e.g., facialExpression, animation, process_type)
    
    Returns:
        dict: Standardized message object
    """
    message = {"type": message_type}
    
    # Only add content if we have any content fields
    if any(x is not None for x in [text, progress, data, images, error]) or metadata:
        message["content"] = {}
        
        if text is not None:
            message["content"]["text"] = text
            
        if progress is not None:
            message["content"]["progress"] = progress
            
        if data is not None:
            message["content"]["data"] = data
            
        if images is not None:
            message["content"]["images"] = images
            
        if error is not None:
            message["content"]["error"] = error
            
        if metadata:
            message["content"]["metadata"] = metadata
    
    return message
