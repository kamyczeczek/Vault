#!/usr/bin/env python
"""Capability ladder — what a Ralph loop can actually be trusted with.

c2 (the abandoned experiment) asked whether a *second LLM* could judge whether a
fresh session re-oriented correctly from a bounded state file. The graph
refutes that instrument before it is built: `00_reflection_compaction_variance`
records that retained knowledge is **variant across runs**, not merely lossy.
Any scorer therefore gets tuned against the thing it measures — the abandoned
branch showed it concretely, when the blind negative control scored 0.50 until
the scorer was hand-edited to 0.00.

This ladder replaces that with predicates that need no model in the loop at
all. Each rung is strictly stronger than the one below, so a loop that converges
at rung N has demonstrated something rather than claimed something.

  rung 0  no worker
          Cannot converge by construction. The gate is already green on
          iteration 0, so "it fixed it" is unfalsifiable. The floor: this
          separates a loop from a spinning no-op.

  rung 1  dumb worker, mechanical fix
          Repairs a defect the gate names. Needs patience, not understanding.
          If this fails, the loop machinery is broken, not the model.

  rung 2  worker must produce a diff
          A real iteration leaves a committable change. A correctness gate
          cannot see this — it is green at iteration 0 — so commit attribution
          is the signal. Rejects a worker that reports success and changes
          nothing.

  rung 3  worker must satisfy a written predicate
          The hardest rung here and still mechanical: the worker edits a named
          file until a named rule holds. The worker does the mechanical work.
          The *criterion* is not independent of the harness here either: the
          ladder writes the rule itself before measuring. It is still the
          closest reachable stand-in for judgement work, and the gap between it
          and real judgement is what a `learned` decision should record.

  rung 4  human judgement
          Not automatable. Listed so the ceiling is visible rather than
          implied away.

What this does NOT claim: that a fresh session *understood* the state. That is
the c2 claim, it is not mechanically checkable, and the ladder measures only
whether work moved forward — deterministically.

Every rung runs in a throwaway `git worktree`, so the real worktree is never
mutated and a failing rung cannot dirty the repository.

Run:  python scripts/ralph_ladder.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ralph_pilot  # noqa: E402

GATE = [sys.executable, "scripts/check_dead_code.py"]
# A real, tracked module the dead-code gate scans. Rungs 1 and 3 mutate it.
TARGET_REL = "scripts/warn.py"
INJECT = "import xml.etree.ElementTree as ET\n"


class Worktree:
    """A detached checkout of HEAD. Nothing here can dirty the real worktree."""

    def __init__(self) -> None:
        self.path = Path(tempfile.mkdtemp(prefix="ralph-ladder-"))
        self.path.rmdir()  # git worktree add requires the path to be free
        self._r = subprocess.run(
            ["git", "worktree", "add", "--detach", str(self.path), "HEAD"],
            cwd=ROOT, capture_output=True, text=True)
        if self._r.returncode != 0:
            raise RuntimeError(f"worktree add failed: {self._r.stderr.strip()}")

    def run(self, body: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-c", body], cwd=self.path,
                              capture_output=True, text=True)

    def gate(self) -> tuple[bool, str]:
        r = subprocess.run(GATE, cwd=self.path, capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr).strip()

    def close(self) -> None:
        subprocess.run(["git", "worktree", "remove", "--force", str(self.path)],
                       cwd=ROOT, capture_output=True, text=True)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                       capture_output=True, text=True)


def _prefix_import() -> str:
    return (f"import pathlib\n"
            f"t = pathlib.Path({TARGET_REL!r})\n"
            f"t.write_text({INJECT!r} + t.read_text(encoding='utf-8'), "
            f"encoding='utf-8', newline='\\n')\n")


def rung0_no_worker() -> dict:
    """A loop with no worker re-runs a green gate and spins. That is the floor."""
    before = ralph_pilot.head_state()
    code, out = ralph_pilot.sh(GATE)
    after = ralph_pilot.head_state()
    return {
        "rung": 0,
        "name": "no worker",
        "expected": "gate green before any work; HEAD unmoved",
        "gate_green_before_work": code == 0,
        "head_moved": before != after,
        "passed": code == 0 and before == after,
        "detail": out.splitlines()[0] if out else "",
    }


def rung1_dumb_worker() -> dict:
    """Inject a provable defect; a mechanical worker must remove it."""
    wt = Worktree()
    try:
        inj = wt.run(_prefix_import())
        if inj.returncode != 0:
            return {"rung": 1, "name": "dumb worker, mechanical fix",
                    "passed": False, "detail": (inj.stdout + inj.stderr)[:300]}
        red, red_out = wt.gate()
        if red:
            return {"rung": 1, "name": "dumb worker, mechanical fix",
                    "passed": False,
                    "detail": f"injection did not turn the gate red: {red_out[:200]}"}

        fix = wt.run(
            "import pathlib\n"
            f"t = pathlib.Path({TARGET_REL!r})\n"
            "t.write_text(t.read_text(encoding='utf-8').replace("
            f"{INJECT!r}, '', 1), encoding='utf-8', newline='\\n')\n"
            "print('worker removed the dead import')\n")
        green, green_out = wt.gate()
        return {
            "rung": 1, "name": "dumb worker, mechanical fix",
            "expected": "defect injected, worker removes it, gate green",
            "gate_red_after_injection": True,
            "worker_exit": fix.returncode,
            "gate_green_after_worker": green,
            "passed": fix.returncode == 0 and green,
            "detail": green_out.splitlines()[0] if green_out else "",
        }
    finally:
        wt.close()


def staged_change(root: Path) -> bool:
    """True when there is something committable. This is the rung-2 signal.

    Deliberately `git add` + `git diff --cached --quiet` and NOT the commit
    itself. Measured reason: a throwaway worktree outside the workspace makes
    Q0 (workspace_root_integrity) report "a root-level file is outside every
    project gate", so the pre-commit hook blocks the commit. The hook is
    behaving correctly; the commit is an orthogonal concern (a real repo
    should refuse a commit that breaks its gates). What rung 2 actually claims
    is the weaker and still-deterministic thing: the iteration changed the
    worktree in a way git can attribute to a commit.
    """
    subprocess.run(["git", "add", "-A"], cwd=root, capture_output=True, text=True)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root,
                       capture_output=True, text=True)
    return r.returncode != 0  # 0 == nothing staged


def rung2_requires_a_diff() -> dict:
    """The gate is green either way. Only a diff tells a real iteration apart."""
    wt = Worktree()
    try:
        noop = wt.run("print('I did nothing, and I report it fixed')\n")
        ok_noop = staged_change(wt.path)

        real = wt.run(
            "import pathlib\n"
            f"t = pathlib.Path({TARGET_REL!r})\n"
            "t.write_text(t.read_text(encoding='utf-8') + '# ladder probe\\n', "
            "encoding='utf-8', newline='\\n')\n")
        ok_real = staged_change(wt.path)
        return {
            "rung": 2, "name": "worker must produce a diff",
            "expected": "no-op rejected, real change accepted",
            "gate_green_in_both_cases": wt.gate()[0],
            "noop_worker_exit": noop.returncode,
            "noop_produced_diff": ok_noop,
            "real_worker_exit": real.returncode,
            "real_produced_diff": ok_real,
            "passed": (noop.returncode == 0 and real.returncode == 0
                       and not ok_noop and ok_real),
            "detail": "the gate is green in both cases; only the diff separates them",
        }
    finally:
        wt.close()


def rung3_written_predicate() -> dict:
    """The closest mechanical stand-in for judgement: a written predicate.

    `check_dead_code.MANUAL` is a list of documented manual runbooks, and its
    own comment says adding a name "is a human decision recorded in git, not a
    silent exemption". That comment describes how the set is maintained in
    production; THIS ladder bypasses it and edits the set itself, so the gate
    stays deterministic but the criterion is not harness-independent.
    is deterministic; only the mechanical edit is delegated.

    Limitation, stated because the ladder is a measurement and a measurement
    that hides its own weakness is worthless: **the ladder writes the
    predicate itself.** It inserts `ladder_probe_worker` into MANUAL, then
    removes it after proving the gate flips. So the criterion is authored by
    the same program that scores it, which does NOT claim independence from
    the harness. The real version of this rung needs a rule authored outside
    the ladder, in its own commit, and the ladder only running the gate.
    """
    wt = Worktree()
    try:
        gate_rel = "scripts/check_dead_code.py"
        add = wt.run(
            "import pathlib, re\n"
            f"t = pathlib.Path({gate_rel!r})\n"
            "text = t.read_text(encoding='utf-8')\n"
            "probe = 'ladder_probe_worker'\n"
            # the worker file exists and is unreferenced -> orphan
            "pathlib.Path('scripts/ladder_probe_worker.py').write_text("
            "\"print('a manual runbook')\\n\", encoding='utf-8')\n"
            "text = text.replace('MANUAL = {', 'MANUAL = {\"' + probe + '\", ', 1)\n"
            "t.write_text(text, encoding='utf-8', newline='\\n')\n"
            "print('predicate written')\n")
        green_with_rule, out1 = wt.gate()
        if not green_with_rule:
            return {"rung": 3, "name": "worker must satisfy a written predicate",
                    "passed": False,
                    "detail": f"predicate failed to hold: {out1[:250]}"}

        # Now remove the rule the ladder itself wrote. Same work, same gate:
        # proof the predicate is doing the work, not the worker's self-report.
        drop = wt.run(
            "import pathlib\n"
            f"t = pathlib.Path({gate_rel!r})\n"
            "t.write_text(t.read_text(encoding='utf-8').replace("
            "'\"ladder_probe_worker\", ', '', 1), encoding='utf-8', newline='\\n')\n")
        red_without_rule, out2 = wt.gate()
        return {
            "rung": 3, "name": "worker must satisfy a written predicate",
            "expected": ("green with the rule in MANUAL (which the ladder "
                         "wrote), red without it"),
            "green_with_predicate": green_with_rule,
            "red_without_predicate": not red_without_rule,
            "passed": (add.returncode == 0 and drop.returncode == 0
                       and green_with_rule and not red_without_rule),
            "detail": out2.splitlines()[-1] if out2 else "",
        }
    finally:
        wt.close()


RUNGS = [
    (0, "no worker", "convergence is impossible, so success is vacuous", rung0_no_worker),
    (1, "dumb worker, mechanical fix", "the injected defect is gone", rung1_dumb_worker),
    (2, "worker must produce a diff", "the worktree changed, so the iteration was real", rung2_requires_a_diff),
    (3, "worker satisfies a written predicate", "a rule in MANUAL holds (the ladder writes it)", rung3_written_predicate),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic Ralph capability ladder.")
    ap.add_argument("--rung", type=int, action="append",
                    help="run only this rung (repeatable)")
    ap.add_argument("--list", action="store_true", help="print the ladder only")
    args = ap.parse_args()

    print("=== Capability ladder: deterministic, no model in the loop ===\n")
    for index, name, predicate, _ in RUNGS:
        print(f"  rung {index}  {name}\n      predicate: {predicate}")
    print("  rung 4  human judgement\n      predicate: NOT automatable. "
          "Out of scope; listed so the ceiling is visible.\n")
    if args.list:
        return 0

    chosen = [r for r in RUNGS if not args.rung or r[0] in args.rung]
    results = []
    for index, _, _, fn in chosen:
        try:
            results.append(fn())
        except Exception as exc:  # a broken rung is a failed rung, not a crash
            results.append({"rung": index, "name": fn.__name__, "passed": False,
                            "detail": f"{type(exc).__name__}: {exc}"})

    print("RESULTS")
    for res in results:
        print(f"  [{'PASS' if res.get('passed') else 'FAIL'}] "
              f"rung {res.get('rung')}: {res.get('name')}")
        for key, value in res.items():
            if key in ("passed", "name", "rung"):
                continue
            print(f"          {key}: {value}")
    failures = [r for r in results if not r.get("passed")]
    print(f"\n{len(results) - len(failures)}/{len(results)} rungs passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
