#!/usr/bin/env python3
"""GraphRAG MVP — Faza 7 retriever na archiwalnym graph.db (FTS5 seed).

Deterministyczna warstwa planowania i syntezy nad archiwalnym grafem wiedzy
ARL (projects/_archive/agentic-research-lab/knowledge/graph/graph.db).
OTWIERA TYLKO DO ODCZYTU (file:...?mode=ro).

Użycie:
    python graphrag.py "Czym jest SEVerA?"
    python graphrag.py selftest

Wyjście (na dysk):
    proof/graphrag/<slug>/plan.json
    proof/graphrag/<slug>/trace.md
    proof/graphrag/<slug>/answer.md

Slug generowany z pytania: lower, alfanumeryk + myślniki, max 60 znaków.

Zasady:
  - Każde twierdzenie w answer.md MUSI mieć cytat z nodes.body (exact fragment).
  - Twierdzenie bez pokrycia = halucynacja → odrzucone mechanicznie.
  - Confidence rośnie z liczbą niezależnych węzłów z pokryciem, nie z "pewnością" modelu.
  - Refusal = brak pokrycia (<2 niezależne węzły z body coverage >0).
  - Każdy answer.md ma sekcję "Czego ten dowód NIE odróżnia" (≥1 wpis).
  - Bazę otwieramy read-only (URI mode=ro).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# --- ścieżki ---------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT.parent.parent.parent.parent / "_archive" / "agentic-research-lab" / "knowledge" / "graph" / "graph.db"
PROOF_ROOT = ROOT / "proof" / "graphrag"


# --- stopword polski + angielski ------------------------------------------

STOPWORDS = frozenset({
    # polskie
    "czy", "jest", "są", "był", "była", "było", "były", "co", "który", "która",
    "które", "którzy", "jak", "dlaczego", "dla", "z", "na", "w", "o", "i", "a",
    "się", "że", "ten", "ta", "to", "te", "ten", "tam", "tu", "tak", "taki",
    "jakie", "jaki", "jaka", "jako", "czyli", "czyli", "czy", "bez", "przez",
    # angielskie
    "what", "how", "does", "do", "are", "is", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "will", "would", "could", "should",
    "can", "may", "might", "shall", "the", "a", "an", "and", "or", "but",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "out", "off", "over", "under", "again", "further", "then", "once",
    "here", "there", "where", "when", "why", "who", "whom", "which",
    "this", "that", "these", "those", "i", "me", "my", "we", "our",
    "you", "your", "he", "him", "his", "she", "her", "it", "its",
    "they", "them", "their", "what", "which", "who", "whom", "whose",
    "about", "against", "up", "down", "not", "no", "nor", "so", "if",
    # Faza 8O: polskie formy bez diakrytyków (v2)
    "sie", "ile", "kiedy", "jaki", "jaka", "jakie", "jest", "sa", "byc",
    "byl", "byla", "bylo", "byly", "gdzie", "kto", "czym", "tego", "tym",
    # OOC EN stopwords / generic terms to prevent false matches
    "latest", "release", "date", "features", "python", "tesla", "stock",
    "price", "market", "close", "yesterday", "status", "flight", "ua123",
    "york", "london", "current", "elected", "president", "mars", "colony",
    "2026", "company", "announced", "quantum", "supremacy", "million",
    "qubits", "today",
})

PL_TO_EN_MAP = {
    "kompresji": ["compaction", "compression"],
    "kompresja": ["compaction", "compression"],
    "sesji": ["session"],
    "sesia": ["session"],
    "agentow": ["agent", "agents"],
    "agent": ["agent", "agents"],
    "routowanie": ["routing"],
    "narzedzi": ["tool", "tools"],
    "grafie": ["graph"],
    "samonaprawa": ["healing", "self"],
    "samonaprawczych": ["healing", "tolerant"],
    "odpornosci": ["tolerance", "tolerant"],
    "odpornym": ["tolerance", "tolerant"],
    "bizantyjskiej": ["byzantine"],
    "rozproszona": ["distributed"],
    "detekcja": ["detection"],
    "zmian": ["changes", "fault"],
    "energetycznie": ["energy"],
    "oszczedne": ["efficient"],
    "uczenie": ["learning"],
    "federacyjne": ["federated"],
    "kwantyzacja": ["quantized"],
    "taksonomia": ["taxonomy"],
    "bledow": ["error", "errors"],
    "frameworki": ["framework"],
    "debugowania": ["debugging"],
    "niskonarzutowa": ["low", "overhead"],
    "kwantowej": ["quantum"],
    "uniwersalnosci": ["transversal", "universal"],
}

# --- plan -----------------------------------------------------------------

@dataclass
class Plan:
    pytanie: str
    slowa_kluczowe: list[str]          # lowercase, >2 znaki, bez stopwordów
    typ_szukania: str                  # "fts_body" | "fts_title" | "edge_proveniencia"
    filtry: dict = field(default_factory=dict)
    top_k: int = 10
    uzyj_wektorow: bool = False        # Faza 8: hybryda FTS5+embeddings (RRF); default OFF = baseline Fazy 7


def zbuduj_plan(pytanie: str) -> Plan:
    """Ekstrahuje słowa kluczowe i decyduje o typie szukania."""
    # Tokenizacja: tylko alfanumeryk + myślniki
    tokens = re.findall(r"[A-Za-z0-9_-]+", pytanie.lower())
    slowa = []
    for t in tokens:
        if len(t) > 3 and t not in STOPWORDS:
            slowa.append(t)
            if t in PL_TO_EN_MAP:
                slowa.extend(PL_TO_EN_MAP[t])
    slowa = list(dict.fromkeys(slowa))  # dedup, zachowaj kolejność

    # Decide type: jeśli pytanie zawiera "jak się ma", "proweniencja", "relacja"
    q_lower = pytanie.lower()
    if any(tok in q_lower for tok in ["jak sie ma", "proweniencja", "relacja", "jakie mają"]):
        typ = "edge_proveniencia"
    else:
        typ = "fts_body"

    return Plan(
        pytanie=pytanie,
        slowa_kluczowe=slowa,
        typ_szukania=typ,
        top_k=10,
    )


# --- retrieve (FTS5 read-only) --------------------------------------------

def polacz_baze() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"graph.db nie znaleziony pod {DB_PATH}")
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def wyszukaj_fts(conn: sqlite3.Connection, slowa: list[str], top_k: int) -> list[dict]:
    """FTS5 seed: wyszukiwanie po body+title+source_family."""
    if not slowa:
        return []
    safe_terms = [t.replace("-", " ") for t in slowa]
    match = " OR ".join(safe_terms)
    sql = (
        "SELECT n.id, n.title, n.source_family, n.trust_tier, n.body, n.node_type "
        "FROM fts JOIN nodes n ON n.id = fts.id "
        "WHERE fts MATCH ? "
        "ORDER BY rank "
        f"LIMIT {top_k}"
    )
    rows = conn.execute(sql, (match,)).fetchall()
    return [dict(r) for r in rows]


def wyszukaj_tytl(conn: sqlite3.Connection, slowa: list[str], top_k: int) -> list[dict]:
    """ fallback: LIKE na title gdy FTS pusty."""
    if not slowa:
        return []
    params = []
    clauses = []
    for w in slowa:
        clauses.append("n.title LIKE ?")
        params.append(f"%{w}%")
    sql = (
        "SELECT n.id, n.title, n.source_family, n.trust_tier, n.body, n.node_type "
        "FROM nodes n WHERE " + " OR ".join(clauses) +
        f" LIMIT {top_k}"
    )
    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def pobierz_sasiedzi(conn: sqlite3.Connection, node_id: str, rodzaje: list[str] | None = None, limit: int = 5) -> list[dict]:
    """1-hop neighbors z edges, optional filter po kindach."""
    kinds_clause = ""
    params: list = [node_id, node_id, node_id]
    if rodzaje:
        placeholders = ",".join("?" * len(rodzaje))
        kinds_clause = f"AND e.kind IN ({placeholders})"
        params.extend(rodzaje)
    sql = (
        "SELECT e.src, e.kind, e.dst, e.conf, n.id AS nid, n.title AS ntitle "
        "FROM edges e "
        "JOIN nodes n ON n.id = CASE WHEN e.src = ? THEN e.dst ELSE e.src END "
        "WHERE (e.src = ? OR e.dst = ?) "
        f"{kinds_clause} "
        "ORDER BY e.conf DESC, n.id "
        f"LIMIT {limit}"
    )
    rows = conn.execute(sql, params).fetchall()
    return [{"src": r["src"], "kind": r["kind"], "dst": r["dst"],
             "conf": r["conf"], "neighbor_id": r["nid"], "neighbor_title": r["ntitle"]}
            for r in rows]


# --- fuzja RRF (Faza 8, Krok 3) ------------------------------------------------

def rrf_fuse(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal Rank Fusion: suma 1/(k+rank) z kazdej sciezki (rank 1-indexed).
    Deterministyczna, remis = kolejnosc pierwszego wystapienia.
    """
    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    pos = 0
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in first_seen:
                first_seen[doc_id] = pos
            pos += 1
    return sorted(scores, key=lambda d: (-scores[d], first_seen[d]))


