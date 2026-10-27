#!/usr/bin/env python3
"""Pragmatic Programmer RAG CLI.

Fix for the "one retrieve() is exhaustive" methodology bug:
  1. DECOMPOSE the question into distinct sub-queries (LLM, heuristic fallback).
  2. RETRIEVE per sub-query and DEDUPE the union (multi-topic coverage).
  3. SELF-CHECK coverage; RETRY uncovered sub-queries (broader sweep).
"""
import sys
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
DB = str(ROOT / "db" / "rag.db")

MODEL = "gemini/gemini-flash-lite-latest"
TOP_K_PER_QUERY = 5
MAX_QUERIES = 6
MAX_CHUNKS = 24
CHUNK_CHARS = 600


def log(msg):
    print(msg, file=sys.stderr, flush=True)


SYSTEM = """Odpowiadasz TYLKO na podstawie dostarczonych fragmentow ksiazki
"The Pragmatic Programmer". Zasady:
- Kazde twierdzenie ma cytat w formacie [ch_XXXX, Rozdział N, Topic M, p. P].
- Uzywaj doslownych cytatow dla kluczowych zdan.
- Maks. 800 slow. Zwiezle, 3-4 zdania na sekcje.
- Na koncu sekcja "## not checked" z 2-3 punktami.
- Fragmenty pochodza z WIELU Topicow (dobranych osobno pod kazda czesc pytania);
  wykorzystaj wszystkie, ktore odpowiadaja na pytanie.
- NIGDY nie pisz "fragmenty nie zawieraja X" jesli X nie bylo osobno wyszukane;
  zamiast tego zaznacz to w "## not checked"."""

PLANNER = """Jestes modułem planowania wyszukiwania w ksiazce "The Pragmatic Programmer".
Otrzymasz pytanie (czessto po polsku, wieloczesciowe). Rozloz je na 3-6 ROZŁĄCZNYCH
pod-tematow i dla KAZDEGO podaj krotkie zapytanie wyszukiwania PO ANGIELSKU
(ksiazka jest po angielsku). Zwroc WYLACZNIE liste zapytan, jedno na linie,
bez numeracji, bez komentarzy. Maksymalnie 6 linii."""


# ---------- Level 1+2: decomposition + multi-query retrieval ----------

def decompose_heuristic(question):
    """Fallback: split on punctuation and Polish conjunctions."""
    parts = re.split(r"[?,;]|\s+i\s+|\s+oraz\s+|\s+a takze\s+|\s+lub\s+|\s+dla\s+|\s+jak\s+",
                     question, flags=re.IGNORECASE)
    out = [p.strip(" .") for p in parts]
    return [p for p in out if len(p) > 8][:MAX_QUERIES]


def plan_queries(question, client):
    """Ask the LLM for distinct English search sub-queries; fall back to heuristic."""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PLANNER},
                {"role": "user", "content": question},
            ],
            temperature=0.2,
            timeout=30.0,
        )
        text = (resp.choices[0].message.content or "").strip()
        queries = []
        for line in text.splitlines():
            q = re.sub(r"^\s*[-*\d.)\]]+\s*", "", line).strip()
            if len(q) > 3:
                queries.append(q)
        if queries:
            return queries[:MAX_QUERIES]
    except Exception as e:
        log(f"  (plan LLM failed: {e}; uzywam heurystyki)")
    return decompose_heuristic(question)


def retrieve_multi(queries, db_path=DB):
    """Retrieve per sub-query, dedupe union, sort by location."""
    from scripts.recall_hybrid import retrieve, get_chunks_meta
    merged = {}
    for q in queries:
        try:
            ids = retrieve(q, top_k=TOP_K_PER_QUERY, db_path=db_path)
        except Exception as e:
            log(f"  (retrieve '{q[:40]}' failed: {e})")
            continue
        for c in get_chunks_meta(ids, db_path=db_path):
            merged[c["id"]] = c
    chunks = sorted(merged.values(),
                    key=lambda c: (c["chapter"], c["topic"], c["page_book"]))
    return chunks[:MAX_CHUNKS]


# ---------- Level 3: coverage self-check + retry ----------

STOPWORDS = {"about", "which", "there", "their", "these", "those", "would",
             "should", "could", "where", "while", "because", "other", "every",
             "after", "before", "between", "under", "above", "using", "what",
             "when", "make", "made", "into", "from", "with", "this", "that"}


def _keywords(query):
    return [w.lower() for w in re.findall(r"[A-Za-z]{5,}", query)
            if w.lower() not in STOPWORDS]


def has_coverage(query, chunks):
    kws = _keywords(query)
    if not kws:
        return True
    for c in chunks:
        text = c["text"].lower()
        hits = sum(1 for kw in kws if kw in text)
        if hits >= max(1, min(2, len(kws))):
            return True
    return False


def self_check(queries, chunks):
    return [q for q in queries if not has_coverage(q, chunks)]


