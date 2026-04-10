"""
Ollama Interface - للتعامل مع Ollama Local LLMs
"""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaInterface:
    """
    Interface للتعامل مع Ollama
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.agent_models = {
            "planner": "qwen2.5:7b",
            "architect": "gemma4:latest",
            "backend": "qwen2.5-coder:7b",
            "frontend": "qwen2.5-coder:7b",
            "ai": "qwen2.5-coder:7b",
            "testing": "llama3.2:3b",
            "debugger": "llama3.1:8b",
            "refactor": "qwen2.5-coder:7b",
            "devops": "llama3.2:3b"
        }
    
    def generate(
        self,
        prompt: str,
        agent_type: str = "planner",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """
        توليد نص من Ollama
        """
        model = self.agent_models.get(agent_type, "qwen2.5:7b")
        
        logger.info(f"Using {model} for {agent_type}")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "format": "json" if json_mode else None,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=300
            )
            
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
    
    def list_models(self) -> list:
        """
        قائمة النماذج المتاحة
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [{"name": m["name"], "size": m["size"]} for m in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

# Singleton
ollama = OllamaInterface()
