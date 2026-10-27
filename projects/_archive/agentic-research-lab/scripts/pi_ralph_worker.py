#!/usr/bin/env python
"""Ralph work phase through pi: the --worker counterpart of recipes/ralph-work.yaml.

`scripts/ralph_pilot.py` accepts any command for a phase via `--worker`; this
is the pi implementation. Same contract as the goose recipe, delivered to a
fresh pi session instead of a goose one:

- **Fresh context is structural, not promised.** `pi -p` processes one prompt
  and exits; `--no-session` makes the session ephemeral, so nothing from the
  previous iteration survives. The only things that cross the iteration
  boundary are the files in `.goose/ralph/` and the git log - exactly the
  mechanism of the technique.
- **The verdict stays in files.** pi's transcript is not read by the loop.
  The worker writes `work-summary.txt`, and only writes `work-complete.txt`
  when the task is genuinely done; `RALPH-BLOCKED.md` stops the loop.

The prompt travels in a file (`--append-system-prompt <path>`), not on the
command line: the task text and the git log can be long, and Windows command
lines are not the place for them. The user message is a short kickoff.

No-model invocation: `RALPH_PI_CMD` (or `--pi-cmd`) replaces the pi command
line. `tests/test_ralph_pi.py` drives the real loop with a fake pi that only
writes the state files, proving control flow at zero cost.

Environment:
    RALPH_WORKER_MODEL      pi model pattern (flag --model overrides; default: pi's config)
    RALPH_WORKER_PROVIDER   pi provider      (flag --provider overrides; default: pi's config)
    RALPH_PI_CMD            full command line for one pi session (flag --pi-cmd
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

MARKER = "RALPH WORK PHASE"

# pi trusts this project's own resources: the worker needs the repo context
# (CLAUDE.md/AGENTS.md, project pi settings). The loop runs in one's own
# repository; drop --approve from build_argv if that is not wanted.
KICKOFF = ("Begin the Ralph work phase now. Read .goose/ralph/task.md first; "
           "the full instructions are appended to your system prompt.")


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
    """What prior iterations actually did. This is the real handoff: the loop
    clears per-iteration files, so a fresh worker reorients from git, not memory."""
    try:
        code, out = ralph_pilot.sh(["git", "log", "-8", "--oneline"])
    except FileNotFoundError:
        return "(git not on PATH - no history available)"
    if code != 0:
        return "(no git history yet)"
    return out.strip() or "(no git history yet)"


def build_prompt(sd: Path) -> str:
    """Mirror of recipes/ralph-work.yaml, inlined so the session does not have
    to find the recipe itself. The task and feedback are inlined verbatim: they
    are the contract, and reorientation from memory is the failure this
    technique exists to prevent."""
    task = read_text(sd / "task.md")
    if not task:
        raise SystemExit("pi_ralph_worker: .goose/ralph/task.md missing - the "
                         "loop seeds it; run the loop, do not hand-assemble "
                         "the state directory")
    iteration = read_text(sd / "iteration.txt") or "?"
    feedback = read_text(sd / "review-feedback.txt")
    return f"""{MARKER} (iteration {iteration})

You are in a RALPH LOOP - one iteration of work, in a fresh session.
You remember nothing from earlier iterations: each is a new, ephemeral
session. Your work persists through files only, and through the git log.

TASK (from .goose/ralph/task.md - the contract):
{task}

GIT LOG (what prior iterations actually did - do not re-do it, do not delete it):
{git_log()}

PRIOR REVIEWER FEEDBACK (.goose/ralph/review-feedback.txt):
{feedback if feedback else "(none this iteration - reorient from the task and the git log)"}

RULES:
- Read existing code before you edit it. One coherent change beats five
  scattered ones.
- Address the prior feedback first when it exists.
- Verify your own work with the project's own commands (tests, gates) and
  report the real result, including failure.
- Never write work-complete.txt early to make the loop stop. A false
  "done" is the single most damaging thing you can do in this loop.

OUTPUT CONTRACT - the loop reads these files in .goose/ralph/, not your
transcript:
- ALWAYS write work-summary.txt: what you did, and what you verified.
- Write work-complete.txt ONLY if the task is genuinely, verifiably done.
- If you are stuck, write RALPH-BLOCKED.md explaining precisely what you
  tried and what is blocking you."""


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
            raise SystemExit(f"pi_ralph_worker: pi command is not parseable: {exc}")
    found = shutil.which("pi")
    if not found:
        raise SystemExit("pi_ralph_worker: pi not found on PATH. Install it, "
                         "or set RALPH_PI_CMD to a full command line.")
    return [found]


def main() -> int:
    p = argparse.ArgumentParser(
        description="One Ralph work phase through pi (see module docstring).")
    p.add_argument("--pi-cmd",
                   help="full command line for one pi session (env: RALPH_PI_CMD)")
    p.add_argument("--model",
                   help=f"pi model pattern (env: {ralph_pilot.WORKER_ENV['model']})")
    p.add_argument("--provider",
                   help=f"pi provider (env: {ralph_pilot.WORKER_ENV['provider']})")
    args = p.parse_args()

    pi_cmd = args.pi_cmd or os.environ.get("RALPH_PI_CMD", "").strip() or None
    model = args.model or os.environ.get(ralph_pilot.WORKER_ENV["model"], "")
    provider = args.provider or os.environ.get(ralph_pilot.WORKER_ENV["provider"], "")

    sd = state_dir()
    prompt_file = sd / "pi-work-prompt.md"
    prompt_file.write_text(build_prompt(sd), encoding="utf-8", newline="\n")

    argv = build_argv(resolve_pi_base(pi_cmd), model, provider, prompt_file)
    try:
        r = subprocess.run(argv, cwd=ralph_pilot.ROOT, text=True, check=False,
                           capture_output=True)
    except FileNotFoundError:
        print(f"pi_ralph_worker: {argv[0]!r} not found")
        return 127
    # Emitted, not silent: the pilot captures this phase's output, so what is
    # written here is preserved without leaking into the loop's own transcript.
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(f"pi_ralph_worker: pi session failed (exit {r.returncode})")
        print(out)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
