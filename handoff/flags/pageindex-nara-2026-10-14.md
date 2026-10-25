---
type: Concept
flag: pageindex-nara-2026-10-14
since: 2026-10-14
owner: mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: session-close
title: pageindex-nara-2026-10-14
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`pageindex-nara-2026-10-14` — 2026-10-14: PageIndex podłączony do Nara (`nemotron-3.5-lightning-free`). Chat działa, pełne indeksowanie 222 str. zablokowane rate-limitami free tier (429 req/min). R11 closed z findingiem. Destination zmienione: LLM przez OmniRoute/Nara (nie offline). Raport: docs/reviews/session-2026-10-14-pageindex-nara.md.

not checked:
- Płatny plan Nara / wyższy limit — czy rozwiązałby indeksowanie.
- Inne modele na OmniRoute (np. darmowe Qwen, Llama) — czy mają wyższe limity.
- Koszt tokenowy pełnego indeksowania (niezmierzony, rate limit go zablokował).
- Naive RAG (R2-R5) — nie zaczął się.
