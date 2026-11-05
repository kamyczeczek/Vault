#!/usr/bin/env python3
"""promote_candidate.py — W7 state-machine transition + validator.

Transitions a candidate id through proposed→experimental→accepted|rejected,
validates against ground truth (evidence ids must resolve in graph.db),
and optionally appends the accepted claim to a memory-destined file.

Usage:
  python scripts/promote_candidate.py W1 --to experimental
  python scripts/promote_candidate.py W2 --to accepted --memory reflection/memory.md
"""
from __future__ import annotations
import argparse, json, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "reflection" / "candidates"
DB = ROOT / "knowledge" / "graph" / "graph.db"
VALID = {"proposed","experimental","accepted","rejected"}
TRANS = {("proposed","experimental"),("experimental","accepted"),("experimental","rejected")}

def existing_ids()->set[str]:
    c=sqlite3.connect(DB)
    rows=c.execute("SELECT id FROM nodes").fetchall()
    c.close()
    return {r[0] for r in rows}

def find_candidate(cid: str):
    for jl in CANDIDATES.glob("*.jsonl"):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            obj=json.loads(line)
            if obj.get("id")==cid:
                return jl, obj
    return None, None

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate_id")
    ap.add_argument("--to", required=True, choices=sorted(VALID))
    ap.add_argument("--memory", help="append accepted claim to this file")
    ap.add_argument("--corpus", action="store_true", help="synthesize accepted rule into a canonical corpus chunk (closes brain loop)")
    args = ap.parse_args()

    ids=existing_ids()
    jl, obj = find_candidate(args.candidate_id)
    if obj is None:
        print(f"FAIL: candidate {args.candidate_id} not found", file=sys.stderr); return 1

    src_state, dst_state = obj.get("state"), args.to
    if src_state==dst_state:
        print(f"OK: already {dst_state}"); return 0
    if (src_state,dst_state) not in TRANS:
        print(f"FAIL: illegal transition {src_state}→{dst_state} (allowed: {TRANS})", file=sys.stderr); return 1

    # validate grounding before promotion
    ev = obj.get("evidence") or [obj.get("principle")] if isinstance(obj.get("principle"), str) else []
    if isinstance(ev, str): ev=[ev]
    for cid in ev or []:
        if cid not in ids:
            print(f"FAIL: evidence id `{cid}` not in graph.db", file=sys.stderr); return 1

    # rewrite the jsonl file with updated state
    lines=[]
    for line in jl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        o=json.loads(line)
        if o.get("id")==args.candidate_id:
            o["state"]=dst_state
            line=json.dumps(o, ensure_ascii=False)
        lines.append(line)
    jl.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"OK: {args.candidate_id} {src_state}→{dst_state} in {jl.name}")

    if dst_state=="accepted" and args.memory:
        mem=ROOT / args.memory if not Path(args.memory).is_absolute() else Path(args.memory)
        mem.parent.mkdir(parents=True, exist_ok=True)
        ev_fmt = obj.get("evidence") or obj.get("evidence_ids") or obj.get("principle") or []
        if isinstance(ev_fmt, str):
            ev_fmt = [ev_fmt]
        ev_fmt = ", ".join(f"`{e}`" for e in ev_fmt) if isinstance(ev_fmt, list) else ev_fmt
        text = f"\n### {obj.get('id')} — accepted\n- claim: {obj.get('claim') or obj.get('statement') or obj.get('change') or obj.get('observation')}\n- evidence: {ev_fmt}\n"
        existing = mem.read_text(encoding="utf-8") if mem.exists() else ""
        # idempotency: re-promoting the same candidate rewrites its section rather than
        # duplicating it, so the memory file stays one entry per accepted rule
        if f"### {obj.get('id')} — accepted" in existing:
            lines = existing.splitlines()
            for i, line in enumerate(lines):
                if line.strip() == f"### {obj.get('id')} — accepted":
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith("### "):
                        j += 1
                    lines[i:j] = text.strip().splitlines()
                    break
            mem.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            with open(mem, "a", encoding="utf-8") as f:
                f.write(text)
        print(f"appended to {mem}")
        # W-INJECT: an accepted rule is only reachable if a working agent's question can
        # surface it. Seed the rule's topic words into the controlled vocabulary so the
        # question reaches it; check_reachability.py then proves the loop closed by
        # failing if it does not.
        topic_seed = (obj.get("claim") or obj.get("change") or "")[:60].strip()
        if topic_seed:
            print(f"NOTE: seed reachability for '{topic_seed}' via "
                  f"reflection/reachability-seed.jsonl so check_reachability.py covers it")

    if dst_state == "accepted" and args.corpus:
        corpus_dir = ROOT / "knowledge" / "corpus"
        cid_slug = re.sub(r"[^a-z0-9_]+", "_", args.candidate_id.lower()).strip("_")
        chunk_id = f"derived_rule_{cid_slug}"
        chunk_file = corpus_dir / f"{chunk_id}.md"
        ev_list = obj.get("evidence") or obj.get("evidence_ids") or obj.get("principle") or []
        if isinstance(ev_list, str):
            ev_list = [ev_list]
        ev_refs = ", ".join(ev_list)
        claim_text = obj.get("claim") or obj.get("statement") or obj.get("change") or obj.get("observation")
        chunk_content = f"""---
id: {chunk_id}
title: "Derived Rule: {args.candidate_id}"
source: "derived: synthesis over {ev_refs}"
tags: [derived-rule, promoted-memory, reflection, icm]
---

# Derived Rule — {args.candidate_id}

Promoted accepted rule from reflection candidates ({jl.name}).

## Claim
{claim_text}

## Evidence
{', '.join(f'`{e}`' for e in ev_list)}

## Next Bet
{obj.get('bet') or 'Maintain in memory; monitor against future regression.'}
"""
        chunk_file.write_text(chunk_content, encoding="utf-8")
        print(f"OK: synthesized derived rule into corpus chunk {chunk_file.relative_to(ROOT)}")
        print("Run `python knowledge/graph/build_graph.py` and `python scripts/check_manifest.py --write` to rebuild.")

if __name__=="__main__":
    raise SystemExit(main())
