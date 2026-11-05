#!/usr/bin/env python3
"""close_session.py — session-end ritual: close the reflection loop.

Session transcript -> bounded .md (export_session_reflection.py)
                   -> agentmemory consolidation (engine REST :3111)
                   -> workspace gates (audit_workspace.py)

Stdlib only. Consolidation warnings never block (the engine is a runtime
service); export and gate failures do.

    python scripts/close_session.py                  # $PI_SESSION_FILE, tiers episodic,semantic
    python scripts/close_session.py --session PATH   # explicit transcript
    python scripts/close_session.py --no-gate        # skip the gate pass
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = "http://localhost:3111"


def resolve_session(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            sys.exit(f"FAIL: session file not found: {p}")
        return p
    env = os.environ.get("PI_SESSION_FILE")
    if env and Path(env).exists():
        return Path(env)
    # fallback: newest transcript under this project's pi session dir
    base = Path(os.path.expanduser("~")) / ".pi" / "agent" / "sessions"
    proj = [d for d in base.glob("*agentic-research-lab--") if d.is_dir()]
    if not proj:
        sys.exit("FAIL: no session file given and no pi session dir for this project found")
    files = [f for d in proj for f in d.glob("*.jsonl")]
    if not files:
        sys.exit(f"FAIL: no *.jsonl under {[str(d) for d in proj]}")
    newest = max(files, key=lambda f: f.stat().st_mtime)
    print(f"note: PI_SESSION_FILE unset; using newest project transcript: {newest}")
    return newest


def export(reflection: Path) -> bool:
    print(f"--- 1/3 export: {reflection.name} ---")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "export_session_reflection.py"), str(reflection)])
    return r.returncode == 0


def _engine_up() -> bool:
    s = socket.socket()
    try:
        s.settimeout(1)
        return s.connect_ex(("localhost", 3111)) == 0
    finally:
        s.close()


def consolidate(tiers: list[str]) -> bool:
    print(f"--- 2/3 consolidate: {', '.join(tiers)} ---")
    if not _engine_up():
        print(f"WARN: engine not listening on :3111 - consolidation skipped "
              f"(run scripts/restart_agentmemory.ps1, then re-run close_session.py)")
        return False
    ok = True
    for tier in tiers:
        body = json.dumps({"tier": tier}).encode()
        req = urllib.request.Request(f"{ENGINE}/agentmemory/consolidate", data=body,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                print(f"  {tier}: HTTP {resp.status} {resp.read().decode()[:200]}")
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  {tier}: WARN engine error ({e}) - not blocking")
            ok = False
    return ok


def gate() -> bool:
    print("--- 3/3 gate: audit_workspace.py ---")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_workspace.py")],
                       capture_output=True, text=True)
    tail = [ln for ln in r.stdout.splitlines() if ln.strip()][-3:]
    print("\n".join(tail))
    if r.returncode != 0:
        print("FAIL: workspace gate failed")
        print(r.stdout[-2000:])
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--session", help="explicit session .jsonl path (default: $PI_SESSION_FILE)")
    ap.add_argument("--no-gate", action="store_true", help="skip audit_workspace.py")
    ap.add_argument("--tiers", default="episodic,semantic",
                    help="comma-separated consolidation tiers (default: episodic,semantic)")
    ap.add_argument("--background-reflect", help="trigger background reflection spawn on session close for given topic")
    args = ap.parse_args()

    session = resolve_session(args.session)
    if not export(session):
        return 1
    tiers = [t.strip() for t in args.tiers.split(",") if t.strip()]
    consolidate(tiers)  # warnings only

    if args.background_reflect:
        print(f"--- background reflect: {args.background_reflect} ---")
        spawn_script = ROOT / "pipeline" / "06_reflect" / "spawn.py"
        subprocess.run([sys.executable, str(spawn_script), "--topic", args.background_reflect, "--background"])

    if args.no_gate:
        print("--- 3/3 gate skipped (--no-gate) ---")
        return 0
    return 0 if gate() else 1


if __name__ == "__main__":
    sys.exit(main())
