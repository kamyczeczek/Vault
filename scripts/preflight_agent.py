#!/usr/bin/env python3
"""Deterministic preflight for coding agents and skill executions.

Verifies the execution environment before an agent starts working, preventing
deadlocks caused by orphaned lock directories (.unlazy/locks, .git/index.lock),
unresponsive Python/Git processes, or unconfigured repository git hooks.

Exit 0: Environment is responsive, locks are clear, hooks active, ready for work.
Exit 1: Environment is degraded, blocked, or timed out.

Usage:
    python scripts/preflight_agent.py                      # read-only check (default)
    python scripts/preflight_agent.py --clean-stale-locks  # clean stale locks and verify
    python scripts/preflight_agent.py --check              # read-only check (alias)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PYTHON_TIMEOUT = 2.5
DEFAULT_GIT_TIMEOUT = 5.0
DEFAULT_STALE_LOCK_AGE = 30.0


def is_pid_running(pid: int) -> bool:
    """Check if a process with given PID is currently running."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists, but caller lacks permission to signal it
        return True
    except OSError:
        return False


def check_and_clean_unlazy_locks(
    clean: bool = False,
    pid_running_check: callable | None = None,
    stale_age: float = DEFAULT_STALE_LOCK_AGE,
    root: Path | None = None,
) -> tuple[bool, str]:
    """Check for and remove stale .unlazy/locks directory which deadlocks Windows Python.

    In clean mode, verifies each lock file's age (> stale_age) and ensures any recorded
    owner PID in JSON metadata is no longer running before removal.
    """
    base = root if root is not None else ROOT
    unlazy_locks = base / ".unlazy" / "locks"
    unlazy_root = base / ".unlazy"
    if not unlazy_locks.exists():
        return True, "OK"

    try:
        entries = list(unlazy_locks.iterdir())
    except OSError as exc:
        return False, f"cannot read {unlazy_locks}: {exc}"

    if not clean:
        count = len(entries)
        return False, (
            f"deadlock directory exists: {unlazy_locks} "
            f"({count} lock(s) present — run with --clean-stale-locks to remove if stale)"
            if count
            else f"deadlock directory exists: {unlazy_locks} (run with --clean-stale-locks to remove)"
        )

    # clean=True: inspect and verify individual lock entries
    if not entries:
        try:
            unlazy_locks.rmdir()
            if unlazy_root.exists() and not list(unlazy_root.iterdir()):
                unlazy_root.rmdir()
            return True, f"removed empty deadlock directory: {unlazy_locks}"
        except OSError as exc:
            return False, f"failed to remove empty deadlock directory {unlazy_locks}: {exc}"

    pid_check = pid_running_check if pid_running_check is not None else is_pid_running

    removed: list[str] = []
    for entry in entries:
        try:
            mtime = entry.stat().st_mtime
            age = time.time() - mtime
        except OSError:
            age = 0.0

        # Inspect JSON lock metadata for owner PID
        owner_pid: int | None = None
        if entry.is_file():
            try:
                data = json.loads(entry.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    p = data.get("pid")
                    if isinstance(p, int):
                        owner_pid = p
            except Exception:
                pass

        if owner_pid is not None and pid_check(owner_pid):
            return False, f"lock '{entry.name}' owner PID {owner_pid} is still running — refusing to remove"

        if age <= stale_age:
            return False, f"lock '{entry.name}' is recent (age {age:.1f}s <= {stale_age:.0f}s) — refusing to remove as stale"

        try:
            if entry.is_file():
                entry.unlink()
            elif entry.is_dir():
                shutil.rmtree(entry, ignore_errors=False)
            removed.append(entry.name)
        except OSError as exc:
            return False, f"failed to remove lock '{entry.name}': {exc}"

    try:
        if not list(unlazy_locks.iterdir()):
            unlazy_locks.rmdir()
        if unlazy_root.exists() and not list(unlazy_root.iterdir()):
            unlazy_root.rmdir()
        return True, f"removed {len(removed)} stale lock(s) and directory: {unlazy_locks}"
    except OSError as exc:
        return False, f"failed to remove directory {unlazy_locks} after cleaning locks: {exc}"


def is_git_process_running() -> bool:
    """Check if any git process is currently running on the system."""
    try:
        if os.name == "nt":
            p = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq git.exe", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=3.0,
            )
            return "git.exe" in p.stdout.lower()
        else:
            try:
                p = subprocess.run(
                    ["pgrep", "-x", "git"],
                    capture_output=True,
                    timeout=3.0,
                )
                return p.returncode == 0
            except FileNotFoundError:
                p = subprocess.run(
                    ["ps", "-A", "-o", "comm="],
                    capture_output=True,
                    text=True,
                    timeout=3.0,
                )
                commands = {line.strip() for line in p.stdout.splitlines()}
                return "git" in commands
    except Exception:
        # If process check fails or times out, err on side of caution
        return True


