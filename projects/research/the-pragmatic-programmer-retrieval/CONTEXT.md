---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# the-pragmatic-programmer-retrieval — CONTEXT.md

grade: candidate

## Open work

- [x] Faza 0.1: Ekstrakcja struktury PDF (`scripts/extract_structure_pdf.py` -> `data/book_structure.json`, 9 rozdziałów, 53 Topics, fingerprint `58c410c0...`)
- [x] Faza 0.2: Weryfikacja `page_offset` (potwierdzono offset = 0, Topic 3 = p.42, Topic 8 = p.75, Topic 9 = p.79)
- [x] Faza 0.3: Walidacja i detektor śmieci (`scripts/validate_chunks.py` -> 0 uszkodzonych)
- [x] Faza 0.4: Chunking semantyczny (`scripts/chunk_semantic.py` -> `data/chunks.json`, 855 chunków, mediana 680 znaków)
- [x] Faza 1.1: Budowa indeksu hybrydowego (`scripts/build_hybrid.py` -> FTS5 BM25 + FastEmbed ONNX vectors w `db/rag.db`)
- [x] Faza 1.2: Retrieval hybrydowy + fuzja RRF (`scripts/recall_hybrid.py`)
- [x] Faza 1.3: Cross-encoder reranker (`scripts/rerank.py` -> BAAI/bge-reranker-base)
- [x] Faza 1.4: Pełny pipeline retrievalu (`full_retrieve()`)
- [x] Faza 2.1: Przygotowanie gold setu (`scripts/build_gold_set.py` -> `eval/gold_set_hard.json`, 30 pytań, fingerprint `c5a0a95f...`)
- [x] Faza 2.2: Pomiar `recall@8` i `MRR` (`scripts/eval_retrieval.py` -> 4 tiery zmierzone)
- [x] Krok 0 (fix): `index_fingerprint` liczony z kanonicznej treści (`scripts/fingerprint.py`, canonical JSON), nie z raw-bytes; wszystkie call-sites (`eval_retrieval.py`, `build_gold_set*.py`) używają wspólnego helpera (commit `34acea4`)
- [x] Zadanie 4: Memoizacja cross-encoder + batch candidate fetch (`scripts/rerank.py`; cache `data/rerank_cache.json`, klucz `model+question+text`, gitignored) (commit `0a1082a`)
- [x] Zadanie 5: Rozstrzygnięte — **Tier 4 @ 100 kandydatów martwy na latencji** (patrz §"Zadanie 5" niżej)
- [~] Zadanie 6 (topic-boost / routing): **POMINIĘTE świadomie** — Krok 1 pokazał 3/9 multi-target queries z dominant ≥5/8 (poniżej progu), a te 3 są już any-topic hitami, więc boost nie ruszyłby Recall@8
- [ ] Decyzja architektoniczna: czy rozszerzać zbiór pytań o generowane (do 60 pytań) i czy wdrażać RAPTOR / Graf wiedzy

## Architecture & Decisions

- Corpus: "The Pragmatic Programmer" (20th Anniversary Edition), 497 stron, 9 rozdziałów, 53 Topics.
- Indeks: SQLite FTS5 (`unicode61`) + FastEmbed ONNX wektory (`BAAI/bge-small-en-v1.5`) + RRF (k=60) + Cross-encoder reranker (`BAAI/bge-reranker-base`).
- Relacja do `retrieval-v2`: `retrieval-v2` mierzył korpus notatek wielu dokumentów i porzucił cross-encoder ze względu na koszt latencji i brak separacji refusal na OOC. W `the-pragmatic-programmer-retrieval` korpus jest zamknięty (monografia), a kluczowym celem jest precyzja cytowania (rozdział, Topic, strona) oraz test czy RAPTOR / Graf CTE są niezbędne dla syntezy multi-hop (D23).

## Status evidence (archived)

Project closed by owner decision D on 2026-10-18. Full measurements, traceability repair, and production decision are recorded in `handoff/` artifacts and project history; this L1 keeps only durable conclusions.

- Production path: Tier 3 Hybrid RRF. EN query improves Recall@8 from 0.827 to 0.981; PL+EN fusion reached 1.000 at higher latency. Cross-encoder remains excluded: ~9.6 s median for +0.038 recall.
- Answer-layer EN pilot: 10/13 answerable strict pass, 8/8 unanswerable refusal, canary clean. Term-presence grading is lexical evidence, not semantic quality.
- R15 traceability repair completed; `hit@5=1.000`, `MRR=0.654` on 15 cases.
- Known audit gap: session 10 pre-registration was not preserved in Git; reconstruction is forbidden. Gap is documented in `handoff/session-10-known-gap.md`.

## Post-closure backlog

Only if owner reopens project: chunk-level sufficiency diagnosis, contextual retrieval augmentation, and multi-topic metric redesign. Any new run requires fresh pre-registration, frozen inputs, and separate development/evaluation origins.

Do not tune against locked results or revive rejected candidates without a new research line and aligned protocol.
