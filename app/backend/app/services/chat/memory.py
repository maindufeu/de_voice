from typing import Dict, List, Tuple, Optional
import time
from pydantic import BaseModel

class Message(BaseModel):
    """Message model for conversation history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = None
    
    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = time.time()
        super().__init__(**data)

class ConversationMemory:
    """Manages conversation history for each user session"""
    
    def __init__(self, max_messages: int = 10):
        """Initialize conversation memory manager
        
        Args:
            max_messages (int): Maximum number of messages to store per conversation
        """
        self.conversations: Dict[str, List[Message]] = {}
        self.max_messages = max_messages
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the conversation history
        
        Args:
            session_id (str): Unique identifier for the conversation
            role (str): "user" or "assistant"
            content (str): Message content
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            
        message = Message(role=role, content=content)
        self.conversations[session_id].append(message)
        
        # Trim if exceeding max messages
        if len(self.conversations[session_id]) > self.max_messages:
            self.conversations[session_id] = self.conversations[session_id][
                -self.max_messages:
            ]
    
    def get_conversation_history(self, session_id: str) -> List[Message]:
        """Get the conversation history for a session
        
        Args:
            session_id (str): Unique identifier for the conversation
            
        Returns:
            List of Message objects
        """
        return self.conversations.get(session_id, [])
    
    def format_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        """Format conversation history for LLM input
        
        Args:
            session_id (str): Unique identifier for the conversation
            
        Returns:
            List of dictionaries with role and content keys
        """
        messages = self.get_conversation_history(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def clear_conversation(self, session_id: str) -> None:
        """Clear the conversation history for a session
        
        Args:
            session_id (str): Unique identifier for the conversation
        """
        if session_id in self.conversations:
            del self.conversations[session_id]

# Create a singleton instance
memory_service = ConversationMemory()