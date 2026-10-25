"""Self-Modification Audit Guard — logs and audits modifications to sensitive workspace configuration and scripts.

Selftest: python scripts/self_modification_audit.py --selftest
Check staged: python scripts/self_modification_audit.py --check-staged
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SENSITIVE_PATHS = {
    "hooks", "scripts/commit_gate_guard.py", "scripts/root_deletion_guard.py",
    "scripts/stop_gate_guard.py", "scripts/read_after_edit_guard.py",
    "scripts/self_modification_audit.py", "AGENTS.md", "CLAUDE.md"
}

def check_path_sensitive(target_path: str | Path) -> bool:
    resolved = Path(target_path).resolve()
    try:
        rel = resolved.relative_to(ROOT.resolve())
    except ValueError:
        return False

    rel_str = str(rel).replace("\\", "/")
    for p in SENSITIVE_PATHS:
        if rel_str == p or rel_str.startswith(p + "/"):
            return True
    return False

def check_staged() -> int:
    """Scan `git diff --cached --name-status` for modifications to sensitive guard/config files.
    Logs any modification to handoff/audit/self-modifications.log and audits them.
    """
    p = subprocess.run(["git", "diff", "--cached", "--name-status"],
                       capture_output=True, text=True, cwd=str(ROOT))
    if p.returncode != 0:
        print(f"self_modification_audit: git diff --cached failed: {p.stderr.strip()}",
              file=sys.stderr)
        return 1

    modified: list[str] = []
    for line in p.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = parts[1] if status.startswith("R") else parts[-1]
        if check_path_sensitive(ROOT / path):
            modified.append(f"{status}\t{path}")

    if modified:
        audit_log_dir = ROOT / "handoff" / "audit"
        audit_log_dir.mkdir(parents=True, exist_ok=True)
        audit_log = audit_log_dir / "self-modifications.log"
        with audit_log.open("a", encoding="utf-8") as f:
            for m in modified:
                f.write(f"SENSITIVE_MODIFICATION: {m}\n")
        print("self_modification_audit: detected modifications to sensitive workspace guard/config files:", file=sys.stderr)
        for m in modified:
            print(f"  {m}", file=sys.stderr)
        print(f"Logged to handoff/audit/self-modifications.log. (Audited successfully)", file=sys.stderr)
    return 0

def selftest():
    print("Running Self-Modification Audit Guard selftest...")
    assert check_path_sensitive(ROOT / "scripts" / "commit_gate_guard.py"), "Failed to detect sensitive script!"
    assert check_path_sensitive(ROOT / "AGENTS.md"), "Failed to detect AGENTS.md!"
    assert not check_path_sensitive(ROOT / "projects" / "foo.txt"), "Incorrectly flagged non-sensitive file!"
    print("Self-Modification Audit Guard selftest PASSED.")
    return True

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check-staged" in sys.argv:
        sys.exit(check_staged())
    else:
        print("Usage: python scripts/self_modification_audit.py [--selftest|--check-staged]")
