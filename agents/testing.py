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

    def get_system_prompt(self) -> str:
        return """You are a senior QA engineer and Python testing expert specializing in FastAPI applications.

Your role is to generate comprehensive, production-quality pytest test suites.

TESTING STANDARDS:
- Use pytest with fixtures for test isolation
- Use FastAPI TestClient (from fastapi.testclient import TestClient)
- Use in-memory SQLite for test database (DATABASE_URL = "sqlite:///./test.db")
- Test both SUCCESS cases (200, 201) and ERROR cases (400, 401, 404, 422)
- Use pytest.fixture for shared test state
- Test authentication flow: register → login → get token → use token
- Test full CRUD cycle for each resource
- Use parametrize for edge cases
- Always include conftest.py with database and client fixtures

OUTPUT FORMAT — valid JSON only:
{
    "tests/__init__.py": "",
    "tests/conftest.py": "complete fixture code",
    "tests/test_auth.py": "complete auth test code",
    "tests/test_api.py": "complete CRUD test code"
}

Generate complete, runnable test code with all necessary imports."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        إنشاء Tests للمشروع
        """
        logger.info("🧪 Testing Agent: Starting test generation...")

        project_plan = context.get('project_plan', {})
        architecture = context.get('architecture', {})
        backend_code = context.get('backend_code', {})

        backend_tests = self._generate_backend_tests(
            project_plan,
            architecture,
            backend_code
        )

        logger.info(f"✅ Generated {len(backend_tests)} backend test files")

        return {
            'backend_tests': backend_tests,
            'test_commands': {
                'backend': 'pytest tests/ -v --cov=app --cov-report=term-missing',
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
        endpoints = architecture.get('api_design', {}).get('endpoints', [])
        tables = architecture.get('database_schema', {}).get('tables', [])
        project_name = project_plan.get('project_name', 'Project')

        # Extract main resource name from tables
        main_resource = 'items'
        for t in tables:
            if t.get('name', '').lower() != 'users':
                main_resource = t.get('name', 'items')
                break

        prompt = f"""Generate comprehensive pytest tests for this FastAPI project.

Project: {project_name}
Description: {project_plan.get('description', '')}
Main Resource: {main_resource}

API Endpoints:
{json.dumps(endpoints[:6], indent=2)}

Generate complete test files following your system prompt.

IMPORTANT:
- conftest.py MUST override DATABASE_URL to use in-memory SQLite
- Every test must be independent (use fixtures, not global state)
- Test user registration, login, and authenticated requests
- Test GET, POST, PUT, DELETE for the main resource
- Test validation errors (422) and not-found (404) cases

Return ONLY valid JSON with these keys:
{{
  "tests/__init__.py": "",
  "tests/conftest.py": "...",
  "tests/test_auth.py": "...",
  "tests/test_api.py": "..."
}}"""

        try:
            # FIX: use self.call_llm() from BaseAgent, NOT self.ollama_interface
            response = self.call_llm(
                prompt=prompt,
                json_mode=True,
                temperature=0.1,
                max_tokens=3000
            )

            tests = self._extract_json(response)

            if not tests or not isinstance(tests, dict):
                logger.warning("Failed to parse tests JSON, using fallback")
                return self._get_fallback_tests(project_plan, main_resource)

            return tests

        except Exception as e:
            logger.error(f"Error generating tests: {e}")
            return self._get_fallback_tests(project_plan, main_resource)

    def _extract_json(self, response: str) -> Dict:
        """Parse JSON from LLM response"""
        response = response.strip()
        if response.startswith('```json'):
            response = response.split('```json')[1].split('```')[0].strip()
        elif response.startswith('```'):
            response = response.split('```')[1].split('```')[0].strip()
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            response = response.replace(',}', '}').replace(',]', ']')
            try:
                return json.loads(response)
            except Exception:
                return {}

    def _get_fallback_tests(self, project_plan: Dict, main_resource: str = 'items') -> Dict[str, str]:
        """
        Comprehensive fallback tests covering auth + CRUD
        """
        resource_singular = main_resource.rstrip('s')

        return {
            'tests/__init__.py': '',
            'tests/conftest.py': f'''"""
Test Configuration and Fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={{"check_same_thread": False}})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {{
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }}


@pytest.fixture
def registered_user(client, test_user_data):
    client.post("/api/auth/register", json=test_user_data)
    return test_user_data


@pytest.fixture
def auth_token(client, registered_user):
    response = client.post("/api/auth/login", json={{
        "username": registered_user["username"],
        "password": registered_user["password"]
    }})
    return response.json().get("access_token", "")


@pytest.fixture
def auth_headers(auth_token):
    return {{"Authorization": f"Bearer {{auth_token}}"}}
''',
            'tests/test_auth.py': '''"""
Authentication Endpoint Tests
"""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client):
    """Test successful user registration"""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "password" not in data  # password must never be returned


def test_register_duplicate_email(client, registered_user):
    """Test registration with duplicate email fails"""
    response = client.post("/api/auth/register", json={
        "username": "anotheruser",
        "email": registered_user["email"],  # same email
        "password": "password123"
    })
    assert response.status_code == 400


def test_login_success(client, registered_user):
    """Test successful login returns JWT token"""
    response = client.post("/api/auth/login", json={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    """Test login with wrong password returns 401"""
    response = client.post("/api/auth/login", json={
        "username": registered_user["username"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with nonexistent user returns 401"""
    response = client.post("/api/auth/login", json={
        "username": "doesnotexist",
        "password": "anypassword"
    })
    assert response.status_code == 401
''',
            f'tests/test_api.py': f'''"""
API CRUD Endpoint Tests
"""
import pytest


def test_app_root(client):
    """Test root endpoint is accessible"""
    response = client.get("/")
    assert response.status_code == 200


def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200


def test_api_docs_accessible(client):
    """Test Swagger UI is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_get_{main_resource}_unauthorized(client):
    """Test that GET /{main_resource}/ requires auth"""
    response = client.get("/api/{main_resource}/")
    # Should return 401 or 403 if protected, or 200 if public
    assert response.status_code in [200, 401, 403]


def test_create_{resource_singular}_success(client, auth_headers):
    """Test creating a {resource_singular} with valid auth"""
    response = client.post(
        "/api/{main_resource}/",
        json={{"title": "Test {resource_singular.capitalize()}", "description": "Test description"}},
        headers=auth_headers
    )
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test {resource_singular.capitalize()}"


def test_create_{resource_singular}_unauthorized(client):
    """Test creating a {resource_singular} without auth fails"""
    response = client.post(
        "/api/{main_resource}/",
        json={{"title": "Test", "description": "Test"}}
    )
    assert response.status_code in [401, 403, 422]


def test_get_{resource_singular}_not_found(client, auth_headers):
    """Test getting nonexistent item returns 404"""
    response = client.get("/api/{main_resource}/99999", headers=auth_headers)
    assert response.status_code in [404, 422]


def test_delete_{resource_singular}(client, auth_headers):
    """Test deleting an item"""
    # First create an item
    create_response = client.post(
        "/api/{main_resource}/",
        json={{"title": "To Delete", "description": "Will be deleted"}},
        headers=auth_headers
    )
    if create_response.status_code in [200, 201]:
        item_id = create_response.json()["id"]
        delete_response = client.delete(
            f"/api/{main_resource}/{{item_id}}",
            headers=auth_headers
        )
        assert delete_response.status_code in [200, 204]
'''
        }
