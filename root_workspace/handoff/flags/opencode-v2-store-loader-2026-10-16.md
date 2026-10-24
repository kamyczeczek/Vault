---
flag: opencode-v2-store-loader-2026-10-16
since: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`opencode-v2-store-loader-2026-10-16` — 2026-10-16: `agent_sessions.py::load_opencode_sessions` czyta teraz `session_v2`, a 2.0 renderuje przez `session_message` — sesje opencode 2.0 wracają do indeksu pamięci i do `last_session.bat`.

- Objaw: „opencode 2.0 nie pojawia się w bazie", `last_session.bat` nie odtwarza sesji 2.0. Jedna przyczyna: loader (używany **i** przez `memory_index.py`, **i** przez `agent_sessions.py last`) czytał tylko tabele v1 `session`/`message`/`part`; opencode 2.0.30 pisze `session_v2` + `session_message`. `session` miało **0** wierszy z `version` 2.x; `session_v2` = 229 (= 228 v1 + 1 nowa 2.0).
- Fix (minimalny, korpus historyczny nietknięty): lista sesji z `session_v2`; render z `session_message` **tylko** dla sesji bez wierszy `message` (nowe 2.0). Stare sesje renderują się identycznie jak dotąd (dawna ścieżka `message`/`part` wydzielona do `_render_opencode_legacy`).
- Weryfikacja: `agent_sessions.py list --agent opencode --limit 6` → sesja 2.0 („Warstwa brain…") na czele; stara „Opencode update problem" nadal 42 wiadomości (render bez zmian); `test_agent_sessions.py` zielony (exit 0); `memory_index.py ingest` → 1 nowa sesja / 219 chunków; `stats` opencode **228→229**; `query` trafia w `ses_ebdc7fc4::*`; `freshness` lag 0:00:04.
- Blizna: `SCARS.md` **S68** (cicha migracja schematu store'u = brak wierszy bez błędu). `ingest_brain.py --check` → 47 problems / 22 decisions / 2 lessons, zielone; `eval_brain.py --check` bez regresji (hit@5 9/10, refusal 3/4, MRR 0.900).

not checked:
- Nie zmigrowano renderu starych sesji na v2 (świadomie — opcja „ujednolić na v2" odrzucona przez właściciela; `--rebuild` przepisałby render 228 sesji i zmienił `chunk_id`).
- tylko happy-path loadera; nie sprawdzono innych agentów (goose/hermes/pi/omp/jcode/cursor/droid/cline/deepseek) pod kątem podobnej migracji schematu — objaw zgłoszony tylko dla opencode.
- Bieżąca sesja (`ses_ebdc7fc4…`) jest w indeksie jako snapshot do momentu ingestu; dalsza część dopisze się przy następnym `ingest`.
