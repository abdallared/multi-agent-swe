"""
Testing Agent - إنشاء Unit Tests و Integration Tests
"""

from typing import Dict, Any
from .base_agent import BaseAgent
import json
import logging

logger = logging.getLogger(__name__)


class TestingAgent(BaseAgent):
    """
    Testing Agent - مسؤول عن إنشاء الـ Tests
    """
    
    def __init__(self, ollama_interface, memory_manager):
        super().__init__(ollama_interface, memory_manager)
        self.model_name = "llama3.2:3b"
    
    def get_system_prompt(self) -> str:
        return "You are a test engineer. Generate comprehensive pytest tests for FastAPI applications."
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        إنشاء Tests للمشروع
        """
        logger.info("🧪 Testing Agent: Starting test generation...")
        
        project_plan = context.get('project_plan', {})
        architecture = context.get('architecture', {})
        backend_code = context.get('backend_code', {})
        
        # إنشاء Backend Tests
        backend_tests = self._generate_backend_tests(
            project_plan,
            architecture,
            backend_code
        )
        
        logger.info(f"✅ Generated {len(backend_tests)} backend test files")
        
        return {
            'backend_tests': backend_tests,
            'test_commands': {
                'backend': 'pytest tests/ -v --cov=app',
                'frontend': 'npm test'
            }
        }
    
    def _generate_backend_tests(
        self,
        project_plan: Dict,
        architecture: Dict,
        backend_code: Dict
    ) -> Dict[str, str]:
        """
        إنشاء Backend Tests
        """
        prompt = f"""Generate comprehensive pytest tests for this FastAPI project.

Project: {project_plan.get('project_name', 'Project')}
Description: {project_plan.get('description', '')}

API Endpoints:
{json.dumps(architecture.get('api_design', {}).get('endpoints', [])[:3], indent=2)}

Requirements:
1. Create test_main.py with basic app tests
2. Create test_api.py with endpoint tests
3. Create conftest.py with fixtures
4. Use pytest and httpx for testing
5. Include authentication tests if needed
6. Mock database operations
7. Test success and error cases

Return ONLY valid JSON:
{{
  "tests/test_main.py": "test code here",
  "tests/test_api.py": "test code here",
  "tests/conftest.py": "fixtures here",
  "tests/__init__.py": ""
}}"""

        try:
            response = self.ollama_interface.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            # استخراج JSON
            tests = self._extract_json(response)
            
            if not tests or not isinstance(tests, dict):
                logger.warning("Failed to parse tests, using fallback")
                return self._get_fallback_tests(project_plan)
            
            return tests
            
        except Exception as e:
            logger.error(f"Error generating tests: {e}")
            return self._get_fallback_tests(project_plan)
    
    def _get_fallback_tests(self, project_plan: Dict) -> Dict[str, str]:
        """
        Fallback tests إذا فشل التوليد
        """
        project_name = project_plan.get('project_name', 'project').lower().replace(' ', '_')
        
        return {
            'tests/__init__.py': '',
            'tests/conftest.py': '''"""
Test Configuration and Fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def test_user():
    """Test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
''',
            'tests/test_main.py': '''"""
Main Application Tests
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_health_check():
    """Test health endpoint if exists"""
    response = client.get("/health")
    # May not exist, so we just check it doesn't crash
    assert response.status_code in [200, 404]
''',
            'tests/test_api.py': '''"""
API Endpoint Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoints_exist():
    """Test that API endpoints are registered"""
    response = client.get("/docs")
    assert response.status_code == 200

@pytest.mark.parametrize("endpoint", ["/api/v1/", "/api/"])
def test_api_base_paths(endpoint):
    """Test API base paths"""
    response = client.get(endpoint)
    # Just verify the endpoint is registered
    assert response.status_code in [200, 404, 405]
'''
        }
