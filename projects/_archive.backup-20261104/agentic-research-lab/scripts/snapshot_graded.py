#!/usr/bin/env python3
"""snapshot_graded.py — copy graded artifacts aside before a gate reads them.

A gate that reports on a file it just read is a gate whose report can be
destroyed by whoever dislikes the result. This writes a timestamped copy of the
artifacts a gate is about to grade, so "the gate saw X" stays checkable after
the working copy is edited or removed.

The snapshot is the audit trail of last resort: if a run's artifacts vanish, the
snapshot still shows what was graded and therefore what the failure was.

    python scripts/snapshot_graded.py                       # digests + candidates
    python scripts/snapshot_graded.py --paths bg-smoke4     # only this run's output
    python scripts/snapshot_graded.py --label gate-failed   # tag the snapshot dir
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIGESTS = ROOT / "reflection" / "digests"
CANDIDATES = ROOT / "reflection" / "candidates"
SNAPSHOTS = ROOT / "reflection" / ".snapshots"
KEEP = 20


def targets(patterns: list[str]) -> list[Path]:
    if not patterns:
        return sorted(DIGESTS.glob("*.md")) + sorted(CANDIDATES.glob("*.jsonl"))
    out: list[Path] = []
    for pat in patterns:
        raw = Path(pat)
        base = raw if raw.is_absolute() else (ROOT / pat)
        if base.is_file():
            out.append(base)
        elif base.is_dir():
            out.extend(sorted(base.glob("*.md")) + sorted(base.glob("*.jsonl")))
        else:
            out.extend(sorted(DIGESTS.glob(f"{pat}.md")))
            out.extend(sorted(CANDIDATES.glob(f"{pat}.jsonl")))
    return [p for p in out if p.is_file()]


def prune() -> None:
    runs = sorted((d for d in SNAPSHOTS.iterdir() if d.is_dir()), key=lambda d: d.name)
    for stale in runs[:-KEEP]:
        shutil.rmtree(stale, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths", nargs="*", help="artifact paths/slugs to snapshot (default: all)")
    ap.add_argument("--label", default="gate", help="label recorded in the manifest")
    args = ap.parse_args()

    found = targets(args.paths)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    dest = SNAPSHOTS / f"{stamp}-{args.label}"
    dest.mkdir(parents=True, exist_ok=True)

    for src in found:
        out = dest / src.name
        if out.exists():
            out = dest / f"{src.stem}-{int(time.time() * 1000)}{src.suffix}"
        shutil.copy2(src, out)

    manifest = {
        "snapshot": dest.name,
        "label": args.label,
        "t": time.time(),
        "files": [p.name for p in found],
        "digests": [p.name for p in found if p.suffix == ".md"],
        "candidates": [p.name for p in found if p.suffix == ".jsonl"],
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    prune()
    print(f"[snapshot] {len(found)} artifact(s) -> reflection/.snapshots/{dest.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
