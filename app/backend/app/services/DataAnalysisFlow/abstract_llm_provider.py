from abc import ABC, abstractmethod
from typing import Dict, List, AsyncGenerator, Optional, Union, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Union[Dict, AsyncGenerator[str, None]]:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def count_tokens(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None
    ) -> Dict[str, int]:
        """Count tokens for a given input."""
        pass