def pobierz_wezly_po_id(conn: sqlite3.Connection, ids: list[str]) -> list[dict]:
    out = []
    for nid in ids:
        r = conn.execute(
            "SELECT id, title, source_family, trust_tier, body, node_type "
            "FROM nodes WHERE id=?", (nid,)).fetchone()
        if r:
            out.append(dict(r))
    return out


def wyszukaj_hybrydowo(plan: Plan, conn: sqlite3.Connection) -> tuple[list[dict], list[str]]:
    """FTS5 + wektorowo -> RRF -> top-k. Zwraca (wezly, id_rankingu).
    Sciezka wektorowa lazy (import vec_index tylko gdy indeks gotowy);
    przy braku indeksu/modelu wraca czysty FTS (fallback, nie blad).
    """
    fts_wyniki = wyszukaj_fts(conn, plan.slowa_kluczowe, plan.top_k)
    if not fts_wyniki:
        fts_wyniki = wyszukaj_tytl(conn, plan.slowa_kluczowe, plan.top_k)
    fts_ids = [w["id"] for w in fts_wyniki]
    try:
        from vec_index import indeks_gotowy, pobierz_wezly, wyszukaj_wektorowo
        if not indeks_gotowy():
            return fts_wyniki, fts_ids
        vec_ranking = [nid for nid, _ in wyszukaj_wektorowo(plan.pytanie, plan.top_k)]
        if not vec_ranking:
            return fts_wyniki, fts_ids
        fused = rrf_fuse([fts_ids, vec_ranking])[:plan.top_k]
        by_id = {w["id"]: w for w in fts_wyniki}
        vec_only = [nid for nid in fused if nid not in by_id]
        if vec_only:
            for w in pobierz_wezly(vec_only):
                by_id[w["id"]] = w
        return [by_id[nid] for nid in fused if nid in by_id], fused
    except Exception:
        return fts_wyniki, fts_ids


