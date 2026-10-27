#!/usr/bin/env python3
"""Tests for the PreToolUse evidence guard and the scoped-gate contract.

Run: python scripts/check_evidence_guard.py

These are behavioural tests. Each one asserts the decision a hook makes for a
real command, because a guard that is never exercised is indistinguishable from
a guard that does not exist — the same "configured != verified" trap that
produced this check in the first place.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "hook_guard_evidence.py"
FAILS: list[str] = []


def decide(command: str, tool: str = "Bash") -> str:
    """Ask the hook what it would do with this command."""
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"tool_name": tool, "tool_input": {"command": command}}),
        capture_output=True, text=True, cwd=str(ROOT), check=False,
    )
    if not proc.stdout.strip():
        return "ALLOW"
    payload = json.loads(proc.stdout).get("hookSpecificOutput", {})
    return payload.get("permissionDecision", "ALLOW")


def expect(label: str, command: str, want: str, tool: str = "Bash") -> None:
    got = decide(command, tool)
    if got != want:
        FAILS.append(f"{label}: want {want}, got {got} — $ {command}")


def check_guard() -> None:
    """Destructive commands against graded evidence must be refused."""
    expect("fatal command from 2026-09-30",
           "rm -f reflection/digests/bg-smoke* reflection/candidates/bg-smoke* reflection/logs/bg-smoke*",
           "deny")
    expect("recursive wipe of digests", "rm -rf reflection/digests/", "deny")
    expect("PowerShell removal", "Remove-Item -Recurse -Force reflection/candidates/bg-smoke2.jsonl",
           "deny", tool="PowerShell")
    expect("truncation in place", "truncate reflection/candidates/bg-smoke4.jsonl", "deny")
    expect("windows separators", r"del reflection\candidates\bg-smoke4.jsonl", "deny")
    expect("globbed snapshot wipe", "rm -rf reflection/.snapshots/*", "deny")
    expect("empty the candidates dir", "rmdir reflection/candidates", "deny")
    expect("absolute path form",
           f'rm -f "{ROOT / "reflection" / "digests" / "x.md"}"', "deny")
    # Critical source-of-truth dirs: recursive deletion is blocked
    expect("recursive wipe of scripts/", "rm -rf scripts/", "deny")
    expect("recursive wipe of knowledge/", "rm -rf knowledge/", "deny")
    expect("recursive wipe of pipeline/", "rm -rf pipeline/", "deny")
    expect("recursive wipe of INBOX/", "rm -rf INBOX/", "deny")
    expect("recursive wipe of stages/", "rm -rf stages/", "deny")
    expect("PowerShell recursive wipe of knowledge/", "Remove-Item -Recurse -Force knowledge/",
           "deny", tool="PowerShell")


def check_allowed() -> None:
    """Everything the guard must not block, or it gets disabled and protects nothing."""
    # Force-only (non-recursive) single-file deletion of critical dirs is allowed
    expect("force-only single-file delete in scripts/", "rm -f scripts/foo.py", "ALLOW")
    expect("force-only PowerShell delete in scripts/", "Remove-Item -Force scripts/foo.py",
           "ALLOW", tool="PowerShell")
    expect("scoped gate is read-only", "python scripts/check_reflection.py --paths bg-smoke4", "ALLOW")
    expect("unscoped gate", "python scripts/check_reflection.py", "ALLOW")
    expect("temp cleanup", "rm -f /tmp/bs4.bak", "ALLOW")
    expect("logs are runtime telemetry", "rm -f reflection/logs/bg-smoke3.log", "ALLOW")
    expect("scratch dir", "rm -f scripts/_scratch/probe.txt", "ALLOW")
    expect("writing new artifacts is the job",
           "python pipeline/06_reflect/spawn.py --topic newtopic --background", "ALLOW")
    expect("reading a digest", "cat reflection/digests/bg-smoke4.md", "ALLOW")
    expect("other tools are not intercepted", "rm -rf /tmp/build", "ALLOW", tool="Read")
    expect("noisy but harmless listing", "ls reflection/digests/", "ALLOW")


def check_hook_contract() -> None:
    """A guard that crashes open is worse than no guard."""
    proc = subprocess.run([sys.executable, str(HOOK)], input="not json at all",
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0 or proc.stdout.strip():
        FAILS.append("malformed hook payload must exit 0 with no decision (fail open, no crash)")
    proc = subprocess.run([sys.executable, str(HOOK)], input="",
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        FAILS.append("empty hook payload must exit 0")


def check_scoped_gate() -> None:
    """--paths must grade the named artifacts and reject an empty scope."""
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_reflection.py"),
                           "--paths", "no-such-topic-xyz"], capture_output=True, text=True,
                          cwd=str(ROOT), check=False)
    if proc.returncode == 0:
        FAILS.append("--paths with no matching artifact must not report OK")
    if "SCOPE ERROR" not in (proc.stdout + proc.stderr):
        FAILS.append("--paths with no matching artifact must say why")


def check_snapshot_recovery() -> None:
    """A graded artifact deleted by any route stays recoverable from the snapshot."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "probe.jsonl"
        src.write_text('{"id":"probe"}\n', encoding="utf-8")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "snapshot_graded.py"),
                               "--paths", str(src), "--label", "selftest"],
                              capture_output=True, text=True, cwd=str(ROOT), check=False)
        if proc.returncode != 0:
            FAILS.append(f"snapshot_graded.py failed on a readable file: {proc.stderr[:200]}")
            return
        snapshots = sorted((ROOT / "reflection" / ".snapshots").glob("*selftest*"))
        if not snapshots:
            FAILS.append("snapshot_graded.py wrote no snapshot directory")
            return
        recovered = snapshots[-1] / "probe.jsonl"
        src.unlink()  # the deletion the guard exists to make recoverable
        if not recovered.exists() or recovered.read_text(encoding="utf-8") != '{"id":"probe"}\n':
            FAILS.append("snapshot did not preserve a recoverable copy of the artifact")
        else:
            subprocess.run(["rm", "-rf", str(snapshots[-1])], capture_output=True, check=False)


def check_preflight_regrade() -> None:
    """A stale failure whose artifacts now pass the gate must clear preflight.

    Regression test: a 0-vs-True identity bug once kept a passing gate from
    clearing a failed status. The fix was to return `True` explicitly, not `0`.
    """
    import importlib
    sys.path.insert(0, str(ROOT))
    try:
        import preflight as pf
        importlib.reload(pf)
    except ImportError:
        FAILS.append("preflight.py not importable — cannot verify _artifacts_now_pass return type")
        return
    for topic in ("bg-smoke3", "smoke-scratch-02"):
        result = pf._artifacts_now_pass(topic)
        if result is not None and not isinstance(result, bool):
            FAILS.append(f"_artifacts_now_pass({topic!r}) returned {type(result).__name__} — "
                         f"must be bool (True/False/None), not int. The 0-vs-True trap.")


def main() -> int:
    for fn in (check_guard, check_allowed, check_hook_contract, check_scoped_gate,
               check_snapshot_recovery, check_preflight_regrade):
        fn()
    if FAILS:
        for f in FAILS:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("OK: evidence guard, scoped gate, and snapshot recovery all behave as specified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
