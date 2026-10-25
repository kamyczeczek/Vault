#!/usr/bin/env python3
"""Shared Agent Memory Index — session-fed FTS5 knowledge base.

Ingests all session files from registered agents, chunks them into
retrievable units, and stores them in a SQLite FTS5 index for fast
keyword search. Designed to be queried by agents to find root causes,
past decisions, and recurring errors.

Usage:
  python scripts/memory_index.py ingest [--days N]   # build / refresh index (all history by default)
  python scripts/memory_index.py query "error text"  # search, one line per hit
  python scripts/memory_index.py get <chunk_id>      # one chunk in full
  python scripts/memory_index.py freshness           # exit 1 if not verified
  python scripts/memory_index.py stats               # index health summary
  python scripts/memory_index.py stats --usage       # query/get usage telemetry

Every `query` and `get` appends one JSON line to the usage telemetry
(`scripts/_scratch/sessions/05_store/queries.jsonl` — derived, gitignored, like
`memory.db`); `stats --usage` reports what was queried and what missed.

Run these with the Windows interpreter (`python.exe`). Under this repo's MSYS
shell `python3` is WSL's, where `Path.home()` is /home/<user> and no agent store
resolves — `freshness` then reports that it could not compare anything.
"""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "scripts" / "_scratch" / "sessions" / "05_store" / "memory.db"
# Usage telemetry (level 1): one JSON line per `query`/`get` — the gitignored
# twin of memory.db, derived runtime state, never source.
TELEMETRY_PATH = DB_PATH.parent / "queries.jsonl"

# ---------------------------------------------------------------------------
# Curated shelf — the workspace's own lessons, indexed alongside the raw
# transcripts. These are the highest-signal, already-digested facts in the
# repo (scars, decisions, the vocabulary, tool grades, principles, the
# handoff contract, and the open-work flags). They are "reference material"
# (factory), so the index re-reads them on every ingest and re-stamps them as
# agent "curated" — a synthetic agent, not a real session store. A debugging
# agent that asks "has this broken before?" reaches this shelf on the same
# query that reaches a raw transcript.
#
# CURATED_BOOST is the additive nudge (lower bm25 = more relevant) applied to
# recalled curated chunks when no type filter is set. It is deliberately
# measured, not assumed: the R15 retrieval eval is the adversarial case
# (a curated chunk may displace the expected *session*). See stats --usage.
# ---------------------------------------------------------------------------
CURATED_SOURCES = [
    "SCARS.md",
    "DECISIONS.md",
    "GLOSSARY.md",
    "TOOLS.md",
    "PHILOSOPHY.md",
    "handoff/CONTEXT.md",
]
CURATED_BOOST = 1.0
CURATED_AGENT = "curated"

# ---------------------------------------------------------------------------
# Durable exclusions — meta-sessions about the session-export / index
# machinery itself. They are not knowledge about the workspace: they carry the
# same terms as the retrieval eval (provider error, FTS5, ...) and re-adding
# them dropped the eval 15/15 -> 13/15 on 2026-10-23. `--exclude-session-id` is
# per-run, so the next ingest undid it; this list is checked in and applied by
# every reader of "sessions on disk" — ingest (which also purges any rows
# already stored), freshness, and the drift checker. Add an id with a one-line
# reason; re-run eval_memory_retrieval.py before removing one.
# ---------------------------------------------------------------------------
EXCLUDED_SESSION_IDS = {
    "ses_ea98f264dffeeYaikj3FJUVZz1": "meta-session: .bat building raw_sessions.md",
    "ses_eb2c4e7e1ffevIcPu2UCaaWYVu": "meta-session: R15 repair and session 6 close-out",
    "01a14d3f-d533-70d4-a56c-bc0a86ba7388": "meta-session: instructions for a fresh agent (cleanup)",
    "01a14d44-6b35-7486-b04e-dff16a7c8c53": "meta-session: instructions for a fresh agent (close-out)",
    "ses_e997f9f91ffewuLps3BjtP7AOI": "meta-session: durable exclusion implementation (2026-10-23)",
}


def is_excluded(session_id: str) -> bool:
    """True when a session is on the durable meta-session exclusion list."""
    return session_id in EXCLUDED_SESSION_IDS


def filter_excluded(sessions: List[SessionItem]) -> List[SessionItem]:
    """Drop durably excluded meta-sessions; every "on disk" reader uses this."""
    return [s for s in sessions if not is_excluded(s.id)]


