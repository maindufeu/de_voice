import asyncio
import logging
from ..abstract_llm_provider import LLMProvider
from typing import Dict, List, AsyncGenerator, Optional, Union

class AzureOpenAIProvider(LLMProvider):
    """LLM provider for Azure OpenAI."""
    
    def __init__(
        self, 
        azure_endpoint: str,
        deployment_name: str,
        model: str,
        api_version: str,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        logger: Optional[logging.Logger] = None
    ):
        self.azure_endpoint = azure_endpoint
        self.deployment_name = deployment_name
        self.model = model
        self.api_version = api_version
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logger or logging.getLogger(__name__)
    
    async def generate_response(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Union[Dict, AsyncGenerator[str, None]]:
        from langchain_openai import AzureChatOpenAI
        from langchain_core.callbacks import CallbackManager
        from langchain.callbacks import AsyncIteratorCallbackHandler
        
        # Convert Bedrock message format to OpenAI format
        formatted_messages = self._convert_message_format(messages, system_prompt)
        
        if stream:
            callback = AsyncIteratorCallbackHandler()
            
            chat_client = AzureChatOpenAI(
                azure_endpoint=self.azure_endpoint,
                deployment_name=self.deployment_name,
                model=self.model,
                callback_manager=CallbackManager([callback]),
                max_tokens=self.max_tokens,
                api_version=self.api_version,
                temperature=self.temperature,
                streaming=True,
                verbose=True,
            )
            
            async def response_generator():
                # Create a done event
                done_event = asyncio.Event()
                finish_reason = None
                
                async def wrap_done(awaitable_future, event):
                    try:
                        await awaitable_future
                    except Exception as e:
                        self.logger.error(f"Error in OpenAI request: {e}")
                    finally:
                        event.set()
                
                # Execute the chat request
                task = asyncio.create_task(
                    wrap_done(chat_client.ainvoke(formatted_messages), done_event)
                )
                
                # Yield tokens as they arrive
                async for chunk in callback.aiter():
                    # Check if the chunk contains finish reason
                    if hasattr(chunk, 'finish_reason') and chunk.finish_reason:
                        finish_reason = chunk.finish_reason
                        self.logger.info(f"Completion reason: {finish_reason}")
                    
                    yield chunk
                
                # Wait for completion
                await task
                
                # Log completion reason if available
                if finish_reason:
                    self.logger.info(f"Final completion reason: {finish_reason}")
            
            return response_generator()
        else:
            chat_client = AzureChatOpenAI(
                azure_endpoint=self.azure_endpoint,
                deployment_name=self.deployment_name,
                model=self.model,
                max_tokens=self.max_tokens,
                api_version=self.api_version,
                temperature=self.temperature,
                streaming=False
            )
            response = await chat_client.ainvoke(formatted_messages)
            
            # Convert response to Bedrock-compatible format
            return {
                "output": {
                    "message": {
                        "content": [{"text": response.content}]
                    }
                }
            }
    
    def _convert_message_format(self, messages, system_prompt=None):
        """Convert messages from Bedrock to OpenAI format."""
        result = []
        
        # Add system message if provided
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        
        # Add user and assistant messages
        for msg in messages:
            content = msg["content"]
            # Handle different content formats
            if isinstance(content, list):
                # Format multimodal content (text + images)
                text_content = ""
                for item in content:
                    if "text" in item:
                        text_content += item["text"]
                result.append({"role": msg["role"], "content": text_content})
            else:
                # Simple text content
                result.append({"role": msg["role"], "content": content})
        
        return result
    
    def count_tokens(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None
    ) -> Dict[str, int]:
        """Approximate token counting for Azure OpenAI."""
        import re
        try:
            # Format messages
            formatted_text = system_prompt or ""
            
            for msg in messages:
                content = msg["content"]
                if isinstance(content, list):
                    for item in content:
                        if "text" in item:
                            formatted_text += item["text"]
                else:
                    formatted_text += content
            
            # Count words and punctuation
            words = len(re.findall(r'\w+', formatted_text))
            punctuation = len(re.findall(r'[^\w\s]', formatted_text))
            total_count = words + punctuation
            
            return {
            "input_tokens": total_count,
            "output_tokens": 0,
            "total_tokens": total_count
            }
        except Exception as e:
            self.logger.warning(f"Failed to count tokens: {e}")
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
