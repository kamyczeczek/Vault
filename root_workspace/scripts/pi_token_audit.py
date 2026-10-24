"""Token-efficiency baseline: where do input/cache/output tokens actually go?

Reads pi session JSONL directly (stdlib only) and reports:
  - spend split by token class (input / cacheRead / cacheWrite / output)
  - cache hit ratio  (cacheRead / (input + cacheRead))  <- the KV-prefix metric
  - top sessions by waste proxy: wasted cacheRead on re-reads, output volume
  - tool-result volume vs. assistant output volume

Usage: python3 scripts/pi_token_audit.py [--since 30d] [--cwd SUBSTR]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

SESSIONS = Path.home() / ".pi" / "agent" / "sessions"


def parse_since(spec: str) -> datetime:
    if spec.endswith("d"):
        return datetime.now(timezone.utc) - timedelta(days=int(spec[:-1]))
    if spec.endswith("h"):
        return datetime.now(timezone.utc) - timedelta(hours=int(spec[:-1]))
    return datetime.fromisoformat(spec)


def iter_records(include_subagents: bool):
    for path in SESSIONS.rglob("*.jsonl"):
        if not include_subagents and path.parent.parent != SESSIONS:
            continue
        yield path


def session_rows(since: datetime, cwd_filter: str):
    rows = []
    for path in iter_records(include_subagents=True):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        agg = defaultdict(int)
        cwd = ""
        sid = path.stem
        n_assistant = 0
        n_tool_results = 0
        n_read_calls = 0
        n_read_calls_files = set()
        n_read_result_chars = 0
        n_bash = 0
        n_bash_result_chars = 0
        tool_result_chars = 0
        assistant_chars = 0
        user_chars = 0
        first_ts = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = rec.get("type")
            if kind == "session":
                cwd = rec.get("cwd") or ""
                continue
            if kind == "message":
                msg = rec.get("message") or {}
                role = msg.get("role")
                if role == "assistant":
                    n_assistant += 1
                    for k, v in (msg.get("usage") or {}).items():
                        if isinstance(v, (int, float)):
                            agg[f"usage_{k}"] += int(v)
                    c = msg.get("content")
                    assistant_chars += _text_len(c)
                    for block in _blocks(c):
                        if block.get("type") == "toolCall":
                            name = block.get("name", "")
                            if name == "read":
                                n_read_calls += 1
                                args = block.get("arguments") or {}
                                key = f"{args.get('path')}:{args.get('offset', '')}"
                                n_read_calls_files.add(key)
                            elif name in ("bash", "powershell"):
                                n_bash += 1
                elif role == "toolResult":
                    n_tool_results += 1
                    out = msg.get("output") or msg.get("content")
                    n = _raw_len(out)
                    tool_result_chars += n
                    name = rec.get("toolName") or ""
                    if name == "read":
                        n_read_result_chars += n
                    elif name in ("bash", "powershell"):
                        n_bash_result_chars += n
                elif role == "user":
                    user_chars += _text_len(msg.get("content"))
            ts = rec.get("timestamp") or rec.get("createdAt")
            if ts and first_ts is None:
                first_ts = ts
        if n_assistant == 0:
            continue
        ts_dt = _parse_ts(first_ts)
        if ts_dt is not None and ts_dt < since:
            continue
        if cwd_filter and cwd_filter.lower() not in (cwd or "").lower():
            continue
        rows.append(
            {
                "session": sid,
                "cwd": cwd,
                "ts": str(first_ts),
                "path": str(path),
                "assistant_msgs": n_assistant,
                "tool_results": n_tool_results,
                "input": agg["usage_input"],
                "cache_read": agg["usage_cacheRead"],
                "cache_write": agg["usage_cacheWrite"],
                "output": agg["usage_output"],
                "cost": agg["usage_cost"] / 1000000.0 if "usage_cost" in agg else 0.0,
                "read_calls": n_read_calls,
                "read_unique_files": len(n_read_calls_files),
                "read_result_chars": n_read_result_chars,
                "bash_calls": n_bash,
                "bash_result_chars": n_bash_result_chars,
                "tool_result_chars": tool_result_chars,
                "assistant_chars": assistant_chars,
                "user_chars": user_chars,
            }
        )
    return rows


def _blocks(content):
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def _text_len(content):
    n = 0
    for b in _blocks(content):
        if b.get("type") == "text":
            n += len(b.get("text") or "")
    return n


def _raw_len(content):
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    try:
        return len(json.dumps(content))
    except (TypeError, ValueError):
        return len(str(content))


def _parse_ts(ts):
    if not ts:
        return None
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="30d")
    ap.add_argument("--cwd", default="")
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    rows = session_rows(parse_since(args.since), args.cwd)
    if not rows:
        print("no sessions matched")
        return 0

    t_in = sum(r["input"] for r in rows)
    t_cr = sum(r["cache_read"] for r in rows)
    t_cw = sum(r["cache_write"] for r in rows)
    t_out = sum(r["output"] for r in rows)
    total = t_in + t_cr + t_cw + t_out
    denom = t_in + t_cr

    print(f"sessions: {len(rows)}   since: {args.since}   cwd~={args.cwd or '*'}")
    print(f"  input        {t_in:>12,}  {pct(t_in, total)}")
    print(f"  cache read   {t_cr:>12,}  {pct(t_cr, total)}")
    print(f"  cache write  {t_cw:>12,}  {pct(t_cw, total)}")
    print(f"  output       {t_out:>12,}  {pct(t_out, total)}")
    print(f"  TOTAL        {total:>12,}")
    print(f"  cache hit ratio (cacheRead/(input+cacheRead)): {pct(t_cr, denom)}")
    print()
    print(f"chars  tool results {sum(r['tool_result_chars'] for r in rows):>10,}")
    print(f"chars  assistant    {sum(r['assistant_chars'] for r in rows):>10,}")
    print(f"chars  user prompts {sum(r['user_chars'] for r in rows):>10,}")
    print(f"read calls {sum(r['read_calls'] for r in rows):,}"
          f"  over unique file:offset {sum(r['read_unique_files'] for r in rows):,}"
          f"  -> re-read ratio {_ratio(sum(r['read_calls'] for r in rows), sum(r['read_unique_files'] for r in rows))}")
    print(f"bash calls {sum(r['bash_calls'] for r in rows):,}"
          f"  result chars {sum(r['bash_result_chars'] for r in rows):,}")
    print()

    rows.sort(key=lambda r: r["output"], reverse=True)
    print(f"top {args.limit} sessions by output tokens:")
    print(f"{'session':<26}{'cwd':<26}{'msgs':>5}{'out':>9}{'toolChr':>10}{'asmChr':>9}{'reads':>7}")
    for r in rows[: args.limit]:
        short = Path(r["cwd"]).name[:24] if r["cwd"] else "-"
        print(f"{r['session'][:24]:<26}{short:<26}{r['assistant_msgs']:>5}"
              f"{r['output']:>9,}{r['tool_result_chars']:>10,}{r['assistant_chars']:>9,}"
              f"{r['read_calls']:>7}")
    return 0


def pct(a: int, b: int) -> str:
    return f"{(100.0 * a / b):.1f}%" if b else "-"


def _ratio(a: int, b: int) -> str:
    return f"{a / b:.2f}x" if b else "-"


if __name__ == "__main__":
    sys.exit(main())