"""
اختبار الإعداد الأساسي
"""

print("=" * 60)
print("🔍 Testing Setup...")
print("=" * 60)

# Test 1: Configuration
print("\n1️⃣ Testing Configuration...")
try:
    from core.config import settings
    print(f"   ✅ LLM Provider: {settings.llm_provider}")
    print(f"   ✅ Ollama URL: {settings.ollama_base_url}")
    print(f"   ✅ Planner Model: {settings.planner_model}")
    print(f"   ✅ Output Dir: {settings.output_dir}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Ollama Connection
print("\n2️⃣ Testing Ollama Connection...")
try:
    from utils.ollama_interface import ollama
    models = ollama.list_models()
    print(f"   ✅ Connected! Found {len(models)} models:")
    for m in models[:5]:
        size_gb = m['size'] / 1e9
        print(f"      - {m['name']:<30} {size_gb:>6.1f} GB")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Simple Generation
print("\n3️⃣ Testing Simple Generation...")
try:
    from utils.ollama_interface import ollama
    response = ollama.generate(
        prompt="Say 'Hello from AI Software Company!' in one short sentence.",
        agent_type="planner",
        max_tokens=50
    )
    print(f"   ✅ Response: {response[:100]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✨ Setup Test Complete!")
print("=" * 60)
