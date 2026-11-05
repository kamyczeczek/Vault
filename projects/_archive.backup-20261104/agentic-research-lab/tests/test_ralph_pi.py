"""Pi-backed Ralph phases: scripts/pi_ralph_worker.py / pi_ralph_reviewer.py.

These pin what the pi wrappers are for, and prove the loop still works when
the model sessions are pi sessions:

- the prompt travels in a file (`--append-system-prompt <path>`), never on
  the command line;
- fresh context is structural: `-p --no-session` in the argv, checked
  against argv, not source;
- a fake pi that only writes the state files proves the loop's control flow
  through the REAL pilot subprocess plumbing (split_command, run_phase,
  verdict-from-file) at zero model cost.

No test in this file launches a model or costs money. The fake-pi loops do
touch the gitignored `.goose/ralph/` scratch directory, exactly like the
repo's own e2e control-flow proofs.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ralph_pilot  # noqa: E402
import pi_ralph_worker  # noqa: E402
import pi_ralph_reviewer  # noqa: E402

FAKE_PI = """
import pathlib
import sys

args = sys.argv[1:]
prompt = pathlib.Path(args[args.index("--append-system-prompt") + 1]).read_text(encoding="utf-8")
sd = pathlib.Path(".goose") / "ralph"
mode = next(a for a in args if a in ("ship", "revise-then-ship", "fail"))
if "RALPH WORK PHASE" in prompt:
    (sd / "work-summary.txt").write_text("did work via fake pi", encoding="utf-8")
elif mode == "fail":
    sys.exit(3)
else:
    n = int((sd / "iteration.txt").read_text(encoding="utf-8").strip() or "1")
    if mode == "ship" or n > 1:
        (sd / "review-result.txt").write_text("SHIP", encoding="utf-8")
    else:
        (sd / "review-result.txt").write_text("REVISE", encoding="utf-8")
        (sd / "review-feedback.txt").write_text(
            "fake reviewer: one more iteration", encoding="utf-8")
"""


class PromptContractTests(unittest.TestCase):
    """What a pi session is told, for a state directory the loop produced."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        sd = self.root / ralph_pilot.STATE_DIR
        sd.mkdir(parents=True)
        (sd / "task.md").write_text("the fake task contract", encoding="utf-8")
        (sd / "iteration.txt").write_text("2", encoding="utf-8")
        (sd / "review-feedback.txt").write_text("fix the fake bug", encoding="utf-8")
        (sd / "work-summary.txt").write_text("the fake worker claim", encoding="utf-8")
        saved_root = ralph_pilot.ROOT
        ralph_pilot.ROOT = self.root
        self.addCleanup(setattr, ralph_pilot, "ROOT", saved_root)

    def test_worker_prompt_carries_the_task_and_the_output_contract(self) -> None:
        prompt = pi_ralph_worker.build_prompt(pi_ralph_worker.state_dir())
        for required in ("the fake task contract", "iteration 2",
                         "fix the fake bug", "work-summary.txt",
                         "work-complete.txt", "RALPH-BLOCKED.md"):
            self.assertIn(required, prompt, f"worker prompt missing {required!r}")
        self.assertIn(pi_ralph_worker.MARKER, prompt)

    def test_reviewer_prompt_labels_the_claim_as_evidence_not_truth(self) -> None:
        prompt = pi_ralph_reviewer.build_prompt(pi_ralph_reviewer.state_dir())
        for required in ("the fake task contract", "the fake worker claim",
                         "EVIDENCE, NOT TRUTH", "review-result.txt",
                         "review-feedback.txt", "SHIP", "REVISE"):
            self.assertIn(required, prompt, f"reviewer prompt missing {required!r}")
        self.assertIn(pi_ralph_reviewer.MARKER, prompt)

    def test_missing_task_is_a_loud_error_not_an_empty_prompt(self) -> None:
        (pi_ralph_worker.state_dir() / "task.md").unlink()
        with self.assertRaises(SystemExit):
            pi_ralph_worker.build_prompt(pi_ralph_worker.state_dir())


