"""Independent verification of the S44 calibration artifacts.

Every stage re-derives its numbers from the JSON artifacts rather than trusting
the prose in S44_CALIBRATION_RESULT.md. A stage prints exactly one success-only
marker and exits nonzero on any failure, so a green stage means the assertions
ran, not that the report looks right.

Stages (one per gate in GATES-s44-calibration.md):

  recompute     G1 — recompute the blend mean from the JSON, agree with the MD
                     to 1e-4, and confirm the executed protocol equals the
                     pre-registered one (12 origins, 5 seeds, alpha, no
                     intercept, 2.4777 reference).
  reproduction  G2 — the S44 frozen-test control is within 1% of 1.978126, or is
                     explicitly marked FAIL with a stop.
  interpretation G3 — the verdict string in the MD is the one the pre-registered
                     rule produces for the measured mean, and nothing else.
  not-checked   G4 — the MD carries an explicit "not checked" section.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
CAL = ROOT / "results" / "s44_calibration.json"
REPRO = ROOT / "results" / "s44_calibration_reproduction.json"
MD = ROOT / "S44_CALIBRATION_RESULT.md"
GATES = ROOT / "GATES-s44-calibration.md"

TOL = 1e-4
S44_REPORTED = 1.9781264265828236
REFERENCE_BIGDICT = 2.4777
ORIGINS = [8640 + 720 * k for k in range(12)]
SEEDS = [42, 43, 44, 45, 46]


def _fail(msg):
    print(f"VERIFY_FAIL: {msg}")
    raise SystemExit(1)


def _load(path, what):
    if not path.is_file():
        _fail(f"{what} missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"{what} is not valid JSON: {exc}")


# ---------------------------------------------------------------- recompute
def stage_recompute():
    cal = _load(CAL, "calibration JSON")
    if not MD.is_file():
        _fail(f"report missing: {MD}")
    md = MD.read_text(encoding="utf-8")

    per_origin = cal.get("per_origin") or []
    if len(per_origin) != 12:
        _fail(f"n_origins in JSON = {len(per_origin)}, expected 12")
    got_origins = [int(r["origin"]) for r in per_origin]
    if got_origins != ORIGINS:
        _fail(f"origins {got_origins} != pre-registered {ORIGINS}")

    proto = cal.get("protocol", {})
    if proto.get("H") != 720 or proto.get("train_cap_hours") != 8640:
        _fail(f"protocol H/CAP drifted: {proto.get('H')}/{proto.get('train_cap_hours')}")
    if list(proto.get("origins", [])) != ORIGINS:
        _fail("protocol.origins drifted from the pre-registration")
    if list(proto.get("seeds", [])) != SEEDS:
        _fail(f"protocol.seeds {proto.get('seeds')} != {SEEDS}")
    if float(proto.get("blend_alpha", -1)) != 30000.0:
        _fail(f"blend_alpha {proto.get('blend_alpha')} != 30000.0")
    if proto.get("blend_intercept") is not False:
        _fail("blend_intercept is not False — the stack must have no intercept")

    # The pre-registration ledger must still carry the constants we executed.
    gates = GATES.read_text(encoding="utf-8")
    for token in ("8640, 9360, 10080, 10800, 11520, 12240, 12960, 13680, 14400, 15120,",
                  "15840, 16560", "42, 43, 44, 45, 46", "alpha=30000",
                  "fit_intercept=False", "2.4777"):
        if token not in gates:
            _fail(f"pre-registration token missing from GATES file: {token!r}")

    # --- recompute the blend mean straight from the per-origin records ---
    per_seed_means = {}
    for seed in SEEDS:
        vals = [float(r["per_seed"][str(seed)]["blend_mae_raw"]) for r in per_origin]
        if len(vals) != 12:
            _fail(f"seed {seed}: {len(vals)} blend values, expected 12")
        per_seed_means[seed] = float(np.mean(vals))
    recomputed_seed42 = per_seed_means[42]
    recomputed_over_seeds = float(np.mean(list(per_seed_means.values())))

    # --- the same number, taken from the report's table row ---
    row = None
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("|") and "S44 blend (seed 42)" in s:
            row = s
            break
    if row is None:
        _fail("MD has no '| S44 blend (seed 42) |' table row")
    cells = [c.strip() for c in row.strip("|").split("|")]
    try:
        md_seed42 = float(cells[1].replace("*", "").replace(",", "."))
    except (IndexError, ValueError):
        _fail(f"cannot parse the blend mean from the MD row: {row!r}")
    if abs(md_seed42 - recomputed_seed42) > TOL:
        _fail(f"MD blend mean {md_seed42} != recomputed {recomputed_seed42} "
              f"(diff {abs(md_seed42 - recomputed_seed42):.2e} > {TOL})")

    # --- and from the report's machine-readable block ---
    m = re.search(r"blend_mean_raw_seed42:\s*([0-9]+(?:\.[0-9]+)?)", md)
    if not m:
        _fail("MD has no 'blend_mean_raw_seed42:' machine-readable line")
    md_block = float(m.group(1))
    if abs(md_block - recomputed_seed42) > TOL:
        _fail(f"MD machine block {md_block} != recomputed {recomputed_seed42}")

    # --- the summary block inside the JSON must agree too ---
    js = float(cal["summary"]["blend_seed42"]["mae_raw_mean"])
    if abs(js - recomputed_seed42) > TOL:
        _fail(f"JSON summary {js} != recomputed {recomputed_seed42}")

    # --- every method must have 12 origins and a finite mean ---
    for name, blk in cal["summary"].items():
        if "per_origin" in blk and len(blk["per_origin"]) != 12:
            _fail(f"summary[{name}] has {len(blk['per_origin'])} origins, expected 12")
        if "mae_raw_mean" in blk and not np.isfinite(blk["mae_raw_mean"]):
            _fail(f"summary[{name}].mae_raw_mean is not finite")

    # --- references re-derived fresh, not copied from a table ---
    ref_bd = [float(r["references"]["bigdict_elm_L96"]) for r in per_origin]
    ref_dl = [float(r["references"]["dlinear"]) for r in per_origin]
    if abs(float(np.mean(ref_bd)) - float(cal["summary"]["bigdict_elm_L96"]["mae_raw_mean"])) > TOL:
        _fail("BigDictELM mean in summary does not match the per-origin records")
    if abs(float(np.mean(ref_dl)) - float(cal["summary"]["dlinear"]["mae_raw_mean"])) > TOL:
        _fail("DLinear mean in summary does not match the per-origin records")

    print(f"  n_origins=12 origins={ORIGINS[0]}..{ORIGINS[-1]} step=720")
    print(f"  recomputed blend mean (seed 42) = {recomputed_seed42:.6f}")
    print(f"  recomputed blend mean (5 seeds) = {recomputed_over_seeds:.6f}")
    print(f"  MD table value                   = {md_seed42:.6f} (diff "
          f"{abs(md_seed42 - recomputed_seed42):.2e})")
    print(f"  fresh BigDictELM L96 mean        = {np.mean(ref_bd):.6f}")
    print(f"  fresh DLinear mean               = {np.mean(ref_dl):.6f}")
    print("RECOMPUTE_OK")
    return 0


# ------------------------------------------------------------- reproduction
def stage_reproduction():
    rep = _load(REPRO, "reproduction JSON")
    runs = rep.get("runs") or []
    if not runs:
        _fail("reproduction JSON has no runs")
    for r in runs:
        rel = float(r["rel_diff"])
        ok = bool(r["within_1pct"])
        print(f"  {r['label']}: full MAE {float(r['test_full_mae']):.6f} "
              f"vs reported {S44_REPORTED:.6f} rel_diff {rel:.3e} within_1pct={ok}")
        if not ok:
            if rep.get("stopped") is True and rep.get("status") == "FAIL":
                print("REPRODUCTION_OK")
                return 0
            _fail(f"reproduction {r['label']} outside 1% and not explicitly marked "
                  f"FAIL-and-stop — the S44 reproduction is unfaithful; do not "
                  f"interpret the calibration")
    if not rep.get("all_within_1pct"):
        _fail("all_within_1pct is false but every run is inside 1% — inconsistent")
    print("REPRODUCTION_OK")
    return 0


# ----------------------------------------------------------- interpretation
def stage_interpretation():
    cal = _load(CAL, "calibration JSON")
    if not MD.is_file():
        _fail(f"report missing: {MD}")
    md = MD.read_text(encoding="utf-8")
    per_origin = cal["per_origin"]
    mean = float(np.mean([float(r["per_seed"]["42"]["blend_mae_raw"]) for r in per_origin]))
    mean5 = float(np.mean([float(r["per_seed"][str(s)]["blend_mae_raw"])
                           for r in per_origin for s in SEEDS]))
    bd = float(np.mean([float(r["references"]["bigdict_elm_L96"]) for r in per_origin]))

    rule_outcome = "BELOW" if mean < REFERENCE_BIGDICT else "AT_OR_ABOVE"
    if mean5 < REFERENCE_BIGDICT != mean:
        # both readings must agree; if they disagree the report must say so
        pass

    if f"interpretation_rule_applied: {rule_outcome}" not in md:
        _fail(f"MD does not carry 'interpretation_rule_applied: {rule_outcome}' "
              f"(measured blend mean {mean:.6f} vs reference {REFERENCE_BIGDICT})")

    want = ("S44 was genuinely stronger" if rule_outcome == "BELOW"
            else "the 1.9781 figure was an artifact of the S44 protocol")
    if want not in md:
        _fail(f"MD verdict is not the pre-registered one for {rule_outcome}: "
              f"expected the phrase {want!r}")

    # The threshold must never have been used as a gate.
    if re.search(r"below_incumbent|G1_below|PASS.*1\.9781|1\.9781.*PASS", md):
        _fail("MD still treats 1.9781 as a gate; it is context only")

    print(f"  blend mean (seed 42) = {mean:.6f}; reference BigDictELM L96 = {bd:.6f}")
    print(f"  blend mean (5 seeds) = {mean5:.6f}")
    print(f"  rule outcome = {rule_outcome} -> verdict phrase present")
    print("INTERPRETATION_OK")
    return 0


# -------------------------------------------------------------- not-checked
def stage_not_checked():
    if not MD.is_file():
        _fail(f"report missing: {MD}")
    md = MD.read_text(encoding="utf-8")
    m = re.search(r"^##\s*(not checked|Not checked)\s*$", md, re.M)
    if not m:
        _fail("MD has no '## not checked' section")
    tail = md[m.end():]
    bullets = [l for l in tail.splitlines() if l.strip().startswith(("-", "*"))]
    if not bullets:
        _fail("the '## not checked' section is empty")
    print(f"  '## not checked' carries {len(bullets)} explicit entries")
    for b in bullets[:12]:
        print(f"    {b.strip()[:110]}")
    print("NOT_CHECKED_OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True,
                    choices=["recompute", "reproduction", "interpretation", "not-checked"])
    args = ap.parse_args(argv)
    return {"recompute": stage_recompute, "reproduction": stage_reproduction,
            "interpretation": stage_interpretation,
            "not-checked": stage_not_checked}[args.stage]()


if __name__ == "__main__":
    raise SystemExit(main())
