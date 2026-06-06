"""Quick smoke test for the memory system."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import shutil
from memory.vector_store import VectorStore, _cosine_similarity

# Test cosine similarity
sim = _cosine_similarity([1, 0, 0], [1, 0, 0])
assert abs(sim - 1.0) < 0.001, f"Expected 1.0, got {sim}"
sim = _cosine_similarity([1, 0, 0], [0, 1, 0])
assert abs(sim - 0.0) < 0.001, f"Expected 0.0, got {sim}"
print("✅ Cosine similarity works")

# Test VectorStore (JSON fallback)
test_dir = "./memory/test_db"
vs = VectorStore(persist_dir=test_dir)
print(f"✅ Backend: {vs.backend}")

fake_emb1 = [0.1] * 10
fake_emb2 = [0.2] * 10
fake_emb3 = [0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

vs.add("p1", "task manager app with auth", embedding=fake_emb1, metadata={"quality": 80})
vs.add("p2", "e-commerce shop with payments", embedding=fake_emb2, metadata={"quality": 90})
vs.add("p3", "blog with comments", embedding=fake_emb3, metadata={"quality": 70})
print(f"✅ Count after add: {vs.count()}")
assert vs.count() == 3

results = vs.query(embedding=fake_emb1, top_k=2)
print(f"✅ Query results: {len(results)} found")
assert len(results) == 2
# p1 should be most similar to itself (same direction vector)
print(f"   Top match: id={results[0]['id']}, sim={results[0]['similarity']:.3f}")

vs.delete("p1")
assert vs.count() == 2
print("✅ Delete works")

vs.clear()
assert vs.count() == 0
print("✅ Clear works")

# Cleanup
shutil.rmtree(test_dir, ignore_errors=True)

# Test ProjectMemory (without real embeddings)
from memory.project_memory import ProjectMemory

pm = ProjectMemory(persist_dir=test_dir)
stats = pm.get_stats()
print(f"✅ ProjectMemory stats: {stats}")
assert stats["total_projects"] == 0

# Test save_project (will skip because embeddings model may not be available)
plan = {"project_name": "Test App", "description": "A test app", "features": [{"name": "auth"}, {"name": "dashboard"}]}
arch = {"tech_stack": {"backend": {"framework": "FastAPI"}, "frontend": {"framework": "React"}, "database": {"primary": "PostgreSQL"}}, "api_design": {"endpoints": []}, "database_schema": {"tables": []}, "metadata": {"complexity": "medium"}}

# This may not save if Ollama embeddings are unavailable, but it should not crash
saved = pm.save_project(plan, arch, quality_score=80)
print(f"✅ save_project returned: {saved} (OK if False when embeddings unavailable)")

# Test find_similar (should return empty if nothing saved)
similar = pm.find_similar("task manager app")
print(f"✅ find_similar returned: {len(similar)} results")

# Test get_few_shot_examples
examples = pm.get_few_shot_examples("task manager app", "backend")
print(f"✅ get_few_shot_examples returned: {'text' if examples else 'None'}")

# Test quality score calculator
from core.pipeline import Pipeline
score = Pipeline._calculate_quality_score(review_passed=True, total_files=15, had_errors=False)
assert score == 85, f"Expected 85, got {score}"
score = Pipeline._calculate_quality_score(review_passed=False, total_files=5, had_errors=True)
assert score == 5, f"Expected 5, got {score}"
print(f"✅ Quality score calculator works")

# Cleanup
shutil.rmtree(test_dir, ignore_errors=True)

print("\n🎉 All memory system tests passed!")
