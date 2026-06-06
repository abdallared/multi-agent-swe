"""
Architect Agent - تصميم البنية المعمارية للمشروع
"""

from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class ArchitectAgent(BaseAgent):
    """
    Agent مسؤول عن تصميم البنية التقنية للمشروع
    """
    
    def get_system_prompt(self) -> str:
        return """You are a principal software architect with 20+ years designing production systems at scale.

Your role is to design complete, runnable system architectures that backend and frontend developers can implement directly.

ARCHITECTURE STANDARDS:
1. ALWAYS use FastAPI + SQLAlchemy + SQLite (for simplicity) unless explicitly asked otherwise
2. ALWAYS use React + TypeScript + Tailwind CSS for the frontend
3. Design a COMPLETE database schema — every entity mentioned in the plan gets a table
4. Every table MUST have: id (INTEGER PRIMARY KEY), created_at (DATETIME), and appropriate columns
5. Define relationships (foreign keys) between tables explicitly. Ensure all database columns use standard snake_case (e.g., user_id, workspace_id) and specify relational integrity constraints.
6. Design ALL necessary API endpoints — include auth endpoints + full CRUD for each resource
7. Group modules logically: auth, each resource type, shared utilities

TECH STACK (default unless features require otherwise):
- Backend: FastAPI, Python 3.11, SQLAlchemy 2.0, JWT auth, bcrypt passwords, Pydantic v2
- Frontend: React 18, TypeScript, Tailwind CSS, React Router v6, Axios
- Database: SQLite (dev), PostgreSQL (prod)
- Deployment: Docker + docker-compose

OUTPUT — valid JSON only:
{
    "tech_stack": {
        "backend": {
            "framework": "FastAPI",
            "language": "Python 3.11",
            "orm": "SQLAlchemy 2.0",
            "authentication": "JWT + bcrypt"
        },
        "frontend": {
            "framework": "React 18",
            "language": "TypeScript",
            "state_management": "React Hooks + Context",
            "styling": "Tailwind CSS"
        },
        "database": {
            "primary": "SQLite",
            "cache": null,
            "search": null
        }
    },
    "database_schema": {
        "tables": [
            {
                "name": "table_name",
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": false, "primary_key": true, "unique": true, "default": null},
                    {"name": "created_at", "type": "DATETIME", "nullable": false, "primary_key": false, "unique": false, "default": "CURRENT_TIMESTAMP"}
                ],
                "indexes": ["column_name"],
                "relationships": [
                    {"type": "many_to_one", "table": "users", "foreign_key": "user_id"}
                ]
            }
        ]
    },
    "api_design": {
        "type": "REST",
        "base_url": "/api",
        "endpoints": [
            {
                "path": "/auth/register",
                "method": "POST",
                "description": "Register new user account",
                "authentication_required": false
            },
            {
                "path": "/auth/login",
                "method": "POST",
                "description": "Authenticate and receive JWT token",
                "authentication_required": false
            }
        ]
    },
    "modules": [
        {
            "name": "Authentication",
            "type": "backend",
            "description": "User registration, login, JWT token management",
            "dependencies": ["users table", "jose", "passlib"]
        }
    ],
    "deployment_strategy": {
        "containerization": "Docker",
        "orchestration": "Docker Compose",
        "ci_cd": "GitHub Actions"
    }
}

Include ALL tables and ALL CRUD endpoints for every resource in the project plan.
Output ONLY valid JSON, no additional text."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ تصميم البنية المعمارية
        """
        plan = context.get('project_plan')
        
        if not plan:
            raise ValueError("project_plan is required in context")
        
        self.logger.info(f"Designing architecture for: {plan.get('project_name')}")
        
        # تحليل التعقيد
        complexity = self._analyze_complexity(plan)
        self.logger.info(f"Project complexity: {complexity}")
        
        # بناء الـ prompt
        architecture_prompt = self._build_architecture_prompt(plan, complexity)
        
        # استدعاء LLM
        response = self.call_llm(
            prompt=architecture_prompt,
            json_mode=True,
            temperature=0.1,  # low for deterministic JSON output
            max_tokens=4000  # enough for complete schema + endpoints
        )
        
        # Parse JSON
        try:
            # تنظيف الـ response
            response = response.strip()
            # إزالة أي نص قبل أو بعد JSON
            if response.startswith('```json'):
                response = response.split('```json')[1].split('```')[0].strip()
            elif response.startswith('```'):
                response = response.split('```')[1].split('```')[0].strip()
            
            architecture = json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse architecture JSON: {e}")
            self.logger.error(f"Response was: {response[:1000]}")
            
            # محاولة إصلاح JSON
            try:
                # إزالة trailing commas
                import re
                response = re.sub(r',\s*}', '}', response)
                response = re.sub(r',\s*]', ']', response)
                architecture = json.loads(response)
                self.logger.info("JSON fixed successfully")
            except:
                raise ValueError(f"Could not parse architecture JSON: {e}")
        
        # Validation
        self._validate_architecture(architecture)
        
        # إضافة metadata
        architecture['metadata'] = {
            'complexity': complexity,
            'estimated_setup_time': self._estimate_setup_time(architecture),
            'recommended_team_size': self._recommend_team_size(complexity)
        }
        
        self.logger.info(f"Architecture design completed for: {plan.get('project_name')}")
        
        return {
            'architecture': architecture,
            'status': 'architecture_completed'
        }
    
    def _analyze_complexity(self, plan: Dict) -> str:
        """
        تحليل تعقيد المشروع
        """
        features = plan.get('features', [])
        
        # عدد الميزات
        feature_count = len(features)
        
        # عدد الميزات المعقدة
        complex_features = sum(
            1 for f in features 
            if f.get('complexity') == 'complex'
        )
        
        # وجود AI/ML
        has_ai = any(
            'ai' in f.get('name', '').lower() or 
            'ml' in f.get('name', '').lower() or
            'recommendation' in f.get('name', '').lower()
            for f in features
        )
        
        # وجود real-time features
        has_realtime = any(
            'realtime' in f.get('name', '').lower() or
            'live' in f.get('name', '').lower() or
            'chat' in f.get('name', '').lower()
            for f in features
        )
        
        # حساب النتيجة
        score = 0
        score += min(feature_count / 5, 3)  # max 3 points
        score += complex_features * 2  # 2 points per complex feature
        score += 3 if has_ai else 0
        score += 2 if has_realtime else 0
        
        if score <= 5:
            return 'simple'
        elif score <= 10:
            return 'medium'
        else:
            return 'complex'
    
    def _build_architecture_prompt(self, plan: Dict, complexity: str) -> str:
        """
        بناء prompt لتصميم البنية
        """
        features_summary = "\n".join([
            f"- {f['name']}: {f.get('description', '')} (Priority: {f.get('priority', 'medium')}, Complexity: {f.get('complexity', 'medium')})"
            for f in plan.get('features', [])
        ])
        
        nfr_raw = plan.get('non_functional_requirements', {})
        if isinstance(nfr_raw, list) and len(nfr_raw) > 0:
            nfr = nfr_raw[0] if isinstance(nfr_raw[0], dict) else {}
        elif isinstance(nfr_raw, dict):
            nfr = nfr_raw
        else:
            nfr = {}
        
        return f"""Design a complete system architecture for this project:

Project: {plan.get('project_name')}
Description: {plan.get('description')}
Complexity Level: {complexity}

Features:
{features_summary}

Non-Functional Requirements:
- Performance: {nfr.get('performance', 'Standard')}
- Security: {nfr.get('security', 'Standard')}
- Scalability: {nfr.get('scalability', 'Standard')}
- Availability: {nfr.get('availability', '99.9%')}

User Stories Count: {len(plan.get('user_stories', []))}

Design the COMPLETE architecture following the JSON structure in your system prompt.

Requirements:
1. Use FastAPI + SQLAlchemy + SQLite + React + TypeScript + Tailwind (default stack)
2. Create a table for EVERY entity mentioned in the features: {list(set(e for f in plan.get('features', []) for e in f.get('entities', [])))}
3. EVERY table needs: id, created_at, and all business columns
4. Include ALL CRUD endpoints for each resource (GET list, GET one, POST, PUT, DELETE)
5. Always include: POST /auth/register and POST /auth/login endpoints
6. Mark endpoints that need authentication: authentication_required = true
7. Create a module for each major feature area

Output ONLY valid JSON, no additional text."""
    
    def _validate_architecture(self, architecture: Dict):
        """
        التحقق من صحة البنية المعمارية
        """
        required_keys = [
            'tech_stack',
            'database_schema',
            'api_design',
            'modules',
            'deployment_strategy'
        ]
        
        for key in required_keys:
            if key not in architecture:
                raise ValueError(f"Missing required key in architecture: {key}")
        
        # التحقق من tech_stack
        tech_stack = architecture['tech_stack']
        if 'backend' not in tech_stack or 'frontend' not in tech_stack:
            raise ValueError("tech_stack must include backend and frontend")
        
        # التحقق من database_schema
        db_schema = architecture['database_schema']
        if 'tables' not in db_schema or not db_schema['tables']:
            raise ValueError("database_schema must include at least one table")
        
        # التحقق من modules
        modules = architecture['modules']
        if not modules:
            raise ValueError("architecture must include at least one module")
        
        self.logger.info("Architecture validation passed")
    
    def _estimate_setup_time(self, architecture: Dict) -> str:
        """
        تقدير وقت الإعداد
        """
        module_count = len(architecture.get('modules', []))
        table_count = len(architecture.get('database_schema', {}).get('tables', []))
        
        # حساب بسيط
        hours = (module_count * 8) + (table_count * 2)
        
        if hours < 40:
            return "1 week"
        elif hours < 80:
            return "2 weeks"
        elif hours < 160:
            return "1 month"
        else:
            return "2+ months"
    
    def _recommend_team_size(self, complexity: str) -> int:
        """
        توصية بحجم الفريق
        """
        team_sizes = {
            'simple': 1,
            'medium': 2,
            'complex': 3
        }
        return team_sizes.get(complexity, 2)
