#!/usr/bin/env python3
"""Hermes local sessions: token/cost per successful task, from state.db.

Measures the unit the user asked about: tokens per successful task.
One "task" = one session (hermes sessions are task-scoped in this CLI).
Read-only.
"""
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

DB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:/Users/Mateusz/AppData/Local/hermes/state.db"
)

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

q = """
SELECT s.id, s.model, s.end_reason, s.message_count, s.tool_call_count,
       s.input_tokens, s.output_tokens, s.cache_read_tokens,
       s.reasoning_tokens, s.api_call_count, s.estimated_cost_usd,
       s.actual_cost_usd, s.cost_status, s.title,
       datetime(s.started_at, 'unixepoch') AS started,
       duration_seconds(s.ended_at - s.started_at) AS dur
FROM sessions s
WHERE s.input_tokens > 0 OR s.output_tokens > 0
ORDER BY s.started_at DESC
LIMIT 200
"""
try:
    rows = con.execute(q).fetchall()
except sqlite3.OperationalError:
    # duration_seconds may not exist; fall back
    q = q.replace("duration_seconds(s.ended_at - s.started_at)", "NULL")
    rows = con.execute(q).fetchall()

def agg(rows, key):
    out = {}
    for r in rows:
        k = r[key] if key != "cost" else (r["cost_status"] or "unknown")
        a = out.setdefault(k, dict(n=0, in_=0, out=0, cr=0, rw=0,
                                    reasoning=0, calls=0, msgs=0, tools=0,
                                    est_cost=0.0, act_cost=0.0))
        a["n"] += 1
        a["in_"] += r["input_tokens"] or 0
        a["out"] += r["output_tokens"] or 0
        a["cr"] += r["cache_read_tokens"] or 0
        a["reasoning"] += r["reasoning_tokens"] or 0
        a["calls"] += r["api_call_count"] or 0
        a["msgs"] += r["message_count"] or 0
        a["tools"] += r["tool_call_count"] or 0
        a["est_cost"] += r["estimated_cost_usd"] or 0.0
        a["act_cost"] += r["actual_cost_usd"] or 0.0
    return out

tot_in = sum((r["input_tokens"] or 0) for r in rows)
tot_cr = sum((r["cache_read_tokens"] or 0) for r in rows)
tot_out = sum((r["output_tokens"] or 0) for r in rows)
tot_rsn = sum((r["reasoning_tokens"] or 0) for r in rows)
tot_cost = sum((r["estimated_cost_usd"] or 0.0) + (r["actual_cost_usd"] or 0.0)
               for r in rows)
done = [r for r in rows if r["end_reason"] in (None, "completed", "user_stopped", "idle")]
print(f"rows={len(rows)} (capped 200, newest first)")
print(f"total: in={tot_in} cache_read={tot_cr} out={tot_out} "
      f"reasoning={tot_rsn} cost=${tot_cost:.2f}")
if tot_cr + tot_in:
    print(f"cache hit ratio (cr/(cr+in)): {tot_cr / (tot_cr + tot_in):.3f}")
if rows and tot_in + tot_cr > 0:
    print(f"avg tokens/task: in+cr={((tot_in + tot_cr) / len(rows)):.0f} "
          f"out={(tot_out / len(rows)):.0f} "
          f"total={((tot_in + tot_cr + tot_out + tot_rsn) / len(rows)):.0f}")
    print(f"avg cost/task: ${tot_cost / len(rows):.4f}")
for label, grp in [("by_model", agg(rows, "model")),
                   ("by_end_reason", agg(rows, "end_reason"))]:
    print(f"\n=== {label} ===")
    for k, a in sorted(grp.items(), key=lambda kv: -kv[1]["in_"]):
        cr_in = a["in_"] + a["cr"]
        hit = a["cr"] / cr_in if cr_in else 0.0
        print(f"{k!s:50} n={a['n']:3} in={a['in_']:>9} cr={a['cr']:>9} "
              f"out={a['out']:>8} rsn={a['reasoning']:>7} "
              f"calls={a['calls']:>4} tools={a['tools']:>5} "
              f"hit={hit:.2f} ${a['est_cost'] + a['act_cost']:.4f}")

# worst tasks: highest total tokens, with title for context
print("\n=== top 10 heaviest sessions (tokens) ===")
for r in sorted(rows, key=lambda r: -((r["input_tokens"] or 0)
                                       + (r["cache_read_tokens"] or 0)
                                       + (r["output_tokens"] or 0)))[:10]:
    t = (r["input_tokens"] or 0) + (r["cache_read_tokens"] or 0) \
        + (r["output_tokens"] or 0) + (r["reasoning_tokens"] or 0)
    print(f"{r['id'][:12]} {r['started']} {r['model']!s:40} "
          f"tot={t:>9} msgs={r['message_count'] or 0} tools={r['tool_call_count'] or 0} "
          f"end={r['end_reason']!s:18} {str(r['title'])[:40]!r}")

# smu: per-task billing detail if populated
smu_rows = con.execute(
    "SELECT COUNT(*), SUM(input_tokens), SUM(cache_read_tokens), "
    "SUM(output_tokens), COUNT(DISTINCT session_id) FROM session_model_usage"
).fetchone()
print(f"\nsmu rows: n={smu_rows[0]} in={smu_rows[1]} cr={smu_rows[2]} "
      f"out={smu_rows[3]} sessions={smu_rows[4]}")
tasks = con.execute(
    "SELECT DISTINCT task FROM session_model_usage LIMIT 20").fetchall()
print("smu tasks:", [t[0] for t in tasks])
