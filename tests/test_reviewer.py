"""
Phase 5 Verification Script — Review Agent + Self-Correction Loop
"""
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_reviewer_import():
    from agents.reviewer import ReviewAgent
    print('1. ReviewAgent class loaded OK')

def test_pipeline_import():
    from core.pipeline import Pipeline, MAX_REVIEW_ITERATIONS
    assert MAX_REVIEW_ITERATIONS == 2, f"Expected 2, got {MAX_REVIEW_ITERATIONS}"
    print(f'2. Pipeline imports ReviewAgent OK (max_iterations={MAX_REVIEW_ITERATIONS})')

def test_config():
    from core.config import settings
    assert hasattr(settings, 'reviewer_model'), 'reviewer_model missing from config'
    print(f'3. Config reviewer_model={settings.reviewer_model} OK')

def test_ollama_mapping():
    from utils.ollama_interface import ollama
    assert 'reviewer' in ollama.agent_models, 'reviewer missing from ollama agent_models'
    model = ollama.agent_models['reviewer']
    print(f'4. Ollama reviewer model={model} OK')

def test_token_manager():
    from utils.token_manager import token_manager
    budget = token_manager.get_budget('reviewer', 'medium')
    temp = token_manager.get_temperature('reviewer')
    assert budget > 0, 'reviewer budget is 0'
    assert 0 <= temp <= 1, 'reviewer temp out of range'
    print(f'5. TokenManager reviewer: budget={budget}, temp={temp} OK')

def test_reviewer_methods():
    from agents.reviewer import ReviewAgent
    r = ReviewAgent.__new__(ReviewAgent)
    assert hasattr(r, 'execute'), 'execute method missing'
    assert hasattr(r, 'get_system_prompt'), 'get_system_prompt missing'
    assert hasattr(r, '_semantic_review'), '_semantic_review missing'
    assert hasattr(r, '_merge_issues'), '_merge_issues missing'
    assert hasattr(r, '_report_to_issues'), '_report_to_issues missing'
    print('6. ReviewAgent methods verified OK')

def test_pipeline_methods():
    from core.pipeline import Pipeline
    p = Pipeline.__new__(Pipeline)
    assert hasattr(p, '_fix_code'), '_fix_code method missing from Pipeline'
    assert hasattr(p, '_parse_fix_response'), '_parse_fix_response method missing'
    print('7. Pipeline self-correction methods OK')

def test_agents_init():
    from agents import ReviewAgent
    print('8. agents __init__ exports ReviewAgent OK')

def test_parse_fix_response():
    from core.pipeline import Pipeline
    p = Pipeline.__new__(Pipeline)
    
    # Test valid JSON
    result = p._parse_fix_response('{"files": {"test.py": "print(1)"}}')
    assert result == {"files": {"test.py": "print(1)"}}, f"Unexpected: {result}"
    
    # Test markdown-wrapped JSON
    result = p._parse_fix_response('```json\n{"files": {"a.py": "x=1"}}\n```')
    assert "files" in result
    
    # Test broken JSON
    result = p._parse_fix_response('not json at all')
    assert result == {}
    
    print('9. Pipeline _parse_fix_response works OK')


if __name__ == '__main__':
    tests = [
        test_reviewer_import,
        test_pipeline_import,
        test_config,
        test_ollama_mapping,
        test_token_manager,
        test_reviewer_methods,
        test_pipeline_methods,
        test_agents_init,
        test_parse_fix_response,
    ]
    
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f'FAILED: {test.__name__}: {e}')
            failed += 1
    
    print(f'\nResults: {passed} passed, {failed} failed')
    if failed > 0:
        sys.exit(1)
    print('All Phase 5 checks passed!')
