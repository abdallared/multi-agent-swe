"""
Base Agent - الفئة الأساسية لجميع Agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class لجميع Agents
    """
    
    def __init__(self, llm_interface, memory_system=None):
        self.llm = llm_interface
        self.memory = memory_system
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ مهمة Agent
        يجب تنفيذها في كل Agent
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        System prompt للـ Agent
        """
        pass
    
    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """
        استدعاء LLM
        """
        try:
            self.logger.info(f"Calling LLM for {self.name}")
            
            # تحديد agent_type من اسم الـ class
            agent_type = self.name.lower().replace("agent", "")
            
            response = self.llm.generate(
                prompt=prompt,
                agent_type=agent_type,
                system_prompt=system_prompt or self.get_system_prompt(),
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode
            )
            
            self.logger.info(f"LLM response received")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        التحقق من صحة المخرجات
        """
        required_keys = ['status']
        return all(key in output for key in required_keys)
