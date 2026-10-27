#!/usr/bin/env python3
"""Non-blocking PostToolUse telemetry hook.

Reads the runtime JSON payload from stdin and appends a bounded event to the
workspace event stream. It never blocks or changes tool results.
"""
from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "reflection" / "events.jsonl"

def main() -> int:
    try:
        raw = sys.stdin.read(64_000)
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {"parse_error": True}
    event = {
        "event": "post_tool_use",
        "t": time.time(),
        "tool": payload.get("tool_name") or payload.get("tool", "unknown"),
        "success": payload.get("success", payload.get("exit_code", 0) == 0),
    }
    try:
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        with EVENTS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
    except OSError:
        pass
    try:
        logger_script = ROOT / "scripts" / "provenance_logger.py"
        if logger_script.exists():
            subprocess.run(
                [
                    sys.executable,
                    str(logger_script),
                    "record-tool",
                    "--tool",
                    str(event["tool"]),
                    "--payload",
                    json.dumps(payload),
                    "--summary",
                    "ok" if event["success"] else "failed",
                ],
                cwd=ROOT,
                capture_output=True,
                timeout=5,
            )
    except Exception:
        pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
