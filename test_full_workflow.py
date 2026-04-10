"""
Test Full Workflow - All Phases
"""

import logging
import sys
import json
from pathlib import Path
from core.config import settings
from utils.ollama_interface import ollama
from agents.planner import PlannerAgent
from agents.architect import ArchitectAgent
from agents.backend import BackendAgent
from agents.frontend import FrontendAgent
from builder.file_builder import FileBuilder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def test_full_workflow():
    """
    اختبار النظام الكامل
    """
    print("=" * 70)
    print("🧪 Testing Full Workflow - All 5 Phases")
    print("=" * 70)
    print()
    
    # Test prompt
    user_prompt = "Build a simple blog platform with user authentication and post management"
    
    print(f"📝 Test Prompt: {user_prompt}")
    print()
    
    try:
        # Phase 1: Planning
        print("=" * 70)
        print("📋 Phase 1: Planning")
        print("=" * 70)
        print("⏳ Generating plan...\n")
        
        planner = PlannerAgent(ollama, None)
        plan_result = planner.execute({'user_prompt': user_prompt})
        
        if plan_result['status'] != 'planning_completed':
            raise Exception("Planning failed")
        
        plan = plan_result['project_plan']
        print(f"✅ Plan generated: {plan['project_name']}")
        print(f"   Features: {len(plan['features'])}")
        print(f"   User Stories: {len(plan['user_stories'])}\n")
        
        # Phase 2: Architecture
        print("=" * 70)
        print("🏗️  Phase 2: Architecture")
        print("=" * 70)
        print("⏳ Designing architecture...\n")
        
        architect = ArchitectAgent(ollama, None)
        arch_result = architect.execute({'project_plan': plan})
        
        if arch_result['status'] != 'architecture_completed':
            raise Exception("Architecture failed")
        
        arch = arch_result['architecture']
        print(f"✅ Architecture designed")
        print(f"   Backend: {arch['tech_stack']['backend']['framework']}")
        print(f"   Frontend: {arch['tech_stack']['frontend']['framework']}")
        print(f"   Database: {arch['tech_stack']['database']['primary']}")
        print(f"   Tables: {len(arch['database_schema']['tables'])}")
        print(f"   Endpoints: {len(arch['api_design']['endpoints'])}\n")
        
        # Phase 3: Backend Code
        print("=" * 70)
        print("💻 Phase 3: Backend Code")
        print("=" * 70)
        print("⏳ Generating backend code...\n")
        
        backend_agent = BackendAgent(ollama, None)
        backend_result = backend_agent.execute({
            'project_plan': plan,
            'architecture': arch
        })
        
        if backend_result['status'] != 'backend_completed':
            raise Exception("Backend generation failed")
        
        backend_code = backend_result['backend_code']
        backend_files = backend_code['files']
        print(f"✅ Backend code generated: {len(backend_files)} files\n")
        
        # Phase 4: File Building
        print("=" * 70)
        print("🏗️  Phase 4: File Building")
        print("=" * 70)
        print("⏳ Creating project structure...\n")
        
        builder = FileBuilder(output_dir="./output/test")
        project_dir = builder.create_project_structure(
            project_name=plan['project_name'],
            architecture=arch
        )
        
        print(f"✅ Project structure created: {project_dir}")
        
        # Write backend files
        backend_dir = project_dir / "backend"
        builder.write_files(backend_files, backend_dir)
        print(f"✅ Backend files written: {len(backend_files)} files\n")
        
        # Phase 5: Frontend Code
        print("=" * 70)
        print("🎨 Phase 5: Frontend Code")
        print("=" * 70)
        print("⏳ Generating frontend code...\n")
        
        frontend_agent = FrontendAgent(ollama, None)
        frontend_result = frontend_agent.execute({
            'project_plan': plan,
            'architecture': arch
        })
        
        if frontend_result['status'] != 'frontend_completed':
            raise Exception("Frontend generation failed")
        
        frontend_code = frontend_result['frontend_code']
        frontend_files = frontend_code['files']
        print(f"✅ Frontend code generated: {len(frontend_files)} files\n")
        
        # Write frontend files
        frontend_dir = project_dir / "frontend"
        builder.write_files(frontend_files, frontend_dir)
        print(f"✅ Frontend files written: {len(frontend_files)} files\n")
        
        # Create README
        project_info = {
            'name': plan['project_name'],
            'description': plan['description'],
            'backend': arch['tech_stack']['backend']['framework'],
            'frontend': arch['tech_stack']['frontend']['framework'],
            'database': arch['tech_stack']['database']['primary'],
            'features': [f['name'] for f in plan['features']]
        }
        builder.create_readme(project_dir, project_info)
        print(f"✅ README created\n")
        
        # Final Summary
        print("=" * 70)
        print("🎉 Full Workflow Test Complete!")
        print("=" * 70)
        print()
        print(f"✅ All 5 phases completed successfully!")
        print()
        print(f"📊 Summary:")
        print(f"   Project: {plan['project_name']}")
        print(f"   Location: {project_dir}")
        print(f"   Backend Files: {len(backend_files)}")
        print(f"   Frontend Files: {len(frontend_files)}")
        print(f"   Total Files: {len(backend_files) + len(frontend_files)}")
        print()
        print(f"📁 Project Structure:")
        print(f"   {project_dir}/")
        print(f"   ├── backend/")
        print(f"   │   └── app/")
        print(f"   ├── frontend/")
        print(f"   │   └── src/")
        print(f"   └── README.md")
        print()
        print("=" * 70)
        print("✨ Test Passed!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
