"""
Full System Test - اختبار النظام الكامل
"""
import sys
import os
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports work"""
    print("\n📦 Testing imports...")
    try:
        from core.config import settings
        from utils.ollama_interface import ollama
        from agents.planner import PlannerAgent
        from agents.architect import ArchitectAgent
        from agents.backend import BackendAgent
        from agents.frontend import FrontendAgent
        from agents.testing import TestingAgent
        from agents.docker import DockerAgent
        from builder.file_builder import FileBuilder
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_ollama_connection():
    """Test Ollama is running"""
    print("\n🔌 Testing Ollama connection...")
    try:
        from utils.ollama_interface import ollama
        models = ollama.list_models()
        print(f"  ✅ Ollama connected - {len(models)} models available")
        for m in models[:3]:
            print(f"     - {m}")
        return True
    except Exception as e:
        print(f"  ❌ Ollama error: {e}")
        return False

def test_planner():
    """Test Planner Agent"""
    print("\n📋 Testing Planner Agent...")
    try:
        from utils.ollama_interface import ollama
        from agents.planner import PlannerAgent
        
        planner = PlannerAgent(ollama, None)
        result = planner.execute({'user_prompt': 'Build a simple todo app'})
        plan = result['project_plan']
        
        assert 'project_name' in plan, "Missing project_name"
        assert 'features' in plan, "Missing features"
        assert len(plan['features']) > 0, "No features"
        
        print(f"  ✅ Planner OK - Project: {plan['project_name']}")
        print(f"     Features: {len(plan['features'])}")
        return plan
    except Exception as e:
        print(f"  ❌ Planner error: {e}")
        traceback.print_exc()
        return None

def test_architect(plan):
    """Test Architect Agent"""
    print("\n🏗️ Testing Architect Agent...")
    try:
        from utils.ollama_interface import ollama
        from agents.architect import ArchitectAgent
        
        architect = ArchitectAgent(ollama, None)
        result = architect.execute({'project_plan': plan})
        arch = result['architecture']
        
        assert 'tech_stack' in arch, "Missing tech_stack"
        assert 'database_schema' in arch, "Missing database_schema"
        assert 'api_design' in arch, "Missing api_design"
        
        print(f"  ✅ Architect OK")
        print(f"     Backend: {arch['tech_stack']['backend']['framework']}")
        print(f"     Tables: {len(arch['database_schema']['tables'])}")
        print(f"     Endpoints: {len(arch['api_design']['endpoints'])}")
        return arch
    except Exception as e:
        print(f"  ❌ Architect error: {e}")
        traceback.print_exc()
        return None

def test_backend(plan, arch):
    """Test Backend Agent"""
    print("\n⚙️ Testing Backend Agent...")
    try:
        from utils.ollama_interface import ollama
        from agents.backend import BackendAgent
        
        agent = BackendAgent(ollama, None)
        result = agent.execute({'project_plan': plan, 'architecture': arch})
        backend_code = result['backend_code']
        
        assert 'files' in backend_code, "Missing files"
        files = backend_code['files']
        
        # Check essential files
        essential = ['app/main.py', 'requirements.txt']
        for f in essential:
            if f in files:
                print(f"     ✓ {f} ({len(files[f])} chars)")
            else:
                print(f"     ⚠ Missing: {f}")
        
        print(f"  ✅ Backend OK - {len(files)} files generated")
        return backend_code
    except Exception as e:
        print(f"  ❌ Backend error: {e}")
        traceback.print_exc()
        return None

def test_frontend(plan, arch):
    """Test Frontend Agent"""
    print("\n🎨 Testing Frontend Agent...")
    try:
        from utils.ollama_interface import ollama
        from agents.frontend import FrontendAgent
        
        agent = FrontendAgent(ollama, None)
        result = agent.execute({'project_plan': plan, 'architecture': arch})
        frontend_code = result['frontend_code']
        
        assert 'files' in frontend_code, "Missing files"
        files = frontend_code['files']
        
        essential = ['src/App.tsx', 'package.json']
        for f in essential:
            if f in files:
                print(f"     ✓ {f} ({len(files[f])} chars)")
            else:
                print(f"     ⚠ Missing: {f}")
        
        print(f"  ✅ Frontend OK - {len(files)} files generated")
        return frontend_code
    except Exception as e:
        print(f"  ❌ Frontend error: {e}")
        traceback.print_exc()
        return None

def test_testing_agent(plan, arch, backend_code):
    """Test Testing Agent"""
    print("\n🧪 Testing Testing Agent...")
    try:
        from utils.ollama_interface import ollama
        from agents.testing import TestingAgent
        
        agent = TestingAgent(ollama, None)
        result = agent.execute({
            'project_plan': plan,
            'architecture': arch,
            'backend_code': backend_code
        })
        
        tests = result['backend_tests']
        assert len(tests) > 0, "No test files generated"
        
        for f in tests:
            print(f"     ✓ {f} ({len(tests[f])} chars)")
        
        print(f"  ✅ Testing Agent OK - {len(tests)} test files")
        return tests
    except Exception as e:
        print(f"  ❌ Testing Agent error: {e}")
        traceback.print_exc()
        return None

def test_docker_agent(plan, arch):
    """Test Docker Agent"""
    print("\n🐳 Testing Docker Agent...")
    try:
        from utils.ollama_interface import ollama
        from agents.docker import DockerAgent
        
        agent = DockerAgent(ollama, None)
        result = agent.execute({'project_plan': plan, 'architecture': arch})
        
        docker_files = result['docker_files']
        assert 'docker-compose.yml' in docker_files, "Missing docker-compose.yml"
        
        for f in docker_files:
            print(f"     ✓ {f}")
        
        print(f"  ✅ Docker Agent OK - {len(docker_files)} files")
        return docker_files
    except Exception as e:
        print(f"  ❌ Docker Agent error: {e}")
        traceback.print_exc()
        return None

def test_file_builder(plan, arch, backend_code, frontend_code, tests, docker_files):
    """Test File Builder - write all files"""
    print("\n📁 Testing File Builder...")
    try:
        from builder.file_builder import FileBuilder
        
        builder = FileBuilder(output_dir="./output")
        project_dir = builder.create_project_structure(
            project_name=plan['project_name'],
            architecture=arch
        )
        
        # Write backend
        backend_dir = project_dir / "backend"
        builder.write_files(backend_code['files'], backend_dir)
        
        # Write frontend
        frontend_dir = project_dir / "frontend"
        builder.write_files(frontend_code['files'], frontend_dir)
        
        # Write tests
        builder.write_files(tests, backend_dir)
        
        # Write docker
        builder.write_files(docker_files, project_dir)
        
        # Write README
        builder.create_readme(project_dir, {
            'name': plan['project_name'],
            'description': plan.get('description', ''),
            'backend': arch['tech_stack']['backend']['framework'],
            'frontend': arch['tech_stack']['frontend']['framework'],
            'database': arch['tech_stack']['database']['primary'],
            'features': [f['name'] for f in plan['features']],
            'test_command': 'pytest tests/ -v'
        })
        
        # Count files
        all_files = list(project_dir.rglob('*'))
        file_count = sum(1 for f in all_files if f.is_file())
        
        print(f"  ✅ File Builder OK")
        print(f"     Project: {project_dir}")
        print(f"     Total files: {file_count}")
        return True
    except Exception as e:
        print(f"  ❌ File Builder error: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    print("=" * 60)
    print("🚀 AI Software Company - Full System Test")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    if not results['imports']:
        print("\n❌ Cannot continue - import errors")
        return
    
    # Test 2: Ollama
    results['ollama'] = test_ollama_connection()
    if not results['ollama']:
        print("\n❌ Cannot continue - Ollama not running")
        print("   Run: ollama serve")
        return
    
    # Test 3: Planner
    plan = test_planner()
    results['planner'] = plan is not None
    if not plan:
        print("\n❌ Cannot continue - Planner failed")
        return
    
    # Test 4: Architect
    arch = test_architect(plan)
    results['architect'] = arch is not None
    if not arch:
        print("\n❌ Cannot continue - Architect failed")
        return
    
    # Test 5: Backend
    backend_code = test_backend(plan, arch)
    results['backend'] = backend_code is not None
    
    # Test 6: Frontend
    frontend_code = test_frontend(plan, arch)
    results['frontend'] = frontend_code is not None
    
    # Test 7: Testing Agent
    tests = test_testing_agent(plan, arch, backend_code or {'files': {}})
    results['testing'] = tests is not None
    
    # Test 8: Docker Agent
    docker_files = test_docker_agent(plan, arch)
    results['docker'] = docker_files is not None
    
    # Test 9: File Builder
    if backend_code and frontend_code and tests and docker_files:
        results['builder'] = test_file_builder(plan, arch, backend_code, frontend_code, tests, docker_files)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
