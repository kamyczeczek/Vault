"""Root Deletion Guard — prevents unauthorized deletion of workspace root entries (S32, S37).

Selftest: python scripts/root_deletion_guard.py --selftest
Staged check: python scripts/root_deletion_guard.py --check-staged
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTECTED_ROOT_ENTRIES = {
    "projects", "skills", "scripts", "hooks", "docs", "tools", "handoff",
    "CLAUDE.md", "AGENTS.md", "CONTEXT-MAP.md", "TOOLS.md", "DECISIONS.md"
}

def check_path_safe(target_path: str | Path) -> bool:
    resolved = Path(target_path).resolve()
    try:
        rel = resolved.relative_to(ROOT.resolve())
    except ValueError:
        return True # Outside workspace root

    parts = rel.parts
    if len(parts) == 1 and parts[0] in PROTECTED_ROOT_ENTRIES:
        return False
    return True

def check_staged() -> int:
    """Scan `git diff --cached --name-status` for deletions of protected root entries.

    Read-only: it never stages, unstages or touches the working tree, so it is
    safe to call from a pre-commit hook. A deletion of a protected root entry
    is what S32/S37 are about: the root is the workspace's contract, and a
    commit that removes an entry silently rewrites it for every later reader.

    Returns 0 when the index is clean of such deletions, 1 otherwise.
    """
    p = subprocess.run(["git", "diff", "--cached", "--name-status"],
                       capture_output=True, text=True, cwd=str(ROOT))
    if p.returncode != 0:
        print(f"root_deletion_guard: git diff --cached failed: {p.stderr.strip()}",
              file=sys.stderr)
        return 1
    violations: list[str] = []
    for line in p.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        # Rename records carry two paths (old, new); the deleted side is old.
        path = parts[1] if status.startswith("R") else parts[-1]
        if not status.startswith("D"):
            continue
        if not check_path_safe(ROOT / path):
            violations.append(f"{status}\t{path}")
    if violations:
        print("root_deletion_guard: staged deletion of a protected workspace "
              "root entry (S32, S37):", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print("Root entries are the workspace contract. Restore it, or get "
              "explicit owner approval recorded in the commit body.",
              file=sys.stderr)
        return 1
    return 0


def selftest():
    print("Running Root Deletion Guard selftest...")
    assert not check_path_safe(ROOT / "projects"), "Failed to protect projects root entry!"
    assert not check_path_safe(ROOT / "CLAUDE.md"), "Failed to protect CLAUDE.md!"
    assert check_path_safe(ROOT / "projects" / "research" / "knowledge-retrieval" / "foo.txt"), "Incorrectly blocked child path!"
    print("Root Deletion Guard selftest PASSED.")
    return True

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check-staged" in sys.argv:
        sys.exit(check_staged())
    else:
        print("Usage: python scripts/root_deletion_guard.py [--selftest|--check-staged]")
