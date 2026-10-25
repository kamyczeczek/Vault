---
type: Concept
flag: retrieval-answer-contract-2026-10-25
since: 2026-10-25
owner: mateusz
agent: codex
model: openai/gpt-5
origin: session-close
title: retrieval-answer-contract-2026-10-25
generated: { by: okf-enforcer/0.6, at: 2026-10-25T03:41:33Z }
---

`retrieval-answer-contract-2026-10-25` — 2026-10-25: dodano kontrakt odpowiedzi
retrieval, porównano 15 wariantów zapytań dla pięciu raw-only missów i wdrożono
generator powtarzalnych source slices z manifestem i `origin_hash`. Slice
retrieval odzyskał właściwy temat jako top-1 w `5/5` przypadków, a `rg`
potwierdził źródłowe passage jako `direct`. Next: przetestować generator na
jednym dużym imporcie `napkin.md`.

not checked:
- pełny folder `Notes/OKF-rag` nadal ma stare wskaźniki Smart Connections po usuniętych prototypach;
- benchmark wszystkich 20 pytań nie został jeszcze ponownie uruchomiony na wygenerowanych slice'ach.
