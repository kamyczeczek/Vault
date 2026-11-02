from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

run1_path = RESULTS / "phase1b_dev_dryrun_run1.json"
run2_path = RESULTS / "phase1b_dev_dryrun.json"

if not run1_path.exists():
    raise SystemExit("Missing run1 file")
if not run2_path.exists():
    raise SystemExit("Missing run2 file (phase1b_dev_dryrun.json)")

run1_data = json.loads(run1_path.read_text(encoding="utf-8"))
run2_data = json.loads(run2_path.read_text(encoding="utf-8"))

t1_map = {t["task_id"]: t for t in run1_data.get("tasks", []) if "error" not in t}
t2_map = {t["task_id"]: t for t in run2_data.get("tasks", []) if "error" not in t}

common_tasks = sorted(set(t1_map.keys()) & set(t2_map.keys()))
print(f"Krok 4: Porównanie {len(common_tasks)} wspólnych bezbłędnych zadań miedzy run1 a nowym przebiegiem:")

differences = []
models = ["SeasonalNaive", "NLinear", "DLinear"]

for tid in common_tasks:
    rec1 = t1_map[tid]
    rec2 = t2_map[tid]
    for m in models:
        m1 = rec1["models"][m]["task_mase"]
        m2 = rec2["models"][m]["task_mase"]
        diff = abs(m1 - m2)
        if diff > 1e-9:
            differences.append((tid, m, m1, m2, diff))

if not differences:
    print(f"  [OK] Wszystkie {len(common_tasks)} wspólne zadania maj p3116 MASE BIT-IDENTYCZNE (abs diff <= 1e-9) na wszystkich 3 baseline'ach!")
else:
    print(f"  [UWAGA] Znaleziono {len(differences)} roznic:")
    for tid, m, m1, m2, diff in differences:
        print(f"    {tid:32s} {m:15s} run1={m1:.8f} run2={m2:.8f} diff={diff:.2e}")
