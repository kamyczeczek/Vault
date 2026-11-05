#!/usr/bin/env python3
"""SIM-2b Q22 cold-start follow-up harness (pre-registered: sim2_q22_protocol.md).

Same scripted-simulation class as SIM-2 v1: real timed `ask.py` subprocess
calls, repeated fresh across three isolated worktrees (cold-orientation
simulator; deterministic FTS query => reproducible A/B).

Pre-run refinements (logged in protocol §Pre-registered changes):
  R-rc  reorient_cum = calls up to first SEED-VALID call (first call
        retrieving >=1 required seed), all calls if never seed-valid.
        ("first rc=0" hollowed the C control: C's evict queries return
        non-seed matches with rc=0, making C reorient == B by construction.)
  R-tt  ttfva = first call index k where the cumulative union of ids across
        calls[0..k] contains BOTH seeds; "NA" if never.
  R-c3  C condition runs 3 evict-domain queries (protocol table said 2;
        the 3-call symmetric budget makes the control spike reliable).
  R-ct  Contamination split into two tiers: TRIVIALIZATION_PROBES
        (reproduced seed-chunk content / stated causal-chain answer)
        auto-disqualify; LAB_STATE_TOKENS are the orientation input under
        test, logged as evidence only.
  R-db  Worktrees get the gitignored graph.db attached by hardlink from the
        main tree after creation; without it every ask.py call exits
        'graph.db missing' and the run is void.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "subprojects" / "vera" / "experiments" / "runs"

# --- frozen per protocol ------------------------------------------------------
SEEDS = ("00_reflection_reorientation_cost",
         "01_workspace_rapid_understanding")
SEED_SET = frozenset(SEEDS)

VERBATIM_Q22 = ("Causal chain: how does reorientation cost convert into "
                "performance loss for a fresh agent session?")

CONDITIONS: dict[str, dict] = {
    "A": {
        "packs": [ROOT / "CONTEXT.md"]
                 + sorted((ROOT / "stages").glob("*/CONTEXT.md")),
        "queries": [VERBATIM_Q22, "reorientation cost", "rapid understanding"],
        "worktree": "sim2b-A",
    },
    "B": {
        "packs": [ROOT / "subprojects" / "vera" / "experiments"
                  / "sim2_packB.md"],
        "queries": ["reorientation cost", "rapid understanding"],
        "worktree": "sim2b-B",
    },
    "C": {
        "packs": [ROOT / "stages" / "05_evict" / "CONTEXT.md"],
        "queries": ["eviction stale memory", "memory rule evict gate",
                    "promote candidate gate"],
        "worktree": "sim2b-C",
    },
}

# --- contamination tiers (R-ct) ------------------------------------------------
# Tier 1 TRIVIALIZATION: reproduced seed-chunk content or the stated
# causal-chain answer to Q22. Any hit auto-disqualifies the session.
# All probes verified CLEAN against pack sets A/B/C pre-run (2026-09-25),
# so a hit at run time indicates genuine leakage, not pack residue.
TRIVIALIZATION_PROBES = [
    "re-orientation cost is the real persistence failure",
    "bounded forward worklist",
    "vista",
    "check_state.py",
    "state.md",
    "ultra-fast",
    "under 500 tokens",
    "pre-index",
    "stage isolation",
    "automated gates",
    "re-query overhead",
    "first-answer latency",
]
# Tier 2 LAB-STATE: workspace pointers / prior verdict metadata (SIM-2, Q1,
# INCONCLUSIVE, ...). These are the orientation input under test, NOT
# contamination — logged as evidence, never disqualifying.
LAB_STATE_TOKENS = [
    "SIM-2", "sim2", "Q1", "Q22", "verdict", "INCONCLUSIVE",
    "ttfva", "reorient", "EXPF", "falsification",
]

# interleave so machine warm-state spreads across conditions (protocol matrix)
INTERLEAVED_ORDER = ["A", "B", "A", "B", "C", "A", "B", "C", "A", "B", "A", "B"]


def contamination_check(pack_text: str) -> tuple[bool, list[str], list[str]]:
    """Return (disqualified, trivialization_hits, lab_state_hits)."""
    low = pack_text.lower()
    triv = [t for t in TRIVIALIZATION_PROBES if t.lower() in low]
    lab = [t for t in LAB_STATE_TOKENS if t.lower() in low]
    return (bool(triv), triv, lab)


def run_ask(ask_script: Path, cwd: Path, query: str) -> dict:
    """One timed ask.py subprocess call; return {query, rc, ids, ...}."""
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, str(ask_script), query],
            capture_output=True, text=True, timeout=120, cwd=cwd,
        )
        rc, stdout = proc.returncode, (proc.stdout or "")
    except subprocess.TimeoutExpired:
        rc, stdout = 124, "TIMEOUT"
    except OSError as e:
        rc, stdout = 125, f"OSERROR: {e}"
    ids = [m.group(1) for m in
           re.finditer(r"^# (\S+)", stdout, re.MULTILINE)]
    return {
        "query": query,
        "rc": rc,
        "ids": ids,
        "ok": rc == 0,
        "wall_s": round(time.perf_counter() - t0, 3),
        "stdout_bytes": len(stdout.encode("utf-8")),
    }


def evaluate_session(calls: list[dict]) -> dict:
    """Pre-registered metrics for one session (R-rc / R-tt).

    seed-valid = call whose ids intersect SEED_SET.
    reorient_cum = calls up to (and incl.) first seed-valid call;
                   all calls if never seed-valid.
    ttfva = first k where cumulative union of ids across calls[0..k]
            contains BOTH seeds; "NA" if never.
    ungrounded = calls after the seed-valid call; all calls if never valid.
    """
    n = len(calls)
    first_valid = next((i for i, c in enumerate(calls)
                       if set(c["ids"]) & SEED_SET), None)
    reorient_cum = (first_valid + 1) if first_valid is not None else n
    ungrounded = n - reorient_cum if first_valid is not None else n
    seen: set[str] = set()
    ttfva = "NA"
    for i, c in enumerate(calls):
        seen.update(c["ids"])
        if SEED_SET <= seen:
            ttfva = i + 1
            break
    return {
        "n_calls": n,
        "reorient_cum": reorient_cum,
        "ttfva": ttfva,
        "ungrounded": ungrounded,
        "ttfva_tok": round(sum(c["stdout_bytes"] for c in calls) / 4),
    }


def attach_graph_db() -> None:
    """R-db: hardlink the gitignored main-tree graph.db into each worktree.

    `git worktree add` checks out tracked files only; graph.db (713 MB,
    gitignored) is absent, so every ask.py call in a worktree would exit
    'graph.db missing'. A hardlink shares one on-disk inode: zero extra
    space, byte-stable; all uses are read-only and sequential."""
    src = ROOT / "knowledge" / "graph" / "graph.db"
    if not src.exists():
        raise RuntimeError(f"main-tree graph.db missing: {src}")
    for cond, spec in CONDITIONS.items():
        dst = (ROOT / ".worktrees" / spec["worktree"]
               / "knowledge" / "graph" / "graph.db")
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        print(f"attached graph.db -> {dst.relative_to(ROOT)} "
              f"({dst.stat().st_nlink} links)")


def ensure_worktrees() -> dict[str, Path]:
    """Create the three isolated worktrees if missing; attach DB; map."""
    wts: dict[str, Path] = {}
    for cond, spec in CONDITIONS.items():
        path = ROOT / ".worktrees" / spec["worktree"]
        if not (path / "knowledge" / "graph" / "ask.py").exists():
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "git_worktree.py"),
                 "create", "--name", spec["worktree"]],
                capture_output=True, text=True, cwd=ROOT,
            )
            if r.returncode != 0:
                raise RuntimeError(
                    f"worktree create failed ({spec['worktree']}): "
                    f"{(r.stdout + r.stderr).strip()}")
        wts[cond] = path
    attach_graph_db()
    return wts


def execute_session(wt: Path, cond: str, slot: int, session_no: int) -> dict:
    spec = CONDITIONS[cond]
    pack_text = "\n\n".join(p.read_text(encoding="utf-8")
                            for p in spec["packs"])
    disqualified, triv_hits, lab_hits = contamination_check(pack_text)
    ask = wt / "knowledge" / "graph" / "ask.py"
    calls = [run_ask(ask, wt, q) for q in spec["queries"]]
    rec = {
        "slot": slot,
        "cond": cond,
        "session_no": session_no,
        "worktree": str(wt),
        "packs": [str(p) for p in spec["packs"]],
        "disqualified": disqualified,
        "trivialization_hits": triv_hits,
        "lab_state_hits": lab_hits,
        **evaluate_session(calls),
        "calls": calls,
    }
    out = RUNS / f"sim2_q22_s{slot:02d}_{cond}_{session_no}.json"
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    return rec


def _median(vals: list[float]) -> float:
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def summarize(recs: list[dict]) -> dict:
    """Per-condition medians; C (n=2) uses max per protocol §Metric
    definitions; ttfva medians skip "NA" rows, empty -> "NA"."""
    out: dict[str, dict] = {}
    for cond in CONDITIONS:
        rows = [r for r in recs if r["cond"] == cond]
        reo = [r["reorient_cum"] for r in rows]
        ung = [r["ungrounded"] for r in rows]
        tfas = [r["ttfva"] for r in rows if r["ttfva"] != "NA"]
        out[cond] = {
            "n_sessions": len(rows),
            "reorient_cum_median": max(reo) if len(reo) <= 2
                                   else _median(reo),
            "ungrounded_median": max(ung) if len(ung) <= 2
                                  else _median(ung),
            "ttfva_median": (max(tfas) if len(tfas) <= 2
                             else _median(tfas)) if tfas else "NA",
            "disqualified_sessions": [r["slot"] for r in rows
                                      if r["disqualified"]],
        }
    return out


def verdict(s: dict, disqualified: list[int]) -> tuple[str, dict]:
    if disqualified:
        return ("INCONCLUSIVE",
                {"reason": (f"session(s) {disqualified} "
                             f"auto-disqualified: trivialization-probe hit")})
    r1 = s["B"]["reorient_cum_median"] <= s["A"]["reorient_cum_median"]
    b_t, a_t = s["B"]["ttfva_median"], s["A"]["ttfva_median"]
    r2 = b_t != "NA" and (a_t == "NA" or b_t <= a_t)
    r3 = s["B"]["ungrounded_median"] == s["A"]["ungrounded_median"]
    r4 = s["C"]["reorient_cum_median"] > s["B"]["reorient_cum_median"]
    checks = {"r1_B_reorient_le_A": r1,
              "r2_B_ttfva_le_A": r2,
              "r3_B_ungrounded_eq_A": r3,
              "r4_C_reorient_gt_B": r4}
    return ("PASS" if all(checks.values()) else "INCONCLUSIVE", checks)


def main() -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    wts = ensure_worktrees()
    counters: dict[str, int] = {}
    recs: list[dict] = []
    for slot, cond in enumerate(INTERLEAVED_ORDER, 1):
        counters[cond] = counters.get(cond, 0) + 1
        print(f"[{slot:02d}/12] {cond} session #{counters[cond]}")
        rec = execute_session(wts[cond], cond, slot, counters[cond])
        recs.append(rec)
        print(f"        reorient_cum={rec['reorient_cum']} "
              f"ttfva={rec['ttfva']} ungrounded={rec['ungrounded']} "
              f"disqualified={rec['disqualified']}")
    s = summarize(recs)
    dq = sorted({slot for slot, r in
                 ((r["slot"], r) for r in recs) if r["disqualified"]})
    v, checks = verdict(s, dq)
    summary = {
        "experiment": "SIM-2b Q22 causal-chain follow-up",
        "verdict": v,
        "checks": checks,
        "disqualified_sessions": dq,
        "per_condition": s,
    }
    with open(RUNS / "sim2_q22_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
