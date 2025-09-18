"""
Utility functions for interacting with Amazon Bedrock API.
"""
import json
import ast
from typing import Dict, List, Any, Optional, Tuple
import logging
from ..abstract_llm_provider import  LLMProvider
from typing import AsyncGenerator, Union


logger = logging.getLogger(__name__)

async def handle_llm_conversation(
    llm_provider: LLMProvider,
    messages: List[Dict],
    system_prompts: str = None,
    stream: bool = False,
    track_tokens: bool = True
) -> Union[Dict, AsyncGenerator[str, None]]:
    """Provider-agnostic handler for LLM conversations."""
    # Track input tokens if requested
    token_counts = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    
    if track_tokens:
        try:
            token_counts = llm_provider.count_tokens(messages, system_prompts)
        except Exception as e:
            logger.warning(f"Failed to count tokens: {e}")
    
    if stream:
        async def response_generator():
            full_response = ""
            async for token in await llm_provider.generate_response(
                messages=messages,
                system_prompt=system_prompts,
                stream=True
            ):
                full_response += token
                yield token
            
            # Estimate output token count (approximate)
            if track_tokens:
                output_tokens = len(full_response.split())  # Simple word approximation
                token_counts["output_tokens"] = output_tokens
                token_counts["total_tokens"] = token_counts["input_tokens"] + output_tokens
        
        return response_generator()
    else:
        # Make the API call
        response = await llm_provider.generate_response(
            messages=messages,
            system_prompt=system_prompts,
            stream=False
        )
        
        # Extract token usage from the response if available
        if track_tokens and "usage" in response:
            input_token_count = response.get("usage", {}).get("inputTokens", 0)
            output_token_count = response.get("usage", {}).get("outputTokens", 0)
            total_token_count = response.get("usage", {}).get("totalTokens", 0)
            token_counts["output_tokens"] = int(output_token_count) if output_token_count else token_counts["output_tokens"]
            token_counts["input_tokens"] = int(input_token_count) if input_token_count else token_counts["input_tokens"]
            token_counts["total_tokens"] = int(total_token_count) if total_token_count else token_counts["total_tokens"]
        
        # Add token counts to the response
        response["token_counts"] = token_counts
        
        return response