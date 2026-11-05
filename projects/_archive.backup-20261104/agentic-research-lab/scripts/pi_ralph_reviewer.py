#!/usr/bin/env python
"""Ralph review phase through pi: the --reviewer counterpart of recipes/ralph-review.yaml.

`scripts/ralph_pilot.py` accepts any command for a phase via `--reviewer`;
this is the pi implementation. The reviewer is a *different* session from the
worker and never sees its conversation; it reads only the state files and the
git log, and its verdict is the loop's stop condition - written to
`.goose/ralph/review-result.txt`, which the loop reads as a file, not as a
model message.

Same mechanism as the work phase: `pi -p --no-session` (fresh context,
ephemeral session), prompt in a file via `--append-system-prompt <path>`.

Environment:
    RALPH_REVIEWER_MODEL      pi model pattern (flag --model overrides; default: pi's config)
    RALPH_REVIEWER_PROVIDER   pi provider      (flag --provider overrides; default: pi's config)
    RALPH_PI_CMD              full command line for one pi session (flag --pi-cmd
                              overrides; default: `pi` on PATH)
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ralph_pilot  # noqa: E402

MARKER = "RALPH REVIEW PHASE"

# pi trusts this project's own resources: the reviewer runs the project's
# verification, which needs the repo context. The loop runs in one's own
# repository; drop --approve from build_argv if that is not wanted.
KICKOFF = ("Begin the Ralph review phase now. The full instructions are "
           "appended to your system prompt; the verdict goes to "
           ".goose/ralph/review-result.txt, not to your reply.")


def state_dir() -> Path:
    """The loop's official state directory, resolved at call time so tests can
    point the module at a scratch root."""
    return ralph_pilot.ROOT / ralph_pilot.STATE_DIR


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def git_log() -> str:
    """What prior iterations actually did - the reviewer checks claims against
    it, not against the worker's prose."""
    try:
        code, out = ralph_pilot.sh(["git", "log", "-8", "--oneline"])
    except FileNotFoundError:
        return "(git not on PATH - no history available)"
    if code != 0:
        return "(no git history yet)"
    return out.strip() or "(no git history yet)"


def build_prompt(sd: Path) -> str:
    """Mirror of recipes/ralph-review.yaml, inlined. The worker's claim is
    inlined verbatim and labelled as evidence, not truth."""
    task = read_text(sd / "task.md")
    if not task:
        raise SystemExit("pi_ralph_reviewer: .goose/ralph/task.md missing - "
                         "the loop seeds it; run the loop, do not hand-assemble "
                         "the state directory")
    iteration = read_text(sd / "iteration.txt") or "?"
    summary = read_text(sd / "work-summary.txt")
    complete = read_text(sd / "work-complete.txt")
    return f"""{MARKER} (iteration {iteration})

You are the REVIEWER in a Ralph loop. A different model did the work in a
session you cannot see. Its claims are EVIDENCE, NOT TRUTH - your value
comes from not believing a claim you have not checked:
- If the summary says the work is done, check the files before agreeing.
- If the summary says tests pass, run them yourself before agreeing.
- A claim that is specific, confident, and wrong is worse than an honest
  "I could not finish this", and you must catch it.

TASK (from .goose/ralph/task.md):
{task}

WORKER'S CLAIM (.goose/ralph/work-summary.txt):
{summary if summary else "(the worker wrote no summary - that is already a red flag)"}

COMPLETION CLAIM (.goose/ralph/work-complete.txt):
{complete if complete else "(absent - the worker did not claim completion)"}

GIT LOG (what actually changed - check claims against it):
{git_log()}

REVIEW CRITERIA, in order of importance:
1. Does the work actually accomplish the task as written above?
2. Does it actually run, and do the project's own checks pass? Run them.
3. Is it complete rather than half-done? Partial work presented as complete
   is the most common failure and must be rejected.
4. Are there obvious defects, regressions, or claims contradicted by the
   code?
Be strict but fair: do not reject for style when the functionality is
correct; do reject work that does not run, failing tests, and a
work-complete.txt the work does not support.

OUTPUT CONTRACT - the loop reads .goose/ralph/review-result.txt, not your
reply:
- Approved: write exactly SHIP to .goose/ralph/review-result.txt
- Not approved: write exactly REVISE to .goose/ralph/review-result.txt and
  write specific, actionable feedback to .goose/ralph/review-feedback.txt.
  The next worker is a different model with no memory of you: "add error
  handling" is nearly useless; "file.py:42 raises ValueError on an empty
  host and nothing catches it; add validation at the boundary" tells it
  exactly what to do."""


def build_argv(pi_base: list[str], model: str, provider: str,
               prompt_file: Path) -> list[str]:
    """One fresh, ephemeral pi session. Checked against argv, not source: a
    `--resume`/`--continue` that ever appears here re-accumulates context and
    defeats the technique while it still looks like it runs."""
    argv = list(pi_base) + ["-p", "--no-session", "--approve"]
    if provider:
        argv += ["--provider", provider]
    if model:
        argv += ["--model", model]
    argv += ["--append-system-prompt", str(prompt_file), KICKOFF]
    return argv


def resolve_pi_base(pi_cmd: str | None) -> list[str]:
    """The command line that launches pi. `--pi-cmd` carries a full command
    (e.g. `python /tmp/fake_pi.py ship`), which is how the test suite proves
    control flow without a model; the default is `pi` on PATH."""
    if pi_cmd:
        try:
            return ralph_pilot.split_command(pi_cmd)
        except ValueError as exc:
            raise SystemExit(f"pi_ralph_reviewer: pi command is not parseable: {exc}")
    found = shutil.which("pi")
    if not found:
        raise SystemExit("pi_ralph_reviewer: pi not found on PATH. Install it, "
                         "or set RALPH_PI_CMD to a full command line.")
    return [found]


def main() -> int:
    p = argparse.ArgumentParser(
        description="One Ralph review phase through pi (see module docstring).")
    p.add_argument("--pi-cmd",
                   help="full command line for one pi session (env: RALPH_PI_CMD)")
    p.add_argument("--model",
                   help=f"pi model pattern (env: {ralph_pilot.REVIEWER_ENV['model']})")
    p.add_argument("--provider",
                   help=f"pi provider (env: {ralph_pilot.REVIEWER_ENV['provider']})")
    args = p.parse_args()

    pi_cmd = args.pi_cmd or os.environ.get("RALPH_PI_CMD", "").strip() or None
    model = args.model or os.environ.get(ralph_pilot.REVIEWER_ENV["model"], "")
    provider = args.provider or os.environ.get(ralph_pilot.REVIEWER_ENV["provider"], "")

    sd = state_dir()
    prompt_file = sd / "pi-review-prompt.md"
    prompt_file.write_text(build_prompt(sd), encoding="utf-8", newline="\n")

    argv = build_argv(resolve_pi_base(pi_cmd), model, provider, prompt_file)
    try:
        r = subprocess.run(argv, cwd=ralph_pilot.ROOT, text=True, check=False,
                           capture_output=True)
    except FileNotFoundError:
        print(f"pi_ralph_reviewer: {argv[0]!r} not found")
        return 127
    # Emitted, not silent: the pilot captures this phase's output, so what is
    # written here is preserved without leaking into the loop's own transcript.
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(f"pi_ralph_reviewer: pi session failed (exit {r.returncode})")
        print(out)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