def purge_excluded(con: sqlite3.Connection) -> int:
    """Delete already-indexed excluded sessions so the list is authoritative.

    Without this an index built before the list existed would keep the rows
    forever: `ingest` skips them on the way in, but never removes what is
    already in the derived store. Returns the number of sessions_meta rows
    removed (their chunks leave `memory_fts` in the same transaction).
    """
    ids = list(EXCLUDED_SESSION_IDS)
    if not ids:
        return 0
    placeholders = ",".join("?" * len(ids))
    n = con.execute(
        f"SELECT COUNT(*) FROM sessions_meta WHERE session_id IN ({placeholders})", ids
    ).fetchone()[0]
    con.execute(f"DELETE FROM memory_fts WHERE session_id IN ({placeholders})", ids)
    con.execute(f"DELETE FROM sessions_meta WHERE session_id IN ({placeholders})", ids)
    con.commit()
    return n


# Reuse agent_sessions loaders by importing the module
sys.path.insert(0, str(ROOT / "scripts"))
from agent_sessions import get_all_sessions, fmt_ts, SessionItem  # noqa: E402

# ---------------------------------------------------------------------------
# Chunk extraction
# ---------------------------------------------------------------------------

# Patterns that signal interesting content worth indexing
_ERROR_RE = re.compile(
    r"(error|exception|traceback|failed|failure|crash|timeout|"
    r"błąd|wyjątek|niepowodzenie|nie dzia\u0142a)",
    re.IGNORECASE,
)
_DECISION_RE = re.compile(
    r"(decision|chose|decided|implemented|naprawiono|zdecydowano|"
    r"rozwiązanie|fixed|solution|approach|implemented|zmieniono)",
    re.IGNORECASE,
)
_TOOL_RE = re.compile(r"^\s*(>\s+\*\*tool|##\s*\[MODEL\s*·)", re.IGNORECASE | re.MULTILINE)


_REASONING_RE = re.compile(r"<details><summary>reasoning</summary>.*?</details>", re.DOTALL | re.IGNORECASE)
_TOOL_OUTPUT_RE = re.compile(r"^\s*(>\s+\*\*tool|##\s*\[MODEL\s*·).*", re.DOTALL | re.MULTILINE | re.IGNORECASE)


def _classify_chunk(text: str) -> str:
    """Return a rough chunk type for display."""
    # Strip internal reasoning blocks and raw tool invocations to avoid false-positive decisions
    clean_text = _REASONING_RE.sub("", text)
    clean_text = _TOOL_OUTPUT_RE.sub("", clean_text).strip()

    if _ERROR_RE.search(clean_text or text):
        return "error"
    if clean_text and _DECISION_RE.search(clean_text):
        return "decision"
    if _TOOL_RE.search(text):
        return "tool"
    return "content"


def _extract_chunks(session: SessionItem, max_chunk_chars: int = 800) -> List[dict]:
    """Split a session's markdown into retrievable chunks with deduplication."""
    text = session.text_markdown
    if not text:
        return []

    # Split by markdown headings
    sections = re.split(r"\n(?=#{1,3} )", text)
    chunks = []
    seen_hashes = set()
    chunk_idx = 0

    def add_chunk(body_text: str, stype: str):
        nonlocal chunk_idx
        cleaned_body = body_text.strip()
        if not cleaned_body:
            return
        h = hashlib.sha256(cleaned_body.encode("utf-8")).hexdigest()
        if h in seen_hashes:
            return
        seen_hashes.add(h)
        chunks.append(_make_chunk(session, cleaned_body, chunk_idx, stype))
        chunk_idx += 1

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Strip internal reasoning and tool blocks at the section level
        # so that if a section is split, the fragments don't trigger false positives.
        clean_section = _REASONING_RE.sub("", section)
        clean_section = _TOOL_OUTPUT_RE.sub("", clean_section).strip()

        # Classify the section based on its clean content
        section_type = "content"
        if _ERROR_RE.search(clean_section or section):
            section_type = "error"
        elif clean_section and _DECISION_RE.search(clean_section):
            section_type = "decision"
        elif _TOOL_RE.search(section):
            section_type = "tool"

        # If section is short enough, keep as-is
        if len(section) <= max_chunk_chars:
            add_chunk(section, section_type)
        else:
            # Split into paragraphs
            paragraphs = re.split(r"\n\n+", section)
            buf = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(buf) + len(para) + 2 > max_chunk_chars and buf:
                    add_chunk(buf, section_type)
                    buf = para
                else:
                    buf = f"{buf}\n\n{para}" if buf else para
            if buf.strip():
                add_chunk(buf, section_type)

    return chunks