class ArgvContractTests(unittest.TestCase):
    """What one pi session looks like on the command line."""

    def test_fresh_context_is_structural_not_promised(self) -> None:
        argv = pi_ralph_worker.build_argv(["pi"], "", "", Path("p.md"))
        self.assertIn("-p", argv)
        self.assertIn("--no-session", argv)
        for flag in ("--resume", "--continue", "-r", "-c"):
            self.assertNotIn(flag, argv,
                             f"{flag} would let context survive the iteration")

    def test_absent_model_or_provider_omits_the_flag(self) -> None:
        argv = pi_ralph_reviewer.build_argv(["pi"], "", "", Path("p.md"))
        self.assertNotIn("--model", argv)
        self.assertNotIn("--provider", argv)

    def test_named_reviewer_model_is_cross_model_review(self) -> None:
        argv = pi_ralph_reviewer.build_argv(["pi"], "gpt-x", "openai", Path("p.md"))
        self.assertIn("gpt-x", argv)
        self.assertIn("openai", argv)

    def test_prompt_file_is_delivered_as_a_path_not_inline_text(self) -> None:
        argv = pi_ralph_worker.build_argv(["pi"], "", "", Path("p.md"))
        i = argv.index("--append-system-prompt")
        self.assertEqual(argv[i + 1], str(Path("p.md")))


class FakePiLoopTests(unittest.TestCase):
    """The full pilot, end-to-end, with a fake pi writing the state files.

    Zero model cost, zero money: the fake proves the control flow - the real
    pilot, the real split_command plumbing, the real verdict-from-file stop
    condition. What is NOT proven is that a real model reads the prompt
    correctly; that is the semantic handoff this repo's evidence says is
    not mechanically checkable.
    """

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.fake = self.tmp / "fake_pi.py"
        self.fake.write_text(FAKE_PI, encoding="utf-8")
        self._env = os.environ.pop("RALPH_PI_CMD", None)

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop("RALPH_PI_CMD", None)
        else:
            os.environ["RALPH_PI_CMD"] = self._env

    def run_loop(self, mode: str, max_iter: int, pi_cmd: str | None) -> tuple[int, str]:
        if pi_cmd is not None:
            os.environ["RALPH_PI_CMD"] = pi_cmd
        else:
            os.environ["RALPH_PI_CMD"] = (f'"{sys.executable}" "{self.fake}" {mode}')
        state = self.tmp / "STATE.md"
        cmd = [sys.executable, "scripts/ralph_pilot.py",
               "pi e2e control-flow proof",
               "--max", str(max_iter),
               "--state", str(state),
               "--worker", f'"{sys.executable}" scripts/pi_ralph_worker.py',
               "--reviewer", f'"{sys.executable}" scripts/pi_ralph_reviewer.py',
               "--no-cost-warning"]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr)

    def test_ship_on_first_review_exits_zero(self) -> None:
        code, out = self.run_loop("ship", 1, None)
        self.assertEqual(code, 0, out)
        self.assertIn("iteration 1: SHIP", out)
        complete = ROOT / ralph_pilot.STATE_DIR / ".ralph-complete"
        self.assertTrue(complete.is_file(), "SHIP must write .ralph-complete")
        state = (self.tmp / "STATE.md").read_text(encoding="utf-8")
        self.assertIn("- verdict: SHIP", state)

    def test_revise_then_ship_crosses_the_iteration_boundary(self) -> None:
        # Iteration 1 gets REVISED, iteration 2 ships: the only things a fresh
        # pi worker sees are task.md, iteration.txt and the git log.
        code, out = self.run_loop("revise-then-ship", 3, None)
        self.assertEqual(code, 0, out)
        self.assertIn("iteration 1: REVISE", out)
        self.assertIn("iteration 2: SHIP", out)
        it = (ROOT / ralph_pilot.STATE_DIR / "iteration.txt").read_text()
        self.assertEqual(it.strip(), "2")

    def test_crashing_reviewer_phase_stops_the_loop_honestly(self) -> None:
        code, out = self.run_loop("fail", 1, None)
        self.assertEqual(code, 1, out)
        self.assertIn("REVIEW PHASE FAILED", out)
        self.assertFalse((ROOT / ralph_pilot.STATE_DIR / ".ralph-complete").is_file())

    def test_unresolvable_pi_binary_is_a_work_phase_failure(self) -> None:
        pi_cmd = '"C:\\no-such-pi-binary\\pi.exe"'
        code, out = self.run_loop("ship", 1, pi_cmd)
        self.assertEqual(code, 1, out)
        self.assertIn("WORK PHASE FAILED", out)

    def test_missing_pi_command_line_errors_at_startup(self) -> None:
        # No pi on PATH and no RALPH_PI_CMD: a no-goose loop must not fail at
        # model resolution, it must name the missing binary.
        os.environ.pop("RALPH_PI_CMD", None)
        sd = ROOT / ralph_pilot.STATE_DIR
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "task.md").write_text("seed", encoding="utf-8")  # hermetic seed
        r = subprocess.run([sys.executable, "scripts/pi_ralph_worker.py"],
                           capture_output=True, text=True, cwd=ROOT,
                           env={**os.environ, "PATH": "C:\\nonexistent"})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("not found on PATH", r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
