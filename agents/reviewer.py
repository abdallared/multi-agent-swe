"""
Review Agent — مراجعة الكود المولد وتحديد المشاكل

Performs two levels of review:
1. Static validation via CodeValidator (syntax, imports, placeholders, schema)
2. Semantic LLM review (cross-file consistency, API contracts, security)

Returns a structured ReviewResult used by the Pipeline self-correction loop.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from utils.code_validator import CodeValidator
import json
import logging

logger = logging.getLogger(__name__)


class ReviewAgent(BaseAgent):
    """
    Review Agent — يراجع الكود المولد ويحدد المشاكل للإصلاح التلقائي
    """

    def get_system_prompt(self) -> str:
        return """You are a senior code reviewer and software quality engineer.

Your role is to review generated Full-Stack code (FastAPI backend + React frontend) and identify issues that would prevent the application from running correctly.

REVIEW CHECKLIST:
1. **Cross-file imports**: Every import in every file must resolve to an actual generated file
2. **API contract match**: Frontend API calls must match backend endpoint paths, methods, and request/response shapes
3. **Database consistency**: SQLAlchemy models must match the architecture schema (tables, columns, relationships)
4. **Security**: Passwords must be hashed (never plain text), protected routes must use auth dependency
5. **Missing files**: All files referenced by imports/routing must exist in the generated set
6. **Completeness**: No placeholder code (TODO, ..., pass # implement, "rest of code")
7. **Router registration**: All API routers must be included in main.py
8. **Frontend routing**: All page components must be imported and routed in App.tsx
9. **Type consistency**: Frontend TypeScript interfaces must match backend Pydantic schemas

OUTPUT FORMAT — valid JSON only:
{
    "passed": true/false,
    "backend_issues": [
        {
            "file": "app/api/auth.py",
            "severity": "critical",
            "description": "Plain text password comparison on line 15",
            "fix_instruction": "Use verify_password() from app.core.security instead of == comparison"
        }
    ],
    "frontend_issues": [
        {
            "file": "src/services/api.ts",
            "severity": "critical",
            "description": "API calls /api/task/ but backend registers router at /api/tasks/",
            "fix_instruction": "Change endpoint path from /task/ to /tasks/"
        }
    ],
    "summary": "Found 2 critical issues: password security and API path mismatch"
}

SEVERITY LEVELS:
- "critical": Will cause runtime errors, security vulnerabilities, or broken functionality
- "warning": May cause issues but won't prevent the app from running

Only report REAL issues. Do not invent problems. If the code looks correct, return {"passed": true, "backend_issues": [], "frontend_issues": [], "summary": "All checks passed"}."""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        مراجعة الكود المولد — static + semantic review
        """
        logger.info("🔍 Review Agent: Starting code review...")

        architecture = context.get('architecture', {})
        backend_code = context.get('backend_code', {})
        frontend_code = context.get('frontend_code', {})
        project_plan = context.get('project_plan', {})

        backend_files = backend_code.get('files', {})
        frontend_files = frontend_code.get('files', {})

        # ── Step 1: Static validation ──────────────────────────
        validator = CodeValidator()

        static_backend_report = validator.validate_backend_files(
            backend_files, architecture=architecture
        )
        static_frontend_report = validator.validate_frontend_files(frontend_files)

        static_issues_backend = self._report_to_issues(static_backend_report)
        static_issues_frontend = self._report_to_issues(static_frontend_report)

        self._emit_verbose("info", (
            f"Static validation: {static_backend_report.critical_count} backend critical, "
            f"{static_frontend_report.critical_count} frontend critical"
        ))

        # ── Step 2: Semantic LLM review ────────────────────────
        llm_issues_backend = []
        llm_issues_frontend = []

        try:
            llm_review = self._semantic_review(
                project_plan, architecture, backend_files, frontend_files
            )
            llm_issues_backend = llm_review.get('backend_issues', [])
            llm_issues_frontend = llm_review.get('frontend_issues', [])
        except Exception as e:
            logger.warning(f"Semantic review failed, using static-only: {e}")
            self._emit_verbose("error", f"Semantic review failed: {e}")

        # ── Step 3: Merge and deduplicate ──────────────────────
        all_backend_issues = self._merge_issues(static_issues_backend, llm_issues_backend)
        all_frontend_issues = self._merge_issues(static_issues_frontend, llm_issues_frontend)

        # Filter to critical only for pass/fail decision
        critical_count = sum(
            1 for i in all_backend_issues + all_frontend_issues
            if i.get('severity') == 'critical'
        )
        passed = critical_count == 0

        summary = (
            f"✅ All checks passed — no critical issues found"
            if passed
            else f"❌ Found {critical_count} critical issue(s) requiring fixes"
        )

        if all_backend_issues or all_frontend_issues:
            detail_lines = []
            for issue in all_backend_issues + all_frontend_issues:
                sev = "❌" if issue['severity'] == 'critical' else "⚠️"
                detail_lines.append(f"  {sev} [{issue['file']}]: {issue['description']}")
            summary += "\n" + "\n".join(detail_lines)

        logger.info(f"🔍 Review complete: {'PASSED' if passed else 'ISSUES FOUND'} "
                     f"({len(all_backend_issues)} backend, {len(all_frontend_issues)} frontend)")

        self._emit_verbose("info", summary)

        return {
            'passed': passed,
            'backend_issues': all_backend_issues,
            'frontend_issues': all_frontend_issues,
            'summary': summary,
            'critical_count': critical_count,
            'total_issues': len(all_backend_issues) + len(all_frontend_issues),
        }

    # ── Semantic LLM Review ─────────────────────────────────────

    def _semantic_review(
        self,
        plan: Dict,
        architecture: Dict,
        backend_files: Dict[str, str],
        frontend_files: Dict[str, str],
    ) -> Dict:
        """
        Use the LLM to perform a semantic review of generated code.
        Sends file summaries (not full content) to stay within token limits.
        """
        # Build file summaries — file name + first 30 lines
        backend_summary = self._summarize_files(backend_files, max_lines=30)
        frontend_summary = self._summarize_files(frontend_files, max_lines=25)

        # Architecture summary
        endpoints = architecture.get('api_design', {}).get('endpoints', [])
        tables = architecture.get('database_schema', {}).get('tables', [])

        endpoints_text = "\n".join(
            f"  - {ep['method']} {ep['path']}: {ep.get('description', '')}"
            for ep in endpoints[:8]
        )
        tables_text = "\n".join(
            f"  - {t['name']}: {', '.join(c['name'] for c in t.get('columns', [])[:6])}"
            for t in tables[:5]
        )

        prompt = f"""Review the following generated Full-Stack project code for issues.

PROJECT: {plan.get('project_name', 'Unknown')}

ARCHITECTURE SPEC:
API Endpoints:
{endpoints_text}

Database Tables:
{tables_text}

BACKEND FILES:
{backend_summary}

FRONTEND FILES:
{frontend_summary}

Review the code against your checklist and return ONLY valid JSON with your findings.
Focus on CRITICAL issues that would prevent the app from running. Do not report style preferences."""

        response = self.call_llm(
            prompt=prompt,
            json_mode=True,
            temperature=0.1,
        )

        return self._parse_review_response(response)

    def _summarize_files(self, files: Dict[str, str], max_lines: int = 30) -> str:
        """Build a compact summary of files for the review prompt."""
        summaries = []
        for filename, content in files.items():
            if not content.strip():
                summaries.append(f"--- {filename} (empty) ---")
                continue
            lines = content.strip().split('\n')
            preview = '\n'.join(lines[:max_lines])
            truncated = f"... ({len(lines) - max_lines} more lines)" if len(lines) > max_lines else ""
            summaries.append(f"--- {filename} ({len(lines)} lines) ---\n{preview}\n{truncated}")
        return "\n\n".join(summaries)

    def _parse_review_response(self, response: str) -> Dict:
        """Parse JSON review response from LLM."""
        response = response.strip()

        # Strip markdown code blocks
        if response.startswith('```json'):
            response = response.split('```json')[1].split('```')[0].strip()
        elif response.startswith('```'):
            response = response.split('```')[1].split('```')[0].strip()

        # Fix common JSON issues
        if not response.endswith('}'):
            last_brace = response.rfind('}')
            if last_brace > 0:
                response = response[:last_brace + 1]

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            response = response.replace(',}', '}').replace(',]', ']')
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse semantic review JSON")
                return {'passed': True, 'backend_issues': [], 'frontend_issues': [], 'summary': 'Parse failed — skipping semantic review'}

        # Validate structure
        if not isinstance(result, dict):
            return {'passed': True, 'backend_issues': [], 'frontend_issues': [], 'summary': 'Invalid review format'}

        # Normalize issues
        for key in ('backend_issues', 'frontend_issues'):
            if key not in result or not isinstance(result[key], list):
                result[key] = []
            result[key] = [
                issue for issue in result[key]
                if isinstance(issue, dict) and 'file' in issue and 'description' in issue
            ]
            # Ensure severity and fix_instruction exist
            for issue in result[key]:
                issue.setdefault('severity', 'warning')
                issue.setdefault('fix_instruction', '')

        result.setdefault('passed', len(result.get('backend_issues', [])) == 0 and len(result.get('frontend_issues', [])) == 0)
        result.setdefault('summary', '')

        return result

    # ── Helpers ──────────────────────────────────────────────────

    def _report_to_issues(self, report) -> List[Dict]:
        """Convert a ValidationReport into a list of issue dicts."""
        issues = []
        for item in report.issues:
            issues.append({
                'file': item.file,
                'severity': item.severity,
                'description': item.description,
                'fix_instruction': item.fix_suggestion or '',
                'source': 'static',
            })
        return issues

    def _merge_issues(
        self,
        static_issues: List[Dict],
        llm_issues: List[Dict],
    ) -> List[Dict]:
        """
        Merge static and LLM issues, deduplicating by file + description similarity.
        """
        merged = list(static_issues)
        seen_descriptions = {
            (i['file'], i['description'][:50]) for i in static_issues
        }

        for issue in llm_issues:
            key = (issue.get('file', ''), issue.get('description', '')[:50])
            if key not in seen_descriptions:
                issue['source'] = 'semantic'
                merged.append(issue)
                seen_descriptions.add(key)

        # Sort: critical first, then by file
        merged.sort(key=lambda x: (0 if x.get('severity') == 'critical' else 1, x.get('file', '')))
        return merged
