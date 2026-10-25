---
type: Concept
flag: okf-rag-benchmark-local-2026-10-25
since: 2026-10-25
owner: codex
agent: codex
model: openai/gpt-6
origin: Notes/OKF-rag/benchmark-results-20.json
title: okf-rag-benchmark-local-2026-10-25
generated: { by: okf-enforcer/0.6, at: 2026-10-25T15:33:10Z }
---

`okf-rag-benchmark-local-2026-10-25` — 2026-10-25: utrwalono pełne, jawnie zrekonstruowane 20 pytań, hash korpusu i ranking source/passage dla `all` oraz `raw_only`; powtarzalne missy Q17–Q18 dostały dwa slice'y z mapą oryginalnych linii. Next: ręcznie przejrzeć Q02 i Q20 — jedyne pytania bez exact/related w top-10 — przed decyzją o potrzebie OKF-RAG.

not checked: nie oceniano treści generowanej odpowiedzi ani literalnej poprawności cytatu; OOC sprawdza retrieval abstention. Oryginalne prompty baseline nie zachowały się, więc zgodność prompt-for-prompt nie jest potwierdzona.
