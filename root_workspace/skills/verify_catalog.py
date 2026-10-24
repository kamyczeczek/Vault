#!/usr/bin/env python3
"""
verify_catalog.py — Deterministic integrity check for the skills catalog.

The routing surface is skills/SKILLS.md (a markdown table). The physical
source of truth is the set of skill folders on disk: every directory
under skills/ that contains a SKILL.md. This verifier enforces the
invariants that keep deterministic routing correct:

  1. MISSING-ROW  — every on-disk skill folder has a row in the catalog.
                    (A skill with no row is unreachable by catalog routing.)
  2. STALE-PATH   — every catalog row's Path points at a real directory
                    that contains a SKILL.md.
  3. NAME-MATCH   — each row's Skill name equals its folder name.

No LLM in the loop; plain parsing. Exit 0 = clean, exit 1 = drift,
exit 2 = the catalog file itself is missing/unparseable.

Usage:
    python skills/verify_catalog.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "skills" / "SKILLS.md"
SKILLS_DIR = ROOT / "skills"

# Matches a routing-table row: | skill-name | `skills/skill-name/` | desc |
ROW_RE = re.compile(
    r"^\|\s*(?P<name>[A-Za-z0-9][A-Za-z0-9-]*)\s*\|"
    r"\s*`(?P<path>[^`]+?)`\s*\|"
)


def catalog_rows() -> list[tuple[str, str]]:
    """Return [(skill_name, path), ...] parsed from the routing table."""
    if not CATALOG.exists():
        return []
    rows: list[tuple[str, str]] = []
    for line in CATALOG.read_text(encoding="utf-8", errors="replace").splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        name = m.group("name")
        path = m.group("path").strip().rstrip("/")
        # Skip the header/separator and any row whose 'name' is a column
        # label rather than a skill (the header has 'Skill', separator has '---').
        if name in ("Skill", "skill") or set(name) <= set("-: "):
            continue
        rows.append((name, path))
    return rows


def on_disk_skills() -> set[str]:
    """Return the set of skill folder names under skills/ that
    contain a SKILL.md (the workspace package contract)."""
    if not SKILLS_DIR.is_dir():
        return set()
    return {
        d.name
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    }


def main() -> int:
    if not CATALOG.exists():
        print(f"FAIL: catalog not found at {CATALOG}")
        return 2

    rows = catalog_rows()
    disk = on_disk_skills()
    if not rows:
        print(f"FAIL: no routing-table rows parsed from {CATALOG} "
              f"(header/separator excluded).")
        return 2

    errors: list[str] = []

    # 1. MISSING-ROW: on-disk folder with no catalog row.
    row_names = {name for name, _ in rows}
    for name in sorted(disk - row_names):
        errors.append(f"MISSING-ROW: skill on disk but not in catalog: {name!r}")

    # 2. STALE-PATH + 3. NAME-MATCH: catalog row whose path is wrong.
    for name, path in rows:
        p = ROOT / path.replace("\\", "/")
        if not (p.is_dir() and (p / "SKILL.md").is_file()):
            errors.append(f"STALE-PATH: row {name!r} -> {path!r} has no "
                          f"SKILL.md on disk")
        elif p.name != name:
            errors.append(f"NAME-MATCH: row {name!r} points to folder "
                          f"{p.name!r}")

    # Duplicate rows (same skill listed twice).
    seen: set[str] = set()
    for name, _ in rows:
        if name in seen:
            errors.append(f"DUP-ROW: {name!r} listed more than once")
        seen.add(name)

    if errors:
        print(f"[verify_catalog] DRIFT DETECTED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        print(f"\nFix skills/SKILLS.md so every skills/<name>/ folder "
              f"has exactly one row with a valid path, then re-commit.")
        return 1

    print(f"[verify_catalog] OK — {len(rows)} catalog row(s), "
          f"{len(disk)} on-disk skill folder(s), all consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