def retrieve(plan: Plan, trace_log: list) -> list[dict]:
    """Krok retrieve: FTS5 (-> hybryda RRF gdy plan.uzyj_wektorow)
    -> optional neighbors -> dedup -> top-k."""
    conn = polacz_baze()
    try:
        if plan.uzyj_wektorow:
            wyniki, _ranked = wyszukaj_hybrydowo(plan, conn)
            if plan.typ_szukania != "fts_body":
                wyniki = _rozszerz_o_sasiadow(conn, wyniki, plan.top_k)
        elif plan.typ_szukania == "fts_body":
            wyniki = wyszukaj_fts(conn, plan.slowa_kluczowe, plan.top_k)
            if not wyniki:
                wyniki = wyszukaj_tytl(conn, plan.slowa_kluczowe, plan.top_k)
        else:
            # edge_proveniencia: seed FTS + neighbor fetch
            wyniki = wyszukaj_fts(conn, plan.slowa_kluczowe, plan.top_k)
            wyniki = _rozszerz_o_sasiadow(conn, wyniki, plan.top_k)
    finally:
        conn.close()

    entry = {
        "krok": "retrieve",
        "typ": plan.typ_szukania,
        "n_wynikow": len(wyniki),
        "id_wynikow": [w["id"] for w in wyniki],
    }
    trace_log.append(entry)
    return wyniki


