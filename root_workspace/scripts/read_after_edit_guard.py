"""Read-After-Edit Enforcer — ensures every edit action on code/config files is followed by a read verification.

Selftest: python scripts/read_after_edit_guard.py --selftest
Check: python scripts/read_after_edit_guard.py --check
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER_LOG = ROOT / "handoff" / "audit" / "edit_read_tracker.json"

def record_edit(filepath: str) -> None:
    TRACKER_LOG.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if TRACKER_LOG.exists():
        try:
            data = json.loads(TRACKER_LOG.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data[filepath] = {"edited": True, "read_after": False}
    TRACKER_LOG.write_text(json.dumps(data, indent=2), encoding="utf-8")

def record_read(filepath: str) -> None:
    TRACKER_LOG.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if TRACKER_LOG.exists():
        try:
            data = json.loads(TRACKER_LOG.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    if filepath in data:
        data[filepath]["read_after"] = True
    else:
        data[filepath] = {"edited": False, "read_after": True}
    TRACKER_LOG.write_text(json.dumps(data, indent=2), encoding="utf-8")

def check_compliance() -> int:
    """Returns 0 if all edited files have been read after edit, 1 if any unread edit violation exists."""
    if not TRACKER_LOG.exists():
        return 0
    try:
        data = json.loads(TRACKER_LOG.read_text(encoding="utf-8"))
    except Exception:
        return 0

    violations = [fp for fp, state in data.items() if state.get("edited") and not state.get("read_after")]
    if violations:
        print("read_after_edit_guard: violation detected — files edited without subsequent read verification:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1
    return 0

def selftest():
    print("Running Read-After-Edit Guard selftest...")
    if TRACKER_LOG.exists():
        TRACKER_LOG.unlink()

    test_file = "scripts/dummy_test_file.py"
    record_edit(test_file)
    assert check_compliance() == 1, "Failed to detect edit without read!"

    record_read(test_file)
    assert check_compliance() == 0, "Failed to clear violation after read!"

    if TRACKER_LOG.exists():
        TRACKER_LOG.unlink()
    print("Read-After-Edit Guard selftest PASSED.")
    return True

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check" in sys.argv:
        sys.exit(check_compliance())
    else:
        print("Usage: python scripts/read_after_edit_guard.py [--selftest|--check]")
