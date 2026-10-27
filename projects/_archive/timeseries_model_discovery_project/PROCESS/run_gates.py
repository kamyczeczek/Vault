#!/usr/bin/env python -X utf8
"""run_gates.py — single fail-loud entry point for all workspace gates.

Replaces the per-gate python-process enumeration duplicated across the
pre-commit twins (brains/icm_brain/hooks/pre-commit, pre-commit.ps1) and
the ORCHESTRATION.md session-close ritual. The gate list lives HERE, as
data — one source of truth, not three.

Modes:
  default : every-commit suite (fast; in-process, no subprocesses)
  --all   : adds session-close gates (live-brain workflow queries, research
            catalog, problem lifecycle, orchestration checker if present)

Exit semantics (scar 2026-09-05_pack-probe-print-only-gate): a gate that
cannot fail is a measurement, not a gate. Exit 1 names the failing gate
and reproduces its tail output. `--quiet` suppresses per-gate PASS lines.

Each gate runs via runpy inside ONE interpreter process — per-gate
subprocess startups (~36ms each) plus duplicated interpreter/library
imports collapse into one. Two isolation invariants make this safe:
  1. sys.path: gates import sibling modules by bare name (their dir is
     prepended when run as __main__ scripts; runpy does not do this).
  2. sys.modules scrub: sibling names collide across gate dirs (both
     skills_brain and reflection_brain ship gen_digest.py), so modules
     added during a gate's run are removed before the next gate runs.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# --- The gate list (single source of truth) ---------------------------------
# (label, path, supports_quiet)
EVERY_COMMIT_GATES = [
    ("skills_catalog", "skills/verify_catalog.py", False),
    ("project_brain_sync", "brain/verify_sync.py", True),
    ("inbox_clean", "PROCESS/check_inbox.py", False),
    ("python_compiles", "PROCESS/check_python_compiles.py", False),
]

SESSION_CLOSE_GATES = [
     ("workflow_routing", "PROCESS/check_workflow.py", True),
     ("research_catalog", "RESEARCH/check_catalog.py", False),
     ("reflection_close", "PROCESS/check_reflection_close.py", True),
 ]
# -----------------------------------------------------------------------------
# Removed harness-only gates:
#   - brain_router_liveness / brain_federation_contract: self-test expects
#     an ICM-routing brain layout that this project does not use.
#   - problem_lifecycle: PROGRESS.md problem citations are not required for
#     this simple project workspace.
#   - orchestration: workspace-slice checks reference workspaces/icm-brain
#     and .omp/extensions/, which are not part of this project.


def run_one(label: str, rel_path: str, supports_quiet: bool, quiet: bool) -> tuple[int, str]:
    """Run one gate in-process. Returns (exit_code, tail_output)."""
    # a gate entry may carry extra argv as a list, e.g. [path, "--require-fresh", "3"]:
    # the runner executes in-process (runpy), so a shell-style command string would
    # never reach the gate's own argument parser.
    if isinstance(rel_path, list):
        script = REPO_ROOT / rel_path[0]
        argv = [str(script)] + list(rel_path[1:])
    else:
        script = REPO_ROOT / rel_path
        argv = [str(script)]
    if not script.is_file():
        # A missing gate is a hard failure, not a skip: the list IS the
        # contract (No Silent Failures). Session-close scaffolding not yet
        # built (e.g. check_orchestration.py) fails loud here.
        return 2, f"[run_gates] FAIL: gate script missing: {script}"

    if quiet and supports_quiet:
        argv.append("--quiet")
    buf = io.StringIO()
    old_argv, old_exit = sys.argv, sys.exit
    sys.argv = argv
    sys.exit = lambda code=0: (_ for _ in ()).throw(SystemExit(code))

    gate_dir = str(script.parent)
    sys.path.insert(0, gate_dir)
    modules_before = set(sys.modules)
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            runpy.run_path(str(script), run_name="__main__")
        code = 0
    except SystemExit as e:
        code = int(e.code or 0)
    except Exception as e:  # gate crashed: that is a failure, not a pass
        buf.write(f"[run_gates] gate crashed: {type(e).__name__}: {e}\n")
        code = 1
    finally:
        for key in set(sys.modules) - modules_before:
            sys.modules.pop(key, None)
        if gate_dir in sys.path:
            sys.path.remove(gate_dir)
        sys.exit = old_exit
        sys.argv = old_argv

    output = buf.getvalue()
    return code, output


def main() -> int:
    ap = argparse.ArgumentParser(description="single fail-loud entry point for all workspace gates")
    ap.add_argument("--all", action="store_true",
                    help="also run session-close gates (workflow/research/problems)")
    ap.add_argument("--quiet", action="store_true", help="suppress PASS lines")
    ap.add_argument("--only", metavar="LABEL",
                    help="run exactly one gate by label (debug/red-path use)")
    args = ap.parse_args()

    gates = list(EVERY_COMMIT_GATES)
    if args.all:
        gates += SESSION_CLOSE_GATES
    if args.only:
        gates = [g for g in gates if g[0] == args.only]
        if not gates:
            print(f"[run_gates] FAIL: no gate labeled {args.only!r}", file=sys.stderr)
            return 2

    failures = []
    for label, path, supports_quiet in gates:
        code, output = run_one(label, path, supports_quiet, args.quiet)
        if code != 0:
            failures.append((label, path, code, output))
            print(f"[run_gates] FAIL {label} (exit {code}) — {path}", file=sys.stderr)
            for line in output.splitlines()[-20:]:
                print(f"    {line}", file=sys.stderr)
        elif not args.quiet:
            # A gate may pass (exit 0) yet still warn on stderr — e.g. EPI
            # reporting a stale ledger. rc=0 with a warning is not "ok": the
            # runner must surface it, or a frozen metric reads as current.
            # (AUDIT-2026-09-16 Finding 1: the warning existed but was
            # swallowed by the "only print failures" branch.)
            warn = "\n".join(
                ln for ln in output.splitlines()
                if ln.startswith(("EPI STALE", "WARNING", "[router] WARNING"))
            )
            if warn:
                print(f"[run_gates] ok   {label}")
                for ln in warn.splitlines():
                    print(f"         warn  {ln}")
            else:
                print(f"[run_gates] ok   {label}")

    if failures:
        names = ", ".join(f"{l}(exit {c})" for l, _, c, _ in failures)
        print(f"[run_gates] {len(failures)} gate(s) failed: {names}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"[run_gates] all {len(gates)} gate(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