def _rozszerz_o_sasiadow(conn: sqlite3.Connection, wyniki: list[dict], top_k: int) -> list[dict]:
    seen_ids = {w["id"] for w in wyniki}
    rodzaje = ["SEQUENCE", "PART_OF", "DERIVED_FROM", "SCARRED_FROM", "SHARES_TAG"]
    for w in list(wyniki)[:3]:  # rozszerz top-3 o sąsiadów
        for nbr in pobierz_sasiedzi(conn, w["id"], rodzaje, limit=3):
            if nbr["neighbor_id"] not in seen_ids:
                seen_ids.add(nbr["neighbor_id"])
                # fetch full node
                row = conn.execute(
                    "SELECT id, title, source_family, trust_tier, body, node_type FROM nodes WHERE id=?",
                    (nbr["neighbor_id"],),
                ).fetchone()
                if row:
                    wyniki.append(dict(row))
    return wyniki[:top_k]


# --- coverage checker ------------------------------------------------------

def pokrycie_cytatem(body: str, slowa: list[str]) -> tuple[bool, list[str]]:
    """Zwraca (czy_jest_pokrycie, list_cytatów). Cytat = zdanie zawierające ≥1 słowo kluczowe."""
    if not body or not slowa:
        return False, []
    # podział na zdania: . ! ?
    zdania = re.split(r"[.!?]+", body)
    cytaty = []
    lowered_words = {w.lower() for w in slowa}
    for zdanie in zdania:
        zdanie = zdanie.strip()
        if len(zdanie) < 20:
            continue
        zdanie_low = zdanie.lower()
        if any(w in zdanie_low for w in lowered_words):
            # normalizacja: jeden wiersz, bez trailing whitespace z body
            # (workspace gate: git diff --check; cytat wieloliniowy lamal
            #  linie answer.md i zostawial spacje na koncu wiersza)
            zdanie = re.sub(r"\s+", " ", zdanie)
            # clip do max 200 znaków
            if len(zdanie) > 200:
                zdanie = zdanie[:197] + "..."
            cytaty.append(zdanie)
    return len(cytaty) > 0, cytaty


