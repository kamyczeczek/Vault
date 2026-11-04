#!/usr/bin/env python3
"""Tests for scripts/preflight_agent.py."""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.preflight_agent as pfa


class PreflightAgentTests(unittest.TestCase):
    def test_normal_run_passes(self):
        with mock.patch.object(pfa, "check_and_clean_unlazy_locks", return_value=(True, "OK")), \
             mock.patch.object(pfa, "check_and_clean_git_lock", return_value=(True, "OK")), \
             mock.patch.object(pfa, "check_git_hooks", return_value=(True, "HOOK_ACTIVE (core.hooksPath='hooks')")), \
             mock.patch.object(pfa, "check_python_responsive", return_value=(True, 0.05, "OK")), \
             mock.patch.object(pfa, "check_git_responsive", return_value=(True, 0.05, "OK")):
            ok, logs = pfa.run_preflight(clean=False)
            self.assertTrue(ok)
            self.assertTrue(any("python responsiveness" in line for line in logs))
            self.assertTrue(any("git responsiveness" in line for line in logs))
            self.assertTrue(all("[PASS]" in line for line in logs))

    def test_run_preflight_fails_when_check_fails(self):
        with mock.patch.object(pfa, "check_and_clean_unlazy_locks", return_value=(True, "OK")), \
             mock.patch.object(pfa, "check_and_clean_git_lock", return_value=(True, "OK")), \
             mock.patch.object(pfa, "check_git_hooks", return_value=(False, "HOOK_INACTIVE")), \
             mock.patch.object(pfa, "check_python_responsive", return_value=(True, 0.05, "OK")), \
             mock.patch.object(pfa, "check_git_responsive", return_value=(True, 0.05, "OK")):
            ok, logs = pfa.run_preflight(clean=False)
            self.assertFalse(ok)
            self.assertTrue(any("[FAIL] git hooks: HOOK_INACTIVE" in line for line in logs))

    def test_unlazy_locks_cleaned_when_clean_true(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            locks = root / ".unlazy" / "locks"
            locks.mkdir(parents=True)
            lock_file = locks / "deadlock.lock"
            lock_file.write_text("lock", encoding="utf-8")

            # Set mtime to 100s in the past (stale)
            past = time.time() - 100.0
            os.utime(lock_file, (past, past))

            with mock.patch.object(pfa, "ROOT", root):
                self.assertTrue(locks.exists())
                ok, msg = pfa.check_and_clean_unlazy_locks(clean=True)
                self.assertTrue(ok)
                self.assertFalse(locks.exists())

    def test_unlazy_locks_retained_when_fresh(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            locks = root / ".unlazy" / "locks"
            locks.mkdir(parents=True)
            lock_file = locks / "active.lock"
            lock_file.write_text("lock", encoding="utf-8")

            # Lock is brand new (age ~0s <= 30s)
            with mock.patch.object(pfa, "ROOT", root):
                ok, msg = pfa.check_and_clean_unlazy_locks(clean=True)
                self.assertFalse(ok)
                self.assertIn("recent", msg)
                self.assertTrue(lock_file.exists())

    def test_unlazy_locks_retained_when_pid_running(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            locks = root / ".unlazy" / "locks"
            locks.mkdir(parents=True)
            lock_file = locks / "process.filelock"
            lock_file.write_text('{"token": "abc", "pid": 4321}', encoding="utf-8")

            # Set mtime to 100s in the past, but process is running
            past = time.time() - 100.0
            os.utime(lock_file, (past, past))

            with mock.patch.object(pfa, "ROOT", root):
                ok, msg = pfa.check_and_clean_unlazy_locks(clean=True, pid_running_check=lambda pid: pid == 4321)
                self.assertFalse(ok)
                self.assertIn("owner PID 4321 is still running", msg)
                self.assertTrue(lock_file.exists())

    def test_unlazy_locks_cleaned_when_pid_dead(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            locks = root / ".unlazy" / "locks"
            locks.mkdir(parents=True)
            lock_file = locks / "process.filelock"
            lock_file.write_text('{"token": "abc", "pid": 4321}', encoding="utf-8")

            past = time.time() - 100.0
            os.utime(lock_file, (past, past))

            with mock.patch.object(pfa, "ROOT", root):
                ok, msg = pfa.check_and_clean_unlazy_locks(clean=True, pid_running_check=lambda pid: False)
                self.assertTrue(ok)
                self.assertFalse(locks.exists())

    def test_unlazy_locks_reported_when_clean_false(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            locks = root / ".unlazy" / "locks"
            locks.mkdir(parents=True)

            with mock.patch.object(pfa, "ROOT", root):
                ok, msg = pfa.check_and_clean_unlazy_locks(clean=False)
                self.assertFalse(ok)
                self.assertIn("deadlock directory exists", msg)

    def test_stale_git_lock_cleaned(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            git_dir = root / ".git"
            git_dir.mkdir(parents=True)
            lock_file = git_dir / "index.lock"
            lock_file.write_text("", encoding="utf-8")

            # Set mtime to 100s in the past
            past = time.time() - 100.0
            os.utime(lock_file, (past, past))

            with mock.patch.object(pfa, "ROOT", root):
                with mock.patch.object(pfa, "is_git_process_running", return_value=False):
                    ok, msg = pfa.check_and_clean_git_lock(clean=True)
                    self.assertTrue(ok)
                    self.assertIn("removed stale", msg)
                    self.assertFalse(lock_file.exists())

    def test_stale_git_lock_retained_when_git_running(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            git_dir = root / ".git"
            git_dir.mkdir(parents=True)
            lock_file = git_dir / "index.lock"
            lock_file.write_text("", encoding="utf-8")

            # Set mtime to 100s in the past
            past = time.time() - 100.0
            os.utime(lock_file, (past, past))

            with mock.patch.object(pfa, "ROOT", root):
                with mock.patch.object(pfa, "is_git_process_running", return_value=True):
                    ok, msg = pfa.check_and_clean_git_lock(clean=True)
                    self.assertFalse(ok)
                    self.assertIn("git process is running", msg)
                    self.assertTrue(lock_file.exists())

    def test_git_lock_reported_when_clean_false(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            git_dir = root / ".git"
            git_dir.mkdir(parents=True)
            lock_file = git_dir / "index.lock"
            lock_file.write_text("", encoding="utf-8")

            # Even if old, clean=False should not delete it
            past = time.time() - 100.0
            os.utime(lock_file, (past, past))

            with mock.patch.object(pfa, "ROOT", root):
                ok, msg = pfa.check_and_clean_git_lock(clean=False)
                self.assertFalse(ok)
                self.assertIn("--clean-stale-locks", msg)
                self.assertTrue(lock_file.exists())

    def test_fresh_git_lock_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            git_dir = root / ".git"
            git_dir.mkdir(parents=True)
            lock_file = git_dir / "index.lock"
            lock_file.write_text("", encoding="utf-8")

            now = time.time()
            with mock.patch.object(pfa, "ROOT", root):
                with mock.patch.object(pfa, "is_git_process_running", return_value=False):
                    with mock.patch("time.time", return_value=now + 5.0):
                        ok, msg = pfa.check_and_clean_git_lock(clean=True)
                        self.assertFalse(ok)
                        self.assertIn("recent", msg)
                        self.assertTrue(lock_file.exists())

    def test_check_git_hooks_active(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            hooks_dir = root / "hooks"
            hooks_dir.mkdir(parents=True)
            (hooks_dir / "pre-commit").write_text("#!/bin/sh\nexit 0", encoding="utf-8")

            fake_cp = mock.Mock(returncode=0, stdout="hooks\n")
            with mock.patch("subprocess.run", return_value=fake_cp):
                ok, msg = pfa.check_git_hooks(root=root)
                self.assertTrue(ok)
                self.assertIn("HOOK_ACTIVE", msg)

    def test_check_git_hooks_inactive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake_cp = mock.Mock(returncode=1, stdout="")
            with mock.patch("subprocess.run", return_value=fake_cp):
                ok, msg = pfa.check_git_hooks(root=root)
                self.assertFalse(ok)
                self.assertIn("HOOK_INACTIVE", msg)
                self.assertIn("git config core.hooksPath hooks", msg)

    def test_check_git_hooks_inactive_when_not_executable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            hooks_dir = root / "hooks"
            hooks_dir.mkdir(parents=True)
            (hooks_dir / "pre-commit").write_text("#!/bin/sh\nexit 0", encoding="utf-8")

            fake_cp = mock.Mock(returncode=0, stdout="hooks\n")
            with mock.patch("subprocess.run", return_value=fake_cp):
                # When executable check returns False
                ok, msg = pfa.check_git_hooks(root=root, is_executable=lambda p: False)
                self.assertFalse(ok)
                self.assertIn("HOOK_INACTIVE", msg)
                self.assertIn("not executable", msg)


if __name__ == "__main__":
    unittest.main()
