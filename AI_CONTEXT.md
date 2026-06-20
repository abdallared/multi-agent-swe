# AI Context: Multi-Agent Software Factory

**Purpose**: An autonomous multi-agent system that transforms a single natural language prompt into a complete, runnable full-stack web application. It runs entirely locally using Ollama LLMs, requiring zero cloud API keys.
**Tech Stack**:
- **System**: Python 3.11+, CrewAI, LangGraph, ChromaDB, FastAPI, WebSockets.
- **Generated Code**: FastAPI (Backend), SQLAlchemy (Database), React + Vite + TypeScript + Tailwind (Frontend), Pytest (Testing), Docker (Deployment).

## 1. System Architecture & Execution Modes

The system supports multiple execution orchestrators:

- **Pipeline Mode (Default - `core/pipeline.py`)**: 
  - A highly optimized, custom async pipeline.
  - **Sequential Phase**: Planner creates the project spec -> Architect creates the technical design.
  - **Parallel Phase 1**: Backend and Frontend agents generate code simultaneously via `asyncio.gather`.
  - **Review Loop**: The ReviewAgent performs static validation and semantic LLM review. If critical issues are found, it triggers a self-correction loop (max 2 iterations) to re-generate broken files.
  - **Parallel Phase 2**: Testing and Docker agents generate their respective files.
  - **Build**: `FileBuilder` writes everything to `./output/<project_name>/`.
  
- **CrewAI Mode (`core/crew_pipeline.py`)**:
  - Leverages the CrewAI framework for sequential agent delegation.
  - Grants agents access to tools like `search_internet` (DuckDuckGo) and `read_file`.
  
- **LangGraph Mode (Alternative)**:
  - Supports advanced node-based graph execution for stateful, highly cyclical agent workflows.

## 2. Core Agents (`agents/`)

Every agent inherits from `BaseAgent`, which provides memory injection, dynamic token budgeting, and standard LLM calling interfaces.

- **`PlannerAgent` (`qwen3.5:latest`)**: 
  - *Input*: User prompt.
  - *Output*: JSON containing project features, priorities, and user stories.
- **`ArchitectAgent` (`gemma4:latest`)**: 
  - *Input*: Planner JSON.
  - *Output*: JSON containing the chosen tech stack, complete database schema (tables & columns), and REST API design (endpoints & methods).
- **`BackendAgent` (`qwen2.5-coder:7b`)**: 
  - *Input*: Architecture JSON.
  - *Output*: Complete FastAPI backend (`main.py`, routers, SQLAlchemy models, Pydantic schemas, JWT auth logic). *Features a robust 17-file fallback generation if LLM fails.*
- **`FrontendAgent` (`qwen2.5-coder:7b`)**: 
  - *Input*: Architecture JSON.
  - *Output*: Complete React SPA (components, Vite config, Tailwind styles, API service layer). *Also features a 17-file fallback generation.*
- **`ReviewAgent` (`qwen2.5-coder:7b`)**: 
  - Validates generated code. Uses `CodeValidator` for static checks (Python AST parsing, import checks, SQLAlchemy `__tablename__` checks, placeholder detection) before invoking the LLM for semantic review.
- **`TestingAgent` & `DockerAgent`**: Generates `pytest` suites and containerization files (`docker-compose.yml`, Dockerfiles, Nginx configs).

## 3. Core Infrastructure Modules

- **`utils/ollama_interface.py`**: A robust, singleton wrapper around the Ollama HTTP API. Supports async execution (`agenerate`), exponential backoff retries via `tenacity`, and transparent response caching via `utils/cache.py` (keyed by prompt hash).
- **`utils/token_manager.py`**: Dynamically adjusts `max_tokens` and `temperature`. For example, `Planner` gets high temperature (0.7) for creativity; `Architect` gets low temperature (0.1) for strict JSON; `Frontend` gets massive token budgets (8000+).
- **`memory/project_memory.py` & `vector_store.py`**: 
  - A dual-backend vector store. Uses ChromaDB if available; falls back to a custom JSON pure-Python cosine similarity search if not.
  - **Learning Loop**: After pipeline completion, if the project quality score is >= 40, a condensed representation (summary + file samples) is embedded and stored. Future runs query this database and inject similar past projects into the agent's system prompt as few-shot examples.

## 4. User Interfaces

- **CLI (`main.py` / `crew_main.py`)**: Terminal execution providing live console updates.
- **Web UI (`ui/`)**: 
  - Backend: A FastAPI server (`ui/backend/app.py`) exposing a WebSocket endpoint (`/ws/generate`).
  - Frontend: A React application (`ui/frontend/src/App.tsx`) that streams real-time execution logs, agent phase transitions, and provides a final `.zip` download of the generated workspace.
