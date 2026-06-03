"""
Planner Agent - تحويل الفكرة إلى خطة منظمة
"""

from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Agent مسؤول عن تحويل user prompt إلى خطة مشروع منظمة
    """
    
    def get_system_prompt(self) -> str:
        return """You are a world-class software project planner with 20+ years of experience delivering enterprise applications.

Your role is to transform user ideas into precise, developer-ready project specifications that leave no ambiguity.

PLANNING STANDARDS:
1. Always decompose the project into CONCRETE, BUILDABLE features — not vague goals
2. Identify every data entity the system will need (users, posts, orders, etc.)
3. For each feature, think about: What database tables does it need? What API endpoints?
4. Write user stories with clear, testable acceptance criteria
5. Prioritize features: P1=must-have for MVP, P2=important, P3=nice-to-have
6. Security is ALWAYS a concern — include auth requirements explicitly
7. Think about the UI: what pages/screens will users interact with?

OUTPUT — valid JSON only, with this exact structure:
{
    "project_name": "CamelCase or Title Case name",
    "description": "2-3 sentence technical description of what gets built",
    "vision": "The long-term goal and value proposition",
    "target_users": ["list of user types, e.g., 'Registered User', 'Admin', 'Guest'"],
    "features": [
        {
            "name": "Short feature name",
            "description": "What this feature does and why it matters",
            "priority": "high|medium|low",
            "complexity": "simple|medium|complex",
            "estimated_hours": 8,
            "entities": ["user", "post"],
            "pages": ["Dashboard", "Create Post"]
        }
    ],
    "user_stories": [
        {
            "as_a": "user type",
            "i_want": "specific action",
            "so_that": "business value",
            "acceptance_criteria": [
                "Given X, when Y, then Z (be specific and testable)"
            ]
        }
    ],
    "non_functional_requirements": {
        "performance": "e.g., API responses under 200ms for list endpoints",
        "security": "e.g., JWT auth, bcrypt passwords, input validation, rate limiting",
        "scalability": "e.g., stateless backend supports horizontal scaling",
        "availability": "e.g., 99.9% uptime, graceful error handling"
    },
    "constraints": ["e.g., Must use SQLite for MVP, PostgreSQL for production"],
    "assumptions": ["e.g., Users have modern web browsers", "Single-region deployment"]
}

Generate at least 5 features and 5 user stories. Be specific and actionable.
Output ONLY valid JSON, no additional text."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ التخطيط
        """
        user_prompt = context.get('user_prompt', '')
        
        if not user_prompt:
            raise ValueError("user_prompt is required")
        
        self.logger.info(f"Planning project for: {user_prompt}")
        
        # بناء الـ prompt
        planning_prompt = self._build_planning_prompt(user_prompt)
        
        # استدعاء LLM
        response = self.call_llm(
            prompt=planning_prompt,
            json_mode=True,
            temperature=0.7
        )
        
        # Parse JSON
        try:
            plan = json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            self.logger.error(f"Response was: {response[:500]}")
            raise
        
        # Validation
        self._validate_plan(plan)
        
        self.logger.info(f"Planning completed for: {plan.get('project_name', 'Unknown')}")
        
        return {
            'project_plan': plan,
            'status': 'planning_completed'
        }
    
    def _build_planning_prompt(self, user_prompt: str) -> str:
        """
        بناء prompt للتخطيط
        """
        return f"""User Request: {user_prompt}

Create a comprehensive project plan following the JSON structure specified in your system prompt.

Consider:
1. Break down the project into clear, manageable features
2. Identify all types of users who will interact with the system
3. Write detailed user stories with acceptance criteria
4. Specify non-functional requirements (performance, security, etc.)
5. List any constraints or assumptions
6. Estimate complexity and time for each feature

Be specific and actionable. The plan will be used to generate actual code.

Output ONLY valid JSON, no additional text."""
    
    def _validate_plan(self, plan: Dict):
        """
        التحقق من صحة الخطة
        """
        required_keys = [
            'project_name',
            'description',
            'features',
            'user_stories'
        ]
        
        for key in required_keys:
            if key not in plan:
                raise ValueError(f"Missing required key in plan: {key}")
        
        if not plan['features']:
            raise ValueError("Plan must have at least one feature")
        
        if not plan['user_stories']:
            raise ValueError("Plan must have at least one user story")
        
        self.logger.info("Plan validation passed")
