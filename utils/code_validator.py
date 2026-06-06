"""
Code Validator — Static analysis for generated code.

Validates generated Python and TypeScript/JSX files before writing to disk.
Catches syntax errors, missing imports, and schema inconsistencies early,
enabling self-correction via the Review Agent or inline retry.
"""

import ast
import re
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """A single validation issue found in generated code."""
    file: str
    severity: str       # "critical" | "warning" | "info"
    category: str       # "syntax" | "import" | "schema" | "placeholder" | "structure"
    description: str
    line: Optional[int] = None
    fix_suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    """Full validation report for a set of generated files."""
    issues: List[ValidationIssue] = field(default_factory=list)

    def add(self, issue: ValidationIssue):
        self.issues.append(issue)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def is_valid(self) -> bool:
        """True if no critical issues found."""
        return self.critical_count == 0

    def summary(self) -> str:
        if not self.issues:
            return "✅ All files passed validation"
        lines = [f"❌ {self.critical_count} critical, ⚠️ {self.warning_count} warnings"]
        for issue in self.issues:
            prefix = "❌" if issue.severity == "critical" else "⚠️"
            loc = f" (line {issue.line})" if issue.line else ""
            lines.append(f"  {prefix} [{issue.file}]{loc}: {issue.description}")
        return "\n".join(lines)

    def to_prompt_text(self) -> str:
        """Format issues as text suitable for an LLM fix-it prompt."""
        lines = []
        for issue in self.issues:
            loc = f" (line {issue.line})" if issue.line else ""
            fix = f" → Fix: {issue.fix_suggestion}" if issue.fix_suggestion else ""
            lines.append(f"- [{issue.severity.upper()}] {issue.file}{loc}: {issue.description}{fix}")
        return "\n".join(lines)


