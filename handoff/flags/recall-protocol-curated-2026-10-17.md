---
flag: recall-protocol-curated-2026-10-17
since: 2026-10-17
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`recall-protocol-curated-2026-10-17` — 2026-10-17: Zweryfikowano hipotezę recallu S75/S73 (problem w metodzie query, nie w indeksie) i naprawiono protokół w `scripts/memory/CONTEXT.md` oraz dodano S76 do SCARS.md. Next step: clean close.

hipoteza: potwierdzona
fix: protokół
recall: A=brak B=jest C=jest

Zweryfikowano hipotezę, że S75/S73 są nieosiągalne w standardowym `memory_index.py query` z powodu domyślnego wykluczenia `chunk_type='curated'`.
Wyniki testów:
- A (default query dla S75): brak S75 (raw output: trafienia tylko w sesjach, brak SCARS.md)
- B (--type curated dla S75): S75 znaleziono (score -8.544, chunk `curated::curated::SCA::0`)
- C (debug.py dla S75): debug.py poprawnie promował curated (`boost_curated=True`) i zwrócił wyniki
- D (--type curated dla S73): S73 znaleziono (score -10.234, `curated::curated::fla::1`)

Podjęte działania:
1. Zaktualizowano `scripts/memory/CONTEXT.md` sekcją wyjaśniającą protokół recallu i różnicę między domyślnym wyszukiwaniem w transkrypcjach a `debug.py` / `--type curated`.
2. Dodano S76 do `SCARS.md` dokumentując błąd metodologiczny polegający na uznawaniu braku w domyślnym query za regresję indeksu.
3. Przebudowano bazę brain (`python.exe scripts/ingest_brain.py`) i przetestowano spójność workspace (`check_workspace_integrity.py` OK).

not checked:
- Ewentualny wrapper skryptowy typu `recall.py` (odłożone jako nadmiarowe, `debug.py` w zupełności wystarcza).