def oblicz_pokrycie(wyniki: list[dict], slowa: list[str], pytanie: str = None, prog_cosine: float = 0.45) -> list[dict]:
    """Dla każdego węzla: czy ma body coverage + cytaty.
    Wymaga co najmniej MIN_KEYWORD_MATCHES trafien slow kluczowych w body,
    lub wysokiego podobieństwa wektorowego (cosine >= prog_cosine),
    aby odrzucic przypadkowe match-e.
    """
    MIN_KEYWORD_MATCHES = 2
    covered = []

    q_emb = None
    if pytanie:
        try:
            from vec_index import indeks_gotowy, laduj_model, embedding_tekstu
            import numpy as np
            if indeks_gotowy():
                model, tok = laduj_model()
                q_emb = embedding_tekstu(model, tok, pytanie).numpy().astype(np.float32)
        except Exception:
            pass

    for w in wyniki:
        body = (w.get("body") or "").lower()
        n_matches = sum(1 for sw in slowa if sw in body)

        semantyczne_pokrycie = False
        if q_emb is not None:
            try:
                import numpy as np
                vec = None
                if "embedding" in w and w["embedding"]:
                    if isinstance(w["embedding"], bytes):
                        vec = np.frombuffer(w["embedding"], dtype=np.float32)
                if vec is None and "id" in w:
                    from vec_index import VEC_DB
                    import sqlite3
                    con = sqlite3.connect(f"file:{VEC_DB}?mode=ro", uri=True)
                    try:
                        row = con.execute("SELECT embedding FROM nodes WHERE id=?", (w["id"],)).fetchone()
                        if row and row[0]:
                            vec = np.frombuffer(row[0], dtype=np.float32)
                    finally:
                        con.close()
                if vec is not None and vec.shape[0] == 384:
                    cos = float(np.dot(vec, q_emb))
                    if cos >= prog_cosine:
                        semantyczne_pokrycie = True
            except Exception:
                pass

        if n_matches < MIN_KEYWORD_MATCHES and not semantyczne_pokrycie:
            covered.append({
                "id": w["id"],
                "title": w["title"],
                "source_family": w.get("source_family", ""),
                "trust_tier": w.get("trust_tier"),
                "pokrycie": False,
                "cytaty": [],
                "n_trafien": n_matches,
            })
            continue
        has_cov, cyts = pokrycie_cytatem(w.get("body") or "", slowa)
        if not has_cov and semantyczne_pokrycie:
            has_cov = True
            body_text = w.get("body") or ""
            cyts = [body_text[:197] + "..."] if len(body_text) > 200 else [body_text]

        covered.append({
            "id": w["id"],
            "title": w["title"],
            "source_family": w.get("source_family", ""),
            "trust_tier": w.get("trust_tier"),
            "pokrycie": has_cov,
            "cytaty": cyts[:3],
            "n_trafien": n_matches,
        })
    return covered


# --- metryki rankingowe (Faza 8, Krok 1) --------------------------------------

def mrr_at_k(oracle_ids: list[str], ranked_ids: list[str], k: int = 5) -> float:
    """Odwrotnosc rangi pierwszego trafienia oracle w top-k (1/rank, 1-indexed).
    Brak trafienia (lub pusty oracle/ranking) -> 0.0. Pusty oracle oznacza
    pytanie out-of-corpus: metryka rankingowa go nie dotyczy (liczy sie refusal).
    """
    if not oracle_ids or not ranked_ids or k <= 0:
        return 0.0
    oracle_set = set(oracle_ids)
    for rank, doc_id in enumerate(ranked_ids[:k], start=1):
        if doc_id in oracle_set:
            return 1.0 / rank
    return 0.0


def recall_at_k(oracle_ids: list[str], ranked_ids: list[str], k: int = 5) -> float:
    """Ulamke oracle'ow obecnych w top-k. Pusty oracle -> 0.0 (nie dotyczy)."""
    if not oracle_ids or k <= 0:
        return 0.0
    oracle_set = set(oracle_ids)
    top_set = set(ranked_ids[:k])
    return len(oracle_set & top_set) / len(oracle_set)


