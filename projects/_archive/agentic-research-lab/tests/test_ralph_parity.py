"""Parity contracts for the Ralph loop (full official-parity implementation).

These pin the parts of the loop that are *control flow*, not subprocess plumbing:
the verdict comes from a file, stale verdicts cannot leak between iterations, a
worker that reports blockage stops the loop, and the loop's exit code reflects
what actually happened.

Deliberately NOT tested here: that a real model reads the state correctly. That
is the semantic handoff question this repo's own evidence says is not
mechanically checkable, so asserting it with a token-overlap scorer would be
tuning the instrument against the thing it measures. What IS tested is that the
loop can express the verdict at all, which is a precondition for the model
phases meaning anything.

No test in this file launches a model or costs money.
"""
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ralph_pilot  # noqa: E402


class VerdictIsAFileTests(unittest.TestCase):
    """The loop's control flow reads review-result.txt, not a model's prose."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.sd = Path(self._td.name)
        self.addCleanup(self._td.cleanup)

    def test_missing_verdict_file_is_not_a_ship(self) -> None:
        # A reviewer that says "looks good!" in its message and writes no file has
        # not approved anything. Defaulting this to SHIP would let any reviewer
        # crash the loop into a false completion.
        self.assertEqual(ralph_pilot.read_verdict(self.sd), "")

    def test_ship_and_revise_are_read_from_the_file(self) -> None:
        (self.sd / "review-result.txt").write_text("SHIP", encoding="utf-8")
        self.assertEqual(ralph_pilot.read_verdict(self.sd), "SHIP")
        (self.sd / "review-result.txt").write_text("REVISE", encoding="utf-8")
        self.assertEqual(ralph_pilot.read_verdict(self.sd), "REVISE")

    def test_whitespace_and_case_are_normalised(self) -> None:
        # The upstream script compares with `tr -d '[:space:]'`. A reviewer that
        # writes "SHIP\n" or " ship " must reach the same branch, otherwise the
        # behaviour depends on the model's whitespace habits.
        (self.sd / "review-result.txt").write_text("  ship \n\n", encoding="utf-8")
        self.assertEqual(ralph_pilot.read_verdict(self.sd), "SHIP")

    def test_stale_verdict_cannot_leak_into_the_next_iteration(self) -> None:
        # The failure this pins: iteration 1 writes SHIP, the loop does not stop
        # for some other reason, and iteration 2 then reads iteration 1's file and
        # exits claiming a completion that never happened.
        (self.sd / "review-result.txt").write_text("SHIP", encoding="utf-8")
        (self.sd / "work-summary.txt").write_text("stale", encoding="utf-8")
        ralph_pilot.clear_iteration_state(self.sd)
        self.assertEqual(ralph_pilot.read_verdict(self.sd), "")
        self.assertFalse((self.sd / "work-summary.txt").exists())

    def test_clear_is_idempotent_on_a_fresh_directory(self) -> None:
        ralph_pilot.clear_iteration_state(self.sd)
        ralph_pilot.clear_iteration_state(self.sd)
        self.assertEqual(ralph_pilot.read_verdict(self.sd), "")


class StateDirectoryContractTests(unittest.TestCase):
    """The official file contract, and that the loop cannot silently drop it."""

    def test_state_dir_matches_the_documented_upstream_path(self) -> None:
        # Chosen to match the upstream tutorial exactly, so a run started here is
        # readable by anyone who has run the documented recipe.
        self.assertEqual(ralph_pilot.STATE_DIR.as_posix(), ".goose/ralph")

    def test_every_documented_state_file_is_written_by_the_loop(self) -> None:
        # Each of these is named in the upstream State Files table. If the loop
        # stops writing one, the next iteration's recipe is reading a file that
        # does not exist, and that failure is invisible from the outside.
        source = (ROOT / "scripts" / "ralph_pilot.py").read_text(encoding="utf-8")
        for name in ("task.md", "iteration.txt", "review-result.txt",
                     "review-feedback.txt", "work-complete.txt",
                     "work-summary.txt", "RALPH-BLOCKED.md", ".ralph-complete"):
            self.assertIn(name, source, f"{name} is part of the documented contract")

    def test_goose_phases_are_real_fresh_sessions(self) -> None:
        # Fresh context is the mechanism of the technique, so it must be structural:
        # `goose run` without --resume. If --resume ever appears in the built argv,
        # iterations start accumulating context again and the whole technique is
        # defeated while still looking like it runs.
        #
        # Checked against the argv, not the file text: the source legitimately
        # contains the string "--resume" in comments explaining its absence, so a
        # text search would fail on the very documentation that keeps it out.
        for recipe in (ralph_pilot.WORK_RECIPE, ralph_pilot.REVIEW_RECIPE):
            argv = ralph_pilot.goose_argv(recipe,
                                          "m", "p")
            self.assertEqual(argv[0:2], ["goose", "run"])
            self.assertNotIn("--resume", argv,
                             "iterations must not resume a prior session")
            self.assertIn("--no-session", argv)
            self.assertIn("--recipe", argv)

    def test_recipes_exist_and_declare_the_required_fields(self) -> None:
        # Schema verified against the goose recipe reference: version, title,
        # description, instructions, prompt.
        for name in ("ralph-work.yaml", "ralph-review.yaml"):
            path = ROOT / "recipes" / name
            self.assertTrue(path.is_file(), f"missing recipe: {path}")
            text = path.read_text(encoding="utf-8")
            for field in ("version:", "title:", "description:", "instructions:",
                          "prompt:"):
                self.assertIn(field, text, f"{name} missing {field}")

    def test_review_recipe_can_write_both_verdicts(self) -> None:
        # The loop's only stop condition is this file. A review recipe that cannot
        # express REVISE would make every run a false SHIP.
        text = (ROOT / "recipes" / "ralph-review.yaml").read_text(encoding="utf-8")
        self.assertIn("SHIP", text)
        self.assertIn("REVISE", text)
        self.assertIn("review-result.txt", text)


class GateIsAdvisoryTests(unittest.TestCase):
    """Full parity deliberately overrides this repo's own c3 claim.

    c3 (knowledge/corpus/00_reflection_compaction_variance.md, and claim c3 in
    INBOX/ideas/the-ralph-loop-fits-this-repo-s-mechanic.md) argues a second LLM
    is the wrong acceptance authority and a deterministic gate should be. The user
    chose full parity anyway, so the reviewer IS authoritative. That is a
    deliberate override, and these tests exist so it cannot quietly revert to a
    gate-driven loop without someone noticing the contract changed.
    """

    def test_the_override_is_documented_not_silent(self) -> None:
        source = (ROOT / "scripts" / "ralph_pilot.py").read_text(encoding="utf-8")
        self.assertIn("DELIBERATE OVERRIDE", source)
        self.assertIn("ralph_pilot.py", source)  # the file names itself honestly
        self.assertIn("00_reflection_compaction_variance", source)

    def test_gate_is_still_run_but_cannot_stop_the_loop(self) -> None:
        source = (ROOT / "scripts" / "ralph_pilot.py").read_text(encoding="utf-8")
        # The gate runs (it is reported to the reviewer)...
        self.assertIn("run_gate()", source)
        # ...but the shipped/not-shipped decision is the reviewer's file.
        self.assertIn('verdict = read_verdict(sd)', source)
        self.assertIn("if verdict == \"SHIP\"", source)

    def test_same_model_on_both_sides_is_a_warning_not_an_error(self) -> None:
        # Upstream warns and lets the user continue. Hard-failing here would make
        # the loop unusable for anyone with one provider configured.
        args = type("A", (), {
            "worker_model": "m", "worker_provider": "p",
            "reviewer_model": "m", "reviewer_provider": "p",
        })()
        import os
        saved = {k: os.environ.get(k) for k in
                 ("RALPH_WORKER_MODEL", "RALPH_WORKER_PROVIDER",
                  "RALPH_REVIEWER_MODEL", "RALPH_REVIEWER_PROVIDER",
                  "GOOSE_MODEL", "GOOSE_PROVIDER")}
        try:
            for k in saved:
                os.environ.pop(k, None)
            wm, wp, rm, rp, warns = ralph_pilot.resolve_models(args)
            self.assertEqual((wm, wp, rm, rp), ("m", "p", "m", "p"))
            self.assertTrue(warns, "same-model use must warn")
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_different_models_produce_no_warning(self) -> None:
        args = type("A", (), {
            "worker_model": "m1", "worker_provider": "p1",
            "reviewer_model": "m2", "reviewer_provider": "p2",
        })()
        import os
        saved = {k: os.environ.get(k) for k in
                 ("RALPH_WORKER_MODEL", "RALPH_WORKER_PROVIDER",
                  "RALPH_REVIEWER_MODEL", "RALPH_REVIEWER_PROVIDER",
                  "GOOSE_MODEL", "GOOSE_PROVIDER")}
        try:
            for k in saved:
                os.environ.pop(k, None)
            _, _, _, _, warns = ralph_pilot.resolve_models(args)
            self.assertEqual(warns, [])
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class PhaseArgvTests(unittest.TestCase):
    """What the loop actually executes for a model phase."""

    def test_argv_is_a_fresh_run_with_the_recipe_and_model(self) -> None:
        argv = ralph_pilot.goose_argv(ralph_pilot.WORK_RECIPE, "gpt-4o", "openai")
        self.assertEqual(argv[0:2], ["goose", "run"])
        self.assertIn("--recipe", argv)
        self.assertIn(str(ralph_pilot.WORK_RECIPE.name), " ".join(argv))
        self.assertIn("--model", argv)
        self.assertIn("gpt-4o", argv)
        self.assertIn("--provider", argv)
        self.assertIn("openai", argv)

    def test_absent_model_or_provider_omits_the_flag(self) -> None:
        # Emitting `--model ""` would make goose fail with a confusing provider
        # error rather than falling back to its own default.
        argv = ralph_pilot.goose_argv(ralph_pilot.REVIEW_RECIPE, None, None)
        self.assertNotIn("--model", argv)
        self.assertNotIn("--provider", argv)


class CliParityTests(unittest.TestCase):
    """What the help text advertises, the parser must accept."""

    def test_every_advertised_flag_parses(self) -> None:
        code, out = ralph_pilot.sh([
            sys.executable, "scripts/ralph_pilot.py",
            "some task", "--max", "2", "--state", "STATE.md",
            "--worker", "echo w", "--reviewer", "echo r",
            "--worker-model", "m1", "--worker-provider", "p1",
            "--reviewer-model", "m2", "--reviewer-provider", "p2",
            "--no-cost-warning", "--dry-run",
        ])
        self.assertNotIn("unrecognized arguments", out)
        self.assertNotIn("invalid choice", out)
        self.assertNotIn("error:", out)
        self.assertIn(code, (0, 1))

    def test_no_task_is_an_error_not_a_silent_run(self) -> None:
        code, out = ralph_pilot.sh([sys.executable, "scripts/ralph_pilot.py",
                                    "--dry-run"])
        # --dry-run returns before the task check, so ask without it.
        self.assertIn(code, (0, 1))
        code, out = ralph_pilot.sh([sys.executable, "scripts/ralph_pilot.py",
                                    "--no-cost-warning"])
        self.assertEqual(code, 2)
        self.assertIn("no task provided", out)

    def test_zero_iterations_is_rejected(self) -> None:
        # A loop that runs zero iterations proves nothing and looks like success.
        code, out = ralph_pilot.sh([sys.executable, "scripts/ralph_pilot.py",
                                    "task", "--max", "0", "--no-cost-warning"])
        self.assertEqual(code, 2)
        self.assertIn("at least 1", out)


class LadderWordingTests(unittest.TestCase):
    """The rung-3 predicate is written by the ladder, and must never claim otherwise.

    Pinned in the output too, not just the label: the `expected` field is
    user-visible, and the earlier fix corrected the label while leaving this
    string claiming the rule was human-written.
    """

    def test_no_human_authored_claim_survives_anywhere(self) -> None:
        source = (ROOT / "scripts" / "ralph_ladder.py").read_text(encoding="utf-8")
        for phrase in ("human-written", "human-authored", "human written"):
            self.assertNotIn(phrase, source,
                             f"the ladder authors its own rung-3 predicate; "
                             f"{phrase!r} overstates it")

    def test_rung_three_output_discloses_the_harness_writes_the_rule(self) -> None:
        text = io.open(ROOT / "scripts" / "ralph_ladder.py", encoding="utf-8").read()
        self.assertIn("which the ladder", text,
                      "the emitted `expected` string must say who wrote the rule")


if __name__ == "__main__":
    unittest.main()


class CoherencePinTests(unittest.TestCase):
    """Pins for four defects found in review, before the first parity commit.

    Each of these shipped green in 225 tests. A test suite that cannot fail on
    a claim the code does not make is not evidence.
    """

    def setUp(self) -> None:
        self.source = (ROOT / "scripts" / "ralph_pilot.py").read_text(encoding="utf-8")

    def test_state_never_claims_the_gate_is_the_acceptance_authority(self) -> None:
        # Full parity makes the REVIEWER authoritative. A state file that tells
        # the next fresh session "the exit code is the stop condition" actively
        # instructs it to ignore the reviewer's REVISE.
        state = (ROOT / "scripts" / "ralph_pilot.py").read_text(encoding="utf-8")
        for claim in ("the gate's exit code is the only acceptance signal",
                      "the loop's exit condition is the exit code"):
            self.assertNotIn(claim, state, f"stale c3 claim still in the loop: {claim!r}")

    def test_state_says_the_reviewer_stops_the_loop(self) -> None:
        self.assertIn("REVIEWER's verdict stops this", self.source)
        self.assertIn("not the gate", self.source)

    def test_final_state_uses_the_latest_gate_output_not_the_probe(self) -> None:
        # `out` is the pre-loop probe; after a REVISE it describes an older tree
        # and would tell the next session about failures that no longer exist.
        self.assertIn('if "gate_out" not in dir() or not gate_out:', self.source)
        self.assertIn("gate_out = out", self.source)

    def test_model_resolution_is_skipped_when_no_model_will_run(self) -> None:
        # Resolving models unconditionally made a no-cost deterministic test
        # fail on missing env vars - a false blocker, since nothing in that mode
        # ever reaches a model.
        body_at = self.source.index("def resolve_models(args)")
        call_at = self.source.index("resolve_models(args)", body_at + 10)
        self.assertIn("if goose_phases:", self.source[body_at:call_at])

    def test_cost_warning_does_not_claim_cost_when_phases_are_overridden(self) -> None:
        self.assertIn("0 model sessions, no cost", self.source)

    def test_gate_is_labelled_advisory_in_the_state_file(self) -> None:
        self.assertIn('(GATE[1:])} (advisory)', self.source)