def _make_chunk(session: SessionItem, body: str, idx: int, chunk_type: str) -> dict:
    chunk_id = f"{session.agent}::{session.id[:12]}::{idx}"
    first_line = body.splitlines()[0][:120].strip() if body else ""
    return {
        "chunk_id": chunk_id,
        "agent": session.agent,
        "session_id": session.id,
        "session_title": session.title,
        "session_date": session.updated_at or session.created_at or "",
        "raw_path": session.raw_path,
        "chunk_type": chunk_type,
        "heading": first_line,
        "body": body,
    }


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS sessions_meta (
    session_id   TEXT PRIMARY KEY,
    agent        TEXT,
    title        TEXT,
    session_date TEXT,
    raw_path     TEXT,
    ingested_at  TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    chunk_id    UNINDEXED,
    agent       UNINDEXED,
    session_id  UNINDEXED,
    session_title,
    session_date UNINDEXED,
    raw_path    UNINDEXED,
    chunk_type  UNINDEXED,
    heading,
    body,
    tokenize = "unicode61 remove_diacritics 1"
);
"""


def open_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(DDL)
    con.commit()
    return con


def _already_ingested(con: sqlite3.Connection, session_id: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sessions_meta WHERE session_id=?", (session_id,)
    ).fetchone()
    return row is not None


def _curated_session(key: str, text: str, now: str, path: Path) -> "SessionItem":
    """One reference document as a pseudo-session on the curated shelf."""
    return SessionItem(
        agent=CURATED_AGENT,
        id=f"curated::{key}",
        title=key,
        directory=str(path.parent),
        created_at=now,
        updated_at=now,
        message_count=0,
        model="",
        raw_path=str(path),
        text_markdown=text,
    )


def load_curated_sessions() -> List["SessionItem"]:
    """The curated shelf: root lessons + open-work flags, re-read on every ingest.

    These are reference material (factory, not product), so they are re-stamped
    as a synthetic agent ('curated') rather than being one-shot like transcripts.
    """
    items: List[SessionItem] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for rel in CURATED_SOURCES:
        p = ROOT / rel
        if p.is_file():
            items.append(_curated_session(
                rel, p.read_text(encoding="utf-8", errors="replace"), now, p))
    flag_dir = ROOT / "handoff" / "flags"
    if flag_dir.is_dir():
        for fp in sorted(flag_dir.glob("*.md")):
            items.append(_curated_session(
                f"flag:{fp.stem}",
                fp.read_text(encoding="utf-8", errors="replace"), now, fp))
    return items


def ingest_curated_shelf(con: sqlite3.Connection) -> int:
    """Rebuild the curated shelf (wipe + re-index). Reference material, not transcripts.

    Always rebuilds so a changed SCARS.md / new flag is picked up; a transcript's
    one-shot '_already_ingested' skip does not apply here.
    """
    con.execute("DELETE FROM memory_fts WHERE agent = ?", (CURATED_AGENT,))
    con.execute("DELETE FROM sessions_meta WHERE agent = ?", (CURATED_AGENT,))
    total = 0
    for session in load_curated_sessions():
        total += ingest_session(con, session)
    con.commit()
    return total


def ingest_session(con: sqlite3.Connection, session: SessionItem) -> int:
    """Index one session; return number of chunks written."""
    if _already_ingested(con, session.id):
        return 0

    chunks = _extract_chunks(session)
    if session.agent == CURATED_AGENT:
        for c in chunks:
            c["chunk_type"] = "curated"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con.execute(
        "INSERT OR REPLACE INTO sessions_meta VALUES (?,?,?,?,?,?)",
        (session.id, session.agent, session.title,
         session.updated_at or session.created_at or "", session.raw_path, now),
    )
    con.executemany(
        "INSERT INTO memory_fts VALUES (?,?,?,?,?,?,?,?,?)",
        [
            (
                c["chunk_id"], c["agent"], c["session_id"],
                c["session_title"], c["session_date"], c["raw_path"],
                c["chunk_type"], c["heading"], c["body"],
            )
            for c in chunks
        ],
    )
    con.commit()
    return len(chunks)


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def _evidence_snippet(body: str, words: List[str], max_chars: int = 400) -> str:
    """Return the most relevant paragraph from body for the given query words."""
    lowered = [w.lower() for w in words if len(w) > 2]
    paragraphs = [p.strip() for p in re.split(r"\n\n+", body) if p.strip()]
    if not paragraphs:
        return body[:max_chars]

    best_score, best_para = -1, paragraphs[0]
    for para in paragraphs:
        score = sum(para.lower().count(w) for w in lowered)
        if score > best_score:
            best_score, best_para = score, para

    snippet = best_para[:max_chars]
    if len(best_para) > max_chars:
        snippet += "..."
    return snippet


def _sanitize_fts_term(term: str) -> str:
    """Sanitize and format a query term for FTS5 unicode61 tokenizer.

    Removes FTS5 syntax control chars, applies prefix matching * on alphanumeric terms.
    """
    clean = re.sub(r'["\'\*\^\:\(\)\{\}\~]', '', term).strip()
    if not clean:
        return ""
    # Prefix match on alphanumeric terms >= 3 chars
    if clean.isalnum() and len(clean) >= 3:
        return f'"{clean}"*'
    return f'"{clean}"'


def _build_fts_query(terms: List[str], op: str = "AND") -> str:
    parts = [_sanitize_fts_term(t) for t in terms]
    valid_parts = [p for p in parts if p]
    if not valid_parts:
        return ""
    return f" {op} ".join(valid_parts)


def get_context_chunks(
    con: sqlite3.Connection,
    agent: str,
    session_id: str,
    chunk_idx: int,
    count: int = 3,
) -> List[dict]:
    """Retrieve consecutive subsequent chunks N+1..N+count for the same session."""
    target_ids = [f"{agent}::{session_id[:12]}::{chunk_idx + offset}" for offset in range(1, count + 1)]
    placeholders = ",".join("?" for _ in target_ids)
    rows = con.execute(
        f"SELECT chunk_id, agent, session_id, session_title, session_date, raw_path, chunk_type, heading, body "
        f"FROM memory_fts WHERE chunk_id IN ({placeholders})",
        target_ids,
    ).fetchall()
    row_map = {r[0]: r for r in rows}
    context = []
    for tid in target_ids:
        if tid in row_map:
            r = row_map[tid]
            context.append({
                "chunk_id": r[0],
                "agent": r[1],
                "session_id": r[2],
                "session_title": r[3],
                "session_date": r[4],
                "raw_path": r[5],
                "chunk_type": r[6],
                "heading": r[7],
                "body": r[8],
            })
    return context


def query_memory(
    con: sqlite3.Connection,
    query_text: str,
    limit: int = 10,
    agent_filter: Optional[str] = None,
    chunk_type_filter: Optional[str] = None,
    with_context: bool = False,
    context_count: int = 3,
    boost_curated: bool = False,
) -> List[dict]:
    """Full-text search; return ranked result dicts with optional sequential context for errors."""
    raw_terms = [t for t in query_text.split() if t]
    if not raw_terms:
        return []

    where_clauses = ["memory_fts MATCH ?"]
    params: list = []

    if agent_filter and agent_filter != "all":
        where_clauses.append("agent = ?")
        params.append(agent_filter)
    if chunk_type_filter:
        where_clauses.append("chunk_type = ?")
        params.append(chunk_type_filter)

    # The curated shelf (agent 'curated': root lessons + open-work flags) is a
    # separate, opt-in surface, not part of the default session pool. It is
    # EXCLUDED from an unfiltered, un-boosted query — the exact shape the R15
    # retrieval bench uses to measure *session* recall — so the hard gate is
    # unaffected by the shelf by construction. A recalled shelf row that merely
    # shares keywords with a session would otherwise displace the expected
    # session out of the top-5 and fail the bench for a non-cause. The shelf
    # is recalled only when the caller names it (chunk_type_filter=='curated')
    # or opts into promotion (boost_curated=True — the door, scripts/debug.py),
    # where it is pinned to the front of the page (sign-independent, only
    # already-recalled rows move, so it cannot mask a stale index: R14 still
    # answers coverage, not ranking).
    if chunk_type_filter is None and not boost_curated:
        where_clauses.append("chunk_type != 'curated'")

    where = " AND ".join(where_clauses)
    sql = f"""
        SELECT chunk_id, agent, session_id, session_title, session_date,
               raw_path, chunk_type, heading, body,
               bm25(memory_fts) AS score
        FROM memory_fts
        WHERE {where}
        ORDER BY score
        LIMIT ?
    """

    def run(match: str, query_limit: int) -> list:
        if not match:
            return []
        return con.execute(sql, [match, *params, query_limit]).fetchall()

    # Request more rows if deduping to ensure `limit` unique or diversified items
    fetch_limit = limit * 3
    and_query = _build_fts_query(raw_terms, op="AND")
    rows = run(and_query, fetch_limit)
    if not rows and len(raw_terms) > 1:
        or_query = _build_fts_query(raw_terms, op="OR")
        rows = run(or_query, fetch_limit)

    results = []
    seen_sessions: Dict[str, int] = {}
    for row in rows:
        sid = row[2]
        # Keep at most 2 hits per session to avoid single-session monopolization
        if seen_sessions.get(sid, 0) >= 2:
            continue
        seen_sessions[sid] = seen_sessions.get(sid, 0) + 1

        item = {
            "chunk_id": row[0],
            "agent": row[1],
            "session_id": row[2],
            "session_title": row[3],
            "session_date": row[4],
            "raw_path": row[5],
            "chunk_type": row[6],
            "heading": row[7],
            "body": row[8],
            "score": row[9],
        }
        if with_context and item["chunk_type"] == "error":
            item["context"] = get_context_chunks(con, item["agent"], item["session_id"], int(item["chunk_id"].split("::")[-1]), context_count)
        results.append(item)
        if len(results) >= limit:
            break

    if boost_curated:
        # Opt-in (door only): pin up to int(CURATED_BOOST) already-recalled
        # curated chunks to the front of the page, preserving bm25 order for
        # the rest. Only chunks bm25 already ranked are moved — this can never
        # surface a chunk a stale index failed to hold, so it does not mask R14.
        pin = int(CURATED_BOOST)
        if pin > 0:
            curated_front = [r for r in results if r["chunk_type"] == "curated"][:pin]
            rest = [r for r in results if r not in curated_front]
            results = curated_front + rest

    return results


def format_results(results: List[dict], query: str) -> str:
    """Format results as compact agent-readable text (the --full view)."""
    if not results:
        return f"[memory] No results for: {query!r}"
    lines = [
        f"[memory] Query: {query!r}  — {len(results)} result(s)",
        "=" * 72,
    ]
    for i, r in enumerate(results, 1):
        body = r.get("snippet") or _evidence_snippet(
            r.get("body") or "", [t for t in query.split() if t]
        )
        lines += [
            f"\n#{i}  [{r['agent']}] {r['session_title']}",
            f"    Chunk  : {r['chunk_id']}",
            f"    Date   : {r['session_date']}",
            f"    Type   : {r['chunk_type']}",
            f"    Heading: {r['heading'][:80]}",
            f"    Source : {r['raw_path']}",
            "    ---",
            f"    {body}",
            "    ---",
        ]
        if r.get("context"):
            lines.append("    [Context N+1..N+k:]")
            for c in r["context"]:
                lines.append(
                    f"      + {c['chunk_id']} ({c['chunk_type']}): {c['heading'][:70]}"
                )
    return "\n".join(lines)


def format_brief(results: List[dict], query: str) -> str:
    """One line per hit — the default survey before drilling into a chunk."""
    if not results:
        return f"[memory] No results for: {query!r}"
    lines = [f"[memory] {query!r} — {len(results)} hit(s); drill: get <chunk_id>"]
    for i, r in enumerate(results, 1):
        heading = " ".join((r["heading"] or "").split())[:70]
        title = " ".join((r["session_title"] or "").split())[:38]
        ctx_tag = f" (+{len(r['context'])}ctx)" if r.get("context") else ""
        lines.append(
            f"#{i} {r['chunk_id']}  {r['session_date'][:16]}  {r['agent']}/{r['chunk_type']}{ctx_tag}"
            f"  | {title} | {heading}"
        )
    return "\n".join(lines)


def get_chunk(con: sqlite3.Connection, chunk_id: str) -> Optional[str]:
    """Return one chunk in full; None on a miss so the caller can exit non-zero."""
    row = con.execute(
        "SELECT chunk_id, agent, session_id, session_title, session_date, raw_path,"
        " chunk_type, heading, body FROM memory_fts WHERE chunk_id=?",
        (chunk_id,),
    ).fetchone()
    if row is None:
        return None
    return "\n".join([
        f"chunk_id : {row[0]}",
        f"agent    : {row[1]}   type: {row[6]}   date: {row[4]}",
        f"session  : {row[2]}  {row[3]}",
        f"source   : {row[5]}",
        f"heading  : {row[7]}",
        "--- body ---",
        row[8] or "",
    ])


def log_usage(entry: dict) -> None:
    """Append one JSON line to queries.jsonl for telemetry.

    Telemetry is observability, not a load-bearing path: a failed append warns
    on stderr and the command still runs (scripts/memory/CONTEXT.md).
    """
    now = datetime.now().isoformat()
    entry["ts"] = now
    entry["timestamp"] = now
    try:
        TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TELEMETRY_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[memory] usage telemetry not recorded: {e}", file=sys.stderr)


def print_usage() -> None:
    """Report usage telemetry from the queries.jsonl log."""
    if not TELEMETRY_PATH.exists():
        print(f"\nUsage telemetry: no events yet ({TELEMETRY_PATH})")
        return
    events: List[dict] = []
    with TELEMETRY_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not events:
        print(f"\nUsage telemetry: {TELEMETRY_PATH} holds no events")
        return
    queries = [e for e in events if e.get("cmd") == "query"]
    gets = [e for e in events if e.get("cmd") == "get"]
    zero = sum(1 for e in queries if e.get("hits", 0) == 0)
    stamps = [e.get("ts") or e.get("timestamp") for e in events]
    stamps = [s for s in stamps if s]
    first, last = (min(stamps), max(stamps)) if stamps else ("?", "?")
    terms: Counter = Counter(
        word.lower() for e in queries for word in (e.get("query") or "").split()
    )
    top = ", ".join(f"{t}×{c}" for t, c in terms.most_common(8))
    print(f"\nUsage telemetry: {TELEMETRY_PATH}")
    print(f"  Events    : {len(events)} (query {len(queries)}, get {len(gets)})")
    if queries:
        print(f"  Zero-hit  : {zero}/{len(queries)} queries returned nothing")
    print(f"  Window    : {first} → {last}")
    if top:
        print(f"  Top terms : {top}")


# ---------------------------------------------------------------------------
# Freshness / Stats
# ---------------------------------------------------------------------------

def freshness(max_lag_hours: float = 24.0) -> int:
    """Exit 1 if index lags behind newest session on disk by more than max_lag_hours.

    Degradation contract (gate docstring + scripts/memory/CONTEXT.md): a check
    that cannot run must never pass silently and must not fail silently either.
      - no index, no sessions on disk  → OK (fresh clone; nothing to be stale about)
      - no index, sessions on disk     → STALE (say how to fix)
      - index holds sessions but this interpreter read none of the agent stores
        → UNVERIFIED (exit 1, say so explicitly — the WSL `python3` case)
    """
    if not DB_PATH.exists():
        probe = filter_excluded(get_all_sessions(limit_per_agent=500, days=None))
        if not probe:
            print("OK — no index and no sessions on disk (nothing to be stale about)")
            return 0
        print(
            f"STALE — no index at {DB_PATH}, but agent stores hold sessions. "
            f"Fix: python.exe scripts/memory_index.py ingest"
        )
        return 1

    try:
        con = open_db()
        row = con.execute(
            "SELECT MAX(session_date) FROM sessions_meta WHERE session_date != ''"
        ).fetchone()
        indexed_agents = [r[0] for r in con.execute("SELECT DISTINCT agent FROM sessions_meta")]
        con.close()
    except Exception as e:
        print(f"UNVERIFIED — index at {DB_PATH} unreadable: {e}")
        return 1
    idx_newest = row[0] if row else None

    # Get all sessions from all agents and find the newest mtime. Durable
    # exclusions never count as "on disk" for freshness: an excluded newest
    # session is intentionally absent from the index, not lag.
    all_sessions = filter_excluded(get_all_sessions(limit_per_agent=500, days=None))

    if not all_sessions:
        if idx_newest:
            print(
                f"UNVERIFIED — the index at {DB_PATH} holds sessions for "
                f"{', '.join(sorted(indexed_agents))} (through {idx_newest}), but this "
                f"interpreter ({sys.executable}, home {Path.home()}) read none of "
                f"their stores, so the lag was never compared. Fix: run with the "
                f"Windows interpreter — `python.exe scripts/memory_index.py "
                f"freshness` — not the WSL `python3`."
            )
            return 1
        print("OK — no index sessions and no sessions on disk (nothing to be stale about)")
        return 0

    disk_newest = None
    for s in all_sessions:
        ts_str = s.updated_at or s.created_at
        if ts_str:
            try:
                dt = datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
                if disk_newest is None or dt > disk_newest:
                    disk_newest = dt
            except Exception:
                pass

    if disk_newest is None:
        print(
            f"UNVERIFIED — {len(all_sessions)} sessions on disk carry no parseable "
            f"timestamp, so the lag was never compared. Fix: run with the Windows "
            f"interpreter — `python.exe scripts/memory_index.py freshness`."
        )
        return 1

    if not idx_newest:
        print(f"STALE — index at {DB_PATH} holds no dated session. Fix: python.exe scripts/memory_index.py ingest --rebuild")
        return 1
    idx_dt = datetime.strptime(idx_newest[:19], "%Y-%m-%d %H:%M:%S")
    lag = disk_newest - idx_dt
    if lag > timedelta(hours=max_lag_hours):
        print(f"FAIL: index newest={idx_dt} disk newest={disk_newest} lag={lag} > {max_lag_hours}h")
        return 1
    print(f"OK — index covers through {idx_dt}; newest on disk {disk_newest} (lag {lag})")
    return 0


def stats(show_usage: bool = False) -> int:
    """Print index statistics."""
    try:
        con = open_db()
        # Sessions
        row = con.execute("SELECT COUNT(*) FROM sessions_meta").fetchone()
        n_sessions = row[0] if row else 0
        # Chunks
        row = con.execute("SELECT COUNT(*) FROM memory_fts").fetchone()
        n_chunks = row[0] if row else 0
        # Date range
        row = con.execute("SELECT MIN(session_date), MAX(session_date) FROM sessions_meta").fetchone()
        date_range = f"{row[0]} → {row[1]}" if row and row[0] and row[1] else "N/A"

        print(f"Memory index: {DB_PATH}")
        print(f"  Sessions  : {n_sessions}")
        print(f"  Chunks    : {n_chunks}")
        print(f"  Date range: {date_range}")

        # By agent
        print()
        print("  By agent:")
        rows = con.execute("SELECT agent, COUNT(*) FROM sessions_meta GROUP BY agent ORDER BY COUNT(*) DESC").fetchall()
        for agent, count in rows:
            print(f"    {agent:<14} {count} sessions")

        # By chunk type
        print()
        print("  By chunk type:")
        rows = con.execute("SELECT chunk_type, COUNT(*) FROM memory_fts GROUP BY chunk_type ORDER BY COUNT(*) DESC").fetchall()
        for ctype, count in rows:
            print(f"    {ctype:<10} {count} chunks")

        if show_usage:
            print_usage()
            if TELEMETRY_PATH.exists():
                all_events: List[dict] = []
                with TELEMETRY_PATH.open(encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            d = json.loads(line)
                        except Exception:
                            continue
                        all_events.append(d)

                # --- Usage-rate metrics (measured, not asserted) -----------
                print()
                print("    Usage-rate metrics:")

                # 1) zero-hit rate: of the runs that reported a hit count,
                #    how many found nothing. High => the base lacks the
                #    knowledge the agent sought (a gap, not a query bug).
                hit_events = [d for d in all_events if "hits" in d]
                zero_hits = sum(1 for d in hit_events if d.get("hits", 0) == 0)
                if hit_events:
                    print(f"    zero_hit_rate: {zero_hits}/{len(hit_events)} "
                          f"({zero_hits / len(hit_events):.1%})")
                else:
                    print("    zero_hit_rate: n/a (no query runs logged yet)")

                # 2) dead chunks: how much of the corpus has never been
                #    retrieved via a `get`/`debug-get` event. A large dead
                #    share means the index is breadth without recall value.
                retrieved_ids = {
                    d["chunk_id"] for d in all_events
                    if d.get("cmd") in ("get", "debug-get") and d.get("chunk_id")
                    and d.get("found", True) is not False
                }
                total_chunks = con.execute("SELECT COUNT(*) FROM memory_fts").fetchone()[0]
                dead = max(0, total_chunks - len(retrieved_ids))
                dead_pct = (dead / total_chunks) if total_chunks else 0.0
                print(f"    chunks: {total_chunks} total, {len(retrieved_ids)} ever "
                      f"retrieved, {dead} never (dead {dead_pct:.1%} of corpus)")

                # 3) prevented-repeat proxy: of the runs the agent closed with
                #    an explicit outcome, how many the past actually helped.
                outcomes = Counter(d.get("outcome") for d in all_events
                                   if d.get("outcome"))
                if outcomes:
                    helped = outcomes.get("helped", 0)
                    print(f"    prevented_repeat (helped/closed): "
                          f"{helped}/{sum(outcomes.values())} "
                          f"({helped / sum(outcomes.values()):.1%})  "
                          f"{dict(outcomes)}")
                else:
                    print("    prevented_repeat: n/a (no closed-loop outcomes logged yet)")
            else:
                print("    (no telemetry file)")

        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(prog="memory_index")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # ingest
    p_ing = sub.add_parser("ingest", help="Ingest session files into the memory index")
    p_ing.add_argument("--days", type=int, default=0,
                       help="Only ingest sessions from last N days; 0 means all history (default: 0)")
    p_ing.add_argument("--agent", default="all",
                       help="Filter by agent (default: all)")
    p_ing.add_argument("--rebuild", action="store_true",
                       help="Wipe the index before ingesting (full rebuild)")
    p_ing.add_argument("--limit", type=int, default=500,
                       help="Max sessions per agent (default: 500)")
    p_ing.add_argument("--exclude-session-id", default=None,
                       help="Skip a specific session by ID (e.g. current active session)")
    p_ing.add_argument("--include-runtime", action="store_true",
                       help="Include DSH runtime sessions (~/.dsh/sessions/) in the memory corpus. "
                            "Default: exclude them (runtime logs are not knowledge).")

    # query
    p_q = sub.add_parser("query", help="Search the memory index")
    p_q.add_argument("query", nargs="+", help="Query terms")
    p_q.add_argument("--limit", type=int, default=8, help="Max results (default: 8)")
    p_q.add_argument("--agent", default=None, help="Filter by agent")
    p_q.add_argument("--type", dest="chunk_type", default=None,
                     choices=["error", "decision", "tool", "content", "curated"],
                     help="Filter by chunk type")
    p_q.add_argument("--json", dest="as_json", action="store_true",
                     help="Output raw JSON instead of formatted text")
    p_q.add_argument("--with-context", action="store_true",
                     help="Include following chunks N+1..N+3 for error chunks")
    p_q.add_argument("--full", dest="full", action="store_true",
                     help="Print a 400-char evidence paragraph per hit (~15 lines "
                          "of context each). The default is the one-line survey, "
                          "because the safe path has to be the cheap one.")

    # get
    p_get = sub.add_parser("get", help="Print one chunk in full by chunk_id")
    p_get.add_argument("chunk_id", help="e.g. opencode::ses_efc4a483::0")

    # freshness
    p_fresh = sub.add_parser("freshness", help="Exit 1 if the index misses recent sessions")
    p_fresh.add_argument("--max-lag-hours", type=float, default=24.0,
                         help="Fail when the newest session on disk is older than the "
                              "index by more than this (default: 24)")

    # stats
    p_stats = sub.add_parser("stats", help="Show index statistics")
    p_stats.add_argument("--usage", action="store_true",
                         help="Also report query/get usage telemetry (queries.jsonl)")

    args = ap.parse_args()

    if args.cmd == "freshness":
        sys.exit(freshness(args.max_lag_hours))

    con = open_db()

    # ------------------------------------------------------------------
    if args.cmd == "ingest":
        if args.rebuild:
            con.execute("DROP TABLE IF EXISTS memory_fts")
            con.execute("DROP TABLE IF EXISTS sessions_meta")
            con.executescript(DDL)
            con.commit()
            print("Index wiped for full rebuild.")

        purged = purge_excluded(con)
        if purged:
            print(f"  Purged : {purged} durably excluded meta-session(s) from the index")

        print(f"Loading sessions (last {args.days} days, agent={args.agent})...")
        sessions = get_all_sessions(args.agent, limit_per_agent=args.limit, days=args.days)
        if args.exclude_session_id:
            sessions = [s for s in sessions if s.id != args.exclude_session_id]
        if not args.include_runtime:
            sessions = [s for s in sessions if ".dsh/sessions" not in s.raw_path and ".dsh\\sessions" not in s.raw_path]
        before_durable = len(sessions)
        sessions = filter_excluded(sessions)
        n_durable = before_durable - len(sessions)
        found = f"  Found {len(sessions)} sessions"
        if n_durable:
            found += f" ({n_durable} durably excluded meta-session(s))"
        print(found + ". Indexing...")

        total_chunks = 0
        skipped = 0
        for s in sessions:
            n = ingest_session(con, s)
            if n == 0:
                skipped += 1
            total_chunks += n

        print(f"  Indexed: {total_chunks} chunks from {len(sessions) - skipped} new sessions")
        print(f"  Skipped: {skipped} already-indexed sessions")

        # Rebuild the curated shelf (root lessons + flags) after transcripts.
        n_curated = ingest_curated_shelf(con)
        print(f"  Curated shelf: {n_curated} chunks from the {len(CURATED_SOURCES)} root lessons + handoff/flags")
        print(f"  DB     : {DB_PATH}")

        # Schema-drift assertion (E1 / scar S68): the newest session of every
        # store that has records on disk must be in the index we just wrote. A
        # loader that silently returned zero rows for a non-empty store is the
        # S68 shape — a hard FAIL that names the store and its expected tables.
        # Run as a subprocess so the checker re-loads the stores itself and a
        # timeout/crash is contained; it shares the durable exclusion list, but
        # still sees a session that `--exclude-session-id` kept out of the index
        # (the shift case). See scripts/memory_index_check_drift.py.
        drift = None
        try:
            drift = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "memory_index_check_drift.py"), "--check"],
                capture_output=True, text=True, check=False, timeout=120,
            )
        except subprocess.TimeoutExpired:
            print("  Drift  : FAILED — drift check did not finish within 120s")
            con.close()
            return 1
        drift_out = (drift.stdout or drift.stderr).strip()
        if drift.returncode != 0:
            print(drift_out)
            print("  Drift  : FAILED — a store's newest session is missing from the index")
            con.close()
            return 1
        print(f"  Drift  : {drift_out.splitlines()[-1] if drift_out else 'skipped (no index)'}")

    # ------------------------------------------------------------------
    elif args.cmd == "query":
        query_text = " ".join(args.query)
        results = query_memory(
            con,
            query_text,
            limit=args.limit,
            agent_filter=args.agent,
            chunk_type_filter=args.chunk_type,
            with_context=args.with_context,
        )
        log_usage(
            {
                "cmd": "query",
                "query": query_text,
                "limit": args.limit,
                "agent": args.agent,
                "type": args.chunk_type,
                "hits": len(results),
            }
        )
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.full:
            print(format_results(results, query_text))
        else:
            print(format_brief(results, query_text))

    # ------------------------------------------------------------------
    elif args.cmd == "get":
        chunk = get_chunk(con, args.chunk_id)
        if chunk is None:
            print(f"Chunk not found: {args.chunk_id}")
            # A mis-drilled get must leave a trace (CONTEXT.md "Usage telemetry"):
            # log the miss, then fail.
            log_usage({"cmd": "get", "chunk_id": args.chunk_id, "found": False})
            return 1
        print(chunk)
        log_usage(
            {
                "cmd": "get",
                "chunk_id": args.chunk_id,
                "found": True,
            }
        )

    # ------------------------------------------------------------------
    elif args.cmd == "stats":
        stats(show_usage=args.usage)

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
