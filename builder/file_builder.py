"""
File Builder - إنشاء الملفات والمجلدات
"""

from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FileBuilder:
    """
    مسؤول عن إنشاء الملفات والمجلدات للمشروع
    """
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def create_project_structure(
        self,
        project_name: str,
        architecture: Dict[str, Any]
    ) -> Path:
        """
        إنشاء هيكل المشروع الكامل
        """
        # تنظيف اسم المشروع - إزالة المسافات والرموز الخاصة
        clean_name = project_name.lower()
        clean_name = clean_name.replace(' ', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        # إنشاء مجلد المشروع
        project_dir = self.output_dir / clean_name
        project_dir.mkdir(exist_ok=True)
        
        logger.info(f"Creating project structure at: {project_dir}")
        
        # إنشاء المجلدات الأساسية
        self._create_base_structure(project_dir, architecture)
        
        # إنشاء ملف التشغيل التلقائي (run.bat)
        self.create_run_bat(project_dir)
        
        return project_dir
    
    def _create_base_structure(self, project_dir: Path, architecture: Dict):
        """
        إنشاء الهيكل الأساسي
        """
        # Backend structure
        backend_dir = project_dir / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        (backend_dir / "app").mkdir(exist_ok=True)
        (backend_dir / "app" / "api").mkdir(exist_ok=True)
        (backend_dir / "app" / "models").mkdir(exist_ok=True)
        (backend_dir / "app" / "schemas").mkdir(exist_ok=True)
        (backend_dir / "app" / "services").mkdir(exist_ok=True)
        (backend_dir / "app" / "core").mkdir(exist_ok=True)
        (backend_dir / "tests").mkdir(exist_ok=True)
        
        # Frontend structure
        frontend_dir = project_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        (frontend_dir / "src").mkdir(exist_ok=True)
        (frontend_dir / "src" / "components").mkdir(exist_ok=True)
        (frontend_dir / "src" / "pages").mkdir(exist_ok=True)
        (frontend_dir / "src" / "services").mkdir(exist_ok=True)
        (frontend_dir / "src" / "types").mkdir(exist_ok=True)
        (frontend_dir / "public").mkdir(exist_ok=True)
        
        # Docker
        (project_dir / "docker").mkdir(exist_ok=True)
        
        logger.info("Base structure created")

    def create_run_bat(self, project_dir: Path):
        """
        إنشاء ملف run.bat لتشغيل المشروع بسهولة على ويندوز بدون دوجر
        """
        bat_content = """@echo off
title Project Runner
echo =======================================================================
echo              Starting Project Setup and Runner (No Docker)
echo =======================================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python.
    pause
    exit /b 1
)

:: Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js.
    pause
    exit /b 1
)

echo [1/4] Setting up Python virtual environment...
if not exist "backend\\venv" (
    python -m venv backend\\venv
)

echo [2/4] Installing backend dependencies...
cd backend
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
    )
)
call venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo [3/4] Installing frontend dependencies (this may take a minute)...
cd frontend
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
    )
)
if not exist "node_modules" (
    call npm install
)
cd ..

echo [4/4] Starting servers...
echo.
echo Launching Backend Server in a new window...
start "Backend Server" cmd /k "cd backend && call venv\\Scripts\\activate && uvicorn app.main:app --port 8001 --reload"

echo Launching Frontend Server in a new window...
:: Detect starting command (Vite vs CRA)
if exist "frontend\\vite.config.ts" (
    set START_CMD=npm run dev
) else if exist "frontend\\vite.config.js" (
    set START_CMD=npm run dev
) else (
    set START_CMD=npm start
)

start "Frontend Server" cmd /k "cd frontend && set PORT=3001 && set BROWSER=none && set NODE_OPTIONS=--openssl-legacy-provider && %START_CMD%"

echo.
echo =======================================================================
echo  Project is starting up!
echo  - Backend: http://127.0.0.1:8001
echo  - Frontend: http://localhost:3001
echo =======================================================================
echo.
pause
"""
        self.write_file(project_dir / "run.bat", bat_content)
    
    def write_file(self, filepath: Path, content: str):
        """
        كتابة ملف
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Created file: {filepath}")
        except Exception as e:
            logger.error(f"Failed to write file {filepath}: {e}")
            raise
    
    def write_files(self, files: Dict[str, str], base_dir: Path):
        """
        كتابة عدة ملفات
        """
        for filepath, content in files.items():
            full_path = base_dir / filepath
            self.write_file(full_path, content)
    
    def create_readme(self, project_dir: Path, project_info: Dict):
        """
        إنشاء README.md كامل
        """
        test_cmd = project_info.get('test_command', 'pytest tests/ -v')
        features_list = '\n'.join(f"- {f}" for f in project_info.get('features', []))
        
        readme_content = f"""# {project_info['name']}

{project_info.get('description', 'A full-stack web application generated by AI Software Company.')}

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | {project_info.get('backend', 'FastAPI')} |
| Frontend | {project_info.get('frontend', 'React + TypeScript')} |
| Database | {project_info.get('database', 'SQLite')} |
| Containerization | Docker + Docker Compose |

## Features

{features_list}

## Project Structure

```
{project_dir.name}/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, DB, Security
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   ├── tests/            # Pytest tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API service layer
│   │   └── types/        # TypeScript types
│   └── package.json
├── docker/               # Dockerfiles
├── docker-compose.yml
└── README.md
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
cd backend
{test_cmd}
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---
*Generated by [AI Software Company](https://github.com) 🤖*
"""
        self.write_file(project_dir / "README.md", readme_content)
