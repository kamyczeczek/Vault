#!/usr/bin/env python3
"""
build_reflection_index.py — Deterministic index over MONITORING/reflection/.

The reflection brain provides deterministic, read-consulted prevention
knowledge alongside skills_brain:

- source of record: MONITORING/reflection/*.md (REFLECTION_RULES.md schema)
- this script: parses every schema-shaped reflection, extracts one
  entry per problem (id, title, invariant, owning_doc), derives
  deterministic FTS keywords, and writes reflection_index.json
- gen_digest.py renders the brain-local marker-delimited digest.md
- verify_reflection_sync.py is the freshness gate (pre-commit + probe)
- local summary cards remain derived index data, not private-store state

Stdlib only. No LLM. Output depends only on the reflection files.

Usage:
    python brain/build_reflection_index.py
    python brain/build_reflection_index.py --group-by-scar  # Alt-A (flag-off scaffold)
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
REFLECT = ROOT / "MONITORING" / "reflection"
OUT = BRAIN / "reflection_index.json"

# Schema-shaped reflections carry this header (REFLECTION_RULES.md R3) and
# a filename per R2: YYYY-MM-DD_HHMM_S-XX-slug.md
NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}_S-[A-Za-z0-9].*\.md$")
PROB_RE = re.compile(r"^(P\d+)(?::\s*(.*))?$")
FIELD_RE = re.compile(r"^- \*\*([a-z_]+):\*\*\s*(.*)$")
CARD_MAX = 2000  # char budget per per-file memory card (compact, FTS-
# friendly). 2026-09-04: raised from 1500 — the S-s19 card hit 1420 with
# 3 invariants and a 4th would truncate mid-invariant text; truncation
# breaks the byte-equality sync check (seeded card != index card) and
# renders the fuzzy-reinforce trap invisible (truncated near-matches
# reinforce too). Budget-checked: longest card 1420 at raise time.

TRACKED_FIELDS = ("symptom", "root_cause", "invariant", "owning_doc",
                  "owning_doc_updated", "family")
SECTIONS = ("problems", "solutions", "prevention_rules")

PROCEDURAL_FAMILIES = (
    "tool-interaction",
    "repo-hygiene",
    "protocol-domain",
    "knowledge-routing",
)

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "must", "when", "from",
    "into", "under", "over", "all", "any", "but", "not", "was", "were",
    "its", "via", "per", "after", "before", "each", "more", "than",
    "even", "only", "also", "would", "should", "have", "has", "had", "will",
}


def classify_family(entry: dict, stem: str = "") -> str:
    """Map one scar to its deterministic procedural family (SkillGLoW / D2).

    1. Explicit declaration in reflection frontmatter or problem rule wins.
    2. Fallback to deterministic token matching over owning_doc, invariant,
       title, and reflection filename stem.
    """
    fam = entry.get("family")
    if fam and fam in PROCEDURAL_FAMILIES:
        return fam

    doc = (entry.get("owning_doc") or "").lower()
    inv = (entry.get("invariant") or "").lower()
    title = (entry.get("title") or "").lower()
    st = stem.lower()

    # 1. tool-interaction (execution traps, shell syntax, tool argument schemas, preflights)
    if any(k in doc or k in inv or k in title or k in st for k in [
        "tool_preflight", "preflight", "edit-anchor", "python -c", "multiedit",
        "robocopy", "read-schema", "run-before-write", "cmd_quoting", "quoting",
        "command-position", "failure_ledger", "tool failure", "harness-hook",
        "tool-schema"
    ]):
        return "tool-interaction"

    # 2. repo-hygiene (git operations, staging, CRLF, packaging, workspace integrity)
    if any(k in doc or k in inv or k in title or k in st for k in [
        "repomix", "pack", "git", "crlf", "vscode", "clean-state",
        "submodule", "gitlink", "staged", "branch", "commit-echo", "pre-commit"
    ]):
        return "repo-hygiene"

    # 3. protocol-domain (TS-ML experiment protocols, sweep evaluation, registry constraints)
    if any(k in doc or k in inv or k in title or k in st for k in [
        "h720", "ts_brain", "ts-brain", "ts-ml", "forecast", "registry",
        "rolling", "elm", "leaderboard", "sweep", "validation_rows", "horizon"
    ]):
        return "protocol-domain"

    # 4. knowledge-routing (ICM navigation, brain sync, routing tables, memory channels)
    return "knowledge-routing"


def parse_reflection(lines: list[str]) -> list[dict]:
    """Extract one entry per problem (its prevention_rules block) from a
    schema-shaped reflection. Handles wrapped continuation lines."""
    out: list[dict] = []
    state = None
    cur_id: str | None = None
    cur: dict = {}
    last_field: str | None = None
    titles: dict[str, str] = {}

    def close() -> None:
        nonlocal cur_id, cur, last_field
        if state == "prevention_rules" and cur_id and cur.get("invariant"):
            title = cur.get("title") or titles.get(cur_id) or cur_id
            entry = {
                "id": cur_id,
                "title": title.strip(),
                "invariant": cur["invariant"].strip(),
                "owning_doc": (cur.get("owning_doc") or "").strip(),
            }
            if cur.get("family"):
                entry["family"] = cur["family"].strip()
            out.append(entry)
        cur_id, cur, last_field = None, {}, None

    for raw in lines:
        line = raw.rstrip("\n")
        if line.startswith("## "):
            close()
            state = line[3:].strip()
            continue
        if line.startswith("### ") and state in SECTIONS:
            close()
            m = PROB_RE.match(line[4:].strip())
            if m:
                cur_id = m.group(1)
                if m.group(2):
                    cur = {"title": m.group(2)}
                    if state == "problems":
                        titles[cur_id] = m.group(2)
                else:
                    cur = {}
            else:
                cur_id, cur = None, {}
            last_field = None
            continue
        if state in SECTIONS and cur_id:
            m = FIELD_RE.match(line.strip())
            if m:
                key = m.group(1)
                if key in TRACKED_FIELDS:
                    cur[key] = m.group(2).strip()
                    last_field = key
                    continue
            elif line.startswith("  ") and last_field:
                cur[last_field] = (cur[last_field] + " " + line.strip()).strip()
    close()
    return out


def keywords_for(entry: dict) -> list[str]:
    """Deterministic FTS keywords: owning_doc path tokens (last-first, most
    distinctive), then title content words, then invariant content words.
    Pure alphanumeric tokens only (FTS5 MATCH hazard for hyphens —
    problem 2026-08-28 fts5-query-crash). Capped at 8."""
    toks: list[str] = []
    doc = entry["owning_doc"].replace("`", "")
    for seg in reversed(re.split(r"[/\s§().]+", doc)):
        if re.fullmatch(r"[A-Za-z0-9._]+", seg) and not seg.startswith("."):
            toks.append(seg.rstrip("."))
    toks += re.findall(r"[A-Za-z][A-Za-z0-9]*", entry["title"])
    toks += re.findall(r"[A-Za-z][A-Za-z0-9]{3,}", entry["invariant"])
    seen: set[str] = set()
    out: list[str] = []
    for t in toks:
        lt = t.lower()
        if lt in seen or lt in STOPWORDS or len(lt) < 3:
            continue
        seen.add(lt)
        out.append(t)
        if len(out) >= 8:
            break
    return out


def make_file_card(stem: str, entries: list[dict]) -> str:
    """One compact memory card PER REFLECTION FILE (not per scar): the
    harness fuzzy-dedupes same-file sibling cards (shared prefix wins),
    so a per-file card is both dedup-safe and semantically nicer (the
    agent recalls the whole lesson set of one work item at once).
    Deterministic: same inputs -> same string."""
    date = stem.split("_", 1)[0]
    session = stem.split("_", 2)[2]
    head = (f"SCAR {session} ({date}, {len(entries)} invariant"
            f"{'s' if len(entries) != 1 else ''}): ")
    body = " | ".join(f"[{e['id']}] {e['invariant'].replace(chr(10), ' ')}"
                      for e in entries)
    tail = f" Source: MONITORING/reflection/{stem}.md"
    room = CARD_MAX - len(head) - len(tail)
    if len(body) > room:
        body = body[:room - 3].rsplit(" ", 1)[0] + "..."
    return head + body + tail


# -- Alternative A scaffolding (merged-card-per-scar, flag-off) -----------
# Design: MONITORING/reflection/2026-09-12_memory-sibling-mitigation-design.md §4 Alt A.
# Flag OFF by default; flipping it requires no re-plumbing, only setting the
# env var or passing --group-by-scar. INVARIANT: single-card-per-file holds
# until the flag is flipped (verified by card_count == file_count assertion
# in the non-grouped path — the reconciler keeps healing siblings until then).
GROUP_BY_SCAR_ENV = "REFLECTION_GROUP_BY_SCAR"


def group_by_scar_id(scars: list[dict]) -> dict[str, list[dict]]:
    """Group scars by canonical scar id (the S-… session token in the stem).

    Normalizes recurrence variants: stems like S-s21-hook-console-flash-recurrence
    map to base S-s21-hook-console-flash so sibling reflections (recurrence
    tightening the same invariant) collapse into one group. Future recurrence
    suffixes are also stripped (-recurrence, -recurrence-2, etc.).
    Deterministic, pure function — no I/O.
    """
    _REC_RE = re.compile(r"-recurrence(?:[-\d]*)?$")
    out: dict[str, list[dict]] = {}
    for s in scars:
        stem = s.get("stem", "")
        parts = stem.split("_", 2)
        scar_id = parts[2] if len(parts) == 3 else stem
        scar_id = _REC_RE.sub("", scar_id)
        out.setdefault(scar_id, []).append(s)
    return out


def make_merged_card(scar_id: str, entries: list[dict], stems: list[str]) -> str:
    """One CARD per scar-id GROUP (Alt-A). Merges sibling invariants.

    Body is ` | `-joined invariants in chronological (stem-sorted) order.
    Head carries date-range and group size; tail lists all stems.
    Respects CARD_MAX via truncation of older invariants first so the
    newest tightening remains verbatim. Deterministic, byte-exact.
    """
    stems_sorted = sorted(stems)
    # Derive date range from stems list (canonical), since entries lack stem field
    stem_dates = sorted(s.split("_", 1)[0] for s in stems_sorted if "_" in s)
    if stem_dates:
        uniq = sorted(set(stem_dates))
        date_range = uniq[0] if len(uniq) == 1 else f"{uniq[0]}..{uniq[-1]}"
    else:
        date_range = "unknown"
    n_inv = len(entries)
    n_ref = len(stems_sorted)
    head = f"SCAR {scar_id} ({date_range}, {n_inv} invariants — {n_ref} reflections): "
    body = " | ".join(f"[{e.get('id', 'P?')}] {str(e.get('invariant', '')).replace(chr(10), ' ')}"
                      for e in entries)
    tail = f" Source: {', '.join(f'MONITORING/reflection/{s}.md' for s in stems_sorted)}"
    room = CARD_MAX - len(head) - len(tail)
    if len(body) > room:
        keep = room - 3
        if keep < 50:
            body = body[:room - 3].rsplit(" ", 1)[0] + "..."
        else:
            body = "..." + body[-(keep):]
            body = body.split(" ", 1)[-1] if " " in body[3:] else body
            body = "..." + body[3:] if not body.startswith("...") else body
    return head + body + tail


def fingerprint_of(file_hashes: dict[str, str]) -> str:
    """12-hex fingerprint of the indexed reflection tree (name:sha16 pairs)."""
    blob = "\n".join(f"{n}:{file_hashes[n]}" for n in sorted(file_hashes))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def main() -> int:
    import argparse as _ap
    import os as _os
    _parser = _ap.ArgumentParser(add_help=False)
    _parser.add_argument("--group-by-scar", action="store_true",
                         help="Alt-A: emit one card per scar id (merge siblings)")
    _args, _ = _parser.parse_known_args()
    group_by_scar = _args.group_by_scar or _os.environ.get(GROUP_BY_SCAR_ENV, "").lower() in ("1", "true", "yes")
    if not REFLECT.is_dir():
        print(f"FAIL: {REFLECT} missing", file=sys.stderr)
        return 2
    files = sorted(p for p in REFLECT.glob("*.md") if NAME_RE.match(p.name))
    scars: list[dict] = []
    cards: list[dict] = []
    file_hashes: dict[str, str] = {}
    _group_entries: dict[str, list[dict]] = {}
    _group_stems: dict[str, list[str]] = {}
    _REC_SUFFIX_RE = re.compile(r"-recurrence(?:[-\d]*)?$")
    for p in files:
        text = p.read_text(encoding="utf-8")
        file_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        stem = p.name[:-3]
        session = stem.split("_", 2)[2]
        entries = parse_reflection(text.splitlines())
        if entries:
            if not group_by_scar:
                cards.append({
                    "stem": stem,
                    "session": session,
                    "invariants": [e["id"] for e in entries],
                    "card": make_file_card(stem, entries),
                })
            else:
                base_scar_id = _REC_SUFFIX_RE.sub("", session)
                _group_entries.setdefault(base_scar_id, []).extend(entries)
                _group_stems.setdefault(base_scar_id, []).append(stem)
        for e in entries:
            fam = classify_family(e, stem)
            scars.append({
                "stem": stem,
                "session": session,
                "id": e["id"],
                "title": e["title"],
                "invariant": e["invariant"],
                "owning_doc": e["owning_doc"],
                "family": fam,
                "keywords": keywords_for(e),
            })
    if group_by_scar:
        for scar_id in sorted(_group_entries):
            entries = _group_entries[scar_id]
            stems = sorted(_group_stems.get(scar_id, []))
            primary = stems[0] if stems else scar_id
            merged = make_merged_card(scar_id, entries, stems)
            cards.append({
                "stem": primary,
                "group_key": scar_id,
                "stems": stems,
                "session": scar_id,
                "invariants": [e["id"] for e in entries],
                "card": merged,
            })
    index = {
        "fingerprint": fingerprint_of(file_hashes),
        "file_count": len(files),
        "scar_count": len(scars),
        "card_count": len(cards),
        "files": {n: file_hashes[n] for n in sorted(file_hashes)},
        "families": {f: sum(1 for s in scars if s.get("family") == f) for f in PROCEDURAL_FAMILIES},
        "cards": cards,
        "scars": scars,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
        f.write("\n")
    mode = "grouped" if group_by_scar else "per-file"
    print(f"[reflection_index] {index['file_count']} schema-shaped reflection(s), "
          f"{index['scar_count']} scar(s) in {index['card_count']} card(s) [{mode}], "
          f"fingerprint {index['fingerprint']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
