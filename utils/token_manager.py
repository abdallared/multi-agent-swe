"""
Token Manager — Dynamic token budget allocation per agent type.

Instead of using a fixed max_tokens=4000 for all agents, this module
calculates optimal budgets based on agent type and project complexity.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Dynamically calculates optimal token budget and temperature per agent.

    Usage:
        tm = TokenManager()
        budget = tm.get_budget("backend", complexity="complex")   # → 12000
        temp = tm.get_temperature("architect")                    # → 0.1
    """

    # Base token budgets per agent type (for "simple" projects)
    BASE_BUDGETS = {
        "planner": 2000,
        "architect": 4000,
        "backend": 6000,
        "frontend": 8000,
        "testing": 3000,
        "docker": 2000,
        "reviewer": 3000,
        "debugger": 4000,
        "refactor": 6000,
        "devops": 2000,
    }

    # Complexity multipliers
    MULTIPLIERS = {
        "simple": 1.0,
        "medium": 1.5,
        "complex": 2.0,
    }

    # Agent-specific default temperatures
    TEMPERATURES = {
        "planner": 0.7,      # Creative — needs variety in planning
        "architect": 0.1,    # Deterministic — consistent JSON schemas
        "backend": 0.1,      # Precise — correct code generation
        "frontend": 0.2,     # Slightly creative for UI/UX
        "testing": 0.1,      # Precise — correct test assertions
        "docker": 0.1,       # Deterministic — standard configs
        "reviewer": 0.1,     # Precise — consistent code review
        "debugger": 0.3,     # Some creativity for fixing bugs
        "refactor": 0.2,     # Balance between consistency and improvement
        "devops": 0.1,       # Deterministic — infrastructure code
    }

    # Hard limits to prevent excessive token usage
    MIN_TOKENS = 1000
    MAX_TOKENS = 16000

    def get_budget(
        self,
        agent_type: str,
        complexity: str = "medium",
        override: Optional[int] = None,
    ) -> int:
        """
        Calculate the optimal token budget for an agent.

        Args:
            agent_type: The type of agent (e.g., "backend", "planner")
            complexity: Project complexity from ArchitectAgent ("simple", "medium", "complex")
            override: If set, use this value directly (for explicit max_tokens in call_llm)

        Returns:
            Optimal max_tokens value
        """
        if override is not None:
            return max(self.MIN_TOKENS, min(override, self.MAX_TOKENS))

        base = self.BASE_BUDGETS.get(agent_type, 4000)
        multiplier = self.MULTIPLIERS.get(complexity, 1.0)
        budget = int(base * multiplier)

        # Clamp to hard limits
        budget = max(self.MIN_TOKENS, min(budget, self.MAX_TOKENS))

        logger.debug(f"Token budget for {agent_type} ({complexity}): {budget}")
        return budget

    def get_temperature(
        self,
        agent_type: str,
        override: Optional[float] = None,
    ) -> float:
        """
        Get the recommended temperature for an agent type.

        Args:
            agent_type: The type of agent
            override: If set, use this value directly

        Returns:
            Temperature value between 0.0 and 1.0
        """
        if override is not None:
            return max(0.0, min(override, 1.0))

        return self.TEMPERATURES.get(agent_type, 0.3)

    def get_config(self, agent_type: str, complexity: str = "medium") -> dict:
        """
        Get complete LLM config for an agent.

        Returns:
            {"max_tokens": int, "temperature": float}
        """
        return {
            "max_tokens": self.get_budget(agent_type, complexity),
            "temperature": self.get_temperature(agent_type),
        }


# Singleton
token_manager = TokenManager()
