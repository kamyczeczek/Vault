"""Stop Gate Enforcer — halts execution / blocks downstream actions when a stop condition or validation failure (exit code 2) is triggered.

Selftest: python scripts/stop_gate_guard.py --selftest
Check: python scripts/stop_gate_guard.py --check
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STOP_FLAG = ROOT / "handoff" / "flags" / ".stop_gate"

def check_stop_condition() -> int:
    """Checks if stop condition / stop flag exists.
    Returns 2 if stopped (Stop Gate active), 0 otherwise.
    """
    if STOP_FLAG.exists():
        print(f"stop_gate_guard: STOP GATE ACTIVE — stop flag found at {STOP_FLAG}.", file=sys.stderr)
        return 2
    return 0

def selftest():
    print("Running Stop Gate Guard selftest...")
    if STOP_FLAG.exists():
        STOP_FLAG.unlink()

    assert check_stop_condition() == 0, "Stop gate triggered when no flag exists!"

    # Adversarial test: simulate stop condition
    STOP_FLAG.parent.mkdir(parents=True, exist_ok=True)
    STOP_FLAG.write_text("stop condition triggered by test", encoding="utf-8")
    assert check_stop_condition() == 2, "Stop gate failed to trigger on stop flag!"

    STOP_FLAG.unlink()
    print("Stop Gate Guard selftest PASSED.")
    return True

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check" in sys.argv:
        sys.exit(check_stop_condition())
    else:
        print("Usage: python scripts/stop_gate_guard.py [--selftest|--check]")
