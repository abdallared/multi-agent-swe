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
        return """You are a senior software architect with 15+ years of experience.

Your role is to design scalable, maintainable, and secure system architectures.

You must output valid JSON with this exact structure:
{
    "tech_stack": {
        "backend": {
            "framework": "string (e.g., FastAPI, Django, Express)",
            "language": "string (e.g., Python 3.11, Node.js 18)",
            "orm": "string (e.g., SQLAlchemy, Prisma)",
            "authentication": "string (e.g., JWT, OAuth2)"
        },
        "frontend": {
            "framework": "string (e.g., React, Vue, Angular)",
            "language": "string (e.g., TypeScript, JavaScript)",
            "state_management": "string (e.g., Redux, Zustand)",
            "styling": "string (e.g., Tailwind CSS, Material-UI)"
        },
        "database": {
            "primary": "string (e.g., PostgreSQL, MongoDB)",
            "cache": "string (e.g., Redis, Memcached)",
            "search": "string (optional, e.g., Elasticsearch)"
        }
    },
    "database_schema": {
        "tables": [
            {
                "name": "string",
                "columns": [
                    {
                        "name": "string",
                        "type": "string (e.g., UUID, VARCHAR, INTEGER)",
                        "nullable": boolean,
                        "primary_key": boolean,
                        "unique": boolean,
                        "default": "string (optional)"
                    }
                ],
                "indexes": ["string"],
                "relationships": [
                    {
                        "type": "string (one_to_many, many_to_one, many_to_many)",
                        "table": "string",
                        "foreign_key": "string"
                    }
                ]
            }
        ]
    },
    "api_design": {
        "type": "REST",
        "base_url": "/api/v1",
        "endpoints": [
            {
                "path": "string",
                "method": "GET|POST|PUT|DELETE|PATCH",
                "description": "string",
                "authentication_required": boolean
            }
        ]
    },
    "modules": [
        {
            "name": "string",
            "type": "backend|frontend|shared",
            "description": "string",
            "dependencies": ["string"]
        }
    ],
    "deployment_strategy": {
        "containerization": "Docker",
        "orchestration": "string (e.g., Docker Compose, Kubernetes)",
        "ci_cd": "string (e.g., GitHub Actions, GitLab CI)"
    }
}

Choose modern, well-supported technologies with good documentation."""
    
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
            temperature=0.2,  # أقل جداً للحصول على JSON صحيح
            max_tokens=2500  # تقليل الحجم لتجنب القطع
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
        
        nfr = plan.get('non_functional_requirements', {})
        
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

Design a complete architecture following the JSON structure in your system prompt.

Important:
1. Choose technologies appropriate for {complexity} complexity
2. Design a simple database schema (2-4 tables maximum)
3. Create essential API endpoints only (5-8 endpoints)
4. Break down into 3-5 modules maximum
5. Keep it concise and focused

Output ONLY valid JSON, no additional text. Keep the response under 2000 tokens."""
    
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
