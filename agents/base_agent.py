"""
Base Agent - الفئة الأساسية لجميع Agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import logging
import time

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class لجميع Agents — supports verbose callback for real-time streaming
    """

    # Class-level verbose callback — set by the WebSocket handler before each run
    _verbose_callback: Optional[Callable] = None

    @classmethod
    def set_verbose_callback(cls, callback: Optional[Callable]):
        """
        Set a callback that receives verbose log entries during LLM calls.
        callback(entry: dict) → None
        The WebSocket handler sets this before running agents, clears after.
        """
        cls._verbose_callback = callback

    def __init__(self, llm_interface, memory_system=None):
        self.llm = llm_interface
        self.memory = memory_system
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def _emit_verbose(self, kind: str, content: str, extra: dict = None):
        """Emit a verbose log entry via the callback if set."""
        callback = BaseAgent._verbose_callback
        if callback:
            agent_type = self.name.lower().replace("agent", "")
            model = self.llm.agent_models.get(agent_type, "unknown")
            entry = {
                "agent": self.name,
                "agent_type": agent_type,
                "model": model,
                "kind": kind,        # "system_prompt" | "prompt" | "response" | "parse" | "info" | "error"
                "content": content,
                "ts": time.time(),
            }
            if extra:
                entry.update(extra)
            try:
                callback(entry)
            except Exception as e:
                self.logger.warning(f"Error in verbose callback: {e}", exc_info=True)

    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """
        استدعاء LLM — emits verbose events for system prompt, user prompt, and response
        """
        resolved_system = system_prompt or self.get_system_prompt()
        agent_type = self.name.lower().replace("agent", "")

        try:
            self.logger.info(f"Calling LLM for {self.name}")

            # ── Verbose: system prompt ──────────────────────────
            self._emit_verbose(
                "system_prompt",
                resolved_system,
                {"char_count": len(resolved_system), "json_mode": json_mode, "temperature": temperature, "max_tokens": max_tokens}
            )

            # ── Verbose: user prompt ────────────────────────────
            self._emit_verbose(
                "prompt",
                prompt,
                {"char_count": len(prompt)}
            )

            # ── Verbose: pending info ───────────────────────────
            model = self.llm.agent_models.get(agent_type, "unknown")
            self._emit_verbose(
                "info",
                f"Calling model '{model}'... Ollama is computing the response (this can take 1-3 minutes on local hardware)."
            )

            t0 = time.time()
            response = self.llm.generate(
                prompt=prompt,
                agent_type=agent_type,
                system_prompt=resolved_system,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode
            )
            elapsed = round(time.time() - t0, 1)

            # ── Verbose: raw response ───────────────────────────
            self._emit_verbose(
                "response",
                response,
                {"char_count": len(response), "elapsed_s": elapsed}
            )

            self.logger.info(f"LLM response received in {elapsed}s")
            return response

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            self._emit_verbose("error", str(e))
            raise

    def validate_output(self, output: Dict[str, Any]) -> bool:
        required_keys = ['status']
        return all(key in output for key in required_keys)
