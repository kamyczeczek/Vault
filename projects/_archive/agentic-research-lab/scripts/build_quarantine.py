#!/usr/bin/env python3
"""Build the list of corpus chunks degraded by extraction damage.

A chunk is quarantined when its text carries lost intra-word whitespace, which
makes FTS5 structurally blind to terms inside the damaged run: the chunk cannot
be found by the words it is supposed to contain.

Quarantine is **chunk-level, not source-level**. A first cut excluded whole
source families and turned out to discard 417 clean chunks to hide 419 damaged
ones — it threw away all 828 chunks of *Paradigms of AI Programming* and all
1,123 of *AIMA* over a single damaged chunk each, and it removed the
`causal-intervention` benchmark gold even though that chunk is undamaged. Damage
is concentrated in a few passages of a few books, not spread across them, so the
exclusion must be as narrow as the damage.

Writes `knowledge/graph/quarantine.json` listing quarantined chunk ids, consumed
by `ask.py` and `run_retrieval_benchmark.py`. The corpus is never modified:
quarantine is a retrieval-time exclusion, so damaged text stays on disk as
evidence and is re-admitted automatically if a source is ever re-ingested clean.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "knowledge" / "corpus"
OUT = ROOT / "knowledge" / "graph" / "quarantine.json"

sys.path.insert(0, str(ROOT / "scripts"))
import check_corpus_health as health  # noqa: E402


def damaged_chunks(corpus_dir: Path = CORPUS_DIR) -> dict[str, dict]:
    """Return {chunk_id: {source, glue_tokens}} for every damaged chunk."""
    out: dict[str, dict] = {}
    for path in sorted(corpus_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        glue = health.suspicious_runs(text)
        if not glue:
            continue
        head = text.split("---", 2)
        source = "unknown"
        if len(head) > 2 and "source:" in head[1]:
            source = head[1].split("source:", 1)[1].splitlines()[0].strip().strip('"')
        out[path.stem] = {"source": source[:80], "glue_tokens": len(glue)}
    return out


def main() -> int:
    stats = damaged_chunks()
    payload = {
        "generated_by": "scripts/build_quarantine.py",
        "detector": "scripts/check_corpus_health.py",
        "min_glue_len": health.MIN_GLUE_LEN,
        "granularity": "chunk",
        "chunk_ids": {cid: info for cid, info in sorted(stats.items())},
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    by_source: dict[str, int] = {}
    for info in stats.values():
        by_source[info["source"]] = by_source.get(info["source"], 0) + 1
    print(f"quarantine: {len(stats)} chunk(s), "
          f"{sum(i['glue_tokens'] for i in stats.values())} glue tokens")
    for source, count in sorted(by_source.items(), key=lambda kv: -kv[1]):
        print(f"    {count:5} chunks  {source[:66]}")
    print(f"  written to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
