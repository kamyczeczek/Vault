#!/usr/bin/env python3
"""memory_index_check_drift.py — per-agent store schema-drift assertion (E1 / scar S68).

Why this exists (S68)
---------------------
opencode 2.0 moved its sessions to `session_v2` + `session_message`, but
`load_opencode_sessions` still read the v1 `session`/`message`/`part` tables, so
every 2.0 session was *silently* absent from the memory index and from
`last_session.bat` — no error, no WARN, just zero rows. The 10 non-opencode
stores share the shape: each reads a *fixed* table name (SQLite) or a *fixed*
JSON key/glob, and none can tell "this store has no sessions" apart from "the
schema moved and I am reading the wrong rows". `B1-drift-surface.md` maps the
surface; this is the assertion that tells those two apart.

The assertion, one question per agent
-------------------------------------
    the newest session this store *has on disk* is in the index
    (`scripts/_scratch/sessions/05_store/memory.db`, table `sessions_meta`).

Definitions (fixed so the assertion is deterministic and cannot false-FAIL):

* "store X has sessions on disk" is answered by a RAW probe that does **not**
  import the production loader — a row count for the expected SQLite table(s),
  or a file count for the expected glob(s). A store that is absent (fresh clone)
  is skipped: there is nothing to drift.
* "the newest session in X" is the first session the production loader returns
  for X under the same newest-first sort `memory_index.py ingest` uses
  (`updated_at or created_at`, descending) and the same filters (500/agent,
  all history, `.dsh/sessions` runtime excluded, durable meta-session
  exclusions removed). The loader is the same object that fed the index, so
  this compares like with like.
* "is in the index" = a `sessions_meta` row with that `session_id`. That table is
  the authoritative "this session was ingested" marker: a session with zero
  extractable chunks still gets a row, while a session the loader never returned
  has none.

Failure modes (both hard, both name the store + its expected tables/keys):

* **silent skip** — the raw probe counts >= 1 record but the loader returned zero
  sessions for X: the S68 shape (`if not events: continue` in deepseek, the bare
  `except: pass` in cursor, the swallowed `OperationalError` in goose/hermes).
* **drift** — the newest loaded session is absent from `sessions_meta`: it was
  seen on disk but never indexed.

**Out of scope.** `.dsh/sessions` runtime transcripts and the sessions on
`memory_index.EXCLUDED_SESSION_IDS` are excluded from the index by `ingest`
(D21 and the 2026-10-23 meta-session policy), so they are excluded here too: a
store whose only records fall in either class is SKIPped, not asserted — drift
on an intentionally-unindexed session is not drift.

`--drift-only` reports only the two schema conditions above (silent skip /
missing table) and not the "newest is indexed" staleness condition; the integrity
gate's R22 uses it, because staleness is R14's question while the hard caller —
`memory_index.py ingest` — runs the full assertion.

This script **detects** silent loss; it never "fixes" a loader (that would hide
the failure it exists to surface).

Usage:
    python.exe scripts/memory_index_check_drift.py --check   # exit 1 on drift
    python.exe scripts/memory_index_check_drift.py --check --agent deepseek
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "scripts" / "_scratch" / "sessions" / "05_store" / "memory.db"

sys.path.insert(0, str(ROOT / "scripts"))
import agent_sessions  # noqa: E402  (module attr is looked up at call time)
import memory_index  # noqa: E402  (shares the durable meta-session exclusion list)
from agent_sessions import SUPPORTED_AGENTS, get_all_sessions  # noqa: E402


@dataclass(frozen=True)
class StoreProbe:
    """How one store's "does it hold sessions on disk" is answered, raw.

    `path` is a callable so the value is read at call time — the loader and this
    probe then agree even when a test points the store at a fixture by patching
    `agent_sessions.<DIR>`.
    """
    agent: str
    kind: str                               # "sqlite" | "dir"
    expected: str                           # human description: tables / glob+keys
    path: Callable[[], Path]
    tables: Tuple[str, ...] = ()            # sqlite: expected table names
    key_like: Optional[Tuple[str, str, str]] = None   # sqlite: (table, col, LIKE prefix)
    patterns: Tuple[str, ...] = ()          # dir: globs that count as records


STORE_REGISTRY: Dict[str, StoreProbe] = {
    "opencode": StoreProbe(
        "opencode", "sqlite",
        "tables session_v2/session, session_message/message/part",
        lambda: agent_sessions.OPENCODE_DB, tables=("session_v2", "session")),
    "goose": StoreProbe(
        "goose", "sqlite", "tables sessions, messages",
        lambda: agent_sessions.GOOSE_DB, tables=("sessions",)),
    "hermes": StoreProbe(
        "hermes", "sqlite", "tables sessions, messages",
        lambda: agent_sessions.HERMES_DB, tables=("sessions",)),
    "cursor": StoreProbe(
        "cursor", "sqlite",
        "tables cursorDiskKV (LIKE 'composerData:%'), composerHeaders",
        lambda: agent_sessions.CURSOR_STATE_DB,
        tables=("composerHeaders", "cursorDiskKV"),
        key_like=("cursorDiskKV", "key", "composerData:%")),
    "pi": StoreProbe(
        "pi", "dir", "glob **/*.jsonl; keys type=session/message",
        lambda: agent_sessions.PI_DIR, patterns=("**/*.jsonl",)),
    "omp": StoreProbe(
        "omp", "dir", "glob **/*.jsonl; keys type=session/message",
        lambda: agent_sessions.OMP_DIR, patterns=("**/*.jsonl",)),
    "jcode": StoreProbe(
        "jcode", "dir", "glob *.json; keys id/title/messages",
        lambda: agent_sessions.JCODE_DIR, patterns=("*.json",)),
    "antigravity": StoreProbe(
        "antigravity", "dir", "glob **/transcript*.jsonl; key type=USER_INPUT",
        lambda: agent_sessions.ANTIGRAVITY_BRAIN, patterns=("**/transcript*.jsonl",)),
    "droid": StoreProbe(
        "droid", "dir", "glob **/*.jsonl; key type=message",
        lambda: agent_sessions.DROID_SESSIONS_DIR, patterns=("**/*.jsonl",)),
    "deepseek": StoreProbe(
        "deepseek", "dir", "glob *.jsonl / *.zstd; dispatch keys type/data",
        lambda: agent_sessions.DEEPSEEK_SESSIONS_DIR, patterns=("*.jsonl",)),
    "cline": StoreProbe(
        "cline", "dir", "glob **/*.messages.json; keys sessionId/messages",
        lambda: agent_sessions.CLINE_SESSIONS_DIR, patterns=("**/*.messages.json",)),
}


@dataclass
class Result:
    agent: str
    status: str      # "ok" | "skip" | "fail"
    detail: str


def raw_record_count(probe: StoreProbe) -> int:
    """Count session records from the store itself, independent of the loader.

    Returns:
        >= 0  records present on disk (0 = store is empty)
        -1    the store's expected table(s) do not exist — the schema moved
    """
    p = probe.path()
    if probe.kind == "dir":
        if not p.is_dir():
            return 0
        total = 0
        for pat in probe.patterns:
            total += sum(1 for _ in p.glob(pat))
        return total

    # sqlite
    if not p.is_file():
        return 0
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True, timeout=2)
    except sqlite3.Error:
        return 0  # cannot even open it — do not assert
    try:
        try:
            names = {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        except sqlite3.Error:
            return 0  # not readable as SQLite — do not assert
        found = False
        total = 0
        for t in probe.tables:
            if t in names:
                found = True
                total += con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        if not found and probe.key_like:
            t, col, pref = probe.key_like
            if t in names:
                found = True
                total += con.execute(
                    f'SELECT COUNT(*) FROM "{t}" WHERE "{col}" LIKE ?', (pref,)
                ).fetchone()[0]
        return total if found else -1
    except sqlite3.Error:
        return 0
    finally:
        con.close()


def in_index(con: sqlite3.Connection, session_id: str) -> bool:
    """A session is in the index iff `sessions_meta` holds its id.

    Fallback to a `memory_fts` chunk for an index written before `sessions_meta`
    existed, so an old-but-valid index is not read as drift.
    """
    try:
        row = con.execute(
            "SELECT 1 FROM sessions_meta WHERE session_id=? LIMIT 1", (session_id,)
        ).fetchone()
        if row is not None:
            return True
    except sqlite3.Error:
        pass
    try:
        row = con.execute(
            "SELECT 1 FROM memory_fts WHERE session_id=? LIMIT 1", (session_id,)
        ).fetchone()
        return row is not None
    except sqlite3.Error:
        return False


def evaluate(
    con: Optional[sqlite3.Connection],
    sessions: List,
    agents: Optional[List[str]] = None,
    registry: Optional[Dict[str, StoreProbe]] = None,
    drift_only: bool = False,
) -> List[Result]:
    """Return one Result per agent. `sessions` must be newest-first (get_all_sessions).

    With `drift_only`, only the schema conditions FAIL (silent skip / missing
    table); the "newest loaded session is indexed" condition is reported OK
    without checking membership, so ordinary staleness is not a failure.
    """
    registry = registry if registry is not None else STORE_REGISTRY
    agents = list(agents) if agents else [a for a in SUPPORTED_AGENTS if a in registry]

    newest: Dict[str, object] = {}
    for s in sessions:
        if s.agent not in newest:      # list is newest-first, so first hit wins
            newest[s.agent] = s

    results: List[Result] = []
    for ag in agents:
        probe = registry.get(ag)
        if probe is None:
            continue
        p = probe.path()
        present = p.is_file() if probe.kind == "sqlite" else p.is_dir()
        if not present:
            results.append(Result(ag, "skip", "store absent (fresh clone)"))
            continue

        raw = raw_record_count(probe)
        loaded = [s for s in sessions if s.agent == ag]

        if raw < 0:
            results.append(Result(
                ag, "fail",
                f"schema drift — none of the expected tables exist ({probe.expected}); "
                f"the store's schema moved and the loader would see nothing"))
            continue
        if raw > 0 and not loaded:
            results.append(Result(
                ag, "fail",
                f"silent skip — store holds {raw} session record(s) on disk "
                f"({probe.expected}) but the loader returned 0 sessions (S68 shape)"))
            continue
        if not loaded:
            results.append(Result(ag, "skip", "store present but empty on disk"))
            continue

        s = newest.get(ag)
        if s is None:
            results.append(Result(ag, "skip", "no loaded session"))
            continue
        if drift_only:
            # The schema is present and the loader read it. Membership is R14's
            # question, not this one (see the R22 caller in check_workspace_integrity).
            results.append(Result(ag, "ok", f"schema present ({raw} record(s) on disk)"))
            continue
        if con is None or not in_index(con, s.id):
            results.append(Result(
                ag, "fail",
                f"drift — newest session {s.id!r} ({s.raw_path}) is not in "
                f"sessions_meta; expected {probe.expected}. "
                f"Fix: python.exe scripts/memory_index.py ingest"))
            continue
        results.append(Result(ag, "ok", f"newest {s.id} indexed (raw on disk: {raw})"))
    return results


def load_sessions_like_ingest(include_runtime: bool = False,
                              days: int = 0, limit_per_agent: int = 500) -> List:
    """Load exactly what `memory_index.py ingest` loads under its defaults."""
    sessions = get_all_sessions("all", limit_per_agent=limit_per_agent, days=days)
    if not include_runtime:
        sessions = [s for s in sessions
                    if ".dsh/sessions" not in s.raw_path
                    and ".dsh\\sessions" not in s.raw_path]
    return memory_index.filter_excluded(sessions)


def _open_index(path: Path) -> Optional[sqlite3.Connection]:
    if not path.is_file():
        return None
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=2)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="memory_index_check_drift")
    ap.add_argument("--check", action="store_true",
                    help="assert every store's newest session is indexed; exit 1 on drift")
    ap.add_argument("--agent", default=None,
                    help=f"limit to one agent ({', '.join(SUPPORTED_AGENTS)})")
    ap.add_argument("--drift-only", action="store_true",
                    help="assert only schema drift (silent skip / missing table); "
                         "skip the 'newest is indexed' staleness condition (used by R22)")
    args = ap.parse_args(argv)

    if not DB_PATH.is_file():
        print(f"FAIL: no memory index at {DB_PATH} — nothing was verified. "
              f"Fix: python.exe scripts/memory_index.py ingest")
        return 1

    con = _open_index(DB_PATH)
    if con is None:
        print(f"FAIL: cannot open memory index at {DB_PATH}")
        return 1
    try:
        sessions = load_sessions_like_ingest()
        agents = [args.agent] if args.agent else None
        results = evaluate(con, sessions, agents=agents, drift_only=args.drift_only)
    finally:
        con.close()

    fails = 0
    for r in results:
        tag = {"ok": "OK  ", "skip": "SKIP", "fail": "FAIL"}[r.status]
        print(f"{tag} {r.agent:<12} {r.detail}")
        fails += r.status == "fail"
    checked = sum(r.status != "skip" for r in results)
    if fails:
        print(f"memory_index drift: {fails} FAIL, {checked} store(s) asserted")
        return 1
    print(f"memory_index drift: OK — {checked} store(s) asserted, no drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
