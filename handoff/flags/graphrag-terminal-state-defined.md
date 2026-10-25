---
type: Concept
flag: graphrag-terminal-state-defined
since: 2026-10-10
owner: Mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
title: graphrag-terminal-state-defined
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# GraphRAG Pilot — Faza 6 ready v2 (falsyfikator odkażony)

Faza 5 (dowód kontraktu) zamknięta: mini-graf, selftest PASS, proof/produkt-x/ istnieje.

Faza 6 ma teraz falsyfikator v2 w CONTRACT.md (v1 SUPERSEDED jako oracle-second):
- **Q-ground** (treściowe, synteza z nodes.body): "Czym jest SEVerA i jak się ma do self-evolving agents?" — oczekiwanie DO UZUPEŁNIENIA przez człowieka PRZED query; do tego czasu niewykonywalne
- **Q-refusal** (oracle-first, wykonywalny): "Jaki wpis dodała sesja 04 do SCARS.md (R13)?" → oczekiwana ODMOWA (źródło: root SCARS.md:20, archiwum to korpus literatury)
- **Kontrola bez narzędzia** (konkret): SEVerA bez grafu → ogólnik z treningu, bez cytatów/triple'i; rozjazd mierzalny

D-001..D-005 wszystkie RESOLVED/DECISION. Pilot commituje się w repo KR (własny .git); root trackuje tylko flagi/HANDOFF/STATE (projects/*/ w root .gitignore).

Next: człowiek wpisuje oczekiwanie Q-ground → uruchomić pilot na archiwum ARL (graph.db, read-only), zweryfikować grounding + odmowę.
