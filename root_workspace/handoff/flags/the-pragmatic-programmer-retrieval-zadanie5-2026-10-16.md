---
flag: the-pragmatic-programmer-retrieval-zadanie5-2026-10-16
since: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`the-pragmatic-programmer-retrieval-zadanie5-2026-10-16` — 2026-10-16: Zadanie 5 rozstrzygnięte — Tier 4 (cross-encoder) trwale wykluczony na latencji; decyzja zapisana w projekcie (`CONTEXT.md`, commit `00165c9`).

- **Zadanie A (skalowanie kosztu predykcji):** `bge-reranker-base`, CPU, tekst syntetyczny stałej długości — 20/40/100 par = **957 / 1937 / 4298 ms** (47.86 / 48.42 / 42.98 ms/para). 20→40 = 2.02×, 40→100 = 2.22× → **skalowanie ~liniowe**; zysk per-para ~10% (szum), nie sublinearność ratująca wide. Ekstrapolacja na realny tekst chunków (~5× dłuższy) → **100 par ≈ ~24 s/zapytanie**.
- **Zadanie B (odtworzenie logu):** `task5_r40.log` jednak się dokończył — Recall@8 any = **0.865** (45/52), primary = 0.827 (43/52), MRR = **0.715**, nDCG@8 = 0.751, mediana 9621 ms, p95 17842 ms.
- **Decyzja:** +0.038 Recall@8 nad Tier 3 (0.827 → 0.865) za ~93× latencji (103 ms → 9621 ms @ 40; ~24 s @ 100). Cache (`data/rerank_cache.json`) przyspiesza **iterację eval**, nie **nowe zapytanie** (nowe pytanie = cache miss = pełne ~10 s). MRR nie ratuje — koszt dyskwalifikuje. **Produkcja = Tier 3 (Hybrid RRF).** `--wide` nie odpalony (bezwartościowy przy liniowym skalowaniu).
- Stan domknięty też w `CONTEXT.md`: hardening `index_fingerprint` (content-based, commit `34acea4`), memoizacja rerankera + batch candidate fetch (commit `0a1082a`), oraz **świadome pominięcie Zadania 6** (Krok 1: 3/9 multi-target z dominant ≥5/8 — poniżej progu; te 3 są już any-topic hitami, więc boost nie ruszyłby Recall@8).
- **No-op na flagach:** żadna istniejąca flaga nie rościła sobie tego otwartego zadania → brak retiracji.

Następny krok — Zadanie 7 (answer-layer, 60+ min) **nie rozpoczęte świadomie**; nic go nie blokuje, wymaga wyraźnego go-ahead. Jeśli wracasz do projektu: produkcja to Tier 3, T4 nie wraca.

not checked:
- Nie zmierzono `--wide` (100 kandydatów) na realnym gold secie — decyzja z ekstrapolacji liniowego skalowania, nie z pomiaru end-to-end.
- Latencja per-para mierzona na tekście syntetycznym (stała długość) — mierzy **skalowanie po `n`**, nie absolutną latencję na realnych chunkach; absolut oszacowany przez porównanie z r40 (~5×).
- Zadanie 6 pominięte świadomie — nie mierzono, czy topic-boost poprawiłby Primary-Topic Recall (ocena: nie ruszyłby Any-Topic Recall@8).
- `data/book_structure.json` pozostaje untracked (derived) — celowo nie dodany do repo.
- Pre-existing advisory `MAP.md is stale` (knowledge-retrieval, the-pragmatic-programmer-retrieval) nietknięte — nie należy do tej sesji.
