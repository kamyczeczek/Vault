#!/usr/bin/env python
"""Ralph loop, full official parity: fresh context per iteration, cross-model review.

Implements the pattern documented at https://goose-docs.ai/docs/tutorials/ralph-loop/
(based on Geoffrey Huntley's Ralph Wiggum technique).

THE MECHANISM, and why it is not a claim
---------------------------------------
"Fresh context per iteration" is usually asserted in a docstring. Here it is a
mechanism, and the mechanism is the reason this file is not just a `while` loop:

    goose run --recipe recipes/ralph-work.yaml

`goose run` starts a NEW session. Nothing from the previous iteration's
conversation survives. The only things that cross the iteration boundary are
files in `.goose/ralph/` and the git log. That is the whole thesis of the
technique, and it is enforced by the runtime rather than promised in prose.

State files (the official set, all in `.goose/ralph/`):

    task.md              the task description
    iteration.txt        current iteration number
    work-summary.txt     what the worker did this iteration
    work-complete.txt    present only if the worker claims the task is done
    review-result.txt    SHIP or REVISE - the loop's stop condition
    review-feedback.txt  concrete feedback handed to the next worker
    .ralph-complete      written on successful completion
    RALPH-BLOCKED.md     written by a worker that is stuck

WHY THE REVIEWER IS AUTHORITATIVE HERE - A DELIBERATE OVERRIDE
--------------------------------------------------------------
This repo's own evidence (knowledge/corpus/00_reflection_compaction_variance.md,
claim c3 in INBOX/ideas/the-ralph-loop-fits-this-repo-s-mechanic.md) argues that
a second LLM is the WRONG acceptance authority: it inherits the worker's
hallucinated world, and any token-overlap scorer gets tuned against the thing it
measures. A deterministic gate was preferred for exactly that reason.

Full parity deliberately does the opposite, and the user chose it knowingly:
**the reviewer's SHIP/REVISE is what stops the loop.** The deterministic gate
still runs, but as an *advisory* signal reported to the reviewer, not as an
authority that can terminate the loop.

The gate's exit code is therefore NOT the stop condition in this script. That is
a real divergence from the earlier pilot, it is intentional, and it is recorded
in the decision artifact rather than left to be discovered by surprise. Anyone
reading `check_dead_code.py` as the loop's guarantee should read this docstring
first: for *mechanical* work the gate is the better authority, and the cost of
this choice is paid on exactly the work the gate cannot judge.

DESIGN CONSTRAINTS, each traceable to a finding in this project:

- **Bounded state.** The loop's own state file is capped at STATE_MAX_LINES
  rendered lines. This is the `00_reflection_reorientation_cost` repair ("bounded
  state plus query beats a growing handoff"), not an invention here.
- **The verdict is read from a file, not from the model's message.** A model
  that says "done" in prose has changed nothing. `review-result.txt` is the only
  input to the loop's control flow.
- **The loop log is a separate stream from the workers'.** Worker and reviewer
  output are captured, never forwarded into the loop's own stdout. Otherwise a
  worker can narrate into the transcript and the log stops being falsifiable.
- **The state cap is measured on rendered lines, never on list length.** A
  character budget does not bound line count: 1200 characters can carry 600
  lines.
- **Every mutation is attributable to a commit** when `--commit` is passed. A
  correctness gate is already green on iteration 0, so it cannot tell a real
  iteration from a no-op; a commit can.
- **No semantic handoff check.** Whether the fresh session *understood* the
  state is not mechanically checkable, so it is not checked. What is checked is
  whether the iteration moved the work. `00_reflection_compaction_variance` is
  why: retained knowledge is variant across runs, so a token-overlap scorer
  would be tuning the instrument against the thing it measures.

COST
----
Every iteration runs TWO model sessions. The default of 10 iterations is
therefore 20 sessions, not 10. `--max` exists partly as a financial circuit
breaker, not only as a quality gate; the cost warning is printed on purpose.

Run:
    python scripts/ralph_pilot.py "Create a simple browser using Electron"
    python scripts/ralph_pilot.py ./prd.md
    python scripts/ralph_pilot.py "..." --max 2 --commit
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_MAX_LINES = 60
STATE_BUDGET_LINES = 20

# The official state directory. Chosen to match the documented recipe exactly so
# a run started here is readable by anyone who has run the upstream tutorial.
STATE_DIR = Path(".goose") / "ralph"

# The deterministic gate. ADVISORY in this script: it is reported to the
# reviewer, and the reviewer decides. See the docstring's override note.
GATE = [sys.executable, "scripts/check_dead_code.py"]

# Default phase commands: real goose sessions, one per phase, no --resume.
WORK_RECIPE = Path("recipes") / "ralph-work.yaml"
REVIEW_RECIPE = Path("recipes") / "ralph-review.yaml"

# Which env vars name the two models. Naming a different model for the reviewer
# is the point of the technique: a fresh perspective from a different model
# catches what the worker's own framing hides.
WORKER_ENV = {"model": "RALPH_WORKER_MODEL", "provider": "RALPH_WORKER_PROVIDER"}
REVIEWER_ENV = {"model": "RALPH_REVIEWER_MODEL", "provider": "RALPH_REVIEWER_PROVIDER"}


def sh(cmd: list[str]) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


def split_command(command: str) -> list[str]:
    """Split a shell-ish command string into argv, safe for Windows paths.

    A bare command *string* handed to `subprocess.run` becomes argv[0] and dies
    with `WinError 2` on Windows, which is the defect this replaces. Note that
    `shlex.split(..., posix=False)` is not sufficient either: it preserves the
    quotes, so a quoted absolute path such as `"C:\\...\\python.exe"` stays a
    quoted string and still fails. Whitespace splitting with quote stripping
    handles both, and backslashes are left untouched.
    """
    lexer = shlex.shlex(command, posix=False)
    lexer.whitespace_split = True
    lexer.commenters = ""
    parts = list(lexer)
    if not parts:
        raise ValueError("empty command")
    return [p.strip('"') for p in parts]


def run_gate() -> tuple[bool, str]:
    code, out = sh(GATE)
    return code == 0, out.strip()


def head_state() -> str:
    code, out = sh(["git", "log", "-1", "--pretty=%H"])
    return out.strip() if code == 0 else ""


def clamp_lines(text: str, budget: int = STATE_BUDGET_LINES) -> str:
    """Bound *rendered lines*, not characters and not list elements.

    The original writer truncated at 1200 characters and then asserted on
    `len(lines)` of the pre-join list. A multiline gate failure admitted hundreds
    of newlines inside a single list element, the rendered file blew the 60-line
    cap, and the assert fired only after the loop had lost its state file.
    Budgets here are measured, not hand-counted.
    """
    lines = text.splitlines() or [""]
    if len(lines) <= budget:
        return text
    kept = lines[: budget - 1]
    kept.append(f"... ({len(lines) - budget + 1} more lines truncated)")
    return "\n".join(kept)


def write_state(state_path: Path, iteration: int, verdict: str, gate_excerpt: str,
                prev_commit: str) -> int:
    """Write bounded present-tense state. A file the next session reads first.

    Returns the rendered line count, which is the number the cap is asserted
    against, so the reported count is always the written count.
    """
    lines = [
        f"# STATE - Ralph pilot (bounded, {STATE_MAX_LINES} lines max)",
        "",
        f"- iteration: {iteration}",
        f"- last_commit: {prev_commit or '(none)'}",
        f"- gate: {' '.join(GATE[1:])} (advisory)",
        f"- verdict: {verdict}",
        "",
        "## what the next iteration does",
        "1. read review-feedback.txt - it is the reason the last iteration "
        "was sent back",
        "2. make the smallest change that addresses it; do not refactor",
        "3. re-verify honestly, then stop - the REVIEWER's verdict stops this "
        "loop, not the gate",
        "",
        "## what is already settled (do not re-litigate)",
        "- the reviewer's SHIP/REVISE in review-result.txt is the acceptance "
        "signal; the gate is advisory input to the reviewer, not the authority",
        "- a green gate is not the same as a correct result",
        "- self-reporting progress is not evidence",
        "- bounded state beats a growing handoff file",
        "",
        "## failure this state was written from",
        "```",
        clamp_lines(gate_excerpt) or "(gate produced no output)",
        "```",
        "",
    ]
    text = "\n".join(lines)
    if len(text.splitlines()) > STATE_MAX_LINES:
        # Never emit an out-of-contract state file: drop the excerpt instead.
        text = "\n".join(
            lines[:18]
            + ["```", f"(excerpt omitted: would exceed {STATE_MAX_LINES} lines)",
               "```", ""]
        )
    state_path.write_text(text, encoding="utf-8", newline="\n")
    return len(text.splitlines())


def commit_iteration(message: str) -> tuple[bool, str]:
    """Make one iteration's work attributable to a commit.

    Returns (False, reason) when there was nothing to commit. A no-op worker must
    not be able to pass a convergence check that a real worker passes.
    """
    code, out = sh(["git", "add", "-A"])
    if code != 0:
        return False, f"git add failed: {out.strip()}"
    code, _ = sh(["git", "diff", "--cached", "--quiet"])
    if code == 0:
        return False, "nothing to commit - the worker changed no file"
    code, out = sh(["git", "commit", "-m", message])
    if code != 0:
        return False, f"git commit failed: {out.strip()}"
    return True, head_state()


# --------------------------------------------------------------------------
# Phase state: the official file contract, read and written by the loop only.
# --------------------------------------------------------------------------

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return ""


def read_verdict(sd: Path) -> str:
    """Read review-result.txt. The file is the verdict; the model's prose is not.

    Normalised because the official script compares with `tr -d '[:space:]'`, and
    a reviewer that writes "SHIP\\n" or " SHIP " must reach the same branch.
    """
    return "".join(read_text(sd / "review-result.txt").split()).upper()


def clear_iteration_state(sd: Path) -> None:
    """Remove per-iteration verdicts so a missing file is never read as SHIP.

    Stale state is the failure mode where iteration 2 exits because iteration 1
    said SHIP. The loop's control flow must depend only on the current review.
    """
    for name in ("review-result.txt", "review-feedback.txt", "work-complete.txt",
                 "work-summary.txt"):
        (sd / name).unlink(missing_ok=True)


def goose_argv(recipe: Path, model: str | None,
               provider: str | None) -> list[str]:
    """Build the argv for one real model session.

    `--no-session` is deliberate: each iteration is a throwaway session whose
    only output is the files it writes. Persisting a session file would quietly
    reintroduce the context accumulation the technique exists to prevent.
    """
    argv = ["goose", "run", "--recipe", str(ROOT / recipe), "--no-session"]
    if provider:
        argv += ["--provider", provider]
    if model:
        argv += ["--model", model]
    return argv


def resolve_models(args) -> tuple[str, str, str, str, list[str]]:
    """Resolve worker/reviewer model+provider from flags, then env.

    Returns (worker_model, worker_provider, reviewer_model, reviewer_provider,
    warnings). Same model on both sides is a warning, not an error: the official
    recipe warns and lets the user continue, and so does this.
    """
    wm = args.worker_model or os.environ.get(WORKER_ENV["model"]) or os.environ.get("GOOSE_MODEL", "")
    wp = args.worker_provider or os.environ.get(WORKER_ENV["provider"]) or os.environ.get("GOOSE_PROVIDER", "")
    rm = args.reviewer_model or os.environ.get(REVIEWER_ENV["model"], "")
    rp = args.reviewer_provider or os.environ.get(REVIEWER_ENV["provider"], "")
    if getattr(args, "same_model", False):
        rm = wm
        rp = wp

    warnings: list[str] = []
    missing = [n for n, v in (("worker model", wm), ("worker provider", wp),
                              ("reviewer model", rm), ("reviewer provider", rp))
               if not v]
    if missing:
        raise SystemExit("ralph: missing " + ", ".join(missing) +
                         ". Pass the flags or set the RALPH_* env vars; see the "
                         "upstream tutorial's Step 2.")
    if wm == rm and wp == rp:
        warnings.append(f"worker and reviewer are the same model ({wm}/{wp}); "
                        "cross-model review is the point of this technique")
    return wm, wp, rm, rp, warnings


def run_phase(argv: list[str]) -> tuple[int, str, int]:
    """Run one phase as a real subprocess, capturing its output.

    Returns (exit_code, captured_output, captured_chars). The output is captured
    deliberately: a worker that narrates into the loop's own stdout makes the log
    unfalsifiable, since the log then contains both the claims and the verdicts.
    """
    try:
        r = subprocess.run(argv, cwd=ROOT, text=True, check=False,
                           capture_output=True)
    except FileNotFoundError:
        return 127, f"{argv[0]}: not found on PATH", 0
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out, len(out)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Ralph loop: fresh context per iteration, cross-model review.")
    p.add_argument("task", nargs="?",
                   help="task description, or a path to a file containing one "
                        "(a PRD or spec).")
    p.add_argument("--max", type=int, default=10,
                   help="iteration budget: a financial circuit breaker, not a "
                        "quality gate. Each iteration costs TWO model sessions.")
    p.add_argument("--state", default="STATE.md",
                   help="path to the bounded state file (default: STATE.md)")
    p.add_argument("--worker",
                   help="command that performs one iteration's work; receives "
                        "the gate output on stdin. Overrides the goose session. "
                        "A loop with no worker cannot converge - it only re-runs "
                        "the gate and spins.")
    p.add_argument("--reviewer",
                   help="command that performs the review phase. Overrides the "
                        "goose session. It must write SHIP or REVISE to "
                        ".goose/ralph/review-result.txt.")
    p.add_argument("--worker-model",
                   help=f"model for the work phase (env: {WORKER_ENV['model']}, "
                        f"falls back to GOOSE_MODEL)")
    p.add_argument("--worker-provider",
                   help=f"provider for the work phase (env: "
                        f"{WORKER_ENV['provider']}, falls back to GOOSE_PROVIDER)")
    p.add_argument("--reviewer-model",
                   help=f"model for the review phase (env: "
                        f"{REVIEWER_ENV['model']}); should differ from the worker")
    p.add_argument("--reviewer-provider",
                   help=f"provider for the review phase (env: "
                        f"{REVIEWER_ENV['provider']})")
    p.add_argument("--same-model", action="store_true",
                   help="use the worker model/provider for review too")
    p.add_argument("--commit", action="store_true",
                   help="commit each iteration's work, so every mutation is "
                        "attributable and recoverable")
    p.add_argument("--dry-run", action="store_true",
                   help="report the gate verdict, change nothing")
    p.add_argument("--no-cost-warning", action="store_true",
                   help="suppress the cost warning; it exists to be read")
    args = p.parse_args()

    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = ROOT / state_path

    print("=== Ralph loop: fresh context per iteration, cross-model review ===")
    ok, out = run_gate()
    print(f"[gate] {'PASS' if ok else 'FAIL'}  (advisory: the reviewer's "
          f"verdict is what stops this loop)")
    if not ok:
        print(clamp_lines(out, budget=STATE_BUDGET_LINES))

    # --dry-run is a gate probe. It reports and returns before any model is
    # resolved, so it costs nothing and needs no credentials.
    if args.dry_run:
        return 0 if ok else 1

    if not args.task:
        p.error("no task provided. Usage: ralph_pilot.py \"task description\" "
                "   or: ralph_pilot.py ./prd.md")
    if args.max < 1:
        p.error("--max must be at least 1; a loop with no iterations proves nothing")

    # A phase that will actually call a model needs credentials; a phase
    # replaced by --worker/--reviewer does not. Resolving models unconditionally
    # would make a no-cost deterministic test fail on missing env vars, which is
    # a false blocker: nothing in that mode ever reaches a model.
    goose_phases = [p_ for p_, override in ((WORK_RECIPE, args.worker),
                                            (REVIEW_RECIPE, args.reviewer))
                    if not override]
    if goose_phases:
        worker_model, worker_provider, reviewer_model, reviewer_provider, warns = (
            resolve_models(args))
        for w in warns:
            print(f"[warn] {w}")
    else:
        worker_model = worker_provider = reviewer_model = reviewer_provider = ""
        warns = []
    for path in goose_phases:
        if not (ROOT / path).exists():
            p.error(f"missing recipe: {path}. Required for the goose phase and "
                    f"must not be silently skipped.")
    if goose_phases and not shutil.which("goose"):
        p.error("goose is not on PATH, but a goose phase will run. Install it, or "
                "pass --worker and --reviewer to run without model sessions.")

    if not args.no_cost_warning:
        if goose_phases:
            print(f"\n*** COST WARNING: up to {args.max} iteration(s), each running a "
                  f"WORKER session and a REVIEWER session - up to {args.max * 2} "
                  f"model sessions in total. ***")
            print(f"    worker:   {worker_model} ({worker_provider})")
            print(f"    reviewer: {reviewer_model} ({reviewer_provider})")
        else:
            print(f"\n[info] both phases are overridden by --worker/--reviewer: "
                  f"0 model sessions, no cost.")

    sd = ROOT / STATE_DIR
    sd.mkdir(parents=True, exist_ok=True)

    # Seed task.md: a file path is copied, a literal string is written.
    task_src = Path(args.task)
    if task_src.is_file():
        task_md = task_src.read_text(encoding="utf-8")
        print(f"\n[init] reading task from file: {args.task}")
    else:
        task_md = args.task
        print("\n[init] task given as a literal string")
    (sd / "task.md").write_text(task_md, encoding="utf-8", newline="\n")
    clear_iteration_state(sd)
    (sd / "RALPH-BLOCKED.md").unlink(missing_ok=True)
    (sd / ".ralph-complete").unlink(missing_ok=True)

    history: list[tuple[int, str]] = []
    shipped = False
    for i in range(1, args.max + 1):
        print(f"\n{'=' * 62}")
        print(f"  Iteration {i} / {args.max}")
        print("=" * 62)
        (sd / "iteration.txt").write_text(str(i), encoding="utf-8", newline="\n")
        clear_iteration_state(sd)

        # ---- WORK PHASE -------------------------------------------------
        print("\n-> WORK PHASE")
        if args.worker:
            try:
                wargv = split_command(args.worker)
            except ValueError as exc:
                print(f"[iter {i}] worker command is not parseable: {exc}")
                break
            code, _captured, nchars = run_phase(wargv)
        else:
            code, _captured, nchars = run_phase(
                goose_argv(WORK_RECIPE, worker_model, worker_provider))
        print(f"[iter {i}] work exit={code} (output captured, {nchars} chars)")
        if code != 0:
            print(f"[iter {i}] WORK PHASE FAILED - loop stops, state is preserved")
            break

        if (sd / "RALPH-BLOCKED.md").exists():
            print(f"\n!!! BLOCKED (worker said so) !!!")
            print(clamp_lines(read_text(sd / "RALPH-BLOCKED.md"),
                              budget=STATE_BUDGET_LINES))
            break

        if args.commit:
            committed, detail = commit_iteration(f"ralph: iteration {i} (work)")
            if committed:
                print(f"[iter {i}] committed {detail[:8]}")
            else:
                print(f"[iter {i}] not committed: {detail}")

        # ---- REVIEW PHASE ----------------------------------------------
        print("\n-> REVIEW PHASE")
        gate_ok, gate_out = run_gate()
        print(f"[gate] {'PASS' if gate_ok else 'FAIL'} (advisory input to the "
              f"reviewer)")
        if args.reviewer:
            try:
                rargv = split_command(args.reviewer)
            except ValueError as exc:
                print(f"[iter {i}] reviewer command is not parseable: {exc}")
                break
            code, _captured, nchars = run_phase(rargv)
        else:
            code, _captured, nchars = run_phase(
                goose_argv(REVIEW_RECIPE, reviewer_model, reviewer_provider))
        print(f"[iter {i}] review exit={code} (output captured, {nchars} chars)")

        if code != 0:
            print(f"[iter {i}] REVIEW PHASE FAILED - loop stops, state is preserved")
            break

        verdict = read_verdict(sd)
        if not verdict:
            print(f"[iter {i}] no review-result.txt written. The loop's control "
                  f"flow reads a file, not a message, so there is no verdict.")
            break

        if verdict == "SHIP":
            history.append((i, "SHIP"))
            print(f"\n{'=' * 62}")
            print(f"  SHIPPED after {i} iteration(s)")
            print("=" * 62)
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            (sd / ".ralph-complete").write_text(
                f"COMPLETE: {stamp}\n", encoding="utf-8", newline="\n")
            shipped = True
            break

        history.append((i, "REVISE"))
        print("\nREVISE - feedback for the next iteration:")
        print(clamp_lines(read_text(sd / "review-feedback.txt"),
                          budget=STATE_BUDGET_LINES))
    else:
        print(f"\n!! max iterations ({args.max}) reached without SHIP !!")

    # The excerpt is the most recent gate run, not the pre-loop probe: after a
    # REVISE the probe describes an older tree and would mislead the next
    # session. Only bind it here if no review phase ever ran.
    if "gate_out" not in dir() or not gate_out:
        gate_out = out
    rendered = write_state(state_path, len(history),
                           history[-1][1] if history else "unknown",
                           gate_out, head_state())
    where = (state_path.relative_to(ROOT) if state_path.is_relative_to(ROOT)
             else state_path)
    print(f"\nstate written: {where} ({rendered} lines, cap {STATE_MAX_LINES})")
    print(f"phase state:   {STATE_DIR.as_posix()}/")
    for i, verdict in history:
        print(f"  iteration {i}: {verdict}")
    if not history:
        print("  (no iteration completed)")
    return 0 if shipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
