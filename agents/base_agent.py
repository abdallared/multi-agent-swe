"""
Base Agent - الفئة الأساسية لجميع Agents

Enhanced with:
- TokenManager integration for dynamic token budgets
- Project complexity awareness
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import logging
import time

from utils.token_manager import token_manager

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
        self.complexity = "medium"  # Can be updated by Pipeline from Architect's result

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
        temperature: float = None,
        max_tokens: int = None,
        json_mode: bool = False
    ) -> str:
        """
        استدعاء LLM — emits verbose events for system prompt, user prompt, and response.

        If temperature or max_tokens are not specified, they are automatically
        determined by the TokenManager based on agent type and project complexity.
        """
        resolved_system = system_prompt or self.get_system_prompt()
        agent_type = self.name.lower().replace("agent", "")

        # ── Enrich with memory-based few-shot examples ───────
        memory_context = self._build_memory_context(prompt, agent_type)
        if memory_context:
            resolved_system = resolved_system + "\n\n" + memory_context

        # ── Dynamic token/temperature from TokenManager ──────
        if temperature is None:
            temperature = token_manager.get_temperature(agent_type)
        if max_tokens is None:
            max_tokens = token_manager.get_budget(agent_type, self.complexity)

        try:
            self.logger.info(f"Calling LLM for {self.name} (tokens={max_tokens}, temp={temperature})")

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
                f"Calling model '{model}' (budget: {max_tokens} tokens)... Ollama is computing the response."
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

            self.logger.info(f"LLM response received in {elapsed}s ({len(response)} chars)")
            return response

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            self._emit_verbose("error", str(e))
            raise

    def _build_memory_context(self, prompt: str, agent_type: str) -> Optional[str]:
        """
        Query project memory for few-shot examples from similar past projects.

        Returns a formatted string to append to the system prompt, or None.
        Never raises — silently returns None on any error.
        """
        if not self.memory:
            return None

        try:
            examples = self.memory.get_few_shot_examples(
                user_prompt=prompt,
                agent_type=agent_type,
                top_k=2,
            )
            if examples:
                self.logger.info(f"Memory: injecting few-shot examples for {agent_type}")
                self._emit_verbose(
                    "info",
                    f"📚 Memory: found similar past projects — injecting few-shot examples",
                )
            return examples
        except Exception as e:
            self.logger.warning(f"Memory lookup failed (non-fatal): {e}")
            return None

    def validate_output(self, output: Dict[str, Any]) -> bool:
        required_keys = ['status']
        return all(key in output for key in required_keys)
