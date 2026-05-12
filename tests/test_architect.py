"""
اختبار Architect Agent
"""

import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 70)
print("🏗️  Testing Architect Agent")
print("=" * 70)

from agents.architect import ArchitectAgent
from utils.ollama_interface import ollama

# Load the plan from previous test
print("\n📋 Loading project plan...")
with open('test_plan_output.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

print(f"✅ Loaded plan for: {plan['project_name']}")

print("\n🏗️  Initializing Architect Agent...")
architect = ArchitectAgent(ollama, None)

context = {
    'project_plan': plan
}

print(f"\n⏳ Designing architecture (this may take 2-3 minutes)...\n")

try:
    result = architect.execute(context)
    
    print("=" * 70)
    print(f"✅ Status: {result['status']}")
    print("=" * 70)
    
    arch = result['architecture']
    
    # Tech Stack
    print(f"\n🛠️  Tech Stack:")
    print(f"   Backend: {arch['tech_stack']['backend']['framework']} ({arch['tech_stack']['backend']['language']})")
    print(f"   Frontend: {arch['tech_stack']['frontend']['framework']} ({arch['tech_stack']['frontend']['language']})")
    print(f"   Database: {arch['tech_stack']['database']['primary']}")
    if arch['tech_stack']['database'].get('cache'):
        print(f"   Cache: {arch['tech_stack']['database']['cache']}")
    
    # Database Schema
    print(f"\n🗄️  Database Schema ({len(arch['database_schema']['tables'])} tables):")
    for i, table in enumerate(arch['database_schema']['tables'][:5], 1):
        print(f"   {i}. {table['name']} ({len(table['columns'])} columns)")
    
    # API Endpoints
    print(f"\n🌐 API Endpoints ({len(arch['api_design']['endpoints'])} total):")
    for i, endpoint in enumerate(arch['api_design']['endpoints'][:5], 1):
        auth = "🔒" if endpoint.get('authentication_required') else "🔓"
        print(f"   {i}. {auth} {endpoint['method']:<6} {endpoint['path']}")
    
    # Modules
    print(f"\n📦 Modules ({len(arch['modules'])} total):")
    for i, module in enumerate(arch['modules'], 1):
        print(f"   {i}. {module['name']} ({module['type']})")
    
    # Metadata
    print(f"\n📊 Metadata:")
    print(f"   Complexity: {arch['metadata']['complexity']}")
    print(f"   Estimated Setup: {arch['metadata']['estimated_setup_time']}")
    print(f"   Team Size: {arch['metadata']['recommended_team_size']} developer(s)")
    
    # Save to file
    with open('test_architecture_output.json', 'w', encoding='utf-8') as f:
        json.dump(arch, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full architecture saved to: test_architecture_output.json")
    print("\n" + "=" * 70)
    print("✨ Architect Agent Test Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
