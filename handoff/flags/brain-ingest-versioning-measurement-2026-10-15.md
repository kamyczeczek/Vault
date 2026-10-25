---
type: Concept
flag: brain-ingest-versioning-measurement-2026-10-15
since: 2026-10-15
owner: mateusz
agent: pi-bolt
model: current
origin: session-close
title: brain-ingest-versioning-measurement-2026-10-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`brain-ingest-versioning-measurement-2026-10-15` — 2026-10-15: Migracja schematu brain.db, ingest plików MD, pomiar FTS5. Werdykt: A (Działający system).

- Dodano kolumny wersjonowania do `lessons`, `decisions`, `sessions`, `problems`.
- Zaingestowano deterministycznie `brain/lessons.md` oraz ADR-001 i ADR-002.
- Przeprowadzono pomiar na gold secie (5 answerable + 2 nieodpowiadalne): Hit@5 = 100%, MRR = 1.000, Odmowa = 2/2 (100%).
- System gotowy do rozszerzenia o SCARS.md i DECISIONS.md w kolejnej sesji.

not checked:
- Ingest SCARS.md, DECISIONS.md (poza zakresem tej sesji)

WYCOFANA 2026-10-16 przez `brain-memory-v1-landed-2026-10-16`: oba zastrzeżenia z `not checked`
zostały domknięte (ingest wyprowadzony do `scripts/ingest_brain.py`, kompletne SCARS.md +
DECISIONS.md), a pomiar 5+2 z tej flagi został zastąpiony przez
`scripts/memory/eval_brain.json` (10 answerable + 4 nieodpowiadalne, baseline zapisany w pliku).
Ta flaga była też ostatnim miejscem, w którym żyła teza „SCARS.md niezaingestowany” —
nieaktualna już w chwili jej powstania (24 wiersze były w `problems`).
