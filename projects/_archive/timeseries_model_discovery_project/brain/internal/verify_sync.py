#!/usr/bin/env python3
"""
verify_sync.py — Unified project brain sync verifier.

Validates that the project_brain corpus, graph, reflection index,
and skills index match their stored sidecar fingerprints.

Sidecar: brain/.last_build.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_THIS_FILE = Path(__file__).resolve()
BRAIN_DIR = _THIS_FILE.parent
ROOT_DIR = BRAIN_DIR.parent
REPO_ROOT = ROOT_DIR.parent

CORPUS_DIR = BRAIN_DIR / "corpus"
RAG_DB = BRAIN_DIR / "rag.db"
GRAPH_DB = BRAIN_DIR / "graph.db"
REFLECTION_INDEX = BRAIN_DIR / "reflection_index.json"
SKILLS_INDEX = BRAIN_DIR / "skills_index.json"
SIDECAR = BRAIN_DIR / ".last_build.json"

SIDECAR_VERSION = 1


@dataclass
class FileFingerprint:
    mtime: float
    size: int


@dataclass
class SyncReport:
    in_sync: bool
    corpus_count: int = 0
    corpus_changed: List[str] = field(default_factory=list)
    graph_changed: bool = False
    reflection_changed: bool = False
    skills_changed: bool = False


def _scan_corpus() -> Dict[str, FileFingerprint]:
    out: Dict[str, FileFingerprint] = {}
    if not CORPUS_DIR.exists():
        return out
    for path in sorted(CORPUS_DIR.iterdir()):
        if path.is_file():
            try:
                stat = path.stat()
                out[path.name] = FileFingerprint(
                    mtime=stat.st_mtime,
                    size=stat.st_size,
                )
            except OSError:
                continue
    return out


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_sidecar() -> Optional[dict]:
    if not SIDECAR.exists():
        return None
    try:
        return json.loads(SIDECAR.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _db_schema_hash(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        conn = sqlite3.connect(path)
        try:
            rows = conn.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            blob = "|".join(f"{name}:{sql or ''}" for name, sql in rows)
            return hashlib.sha256(blob.encode()).hexdigest()
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        return ""


def is_in_sync() -> SyncReport:
    sidecar = _load_sidecar()
    report = SyncReport(in_sync=True)

    corpus = _scan_corpus()
    report.corpus_count = len(corpus)
    if sidecar and isinstance(sidecar.get("corpus"), dict):
        for name, fp in corpus.items():
            stored = sidecar["corpus"].get(name)
            if not stored:
                report.corpus_changed.append(name)
                report.in_sync = False
                continue
            if stored.get("mtime") != fp.mtime or stored.get("size") != fp.size:
                report.corpus_changed.append(name)
                report.in_sync = False
    else:
        if corpus:
            report.in_sync = False
            report.corpus_changed.extend(list(corpus.keys()))

    graph_hash = _db_schema_hash(GRAPH_DB)
    if sidecar and isinstance(sidecar.get("graph"), dict):
        if sidecar["graph"].get("schema_hash") != graph_hash:
            report.graph_changed = True
            report.in_sync = False
    elif GRAPH_DB.exists():
        report.graph_changed = True
        report.in_sync = False

    reflection_hash = _file_hash(REFLECTION_INDEX) if REFLECTION_INDEX.exists() else ""
    if sidecar and isinstance(sidecar.get("reflection"), dict):
        if sidecar["reflection"].get("sha256") != reflection_hash:
            report.reflection_changed = True
            report.in_sync = False
    elif REFLECTION_INDEX.exists():
        report.reflection_changed = True
        report.in_sync = False

    skills_hash = _file_hash(SKILLS_INDEX) if SKILLS_INDEX.exists() else ""
    if sidecar and isinstance(sidecar.get("skills"), dict):
        if sidecar["skills"].get("sha256") != skills_hash:
            report.skills_changed = True
            report.in_sync = False
    elif SKILLS_INDEX.exists():
        report.skills_changed = True
        report.in_sync = False

    return report


def write_sidecar() -> Path:
    corpus = {}
    for name, fp in _scan_corpus().items():
        corpus[name] = {"mtime": fp.mtime, "size": fp.size}
    payload = {
        "version": SIDECAR_VERSION,
        "brain": "project_brain",
        "corpus": corpus,
        "graph": {
            "schema_hash": _db_schema_hash(GRAPH_DB),
        },
        "reflection": {
            "sha256": _file_hash(REFLECTION_INDEX) if REFLECTION_INDEX.exists() else "",
            "path": str(REFLECTION_INDEX),
        },
        "skills": {
            "sha256": _file_hash(SKILLS_INDEX) if SKILLS_INDEX.exists() else "",
            "path": str(SKILLS_INDEX),
        },
    }
    SIDECAR.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return SIDECAR


def _print_human(report: SyncReport) -> None:
    if report.in_sync:
        print(f"[verify_sync] project_brain in sync — {report.corpus_count} corpus files")
        return
    print("project_brain is STALE.", file=sys.stderr)
    if report.corpus_changed:
        print(f"  - {len(report.corpus_changed)} corpus file(s) modified: "
              f"{', '.join(report.corpus_changed)}", file=sys.stderr)
    if report.graph_changed:
        print("  - graph.db schema changed", file=sys.stderr)
    if report.reflection_changed:
        print("  - reflection_index.json changed", file=sys.stderr)
    if report.skills_changed:
        print("  - skills_index.json changed", file=sys.stderr)
    print("Rebuild the unified brain corpus/indices to fix staleness.", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Verify project_brain sync status.")
    parser.add_argument("--json", dest="json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--rebuild", action="store_true", help="Rewrite .last_build.json sidecar from current corpus/graph/reflection/skills state. This does NOT regenerate reflection_index.json or digest.md; run build_reflection_index.py + gen_digest.py first if reflections changed.")
    args = parser.parse_args(argv)

    if args.rebuild:
        write_sidecar()
        if not args.quiet:
            print(f"[verify_sync] rebuilt sidecar: {SIDECAR}")
        return 0

    report = is_in_sync()
    if args.json:
        print(json.dumps({
            "in_sync": report.in_sync,
            "corpus_count": report.corpus_count,
            "corpus_changed": report.corpus_changed,
            "graph_changed": report.graph_changed,
            "reflection_changed": report.reflection_changed,
            "skills_changed": report.skills_changed,
        }, indent=2))
        return 0 if report.in_sync else 1

    if not args.quiet:
        _print_human(report)
    return 0 if report.in_sync else 1


if __name__ == "__main__":
    raise SystemExit(main())
