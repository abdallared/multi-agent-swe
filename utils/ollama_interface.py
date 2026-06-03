"""
Ollama Interface - للتعامل مع Ollama Local LLMs
"""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaInterface:
    """
    Interface للتعامل مع Ollama — reads model assignments from core/config settings
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        # Import settings here to avoid circular imports at module level
        try:
            from core.config import settings
            self.agent_models = {
                "planner":   settings.planner_model,
                "architect": settings.architect_model,
                "backend":   settings.backend_model,
                "frontend":  settings.frontend_model,
                "ai":        settings.ai_model,
                "testing":   settings.testing_model,
                "debugger":  settings.debugger_model,
                "refactor":  settings.refactor_model,
                "devops":    settings.devops_model,
                # DockerAgent maps to "docker" via BaseAgent name stripping
                # Point it at devops_model (llama3.2:3b)
                "docker":    settings.devops_model,
            }
            self.embeddings_model = settings.embeddings_model
            logger.info("OllamaInterface: loaded model config from settings")
        except Exception as e:
            logger.warning(f"Could not load settings, using defaults: {e}")
            self.agent_models = {
                "planner":   "qwen3.5:latest",
                "architect": "gemma4:latest",
                "backend":   "qwen2.5-coder:7b",
                "frontend":  "qwen2.5-coder:7b",
                "ai":        "qwen2.5-coder:7b",
                "testing":   "qwen2.5-coder:7b",
                "debugger":  "llama3.1:8b",
                "refactor":  "qwen2.5-coder:7b",
                "devops":    "llama3.2:3b",
                "docker":    "llama3.2:3b",
            }
            self.embeddings_model = "bge-m3:latest"
    
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
        model = self.agent_models.get(agent_type, self.agent_models.get("planner", "qwen3.5:latest"))
        
        logger.info(f"Using model '{model}' for agent_type='{agent_type}'")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Ollama format param: must be "json" or omitted — cannot be None
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if json_mode:
            payload["format"] = "json"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=600  # increased to 10 min for large models
            )
            
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.Timeout:
            logger.error(f"Ollama timeout after 600s for model '{model}'")
            raise
        except Exception as e:
            logger.error(f"Ollama error for model '{model}': {e}")
            raise
    
    def list_models(self) -> list:
        """
        قائمة النماذج المتاحة
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [{"name": m["name"], "size": m.get("size", 0)} for m in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if Ollama server is reachable"""
        try:
            requests.get(f"{self.base_url}/api/tags", timeout=5)
            return True
        except Exception:
            return False

# Singleton
ollama = OllamaInterface()
