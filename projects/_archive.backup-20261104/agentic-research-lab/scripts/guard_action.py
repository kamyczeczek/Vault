#!/usr/bin/env python3
"""Deterministic guard for agent actions and side-effect evidence.

No model calls. Intended for hooks and CI.

Examples:
  python scripts/guard_action.py check-command --command "git add ."
  python scripts/guard_action.py check-command --command "rm -rf /tmp/x"
  python scripts/guard_action.py verify-file --path reflection/memory.md --sha256 HASH
  python scripts/guard_action.py check-budget --steps 11 --max-steps 10
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "reflection" / "events.jsonl"

# Explicitly blocked regardless of agent intent. Safer alternatives require a human.
BLOCKED_PATTERNS = [
    (r"\bgit\s+(add\s+(-A|--all|\.)|reset\s+--hard|clean\s+-[a-z]*f|push\s+--force)", "destructive or unscoped git command"),
    (r"\b(rm|rmdir|del|format)\s+(-[a-z]+\s+)?(/|[A-Za-z]:\\|\$HOME|~)(?:\s|$)", "destructive root/home filesystem command"),
    (r"\b(curl|wget|invoke-webrequest)\b[^\n]*(?:\||;|&&)\s*(?:sh|bash|powershell|cmd)\b", "download-and-execute command"),
    (r"\b(chmod\s+777|sudo\s+|curl[^\n]*\|\s*sudo)", "privilege escalation or unsafe permissions"),
]

HIGH_RISK_PATTERNS = [
    (r"\b(git\s+push|deploy|publish|npm\s+publish|docker\s+push)\b", "external publication/deployment"),
    (r"\b(rm|rmdir|del|format|drop\s+database|truncate)\b", "destructive operation"),
    (r"\b(secret|token|password|api[_-]?key|credential)\b", "credential-sensitive operation"),
]


def classify(command: str) -> dict:
    findings = []
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.I):
            findings.append({"level": "block", "reason": reason, "pattern": pattern})
    for pattern, reason in HIGH_RISK_PATTERNS:
        if re.search(pattern, command, re.I) and not any(f["pattern"] == pattern for f in findings):
            findings.append({"level": "approval", "reason": reason, "pattern": pattern})
    level = "block" if any(f["level"] == "block" for f in findings) else ("approval" if findings else "allow")
    return {"decision": level, "command": command, "findings": findings}


def verify_file(path: str, expected: str) -> dict:
    target = (ROOT / path).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return {"verified": False, "reason": "path outside workspace"}
    if not target.is_file():
        return {"verified": False, "reason": "file does not exist", "path": path}
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"verified": actual == expected, "path": path, "expected": expected, "actual": actual}


def log(event: dict) -> None:
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="op", required=True)
    c = sub.add_parser("check-command"); c.add_argument("--command", required=True); c.add_argument("--log", action="store_true")
    v = sub.add_parser("verify-file"); v.add_argument("--path", required=True); v.add_argument("--sha256", required=True)
    b = sub.add_parser("check-budget"); b.add_argument("--steps", type=int, required=True); b.add_argument("--max-steps", type=int, required=True); b.add_argument("--retries", type=int, default=0); b.add_argument("--max-retries", type=int, default=3)
    args = p.parse_args()
    if args.op == "check-command":
        result = classify(args.command)
        if args.log: log({"event": "action_guard", **result})
        print(json.dumps(result, indent=2)); return 1 if result["decision"] == "block" else (2 if result["decision"] == "approval" else 0)
    if args.op == "verify-file":
        result = verify_file(args.path, args.sha256); print(json.dumps(result, indent=2)); return 0 if result["verified"] else 1
    if args.op == "check-budget":
        ok = args.steps <= args.max_steps and args.retries <= args.max_retries
        result = {"allowed": ok, "steps": args.steps, "max_steps": args.max_steps, "retries": args.retries, "max_retries": args.max_retries}
        print(json.dumps(result, indent=2)); return 0 if ok else 1
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