def build_context(chunks):
    parts = []
    for c in chunks:
        parts.append(
            f"[{c['id']}, Rozdział {c['chapter']}, Topic {c['topic']}, "
            f"p. {c['page_book']}]\n{c['text'][:CHUNK_CHARS]}"
        )
    return "\n\n---\n\n".join(parts)


# ---------- Answer pipeline ----------

def gather_chunks(question, client):
    """Decompose -> multi-retrieve -> coverage-check -> retry. Returns (chunks, queries)."""
    queries = plan_queries(question, client)
    log(f"--> pod-zapytania ({len(queries)}):")
    for q in queries:
        log(f"      - {q}")

    chunks = retrieve_multi(queries)
    log(f"--> {len(chunks)} unikalnych chunkow (po dedupe)")

    uncovered = self_check(queries, chunks)
    if uncovered:
        log(f"--> brak pokrycia dla {len(uncovered)} pod-zapytan, robie retry:")
        for q in uncovered:
            log(f"      ! {q}")
        broad = query_broaden(uncovered, client, question)
        log(f"--> retry queries ({len(broad)}): {broad}")
        retry = retrieve_multi(broad, db_path=DB)
        merged = {c["id"]: c for c in chunks}
        for c in retry:
            merged[c["id"]] = c
        chunks = sorted(merged.values(),
                        key=lambda c: (c["chapter"], c["topic"], c["page_book"]))[:MAX_CHUNKS]
        still = self_check(queries, chunks)
        log(f"--> po retry: {len(chunks)} chunkow, nadal niepokryte: {still}")
    return chunks, queries


def query_broaden(uncovered, client, question):
    """Generate broader/synonym queries for uncovered sub-questions."""
    listing = "\n".join(f"- {q}" for q in uncovered)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content":
                 "Dla kazdego zapytania podaj SYNONIMICZNE, szersze zapytanie PO ANGIELSKU "
                 "(inne slowa kluczowe, ten sam temat). Zwroc tylko zapytania, jedno na linie."},
                {"role": "user", "content": f"Pytanie oryginalne: {question}\n\nZapytania:\n{listing}"},
            ],
            temperature=0.3,
            timeout=30.0,
        )
        text = (resp.choices[0].message.content or "").strip()
        out = []
        for line in text.splitlines():
            q = re.sub(r"^\s*[-*\d.)\]]+\s*", "", line).strip()
            if len(q) > 3:
                out.append(q)
        if out:
            return out[:MAX_QUERIES]
    except Exception as e:
        log(f"  (broaden LLM failed: {e})")
    return uncovered


def answer(question, client):
    chunks, queries = gather_chunks(question, client)
    if not chunks:
        log("BLAD: brak jakichkolwiek chunkow (sprawdz db/rag.db).")
        return
    context = build_context(chunks)
    log(f"--> {len(context)} znakow kontekstu")

    prompt = (
        f"Pod-tematy wyszukane (dla orientacji): {', '.join(queries)}\n\n"
        f"Fragmenty:\n\n{context}\n\n---\n\nPytanie: {question}"
    )
    print()
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            temperature=0.2,
            timeout=120.0,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                print(delta.content, end="", flush=True)
        print()
    except Exception as e:
        log(f"BLAD LLM: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pragmatic Programmer RAG CLI")
    parser.add_argument("query", nargs="*", help="pytanie (tryb jednorazowy)")
    args = parser.parse_args()

    print("=" * 60, flush=True)
    print(" Pragmatic Programmer RAG CLI ", flush=True)
    print("=" * 60, flush=True)

    if not Path(DB).exists():
        log(f"BLAD: brak bazy {DB}")
        return 1
    log(f"[1/3] DB OK: {DB}")

    log("[2/3] Ladowanie modelu embeddingow (moze potrwac 5-15s)...")
    try:
        from scripts.recall_hybrid import retrieve
        retrieve("warmup")
        log("[2/3] Model gotowy.")
    except Exception as e:
        log(f"[2/3] UWAGA: blad ladowania modelu: {e}")

    log("[3/3] Tworze klienta OmniRoute...")
    from openai import OpenAI
    base_url = os.environ.get("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
    api_key = os.environ.get("OMNIROUTE_API_KEY", "sk_omniroute")
    log(f"[3/3] base_url={base_url}")
    client = OpenAI(base_url=base_url, api_key=api_key, timeout=60.0)
    log("[3/3] Gotowe.")

    one_shot = " ".join(args.query).strip()
    if one_shot:
        answer(one_shot, client)
        return 0

    print()
    print("Wpisz pytanie i nacisnij Enter.", flush=True)
    print("Wpisz 'exit' aby zakonczyc.", flush=True)

    while True:
        try:
            sys.stdout.flush()
            question = input("\nPytanie: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[przerwano]", flush=True)
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            print("Pa!", flush=True)
            break

        answer(question, client)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
