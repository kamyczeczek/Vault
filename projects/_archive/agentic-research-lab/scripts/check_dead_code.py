#!/usr/bin/env python3
"""Dead-code gate: unused imports and orphan modules (stdlib AST only).

Agent iterations leave abandoned imports and scratch scripts behind; manual
review does not scale against that volume (approval-by-fatigue), so this
runs deterministically instead. Two checks:

1. Unused imports (F401-equivalent): names bound by `import X` / `from M
   import Y` that no code in the same file references. `__main__`-guarded
   re-exports are out of scope — imports are usage, not interface.
2. Orphan modules: `.py` files under `scripts/`, `pipeline/`, and the repo
   root that nothing imports and no gate/contract references by path, and
   that are not CLI entry points (`if __name__ == ...` or argparse `main`).
   Tests, hooks, and skills are excluded by directory by design.

Exit 0 = clean, 1 = dead code found (listed). No auto-fix: deletion is a
human decision; this gate only refuses to let it accumulate silently.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["scripts", "pipeline"]
SCAN_ROOT_GLOBS = ["*.py"]
EXCLUDE_DIRS = {"tests", "hooks", "skills", "__pycache__", ".git",
                ".venv", "node_modules", "_scratch"}
# Documented manual runbooks: imported by no one, run by hand. Orphan +
# undocumented fails; orphan + documented must be listed here. Adding a
# name is a human decision recorded in git, not a silent exemption.
MANUAL = {"final_graph_verify", "stage_corpus", "verify_graph_fixes"}


def target_files() -> list[Path]:
    out = []
    for d in SCAN_DIRS:
        p = ROOT / d
        if p.exists():
            out.extend(sorted(p.rglob("*.py")))
    for g in SCAN_ROOT_GLOBS:
        out.extend(sorted(ROOT.glob(g)))
    return [p for p in out
            if not any(part in EXCLUDE_DIRS for part in p.relative_to(ROOT).parts)]


def unused_imports(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    bound: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                bound[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue  # compiler flags, never referenced by name
            for a in node.names:
                if a.name != "*":
                    bound[a.asname or a.name] = node.lineno
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            pass
    # Attribute roots (e.g. `os` in `os.path`) appear as Name nodes too.
    return [f"{path.relative_to(ROOT)}:{ln}: unused import `{name}`"
            for name, ln in sorted(bound.items(), key=lambda kv: kv[1])
            if name not in used]


def is_entry_point(path: Path, tree: ast.AST) -> bool:
    src_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and any(
                isinstance(t, ast.Constant) and t.value == "__main__"
                for t in [node.left, *node.comparators]):
            return True
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            src_names.add(node.name)
    if "main" in src_names:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "argparse" in text or "sys.argv" in text:
            return True
    return False


def referenced_names() -> set[str]:
    """Module stems referenced by gate/contract/router files (by path)."""
    refs = set()
    for base in [ROOT / "scripts" / "quality_check.py",
                 ROOT / "skill_router.py",
                 ROOT / "pipeline" / "WORKFLOW.md",
                 ROOT / "skills" / "MANIFEST.md",
                 ROOT / "local_skills.md"]:
        if base.exists():
            text = base.read_text(encoding="utf-8", errors="ignore")
            for p in target_files():
                if p.stem in text:
                    refs.add(p.stem)
    # Every module imported anywhere in the scanned tree is referenced.
    for p in target_files():
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                refs.add(node.module.split(".")[-1])
            elif isinstance(node, ast.Import):
                for a in node.names:
                    refs.add((a.asname or a.name).split(".")[-1])
    return refs


def orphans() -> list[str]:
    refs = referenced_names()
    out = []
    for p in target_files():
        if p.stem in refs:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        if is_entry_point(p, tree):
            continue
        if p.stem in MANUAL:
            continue
        out.append(f"{p.relative_to(ROOT)}: orphan module (no importers, no CLI, unreferenced)")
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    findings = []
    for p in target_files():
        findings.extend(unused_imports(p))
    findings.extend(orphans())
    if findings:
        print("DEAD CODE:")
        for f in findings:
            print(f"  - {f}")
        return 1
    print(f"OK: no unused imports or orphan modules ({len(target_files())} files scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
