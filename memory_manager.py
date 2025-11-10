"""
Memory Management Module
Manages conversation history and context
Compatible with new LangChain version
"""

from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
import json
import os
from datetime import datetime


class MemoryManager:
    """Manages agent's conversation memory"""
    
    def __init__(self, 
                 max_length: int = 10, 
                 memory_type: str = "buffer",
                 llm: Any = None,
                 save_to_file: bool = True):
        """
        Initialize memory manager
        
        Args:
            max_length: Maximum conversation rounds to save
            memory_type: Memory type ("buffer" or "summary")
            llm: LLM instance (kept for compatibility)
            save_to_file: Whether to save memory to file
        """
        self.max_length = max_length
        self.memory_type = memory_type
        self.save_to_file = save_to_file
        self.memory_file = "chat_history.json"
        
        # Use simple list to store messages
        self.messages: List[BaseMessage] = []
        
        # Load historical memory
        if save_to_file:
            self._load_memory()
    
    def add_user_message(self, message: str):
        """Add user message"""
        self.messages.append(HumanMessage(content=message))
        if self.save_to_file:
            self._save_memory()
    
    def add_ai_message(self, message: str):
        """Add AI message"""
        self.messages.append(AIMessage(content=message))
        if self.save_to_file:
            self._save_memory()
    
    def get_memory(self) -> List[BaseMessage]:
        """Get memory content"""
        # Limit memory length
        if len(self.messages) > self.max_length * 2:
            return self.messages[-(self.max_length * 2):]
        return self.messages
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables (for agent)"""
        return {"chat_history": self.get_memory()}
    
    def clear_memory(self):
        """Clear memory"""
        self.messages = []
        if self.save_to_file and os.path.exists(self.memory_file):
            os.remove(self.memory_file)
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            messages = []
            for msg in self.messages:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    messages.append({"role": "system", "content": msg.content})
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "messages": messages
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")
    
    def _load_memory(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for msg in data.get("messages", []):
                    if msg["role"] == "user":
                        self.messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        self.messages.append(AIMessage(content=msg["content"]))
                
                print(f"Successfully loaded {len(data.get('messages', []))} historical messages")
        except Exception as e:
            print(f"Failed to load memory: {e}")
    
    def get_context_string(self) -> str:
        """Get formatted context string"""
        messages = self.get_memory()
        if not messages:
            return "No conversation history"
        
        context = []
        for msg in messages[-6:]:  # Last 3 rounds of conversation
            if isinstance(msg, HumanMessage):
                context.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                context.append(f"Assistant: {msg.content}")
        
        return "\n".join(context)
