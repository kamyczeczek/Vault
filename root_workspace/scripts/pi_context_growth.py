"""Per-turn context growth model: O(n^2) vs O(n).

For each assistant message we know input / cacheRead / cacheWrite / output.
  context_at_turn = input + cacheRead  (full prefix the provider had to process)
Sum(context_at_turn) over a session = total "context tokens touched".
If it grows super-linearly, the fix is turn-count reduction (shorter sessions,
delegate to subagents, compact) — not cheaper output.

Usage: python3 scripts/pi_context_growth.py <session.jsonl> [--limit 60]
       python3 scripts/pi_context_growth.py --latest [--cwd SUBSTR]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SESSIONS = Path.home() / ".pi" / "agent" / "sessions"


def latest_session(cwd_filter: str) -> Path:
    best: tuple[float, Path] | None = None
    for path in SESSIONS.rglob("*.jsonl"):
        if path.parent.parent != SESSIONS:
            continue
        first = _header(path)
        if first is None:
            continue
        if cwd_filter and cwd_filter.lower() not in (first.get("cwd") or "").lower():
            continue
        ts = _num(first.get("timestamp"))
        if ts is None:
            continue
        if best is None or ts > best[0]:
            best = (ts, path)
    if best is None:
        raise SystemExit("no session found")
    return best[1]


def _header(path: Path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") == "session":
                return rec
    return None


def _num(v) -> float | None:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def turns(path: Path):
    out = []
    model = None
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") == "model_change":
                mid = rec.get("modelId")
                if not mid and isinstance(rec.get("to"), dict):
                    mid = rec["to"].get("id")
                model = mid or model
            if rec.get("type") != "message":
                continue
            m = rec.get("message") or {}
            if m.get("role") != "assistant":
                continue
            u = m.get("usage") or {}
            cost = u.get("cost")
            if isinstance(cost, dict):
                cost = cost.get("total", 0)
            try:
                cost_f = float(cost or 0)
            except (TypeError, ValueError):
                cost_f = 0.0
            out.append(
                {
                    "model": model,
                    "input": int(u.get("input", 0) or 0),
                    "cache_read": int(u.get("cacheRead", 0) or 0),
                    "cache_write": int(u.get("cacheWrite", 0) or 0),
                    "output": int(u.get("output", 0) or 0),
                    "cost": cost_f,
                }
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("session", nargs="?")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--cwd", default="")
    ap.add_argument("--limit", type=int, default=60)
    args = ap.parse_args()

    path = Path(args.session) if args.session else latest_session(args.cwd)
    head = _header(path) or {}
    rows = turns(path)
    print(f"session : {path.name}")
    print(f"cwd     : {head.get('cwd')}")
    print(f"turns   : {len(rows)}")
    if not rows:
        return 0

    static_prefix = rows[0]["input"] + rows[0]["cache_read"]
    touched = sum(r["input"] + r["cache_read"] for r in rows)
    outputs = sum(r["output"] for r in rows)
    final_ctx = rows[-1]["input"] + rows[-1]["cache_read"]

    # models used and any switch => KV cache invalidation
    models = []
    for r in rows:
        if not models or models[-1] != r["model"]:
            models.append(r["model"])

    print(f"static prefix (turn 1 context): {static_prefix:,} tokens")
    print(f"final context:                   {final_ctx:,} tokens")
    print(f"context growth:                  {final_ctx / max(static_prefix, 1):.1f}x")
    print(f"total context touched:           {touched:,} tokens")
    print(f"total output generated:          {outputs:,} tokens")
    print(f"amplification touched/output:    {touched / max(outputs, 1):.1f}x")
    print(f"model sequence:                  {' -> '.join(str(m) for m in models)}")
    print()

    step = max(1, len(rows) // args.limit or 1)
    print(f"{'turn':>5}{'model':<22}{'in':>8}{'cacheRead':>11}{'ctx':>9}{'out':>7}{'cum ctx':>12}")
    cum = 0
    for i, r in enumerate(rows, 1):
        cum += r["input"] + r["cache_read"]
        if i % step and i != len(rows) and i > step * 12:
            continue
        ctx = r["input"] + r["cache_read"]
        print(f"{i:>5}{str(r['model'])[:20]:<22}{r['input']:>8,}{r['cache_read']:>11,}"
              f"{ctx:>9,}{r['output']:>7,}{cum:>12,}")

    # Where does the quadratic come from: growth per turn
    deltas = [
        (rows[i]["input"] + rows[i]["cache_read"]) - (rows[i - 1]["input"] + rows[i - 1]["cache_read"])
        for i in range(1, len(rows))
    ]
    if deltas:
        deltas_sorted = sorted(deltas)
        med = deltas_sorted[len(deltas_sorted) // 2]
        print()
        print(f"context delta per turn: median {med:+,}  mean {sum(deltas)/len(deltas):+,}"
              f"  max {max(deltas):+,}  (a healthy turn adds ~1 turn-worth of its own output+tool results)")
    return 0


if __name__ == "__main__":
    sys.exit(main())