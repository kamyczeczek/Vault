#!/usr/bin/env python3
"""review_gate.py — W8 measured Review Gate logger.

Run before and after inserting a reflection artifact on a sequential workflow,
and diff a cheap metric (e.g. plan-drift / compliance) supplied by the caller.

Usage:
  python scripts/review_gate.py --phase before --metric plan_drift=0.42 --out reflection/review_gate.jsonl
  python scripts/review_gate.py --phase after  --metric plan_drift=0.18 --out reflection/review_gate.jsonl
  python scripts/review_gate.py --report reflection/review_gate.jsonl
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", choices=["before","after"])
    ap.add_argument("--metric", action="append", default=[], help="k=v, e.g. plan_drift=0.42 (repeatable)")
    ap.add_argument("--out", default="reflection/review_gate.jsonl")
    ap.add_argument("--report", action="store_true", help="print delta summary from existing log")
    args=ap.parse_args()

    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)

    if args.report:
        if not out.exists():
            print(f"no log yet: {out}")
            return 0
        rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
        # pair consecutive before/after
        for i in range(1,len(rows)):
            if rows[i-1].get("phase")=="before" and rows[i].get("phase")=="after":
                b,a=rows[i-1],rows[i]
                for k in set(b.get("metrics",{})) & set(a.get("metrics",{})):
                    try:
                        d=float(a["metrics"][k]) - float(b["metrics"][k])
                    except: continue
                    print(f"{k}: {b['metrics'][k]} → {a['metrics'][k]}  (delta {d:+.4f})  [{b.get('ts')} → {a.get('ts')}]")
        return 0

    if not args.phase:
        ap.error("--phase required unless --report")

    metrics={}
    for kv in args.metric:
        if "=" in kv:
            k,v=kv.split("=",1)
            try: v=float(v)
            except: pass
            metrics[k.strip()]=v

    fp_path = ROOT / "knowledge/graph/.graph_fingerprint"
    fp = fp_path.read_text().strip() if fp_path.exists() else "?"

    rec={"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "phase": args.phase, "fingerprint": fp, "metrics": metrics}
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out,"a",encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    print(f"logged {args.phase} → {out}  {rec}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
