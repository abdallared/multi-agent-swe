"""
Project Memory — High-level interface for learning from past projects.

Stores successful project generations and retrieves similar past projects
to enrich agent prompts with few-shot examples, improving quality over time.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from memory.vector_store import VectorStore, OllamaEmbedder

logger = logging.getLogger(__name__)


class ProjectMemory:
    """
    Long-term project memory that learns from successful generations.

    Usage:
        memory = ProjectMemory(persist_dir="./memory/db")

        # After a successful generation
        memory.save_project(plan, architecture, backend_code, frontend_code, quality_score=85)

        # Before a new generation — get few-shot examples
        examples = memory.get_few_shot_examples("Build a task manager app", agent_type="backend")
    """

    # ── The minimum quality score required to save a project ───
    MIN_QUALITY_TO_SAVE = 40

    def __init__(
        self,
        persist_dir: str = "./memory/db",
        ollama_base_url: str = "http://localhost:11434",
        embeddings_model: str = "bge-m3:latest",
    ):
        self.embedder = OllamaEmbedder(
            base_url=ollama_base_url,
            model=embeddings_model,
        )
        self.store = VectorStore(
            persist_dir=persist_dir,
            collection_name="projects",
            embedder=self.embedder,
        )
        logger.info(
            f"ProjectMemory initialized (backend={self.store.backend}, "
            f"embeddings={embeddings_model}, {self.store.count()} projects stored)"
        )

    # ═════════════════════════════════════════════════════════════
    # Save a successful project
    # ═════════════════════════════════════════════════════════════

    def save_project(
        self,
        plan: Dict[str, Any],
        architecture: Dict[str, Any],
        backend_code: Optional[Dict[str, Any]] = None,
        frontend_code: Optional[Dict[str, Any]] = None,
        quality_score: int = 50,
    ) -> bool:
        """
        Store a completed project for future reference.

        Only stores projects with quality_score >= MIN_QUALITY_TO_SAVE.

        Returns True if saved, False if skipped (low quality or error).
        """
        if quality_score < self.MIN_QUALITY_TO_SAVE:
            logger.info(
                f"Skipping project save — quality {quality_score} < {self.MIN_QUALITY_TO_SAVE}"
            )
            return False

        try:
            project_name = plan.get("project_name", "unknown")

            # ── Build searchable text ──────────────────────────
            searchable_parts = [
                plan.get("description", ""),
                project_name,
            ]
            # Add feature names
            for feature in plan.get("features", []):
                if isinstance(feature, dict):
                    searchable_parts.append(feature.get("name", ""))
                    searchable_parts.append(feature.get("description", ""))
                elif isinstance(feature, str):
                    searchable_parts.append(feature)

            # Add tech stack info
            tech_stack = architecture.get("tech_stack", {})
            for layer in ["backend", "frontend", "database"]:
                layer_info = tech_stack.get(layer, {})
                if isinstance(layer_info, dict):
                    searchable_parts.append(layer_info.get("framework", ""))
                    searchable_parts.append(layer_info.get("primary", ""))

            searchable_text = " | ".join(p for p in searchable_parts if p)

            # ── Build metadata ─────────────────────────────────
            backend_files = backend_code.get("files", {}) if backend_code else {}
            frontend_files = frontend_code.get("files", {}) if frontend_code else {}

            metadata = {
                "project_name": project_name,
                "quality_score": quality_score,
                "complexity": architecture.get("metadata", {}).get("complexity", "medium"),
                "feature_count": len(plan.get("features", [])),
                "backend_files_count": len(backend_files),
                "frontend_files_count": len(frontend_files),
                "backend_framework": tech_stack.get("backend", {}).get("framework", ""),
                "frontend_framework": tech_stack.get("frontend", {}).get("framework", ""),
                "database": tech_stack.get("database", {}).get("primary", ""),
                "saved_at": time.time(),
            }

            # ── Build the full document for storage ────────────
            # We store a condensed version, not the entire codebase
            doc_data = {
                "plan_summary": {
                    "project_name": project_name,
                    "description": plan.get("description", ""),
                    "features": [
                        f.get("name", str(f)) if isinstance(f, dict) else str(f)
                        for f in plan.get("features", [])
                    ],
                    "user_stories": plan.get("user_stories", [])[:5],  # Keep first 5
                },
                "architecture_summary": {
                    "tech_stack": tech_stack,
                    "api_endpoints": [
                        ep.get("path", "") for ep in
                        architecture.get("api_design", {}).get("endpoints", [])
                    ][:10],  # Keep first 10 endpoints
                    "tables": [
                        t.get("name", "") for t in
                        architecture.get("database_schema", {}).get("tables", [])
                    ],
                },
                "backend_file_list": list(backend_files.keys())[:20],
                "frontend_file_list": list(frontend_files.keys())[:20],
                # Store a few representative backend files (limited to keep size manageable)
                "backend_samples": self._sample_files(backend_files, max_files=3, max_chars=2000),
                "frontend_samples": self._sample_files(frontend_files, max_files=2, max_chars=1500),
            }

            # ── Store it ───────────────────────────────────────
            doc_id = VectorStore.make_id(f"{project_name}_{time.time()}")
            full_text = f"{searchable_text}\n\n{json.dumps(doc_data, ensure_ascii=False)}"

            self.store.add(
                doc_id=doc_id,
                text=full_text,
                metadata=metadata,
            )

            logger.info(
                f"✅ Saved project '{project_name}' to memory "
                f"(id={doc_id}, quality={quality_score}, "
                f"files={len(backend_files)}+{len(frontend_files)})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to save project to memory: {e}", exc_info=True)
            return False

    # ═════════════════════════════════════════════════════════════
    # Retrieve similar projects
    # ═════════════════════════════════════════════════════════════

    def find_similar(self, user_prompt: str, top_k: int = 3) -> List[Dict]:
        """
        Find the most similar past projects to the given prompt.

        Returns list of dicts with keys: id, text, metadata, similarity.
        """
        if self.store.count() == 0:
            return []

        try:
            results = self.store.query(text=user_prompt, top_k=top_k)
            # Filter out very low similarity results
            return [r for r in results if r.get("similarity", 0) > 0.3]
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []

    # ═════════════════════════════════════════════════════════════
    # Get few-shot examples for a specific agent
    # ═════════════════════════════════════════════════════════════

    def get_few_shot_examples(
        self,
        user_prompt: str,
        agent_type: str,
        top_k: int = 2,
    ) -> Optional[str]:
        """
        Return formatted few-shot examples for a specific agent type.

        Args:
            user_prompt: The current project description
            agent_type: One of "planner", "architect", "backend", "frontend", etc.
            top_k: Max number of examples to return

        Returns:
            Formatted string to append to the system prompt, or None if no
            relevant examples found.
        """
        similar = self.find_similar(user_prompt, top_k=top_k)
        if not similar:
            return None

        try:
            sections = []
            for i, result in enumerate(similar, 1):
                text = result.get("text", "")
                metadata = result.get("metadata", {})
                similarity = result.get("similarity", 0)

                # Try to parse the JSON portion of the stored text
                doc_data = self._parse_stored_doc(text)
                if not doc_data:
                    continue

                section = self._format_example_for_agent(
                    i, agent_type, doc_data, metadata, similarity
                )
                if section:
                    sections.append(section)

            if not sections:
                return None

            header = (
                "## 📚 Past Successful Examples\n\n"
                "Below are examples from similar past projects that were successfully generated. "
                "Use them as reference for quality and structure, but adapt to the current request.\n"
            )
            return header + "\n".join(sections)

        except Exception as e:
            logger.error(f"Failed to build few-shot examples: {e}")
            return None

    def _format_example_for_agent(
        self,
        index: int,
        agent_type: str,
        doc_data: Dict,
        metadata: Dict,
        similarity: float,
    ) -> Optional[str]:
        """Format a single example for a specific agent type."""
        plan_summary = doc_data.get("plan_summary", {})
        arch_summary = doc_data.get("architecture_summary", {})
        project_name = plan_summary.get("project_name", metadata.get("project_name", "Unknown"))
        quality = metadata.get("quality_score", "N/A")

        header = f"\n### Example {index}: {project_name} (quality: {quality}/100, similarity: {similarity:.0%})\n"

        if agent_type == "planner":
            features = plan_summary.get("features", [])
            stories = plan_summary.get("user_stories", [])
            body = f"**Description**: {plan_summary.get('description', 'N/A')}\n"
            if features:
                body += f"**Features**: {', '.join(features[:8])}\n"
            if stories:
                body += f"**User Stories** (sample): {json.dumps(stories[:3], ensure_ascii=False)}\n"
            return header + body

        elif agent_type == "architect":
            tech_stack = arch_summary.get("tech_stack", {})
            endpoints = arch_summary.get("api_endpoints", [])
            tables = arch_summary.get("tables", [])
            body = f"**Tech Stack**: {json.dumps(tech_stack, ensure_ascii=False)}\n"
            if endpoints:
                body += f"**API Endpoints** (sample): {', '.join(endpoints[:6])}\n"
            if tables:
                body += f"**DB Tables**: {', '.join(tables)}\n"
            return header + body

        elif agent_type in ("backend", "frontend"):
            samples_key = f"{agent_type}_samples"
            samples = doc_data.get(samples_key, {})
            file_list = doc_data.get(f"{agent_type}_file_list", [])
            body = ""
            if file_list:
                body += f"**File structure**: {', '.join(file_list[:10])}\n"
            if samples:
                body += "**Code samples**:\n"
                for fname, content in list(samples.items())[:2]:
                    # Limit content length in few-shot
                    truncated = content[:1200] + "..." if len(content) > 1200 else content
                    ext = fname.rsplit(".", 1)[-1] if "." in fname else ""
                    body += f"\n`{fname}`:\n```{ext}\n{truncated}\n```\n"
            if not body:
                return None
            return header + body

        elif agent_type in ("testing", "reviewer"):
            # Give testing/reviewer a lighter summary
            body = f"**Description**: {plan_summary.get('description', '')}\n"
            body += f"**Backend files**: {len(doc_data.get('backend_file_list', []))}\n"
            body += f"**Frontend files**: {len(doc_data.get('frontend_file_list', []))}\n"
            return header + body

        else:
            # Generic summary for unknown agent types
            body = f"**Description**: {plan_summary.get('description', 'N/A')}\n"
            return header + body

    # ═════════════════════════════════════════════════════════════
    # Stats
    # ═════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Return memory statistics."""
        return {
            "total_projects": self.store.count(),
            "backend": self.store.backend,
            "persist_dir": self.store.persist_dir,
        }

    def clear(self):
        """Clear all stored projects."""
        self.store.clear()
        logger.info("ProjectMemory cleared")

    # ═════════════════════════════════════════════════════════════
    # Internal helpers
    # ═════════════════════════════════════════════════════════════

    @staticmethod
    def _sample_files(
        files: Dict[str, str],
        max_files: int = 3,
        max_chars: int = 2000,
    ) -> Dict[str, str]:
        """
        Pick a few representative files, truncated to max_chars each.

        Prefers files like main.py, models.py, App.tsx — the most informative ones.
        """
        if not files:
            return {}

        # Priority filenames
        priority_patterns = [
            "main.py", "app.py", "models.py", "schemas.py",
            "App.tsx", "App.jsx", "index.tsx", "index.jsx",
        ]

        # Sort: priority files first, then by name
        def sort_key(fname):
            basename = fname.rsplit("/", 1)[-1] if "/" in fname else fname
            for i, pattern in enumerate(priority_patterns):
                if basename == pattern:
                    return (0, i, fname)
            return (1, 0, fname)

        sorted_files = sorted(files.keys(), key=sort_key)

        result = {}
        for fname in sorted_files[:max_files]:
            content = files[fname]
            if len(content) > max_chars:
                content = content[:max_chars] + "\n# ... (truncated)"
            result[fname] = content

        return result

    @staticmethod
    def _parse_stored_doc(text: str) -> Optional[Dict]:
        """Parse the JSON data portion of a stored document text."""
        try:
            # The text format is: "searchable text\n\n{json data}"
            json_start = text.find("{")
            if json_start < 0:
                return None
            json_text = text[json_start:]
            return json.loads(json_text)
        except (json.JSONDecodeError, ValueError):
            return None