def check_and_clean_git_lock(clean: bool = False,
                             git_running_check: callable | None = None) -> tuple[bool, str]:
    """Check for .git/index.lock and remove if clean=True, age > 30s, and git is not running."""
    lock_file = ROOT / ".git" / "index.lock"
    if not lock_file.exists():
        return True, "OK"

    # Check lock file age
    try:
        mtime = lock_file.stat().st_mtime
        age = time.time() - mtime
    except OSError:
        age = 0.0

    if not clean:
        return False, f".git/index.lock exists (age {age:.1f}s) — run with --clean-stale-locks to remove if stale"

    # clean=True: verify git process is not running
    git_running = git_running_check() if git_running_check is not None else is_git_process_running()
    if git_running:
        return False, f".git/index.lock exists (age {age:.1f}s) and git process is running — refusing to remove"

    if age <= 30.0:
        return False, f".git/index.lock is recent (age {age:.1f}s <= 30s) — refusing to remove as stale"

    try:
        lock_file.unlink()
        return True, f"removed stale .git/index.lock (age {age:.1f}s, git process not running)"
    except OSError as exc:
        return False, f"failed to remove stale .git/index.lock: {exc}"


def check_git_hooks(root: Path = ROOT,
                    is_executable: callable | None = None) -> tuple[bool, str]:
    """Check if repository pre-commit hook is active (core.hooksPath configured and executable on Unix)."""
    try:
        p = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=DEFAULT_GIT_TIMEOUT,
        )
        hooks_path = p.stdout.strip()
        if p.returncode == 0 and hooks_path:
            hook_file = (root / hooks_path / "pre-commit") if not Path(hooks_path).is_absolute() else (Path(hooks_path) / "pre-commit")
            if hook_file.exists():
                check_x = is_executable if is_executable is not None else (lambda p: os.access(p, os.X_OK))
                if os.name != "nt" or is_executable is not None:
                    if not check_x(hook_file):
                        return False, f"HOOK_INACTIVE ({hook_file} is not executable; run: chmod +x {hook_file})"
                return True, f"HOOK_ACTIVE (core.hooksPath='{hooks_path}')"
            return False, f"HOOK_INACTIVE (core.hooksPath='{hooks_path}' set, but {hook_file} does not exist)"
        return False, "HOOK_INACTIVE (core.hooksPath not configured; run: git config core.hooksPath hooks)"
    except Exception as exc:
        return False, f"HOOK_INACTIVE (error checking git hooks: {exc})"


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


def run_preflight(clean: bool = False,
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

    # 3. git hook configuration
    ok_hook, msg_hook = check_git_hooks()
    if not ok_hook:
        success = False
        logs.append(f"[FAIL] git hooks: {msg_hook}")
    else:
        logs.append(f"[PASS] git hooks: {msg_hook}")

    # 4. python responsiveness
    ok_py, elapsed_py, msg_py = check_python_responsive(timeout=python_timeout)
    if not ok_py:
        success = False
        logs.append(f"[FAIL] python responsiveness ({elapsed_py:.3f}s): {msg_py}")
    else:
        logs.append(f"[PASS] python responsiveness: {elapsed_py:.3f}s (< {python_timeout}s)")

    # 5. git responsiveness
    ok_git, elapsed_git, msg_git = check_git_responsive(timeout=git_timeout)
    if not ok_git:
        success = False
        logs.append(f"[FAIL] git responsiveness ({elapsed_git:.3f}s): {msg_git}")
    else:
        logs.append(f"[PASS] git responsiveness: {elapsed_git:.3f}s (< {git_timeout}s)")

    return success, logs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clean-stale-locks", "--clean", action="store_true",
                    dest="clean", default=False,
                    help="clean stale locks (.unlazy/locks, aged .git/index.lock)")
    ap.add_argument("--check", action="store_true",
                    help="read-only check (default behavior)")
    ap.add_argument("--python-timeout", type=float, default=DEFAULT_PYTHON_TIMEOUT,
                    help="timeout in seconds for python check")
    ap.add_argument("--git-timeout", type=float, default=DEFAULT_GIT_TIMEOUT,
                    help="timeout in seconds for git check")
    args = ap.parse_args()

    clean = args.clean and not args.check
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
