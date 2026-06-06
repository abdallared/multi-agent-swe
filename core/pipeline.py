"""
Pipeline — Orchestrates agent execution with parallel support.

Replaces the linear sequential flow with an intelligent pipeline that
runs independent agents concurrently while maintaining correct dependencies.

Flow:
    Plan → Architect → [Backend ∥ Frontend] → Review (self-correction loop) → Build → [Testing ∥ Docker] → Done

Supports optional ProjectMemory for learning from past generations.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional, Callable, Dict, Any

try:
    from memory.project_memory import ProjectMemory
except ImportError:
    ProjectMemory = None

from agents.planner import PlannerAgent
from agents.architect import ArchitectAgent
from agents.backend import BackendAgent
from agents.frontend import FrontendAgent
from agents.testing import TestingAgent
from agents.docker import DockerAgent
from agents.reviewer import ReviewAgent
from builder.file_builder import FileBuilder

logger = logging.getLogger(__name__)

# Maximum number of review → fix → re-review cycles
MAX_REVIEW_ITERATIONS = 2


class PipelineUpdate:
    """Structured update event from the pipeline."""

    def __init__(self, event: str, phase: int, name: str, status: str, data: dict = None):
        self.event = event        # "phase_start" | "phase_complete" | "generation_complete" | "error"
        self.phase = phase
        self.name = name
        self.status = status      # "running" | "completed" | "failed"
        self.data = data or {}

    def to_dict(self) -> dict:
        return {
            "type": self.event,
            "data": {
                "phase": self.phase,
                "name": self.name,
                "status": self.status,
                **self.data,
            },
        }


class Pipeline:
    """
    Agent orchestrator with parallel execution and self-correction support.

    Usage (async):
        pipeline = Pipeline(ollama_interface, output_dir="./output")
        result = await pipeline.run("Build a task manager app", on_update=callback)

    Usage (sync):
        pipeline = Pipeline(ollama_interface, output_dir="./output")
        result = pipeline.run_sync("Build a task manager app")
    """

    def __init__(self, llm_interface, output_dir: str = "./output", memory=None):
        self.llm = llm_interface
        self.output_dir = output_dir
        self.memory = memory  # Optional ProjectMemory instance

    # ── Main async entry point ──────────────────────────────────

    async def run(
        self,
        user_prompt: str,
        on_update: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Run the full generation pipeline with parallel execution.

        Args:
            user_prompt: The project description from the user.
            on_update: Optional async/sync callback for progress updates.

        Returns:
            Dictionary with all generation results.
        """
        t0 = time.time()
        result = {}

        try:
            # ── Phase 1: Planning (sequential) ─────────────────
            await self._emit(on_update, "phase_start", 1, "Planning", "running")

            planner = PlannerAgent(self.llm, self.memory)
            plan_result = await asyncio.to_thread(planner.execute, {"user_prompt": user_prompt})
            plan = plan_result["project_plan"]

            await self._emit(on_update, "phase_complete", 1, "Planning", "completed", {
                "project_name": plan["project_name"],
                "features_count": len(plan["features"]),
                "user_stories_count": len(plan["user_stories"]),
            })

            # ── Phase 2: Architecture (sequential) ─────────────
            await self._emit(on_update, "phase_start", 2, "Architecture", "running")

            architect = ArchitectAgent(self.llm, self.memory)
            arch_result = await asyncio.to_thread(architect.execute, {"project_plan": plan})
            arch = arch_result["architecture"]
            complexity = arch.get("metadata", {}).get("complexity", "medium")

            await self._emit(on_update, "phase_complete", 2, "Architecture", "completed", {
                "backend": arch["tech_stack"]["backend"]["framework"],
                "frontend": arch["tech_stack"]["frontend"]["framework"],
                "database": arch["tech_stack"]["database"]["primary"],
                "tables_count": len(arch["database_schema"]["tables"]),
                "endpoints_count": len(arch["api_design"]["endpoints"]),
                "complexity": complexity,
            })

            # ── Phase 3 & 4: Backend + Frontend (PARALLEL) ─────
            await self._emit(on_update, "phase_start", 3, "Backend Code", "running")
            await self._emit(on_update, "phase_start", 4, "Frontend Code", "running")

            backend_agent = BackendAgent(self.llm, self.memory)
            frontend_agent = FrontendAgent(self.llm, self.memory)

            backend_future = asyncio.to_thread(
                backend_agent.execute,
                {"project_plan": plan, "architecture": arch},
            )
            frontend_future = asyncio.to_thread(
                frontend_agent.execute,
                {"project_plan": plan, "architecture": arch},
            )

            # Run both concurrently
            backend_result, frontend_result = await asyncio.gather(
                backend_future, frontend_future
            )

            backend_code = backend_result["backend_code"]
            frontend_code = frontend_result["frontend_code"]

            await self._emit(on_update, "phase_complete", 3, "Backend Code", "completed", {
                "files_count": len(backend_code["files"]),
            })
            await self._emit(on_update, "phase_complete", 4, "Frontend Code", "completed", {
                "files_count": len(frontend_code["files"]),
            })

            # ── Phase 5: Review + Self-Correction Loop ─────────
            review_summary = "Skipped"
            for iteration in range(MAX_REVIEW_ITERATIONS):
                await self._emit(on_update, "phase_start", 5, "Code Review", "running", {
                    "iteration": iteration + 1,
                    "max_iterations": MAX_REVIEW_ITERATIONS,
                })

                reviewer = ReviewAgent(self.llm, self.memory)
                review_result = await asyncio.to_thread(reviewer.execute, {
                    "project_plan": plan,
                    "architecture": arch,
                    "backend_code": backend_code,
                    "frontend_code": frontend_code,
                })

                review_summary = review_result.get("summary", "")

                if review_result["passed"]:
                    await self._emit(on_update, "phase_complete", 5, "Code Review", "completed", {
                        "result": "passed",
                        "iteration": iteration + 1,
                        "summary": review_summary,
                    })
                    break

                # Self-correction: fix issues and re-review
                logger.info(
                    f"Review iteration {iteration + 1}: {review_result['critical_count']} critical issues found, "
                    f"attempting self-correction..."
                )

                backend_issues = review_result.get("backend_issues", [])
                frontend_issues = review_result.get("frontend_issues", [])

                # Fix backend if needed
                if backend_issues:
                    backend_code = await self._fix_code(
                        backend_agent, plan, arch, backend_code, backend_issues, "backend"
                    )

                # Fix frontend if needed
                if frontend_issues:
                    frontend_code = await self._fix_code(
                        frontend_agent, plan, arch, frontend_code, frontend_issues, "frontend"
                    )

                await self._emit(on_update, "phase_complete", 5, "Code Review", "completed", {
                    "result": "self_corrected",
                    "iteration": iteration + 1,
                    "issues_fixed": len(backend_issues) + len(frontend_issues),
                })
            else:
                # Max iterations reached without passing — proceed anyway
                logger.warning(
                    f"Review did not pass after {MAX_REVIEW_ITERATIONS} iterations. "
                    f"Proceeding with best-effort code."
                )
                await self._emit(on_update, "phase_complete", 5, "Code Review", "completed", {
                    "result": "max_iterations_reached",
                    "iteration": MAX_REVIEW_ITERATIONS,
                    "summary": review_summary,
                })

            # ── Phase 6: Build Files (sequential) ──────────────
            await self._emit(on_update, "phase_start", 6, "File Building", "running")

            builder = FileBuilder(output_dir=self.output_dir)
            project_dir = builder.create_project_structure(
                project_name=plan["project_name"],
                architecture=arch,
            )
            builder.write_files(backend_code["files"], project_dir / "backend")
            builder.write_files(frontend_code["files"], project_dir / "frontend")

            await self._emit(on_update, "phase_complete", 6, "File Building", "completed", {
                "project_path": str(project_dir),
            })

            # ── Phase 7 & 8: Testing + Docker (PARALLEL) ──────
            await self._emit(on_update, "phase_start", 7, "Testing", "running")
            await self._emit(on_update, "phase_start", 8, "Docker", "running")

            testing_agent = TestingAgent(self.llm, self.memory)
            docker_agent = DockerAgent(self.llm, self.memory)

            test_future = asyncio.to_thread(
                testing_agent.execute,
                {"project_plan": plan, "architecture": arch, "backend_code": backend_code},
            )
            docker_future = asyncio.to_thread(
                docker_agent.execute,
                {"project_plan": plan, "architecture": arch},
            )

            test_result, docker_result = await asyncio.gather(
                test_future, docker_future
            )

            # Write test and docker files
            backend_tests = test_result["backend_tests"]
            docker_files = docker_result["docker_files"]
            builder.write_files(backend_tests, project_dir / "backend")
            builder.write_files(docker_files, project_dir)

            await self._emit(on_update, "phase_complete", 7, "Testing", "completed", {
                "test_files": len(backend_tests),
            })
            await self._emit(on_update, "phase_complete", 8, "Docker", "completed", {
                "docker_files": len(docker_files),
            })

            # ── Create README ──────────────────────────────────
            project_info = {
                "name": plan["project_name"],
                "description": plan["description"],
                "backend": arch["tech_stack"]["backend"]["framework"],
                "frontend": arch["tech_stack"]["frontend"]["framework"],
                "database": arch["tech_stack"]["database"]["primary"],
                "features": [f["name"] for f in plan["features"]],
                "test_command": test_result.get("test_commands", {}).get("backend", "pytest tests/ -v"),
            }
            builder.create_readme(project_dir, project_info)

            # ── File tree ──────────────────────────────────────
            file_tree = self._get_file_tree(project_dir)

            clean_project_name = plan["project_name"].lower().replace(" ", "_")
            clean_project_name = "".join(c for c in clean_project_name if c.isalnum() or c == "_")

            elapsed = round(time.time() - t0, 1)

            result = {
                "project_name": plan["project_name"],
                "clean_project_name": clean_project_name,
                "project_path": str(project_dir),
                "file_tree": file_tree,
                "elapsed_seconds": elapsed,
                "plan": plan,
                "architecture": arch,
                "backend_code": backend_code,
                "frontend_code": frontend_code,
                "backend_tests": backend_tests,
                "docker_files": docker_files,
                "review_summary": review_summary,
                "total_files": (
                    len(backend_code["files"])
                    + len(frontend_code["files"])
                    + len(backend_tests)
                    + len(docker_files)
                ),
                "summary": {
                    "features": len(plan["features"]),
                    "backend_files": len(backend_code["files"]),
                    "frontend_files": len(frontend_code["files"]),
                    "test_files": len(backend_tests),
                    "docker_files": len(docker_files),
                },
            }

            await self._emit(on_update, "generation_complete", 0, "Complete", "completed", result)

            logger.info(f"🎉 Pipeline completed in {elapsed}s — {result['total_files']} files generated")

            # ── Save to memory for future reference ────────────
            self._save_to_memory(
                plan=plan,
                architecture=arch,
                backend_code=backend_code,
                frontend_code=frontend_code,
                review_passed=(review_summary != "Skipped" and "max_iterations_reached" not in str(review_summary)),
                total_files=result["total_files"],
                had_errors=False,
            )

            return result

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            await self._emit(on_update, "error", 0, "Error", "failed", {"message": str(e)})

            # Still try to save partial results to memory
            self._save_to_memory(
                plan=result.get("plan") or {},
                architecture=result.get("architecture") or {},
                had_errors=True,
            )

            raise

    # ── Self-Correction Helper ──────────────────────────────────

    async def _fix_code(
        self,
        agent,
        plan: Dict,
        arch: Dict,
        current_code: Dict,
        issues: list,
        code_type: str,
    ) -> Dict:
        """
        Re-run a code agent with fix instructions to correct review issues.

        Args:
            agent: The BackendAgent or FrontendAgent instance
            plan: Project plan dict
            arch: Architecture dict
            current_code: Current {"files": {...}} dict
            issues: List of issue dicts from ReviewAgent
            code_type: "backend" or "frontend"

        Returns:
            Updated code dict with fixed files
        """
        # Build fix prompt with issues
        issues_text = "\n".join(
            f"- [{i.get('severity', 'warning').upper()}] {i['file']}: {i['description']}"
            + (f"\n  Fix: {i['fix_instruction']}" if i.get('fix_instruction') else "")
            for i in issues
        )

        # List affected files
        affected_files = list({i['file'] for i in issues if i.get('file')})
        affected_code = {}
        for fname in affected_files:
            if fname in current_code.get('files', {}):
                affected_code[fname] = current_code['files'][fname]

        if not affected_code:
            logger.warning(f"No affected files found for {code_type} fix, skipping")
            return current_code

        # Build the fix prompt
        files_content = "\n\n".join(
            f"--- {fname} ---\n{content}"
            for fname, content in affected_code.items()
        )

        fix_prompt = f"""The following {code_type} files have issues that need to be fixed.

PROJECT: {plan.get('project_name', '')}

ISSUES FOUND:
{issues_text}

CURRENT FILES WITH ISSUES:
{files_content}

Fix ALL the issues listed above. Return ONLY valid JSON with the fixed files:
{{"files": {{"filename": "complete fixed file content", ...}}}}

IMPORTANT:
- Return COMPLETE file content for each fixed file, not just the changed lines
- Only include files that needed fixes
- Do not introduce new issues while fixing"""

        try:
            response = await asyncio.to_thread(
                agent.call_llm,
                fix_prompt,
                None,  # system_prompt (use default)
                0.1,   # temperature
                None,  # max_tokens (auto)
                True,  # json_mode
            )

            # Parse the fix response
            fixed_code = self._parse_fix_response(response)

            if fixed_code and 'files' in fixed_code:
                # Merge fixed files into current code
                merged = dict(current_code.get('files', {}))
                for fname, content in fixed_code['files'].items():
                    if content.strip():  # Only update if content is non-empty
                        merged[fname] = content
                        logger.info(f"  ✅ Fixed: {fname}")

                return {'files': merged}

        except Exception as e:
            logger.warning(f"Self-correction failed for {code_type}: {e}")

        # Return original code if fix failed
        return current_code

    def _parse_fix_response(self, response: str) -> Dict:
        """Parse JSON fix response from LLM."""
        response = response.strip()

        if response.startswith('```json'):
            response = response.split('```json')[1].split('```')[0].strip()
        elif response.startswith('```'):
            response = response.split('```')[1].split('```')[0].strip()

        if not response.endswith('}'):
            last_brace = response.rfind('}')
            if last_brace > 0:
                response = response[:last_brace + 1]

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            response = response.replace(',}', '}').replace(',]', ']')
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}

    # ── Sync wrapper ────────────────────────────────────────────

    def run_sync(self, user_prompt: str, on_update: Optional[Callable] = None) -> Dict[str, Any]:
        """Synchronous wrapper for CLI usage."""
        return asyncio.run(self.run(user_prompt, on_update=on_update))

    # ── Memory helpers ──────────────────────────────────────────

    def _save_to_memory(
        self,
        plan: Dict = None,
        architecture: Dict = None,
        backend_code: Dict = None,
        frontend_code: Dict = None,
        review_passed: bool = False,
        total_files: int = 0,
        had_errors: bool = False,
    ):
        """Save a completed project to memory for future reference."""
        if not self.memory:
            return

        try:
            quality_score = self._calculate_quality_score(
                review_passed=review_passed,
                total_files=total_files,
                had_errors=had_errors,
            )
            self.memory.save_project(
                plan=plan or {},
                architecture=architecture or {},
                backend_code=backend_code,
                frontend_code=frontend_code,
                quality_score=quality_score,
            )
            logger.info(f"📚 Project saved to memory (quality={quality_score})")
        except Exception as e:
            logger.warning(f"Failed to save project to memory (non-fatal): {e}")

    @staticmethod
    def _calculate_quality_score(
        review_passed: bool = False,
        total_files: int = 0,
        had_errors: bool = False,
    ) -> int:
        """
        Calculate a simple quality score (0–100) for a generated project.

        Scoring:
        - Review passed:        +40 points
        - No errors:            +30 points
        - Files generated:      +1 per file (max 30)
        """
        score = 0
        if review_passed:
            score += 40
        if not had_errors:
            score += 30
        score += min(total_files, 30)
        return min(score, 100)

    # ── Internal helpers ────────────────────────────────────────

    async def _emit(
        self,
        callback: Optional[Callable],
        event: str,
        phase: int,
        name: str,
        status: str,
        data: dict = None,
    ):
        """Emit a progress update to the callback if set."""
        if callback is None:
            return

        update = PipelineUpdate(event, phase, name, status, data)
        try:
            result = callback(update)
            # If callback is async, await it
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.warning(f"Pipeline callback error: {e}")

    def _get_file_tree(self, project_dir: Path) -> dict:
        """Recursively build a file tree dict."""
        def build_tree(path: Path) -> dict:
            if path.is_file():
                return {
                    "name": path.name,
                    "type": "file",
                    "path": str(path.relative_to(project_dir)),
                }
            children = []
            try:
                for child in sorted(path.iterdir()):
                    if child.name not in ("__pycache__", ".git", "node_modules", "venv"):
                        children.append(build_tree(child))
            except PermissionError:
                pass
            return {
                "name": path.name,
                "type": "folder",
                "path": str(path.relative_to(project_dir)),
                "children": children,
            }

        return build_tree(project_dir)

