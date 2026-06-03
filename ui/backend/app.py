"""
FastAPI Backend for AI Software Company UI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import asyncio
import json
from pathlib import Path
import sys
import os
import zipfile
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.config import settings
from utils.ollama_interface import ollama
from agents.planner import PlannerAgent
from agents.architect import ArchitectAgent
from agents.backend import BackendAgent
from agents.frontend import FrontendAgent
from agents.testing import TestingAgent
from agents.docker import DockerAgent
from builder.file_builder import FileBuilder

app = FastAPI(title="AI Software Company UI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active connections
active_connections: list[WebSocket] = []


class ProjectGenerator:
    """
    Project generation with real-time updates
    """
    
    def __init__(self, websocket: WebSocket):
        self.ws = websocket
        # Use absolute path relative to this file so output always goes to ui/backend/output/
        # regardless of where uvicorn is launched from
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    async def send_update(self, type: str, data: dict):
        """Send update to client"""
        await self.ws.send_json({
            "type": type,
            "data": data
        })
    
    async def generate_project(self, user_prompt: str):
        """Generate complete project with real-time updates"""
        from agents.base_agent import BaseAgent
        
        loop = asyncio.get_running_loop()
        
        def verbose_callback(entry: dict):
            # Safe dispatch to main loop thread
            asyncio.run_coroutine_threadsafe(
                self.send_update("verbose", entry),
                loop
            )
            
        BaseAgent.set_verbose_callback(verbose_callback)
        
        try:
            # Phase 1: Planning
            await self.send_update("phase_start", {
                "phase": 1,
                "name": "Planning",
                "status": "running"
            })
            
            planner = PlannerAgent(ollama, None)
            plan_result = await asyncio.to_thread(planner.execute, {'user_prompt': user_prompt})
            plan = plan_result['project_plan']
            
            await self.send_update("phase_complete", {
                "phase": 1,
                "name": "Planning",
                "status": "completed",
                "data": {
                    "project_name": plan['project_name'],
                    "features_count": len(plan['features']),
                    "user_stories_count": len(plan['user_stories'])
                }
            })
            
            # Phase 2: Architecture
            await self.send_update("phase_start", {
                "phase": 2,
                "name": "Architecture",
                "status": "running"
            })
            
            architect = ArchitectAgent(ollama, None)
            arch_result = await asyncio.to_thread(architect.execute, {'project_plan': plan})
            arch = arch_result['architecture']
            
            await self.send_update("phase_complete", {
                "phase": 2,
                "name": "Architecture",
                "status": "completed",
                "data": {
                    "backend": arch['tech_stack']['backend']['framework'],
                    "frontend": arch['tech_stack']['frontend']['framework'],
                    "database": arch['tech_stack']['database']['primary'],
                    "tables_count": len(arch['database_schema']['tables']),
                    "endpoints_count": len(arch['api_design']['endpoints'])
                }
            })
            
            # Phase 3: Backend Code
            await self.send_update("phase_start", {
                "phase": 3,
                "name": "Backend Code",
                "status": "running"
            })
            
            backend_agent = BackendAgent(ollama, None)
            backend_result = await asyncio.to_thread(backend_agent.execute, {
                'project_plan': plan,
                'architecture': arch
            })
            backend_code = backend_result['backend_code']
            
            await self.send_update("phase_complete", {
                "phase": 3,
                "name": "Backend Code",
                "status": "completed",
                "data": {
                    "files_count": len(backend_code['files'])
                }
            })
            
            # Phase 4: File Building
            await self.send_update("phase_start", {
                "phase": 4,
                "name": "File Building",
                "status": "running"
            })
            
            builder = FileBuilder(output_dir=str(self.output_dir))
            project_dir = builder.create_project_structure(
                project_name=plan['project_name'],
                architecture=arch
            )
            
            backend_dir = project_dir / "backend"
            builder.write_files(backend_code['files'], backend_dir)
            
            await self.send_update("phase_complete", {
                "phase": 4,
                "name": "File Building",
                "status": "completed",
                "data": {
                    "project_path": str(project_dir)
                }
            })
            
            # Phase 5: Frontend Code
            await self.send_update("phase_start", {
                "phase": 5,
                "name": "Frontend Code",
                "status": "running"
            })
            
            frontend_agent = FrontendAgent(ollama, None)
            frontend_result = await asyncio.to_thread(frontend_agent.execute, {
                'project_plan': plan,
                'architecture': arch
            })
            frontend_code = frontend_result['frontend_code']
            
            frontend_dir = project_dir / "frontend"
            builder.write_files(frontend_code['files'], frontend_dir)
            
            await self.send_update("phase_complete", {
                "phase": 5,
                "name": "Frontend Code",
                "status": "completed",
                "data": {
                    "files_count": len(frontend_code['files'])
                }
            })
            
            # Phase 6: Testing
            await self.send_update("phase_start", {
                "phase": 6,
                "name": "Testing",
                "status": "running"
            })
            
            testing_agent = TestingAgent(ollama, None)
            test_result = await asyncio.to_thread(testing_agent.execute, {
                'project_plan': plan,
                'architecture': arch,
                'backend_code': backend_code
            })
            
            backend_tests = test_result['backend_tests']
            backend_dir = project_dir / "backend"
            builder.write_files(backend_tests, backend_dir)
            
            await self.send_update("phase_complete", {
                "phase": 6,
                "name": "Testing",
                "status": "completed",
                "data": {
                    "test_files": len(backend_tests)
                }
            })
            
            # Phase 7: Docker
            await self.send_update("phase_start", {
                "phase": 7,
                "name": "Docker",
                "status": "running"
            })
            
            docker_agent = DockerAgent(ollama, None)
            docker_result = await asyncio.to_thread(docker_agent.execute, {
                'project_plan': plan,
                'architecture': arch
            })
            
            docker_files = docker_result['docker_files']
            builder.write_files(docker_files, project_dir)
            
            await self.send_update("phase_complete", {
                "phase": 7,
                "name": "Docker",
                "status": "completed",
                "data": {
                    "docker_files": len(docker_files)
                }
            })
            
            # Create README
            project_info = {
                'name': plan['project_name'],
                'description': plan['description'],
                'backend': arch['tech_stack']['backend']['framework'],
                'frontend': arch['tech_stack']['frontend']['framework'],
                'database': arch['tech_stack']['database']['primary'],
                'features': [f['name'] for f in plan['features']],
                'test_command': test_result.get('test_commands', {}).get('backend', 'pytest tests/ -v')
            }
            builder.create_readme(project_dir, project_info)
            
            # Get file tree
            file_tree = self._get_file_tree(project_dir)
            
            # تنظيف اسم المشروع للتأكد من التطابق
            clean_project_name = plan['project_name'].lower()
            clean_project_name = clean_project_name.replace(' ', '_')
            clean_project_name = ''.join(c for c in clean_project_name if c.isalnum() or c == '_')
            
            # Complete
            await self.send_update("generation_complete", {
                "project_name": plan['project_name'],
                "clean_project_name": clean_project_name,  # اسم المشروع النظيف للتحميل
                "project_path": str(project_dir),
                "file_tree": file_tree,
                "total_files": len(backend_code['files']) + len(frontend_code['files']) + len(backend_tests) + len(docker_files),
                "summary": {
                    "features": len(plan['features']),
                    "backend_files": len(backend_code['files']),
                    "frontend_files": len(frontend_code['files']),
                    "test_files": len(backend_tests),
                    "docker_files": len(docker_files)
                }
            })
            
        except Exception as e:
            await self.send_update("error", {
                "message": str(e)
            })
        finally:
            BaseAgent.set_verbose_callback(None)
    
    def _get_file_tree(self, project_dir: Path) -> dict:
        """Get file tree structure"""
        def build_tree(path: Path) -> dict:
            if path.is_file():
                return {
                    "name": path.name,
                    "type": "file",
                    "path": str(path.relative_to(project_dir))
                }
            else:
                children = []
                try:
                    for child in sorted(path.iterdir()):
                        if child.name not in ['__pycache__', '.git', 'node_modules', 'venv']:
                            children.append(build_tree(child))
                except PermissionError:
                    pass
                
                return {
                    "name": path.name,
                    "type": "folder",
                    "path": str(path.relative_to(project_dir)),
                    "children": children
                }
        
        return build_tree(project_dir)


@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """WebSocket endpoint for project generation"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Receive user prompt
        data = await websocket.receive_json()
        user_prompt = data.get('prompt', '')
        
        if not user_prompt:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Prompt is required"}
            })
            return
        
        # Generate project
        generator = ProjectGenerator(websocket)
        await generator.generate_project(user_prompt)
        
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })


