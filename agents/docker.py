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

    def get_system_prompt(self) -> str:
        return """You are a senior DevOps engineer specializing in Docker and container orchestration.

Your role is to generate production-ready Docker configuration for full-stack applications.

DOCKER STANDARDS:
- Use multi-stage builds for frontend to minimize image size
- Use slim/alpine base images for smaller footprint
- Always define health checks for services
- Use environment variables with sensible defaults
- Pin dependency versions for reproducibility
- Add proper .dockerignore patterns
- Use named volumes for persistent data
- Ensure CORS-compatible network configuration between services

For SQLite databases: NO separate DB container needed — just a volume mount
For PostgreSQL databases: include a postgres service with health checks"""

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
        إنشاء Docker files - hardcoded high-quality templates
        """
        tech_stack = architecture.get('tech_stack', {})
        project_name = project_plan.get('project_name', 'app').lower().replace(' ', '_')
        database = tech_stack.get('database', {}).get('primary', 'SQLite')
        use_postgres = 'postgres' in database.lower() or 'postgresql' in database.lower()

        compose_db_section = ''
        compose_backend_env = 'DATABASE_URL=sqlite:///./app.db'
        compose_db_depends = ''
        compose_volumes_section = ''

        if use_postgres:
            compose_backend_env = 'DATABASE_URL=postgresql://user:password@db:5432/appdb'
            compose_db_depends = '''    depends_on:
      db:
        condition: service_healthy'''
            compose_db_section = '''
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5'''
            compose_volumes_section = '''
volumes:
  postgres_data:'''
        else:
            compose_volumes_section = '''
volumes:
  sqlite_data:'''
            compose_db_section = ''

        return {
            'docker/Dockerfile.backend': '''FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \\
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
            'docker/Dockerfile.frontend': '''# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies (layer cache)
COPY frontend/package*.json ./
RUN npm ci --only=production=false

# Copy source and build
COPY frontend/ .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine AS runner

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s \\
    CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
''',
            'docker/nginx.conf': '''server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Handle React Router (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
''',
            'docker-compose.yml': f'''version: '3.9'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - {compose_backend_env}
      - SECRET_KEY=change-this-secret-key-in-production
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
    volumes:
      - sqlite_data:/app
    restart: unless-stopped
{compose_db_depends}
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
{compose_db_section}
{compose_volumes_section}
''',
            'docker-compose.dev.yml': f'''version: '3.9'

# Development override — mounts source code for hot reload
services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    environment:
      - {compose_backend_env}
      - SECRET_KEY=dev-secret-key-not-for-production

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
      target: builder
    command: npm run dev -- --host 0.0.0.0 --port 3000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000/api
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
.pytest_cache/
.coverage
htmlcov/

# Node
node_modules/
dist/
build/
npm-debug.log*
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

# Env files (use environment variables in compose)
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Test artifacts
output/
'''
        }
