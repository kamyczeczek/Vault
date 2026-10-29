#!/usr/bin/env python3
"""Test that every non-system entry in ALLOWED_ROOT of check_workspace_integrity.py
is declared in CLAUDE.md's "Where things live" table as a table row entry (e.g. | `entry` |).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

# Import ALLOWED_ROOT from check_workspace_integrity.py
sys.path.insert(0, str(ROOT / "scripts"))
from check_workspace_integrity import ALLOWED_ROOT, VAULT_OWNED

def is_declared_in_claude_table(entry, claude_content):
    clean_entry = entry.strip('/')
    patterns = [
        f"| `{entry}` |",
        f"| `{clean_entry}/` |",
        f"| `{clean_entry}` |",
        f"| {entry} |",
        f"| {clean_entry}/ |",
    ]
    return any(p in claude_content for p in patterns)

def is_declared_as_vault_row(entry, claude_content):
    """Knowledge-layer entries (ADR-008) are declared as rows into `kb/`."""
    clean = entry.strip('/')
    return any(p in claude_content for p in (f"| `kb/{entry}` |", f"| `kb/{clean}/` |"))

def parity_ok(allowed_entries, claude_content, gitignore_content):
    system_entries = {
        "CLAUDE.md", "AGENTS.md", "projects", "skills", "CONTEXT-MAP.md",
        "TOOLS.md", "DECISIONS.md", "PHILOSOPHY.md", "TOKEN-EFFICIENCY.md",
        "GLOSSARY.md", "HANDOFF.md", ".ralph", "scripts", "kb",
        ".git", ".gitignore", ".gitattributes",
        ".agents", ".forge", "WORKFLOW_GOOSE_ICM.md", ".dgc-evidence",
        "STATE.md", "handoff", "docs", "tools", "agents", "hooks",
        "SCARS.md", ".pi", "logs",
    }
    runtime_entries = {
        "__pycache__",
    }
    new_entries = allowed_entries - system_entries
    for entry in new_entries:
        if entry in runtime_entries:
            # Runtime entries must be present in .gitignore
            if entry not in gitignore_content and f"{entry}/" not in gitignore_content:
                return False
        else:
            if not is_declared_in_claude_table(entry, claude_content):
                return False
    return True

def test_false_positive_brain():
    """Negative test: root brain/ must not pass if only projects/research/brain/ is present."""
    claude_content = """
| Path | Role | Description |
|---|---|---|
| `projects/research/brain/` | Project Brain | FTS5 corpus |
"""
    assert not parity_ok({"brain"}, claude_content, "")
    print("PASS: test_false_positive_brain correctly caught substring match!")

def test_parity():
    claude_md_path = ROOT / "CLAUDE.md"
    gitignore_path = ROOT / ".gitignore"

    claude_content = claude_md_path.read_text(encoding="utf-8")
    gitignore_content = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""

    system_entries = {
        "CLAUDE.md", "AGENTS.md", "projects", "skills", "CONTEXT-MAP.md",
        "TOOLS.md", "DECISIONS.md", "PHILOSOPHY.md", "TOKEN-EFFICIENCY.md",
        "GLOSSARY.md", "HANDOFF.md", ".ralph", "scripts", "kb",
        ".git", ".gitignore", ".gitattributes",
        ".agents", ".forge", "WORKFLOW_GOOSE_ICM.md", ".dgc-evidence",
        "STATE.md", "handoff", "docs", "tools", "agents", "hooks",
        "SCARS.md", ".pi", "logs",
    }
    runtime_entries = {
        "__pycache__",
    }

    new_entries = ALLOWED_ROOT - system_entries
    print(f"Checking new/additional ALLOWED_ROOT entries: {new_entries}")

    failed = []
    for entry in new_entries:
        if entry in runtime_entries:
            # Runtime entries must be in .gitignore
            if entry not in gitignore_content and f"{entry}/" not in gitignore_content:
                failed.append(entry)
                print(f"FAIL: Runtime ALLOWED_ROOT entry '{entry}' lacks .gitignore entry!")
            else:
                print(f"PASS: Runtime entry '{entry}' found in .gitignore")
        else:
            declared = is_declared_in_claude_table(entry, claude_content)
            if not declared:
                failed.append(entry)
                print(f"FAIL: Structural ALLOWED_ROOT entry '{entry}' lacks table row declaration in CLAUDE.md!")
            else:
                print(f"PASS: Structural entry '{entry}' found as table row in CLAUDE.md")

    for entry in sorted(VAULT_OWNED):
        if is_declared_as_vault_row(entry, claude_content):
            print(f"PASS: vault-owned entry '{entry}' declared as a `../` row in CLAUDE.md")
        else:
            failed.append(f"../{entry}")
            print(f"FAIL: vault-owned entry '{entry}' lacks a `../{entry}/` row in CLAUDE.md")

    if failed:
        print(f"\nERROR: {len(failed)} ALLOWED_ROOT entries lack CLAUDE.md table declaration: {failed}")
        raise SystemExit(1)

    print("\nSUCCESS: All ALLOWED_ROOT entries have CLAUDE.md table declarations.")


if __name__ == "__main__":
    test_false_positive_brain()
    test_parity()
