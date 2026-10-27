"""Compare the S-47 fit-window policies (Q9): fixed trailing 2000 vs expanding.

Reads the two result files the runner writes and reports whether the policy
changes the gate verdict, the locked candidate, or which tasks pool B wins.

    python s47_ref/rolling_arm.py                    # writes results_s47.json
    python s47_ref/rolling_arm.py --window expanding # writes results_s47_expanding.json
    python s47_ref/compare_window_policies.py

Exit 0 = the verdict is policy-robust, 1 = the verdict depends on the window
policy, 2 = a result file is missing.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).parent
FILES = {"fixed": HERE / "results_s47.json",
         "expanding": HERE / "results_s47_expanding.json"}
GATES = ("G1", "G2", "G3")


def load(policy: str) -> dict:
    path = FILES[policy]
    if not path.exists():
        raise SystemExit(f"{path.name} missing — run `python s47_ref/rolling_arm.py "
                         f"--window {policy}` first")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    results = {policy: load(policy) for policy in FILES}
    fixed, expanding = results["fixed"], results["expanding"]

    print(f"{'task':16s} {'A_fix':>9s} {'B_fix':>9s} {'B_exp':>9s} "
          f"{'dA':>9s} {'dB':>9s}  win fix/exp")
    flips = 0
    for task in fixed["per_task"]:
        fix = fixed["per_task"][task]["pool_blend_normalized"]
        exp = expanding["per_task"][task]["pool_blend_normalized"]
        win_fix = "B" if fix["B"] < fix["A"] else "A"
        win_exp = "B" if exp["B"] < exp["A"] else "A"
        flips += int(win_fix != win_exp)
        print(f"{task:16s} {fix['A']:9.6f} {fix['B']:9.6f} {exp['B']:9.6f} "
              f"{exp['A'] - fix['A']:+9.6f} {exp['B'] - fix['B']:+9.6f}  "
              f"{win_fix}/{win_exp}")

    gates_agree = all(fixed["gates"][g] == expanding["gates"][g] for g in GATES)
    choices = {policy: {t: results[policy]["per_task"][t]["screened"]["choice"]
                        for t in results[policy]["per_task"]}
               for policy in results}
    choice_agree = len(set(frozenset(c.items()) for c in choices.values())) == 1

    for policy, res in results.items():
        agg = res["aggregate"]
        gates = " ".join(f"{name}={res['gates'][name]}" for name in GATES)
        print(f"{policy:9s} mean A={agg['meanA_normalized']:.6f} "
              f"B={agg['meanB_normalized']:.6f} rank B={agg['mean_rankB']:.3f} "
              f"wins={agg['winsB']}/6 {gates}")

    print(f"\ngates agree: {gates_agree}; locked choice agree: {choice_agree}; "
          f"per-task winners flipped: {flips}/6")
    if gates_agree and choice_agree:
        print("Q9 VERDICT: policy-robust — fixed 2000 stands, expanding is "
              "a sensitivity check.")
        return 0
    print("Q9 VERDICT: policy-dependent — the gate does not survive the window "
          "change; no candidate advances.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
