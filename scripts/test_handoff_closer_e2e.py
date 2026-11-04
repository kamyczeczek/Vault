#!/usr/bin/env python3
"""Hermetic end-to-end test for handoff-closer workflow on a dirty tree.

Verifies:
1. Dirty tree detection: uncommitted tracked changes outside --include block close.
2. Partial include: changes not covered by --include are flagged as strays.
3. Dry-run validation: clean pass when all modified tracked files are included.
4. Full transaction execution: flag writing, views rebuilding, integrity check,
   token approval, git commit, and clean post-close working tree.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOSE_PY = ROOT / "scripts" / "close.py"


class HandoffCloserE2ETest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp(prefix="closer-e2e-")
        self.repo = Path(self.td)
        self._setup_repo()

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def _run_git(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
            check=True,
        )

    def _setup_repo(self):
        self._run_git(["init", "-q", "-b", "master"])
        self._run_git(["config", "user.email", "closer-test@example.com"])
        self._run_git(["config", "user.name", "Closer Test"])

        # Directory structure
        (self.repo / "handoff" / "flags").mkdir(parents=True)
        (self.repo / "handoff" / "status").mkdir(parents=True)
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "docs").mkdir(parents=True)

        # Initial generated views and files
        (self.repo / "HANDOFF.md").write_text("# HANDOFF\n", encoding="utf-8")
        (self.repo / "STATE.md").write_text("# STATE\n", encoding="utf-8")
        (self.repo / "handoff" / "flags" / "INDEX.md").write_text("# INDEX\n", encoding="utf-8")
        (self.repo / "handoff" / "status" / "STATUS.md").write_text("# STATUS\n", encoding="utf-8")
        (self.repo / "handoff" / "flags" / "seed-flag.md").write_text("---\nflag: seed-flag\n---\n`seed-flag`\nnot checked: -\n", encoding="utf-8")

        # Tracked project files
        (self.repo / "src" / "worker.py").write_text("def work(): pass\n", encoding="utf-8")
        (self.repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")

        # Mock generators for views and integrity gate
        build_handoff = self.repo / "scripts" / "build_handoff.py"
        build_handoff.write_text(
            "import sys\nfrom pathlib import Path\n"
            "root = Path(__file__).resolve().parent.parent\n"
            "(root / 'HANDOFF.md').write_text('# HANDOFF (rebuilt)\\n', encoding='utf-8')\n"
            "(root / 'handoff' / 'flags' / 'INDEX.md').write_text('# INDEX (rebuilt)\\n', encoding='utf-8')\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        build_state = self.repo / "scripts" / "build_state.py"
        build_state.write_text(
            "import sys\nfrom pathlib import Path\n"
            "root = Path(__file__).resolve().parent.parent\n"
            "(root / 'STATE.md').write_text('# STATE (rebuilt)\\n', encoding='utf-8')\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        build_status = self.repo / "scripts" / "build_status.py"
        build_status.write_text(
            "import sys\nfrom pathlib import Path\n"
            "root = Path(__file__).resolve().parent.parent\n"
            "(root / 'handoff' / 'status' / 'STATUS.md').write_text('# STATUS (rebuilt)\\n', encoding='utf-8')\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        gate = self.repo / "scripts" / "check_workspace_integrity.py"
        gate.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")

        # Copy actual close.py and its git_paths.py dependency
        shutil.copy(CLOSE_PY, self.repo / "scripts" / "close.py")
        shutil.copy(ROOT / "scripts" / "git_paths.py", self.repo / "scripts" / "git_paths.py")

        # Initial commit
        self._run_git(["add", "-A"])
        self._run_git(["commit", "-m", "initial repo state"])

    def test_full_handoff_closer_lifecycle_on_dirty_tree(self):
        # 1. Dirty the tree with controlled changes
        (self.repo / "src" / "worker.py").write_text("def work(): return 42\n", encoding="utf-8")
        (self.repo / "docs" / "guide.md").write_text("# Updated Guide\nNew details.\n", encoding="utf-8")

        status = self._run_git(["status", "--porcelain"]).stdout
        self.assertIn("M docs/guide.md", status)
        self.assertIn("M src/worker.py", status)

        # Flag body file
        flag_body = (
            "`e2e-closer-flag` — 2026-11-04: Full E2E closer test on dirty tree.\n"
            "not checked: —\n"
        )
        body_file = self.repo / "body.txt"
        body_file.write_text(flag_body, encoding="utf-8")

        # 2. Test dry-run with NO includes -> MUST fail on strays
        p_dry_no_inc = subprocess.run(
            [sys.executable, "scripts/close.py", "--flag", "e2e-closer-flag",
             "--model", "test/provider-v1", "--body-file", "body.txt", "--dry-run"],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        self.assertEqual(p_dry_no_inc.returncode, 1)
        self.assertIn("uncommitted tracked work", p_dry_no_inc.stdout)
        self.assertIn("docs/guide.md", p_dry_no_inc.stdout)
        self.assertIn("src/worker.py", p_dry_no_inc.stdout)

        # 3. Test dry-run with PARTIAL include -> MUST fail with remaining stray
        p_dry_partial = subprocess.run(
            [sys.executable, "scripts/close.py", "--flag", "e2e-closer-flag",
             "--model", "test/provider-v1", "--body-file", "body.txt", "--dry-run",
             "--include", "src/worker.py"],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        self.assertEqual(p_dry_partial.returncode, 1)
        self.assertIn("uncommitted tracked work", p_dry_partial.stdout)
        self.assertIn("docs/guide.md", p_dry_partial.stdout)
        self.assertNotIn("src/worker.py", p_dry_partial.stdout)

        # 4. Test dry-run with ALL modified files included -> MUST PASS
        p_dry_full = subprocess.run(
            [sys.executable, "scripts/close.py", "--flag", "e2e-closer-flag",
             "--model", "test/provider-v1", "--body-file", "body.txt", "--dry-run",
             "--include", "src/worker.py", "docs/guide.md"],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        self.assertEqual(p_dry_full.returncode, 0, p_dry_full.stdout + p_dry_full.stderr)
        self.assertIn("dry-run OK", p_dry_full.stdout)

        # 5. Execute FULL close transaction
        p_close = subprocess.run(
            [sys.executable, "scripts/close.py", "--flag", "e2e-closer-flag",
             "--model", "test/provider-v1", "--body-file", "body.txt",
             "--include", "src/worker.py", "docs/guide.md"],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        self.assertEqual(p_close.returncode, 0, p_close.stdout + p_close.stderr)
        self.assertIn("committed `e2e-closer-flag` — session closed", p_close.stdout)

        # 6. Verify artifacts and post-close state
        flag_file = self.repo / "handoff" / "flags" / "e2e-closer-flag.md"
        self.assertTrue(flag_file.exists())
        flag_content = flag_file.read_text(encoding="utf-8")
        self.assertIn("flag: e2e-closer-flag", flag_content)
        self.assertIn("model: test/provider-v1", flag_content)
        self.assertIn("not checked: —", flag_content)

        # Generated views rebuilt
        self.assertIn("rebuilt", (self.repo / "HANDOFF.md").read_text(encoding="utf-8"))
        self.assertIn("rebuilt", (self.repo / "STATE.md").read_text(encoding="utf-8"))
        self.assertIn("rebuilt", (self.repo / "handoff" / "flags" / "INDEX.md").read_text(encoding="utf-8"))
        self.assertIn("rebuilt", (self.repo / "handoff" / "status" / "STATUS.md").read_text(encoding="utf-8"))

        # .commit-approved cleaned up
        self.assertFalse((self.repo / ".commit-approved").exists())

        # Clean working tree (except untracked body.txt which wasn't part of repo)
        status_after = self._run_git(["status", "--porcelain"]).stdout
        tracked_changes = [line for line in status_after.splitlines() if not line.startswith("??")]
        self.assertEqual(tracked_changes, [], f"Tracked dirty files remain: {tracked_changes}")

        # Git log check: HEAD is the close commit
        last_commit_msg = self._run_git(["log", "-1", "--pretty=%s"]).stdout.strip()
        self.assertTrue(last_commit_msg.startswith("e2e-closer-flag: `e2e-closer-flag`"))


if __name__ == "__main__":
    unittest.main()
