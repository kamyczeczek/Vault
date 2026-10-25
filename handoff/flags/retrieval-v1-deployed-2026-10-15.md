---
type: Concept
flag: retrieval-v1-deployed-2026-10-15
since: 2026-10-15
owner: mateusz
agent: pi
model: nara/deepseek-v4.1-flash-free
origin: session-close
title: retrieval-v1-deployed-2026-10-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`retrieval-v1-deployed-2026-10-15` — 2026-10-15: Wdrożono K1 jako `scripts/memory/retrieval_v1.py`.

- Recall@5: 81.5% (22/27), refusal: 81.8% (9/11), MRR: 0.778 na 38-pytaniowym gold secie.
- H5 odrzucona jako overfit (0/5 nowych pytań złapanych, 2/6 starych).
- Parity proof: `scripts/_scratch/parity_retrieval_v1.py` — deployed module reproduces K1 exactly.
- Metryki: `scripts/_scratch/k_results_38.json`.
- Nie rozwiązane: 2 klasy wycieku (over-stemming `alla`→`all`, vocabulary overlap `zasad`/`hold`) — próg refusal ≥90% odłożony.

not checked:
- wektory, reranker, graf (brak dowodu potrzeby na tym korpusie).
- sesje z innych wątków (patrz residue inventory w `scripts/_scratch/`).
- `HANDOFF.md` i `handoff/flags/INDEX.md` w tym commicie odwołują się do dwóch flag untracked (`governance-ontology-prototype-2026-10-15`, `brain-ingest-versioning-measurement-2026-10-15`) — dług zastany (R19 advisory), nie wprowadzony tym commitem.
