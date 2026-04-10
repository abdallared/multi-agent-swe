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
        return """You are an expert software project planner.

Your role is to convert user ideas into structured, actionable project requirements.

You must output valid JSON with this exact structure:
{
    "project_name": "string",
    "description": "string",
    "vision": "string",
    "target_users": ["string"],
    "features": [
        {
            "name": "string",
            "description": "string",
            "priority": "high|medium|low",
            "complexity": "simple|medium|complex",
            "estimated_hours": number
        }
    ],
    "user_stories": [
        {
            "as_a": "string",
            "i_want": "string",
            "so_that": "string",
            "acceptance_criteria": ["string"]
        }
    ],
    "non_functional_requirements": {
        "performance": "string",
        "security": "string",
        "scalability": "string",
        "availability": "string"
    },
    "constraints": ["string"],
    "assumptions": ["string"]
}

Be thorough, specific, and realistic in your planning."""
    
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
