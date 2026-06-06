"""
AI Software Company - Main Entry Point

Uses the Pipeline orchestrator for parallel agent execution.
"""

import logging
import sys
import json
from pathlib import Path
from core.config import settings
from utils.ollama_interface import ollama
from core.pipeline import Pipeline, PipelineUpdate

# Initialize memory system (graceful if unavailable)
try:
    from memory.project_memory import ProjectMemory
    project_memory = ProjectMemory(
        persist_dir="./memory/db",
        ollama_base_url=settings.ollama_base_url,
        embeddings_model=settings.embeddings_model,
    )
except Exception:
    project_memory = None

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def _cli_update_handler(update: PipelineUpdate):
    """Handle pipeline progress updates for CLI display."""
    if update.event == "phase_start":
        phase_emojis = {
            "Planning": "📋", "Architecture": "🏗️", "Backend Code": "💻",
            "Frontend Code": "🎨", "File Building": "📁", "Testing": "🧪", "Docker": "🐳",
        }
        emoji = phase_emojis.get(update.name, "⚙️")
        print(f"\n{'=' * 70}")
        print(f"{emoji}  Phase {update.phase}: {update.name}")
        print(f"{'=' * 70}")
        print(f"⏳ Working on {update.name}...\n")

    elif update.event == "phase_complete":
        print(f"✅ {update.name} completed!")
        data = update.data
        if update.name == "Planning":
            print(f"   📦 Project: {data.get('project_name', 'N/A')}")
            print(f"   ✨ Features: {data.get('features_count', 0)}")
            print(f"   📖 User Stories: {data.get('user_stories_count', 0)}")
        elif update.name == "Architecture":
            print(f"   Backend:  {data.get('backend', 'N/A')}")
            print(f"   Frontend: {data.get('frontend', 'N/A')}")
            print(f"   Database: {data.get('database', 'N/A')}")
            print(f"   Tables:   {data.get('tables_count', 0)}")
            print(f"   Endpoints: {data.get('endpoints_count', 0)}")
            print(f"   Complexity: {data.get('complexity', 'N/A')}")
        elif "files_count" in data:
            print(f"   📝 Generated {data['files_count']} files")
        elif "test_files" in data:
            print(f"   🧪 Generated {data['test_files']} test files")
        elif "docker_files" in data:
            print(f"   🐳 Generated {data['docker_files']} Docker files")

    elif update.event == "generation_complete":
        data = update.data
        print(f"\n{'=' * 70}")
        print("🎉 Project Generation Complete!")
        print(f"{'=' * 70}")
        print(f"\n📦 Project: {data.get('project_name', 'N/A')}")
        print(f"📁 Location: {data.get('project_path', 'N/A')}")
        print(f"📊 Total Files: {data.get('total_files', 0)}")
        print(f"⏱️  Time: {data.get('elapsed_seconds', 0)}s")

        summary = data.get("summary", {})
        print(f"\n✨ What was generated:")
        print(f"   ✅ Project Plan ({summary.get('features', 0)} features)")
        print(f"   ✅ Backend Code ({summary.get('backend_files', 0)} files)")
        print(f"   ✅ Frontend Code ({summary.get('frontend_files', 0)} files)")
        print(f"   ✅ Test Suite ({summary.get('test_files', 0)} files)")
        print(f"   ✅ Docker Config ({summary.get('docker_files', 0)} files)")
        print(f"   ✅ README Documentation")

        project_path = data.get("project_path", "")
        print(f"\n🚀 Next Steps:")
        print(f"\n   Backend:")
        print(f"   1. cd {project_path}/backend")
        print(f"   2. python -m venv venv")
        print(f"   3. venv\\Scripts\\activate")
        print(f"   4. pip install -r requirements.txt")
        print(f"   5. uvicorn app.main:app --reload")
        print(f"\n   Frontend:")
        print(f"   1. cd {project_path}/frontend")
        print(f"   2. npm install")
        print(f"   3. npm run dev")

    elif update.event == "error":
        print(f"\n❌ Error: {update.data.get('message', 'Unknown error')}")


def main():
    """
    نقطة البداية الرئيسية — uses Pipeline for parallel execution
    """
    print("=" * 70)
    print("🤖 AI Software Company - Autonomous Project Generator")
    print("=" * 70)
    print()
    print("💡 Powered by Ollama (Local LLMs)")
    print(f"📦 Models: {settings.planner_model} / {settings.backend_model}")
    print("⚡ Parallel execution enabled (Backend + Frontend run concurrently)")
    if project_memory:
        print(f"📚 Memory: {project_memory.get_stats()['total_projects']} past projects stored")
    else:
        print("📚 Memory: disabled (chromadb not installed or embeddings model unavailable)")
    print()

    # Get user input
    user_prompt = input("📝 Describe your project: ")

    if not user_prompt.strip():
        print("❌ Error: Project description cannot be empty")
        return

    print(f"\n🚀 Starting project generation...")
    print(f"💭 Analyzing: {user_prompt}")
    print()

    try:
        pipeline = Pipeline(ollama, output_dir=settings.output_dir, memory=project_memory)
        result = pipeline.run_sync(user_prompt, on_update=_cli_update_handler)

        # Save plan and architecture as JSON
        if result:
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(exist_ok=True)

            plan = result.get("plan")
            if plan:
                plan_file = output_dir / f"{result['clean_project_name']}_plan.json"
                with open(plan_file, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Plan saved to: {plan_file}")

            arch = result.get("architecture")
            if arch:
                arch_file = output_dir / f"{result['clean_project_name']}_architecture.json"
                with open(arch_file, "w", encoding="utf-8") as f:
                    json.dump(arch, f, indent=2, ensure_ascii=False)
                print(f"💾 Architecture saved to: {arch_file}")

        print("\n" + "=" * 70)
        print("✨ Generation Complete!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
