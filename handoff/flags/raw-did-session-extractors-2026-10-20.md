---
type: Concept
flag: raw-did-session-extractors-2026-10-20
since: 2026-10-20
owner: mateusz
agent: opencode
model: opencode/glm-5.3-flash-free
origin: session-close
title: raw-did-session-extractors-2026-10-20
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`raw-did-session-extractors-2026-10-20` — 2026-10-20: dwa deterministyczne eksportory sesji agentów dostarczone i zweryfikowane na live store'ach.

- `scripts/raw_sessions.bat` (N, default 10) → `extract_exact_sessions.py --count N`: pełny transkrypt N ostatnich sesji (opencode sqlite v2/v1 + omp JSONL) bez ucinania tool payloadów. Wygenerowano 10 sesji (2523 KB) do `scripts/_scratch/sessions/raw_sessions.md`.
- `scripts/did_sessions.bat` (N, default 10) → `scripts/extract_did.py`: filtr po parts[].type, bez NLP/LLM — zostawia user text, assistant text oraz mutujące tool-calle (`write`, `edit`, `bash`/`shell`, `question`/`ask`, `skill`) z pełnym input/output; pomija reasoning, read-only (read/grep/glob/list/webfetch/codesearch), step-start/step-finish i zdarzenia harnessu. Wygenerowano 10 sesji (1351 KB) do `scripts/_scratch/sessions/did_sessions.md`; nagłówek każdej sesji deklaruje `Pominięto: reasoning×N, read-only×N`. Shell'e wliczane w całości (klasyfikacja treści komendy = heurystyka, poza formatem).
- Wyjście z root przeniesione do `scripts/_scratch/sessions/`: integrity gate zgłosił `raw_sessions.md` i `did_sessions.md` jako unexpected root files; naprawiono przez usunięcie kopii z roota (dane jako routed artefakty), nie przez rozszerzenie gate'a. Parametr `%2` obu .bat pozwala podać własną ścieżkę wyjścia.
- Memory index: gate R14 padł na pusty `memory.db`; naprawa nazwanym fixem `python.exe scripts/memory_index.py ingest` — 1500 sesji, 213 854 chunks, drift OK.
- Fix R15 (data, nie próg): eval memory retrieval na korpusie 1500 sesji mierzył 12/15, bo okno top-5 zliczało chunki, a "expected" jest sesją — duplikat chunków tej samej sesji jadł sloty i maskował kandydatów (symulacja w `scripts/_scratch/eval_dedup_probe.py`: dedup per-session → na tym samym korpusie 15/15). Minimalna poprawka w `scripts/eval_memory_retrieval.py`: dedup distinct-session przed wycięciem okna + re-fetch gdy dedup skurczył bufor; zmierzono `hit@5=1.000 MRR=0.557 (15/15)`. Złote zapytania, excludes i próg nietknięte.

Next step: owner decyduje, czy domyślnym wyjściem ma zostać `scripts/_scratch/sessions/` (stan obecny), czy root ma znowu trzymać `raw_sessions.md` (wtedy deklaracja w ALLOWED_ROOT).

not checked: fallback `_generic_events` dla agentów poza opencode/omp (goose, hermes, jcode, cursor, droid, deepseek, cline) — nieużywany w wygenerowanych eksportach (N=10 to czysty opencode); omp w `_pi_style_events` sprawdzony tylko ad hoc (throwaway run N=13), nie w artefakcie z tej sesji; popełnione skrypty (extract_exact_sessions.py, last_session_merged.py, agent_sessions.py) poza zakresem tej sesji i nieweryfikowane; fix R15 zmierzono na korpusie po jednym ingest — brak ponownego uruchomienia ingestu i re-weryfikacji 15/15 po drugim ingest.
