"""retrieval_v1 — production FTS5 retrieval over `brain/brain.db` (validated config **K1**).

Owner-approved deployment (2026-10-15). Evidence and full analysis:
`tools/out/brain-db-and-wiki-report.md` §15–§20.

Configuration (this is the *validated* configuration — do not "improve" it silently):

  engine / ranking
      **B1** — the corrected top-5. Each `*_fts` table is queried once with
      ``fetchall()``, then the three candidate lists are merged and sorted by
      FTS5 rank. The pre-B1 bug (`scripts/_scratch/deep_audit_v2.py`) reused the
      same cursor inside the row loop (``SELECT source ... WHERE id = ?`` while
      iterating ``SELECT rowid, rank ...``), which reset the SELECT and left only
      the **top-1 row per table**. H5 on B0 regressed recall to 74.1%; B0 is not
      used here.

  query pipeline  (**K1 = the source fix**)
      tokenize -> drop words <= 2 chars -> **stem** -> drop stopwords **after**
      stemming -> sort (deterministic FTS OR-order).
      Applying stopwords *after* the stemmer is the whole fix: `Jakie` -> `jak`
      -> dropped, so it never enters the query. The pre-fix order (stopwords
      *before* the stemmer) let `Jakie`/`Jakieś` through as `jak` and leaked into
      `problems:62` / `problems:64` (report §9).

  decision layer
      **none.** H5 ("reject a hit matched only by a post-stem stopword") was
      measured and **rejected as an overfit**: it fired on 0/5 new unanswerable
      questions and scored worse (72.7%) than K1 (81.8%) on the 11-question set.
      No filter is applied here; an empty result list *is* the refusal.

Measured on `scripts/_scratch/gold_set_extended_v2.json` (27 answerable + 11 unanswerable),
engine B1, this exact pipeline:

    family_recall@5 = 81.5% (22/27)   refusal = 81.8% (9/11)   MRR = 0.778

Known limitations — 3 residual leak classes, **deliberately not fixed** (report §18,
no hypothesis for them was authorized):

    1. over-stemming: `alla` -> `all` matches 5 `decisions` rows (Q34 "risotto").
    2. FTS5-vs-substring divergence is irrelevant here (no H5), but `przepis`
       does not match `przepisy` in FTS5, so Q35 is refused only because `jak`
       was removed from the query.
    3. genuine vocabulary overlap: `zasad`, `hold` (Q38 "poker").

Stdlib only (no third-party imports). Database path: ``$BRAIN_DB`` if set, else
``<repo root>/brain/brain.db``.

CLI:
    python scripts/memory/retrieval_v1.py "Jakie ADR-y obowiązują?"
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Pipeline constants — frozen to the validated K1 configuration.
# --------------------------------------------------------------------------- #

#: Polish stopwords. Applied AFTER stemming (that is the K1 fix).
POLISH_STOPWORDS: frozenset[str] = frozenset({
    "i", "w", "na", "do", "o", "z", "że", "się", "to", "jest", "są", "po", "oraz",
    "nie", "ile", "kto", "czy", "ich", "jak", "co", "dlaczego", "ale", "za",
    "od", "przez", "pod", "nad", "tej", "tego", "tę", "ten", "ta", "te", "mamy",
    "być", "był", "była", "było", "byli", "ma", "mieć", "dla",
    "tym", "tymi", "jeśli",
})

_SUFFIXES = ("anie", "enie", "ość", "nych", "nym", "ego", "emu", "ymi", "ych",
             "ej", "ym", "ie", "y", "i", "a", "o", "e")

#: (table, FTS table, SQL to fetch a display snippet) — the three search surfaces.
TABLES: tuple[tuple[str, str, str], ...] = (
    ("lessons", "lessons_fts", "SELECT content FROM lessons WHERE id = ?"),
    ("decisions", "decisions_fts", "SELECT title FROM decisions WHERE id = ?"),
    ("problems", "problems_fts", "SELECT title FROM problems WHERE id = ?"),
)

DEFAULT_LIMIT = 5


def stem_pl(word: str) -> str:
    """Suffix-stripping stemmer, verbatim from the harness the config was measured on."""
    word = word.lower()
    for suffix in sorted(_SUFFIXES, key=len, reverse=True):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def extract_tokens(text: str) -> list[str]:
    """K1 query pipeline: tokenize -> len>2 -> stem -> drop post-stem stopwords -> sort.

    Stopwords are removed *after* the stemmer, which is precisely the difference
    from the pre-fix pipeline. Sorting makes the FTS ``OR`` order deterministic.
    """
    tokens: list[str] = []
    for word in re.findall(r"\w+", (text or "").lower()):
        if len(word) > 2:
            tokens.append(stem_pl(word))
    return sorted({t for t in tokens if t not in POLISH_STOPWORDS})


def connect(db_path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    """Open the brain database. ``$BRAIN_DB`` wins, else ``<repo>/brain/brain.db``."""
    if db_path is None:
        db_path = os.environ.get("BRAIN_DB") or (
            Path(__file__).resolve().parents[2] / "brain" / "brain.db"
        )
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"brain database not found: {path}")
    return sqlite3.connect(str(path))


def _snippet(cur: sqlite3.Cursor, table: str, rowid: int) -> str:
    for name, _fts, sql in TABLES:
        if name == table:
            row = cur.execute(sql, (rowid,)).fetchone()
            text = (row[0] if row else "") or ""
            return " ".join(text.split())[:160]
    return ""


def search(query: str, limit: int = DEFAULT_LIMIT,
           conn: sqlite3.Connection | None = None) -> dict:
    """Retrieve top-``limit`` rows for ``query``.

    Returns ``{"query", "tokens", "hits"}``. ``hits == []`` means refusal
    (no lexical evidence in the corpus) — that is the only refusal mechanism.
    """
    tokens = extract_tokens(query)
    own = conn is None
    if own:
        conn = connect()
    cur = conn.cursor()

    matches: list[dict] = []
    if tokens:
        fts_query = " OR ".join(tokens)
        for table, fts_table, _sql in TABLES:
            try:
                # B1 engine: one SELECT, fetched whole. Never reuse `cur` here.
                rows = cur.execute(
                    f"SELECT rowid, rank FROM {fts_table} "
                    f"WHERE {fts_table} MATCH ? ORDER BY rank LIMIT ?",
                    (fts_query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                # FTS5 rejects a malformed query (e.g. a lone "'" token) -> no evidence.
                continue
            for rowid, rank in rows:
                matches.append({
                    "table": table,
                    "id": rowid,
                    "rank": rank,
                    "matched_tokens": [],
                    "preview": _snippet(cur, table, rowid),
                })
        matches.sort(key=lambda h: h["rank"])
        matches = matches[:limit]
        for hit in matches:
            hit["matched_tokens"] = _matched_tokens(cur, hit, tokens)

    if own:
        conn.close()
    return {"query": query, "tokens": tokens, "hits": matches}


def _matched_tokens(cur: sqlite3.Cursor, hit: dict, tokens: list[str]) -> list[str]:
    """Tokens of the query found in the full row text (substring check, as measured).

    Reported for diagnostics only. It does **not** filter anything: the decision
    layer is deliberately empty (H5 was rejected).
    """
    for name, _fts, _sql in TABLES:
        if name != hit["table"]:
            continue
        if name == "lessons":
            row = cur.execute("SELECT content FROM lessons WHERE id = ?", (hit["id"],)).fetchone()
        elif name == "decisions":
            row = cur.execute("SELECT title || ' ' || content FROM decisions WHERE id = ?",
                              (hit["id"],)).fetchone()
        else:
            row = cur.execute(
                "SELECT title || ' ' || COALESCE(root_cause,'') || ' ' || COALESCE(fix,'') "
                "FROM problems WHERE id = ?", (hit["id"],)).fetchone()
        text = (row[0] if row else "") or ""
        text = text.lower()
        return [t for t in tokens if t in text]
    return []


def format_result(result: dict) -> str:
    lines = [f"query : {result['query']}"]
    lines.append(f"tokens: {result['tokens']}")
    if not result["hits"]:
        lines.append("hits  : []  -> REFUSAL (no lexical evidence)")
        return "\n".join(lines)
    lines.append(f"hits  : {len(result['hits'])}")
    for i, h in enumerate(result["hits"], 1):
        lines.append(f"  {i}. {h['table']}:{h['id']}  rank={h['rank']:.3f}  {h['preview']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv:
        print(__doc__.strip().splitlines()[0])
        print('usage: python scripts/memory/retrieval_v1.py [--json] "<query>"')
        return 2
    result = search(" ".join(argv))
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
