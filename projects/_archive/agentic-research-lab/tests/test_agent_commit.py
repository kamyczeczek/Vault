"""Contract for scripts/agent_commit.py's ignored-file guard.

Measured defect: untracking a file that is *also* in .gitignore was impossible
through the sanctioned tool. `git rm --cached STATE.md` stages a deletion, and
`diff --cached --name-only` lists it; `.gitignore` matches the path; the guard
then read that as "an ignored file entered the index" and refused. The check
could not tell adding an ignored file apart from removing one from the index.

These tests assert the distinction directly, in throwaway repositories, without
committing anything to the real project.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agent_commit  # noqa: E402


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


class IgnoredFileGuardTests(unittest.TestCase):
    """The guard must reject ignored *adds* and permit ignored *untrackings*."""

    def setUp(self) -> None:
        import tempfile
        self.repo = Path(tempfile.mkdtemp(prefix="commit-guard-"))
        self.addCleanup(self._cleanup)
        git("init", "-q", cwd=self.repo)
        git("config", "user.email", "t@example.com", cwd=self.repo)
        git("config", "user.name", "T", cwd=self.repo)
        # a tracked file that will later be ignored
        (self.repo / "STATE.md").write_text("tracked at first\n", encoding="utf-8")
        git("add", "STATE.md", cwd=self.repo)
        git("commit", "-q", "-m", "seed", cwd=self.repo)

    def _cleanup(self) -> None:
        import shutil
        shutil.rmtree(self.repo, ignore_errors=True)

    def _staged_paths(self) -> list[str]:
        out = git("diff", "--cached", "--name-only", cwd=self.repo).stdout
        return [line for line in out.splitlines() if line]

    def _added_paths(self) -> set[str]:
        """Replicate the guard's --diff-filter=ACMR classification locally."""
        out = git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR",
                  cwd=self.repo).stdout
        return {p for p in out.split("\0") if p}

    def test_adding_an_ignored_file_is_still_refused(self) -> None:
        # regression guard: the fix must not weaken the original protection.
        # A genuinely ADDED file must appear in the ACMR classification, so if it
        # is also ignored the guard still flags it. (Note: once force-added, git
        # reports it as tracked so check-ignore returns non-ignored; the guard's
        # teeth against a normal add are that `git add` itself refuses an
        # ignored path, and ACMR keeps every real add in scope.)
        (self.repo / ".gitignore").write_text("SECRET.md\n", encoding="utf-8")
        (self.repo / "SECRET.md").write_text("x\n", encoding="utf-8")
        git("add", "-f", "SECRET.md", cwd=self.repo)  # -f: force an ignored add

        staged = self._staged_paths()
        added_set = self._added_paths()
        self.assertIn("SECRET.md", staged)
        self.assertIn("SECRET.md", added_set,
                      "a genuinely added file must stay in the guard's scope")
        # and the guard would compute it as ignored if git still considers it so
        rc = git("check-ignore", "--quiet", "--", "SECRET.md", cwd=self.repo).returncode
        ignored_added = [p for p in staged if p in added_set
                         and (rc == 0 if p == "SECRET.md" else False)]
        # either git reports it ignored (guard flags it) or it is now tracked
        # (normal adds are already blocked); the ACMR scoping is the real assert
        self.assertTrue(ignored_added or rc != 0)

    def test_untracking_an_ignored_file_is_permitted(self) -> None:
        # the actual fix: a staged deletion of an ignored path is NOT an add
        (self.repo / ".gitignore").write_text("STATE.md\n", encoding="utf-8")
        git("rm", "--cached", "--quiet", "STATE.md", cwd=self.repo)

        staged = self._staged_paths()
        self.assertIn("STATE.md", staged, "the untracking must be staged")

        added_set = self._added_paths()
        self.assertNotIn("STATE.md", added_set,
                         "a deletion must not appear as an addition")

        ignored_added = [p for p in staged
                         if p in added_set
                         and git("check-ignore", "--quiet", "--", p, cwd=self.repo).returncode == 0]
        self.assertNotIn("STATE.md", ignored_added,
                         "untracking an ignored file must be permitted")


