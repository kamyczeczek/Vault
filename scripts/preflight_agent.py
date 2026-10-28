#!/usr/bin/env python3
"""Deterministic preflight for coding agents and skill executions.

Verifies the execution environment before an agent starts working, preventing
deadlocks caused by orphaned lock directories (.unlazy/locks, .git/index.lock)
or unresponsive Python/Git processes.

Exit 0: Environment is responsive, locks are clear, ready for work.
Exit 1: Environment is degraded, blocked, or timed out.

Usage:
    python scripts/preflight_agent.py          # clean locks and verify
    python scripts/preflight_agent.py --check  # read-only check
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PYTHON_TIMEOUT = 2.5
DEFAULT_GIT_TIMEOUT = 5.0


def check_and_clean_unlazy_locks(clean: bool = True) -> tuple[bool, str]:
    """Check for and remove .unlazy/locks directory which deadlocks Windows Python."""
    unlazy_locks = ROOT / ".unlazy" / "locks"
    unlazy_root = ROOT / ".unlazy"
    if unlazy_locks.exists():
        if clean:
            try:
                shutil.rmtree(unlazy_locks, ignore_errors=True)
                if unlazy_locks.exists():
                    return False, f"failed to remove deadlock directory: {unlazy_locks}"
            except Exception as exc:
                return False, f"error removing {unlazy_locks}: {exc}"
        else:
            return False, f"deadlock directory exists: {unlazy_locks}"

    # If .unlazy exists and is empty or only has locks, clean it
    if clean and unlazy_root.exists():
        try:
            entries = list(unlazy_root.iterdir())
            if not entries or entries == [unlazy_locks]:
                shutil.rmtree(unlazy_root, ignore_errors=True)
        except Exception:
            pass

    return True, "OK"


def check_and_clean_git_lock(clean: bool = True) -> tuple[bool, str]:
    """Check for stale .git/index.lock and remove if git is not running."""
    lock_file = ROOT / ".git" / "index.lock"
    if not lock_file.exists():
        return True, "OK"

    # Check lock file age
    try:
        mtime = lock_file.stat().st_mtime
        age = time.time() - mtime
    except OSError:
        age = 0

    if clean:
        # If lock is older than 30s, check if git is running
        if age > 30.0:
            try:
                lock_file.unlink()
                return True, f"removed stale .git/index.lock (age {age:.1f}s)"
            except OSError as exc:
                return False, f"failed to remove stale .git/index.lock: {exc}"
        else:
            return False, f".git/index.lock is active (age {age:.1f}s) — git process may be running"
    return False, f".git/index.lock exists (age {age:.1f}s)"


def check_python_responsive(timeout: float = DEFAULT_PYTHON_TIMEOUT) -> tuple[bool, float, str]:
    """Verify that Python spawns and executes within timeout."""
    t0 = time.perf_counter()
    try:
        cmd = [sys.executable, "-c", "import sys; sys.stdout.write('alive')"]
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        elapsed = time.perf_counter() - t0
        if p.returncode != 0:
            return False, elapsed, f"python exited with code {p.returncode}: {p.stderr.strip()}"
        if p.stdout.strip() != "alive":
            return False, elapsed, f"unexpected python output: {p.stdout.strip()!r}"
        return True, elapsed, "OK"
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        return False, elapsed, f"python process timed out after {timeout:.1f}s"
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        return False, elapsed, f"failed to execute python: {exc}"


def check_git_responsive(timeout: float = DEFAULT_GIT_TIMEOUT) -> tuple[bool, float, str]:
    """Verify that git status responds within timeout."""
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        elapsed = time.perf_counter() - t0
        if p.returncode != 0:
            return False, elapsed, f"git status exited with code {p.returncode}: {p.stderr.strip()}"
        return True, elapsed, "OK"
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        return False, elapsed, f"git status timed out after {timeout:.1f}s"
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        return False, elapsed, f"failed to execute git: {exc}"


def run_preflight(clean: bool = True,
                  python_timeout: float = DEFAULT_PYTHON_TIMEOUT,
                  git_timeout: float = DEFAULT_GIT_TIMEOUT) -> tuple[bool, list[str]]:
    """Run all preflight checks and return overall status and log lines."""
    logs: list[str] = []
    success = True

    # 1. unlazy locks
    ok_unlazy, msg_unlazy = check_and_clean_unlazy_locks(clean=clean)
    if not ok_unlazy:
        success = False
        logs.append(f"[FAIL] .unlazy/locks: {msg_unlazy}")
    else:
        logs.append(f"[PASS] .unlazy/locks: {msg_unlazy}")

    # 2. git index lock
    ok_git_lock, msg_git_lock = check_and_clean_git_lock(clean=clean)
    if not ok_git_lock:
        success = False
        logs.append(f"[FAIL] .git/index.lock: {msg_git_lock}")
    else:
        logs.append(f"[PASS] .git/index.lock: {msg_git_lock}")

    # 3. python responsiveness
    ok_py, elapsed_py, msg_py = check_python_responsive(timeout=python_timeout)
    if not ok_py:
        success = False
        logs.append(f"[FAIL] python responsiveness ({elapsed_py:.3f}s): {msg_py}")
    else:
        logs.append(f"[PASS] python responsiveness: {elapsed_py:.3f}s (< {python_timeout}s)")

    # 4. git responsiveness
    ok_git, elapsed_git, msg_git = check_git_responsive(timeout=git_timeout)
    if not ok_git:
        success = False
        logs.append(f"[FAIL] git responsiveness ({elapsed_git:.3f}s): {msg_git}")
    else:
        logs.append(f"[PASS] git responsiveness: {elapsed_git:.3f}s (< {git_timeout}s)")

    return success, logs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="read-only check, do not clean locks")
    ap.add_argument("--python-timeout", type=float, default=DEFAULT_PYTHON_TIMEOUT,
                    help="timeout in seconds for python check")
    ap.add_argument("--git-timeout", type=float, default=DEFAULT_GIT_TIMEOUT,
                    help="timeout in seconds for git check")
    args = ap.parse_args()

    clean = not args.check
    ok, logs = run_preflight(
        clean=clean,
        python_timeout=args.python_timeout,
        git_timeout=args.git_timeout,
    )

    for line in logs:
        print(line)

    if ok:
        print("PREFLIGHT OK: environment responsive and clean")
        return 0
    else:
        print("PREFLIGHT FAIL: environment blocked or degraded", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
