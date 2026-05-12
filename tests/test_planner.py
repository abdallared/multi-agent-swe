"""
اختبار Planner Agent
"""

import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 60)
print("🎯 Testing Planner Agent")
print("=" * 60)

from agents.planner import PlannerAgent
from utils.ollama_interface import ollama

print("\n📋 Initializing Planner Agent...")
planner = PlannerAgent(ollama, None)

context = {
    'user_prompt': 'Build a simple todo app with user authentication and task prioritization'
}

print(f"💡 User Prompt: {context['user_prompt']}")
print("\n⏳ Generating project plan (this may take 1-2 minutes)...\n")

try:
    result = planner.execute(context)
    
    print("=" * 60)
    print(f"✅ Status: {result['status']}")
    print("=" * 60)
    
    plan = result['project_plan']
    
    print(f"\n📦 Project: {plan['project_name']}")
    print(f"📝 Description: {plan['description'][:100]}...")
    print(f"\n✨ Features ({len(plan['features'])} total):")
    for i, f in enumerate(plan['features'][:5], 1):
        print(f"   {i}. {f['name']} ({f.get('priority', 'N/A')} priority, {f.get('complexity', 'N/A')} complexity)")
    
    print(f"\n📖 User Stories ({len(plan['user_stories'])} total):")
    for i, story in enumerate(plan['user_stories'][:3], 1):
        print(f"   {i}. As a {story['as_a']}, I want {story['i_want']}")
    
    # Save to file
    with open('test_plan_output.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full plan saved to: test_plan_output.json")
    print("\n" + "=" * 60)
    print("✨ Planner Agent Test Complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
