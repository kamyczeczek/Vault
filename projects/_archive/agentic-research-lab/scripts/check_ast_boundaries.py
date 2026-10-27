#!/usr/bin/env python3
"""check_ast_boundaries.py — Deterministic AST boundary linter for architectural rules.

Replaces unfaithful in-loop CoT deviation detection with deterministic AST verification.
Inspects Python AST import trees against explicit architectural layer rules.
"""
from __future__ import annotations
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Architectural boundary definitions:
# For each source directory prefix, define forbidden imported modules / prefixes.
DEFAULT_BOUNDARIES = [
    {
        "source_scope": "stages/",
        "forbidden_imports": ["scripts.repair_graph_state", "scripts.ingest"],
        "reason": "Stage execution must not directly trigger offline ingestion or state repair",
    },
    {
        "source_scope": "knowledge/graph/",
        "forbidden_imports": ["stages", "reflection.candidates"],
        "reason": "Knowledge graph core must not depend on higher-level stage contracts or reflection candidates",
    },
]


def extract_imports(file_path: Path) -> list[tuple[str, int]]:
    """Extract all imported module names and their line numbers from a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(file_path))
    except Exception as err:
        return []

    imports: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append((module, node.lineno))
    return imports


def check_boundaries(project_root: Path | None = None, boundaries: list[dict] | None = None) -> list[dict]:
    root = project_root or ROOT
    rules = boundaries or DEFAULT_BOUNDARIES
    violations: list[dict] = []

    py_files = [p for p in root.rglob("*.py") if not any(part.startswith((".", "__pycache__")) for part in p.parts)]

    for py_file in py_files:
        rel_path = py_file.relative_to(root).as_posix()
        for rule in rules:
            scope = rule["source_scope"]
            if rel_path.startswith(scope):
                file_imports = extract_imports(py_file)
                for mod_name, lineno in file_imports:
                    for forbidden in rule["forbidden_imports"]:
                        if mod_name == forbidden or mod_name.startswith(forbidden + "."):
                            violations.append({
                                "file": rel_path,
                                "line": lineno,
                                "imported": mod_name,
                                "forbidden_by": forbidden,
                                "reason": rule["reason"],
                            })
    return violations


def main() -> int:
    violations = check_boundaries()
    if violations:
        print(f"FAIL: Architectural boundary violations detected ({len(violations)}):", file=sys.stderr)
        for v in violations:
            print(f"  {v['file']}:{v['line']} imports `{v['imported']}` (violates: {v['forbidden_by']}) - {v['reason']}", file=sys.stderr)
        return 1

    print("OK: All AST architectural boundary constraints satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