@app.get("/api/download/{project_name}")
async def download_project(project_name: str):
    """Download project as ZIP"""
    try:
        print(f"🔍 Download requested for: {project_name}")
        
        # تنظيف اسم المشروع
        clean_name = project_name.lower()
        clean_name = clean_name.replace(' ', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        print(f"🔍 Looking for project: {clean_name}")
        
        output_dir = Path(__file__).parent / "output"
        project_path = output_dir / clean_name
        
        if not project_path.exists():
            available = [p.name for p in output_dir.iterdir() if p.is_dir()] if output_dir.exists() else []
            return {"error": f"Project not found: {clean_name}", "available": available}
        
        # إنشاء ZIP file في الذاكرة
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # إضافة جميع الملفات
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and '__pycache__' not in str(file_path):
                    arcname = file_path.relative_to(project_path)
                    zip_file.write(file_path, arcname)
        
        # إعادة المؤشر إلى البداية
        zip_buffer.seek(0)
        
        print(f"✅ ZIP created successfully for: {clean_name}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={clean_name}.zip",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/api/file/{project_name}/{file_path:path}")
async def get_file_content(project_name: str, file_path: str):
    """Get file content"""
    try:
        # تنظيف اسم المشروع
        clean_name = project_name.lower()
        clean_name = clean_name.replace(' ', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        output_dir = Path(__file__).parent / "output"
        full_path = output_dir / clean_name / file_path
        
        if full_path.exists() and full_path.is_file():
            content = full_path.read_text(encoding='utf-8')
            return {"content": content, "path": str(full_path)}
        
        return {"error": f"File not found: {file_path}"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "ollama_connected": len(ollama.list_models()) > 0
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Software Company UI Backend",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("AI Software Company Backend")
    print("="*60)
    print("Backend running on: http://localhost:8000")
    print("API Docs:           http://localhost:8000/docs")
    print("WebSocket:          ws://localhost:8000/ws/generate")
    print("="*60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
