import ast, sys

print("=== SYNTAX CHECK ===")
files = [
    "main.py",
    "agents/base_agent.py", "agents/planner.py", "agents/architect.py",
    "agents/backend.py", "agents/frontend.py", "agents/testing.py", "agents/docker.py",
    "utils/ollama_interface.py", "builder/file_builder.py", "core/config.py",
    "ui/backend/app.py",
]
all_ok = True
for f in files:
    try:
        src = open(f, encoding="utf-8").read()
        ast.parse(src)
        print("  OK  " + f)
    except SyntaxError as e:
        print("  ERR " + f + ": " + str(e))
        all_ok = False
    except FileNotFoundError:
        print("  MISS " + f)
        all_ok = False

print()
print("=== IMPORT CHECK ===")
sys.path.insert(0, ".")
try:
    from core.config import settings
    print("  OK  core.config - planner=" + settings.planner_model)
except Exception as e:
    print("  ERR core.config: " + str(e))

try:
    from utils.ollama_interface import OllamaInterface
    oi = OllamaInterface()
    keys = list(oi.agent_models.keys())
    print("  OK  OllamaInterface - model keys: " + str(keys))
    for k in ["planner", "architect", "backend", "frontend", "testing", "docker", "debugger"]:
        m = oi.agent_models.get(k, "MISSING")
        print("      " + k + " -> " + m)
except Exception as e:
    print("  ERR OllamaInterface: " + str(e))

try:
    from agents.planner import PlannerAgent
    from agents.architect import ArchitectAgent
    from agents.backend import BackendAgent
    from agents.frontend import FrontendAgent
    from agents.testing import TestingAgent
    from agents.docker import DockerAgent
    print("  OK  All 6 agents imported")
except Exception as e:
    print("  ERR agents: " + str(e))

try:
    from builder.file_builder import FileBuilder
    print("  OK  FileBuilder imported")
except Exception as e:
    print("  ERR FileBuilder: " + str(e))

print()
print("=== PIPELINE FLOW CHECK ===")
print("Agent class_name -> derived key -> assigned model:")
agents_check = [
    ("PlannerAgent", "planner"),
    ("ArchitectAgent", "architect"),
    ("BackendAgent", "backend"),
    ("FrontendAgent", "frontend"),
    ("TestingAgent", "testing"),
    ("DockerAgent", "docker"),
]
from utils.ollama_interface import OllamaInterface
oi2 = OllamaInterface()
for class_name, expected_key in agents_check:
    derived = class_name.lower().replace("agent", "")
    model = oi2.agent_models.get(derived, "MISSING!")
    status = "OK " if "MISSING" not in model else "ERR"
    print("  " + status + " " + class_name + " -> " + derived + " -> " + model)

print()
print("=== REQUIREMENTS CHECK ===")
import importlib
pkgs = ["fastapi", "uvicorn", "requests", "pydantic", "sqlalchemy", "passlib", "jose"]
for pkg in pkgs:
    try:
        importlib.import_module(pkg)
        print("  OK  " + pkg)
    except ImportError:
        print("  MISS " + pkg + " (not installed)")

print()
if all_ok:
    print("ALL SYNTAX CHECKS PASSED")