class CodeValidator:
    """
    Validates generated code files.

    Supports:
    - Python syntax validation (AST parsing)
    - Import completeness check
    - Placeholder / truncation detection
    - Schema consistency (architecture tables vs generated models)
    - Frontend structure validation
    """

    # ── Python Validation ───────────────────────────────────────

    def validate_python_syntax(self, filename: str, code: str) -> List[ValidationIssue]:
        """Parse Python code with AST to detect syntax errors."""
        issues = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(ValidationIssue(
                file=filename,
                severity="critical",
                category="syntax",
                description=f"Python syntax error: {e.msg}",
                line=e.lineno,
                fix_suggestion=f"Fix the syntax error at line {e.lineno}: {e.msg}",
            ))
        return issues

    def validate_python_imports(self, filename: str, code: str) -> List[ValidationIssue]:
        """
        Check for commonly missing imports in generated FastAPI code.
        Not a full static analyzer — just catches the most frequent LLM mistakes.
        """
        issues = []

        # Known patterns: if X is used, Y must be imported
        patterns = [
            # SQLAlchemy models
            {
                "usage": r"Column\(",
                "import": "from sqlalchemy import",
                "desc": "Uses Column() but missing sqlalchemy import",
                "fix": "Add: from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text",
            },
            {
                "usage": r"class \w+\(Base\)",
                "import": "from app.core.database import Base",
                "desc": "Inherits from Base but missing Base import",
                "fix": "Add: from app.core.database import Base",
            },
            # Security
            {
                "usage": r"get_password_hash\(",
                "import": "get_password_hash",
                "desc": "Uses get_password_hash() but not imported",
                "fix": "Add: from app.core.security import get_password_hash, verify_password",
            },
            {
                "usage": r"verify_password\(",
                "import": "verify_password",
                "desc": "Uses verify_password() but not imported",
                "fix": "Add: from app.core.security import verify_password, get_password_hash",
            },
            {
                "usage": r"create_access_token\(",
                "import": "create_access_token",
                "desc": "Uses create_access_token() but not imported",
                "fix": "Add: from app.core.security import create_access_token",
            },
            # FastAPI
            {
                "usage": r"Depends\(",
                "import": "Depends",
                "desc": "Uses Depends() but not imported",
                "fix": "Add: from fastapi import Depends",
            },
            {
                "usage": r"HTTPException\(",
                "import": "HTTPException",
                "desc": "Uses HTTPException but not imported",
                "fix": "Add: from fastapi import HTTPException",
            },
            # Database
            {
                "usage": r"get_db\b",
                "import": "get_db",
                "desc": "Uses get_db but not imported",
                "fix": "Add: from app.core.database import get_db",
            },
        ]

        for pattern in patterns:
            if re.search(pattern["usage"], code) and pattern["import"] not in code:
                issues.append(ValidationIssue(
                    file=filename,
                    severity="critical",
                    category="import",
                    description=pattern["desc"],
                    fix_suggestion=pattern["fix"],
                ))

        return issues

    def validate_no_placeholders(self, filename: str, code: str) -> List[ValidationIssue]:
        """Detect truncated or placeholder code that LLMs sometimes generate."""
        issues = []

        placeholder_patterns = [
            (r"#\s*\.\.\..*rest\s*of\s*code", "Found '... rest of code' placeholder"),
            (r"#\s*TODO:?\s*implement", "Found 'TODO: implement' placeholder"),
            (r"#\s*Add\s+more\s+", "Found 'Add more...' placeholder"),
            (r"\.\.\.\s*$", "Found '...' truncation at end of line"),
            (r"pass\s*#\s*implement", "Found 'pass # implement' placeholder"),
            (r"#\s*remaining\s+(code|logic|endpoints)", "Found 'remaining code' placeholder"),
        ]

        for pattern, desc in placeholder_patterns:
            matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = code[:match.start()].count("\n") + 1
                issues.append(ValidationIssue(
                    file=filename,
                    severity="warning",
                    category="placeholder",
                    description=desc,
                    line=line_num,
                    fix_suggestion="Replace placeholder with complete implementation",
                ))

        return issues

    def validate_python_model_structure(self, filename: str, code: str) -> List[ValidationIssue]:
        """Validate SQLAlchemy model files have __tablename__."""
        issues = []

        if "/models/" in filename and filename.endswith(".py"):
            # Skip __init__.py
            if "__init__" in filename:
                return issues

            if "class " in code and "(Base)" in code:
                if "__tablename__" not in code:
                    issues.append(ValidationIssue(
                        file=filename,
                        severity="critical",
                        category="structure",
                        description="SQLAlchemy model missing __tablename__",
                        fix_suggestion="Add __tablename__ = 'table_name' to the model class",
                    ))

        return issues

    # ── Frontend Validation ─────────────────────────────────────

    def validate_frontend_file(self, filename: str, code: str) -> List[ValidationIssue]:
        """Basic validation for TypeScript/JSX files."""
        issues = []

        # Check API base URL
        if filename.endswith("api.ts") or filename.endswith("api.tsx"):
            if "import.meta.env.VITE_API_URL" not in code and "localhost:8000" not in code:
                issues.append(ValidationIssue(
                    file=filename,
                    severity="warning",
                    category="structure",
                    description="API service missing VITE_API_URL or localhost fallback",
                    fix_suggestion="Add: const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'",
                ))

        # Check for export default in page/component files
        if ("/pages/" in filename or "/components/" in filename) and filename.endswith((".tsx", ".ts")):
            if "export default" not in code:
                issues.append(ValidationIssue(
                    file=filename,
                    severity="warning",
                    category="structure",
                    description="Component/page missing 'export default'",
                    fix_suggestion="Add 'export default ComponentName;' at the end of the file",
                ))

        # Check for placeholders
        issues.extend(self.validate_no_placeholders(filename, code))

        return issues

    # ── Schema Consistency ──────────────────────────────────────

    def validate_schema_consistency(
        self,
        architecture: Dict,
        backend_files: Dict[str, str],
    ) -> List[ValidationIssue]:
        """
        Verify that database tables defined in the architecture
        have corresponding model files in the generated code.
        """
        issues = []

        # Extract expected table names from architecture
        tables = architecture.get("database_schema", {}).get("tables", [])
        expected_tables = {t["name"].lower() for t in tables}

        # Extract __tablename__ values from generated models
        generated_tables = set()
        for filename, code in backend_files.items():
            if "/models/" in filename and "__tablename__" in code:
                match = re.search(r'__tablename__\s*=\s*["\'](\w+)["\']', code)
                if match:
                    generated_tables.add(match.group(1).lower())

        # Find missing tables
        missing = expected_tables - generated_tables
        for table_name in missing:
            issues.append(ValidationIssue(
                file="(schema)",
                severity="warning",
                category="schema",
                description=f"Architecture defines table '{table_name}' but no model was generated for it",
                fix_suggestion=f"Generate a SQLAlchemy model with __tablename__ = '{table_name}'",
            ))

        return issues

    # ── Aggregate Validators ────────────────────────────────────

    def validate_backend_files(
        self,
        files: Dict[str, str],
        architecture: Optional[Dict] = None,
    ) -> ValidationReport:
        """Run all backend validations on a set of generated files."""
        report = ValidationReport()

        for filename, code in files.items():
            if not code.strip():
                continue

            if filename.endswith(".py"):
                report.issues.extend(self.validate_python_syntax(filename, code))
                report.issues.extend(self.validate_python_imports(filename, code))
                report.issues.extend(self.validate_no_placeholders(filename, code))
                report.issues.extend(self.validate_python_model_structure(filename, code))

        if architecture:
            report.issues.extend(self.validate_schema_consistency(architecture, files))

        # Log summary
        if report.issues:
            logger.warning(f"Backend validation: {report.summary()}")
        else:
            logger.info("Backend validation: all files passed ✅")

        return report

    def validate_frontend_files(self, files: Dict[str, str]) -> ValidationReport:
        """Run all frontend validations on a set of generated files."""
        report = ValidationReport()

        for filename, code in files.items():
            if not code.strip():
                continue

            if filename.endswith((".ts", ".tsx", ".jsx")):
                report.issues.extend(self.validate_frontend_file(filename, code))

        if report.issues:
            logger.warning(f"Frontend validation: {report.summary()}")
        else:
            logger.info("Frontend validation: all files passed ✅")

        return report


# Singleton
validator = CodeValidator()
