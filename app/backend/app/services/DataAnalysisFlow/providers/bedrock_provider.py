import json
import asyncio
import logging
from ..abstract_llm_provider import LLMProvider
from typing import List, Dict, Optional, Union, AsyncGenerator
class BedrockProvider(LLMProvider):
    """LLM provider for Amazon Bedrock."""
    
    def __init__(
        self, 
        bedrock_client, 
        model_id: str,
        temperature: float = 0.5,
        top_k: int = 200,
        logger: Optional[logging.Logger] = None
    ):
        self.bedrock_client = bedrock_client
        self.model_id = model_id
        self.temperature = temperature
        self.top_k = top_k
        self.logger = logger or logging.getLogger(__name__)
    
    async def generate_response(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Union[Dict, AsyncGenerator[str, None]]:
        if stream:
            async def response_generator():
                # Configure the request
                inference_config = {"temperature": self.temperature}
                additional_model_fields = {"top_k": self.top_k}
                
                try:
                    # Make the API call with streaming
                    response_stream = self.bedrock_client.converse_stream(
                        modelId=self.model_id,
                        messages=messages,
                        system=[{"text": system_prompt}] if system_prompt else None,
                        inferenceConfig=inference_config,
                        additionalModelRequestFields=additional_model_fields
                    )
                    
                    # Yield tokens as they arrive
                    for event in response_stream:
                        if "message" in event:
                            chunk = event["message"]["content"][0]["text"]
                            yield chunk
                
                except Exception as e:
                    self.logger.error(f"Error in Bedrock streaming: {e}")
                    yield f"Error: {str(e)}"
            
            return response_generator()
        else:
            # Set up inference parameters
            inference_config = {"temperature": self.temperature}
            additional_model_fields = {"top_k": self.top_k}
            
            # Make the API call
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                system=[{"text": system_prompt}] if system_prompt else None,
                inferenceConfig=inference_config,
                additionalModelRequestFields=additional_model_fields
            )
            
            return response
    
    def count_tokens(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None
    ) -> Dict[str, int]:
        try:
            # Format input for token counting
            formatted_input = {
                "messages": messages,
                "system": [{"text": system_prompt}] if system_prompt else None
            }

            # Call the token counting API
            token_response = self.bedrock_client.count_tokens(
                modelId=self.model_id,
                contentType="application/json",
                body=json.dumps(formatted_input)
            )
            
            return {
                "input_tokens": token_response.get("inputTokenCount", 0),
                "output_tokens": 0,
                "total_tokens": token_response.get("inputTokenCount", 0)
            }
        except Exception as e:
            self.logger.warning(f"Failed to count tokens: {e}")
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}