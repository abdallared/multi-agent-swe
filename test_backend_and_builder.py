"""
اختبار Backend Agent + File Builder
"""

import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 70)
print("💻 Testing Backend Agent + File Builder")
print("=" * 70)

from agents.backend import BackendAgent
from builder.file_builder import FileBuilder
from utils.ollama_interface import ollama

# Load plan and architecture
print("\n📋 Loading project data...")
with open('test_plan_output.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

with open('test_architecture_output.json', 'r', encoding='utf-8') as f:
    architecture = json.load(f)

print(f"✅ Loaded: {plan['project_name']}")

# Test Backend Agent
print("\n💻 Initializing Backend Agent...")
backend_agent = BackendAgent(ollama, None)

context = {
    'project_plan': plan,
    'architecture': architecture
}

print(f"\n⏳ Generating backend code (this may take 2-3 minutes)...\n")

try:
    result = backend_agent.execute(context)
    
    print("=" * 70)
    print(f"✅ Status: {result['status']}")
    print("=" * 70)
    
    backend_code = result['backend_code']
    files = backend_code['files']
    
    print(f"\n📁 Generated Files ({len(files)} total):")
    for i, filepath in enumerate(files.keys(), 1):
        print(f"   {i}. {filepath}")
    
    # Test File Builder
    print("\n🏗️  Testing File Builder...")
    builder = FileBuilder(output_dir="./output")
    
    project_dir = builder.create_project_structure(
        project_name=plan['project_name'],
        architecture=architecture
    )
    
    print(f"✅ Project structure created at: {project_dir}")
    
    # Write backend files
    print("\n📝 Writing backend files...")
    backend_dir = project_dir / "backend"
    builder.write_files(files, backend_dir)
    
    print(f"✅ Wrote {len(files)} files to {backend_dir}")
    
    # Create README
    print("\n📄 Creating README...")
    project_info = {
        'name': plan['project_name'],
        'description': plan['description'],
        'backend': architecture['tech_stack']['backend']['framework'],
        'frontend': architecture['tech_stack']['frontend']['framework'],
        'database': architecture['tech_stack']['database']['primary'],
        'features': [f['name'] for f in plan['features']]
    }
    builder.create_readme(project_dir, project_info)
    
    print(f"✅ README.md created")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"   Project: {plan['project_name']}")
    print(f"   Location: {project_dir}")
    print(f"   Backend Files: {len(files)}")
    print(f"   Structure: ✅ Created")
    print(f"   README: ✅ Created")
    
    print("\n" + "=" * 70)
    print("✨ Backend Agent + File Builder Test Complete!")
    print("=" * 70)
    
    print(f"\n💡 Next: cd {project_dir} && explore the generated code!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
