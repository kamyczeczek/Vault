#!/usr/bin/env python3
"""check_wiring.py — verify claimed integrations are actually functional.

Catches cargo-cult completions: docs say "wired" but the wiring is
missing, dead, or only partial.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

FAILS: list[str] = []


def check_import_call(source: str, module: str, func: str) -> bool:
    """Return True if `func` from `module` is called in `source`."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            for alias in node.names:
                if alias.name == func or (func == "*" and alias.name):
                    return True
        if isinstance(node, ast.Call):
            callee = node.func
            if isinstance(callee, ast.Attribute) and callee.attr == func:
                return True
            if isinstance(callee, ast.Name) and callee.id == func:
                return True
    return False


def check_inspect_pdf_wired() -> None:
    src = (SCRIPTS / "ingest.py").read_text(encoding="utf-8")
    if "inspect_pdf" not in src:
        FAILS.append("inspect_pdf not referenced in ingest.py")
    if not check_import_call(src, "inspect_pdf", "inspect_pdf"):
        FAILS.append("inspect_pdf function not imported/called in ingest.py")


def check_audit_candidate_wired() -> None:
    src = (SCRIPTS / "check_reflection.py").read_text(encoding="utf-8")
    if "audit_claim_grounding" not in src:
        FAILS.append("audit_claim_grounding not referenced in check_reflection.py")
    if not check_import_call(src, "audit_candidate", "audit_claim_grounding"):
        FAILS.append("audit_claim_grounding not actually called in check_reflection.py")


def check_expand_topic_removed() -> None:
    if (SCRIPTS / "expand_topic.py").exists():
        FAILS.append("expand_topic.py still exists (consolidation incomplete)")


def check_git_tools_wired() -> None:
    for script in ["git_rollback.py", "git_worktree.py"]:
        src = (SCRIPTS / script).read_text(encoding="utf-8")
        if "def main" not in src:
            FAILS.append(f"{script} missing def main")


def check_review_gate_wired() -> None:
    src = (SCRIPTS / "review_gate.py").read_text(encoding="utf-8")
    if "def main" not in src:
        FAILS.append("review_gate.py missing def main")
    refs = sum(1 for p in SCRIPTS.glob("*.py") if p.name != "review_gate.py" and "review_gate" in p.read_text(encoding="utf-8", errors="ignore"))
    if refs == 0:
        FAILS.append("review_gate.py has zero external callers")


def check_skill_router_consistent() -> None:
    src = (ROOT / "skill_router.py").read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        FAILS.append("skill_router.py has syntax error")
        return
    router_values = set()
    routed_keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for val in node.values:
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    router_values.add(val.value)
        if isinstance(node, ast.FunctionDef) and node.name == "select_skill_for_step":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Return) and sub.value is not None:
                    v = sub.value
                    if isinstance(v, ast.Subscript) and isinstance(v.slice, ast.Constant) and isinstance(v.slice.value, str):
                        routed_keys.add(v.slice.value)
                    elif isinstance(v, ast.Constant) and isinstance(v.value, str):
                        routed_keys.add(v.value)
    required_routable = {
        "tdd", "git-guardrails-claude-code", "icm-architect",
        "agent-reach", "code-review", "research",
        "diagnosing-bugs",
        "to-tickets", "domain-modeling",
        "triage", "grill-with-docs", "unlazy",
        "implement", "prototype", "improve-codebase-architecture",
    }
    # Retired 2026-09-27: `wizard` and `resolving-merge-conflicts` were
    # archived upstream and dropped from routing (see skills/MANIFEST.md).
    # The retirement is locked here: re-adding a route must delete these
    # lines deliberately, not slip in unnoticed.
    retired = {"wizard", "resolving-merge-conflicts"}
    missing = required_routable - router_values
    if missing:
        FAILS.append(f"skill_router.py missing entries for: {sorted(missing)}")
    unreachable = required_routable - routed_keys
    if unreachable:
        FAILS.append(f"skill_router.py select_skill_for_step missing routing branches for: {sorted(unreachable)}")
    resurrected = retired & router_values
    if resurrected:
        FAILS.append(f"skill_router.py re-adds retired skills: {sorted(resurrected)}")


def check_apply_meta_learning_targets() -> None:
    src = (SCRIPTS / "apply_meta_learning.py").read_text(encoding="utf-8")
    if 'target in {"general", "multi-agent"}' not in src:
        FAILS.append("apply_meta_learning.py missing general/multi-agent target branch")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify claimed integrations are actually functional")
    parser.parse_args()

    check_inspect_pdf_wired()
    check_audit_candidate_wired()
    check_expand_topic_removed()
    check_git_tools_wired()
    check_review_gate_wired()
    check_skill_router_consistent()
    check_apply_meta_learning_targets()

    if FAILS:
        print("WIRING FAIL:")
        for msg in FAILS:
            print(f"  - {msg}")
        return 1
    print("OK: all claimed integrations are functionally wired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
