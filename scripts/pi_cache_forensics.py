"""Why does the KV prefix cache break? Attribute every cold prefix to an event.

pi's own cacheWrite counter is the ground truth: a turn with cacheWrite == 0
while context > 0 means the provider had to re-process the entire prefix at
full price. This script walks each session in order, flags every turn where the
prefix went cold, and attributes it to the nearest preceding structural event
(model_change / thinking_level_change / context_edit / compaction).

Usage: python3 scripts/pi_cache_forensics.py [--since 30d] [--cwd SUBSTR] [--limit 20]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

SESSIONS = Path.home() / ".pi" / "agent" / "sessions"


def _num(v) -> float | None:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def parse_since(spec: str) -> float:
    if spec.endswith("d"):
        return (datetime.now(timezone.utc) - timedelta(days=int(spec[:-1]))).timestamp()
    if spec.endswith("h"):
        return (datetime.now(timezone.utc) - timedelta(hours=int(spec[:-1]))).timestamp()
    return _num(spec) or 0.0


def no_cache_provider(model: str | None) -> bool:
    """Providers observed to never return a cacheRead (empirically, from this
    workspace's own transcripts). Update when the provider list changes."""
    m = str(model or "").lower()
    return m.startswith("oc/")


def walk(path: Path):
    """Yield ('turn', usage) and ('event', kind, detail) in file order."""
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
            t = rec.get("type")
            if t == "session":
                yield "session", rec
            elif t == "model_change":
                new = rec.get("modelId") or rec.get("to")
                if isinstance(new, dict):
                    new = new.get("id")
                yield "event", "model_change", {"from": model, "to": new}
                model = new
            elif t == "thinking_level_change":
                lvl = rec.get("level") or rec.get("to") or rec.get("thinkingLevel")
                if isinstance(lvl, dict):
                    lvl = lvl.get("level")
                yield "event", "thinking_change", lvl
            elif t == "context_edit":
                yield "event", "context_edit", rec.get("targetId")
            elif t == "compaction":
                yield "event", "compaction", None
            elif t == "message":
                m = rec.get("message") or {}
                if m.get("role") == "assistant":
                    yield "turn", (m.get("usage") or {}), model


def analyse(path: Path):
    cold_by_cause = Counter()
    cold_tokens_by_cause = Counter()
    cold_events = 0
    total_input = 0
    total_cache_read = 0
    total_cache_write = 0
    n_turns = 0
    last_event = "session_start"
    last_event_detail = None
    events_since_cold = 0
    switched = False
    header = {}
    causes = []
    for item in walk(path):
        if item[0] == "session":
            header = item[1]
            continue
        if item[0] == "event":
            last_event, last_event_detail = item[1], item[2]
            if last_event == "model_change" and isinstance(last_event_detail, dict):
                if last_event_detail.get("from") != last_event_detail.get("to"):
                    switched = True
            events_since_cold += 1
            continue
        _, usage, model = item
        inp = int(usage.get("input", 0) or 0)
        cr = int(usage.get("cacheRead", 0) or 0)
        cw = int(usage.get("cacheWrite", 0) or 0)
        total_input += inp
        total_cache_read += cr
        total_cache_write += cw
        n_turns += 1
        ctx = inp + cr
        if ctx > 2000 and cr == 0 and cw == 0 and inp > 2000:
            # full-price re-process of an entire prefix. Attribute to the *dominant*
            # cause, not merely the nearest event: a provider with no prefix cache at
            # all makes every turn cold, so "nearest event" is misleading.
            if switched:
                cause = "model_switch"
                detail = f"{model}"
            elif no_cache_provider(model):
                cause = "provider_no_cache"
                detail = f"{model}"
            else:
                cause = last_event
                detail = last_event_detail
            cold_by_cause[cause] += 1
            cold_tokens_by_cause[cause] += inp
            cold_events += 1
            causes.append(
                {
                    "turn": n_turns,
                    "cause": cause,
                    "detail": detail,
                    "cold_tokens": inp,
                    "intervening_events": events_since_cold,
                }
            )
            events_since_cold = 0
            switched = False
    return {
        "path": path,
        "cwd": header.get("cwd") or "",
        "turns": n_turns,
        "input": total_input,
        "cache_read": total_cache_read,
        "cache_write": total_cache_write,
        "cold_events": cold_events,
        "cold_by_cause": cold_by_cause,
        "cold_tokens_by_cause": cold_tokens_by_cause,
        "causes": causes,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="60d")
    ap.add_argument("--cwd", default="")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    since = parse_since(args.since)
    reports = []
    for path in SESSIONS.rglob("*.jsonl"):
        if path.parent.parent != SESSIONS:
            continue
        try:
            rep = analyse(path)
        except OSError:
            continue
        if rep["turns"] == 0:
            continue
        try:
            ts = _num(json.loads(path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]).get("timestamp"))
        except (json.JSONDecodeError, ValueError, IndexError, OSError):
            ts = 0.0
        if ts and ts < since:
            continue
        if args.cwd and args.cwd.lower() not in rep["cwd"].lower():
            continue
        reports.append(rep)

    if not reports:
        print("no sessions matched")
        return 0

    t_in = sum(r["input"] for r in reports)
    t_cr = sum(r["cache_read"] for r in reports)
    t_cw = sum(r["cache_write"] for r in reports)
    cold_tokens = sum(sum(r["cold_tokens_by_cause"].values()) for r in reports)
    denom = t_in + t_cr

    print(f"sessions {len(reports)}   since {args.since}   cwd~={args.cwd or '*'}")
    print(f"  input(full price) {t_in:>12,}   cacheRead {t_cr:>12,}   cacheWrite {t_cw:>12,}")
    print(f"  cache hit ratio   {100.0 * t_cr / denom if denom else 0:.1f}%   (target > 90%)")
    print(f"  cold-prefix turns {sum(r['cold_events'] for r in reports):>12,}"
          f"   burning {cold_tokens:,} full-price tokens")
    print(f"  cold tokens as share of all input+cacheRead: "
          f"{100.0 * cold_tokens / denom if denom else 0:.1f}%")
    print()

    agg = Counter()
    agg_tok = Counter()
    for r in reports:
        agg.update(r["cold_by_cause"])
        agg_tok.update(r["cold_tokens_by_cause"])
    print("cold-prefix attribution (cause -> turns / full-price tokens / share of waste):")
    for cause, n in agg.most_common():
        tok = agg_tok[cause]
        print(f"  {cause:<18}{n:>6} turns {tok:>12,} tok   {100.0 * tok / cold_tokens if cold_tokens else 0:>5.1f}%")
    print()

    reports.sort(key=lambda r: sum(r["cold_tokens_by_cause"].values()), reverse=True)
    print(f"worst sessions by wasted full-price tokens:")
    print(f"{'session':<26}{'turns':>6}{'coldTurns':>10}{'wastedTok':>12}{'hitRatio':>10}  top cause")
    for r in reports[: args.limit]:
        d = r["input"] + r["cache_read"]
        hr = 100.0 * r["cache_read"] / d if d else 0
        top = r["cold_by_cause"].most_common(1)
        top_s = f"{top[0][0]} x{top[0][1]}" if top else "-"
        print(f"{r['path'].stem[:24]:<26}{r['turns']:>6}{r['cold_events']:>10}"
              f"{sum(r['cold_tokens_by_cause'].values()):>12,}{hr:>9.1f}%  {top_s}")

    worst = reports[0]
    if worst["causes"]:
        print()
        print(f"timeline of cold prefixes in {worst['path'].stem[:24]}:")
        for c in worst["causes"][:12]:
            print(f"  turn {c['turn']:>4}  {c['cause']:<18}{str(c['detail'])[:34]:<36}"
                  f"{c['cold_tokens']:>9,} tok")
    return 0


if __name__ == "__main__":
    sys.exit(main())