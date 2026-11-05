"""Contracts for the scoped Ralph-loop pilot.

Human-authored. Each test pins a defect that was measured in this repo, not a
behaviour the code happens to have:

- the pilot's docstring advertised `--state STATE.md` and the parser had no such
  option, so the documented invocation died in argparse;
- `write_state()` counted *list elements*, not rendered lines, so a multiline
  gate failure blew the 60-line cap and the assert fired after the loop had
  already lost its state file;
- a worker command string was handed to `subprocess.run` without `shell=True`,
  producing a Windows `WinError 2` instead of running anything;
- the worker wrote to the pilot's own stdout, so worker narration landed in the
  loop log and made it unfalsifiable;
- "every iteration is a commit" was a docstring claim with no implementation.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ralph_pilot  # noqa: E402


class StateBoundTests(unittest.TestCase):
    """The cap is a contract on rendered lines, not on characters."""

    def test_multiline_failure_cannot_exceed_the_line_cap(self) -> None:
        # The regression that killed the abandoned branch: 1200 characters of
        # newline-separated failure comfortably exceeded 60 rendered lines.
        gate_excerpt = "\n".join(
            f"  - scripts/mod{i}.py:{i}: unused import X{i}" for i in range(400))
        with tempfile.TemporaryDirectory() as td:
            state = Path(td) / "STATE.md"
            rendered = ralph_pilot.write_state(state, 1, "red", gate_excerpt, "")
            self.assertLessEqual(rendered, ralph_pilot.STATE_MAX_LINES)
            self.assertEqual(
                len(state.read_text(encoding="utf-8").splitlines()),
                rendered,
                "write_state must report the count it actually wrote")

    def test_clamp_keeps_short_output_intact(self) -> None:
        self.assertEqual(ralph_pilot.clamp_lines("one\ntwo"), "one\ntwo")

    def test_clamp_bounds_lines_not_characters(self) -> None:
        clamped = ralph_pilot.clamp_lines(
            "\n".join(str(i) for i in range(1000)), budget=20)
        self.assertLessEqual(len(clamped.splitlines()), 20)
        self.assertIn("truncated", clamped)


class CliContractTests(unittest.TestCase):
    """What the docstring advertises, the parser must accept."""

    def test_documented_state_flag_is_accepted(self) -> None:
        code, out = ralph_pilot.sh([sys.executable, "scripts/ralph_pilot.py",
                                    "--state", "STATE.md", "--dry-run"])
        self.assertNotIn("unrecognized arguments", out)
        self.assertNotIn("invalid choice", out)
        # --dry-run returns the gate verdict; 0 and 1 are both legitimate.
        self.assertIn(code, (0, 1))

    def test_quoted_windows_worker_path_becomes_argv(self) -> None:
        # A bare string would become argv[0] and raise WinError 2. The first
        # fix (shlex posix=False) preserved the quotes and failed the same way;
        # that regression is pinned here rather than left to memory.
        parts = ralph_pilot.split_command(
            f'"{sys.executable}" "C:\\tmp\\a b.py" --flag')
        self.assertEqual(parts[0], sys.executable)
        self.assertEqual(parts[1], "C:\\tmp\\a b.py")
        self.assertEqual(parts[2], "--flag")
        self.assertEqual(len(parts), 3)

    def test_unquoted_worker_path_is_split(self) -> None:
        parts = ralph_pilot.split_command("python scripts/fix.py")
        self.assertEqual(parts, ["python", "scripts/fix.py"])

    def test_empty_worker_command_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ralph_pilot.split_command("   ")


class CommitAttributionTests(unittest.TestCase):
    """A correctness gate cannot tell a real iteration from a no-op."""

    def test_no_op_iteration_is_not_committable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            for args in (["git", "init", "-q"],
                         ["git", "config", "user.email", "t@t"],
                         ["git", "config", "user.name", "t"]):
                subprocess.run(args, cwd=repo, check=True, capture_output=True)
            (repo / "a.txt").write_text("x", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True,
                           capture_output=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True,
                           capture_output=True)

            original_root = ralph_pilot.ROOT
            ralph_pilot.ROOT = repo
            try:
                no_change, reason = ralph_pilot.commit_iteration("iter 1")
                (repo / "a.txt").write_text("y", encoding="utf-8")
                changed, detail = ralph_pilot.commit_iteration("iter 2")
            finally:
                ralph_pilot.ROOT = original_root

            self.assertFalse(no_change,
                             "an iteration that changed nothing must not pass")
            self.assertIn("nothing to commit", reason)
            self.assertTrue(changed, "a real change must be attributable")
            self.assertRegex(detail, r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