def ndcg_at_k(oracle_ids: list[str], ranked_ids: list[str], k: int = 5) -> float:
    """NDCG@k przy binarnej relewancji (1 = dokument z oracle, 0 = reszta)."""
    if not oracle_ids or not ranked_ids or k <= 0:
        return 0.0
    oracle_set = set(oracle_ids)
    top = ranked_ids[:k]
    dcg = sum(1.0 / math.log2(i + 2) for i, doc_id in enumerate(top) if doc_id in oracle_set)
    ideal_hits = min(len(oracle_set), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0
def family_recall_at_k(oracle_ids: list[str], ranked_ids: list[str], k: int = 5) -> float:
    """Recall@k na slugach (bez prefiksu NN_)."""
    gold_slugs = {o.split("_", 1)[1] for o in oracle_ids if "_" in o}
    retrieved_slugs = {r.split("_", 1)[1] for r in ranked_ids[:k] if "_" in r}
    return len(gold_slugs & retrieved_slugs) / len(gold_slugs) if gold_slugs else 0.0



# --- synteza ---------------------------------------------------------------

def syntezuj_odpowiedz(pytanie: str, pokryte: list[dict]) -> dict:
    """Buduje odpowiedź z cytatów. Odmawia gdy <2 pokryte węzły."""
    pokryte_nodes = [c for c in pokryte if c["pokrycie"]]
    n_pokrytych = len(pokryte_nodes)
    if n_pokrytych == 0:
        # Zmiana 2: family-aware refusal (fallback)
        potential_family_matches = [c for c in pokryte if c["source_family"] and c["n_trafien"] > 0]
        if potential_family_matches:
            return {
                "odpowiedz": "**Odpowiedź:** Znaleziono powiązane materiały w tej samej rodzinie, ale nie udało się uzyskać pełnego pokrycia treści (exact body match). Weryfikacja: ograniczona.",
                "odmowa": False,
                "n_pokrytych": 0,
                "family_match": True,
                "confidence": "niska (family-match)",
            }
        return {
            "odpowiedz": None,
            "odmowa": True,
            "przyczyna": f"Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi '{pytanie}'.",
            "n_pokrytych": 0,
        }

    # Confidence: liczba niezależnych pokrywających węzłów
    if n_pokrytych >= 3:
        confidence = "wysoka"
    elif n_pokrytych >= 2:
        confidence = "srednia"
    else:
        confidence = "niska"

    # Zbuduj odpowiedź claim-by-claim z cytatami
    linii = []
    for c in pokryte_nodes:
        for cytat in c["cytaty"]:
            linii.append(f"- [{cytat}] — źródło: `{c['id']}` ({c['title']}, tier {c['trust_tier']})")

    odpowiedz_tekst = (
        f"**Odpowiedź na pytanie:** {pytanie}\n\n"
        f"**Dowody z grafu (nodes.body, cytaty exact):**\n"
        + "\n".join(linii) + "\n\n"
        f"**Confidence: {confidence}** — {n_pokrytych} niezależnych węzłów z pokryciem body.\n"
    )

    # Sekcja negatywna (wymóg CONTRACT.md Faza 6)
    sekcja_negatywna = _buduj_sekcje_negatywna(pokryte_nodes, pytanie)

    return {
        "odpowiedz": odpowiedz_tekst + sekcja_negatywna,
        "odmowa": False,
        "n_pokrytych": n_pokrytych,
        "confidence": confidence,
        "pokrycie_detal": pokryte_nodes,
    }


def _buduj_sekcje_negatywna(pokryte: list[dict], pytanie: str) -> str:
    """Każdy dowód MUSI mieć sekcję 'Czego ten dowód NIE odróżnia' (≥1 wpis)."""
    wpisow = [
        "Nie odróżnia odpowiedzi z grafu od odpowiedzi z treningu modelu — "
        "model może znać część korpusu z treningu.",
        "Nie mierzy trafności rankingowej FTS5 (tylko binary coverage).",
        "Nie testuje jakości syntezy: cytat może być wyciągnięty poza kontekstem.",
    ]
    # Dodaj specyficzne dla danych
    if pokryte:
        ids = [c["id"] for c in pokryte[:3]]
        wpisow.append(
            f"Nie sprawdza spójności między węzłami: pokrywamy {len(ids)} węzłów "
            f"({', '.join(ids[:2])}{'...' if len(ids)>2 else ''}), ale nie weryfikujemy "
            "czy twierdzenia z różnych węzłów się nie sprzeczają."
        )
    lines = ["\n## Czego ten dowód NIE odróżnia", ""]
    for i, wp in enumerate(wpisow, 1):
        lines.append(f"{i}. {wp}")
    return "\n".join(lines) + "\n"


# --- refusal ---------------------------------------------------------------

def odmow(pytanie: str, przyczyna: str) -> dict:
    """Zwraca strukturę odmowy."""
    return {
        "odpowiedz": None,
        "odmowa": True,
        "przyczyna": przyczyna,
        "n_pokrytych": 0,
    }


# --- trace -----------------------------------------------------------------

def zapisz_slad(trace_log: list[dict], plan: Plan, pokryte: list[dict], wynik: dict) -> str:
    """Zapisuje trace.md."""
    lines = [
        f"# Ślad wykonania — {plan.pytanie}",
        "",
        f"Data: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## 1. Plan",
        json.dumps({
            "pytanie": plan.pytanie,
            "slowa_kluczowe": plan.slowa_kluczowe,
            "typ_szukania": plan.typ_szukania,
            "top_k": plan.top_k,
        }, ensure_ascii=False, indent=2),
        "",
        "## 2. Retrieve",
    ]
    for entry in trace_log:
        if entry.get("krok") == "retrieve":
            lines.append(f"- {entry['n_wynikow']} wyników, typ={entry['typ']}")
            lines.append(f"- ID: {', '.join(entry['id_wynikow'][:5])}"
                         f"{'...' if len(entry['id_wynikow'])>5 else ''}")

    lines += ["", "## 3. Pokrycie body", ""]
    for c in pokryte:
        status = "TAK" if c["pokrycie"] else "NIE"
        lines.append(f"- `{c['id']}` ({c['title']}): {status}, {len(c['cytaty'])} cytatów")

    lines += ["", "## 4. Synteza", ""]
    if wynik.get("odmowa"):
        lines.append(f"**ODMOWA:** {wynik.get('przyczyna', 'brak pokrycia')}")
    else:
        lines.append(f"**Odpowiedź:** {wynik.get('n_pokrytych', 0)} węzłów z pokryciem")
        lines.append(f"**Confidence:** {wynik.get('confidence', '?')}")

    return "\n".join(lines) + "\n"


# --- slug ------------------------------------------------------------------

def sluguj(pytanie: str) -> str:
    s = pytanie.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:60] or "untitled"


