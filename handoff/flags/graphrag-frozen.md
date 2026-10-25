---
type: Concept
flag: graphrag-frozen
since: 2026-10-11
owner: root
ag: root
title: graphrag-frozen
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Pilot graphrag — zamrożony (Faza 8S)

Pilot graphrag w `projects/research/knowledge-retrieval/pilots/graphrag/` został zamrożony po Fazie 8R.

**Osiągnięcia:**
- In-corpus EN (10 pytań): MRR@5 = 0.950, Recall@5 = 1.000
- In-corpus PL (13 pytań): MRR@5 = 0.183, Recall@5 = 0.300
- OOC PL (5 pytań): refusal 5/5
- Canary (5 pytań): refusal 5/5 (po fixie v2, commit `5bc4859`)
- Infrastruktura: manifest + pre-commit hook + SCARS + SESSION_TEMPLATE

**Znany dług (nierozwiązany):**
- OOC EN (Q26–Q30): refusal 0/5 (baseline) lub 3/5 (semantic gate z 8Q).
- Przyczyna: `MIN_KEYWORD_MATCHES=2` + generyczne angielskie słowa (`release`, `price`, `market`, `president`, `company`, `million`, `today`) w niepowiązanych kontekstach.
- Rozwiązanie wymaga architektury semantycznej (cross-encoder / LLM-as-judge), niedostępnej w obecnym środowisku bez `pip install`.

**Wznowienie wymaga decyzji właściciela.** Możliwe ścieżki:
- A: zaakceptować dług jako znany (pilot działa dla pytań z korpusu, nie dla OOC EN),
- B: otworzyć nowy projekt z semantic rerankerem jako osobną architekturą.
