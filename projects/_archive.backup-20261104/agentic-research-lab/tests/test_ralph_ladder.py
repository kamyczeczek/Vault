"""Contracts for the Ralph capability ladder.

The ladder replaces the abandoned c2 experiment. c2 tried to measure re-
orientation with a *second LLM* scoring a fresh worker's answer, and its blind
negative control scored 0.50 until the scorer was hand-edited. The graph
(`00_reflection_compaction_variance`) explains why: retained knowledge is
*variant across runs*, so that instrument tunes itself against its own
measurement.

The ladder's calibration claim is therefore the thing worth pinning: a worker
that claims success while doing nothing is **rejected deterministically**, with
no model in the loop. These tests check that property directly rather than
trusting the printed table.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ralph_ladder  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


class NoOpIsRejectedTests(unittest.TestCase):
    """The negative control, pinned as a control rather than as a claim.

    A blind control must be rejected for the right reason. This is the failure
    c2 exhibited: its control scored 0.50 because the scorer rewarded the right
    nouns in a wrong answer.
    """

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.repo = Path(self._td.name)
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "t@t")
        _git(self.repo, "config", "user.name", "t")
        (self.repo / "a.txt").write_text("original\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-qm", "base")

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_worker_that_does_nothing_produces_no_diff(self) -> None:
        # The worker claims success on stdout. Stdout is not a signal.
        r = subprocess.run([sys.executable, "-c",
                            "print('fixed it, everything is green')"],
                           cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertFalse(ralph_ladder.staged_change(self.repo),
                         "a no-op worker must be rejected")

    def test_worker_that_actually_edits_produces_a_diff(self) -> None:
        r = subprocess.run(
            [sys.executable, "-c",
             "import pathlib\n"
             "p = pathlib.Path('a.txt')\n"
             "p.write_text(p.read_text(encoding='utf-8') + 'edited\\n', "
             "encoding='utf-8')\n"],
            cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(ralph_ladder.staged_change(self.repo),
                        "a real edit must be attributable")

    def test_rejection_is_independent_of_what_the_worker_says(self) -> None:
        # A worker that loudly asserts completion and one that says nothing
        # must be judged identically. If the verdict moved with the wording,
        # the instrument would be scoring narration, which is c2's bug.
        quiet = subprocess.run([sys.executable, "-c", "pass"], cwd=self.repo,
                               capture_output=True, text=True)
        loud = subprocess.run(
            [sys.executable, "-c",
             "print('SUCCESS: all gates pass, the fix is complete and verified')\n"],
            cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(quiet.returncode, 0)
        self.assertEqual(loud.returncode, 0)
        self.assertFalse(ralph_ladder.staged_change(self.repo))


class LadderShapeTests(unittest.TestCase):
    """The ladder must not imply it reaches judgement work."""

    def test_rungs_are_declared_in_order(self) -> None:
        indices = [index for index, _, _, _ in ralph_ladder.RUNGS]
        self.assertEqual(indices, sorted(indices))
        self.assertEqual(indices, list(range(len(indices))))

    def test_every_rung_states_a_predicate(self) -> None:
        for index, name, predicate, fn in ralph_ladder.RUNGS:
            with self.subTest(rung=index):
                self.assertTrue(predicate.strip(),
                                f"rung {index} ({name}) has no predicate")
                self.assertTrue(callable(fn))

    def test_rung_two_label_matches_what_the_code_measures(self) -> None:
        """The rung-2 predicate is a *staged diff*, not HEAD movement.

        Measured defect: the label said "HEAD moved, so the iteration was
        real" while the implementation ran `git add -A` + `git diff --cached`.
        HEAD movement is strictly stronger (a worker that edits and reverts
        the same tree moves no HEAD but is still a real iteration; a worker
        that only stages a deletion-free no-op would move nothing). A label
        that overstates the measurement is a false claim, and the ladder's
        whole point is that it overclaims nothing.
        """
        label = dict((i, p) for i, _, p, _ in ralph_ladder.RUNGS)[2]
        self.assertNotIn("HEAD", label)
        self.assertIn("worktree changed", label)
        # and the label must be derived, not hand-maintained next to the code
        self.assertEqual("the worktree changed, so the iteration was real", label)

    def test_rung_three_declares_the_predicate_is_harness_written(self) -> None:
        """Rung 3's stated limitation, made checkable.

        Measured defect: rung 3 is described as "a human-written rule", but
        the ladder itself authors the rule (`MANUAL = {` -> insert the probe
        name) and then removes it. So the criterion is produced by the same
        program that measures it. That is a weaker experiment than the label
        implies, and the honest fix is to say so out loud rather than to
        quietly keep the strong wording.
        """
        source = (ROOT / "scripts" / "ralph_ladder.py").read_text(encoding="utf-8")
        self.assertIn("does NOT claim", source)
        self.assertIn("ladder writes it", source)
        # the rung must not claim the rule is human-authored
        label = dict((i, p) for i, _, p, _ in ralph_ladder.RUNGS)[3]
        self.assertNotIn("human-authored", label)

    def test_the_ceiling_is_declared_not_implied_away(self) -> None:
        # c3 (graph-based self-healing routing) supports the hybrid: deterministic
        # for known mechanical paths, LLM only for escalation. If the ladder
        # stopped at rung 3 without naming rung 4, it would imply rung 3 is
        # enough -- exactly the overclaim the evidence does not support.
        source = (ROOT / "scripts" / "ralph_ladder.py").read_text(encoding="utf-8")
        self.assertIn("rung 4", source)
        self.assertIn("Not automatable", source)

    def test_no_rung_claims_to_measure_understanding(self) -> None:
        # The c2 claim: a fresh session *understood* the state. The ladder must
        # not quietly re-import it.
        source = (ROOT / "scripts" / "ralph_ladder.py").read_text(encoding="utf-8")
        self.assertIn("does NOT claim", source)


class WorktreeHygieneTests(unittest.TestCase):
    """A measurement must not leave the repository dirtied."""

    def test_worktree_is_removed_even_when_the_body_fails(self) -> None:
        wt = ralph_ladder.Worktree()
        try:
            self.assertTrue((wt.path / "scripts").is_dir())
            wt.run("raise SystemExit(3)")
        finally:
            wt.close()
        self.assertFalse(wt.path.exists(), "throwaway worktree must be removed")
        listed = subprocess.run(["git", "worktree", "list"], cwd=ROOT,
                                capture_output=True, text=True).stdout
        self.assertNotIn(str(wt.path), listed, "worktree must be pruned from git")


if __name__ == "__main__":
    unittest.main()
