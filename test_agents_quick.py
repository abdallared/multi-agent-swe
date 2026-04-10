"""
Quick Agent Test - no Ollama needed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

plan = {
    'project_name': 'Test Todo App',
    'description': 'A test app',
    'features': [{'name': 'Task Management'}, {'name': 'User Auth'}]
}
arch = {
    'tech_stack': {
        'backend': {'framework': 'FastAPI', 'orm': 'SQLAlchemy'},
        'frontend': {'framework': 'React', 'language': 'TypeScript'},
        'database': {'primary': 'SQLite'}
    },
    'database_schema': {
        'tables': [
            {'name': 'users', 'columns': [{'name': 'id'}, {'name': 'email'}]},
            {'name': 'tasks', 'columns': [{'name': 'id'}, {'name': 'title'}]}
        ]
    },
    'api_design': {
        'endpoints': [{'method': 'GET', 'path': '/tasks', 'description': 'Get all tasks'}]
    }
}

errors = []

# Test 1: Imports
print("TEST 1: Imports")
try:
    from agents.backend import BackendAgent
    from agents.frontend import FrontendAgent
    from agents.testing import TestingAgent
    from agents.docker import DockerAgent
    from builder.file_builder import FileBuilder
    print("  PASS - All imports OK")
except Exception as e:
    print(f"  FAIL - {e}")
    errors.append(str(e))

# Test 2: Backend fallback
print("TEST 2: Backend Agent (fallback)")
try:
    b = BackendAgent(None, None)
    result = b._generate_fallback_backend(arch, plan)
    files = result['backend_code']['files']
    assert len(files) >= 10, f"Expected 10+ files, got {len(files)}"
    assert 'app/main.py' in files
    assert 'app/core/database.py' in files
    assert 'app/models/user.py' in files
    assert 'app/api/auth.py' in files
    assert 'requirements.txt' in files
    print(f"  PASS - {len(files)} files generated")
    for f in sorted(files.keys()):
        print(f"    - {f}")
except Exception as e:
    print(f"  FAIL - {e}")
    errors.append(str(e))

# Test 3: Frontend fallback
print("TEST 3: Frontend Agent (fallback)")
try:
    fe = FrontendAgent(None, None)
    result = fe._generate_fallback_frontend(arch, plan)
    files = result['frontend_code']['files']
    assert len(files) >= 10, f"Expected 10+ files, got {len(files)}"
    assert 'src/App.tsx' in files
    assert 'src/pages/Login.tsx' in files
    assert 'src/pages/Dashboard.tsx' in files
    assert 'src/services/api.ts' in files
    assert 'package.json' in files
    print(f"  PASS - {len(files)} files generated")
    for f in sorted(files.keys()):
        print(f"    - {f}")
except Exception as e:
    print(f"  FAIL - {e}")
    errors.append(str(e))

# Test 4: Testing Agent fallback
print("TEST 4: Testing Agent (fallback)")
try:
    t = TestingAgent(None, None)
    tests = t._get_fallback_tests(plan)
    assert len(tests) >= 3
    assert 'tests/conftest.py' in tests
    assert 'tests/test_main.py' in tests
    assert 'tests/test_api.py' in tests
    print(f"  PASS - {len(tests)} test files generated")
    for f in tests:
        print(f"    - {f}")
except Exception as e:
    print(f"  FAIL - {e}")
    errors.append(str(e))

# Test 5: Docker Agent
print("TEST 5: Docker Agent")
try:
    d = DockerAgent(None, None)
    result = d.execute({'project_plan': plan, 'architecture': arch})
    files = result['docker_files']
    assert 'docker-compose.yml' in files
    assert 'docker/Dockerfile.backend' in files
    assert 'docker/Dockerfile.frontend' in files
    print(f"  PASS - {len(files)} docker files generated")
    for f in files:
        print(f"    - {f}")
except Exception as e:
    print(f"  FAIL - {e}")
    errors.append(str(e))

# Test 6: File Builder - write everything
print("TEST 6: File Builder")
try:
    from builder.file_builder import FileBuilder
    from pathlib import Path

    b_agent = BackendAgent(None, None)
    fe_agent = FrontendAgent(None, None)
    t_agent = TestingAgent(None, None)
    d_agent = DockerAgent(None, None)

    backend = b_agent._generate_fallback_backend(arch, plan)
    frontend = fe_agent._generate_fallback_frontend(arch, plan)
    tests = t_agent._get_fallback_tests(plan)
    docker = d_agent.execute({'project_plan': plan, 'architecture': arch})

    builder = FileBuilder('./output')
    project_dir = builder.create_project_structure('test_complete_project', arch)
    builder.write_files(backend['backend_code']['files'], project_dir / 'backend')
    builder.write_files(frontend['frontend_code']['files'], project_dir / 'frontend')
    builder.write_files(tests, project_dir / 'backend')
    builder.write_files(docker['docker_files'], project_dir)
    builder.create_readme(project_dir, {
        'name': plan['project_name'],
        'description': plan['description'],
        'backend': 'FastAPI',
        'frontend': 'React + TypeScript',
        'database': 'SQLite',
        'features': ['Task Management', 'User Auth'],
        'test_command': 'pytest tests/ -v --cov=app'
    })

    total = sum(1 for f in project_dir.rglob('*') if f.is_file())
    print(f"  PASS - {total} total files written to {project_dir}")
except Exception as e:
    import traceback
    print(f"  FAIL - {e}")
    traceback.print_exc()
    errors.append(str(e))

# Summary
print("\n" + "="*50)
if not errors:
    print("ALL 6 TESTS PASSED!")
else:
    print(f"FAILED: {len(errors)} error(s)")
    for e in errors:
        print(f"  - {e}")
print("="*50)
