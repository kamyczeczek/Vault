---
type: Concept
flag: sessions-lab-icm-restructure-2026-10-21
since: 2026-10-21
owner: mateusz
agent: opencode
model: opencode/minimax-m3.1-flash-free
origin: session-close
title: sessions-lab-icm-restructure-2026-10-21
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`sessions-lab-icm-restructure-2026-10-21` — 2026-10-21: `scripts/_scratch/sessions/` przebudowane na ICM (one folder, one job), 740 MB → 389 MB, martwizy wyczyszczone, referencje zaktualizowane w tym samym przebiegu.

- **Struktura** (6 folderów + plik wejściowy): `01_tools/` (fabryka: eksporter ground-truth + launchery + shim), `02_products/` (produkty: raw / did / merged / full / actions / ground-truth + sidecary), `03_records/sessions/` (bodies sesji), `04_payloads/` (pełne wyjścia tool-calli + MANIFEST), `05_store/` (`memory.db` + `queries.jsonl`), `90_archive/` (superseded + martwizy). Każdy folder ma własny `CONTEXT.md` (inputs / process / outputs / human check); wejście: `scripts/_scratch/sessions/CLAUDE.md` (routing, <60 linii), wiersz w root `CLAUDE.md` ("Where things live") wskazuje na lab.
- **Ścieżki kontraktowe przeniesione** (referencerzy zaktualizowani w tym samym przebiegu): `scripts/memory_index.py` (`DB_PATH` → `05_store/memory.db`), `scripts/memory_index_check_drift.py`, `scripts/check_workspace_integrity.py` (R16 → `05_store/queries.jsonl`), `scripts/agent_sessions.py` (`OUTDIR` → `02_products`), `scripts/extract_did.py`, `scripts/extract_exact_sessions.py`, `scripts/last_session_merged.py` (`OUTDIR` + nowe `--records-dir` / `--payloads-dir`), `scripts/raw_sessions.bat`, `scripts/did_sessions.bat`, oraz dokumenty `CLAUDE.md`, `DECISIONS.md`, `brain/CONTEXT.md`, `scripts/memory/CONTEXT.md`, `skills/debug-with-memory/SKILL.md`, `tools/governance_ontology_prototype.py`. Linki w produktach liczone są względem pliku, w którym siedzą (`../03_records/sessions/…`, `../04_payloads/…`).
- **Usunięte martwizy** (po sprawdzeniu referrerów): `90_archive/ARCHIVE/memory.db` (326 MB — stara kopia sklepu z 10-18, nic nie wskazywało), `browse_all.html` (11 MB), `browse.html`, `sessions_dump.txt` (16 MB), `Kontynuacja-pracy-2026-10-03.json` (5 MB). Podkatalog `last_sessions/` (poprzedni layout rekordów) i `sess_1003.py` (dump sesji z rozszerzeniem `.py`) → `90_archive/`.
- **Promocja testów**: `test_zstd.py` / `test_load_deepseek.py` ze scrachu → `scripts/smoke_zstd.py` / `scripts/smoke_load_deepseek.py` (tracked). Uczciwe nazwy: to **skrypty dymne** (print, zero asercji), więc NIE są pokryciem testowym parsera zstd/DSH — realne testy pytest nadal nie istnieją.
- **Naprawa loadera (S68 powtórzone)**: `load_opencode_sessions` czytał tylko `session_v2`, a żywy opencode zapisuje sesje główne z powrotem do tabeli `session` — 6 ostatnich sesji (10-19 15:25 → 10-21) były niewidoczne. Loader czyta teraz **unię** obu tabel (dedup po `id`, wybór wiersza z późniejszym `time_updated`).
- **Ground truth jako produkt**: `session_ground_truth.py` przebudowany w iteracjach recenzji (nagłówki-metadata, numerowane operacje, global feed, atrybucja commitów z markerami revert/delete, jawne „reverts: 0") — teraz w `01_tools/`, produkt w `02_products/`. Ścieżki w narzędziu kotwiczone na `AGENTS.md` (nie na stałej głębokości), więc przetrwa kolejne przeniesienie folderu.
- **Weryfikacja**: loadery widzą sesje 10-20/10-21 ✓; `memory_index.py freshness` OK (lag 2:50) ✓; eksportory (raw / did / merged / full / actions / ground truth) piszą do `02_products` ✓; linki produktów rozwiązywują się ✓; `check_workspace_integrity.py` → **OK** (po `ingest_brain.py`, bo R21 driftował na zmienionej linii DECISIONS.md) ✓; `git diff --check` OK ✓.
- **Samo-uszkodzenie i naprawa**: `Set-Content -Encoding UTF8` (PowerShell 5.1) dodał BOM do trzech tracked plików — wykryte i naprawione (restore + ponowne edycje narzędziem edycji, bez BOM); `last_session_merged.py` oczyszczony z BOM na poziomie bajtów (miał niezacommitowane zmiany z poprzedniej sesji). Wniosek: w tym workspace nie używamy `Set-Content` do edycji tracked plików.

Next step: decyzja właściciela o commicie — zmodyfikowane tracked: `CLAUDE.md`, `DECISIONS.md`, `brain/CONTEXT.md`, `scripts/{agent_sessions,check_workspace_integrity,extract_did,last_session_merged,memory_index,memory_index_check_drift}.py`, `scripts/{raw_sessions,did_sessions}.bat`, `scripts/memory/CONTEXT.md`, `skills/debug-with-memory/SKILL.md`, `tools/governance_ontology_prototype.py`; nowe: `scripts/smoke_zstd.py`, `scripts/smoke_load_deepseek.py`. Do decyzji pozostaje też commit resztek z poprzedniej sesji (`scripts/agent_sessions.py`, `scripts/test_last_session_merged.py`, `handoff/flags/merged-session-loss-declarations-2026-10-19.md`, `scripts/extract_exact_sessions.py`).

not checked: bitowa równoważność usuniętego `ARCHIVE/memory.db` z żywym sklepem (obie kopie były pochodne i odbudowywalne, ale zawartości nie porównano); testy `scripts/test_extract_did.py` nie istnieją — `extract_did.py` zmieniony tylko ścieżką wyjścia (domyślna), bez zmiany logiki filtru; `scripts/smoke_*.py` to skrypty dymne bez asercji, więc realne pokrycie testowe parsera zstd/DSH nadal nie istnieje.
