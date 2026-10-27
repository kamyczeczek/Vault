"""Standalone preflight for this project.

Answer for a cold agent: can work start here, in this tree, right now?
Checks local hard dependencies, then sibling links this project's docs
point at. Then the agentmemory layer (the .env LLM config and the engine),
so silent distillation failures surface at session start. Siblings live under ``$WORKSPACE_ROOT`` (default: this
project's parent directory, i.e. ``projects/research/``); two advisory links
reach one level above the siblings tree, at the workspace root.
Missing optional siblings degrade the project; missing hard files block
it.

    python preflight.py              # report + exit code
    WORKSPACE_ROOT=... preflight.py  # point at a different siblings tree
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIBLINGS = Path(os.environ.get("WORKSPACE_ROOT", ROOT.parent))
WORKSPACE = SIBLINGS.parent.parent

# (severity, path, why it matters). Only "hard" counts toward the exit code.
CHECKS: list[tuple[str, Path, str]] = [
    # Local — hard
    ("hard", ROOT / "CLAUDE.md", "entry file; cannot route without it"),
    ("hard", ROOT / "CONTEXT.md", "contract; root operating contract and chunk format"),
    ("hard", ROOT / "skills/MANIFEST.md", "stamp of the local skill factory; the local copy shadows the root"),
    ("hard", ROOT / "scripts/quality_check.py", "the gate runner: the 21 project gates"),
    ("hard", ROOT / "knowledge/graph/build_graph.py", "index construction for the derived brain"),
    # Root — optional (advisory; gate Q0 and the shared factory degrade, not block)
    ("optional", WORKSPACE / "scripts/check_workspace_integrity.py",
     "gate Q0 fails fast without it; all 21 project gates still run"),
    ("optional", WORKSPACE / "skills",
     "root shared factory; local skills/ shadows it, so purely advisory"),
]


def _shown(path: Path) -> str:
    for base in (ROOT, SIBLINGS, WORKSPACE):
        if path.is_relative_to(base):
            return str(path.relative_to(base))
    return str(path)


def agentmemory_checks() -> int:
    """Memory-layer preflight (scar 2026-09-30): catch the silent LLM
    failure modes at session start, not after 30 turns.

    Hard-missing: .env absent, model not served by the router.
    Advisory: engine down (close_session.py - its only caller - skips
    consolidation; run restart_agentmemory.ps1 before closing a session
    you want distilled), router unreachable.
    Returns the number of hard misses.
    """
    import json as _json
    import socket
    import urllib.request

    env_file = Path(os.path.expanduser("~")) / ".agentmemory" / ".env"
    hard = 0
    print("agentmemory layer:")

    if not env_file.exists():
        print(f"  [MISSING] hard {env_file}  (create: python scripts/configure_agentmemory_env.py)")
        hard += 1
    else:
        vars_: dict[str, str] = {}
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                vars_[k.strip()] = v.strip()
        model, base, key = vars_.get("OPENAI_MODEL", ""), vars_.get("OPENAI_BASE_URL", "").rstrip("/"), vars_.get("OPENAI_API_KEY", "")
        if not model:
            print(f"  [MISSING] hard {env_file} has no OPENAI_MODEL (distillation tiers would no-op)")
            hard += 1
        else:
            # Probe the router: configured provider != working provider.
            try:
                req = urllib.request.Request(base + "/models", headers={"Authorization": f"Bearer {key}"})
                ids = [m["id"] for m in _json.load(urllib.request.urlopen(req, timeout=10)).get("data", [])]
                if model in ids:
                    print(f"  [ok] model {model} served by router ({len(ids)} models listed)")
                else:
                    print(f"  [MISSING] hard OPENAI_MODEL={model} is NOT served by {base} -> LLM calls 404; "
                          f"re-run scripts/configure_agentmemory_env.py")
                    hard += 1
            except Exception:
                print(f"  [advisory] router {base} unreachable - model {model} unverified (offline?)")

    if socket.socket().connect_ex(("localhost", 3111)) == 0:
        print("  [ok] engine listening on :3111")
    else:
        print("  [advisory] engine not on :3111 - close_session.py will skip consolidation; "
              "run scripts/restart_agentmemory.ps1 before closing a session you want distilled")
    return hard


def background_reflection_checks() -> int:
    """Surface unconsumed background-reflection outcomes.

    A status file nobody reads is a failure nobody sees. A run that ended
    `failed`/`timeout`/`error` — or that is still `running` long after its PID
    died — is a hole in the reflection surface, and the session that created it
    has usually moved on. Reporting it at session start is what makes a silent
    failure surface at the *next* session instead of never.
    """
    logs = ROOT / "reflection" / "logs"
    if not logs.is_dir():
        return 0
    hard = 0
    for status_file in sorted(logs.glob("*.status.json")):
        try:
            status = json.loads(status_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print(f"  [MISSING] hard reflection/logs/{status_file.name} unreadable "
                  f"(worker was killed mid-write; artifacts need re-running)")
            hard += 1
            continue
        state = status.get("state")
        topic = status_file.stem.removesuffix(".status")
        if state in ("failed", "timeout", "error"):
            # A stale failure is not a current failure. The cause may have been
            # fixed since (a prompt change, a re-stamp), in which case blocking
            # forever would create pressure to delete the very evidence this
            # check exists to preserve. Re-grade the artifacts that run produced:
            # if they pass now, the failure is history, not a hole in the surface.
            resolved = _artifacts_now_pass(topic)
            if resolved is True:
                print(f"  [ok]    local reflection/logs/{status_file.name} stale {state}, "
                      f"artifacts re-grade OK — run again to clear")
                continue
            detail = status.get("gate") or status.get("reason") or status.get("error") or "see log"
            extra = "" if resolved is None else " (artifacts still fail the gate)"
            print(f"  [MISSING] hard reflection run `{topic}` ended {state} ({detail}){extra} — "
                  f"reflection/logs/{topic}.log")
            hard += 1
        elif state == "running":
            pid = status.get("pid")
            if pid and not _pid_alive(int(pid)):
                print(f"  [MISSING] hard reflection run `{topic}` is stuck in `running` "
                      f"(pid {pid} is gone) — artifacts need re-running")
                hard += 1
    return hard


def _artifacts_now_pass(topic: str) -> bool | None:
    """Re-grade one topic's artifacts with the same gate that failed them.

    Returns True when they now pass (the failure is stale), False when they
    still fail (a live hole), and None when there is nothing left to grade.
    Exit code 2 from check_reflection.py (SCOPE ERROR) means the topic has no
    artifacts in either the graded or scratch dirs — treat as nothing to grade,
    not as a failure.
    """
    try:
        res = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_reflection.py"), "--paths", topic],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
    except OSError:
        return None
    return True if res.returncode == 0 else (None if res.returncode == 2 else False)


def _pid_alive(pid: int) -> bool:
    if os.name == "nt":
        res = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, text=True, check=False)
        return str(pid) in res.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def ralph_mode_hint() -> None:
    """Display-only: ralph-loop is this project's default work mode (2026-10-02).

    Prints the active run's state so a cold session sees the loop ritual at
    session start. Never affects the preflight exit code.
    """
    state_path = ROOT / ".ralph" / "STATE.json"
    if not state_path.exists():
        print("  [ralph] no active run - init one before substantial work "
              "(skills/ralph-loop, default work mode per CLAUDE.md)")
        return
    import json as _json
    state = _json.loads(state_path.read_text(encoding="utf-8"))
    run_name = str(state.get("run", "?")).replace(".ralph\\runs\\", "").replace(".ralph/runs/", "")
    print(f"  [ralph] active run {run_name}: {state.get('status', '?')} | iter {state.get('iteration', 0)} | "
          f"frontier {state.get('next_frontier') or '-'} | handoff {state.get('handoff_at') or 'never stamped'}")
    print("  [ralph] default work mode - session ritual: python skills/ralph-loop/scripts/ralph.py --project . resume")


def main() -> int:
    missing = 0
    for severity, path, why in CHECKS:
        ok = path.exists()
        base = "local" if path.is_relative_to(ROOT) else "ext  "
        print(f"  [{'ok' if ok else 'MISSING'}] {base} {_shown(path)}  ({why})")
        if not ok and severity == "hard":
            missing += 1
    missing += agentmemory_checks()
    missing += background_reflection_checks()
    ralph_mode_hint()
    verdict = "NOT READY" if missing else "READY"
    print(f"agentic-research-lab preflight: {verdict} ({missing} hard missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
