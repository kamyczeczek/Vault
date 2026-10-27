#!/usr/bin/env python3
"""
check_catalog.py — RESEARCH/ shelf routing-table integrity gate.

The routing table in RESEARCH/CONTEXT.md is the deterministic router for
standalone research records (S4). Per the workspace doctrine (scar S-s12
P2: "a routing surface without a verifier is a silent mis-router"), the
table is not trusted on declaration: this gate re-validates the table
against the disk at commit time and blocks the commit on drift.

Checks (fail-loud, exit 1 on any violation):
  1. record shape   — every non-`_` subfolder of RESEARCH/ is a record:
                      name matches RECORD_NAME_RE, the three canonical
                      artifacts exist non-empty, README.md carries all
                      five frontmatter keys, frontmatter id == folder
                      name, status is legal.
  2. table rows     — every routing-table row has exactly 4 fields, a
                      unique R-NN id, and a record name matching
                      RECORD_NAME_RE.
  3. table <-> disk — every row's record exists on disk; every record
                      with status done/superseded appears in at least
                      one row (coverage: an unrouted finished record is
                      a silent routing hole).
  4. supersede      — supersedes: <id> targets exist (or 'none'); no
                      cycle in the supersedes chain.

Informational (printed, never fatal):
  * live referrers — tracked-looking text files outside RESEARCH/ that
    still mention the pre-cutover shared paths
    PROCESS/02_research/{findings,open_questions,references}.md, so a
    referrer drift surfaces in the commit log.

Usage:
    python RESEARCH/check_catalog.py            # full report
    python RESEARCH/check_catalog.py --quiet    # silent on pass
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHELF = ROOT / "RESEARCH"
CONTRACT = SHELF / "CONTEXT.md"
ROW_RE = re.compile(r"^\|\s*(R-\d+)\s*\|")
RECORD_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---", re.S)
CANONICAL = ("findings.md", "open_questions.md", "references.md")
STATUS_LEGAL = ("in-progress", "done", "superseded")
FM_KEYS = ("id", "date", "scenario", "surface", "status", "supersedes")
STALE_REF_RE = re.compile(
    r"PROCESS/02_research/(?:findings|open_questions|references)\.md")

# Tracked-text extensions we scan for stale referrers (informational).
REFERRER_EXTS = {".md", ".py", ".ts", ".js", ".json", ".bat", ".ps1", ".toml"}
REFERRER_SKIP_DIRS = {".git", ".jcode", "brains", "node_modules", "skills",
                      "projects", "_factory"}


def parse_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not ROW_RE.match(line.strip()):
            continue
        fields = [f.strip() for f in line.strip().strip("|").split("|")]
        rows.append(fields)
    return rows


def parse_frontmatter(readme: Path) -> dict[str, str]:
    text = readme.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def record_dirs() -> list[Path]:
    return sorted(
        d for d in SHELF.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )


def main() -> int:
    quiet = "--quiet" in sys.argv
    if not CONTRACT.is_file():
        print("FAIL: RESEARCH/CONTEXT.md missing", file=sys.stderr)
        return 1
    rows = parse_rows(CONTRACT.read_text(encoding="utf-8"))
    errors: list[str] = []

    # 1. record shape
    records: dict[str, dict[str, str]] = {}
    for d in record_dirs():
        if not RECORD_NAME_RE.match(d.name):
            errors.append(f"record {d.name!r}: folder name violates "
                          f"RECORD_NAME_RE")
        for artifact in CANONICAL:
            p = d / artifact
            if not p.is_file() or not p.read_text(encoding="utf-8",
                                                  errors="replace").strip():
                errors.append(f"record {d.name!r}: {artifact} missing "
                              f"or empty")
        readme = d / "README.md"
        if not readme.is_file():
            errors.append(f"record {d.name!r}: README.md missing")
            continue
        fm = parse_frontmatter(readme)
        missing = [k for k in FM_KEYS if k not in fm]
        if missing:
            errors.append(f"record {d.name!r}: frontmatter missing "
                          f"{missing}")
        if "id" in fm and fm["id"] != d.name:
            errors.append(f"record {d.name!r}: frontmatter id "
                          f"{fm['id']!r} != folder name")
        if fm.get("status") not in STATUS_LEGAL:
            errors.append(f"record {d.name!r}: illegal status "
                          f"{fm.get('status')!r}")
        records[d.name] = fm

    # 2. table rows
    seen_ids: set[str] = set()
    row_records: set[str] = set()
    for f in rows:
        rid = f[0]
        if len(f) != 4:
            errors.append(f"{rid}: expected 4 fields, got {len(f)}: {f}")
            continue
        if not RECORD_NAME_RE.match(f[2]):
            errors.append(f"{rid}: record {f[2]!r} violates RECORD_NAME_RE")
        if rid in seen_ids:
            errors.append(f"{rid}: duplicate row id")
        seen_ids.add(rid)
        row_records.add(f[2])

    # 3. table <-> disk
    for rec in row_records:
        if rec not in records:
            errors.append(f"routing row points at record {rec!r} which "
                          f"does not exist on disk")
    for name, fm in records.items():
        if fm.get("status") in ("done", "superseded") and name not in row_records:
            errors.append(f"record {name!r} is {fm.get('status')} but has "
                          f"no routing row (coverage hole)")

    # 4. supersede links + cycle check
    for name, fm in records.items():
        sup = fm.get("supersedes", "none")
        if sup and sup != "none":
            if sup not in records:
                errors.append(f"record {name!r}: supersedes target "
                              f"{sup!r} does not exist")
    def chain(recurse_ok: bool) -> bool:
        for name in records:
            seen: set[str] = set()
            cur = name
            while cur in records and records[cur].get("supersedes", "none") != "none":
                cur = records[cur].get("supersedes", "none")
                if cur in seen:
                    return True
                seen.add(cur)
        return False
    if chain(True):
        errors.append("supersedes chain contains a cycle")

    if errors:
        print("FAIL: RESEARCH/ routing catalog:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print(f"{len(errors)} violation(s). Fix the table or the records, "
              f"then re-run.", file=sys.stderr)
        return 1

    # Informational: stale referrers outside the shelf.
    stale: list[str] = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in REFERRER_EXTS:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith("RESEARCH/") or rel.startswith("PROCESS/"):
            continue
        if any(part in REFERRER_SKIP_DIRS for part in p.parts[1:2]):
            continue
        try:
            if STALE_REF_RE.search(p.read_text(encoding="utf-8",
                                                errors="replace")):
                stale.append(rel)
        except OSError:
            continue
    if stale:
        print("[check_catalog] NOTE: stale referrers to pre-cutover "
              f"PROCESS/02_research shared artifacts ({len(stale)}):")
        for rel in stale:
            print(f"  - {rel}")

    if not quiet:
        print(f"[check_catalog] OK — {len(rows)} routing row(s), "
              f"{len(records)} record(s), all linked, supersede acyclic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
