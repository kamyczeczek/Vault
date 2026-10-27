#!/usr/bin/env python3
"""route.py — deterministic tag-intersection routing (no model) + P2 ADAPT split.

Uses graph.db directly. Same tags + same fingerprint → same id set (ORDER BY id).
P2: if intersection cardinality < threshold and query contains `planning`, deterministically
splits one level via alias tags (decomposition/htn/pddl/classical-planning) ordered ORDER BY id.
One level only (00_is_progressive_disclosure...); no recursion. Logs depth via --json depth field.
A tag intersection that matches nothing is a dead routing key (W-AUDIT-4): exit 2 with the
dead tags on stderr, like ask.py — an empty id list with rc=0 silently meant "no principles
apply" instead of "typo/stale tag". --all-topics stays rc=0: per-topic counts are inventory,
and a printed 0 is visible, not silent.

Usage:
  python pipeline/06_reflect/route.py --tag icm --tag reflection --limit 12
  python pipeline/06_reflect/route.py --all-topics --limit 12
  python pipeline/06_reflect/route.py --tag planning --tag decomposition --limit 12  # alias
  python pipeline/06_reflect/route.py --tag planning --limit 12 --threshold 3  # ADAPT split if <3
"""
import argparse, json, os, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
try:
    from agent_trace import emit as emit_trace
except ImportError:
    emit_trace = None
DB = ROOT / "knowledge" / "graph" / "graph.db"
TOPICS = ROOT / "knowledge" / "topics.md"

def query_ids(tags: list[str], limit: int) -> list[str]:
    if not DB.exists():
        raise SystemExit("graph.db missing — run build_graph.py")
    conn = sqlite3.connect(DB)
    # tags stored as JSON array string: '["icm","reflection"]' → LIKE '%"icm"%'
    where = " AND ".join(["tags LIKE ?" for _ in tags]) if tags else "1"
    params = [f'%"{t}"%' for t in tags] if tags else []
    sql = f"SELECT id FROM nodes WHERE {where} ORDER BY id LIMIT ?"
    rows = conn.execute(sql, (*params, limit)).fetchall()
    conn.close()
    result = [r[0] for r in rows]
    if emit_trace:
        try:
            trace_id = emit_trace("retrieval", route={"tags": tags, "limit": limit}, returned_ids=result,
                                  selected_ids=[], expansion_depth=0)
            os.environ["AGENT_TRACE_LAST_RETRIEVAL"] = trace_id
        except OSError:
            pass
    return result

def load_topics() -> list[str]:
    if not TOPICS.exists():
        return []
    out=[]
    for line in TOPICS.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if line.startswith("- "):
            out.append(line[2:].strip())
    return sorted(set(out))

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", action="append", default=[], help="require tag (repeatable, intersection)")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--all-topics", action="store_true", help="emit one line per topic in topics.md: <topic> <count> [ids]")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-topics", type=int, default=4, help="auto-batch: cap topics per run (deterministic, sorted prefix)")
    ap.add_argument("--threshold", type=int, default=0, help="P2 ADAPT: if 0 disables; if >0 and result card < threshold and query has planning, split one level via alias tags")
    args=ap.parse_args()
    # P2 alias expansion (one level, flat — no recursion)
    ALIASES = ["decomposition", "htn", "pddl", "classical-planning"]
    def maybe_expand(tags: list[str], ids: list[str]) -> tuple[list[str], int, str]:
        depth = 0
        expanded_via = ""
        if args.threshold and len(ids) < args.threshold and any(t in ("planning", "decomposition", "htn", "pddl") for t in tags):
            # try each alias intersection deterministically; first hit wins
            for alias in ALIASES:
                cand_tags = sorted(set(tags + [alias]))
                cand = query_ids(cand_tags, args.limit)
                if cand:
                    # union with original, dedup ordered by id
                    merged = sorted(set(ids + cand))
                    if len(merged) > len(ids):
                        return merged, 1, alias
            # fallback: try alias alone
            for alias in ALIASES:
                cand = query_ids([alias], args.limit)
                if cand:
                    merged = sorted(set(ids + cand))
                    if len(merged) > len(ids):
                        return merged, 1, alias
        return ids, depth, expanded_via
    if args.all_topics:
        res={}
        for t in load_topics()[:args.max_topics]:
            ids=query_ids([t], args.limit)
            ids, depth, via = maybe_expand([t], ids)
            res[t]=ids
            if args.json:
                continue
            extra = f" depth={depth} via={via}" if depth else ""
            print(f"{t} {len(ids)} {' '.join(ids)}{extra}")
        if args.json:
            print(json.dumps(res, indent=2))
        return 0
    ids=query_ids(args.tag, args.limit)
    ids, depth, via = maybe_expand(args.tag, ids)
    if args.tag and not ids:
        print(f"Error: tag intersection {args.tag} matched no chunks — a requested tag "
              f"is absent from the corpus vocabulary (see knowledge/topics.md)",
              file=sys.stderr)
        if args.json:
            print(json.dumps({"ids": [], "depth": depth, "via": via, "tags": args.tag,
                              "dead": True}, indent=2))
        return 2
    if args.json:
        print(json.dumps({"ids": ids, "depth": depth, "via": via, "tags": args.tag}, indent=2))
    else:
        for i in ids:
            print(i)
        if depth:
            print(f"# ADAPT depth={depth} via={via}", file=__import__("sys").stderr)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