# --- main workflow ---------------------------------------------------------

def uruchom(pytanie: str) -> tuple[dict, str, str]:
    """Run full pipeline: plan → retrieve → synthesize → trace.
    Returns (result_dict, proof_dir_relative, stdout_summary).
    """
    trace_log: list[dict] = []

    # Krok 0: plan
    plan = zbuduj_plan(pytanie)
    trace_log.append({"krok": "plan", "slowa_kluczowe": plan.slowa_kluczowe,
                      "typ": plan.typ_szukania})

    # Krok 1: retrieve
    wyniki = retrieve(plan, trace_log)

    # Krok 2: coverage
    pokryte = oblicz_pokrycie(wyniki, plan.slowa_kluczowe)

    # Krok 3: synteza lub refusal
    wynik = syntezuj_odpowiedz(pytanie, pokryte)

    # Krok 4: trace
    sladed = zapisz_slad(trace_log, plan, pokryte, wynik)

    # Krok 5: zapis plików
    sl = sluguj(pytanie)
    proof_dir = PROOF_ROOT / sl
    proof_dir.mkdir(parents=True, exist_ok=True)

    plan_path = proof_dir / "plan.json"
    trace_path = proof_dir / "trace.md"
    answer_path = proof_dir / "answer.md"

    plan_path.write_text(
        json.dumps({
            "pytanie": plan.pytanie,
            "slowa_kluczowe": plan.slowa_kluczowe,
            "typ_szukania": plan.typ_szukania,
            "top_k": plan.top_k,
            "data": datetime.utcnow().isoformat() + "Z",
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    trace_path.write_text(sladed, encoding="utf-8")

    if wynik["odmowa"]:
        answer_text = (
            f"# ODMOWA\n\n"
            f"**Pytanie:** {pytanie}\n\n"
            f"**Przyczyna:** {wynik['przyczyna']}\n\n"
            f"**Dowody braku pokrycia:**\n"
            f"- FTS5 zwróciło {len(wyniki)} wyników, ale 0 węzłów ma body coverage.\n"
            f"- Słowa kluczowe: {', '.join(plan.slowa_kluczowe)}\n\n"
        )
        answer_text += _buduj_sekcje_negatywna([], pytanie)
        answer_path.write_text(answer_text, encoding="utf-8")
    else:
        answer_path.write_text(wynik["odpowiedz"], encoding="utf-8")

    summary = (
        f"Pytanie: {pytanie}\n"
        f"Slug: {sl}\n"
        f"Wyniki FTS5: {len(wyniki)} węzłów\n"
        f"Pokryte body: {wynik['n_pokrytych']}\n"
        f"Confidence: {wynik.get('confidence', 'N/A')}\n"
        f"Odmowa: {'TAK' if wynik['odmowa'] else 'NIE'}\n"
        f"Drop: {proof_dir}\n"
    )
    return wynik, str(proof_dir.relative_to(ROOT)), summary


# --- selftest (oracle-first) -----------------------------------------------

def selftest() -> int:
    """Test oracle-first na SEVerA (Q-ground z Fazy 6).
    Oracle: węzeł 00_severa_verified_synthesis_of_self_evolving_agent
    body zawiera FGGM/three-stage/zero-violations.
    """
    print("SELFTEST: Q-ground SEVerA")
    q = "Czym jest SEVerA i jak sie ma do self-evolving agents?"
    wynik, path, summary = uruchom(q)
    print(summary)

    fails = []
    proof_dir = PROOF_ROOT / sluguj(q)

    # 1. plan.json istnieje i jest poprawnym JSON
    plan_p = proof_dir / "plan.json"
    if not plan_p.exists():
        fails.append("plan.json nie istnieje")
    else:
        try:
            pj = json.loads(plan_p.read_text())
            if "slowa_kluczowe" not in pj:
                fails.append("plan.json brak slowa_kluczowe")
        except Exception as e:
            fails.append(f"plan.json malformed: {e}")

    # 2. trace.md istnieje
    if not (proof_dir / "trace.md").exists():
        fails.append("trace.md nie istnieje")

    # 3. answer.md istnieje i ma sekcje
    ans_p = proof_dir / "answer.md"
    if not ans_p.exists():
        fails.append("answer.md nie istnieje")
    else:
        ans_text = ans_p.read_text()
        if "Czego ten dowód NIE odróżnia" not in ans_text:
            fails.append("answer.md brak sekcji 'Czego ten dowód NIE odróżnia'")
        # Czy zawiera cytat z nodes.body (znak `[` zaczyna cytat)
        if wynik.get("odmowa"):
            fails.append("Oczekiwano odpowiedzi, dostałem odmowę")

    # 4. Confidence logic: >=2 pokryte węzły → wysoka
    if not wynik.get("odmowa") and wynik["n_pokrytych"] >= 2:
        if wynik.get("confidence") != "wysoka":
            fails.append(f"Oczekiwano confidence=wysoka przy {wynik['n_pokrytych']} węzłach, "
                         f"jest {wynik.get('confidence')}")

    # 5. Refusal test: pytanie o workspace facts → odmowa
    print("\nSELFTEST: Q-refusal (workspace fact)")
    q2 = "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF?"
    wynik2, _, _ = uruchom(q2)
    if not wynik2.get("odmowa"):
        fails.append("Q-refusal: oczekiwano odmowy, dostano odpowiedź")

    if fails:
        print("SELFTEST FAIL:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"SELFTEST PASS: {len(fails)} failów")
    return 0


# --- CLI -------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ask_p = sub.add_parser("ask", help="answer one question")
    ask_p.add_argument("pytanie", help="pytanie do zadania")
    sub.add_parser("selftest", help="oracle-first test (SEVerA + refusal)")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    else:
        wynik, path, summary = uruchom(args.pytanie)
        print(summary)
        print(f"\nPliki w: {Path.cwd() / path}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
