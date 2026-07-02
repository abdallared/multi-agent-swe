"""
FastAPI Backend for AI Software Company UI

Uses Pipeline orchestrator for parallel agent execution with real-time
WebSocket updates.
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
from core.pipeline import Pipeline, PipelineUpdate
from agents.base_agent import BaseAgent

# ── Shared Memory Instance ──────────────────────────────────────
try:
    from memory.project_memory import ProjectMemory
    project_memory = ProjectMemory(
        persist_dir="./memory/db",
        ollama_base_url=settings.ollama_base_url,
        embeddings_model=settings.embeddings_model,
    )
except Exception as e:
    import logging as _log
    _log.getLogger(__name__).warning(f"Memory system unavailable: {e}")
    project_memory = None

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


class WebSocketProjectGenerator:
    """
    Project generation with real-time WebSocket updates via Pipeline.
    """

    def __init__(self, websocket: WebSocket):
        self.ws = websocket
        # Use absolute path relative to this file so output always goes to ui/backend/output/
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    async def send_update(self, type: str, data: dict):
        """Send update to client"""
        await self.ws.send_json({
            "type": type,
            "data": data
        })

    async def generate_project(self, user_prompt: str):
        """Generate complete project with real-time updates using Pipeline."""
        loop = asyncio.get_running_loop()

        def verbose_callback(entry: dict):
            # Safe dispatch to main loop thread
            asyncio.run_coroutine_threadsafe(
                self.send_update("verbose", entry),
                loop
            )

        BaseAgent.set_verbose_callback(verbose_callback)

        try:
            pipeline = Pipeline(ollama, output_dir=str(self.output_dir), memory=project_memory)

            async def on_pipeline_update(update: PipelineUpdate):
                """Forward pipeline updates to WebSocket."""
                await self.send_update(update.event, {
                    "phase": update.phase,
                    "name": update.name,
                    "status": update.status,
                    **update.data,
                })

            await pipeline.run(user_prompt, on_update=on_pipeline_update)

        except Exception as e:
            await self.send_update("error", {
                "message": str(e)
            })
        finally:
            BaseAgent.set_verbose_callback(None)


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
        generator = WebSocketProjectGenerator(websocket)
        await generator.generate_project(user_prompt)

    except WebSocketDisconnect:
        if websocket in active_connections:
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
    cache_stats = ollama.cache_stats
    return {
        "status": "healthy",
        "ollama_connected": len(ollama.list_models()) > 0,
        "cache": cache_stats,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Software Company UI Backend",
        "version": "2.1.0",
        "features": [
            "parallel_execution",
            "response_caching",
            "auto_retry",
            "project_memory",
        ],
        "memory_enabled": project_memory is not None,
        "docs": "/docs"
    }


@app.get("/api/memory/stats")
async def memory_stats():
    """Return memory system statistics"""
    if project_memory is None:
        return {"enabled": False, "message": "Memory system not available"}
    try:
        stats = project_memory.get_stats()
        return {"enabled": True, **stats}
    except Exception as e:
        return {"enabled": True, "error": str(e)}


@app.delete("/api/memory/clear")
async def memory_clear():
    """Clear all stored project memory"""
    if project_memory is None:
        return {"success": False, "message": "Memory system not available"}
    try:
        project_memory.clear()
        return {"success": True, "message": "Memory cleared"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("AI Software Company Backend")
    print("="*60)
    print("Backend running on: http://localhost:8000")
    print("API Docs:           http://localhost:8000/docs")
    print("WebSocket:          ws://localhost:8000/ws/generate")
    print("[*] Parallel execution enabled")
    print("="*60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
