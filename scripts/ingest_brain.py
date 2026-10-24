#!/usr/bin/env python3
"""ingest_brain.py — rebuild the curated brain layer of `brain/brain.db` from source files.

What this owns (the *curated reference* layer, as opposed to the session-transcript
layer owned by `scripts/memory_index.py`):

    brain/lessons.md  -> lessons     (one row per failure-condition group)
    DECISIONS.md      -> decisions   (one row per `## D<n> — ...` block)
    SCARS.md          -> problems    (one row per scar)

Why it exists
-------------
`brain/brain.db` is **gitignored** — it is a derived artifact, rebuildable only if
the transformation is a committed script. Its predecessor
(`scripts/_scratch/parse_and_ingest_v5.py`) was neither: it lived in `_scratch/`,
and it was wrong in two ways this script fixes.

  1. **It fabricated rows.** For every `S<n>` in the range 32..65 that it could not
     find as a `## S<n>` block it inserted `title='Scar S<n>'`,
     `fix='Mention of S<n> in SCARS.md'` — a row asserting content that does not
     exist. `S32`/`S33` are not entries at all; they are mentioned *inside* another
     scar's prose. 12 of the 24 rows in the table were these placeholders.
  2. **It only saw `## S<n>` blocks.** SCARS.md's dominant shape is the opposite:
     a flat list, one line per scar, with no heading. ~60 of the file's lines were
     silently dropped (0/10 sampled bullet fragments were in the DB), so the layer
     held ~37% of the file it claimed to represent.

Shape decision (owner, this session): scars stay in `problems` — no new table, no
`kind` column. `problems` already carries `title, root_cause, fix, scar, gate`, and
the "scar vs lesson" distinction the reader cares about is already the *table*
boundary (`problems` = operational scars, `lessons` = lessons). A second table would
split one file across two homes and two ingest paths.

Identity (`id`) is file-derived and stable, so the checked-in evaluation and the
FTS rowids survive a rebuild:

    decisions  -> id = the D-number (matches `decisions:1` in the gold set)
    scars      -> id = the S-number for `## S<n>` blocks and `- S<n>:` lines
                  id = 1000 + line order for the unnamed one-line scars
    lessons    -> id = 1..n in file order

Idempotence
-----------
Ingest rewrites the three source-backed tables inside one transaction (the FTS
tables are kept in sync by the existing `*_ai/*_ad/*_au` triggers). Running it
twice on the same sources produces the same rows — `--check` proves it.

CLI:
    python.exe scripts/ingest_brain.py            # rebuild
    python.exe scripts/ingest_brain.py --check    # exit 1 if brain.db is not the
                                                  # parse of the current sources
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("BRAIN_DB") or (ROOT / "brain" / "brain.db"))

SOURCES = {
    "lessons": "brain/lessons.md",
    "decisions": "DECISIONS.md",
    "problems": "SCARS.md",
}

# Unnamed one-line scars get ids from this base so they can never collide with an
# S-number (the file currently reaches S67).
UNNAMED_ID_BASE = 1000

# Bold field labels inside a `## S<n>` block -> the column they fill.
_SCAR_FIELD_LABELS = {
    "problem": "root_cause",
    "wniosek": "fix",
    "zasada": "fix",
    "zalecenie": "fix",
    "mechaniczna korekta": "fix",
    "reguła": "fix",
    "regula": "fix",
    "bramka": "gate",
    "gate": "gate",
}

# Inline rule marker inside an unnamed one-line scar. SCARS.md writes the colon
# *inside* the bold (`**Reguła:**`), but `**Reguła**:` also occurs — accept both.
_RULE_MARKER = re.compile(r"\*\*(Reguła|Regula|Zasada|Fix|Naprawione|Wniosek):?\*\*\s*:?\s*", re.I)
# Bold field label at the start of a line, colon inside or outside the bold.
_BLOCK_LABEL = re.compile(r"^-\s+\*\*([^*:]+):?\*\*\s*:?\s*(.*)$")
# A scar's leading "symptom" ends at its parenthetical date. Without a date, a colon
# only cuts the title when enough of the symptom precedes it — otherwise a scar like
# "`STATUS: OK` po sesji ..." would keep only the first word.
_TITLE_CUT = re.compile(r"\s*\((?:19|20)\d\d-\d\d-\d\d[^)]*\)")
_TITLE_MIN = 25


def _strip_md(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip()


def parse_lessons(text: str) -> list[dict]:
    """Group `- **Warunek porażki:** ... / **Przyczyna:** / **Mechaniczna korekta:**` triples."""
    groups: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        m = re.match(r"^-\s+\*\*(.+?):\*\*\s*(.*)$", line.strip())
        if not m:
            continue
        label, body = _strip_md(m.group(1)).lower(), m.group(2).strip()
        if "warunek" in label:
            cur = {"content": [f"Warunek porażki: {body}"]}
            groups.append(cur)
        elif cur is not None:
            cur["content"].append(f"{m.group(1).strip()}: {body}")
    return [
        {"id": i, "content": "\n".join(g["content"]), "source": SOURCES["lessons"]}
        for i, g in enumerate(groups, 1)
    ]


def parse_decisions(text: str) -> list[dict]:
    """One row per `## D<n> — title`. Last block wins for a duplicated D-number."""
    by_id: dict[int, dict] = {}
    blocks = re.split(r"\n(?=##\s+D\d+\s*[—\-])", text)
    for block in blocks:
        m = re.match(r"##\s+D(\d+)\s*[—\-]\s*(.+)", block.strip())
        if not m:
            continue
        d_id = int(m.group(1))
        by_id[d_id] = {
            "id": d_id,
            "title": m.group(2).strip(),
            "content": block.strip(),
            "source": SOURCES["decisions"],
        }
    return [by_id[k] for k in sorted(by_id)]


def parse_scars(text: str) -> list[dict]:
    """Every scar in SCARS.md: `## S<n>` blocks, `- S<n>:` lines, and unnamed one-line scars."""
    out: list[dict] = []
    seen_ids: set[int] = set()
    cur: dict | None = None
    field: str | None = None
    unnamed = 0

    def close_block() -> None:
        nonlocal cur, field
        if cur is not None and cur["id"] not in seen_ids:
            seen_ids.add(cur["id"])
            out.append(cur)
        cur, field = None, None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        head = re.match(r"^##\s+S(\d+)\s*:\s*(.+)$", line)
        if head:
            close_block()
            cur = {
                "id": int(head.group(1)),
                "title": head.group(2).strip(),
                "root_cause": "",
                "fix": "",
                "gate": "",
                "scar": f"S{head.group(1)}",
                "source": SOURCES["problems"],
            }
            field = None
            continue

        if line.startswith("#"):
            close_block()
            continue

        if cur is not None:
            label = _BLOCK_LABEL.match(line)
            if label:
                key = _SCAR_FIELD_LABELS.get(_strip_md(label.group(1)).lower())
                body = label.group(2).strip()
                if key:
                    cur[key] = f"{cur[key]} {body}".strip() if cur[key] else body
                    field = key
                else:
                    field = None
                continue
            if field:  # wrapped continuation of the current field
                cur[field] = f"{cur[field]} {line}".strip()
            continue

        named = re.match(r"^-\s+S(\d+)\s*:\s*(.*)$", line)
        if named:
            s_id = int(named.group(1))
            if s_id not in seen_ids:
                seen_ids.add(s_id)
                body = named.group(2).strip()
                out.append({
                    "id": s_id,
                    "title": body,
                    "root_cause": "",
                    "fix": body,
                    "gate": "",
                    "scar": f"S{s_id}",
                    "source": SOURCES["problems"],
                })
            continue

        if not line.startswith("- "):
            continue  # intro prose, not a scar

        body = line[2:].strip()
        date_cut = _TITLE_CUT.search(body)
        if date_cut:
            title = body[: date_cut.start()].strip()
        else:
            colon = body.find(": ")
            title = body[:colon].strip() if colon >= _TITLE_MIN else body
        marker = _RULE_MARKER.search(body)
        if marker:
            root_cause = body[: marker.start()].strip()
            fix = body[marker.end():].strip()
        else:
            root_cause = body
            fix = ""
        unnamed += 1
        out.append({
            "id": UNNAMED_ID_BASE + unnamed,
            "title": title[:300] or body[:300],
            "root_cause": root_cause,
            "fix": fix,
            "gate": "",
            "scar": "",
            "source": SOURCES["problems"],
        })
    close_block()
    return out


def read_sources() -> dict[str, list[dict]]:
    return {
        "lessons": parse_lessons((ROOT / SOURCES["lessons"]).read_text(encoding="utf-8")),
        "decisions": parse_decisions((ROOT / SOURCES["decisions"]).read_text(encoding="utf-8")),
        "problems": parse_scars((ROOT / SOURCES["problems"]).read_text(encoding="utf-8")),
    }


def _row_fingerprint(table: str, row: dict) -> str:
    if table == "lessons":
        payload = f"{row['id']}|{row['content']}"
    elif table == "decisions":
        payload = f"{row['id']}|{row['title']}|{row['content']}"
    else:
        payload = f"{row['id']}|{row['title']}|{row['root_cause']}|{row['fix']}|{row['gate']}|{row['scar']}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def rebuild(con: sqlite3.Connection) -> dict[str, int]:
    """Rewrite the three source-backed tables from the current sources."""
    parsed = read_sources()
    cur = con.cursor()
    counts: dict[str, int] = {}

    cur.execute("BEGIN")
    cur.execute("DELETE FROM lessons WHERE source = ?", (SOURCES["lessons"],))
    cur.execute("DELETE FROM decisions WHERE source = ?", (SOURCES["decisions"],))
    cur.execute("DELETE FROM problems WHERE source = ?", (SOURCES["problems"],))

    for row in parsed["lessons"]:
        cur.execute(
            "INSERT OR REPLACE INTO lessons (id, content, status, version, source, ingested_at) "
            "VALUES (?, ?, 'active', 1, ?, CURRENT_TIMESTAMP)",
            (row["id"], row["content"], row["source"]),
        )
    for row in parsed["decisions"]:
        cur.execute(
            "INSERT OR REPLACE INTO decisions (id, title, content, status, version, source, ingested_at) "
            "VALUES (?, ?, ?, 'active', 1, ?, CURRENT_TIMESTAMP)",
            (row["id"], row["title"], row["content"], row["source"]),
        )
    for row in parsed["problems"]:
        cur.execute(
            "INSERT OR REPLACE INTO problems "
            "(id, title, root_cause, fix, gate, scar, status, version, source, ingested_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'active', 1, ?, CURRENT_TIMESTAMP)",
            (row["id"], row["title"], row["root_cause"], row["fix"],
             row["gate"], row["scar"], row["source"]),
        )
    con.commit()

    for table in parsed:
        counts[table] = len(parsed[table])
    return counts


def check(con: sqlite3.Connection) -> int:
    """Exit 1 unless brain.db is exactly the parse of the current sources.

    This is both the freshness and the coverage check: a source line that stopped
    being parsed, or a DB row that no longer matches its source, is the same failure
    — the layer claims to hold a rule it no longer holds.
    """
    parsed = read_sources()
    cur = con.cursor()
    problems: list[str] = []

    for table, rows in parsed.items():
        expected = {r["id"]: _row_fingerprint(table, r) for r in rows}
        if table == "lessons":
            sel = "SELECT id, content FROM lessons WHERE source = ?"
        elif table == "decisions":
            sel = "SELECT id, title, content FROM decisions WHERE source = ?"
        else:
            sel = ("SELECT id, title, root_cause, fix, gate, scar FROM problems WHERE source = ?")
        actual: dict[int, str] = {}
        for db_row in cur.execute(sel, (SOURCES[table],)):
            keys = ("id", "content") if table == "lessons" else (
                ("id", "title", "content") if table == "decisions"
                else ("id", "title", "root_cause", "fix", "gate", "scar"))
            actual[db_row[0]] = _row_fingerprint(table, dict(zip(keys, db_row)))

        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        drifted = sorted(i for i in set(expected) & set(actual) if expected[i] != actual[i])
        if missing:
            problems.append(f"{table}: {len(missing)} source row(s) absent from brain.db: {missing[:8]}")
        if extra:
            problems.append(f"{table}: {len(extra)} row(s) in brain.db with no source (fabricated?): {extra[:8]}")
        if drifted:
            problems.append(f"{table}: {len(drifted)} row(s) drifted from source: {drifted[:8]}")
        if missing or extra or drifted:
            continue
        print(f"  - {table}: {len(expected)} row(s) match {SOURCES[table]}")

    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        print("Fix: python.exe scripts/ingest_brain.py")
        return 1
    print("OK — brain.db is the parse of the current lessons/decisions/scars sources")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="ingest_brain")
    ap.add_argument("--check", action="store_true",
                    help="verify brain.db matches the sources instead of rebuilding it")
    args = ap.parse_args()

    if not DB_PATH.exists() and args.check:
        print(f"STALE — no brain.db at {DB_PATH}. Fix: python.exe scripts/ingest_brain.py")
        return 1

    con = sqlite3.connect(str(DB_PATH))
    try:
        if args.check:
            return check(con)
        counts = rebuild(con)
    finally:
        con.close()
    for table, n in counts.items():
        print(f"  {table:<10} <- {SOURCES[table]:<20} {n} row(s)")
    print(f"OK — {DB_PATH} rebuilt from sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