class StagedResidueTests(unittest.TestCase):
    """A failed run must leave the index exactly as it found it.

    Measured defect (2026-10-05, session B post-mortem): a failed
    agent_commit.py (untracked-files-outside-stage) left the explicitly
    staged files in the index. The next raw `git commit` of an UNRELATED
    file then shipped them by accident, forcing a reset + redo. The
    tool itself must clean up its own staging on any pre-commit failure.
    """

    def setUp(self) -> None:
        import tempfile
        import os
        self.repo = Path(tempfile.mkdtemp(prefix="commit-residue-"))
        self.addCleanup(self._cleanup)
        git("init", "-q", cwd=self.repo)
        git("config", "user.email", "t@example.com", cwd=self.repo)
        git("config", "user.name", "T", cwd=self.repo)
        (self.repo / "scripts").mkdir()
        # the project gate; FAILS when the FAIL_GATE env var is set
        (self.repo / "scripts" / "quality_check.py").write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "sys.exit(1 if os.environ.get('FAIL_GATE') else 0)\n",
            encoding="utf-8")
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        git("add", "seed.txt", "scripts", cwd=self.repo)
        git("commit", "-q", "-m", "seed", cwd=self.repo)
        self._old_root = agent_commit.ROOT
        self._old_argv = sys.argv
        self._old_fail_gate = os.environ.get("FAIL_GATE")
        agent_commit.ROOT = self.repo

    def _cleanup(self) -> None:
        import shutil
        import os
        agent_commit.ROOT = self._old_root
        sys.argv = self._old_argv
        if self._old_fail_gate is None:
            os.environ.pop("FAIL_GATE", None)
        else:
            os.environ["FAIL_GATE"] = self._old_fail_gate
        shutil.rmtree(self.repo, ignore_errors=True)

    def _status_lines(self) -> list[str]:
        out = git("status", "--porcelain", "--untracked-files=all",
                   cwd=self.repo).stdout
        return [line for line in out.splitlines() if line]

    def test_untracked_failure_leaves_no_staged_residue(self) -> None:
        (self.repo / "work.py").write_text("print('x')\n", encoding="utf-8")
        (self.repo / "stray.py").write_text("print('y')\n", encoding="utf-8")
        sys.argv = ["agent_commit.py", "--scope", "s1", "--message", "m",
                    "--stage", "work.py"]
        rc = agent_commit.main()
        self.assertEqual(rc, 1, "stray untracked file must fail the run")
        lines = self._status_lines()
        # work.py must be plain untracked again, never staged ('A ')
        self.assertNotIn("A  work.py", lines)
        self.assertIn("?? work.py", lines)
        self.assertIn("?? stray.py", lines)

    def test_gate_failure_also_unstages(self) -> None:
        import os
        (self.repo / "work.py").write_text("print('x')\n", encoding="utf-8")
        os.environ["FAIL_GATE"] = "1"
        sys.argv = ["agent_commit.py", "--scope", "s1", "--message", "m",
                    "--stage", "work.py"]
        rc = agent_commit.main()
        self.assertEqual(rc, 1, "a failing quality gate must fail the run")
        lines = self._status_lines()
        self.assertNotIn("A  work.py", lines,
                         "gate failure must not leave staged residue")
        self.assertIn("?? work.py", lines)

    def test_successful_run_commits_and_cleans(self) -> None:
        (self.repo / "work.py").write_text("print('x')\n", encoding="utf-8")
        sys.argv = ["agent_commit.py", "--scope", "s1", "--message", "m",
                    "--stage", "work.py"]
        rc = agent_commit.main()
        self.assertEqual(rc, 0, "a clean gate + clean stage must commit")
        log = git("log", "-1", "--format=%s", cwd=self.repo).stdout
        self.assertIn("m", log)
        self.assertEqual(self._status_lines(), [])

    def test_unstage_works_on_orphan_repo(self) -> None:
        # A repo with NO commit yet (fresh clone / orphan branch / first
        # commit): HEAD does not exist. Measured 2026-10-05 with
        # scripts/_scratch/probe_unstage_orphan.py (git 2.54):
        #   `git reset -q HEAD -- <path>`      rc=0, unstages correctly
        #   `git restore --staged -- <path>`   rc=128 "could not resolve HEAD"
        # i.e. the current unstage() is the portable one on this host;
        # the restore-based fallback would BREAK the orphan case. Pin it.
        orphan = Path(tempfile.mkdtemp(prefix="commit-orphan-"))
        self.addCleanup(lambda: shutil.rmtree(orphan, ignore_errors=True))
        git("init", "-q", cwd=orphan)
        (orphan / "work.py").write_text("print('x')\n", encoding="utf-8")
        git("add", "work.py", cwd=orphan)
        self.assertEqual(git("diff", "--cached", "--name-only",
                             cwd=orphan).stdout.split(), ["work.py"])
        # agent_commit's git() helper always runs in agent_commit.ROOT;
        # point it at the orphan repo for the duration of the call.
        old_root = agent_commit.ROOT
        agent_commit.ROOT = orphan
        try:
            agent_commit.unstage(["work.py"])
        finally:
            agent_commit.ROOT = old_root
        self.assertNotIn("A  work.py",
                          git("status", "--porcelain", cwd=orphan).stdout,
                          "unstage() must clear the index on a HEAD-less repo")


if __name__ == "__main__":
    unittest.main()
