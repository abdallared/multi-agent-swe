"""
Docker Agent - إنشاء Docker Configuration
"""

from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class DockerAgent(BaseAgent):
    """
    Docker Agent - مسؤول عن إنشاء Docker files
    """
    
    def __init__(self, ollama_interface, memory_manager):
        super().__init__(ollama_interface, memory_manager)
        self.model_name = "llama3.2:3b"
    
    def get_system_prompt(self) -> str:
        return "You are a DevOps engineer. Generate Docker configuration files."
    
    def get_system_prompt(self) -> str:
        return "You are a DevOps engineer. Generate Docker configuration files."
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        إنشاء Docker configuration
        """
        logger.info("🐳 Docker Agent: Creating Docker files...")
        
        project_plan = context.get('project_plan', {})
        architecture = context.get('architecture', {})
        
        docker_files = self._generate_docker_files(project_plan, architecture)
        
        logger.info(f"✅ Generated {len(docker_files)} Docker files")
        
        return {'docker_files': docker_files}
    
    def _generate_docker_files(
        self,
        project_plan: Dict,
        architecture: Dict
    ) -> Dict[str, str]:
        """
        إنشاء Docker files
        """
        tech_stack = architecture.get('tech_stack', {})
        backend_framework = tech_stack.get('backend', {}).get('framework', 'FastAPI')
        frontend_framework = tech_stack.get('frontend', {}).get('framework', 'React')
        database = tech_stack.get('database', {}).get('primary', 'PostgreSQL')
        
        return {
            'docker/Dockerfile.backend': f'''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
            'docker/Dockerfile.frontend': f'''FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy application
COPY frontend/ .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
''',
            'docker-compose.yml': f'''version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
''',
            '.dockerignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Env
.env
.env.local
'''
        }
