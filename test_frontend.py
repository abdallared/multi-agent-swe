"""
Test Frontend Agent
"""

from agents.frontend import FrontendAgent
from utils.ollama_interface import ollama
import json

print("=" * 70)
print("🎨 Testing Frontend Agent")
print("=" * 70)
print()

# Sample architecture and plan
architecture = {
    'tech_stack': {
        'frontend': {
            'framework': 'React',
            'language': 'TypeScript'
        }
    }
}

plan = {
    'project_name': 'Simple Todo App',
    'description': 'A simple todo application',
    'features': [
        {'name': 'User Authentication', 'description': 'Login and registration'},
        {'name': 'Task Management', 'description': 'Create, edit, delete tasks'},
        {'name': 'Task Filtering', 'description': 'Filter by status'}
    ]
}

# Initialize agent
frontend_agent = FrontendAgent(ollama, None)

# Execute
print("⏳ Generating frontend code...")
print("   (This may take 1-2 minutes)\n")

try:
    result = frontend_agent.execute({
        'project_plan': plan,
        'architecture': architecture
    })
    
    print("=" * 70)
    print("✅ Frontend Generation Complete!")
    print("=" * 70)
    print()
    
    frontend_code = result['frontend_code']
    files = frontend_code['files']
    
    print(f"📊 Generated {len(files)} files:\n")
    
    for filepath in files.keys():
        print(f"   ✅ {filepath}")
    
    print()
    
    # Save to file
    output_file = "test_frontend_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(frontend_code, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Output saved to: {output_file}")
    
    # Show sample file
    print("\n" + "=" * 70)
    print("📄 Sample File: src/App.tsx")
    print("=" * 70)
    print()
    print(files.get('src/App.tsx', 'Not found')[:500])
    print()
    
    print("=" * 70)
    print("✨ Test Completed Successfully!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
