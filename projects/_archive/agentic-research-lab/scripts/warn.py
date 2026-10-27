#!/usr/bin/env python3
"""Warning-case retrieval: past failures relevant to the task at hand.

EXG-style online reuse over the workspace's own scar tissue. Sources, all
read-only:

- `reflection/repair_ledger.jsonl` entries with state `quarantined`
  (FailureEvent / Defect records with issue kind, repair, target);
- `reflection/candidates/*.jsonl` records with state `rejected`;
- `reflection/trace/events.jsonl` events with status `failed`;
- `reflection/stale/<generation>/` quarantined reflections (topic slugs).

Ranking is deterministic keyword overlap between task words and record text
(length > 2, stopwords removed); ties break by record id. No LLM judgment:
a warning is a pointer to a recorded failure, never a generated lesson.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "reflection" / "repair_ledger.jsonl"
CANDIDATES = ROOT / "reflection" / "candidates"
TRACE = ROOT / "reflection" / "trace" / "events.jsonl"
STALE = ROOT / "reflection" / "stale"

STOPWORDS = {
    "what", "how", "does", "the", "and", "for", "with", "from",
    "this", "that", "are", "was", "were", "been", "have", "has",
    "will", "would", "should", "could", "into", "over", "under",
}


def words(text: str) -> set[str]:
    return {
        w.lower()
        for w in re.findall(r"[A-Za-z0-9_]+", text)
        if len(w) > 2 and w.lower() not in STOPWORDS
    }


def collect() -> list[dict]:
    """All warning records as {id, source, text}."""
    out: list[dict] = []
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("state") != "quarantined":
                continue
            issues = " ".join(
                f"{i.get('kind', '')} {i.get('repair', '')} {i.get('target', '')}"
                for i in d.get("issues", [])
            )
            out.append({
                "id": str(d.get("id", "?")),
                "source": f"repair_ledger:{d.get('type', '?')}",
                "text": f"{d.get('category', '')} {issues} "
                        f"{d.get('validation_boundary', '')}".strip(),
            })
    if CANDIDATES.exists():
        for jl in sorted(CANDIDATES.glob("*.jsonl")):
            for line in jl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("state") != "rejected":
                    continue
                out.append({
                    "id": str(d.get("id", "?")),
                    "source": f"candidates:{jl.name}",
                    "text": f"{d.get('Rule', '')} "
                            f"{d.get('why', d.get('reason', ''))}".strip(),
                })
    if TRACE.exists():
        for line in TRACE.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("status") != "failed":
                continue
            out.append({
                "id": str(d.get("event_id", "?")),
                "source": "trace:failure",
                "text": f"{d.get('failure_kind', d.get('kind', ''))} "
                        f"{d.get('module', '')} {d.get('artifact', '')}".strip(),
            })
    if STALE.exists():
        for gen in sorted(p for p in STALE.iterdir() if p.is_dir()):
            files = sorted(p.name for p in gen.iterdir() if p.is_file())
            topics = sorted({f.split(".")[0] for f in files})
            out.append({
                "id": f"stale:{gen.name}",
                "source": "stale",
                "text": f"quarantined generation {gen.name}: "
                        f"{len(files)} files ({', '.join(topics[:6])})",
            })
    return out


def warnings_for(task: str, limit: int = 3) -> list[dict]:
    """Top-`limit` warnings ranked by keyword overlap with `task`."""
    task_words = words(task)
    ranked = []
    for rec in collect():
        overlap = sorted(task_words & words(f"{rec['id']} {rec['text']}"))
        if overlap:
            ranked.append((len(overlap), overlap, rec))
    ranked.sort(key=lambda t: (-t[0], t[2]["id"]))
    return [
        {"id": r["id"], "source": r["source"], "matched": m, "text": r["text"][:300]}
        for _, m, r in ranked[:limit]
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("task")
    ap.add_argument("--limit", type=int, default=3)
    args = ap.parse_args()
    print(json.dumps(warnings_for(args.task, args.limit), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
