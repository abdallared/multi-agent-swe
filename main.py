"""
AI Software Company - Main Entry Point
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
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    نقطة البداية الرئيسية
    """
    print("=" * 70)
    print("🤖 AI Software Company - Autonomous Project Generator")
    print("=" * 70)
    print()
    print("💡 Powered by Ollama (Local LLMs)")
    print(f"📦 Using: {settings.planner_model}")
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
        # Phase 1: Planning
        print("=" * 70)
        print("📋 Phase 1: Project Planning")
        print("=" * 70)
        print("⏳ Generating project plan (this may take 1-2 minutes)...\n")
        
        planner = PlannerAgent(ollama, None)
        result = planner.execute({'user_prompt': user_prompt})
        
        if result['status'] == 'planning_completed':
            plan = result['project_plan']
            
            print("✅ Planning completed successfully!\n")
            print("=" * 70)
            print(f"📦 Project: {plan['project_name']}")
            print("=" * 70)
            print(f"📝 Description: {plan['description']}")
            print(f"\n✨ Features ({len(plan['features'])} total):")
            for i, f in enumerate(plan['features'], 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(f.get('priority', 'medium'), "⚪")
                print(f"   {i}. {priority_emoji} {f['name']} ({f.get('complexity', 'N/A')} complexity)")
            
            print(f"\n📖 User Stories ({len(plan['user_stories'])} total):")
            for i, story in enumerate(plan['user_stories'][:5], 1):
                print(f"   {i}. As a {story['as_a']}, I want {story['i_want']}")
            
            # Save plan
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(exist_ok=True)
            
            plan_file = output_dir / f"{plan['project_name'].replace(' ', '_').lower()}_plan.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Plan saved to: {plan_file}")
            
            # Phase 2: Architecture Design
            print("\n" + "=" * 70)
            print("🏗️  Phase 2: Architecture Design")
            print("=" * 70)
            print("⏳ Designing system architecture (this may take 2-3 minutes)...\n")
            
            architect = ArchitectAgent(ollama, None)
            arch_result = architect.execute({'project_plan': plan})
            
            if arch_result['status'] == 'architecture_completed':
                arch = arch_result['architecture']
                
                print("✅ Architecture design completed!\n")
                print("=" * 70)
                print("🛠️  Tech Stack")
                print("=" * 70)
                print(f"   Backend:  {arch['tech_stack']['backend']['framework']} ({arch['tech_stack']['backend']['language']})")
                print(f"   Frontend: {arch['tech_stack']['frontend']['framework']} ({arch['tech_stack']['frontend']['language']})")
                print(f"   Database: {arch['tech_stack']['database']['primary']}")
                if arch['tech_stack']['database'].get('cache'):
                    print(f"   Cache:    {arch['tech_stack']['database']['cache']}")
                
                print(f"\n🗄️  Database Schema ({len(arch['database_schema']['tables'])} tables):")
                for i, table in enumerate(arch['database_schema']['tables'], 1):
                    print(f"   {i}. {table['name']} ({len(table['columns'])} columns)")
                
                print(f"\n🌐 API Endpoints ({len(arch['api_design']['endpoints'])} total):")
                for i, endpoint in enumerate(arch['api_design']['endpoints'][:5], 1):
                    auth = "🔒" if endpoint.get('authentication_required') else "🔓"
                    print(f"   {i}. {auth} {endpoint['method']:<6} {endpoint['path']}")
                if len(arch['api_design']['endpoints']) > 5:
                    print(f"   ... and {len(arch['api_design']['endpoints']) - 5} more")
                
                print(f"\n📦 Modules ({len(arch['modules'])} total):")
                for i, module in enumerate(arch['modules'], 1):
                    print(f"   {i}. {module['name']} ({module['type']})")
                
                print(f"\n📊 Project Metadata:")
                print(f"   Complexity:      {arch['metadata']['complexity']}")
                print(f"   Estimated Setup: {arch['metadata']['estimated_setup_time']}")
                print(f"   Team Size:       {arch['metadata']['recommended_team_size']} developer(s)")
                
                # Save architecture
                arch_file = output_dir / f"{plan['project_name'].replace(' ', '_').lower()}_architecture.json"
                with open(arch_file, 'w', encoding='utf-8') as f:
                    json.dump(arch, f, indent=2, ensure_ascii=False)
                
                print(f"\n💾 Architecture saved to: {arch_file}")
                
                # Phase 3: Backend Code Generation
                print("\n" + "=" * 70)
                print("💻 Phase 3: Backend Code Generation")
                print("=" * 70)
                print("⏳ Generating backend code (this may take 1-2 minutes)...\n")
                
                backend_agent = BackendAgent(ollama, None)
                backend_result = backend_agent.execute({
                    'project_plan': plan,
                    'architecture': arch
                })
                
                if backend_result['status'] == 'backend_completed':
                    backend_code = backend_result['backend_code']
                    files = backend_code['files']
                    
                    print(f"✅ Generated {len(files)} backend files!\n")
                    
                    # Phase 4: File Building
                    print("=" * 70)
                    print("🏗️  Phase 4: Building Project Structure")
                    print("=" * 70)
                    
                    builder = FileBuilder(output_dir=settings.output_dir)
                    project_dir = builder.create_project_structure(
                        project_name=plan['project_name'],
                        architecture=arch
                    )
                    
                    print(f"✅ Project structure created at: {project_dir}\n")
                    
                    # Write backend files
                    print("📝 Writing backend files...")
                    backend_dir = project_dir / "backend"
                    builder.write_files(files, backend_dir)
                    print(f"✅ Wrote {len(files)} files\n")
                    
                    # Create README
                    print("📄 Creating README...")
                    project_info = {
                        'name': plan['project_name'],
                        'description': plan['description'],
                        'backend': arch['tech_stack']['backend']['framework'],
                        'frontend': arch['tech_stack']['frontend']['framework'],
                        'database': arch['tech_stack']['database']['primary'],
                        'features': [f['name'] for f in plan['features']]
                    }
                    builder.create_readme(project_dir, project_info)
                    print(f"✅ README.md created\n")
                    
                    # Phase 5: Frontend Code Generation
                    print("=" * 70)
                    print("🎨 Phase 5: Frontend Code Generation")
                    print("=" * 70)
                    print("⏳ Generating frontend code (this may take 1-2 minutes)...\n")
                    
                    frontend_agent = FrontendAgent(ollama, None)
                    frontend_result = frontend_agent.execute({
                        'project_plan': plan,
                        'architecture': arch
                    })
                    
                    if frontend_result['status'] == 'frontend_completed':
                        frontend_code = frontend_result['frontend_code']
                        frontend_files = frontend_code['files']
                        
                        print(f"✅ Generated {len(frontend_files)} frontend files!\n")
                        
                        # Write frontend files
                        print("📝 Writing frontend files...")
                        frontend_dir = project_dir / "frontend"
                        builder.write_files(frontend_files, frontend_dir)
                        print(f"✅ Wrote {len(frontend_files)} files\n")
                    
                    # Final Summary
                    print("=" * 70)
                    print("🎉 Project Generation Complete!")
                    print("=" * 70)
                    print(f"\n📦 Project: {plan['project_name']}")
                    print(f"📁 Location: {project_dir}")
                    print(f"📊 Total Files: {len(files) + len(frontend_files)}")
                    print(f"\n✨ What was generated:")
                    print(f"   ✅ Project Plan ({len(plan['features'])} features)")
                    print(f"   ✅ System Architecture ({len(arch['modules'])} modules)")
                    print(f"   ✅ Backend Code ({len(files)} files)")
                    print(f"   ✅ Frontend Code ({len(frontend_files)} files)")
                    print(f"   ✅ Project Structure")
                    print(f"   ✅ README Documentation")
                    
                    print(f"\n🚀 Next Steps:")
                    print(f"\n   Backend:")
                    print(f"   1. cd {project_dir}/backend")
                    print(f"   2. python -m venv venv")
                    print(f"   3. venv\\Scripts\\activate")
                    print(f"   4. pip install -r requirements.txt")
                    print(f"   5. uvicorn app.main:app --reload")
                    
                    print(f"\n   Frontend:")
                    print(f"   1. cd {project_dir}/frontend")
                    print(f"   2. npm install")
                    print(f"   3. npm run dev")
            
            # TODO: Next phases
            print("\n" + "=" * 70)
            print("🔜 Future Phases:")
            print("=" * 70)
            print("   6. 🧪 Testing Agent")
            print("   7. 🐛 Debugging Agent")
            print("   8. ♻️  Refactoring Agent")
            print("   9. 🚀 DevOps & Deployment")
            
            print("\n" + "=" * 70)
            print("✨ Phases 1-5 Complete!")
            print("=" * 70)
        else:
            print("❌ Planning failed")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
