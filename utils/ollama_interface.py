"""
Ollama Interface — للتعامل مع Ollama Local LLMs

Enhanced with:
- Async support (httpx.AsyncClient) with sync backward-compatible wrapper
- Streaming responses
- Response caching
- Retry with exponential backoff (tenacity)
- Connection pooling
"""

import asyncio
import json
import logging
import time
from typing import Optional, AsyncIterator, Callable

import httpx
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from utils.cache import ResponseCache

logger = logging.getLogger(__name__)


class OllamaInterface:
    """
    Interface للتعامل مع Ollama — reads model assignments from core/config settings.

    Provides both sync (`generate`) and async (`agenerate`) methods.
    Includes response caching, retry logic, and streaming support.
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._cache = ResponseCache(max_size=100, ttl_seconds=3600)

        # Import settings here to avoid circular imports at module level
        try:
            from core.config import settings

            self.agent_models = {
                "planner": settings.planner_model,
                "architect": settings.architect_model,
                "backend": settings.backend_model,
                "frontend": settings.frontend_model,
                "ai": settings.ai_model,
                "testing": settings.testing_model,
                "debugger": settings.debugger_model,
                "refactor": settings.refactor_model,
                "devops": settings.devops_model,
                # DockerAgent maps to "docker" via BaseAgent name stripping
                "docker": settings.devops_model,
                # ReviewerAgent
                "reviewer": settings.reviewer_model,
            }
            self.embeddings_model = settings.embeddings_model
            logger.info("OllamaInterface: loaded model config from settings")
        except Exception as e:
            logger.warning(f"Could not load settings, using defaults: {e}")
            self.agent_models = {
                "planner": "qwen3.5:latest",
                "architect": "gemma4:latest",
                "backend": "qwen2.5-coder:7b",
                "frontend": "qwen2.5-coder:7b",
                "ai": "qwen2.5-coder:7b",
                "testing": "qwen2.5-coder:7b",
                "debugger": "llama3.1:8b",
                "refactor": "qwen2.5-coder:7b",
                "devops": "llama3.2:3b",
                "docker": "llama3.2:3b",
                "reviewer": "qwen2.5-coder:7b",
            }
            self.embeddings_model = "bge-m3:latest"

    # ── Async Generate (primary) ────────────────────────────────

    async def agenerate(
        self,
        prompt: str,
        agent_type: str = "planner",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False,
        use_cache: bool = True,
    ) -> str:
        """
        Async LLM generation with caching and retry.
        """
        model = self.agent_models.get(
            agent_type, self.agent_models.get("planner", "qwen3.5:latest")
        )
        logger.info(f"Using model '{model}' for agent_type='{agent_type}'")

        # ── Check cache ────────────────────────────────────────
        if use_cache:
            cache_key = ResponseCache.make_key(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt or "",
                temperature=temperature,
                json_mode=json_mode,
            )
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache HIT for {agent_type} (key={cache_key[:12]}…)")
                return cached
        else:
            cache_key = None

        # ── Build payload ──────────────────────────────────────
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"

        # ── Call with retry ────────────────────────────────────
        response_text = await self._call_with_retry(model, payload)

        # ── Store in cache ─────────────────────────────────────
        if use_cache and cache_key:
            self._cache.set(cache_key, response_text)
            logger.debug(f"Cached response for {agent_type}")

        return response_text

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=3, max=30),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException, ConnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _call_with_retry(self, model: str, payload: dict) -> str:
        """POST to Ollama /api/chat with automatic retry on transient failures."""
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]

    # ── Async Streaming ─────────────────────────────────────────

    async def agenerate_stream(
        self,
        prompt: str,
        agent_type: str = "planner",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Streaming generation — yields tokens as they arrive.

        Returns the full concatenated response. Optionally calls `on_token`
        for each chunk so the caller can display incremental progress.
        """
        model = self.agent_models.get(
            agent_type, self.agent_models.get("planner", "qwen3.5:latest")
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"

        full_response = []

        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            full_response.append(token)
                            if on_token:
                                on_token(token)
                    except json.JSONDecodeError:
                        continue

        return "".join(full_response)

    # ── Sync Generate (backward compatible) ─────────────────────

    def generate(
        self,
        prompt: str,
        agent_type: str = "planner",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False,
    ) -> str:
        """
        Synchronous LLM generation — backward compatible with existing code.

        Uses the async method internally. If already in an async context,
        falls back to a direct requests.post call.
        """
        # Try to get or create an event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're inside an async context (e.g., FastAPI with asyncio.to_thread)
            # Fall back to synchronous requests call
            return self._sync_generate(
                prompt=prompt,
                agent_type=agent_type,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )
        else:
            # No running loop — safe to use asyncio.run
            return asyncio.run(
                self.agenerate(
                    prompt=prompt,
                    agent_type=agent_type,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )
            )

    def _sync_generate(
        self,
        prompt: str,
        agent_type: str = "planner",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False,
    ) -> str:
        """
        Pure synchronous fallback (original requests-based implementation).
        Used when we're already inside an async event loop.
        """
        model = self.agent_models.get(
            agent_type, self.agent_models.get("planner", "qwen3.5:latest")
        )
        logger.info(f"[sync] Using model '{model}' for agent_type='{agent_type}'")

        # ── Check cache ──────────────────────────────────────
        cache_key = ResponseCache.make_key(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt or "",
            temperature=temperature,
            json_mode=json_mode,
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache HIT for {agent_type} (sync)")
            return cached

        # ── Build payload ────────────────────────────────────
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=600,
            )
            response.raise_for_status()
            result = response.json()
            response_text = result["message"]["content"]

            # Cache
            self._cache.set(cache_key, response_text)
            return response_text

        except requests.exceptions.Timeout:
            logger.error(f"Ollama timeout after 600s for model '{model}'")
            raise
        except Exception as e:
            logger.error(f"Ollama error for model '{model}': {e}")
            raise

    # ── Utility methods ─────────────────────────────────────────

    def list_models(self) -> list:
        """قائمة النماذج المتاحة"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=30)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [{"name": m["name"], "size": m.get("size", 0)} for m in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def is_available(self) -> bool:
        """Check if Ollama server is reachable"""
        try:
            requests.get(f"{self.base_url}/api/tags", timeout=15)
            return True
        except Exception:
            return False

    @property
    def cache_stats(self) -> dict:
        """Return cache hit/miss statistics."""
        return self._cache.stats

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Response cache cleared")


# Singleton
ollama = OllamaInterface()
