---
type: Concept
flag: cold-start-recall-proof-2026-10-17
since: 2026-10-18
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: cold-start-recall-proof-2026-10-17
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`cold-start-recall-proof-2026-10-17` — 2026-10-17: Cold-start walk test recallu wykonany end-to-end — świeży agent, czytając tylko `HANDOFF.md` + `scripts/memory/CONTEXT.md`, z objawu „agent pominął recall przed naprawą nieznanego błędu" **znajduje S75 bez czytania kodu i transkryptów**. Domknięta luka end-to-end ~0% z review (`ses_eb43216f`): cold start **działa**. S81 **nie potrzebne**, dokumentacji nie zmieniano (nic nie było zepsute). Next step: decyzja ownera o 6 długach nazwanych w `review-debt-named-s80-2026-10-17` (stary flag edit vs retire, S76 leak, S78 retire).

Wejście: HEAD `2617369` (S80), drzewo czyste, `check_workspace_integrity.py` EXIT=0.

Krok 1 (cold read — bez czytania kodu, `SCARS.md` i transkryptów): `HANDOFF.md` linie 1–345/952 (output ucięty; flagi newest-first na górze), `scripts/memory/CONTEXT.md` linie 1–70/179 (sekcja „Recall — which command", 13–33, w całości); `AGENTS.md` w kontekście (wiersz session-memory → CONTEXT, „survey then `get <chunk_id>`"). HANDOFF **jednoznacznie** mówi, gdzie szukać: najnowsza flaga (linie 39–53) wkleja raw output z komendą i trafieniem.

Krok 2 (plan na kartce, źródło = HANDOFF/CONTEXT, nie pamięć): objaw → `memory_index.py query "<fraza>" --type curated --limit 5`, potem `get <chunk_id>`. Źródło: CONTEXT:19 (komenda `--type curated --limit 10`), CONTEXT:20–23 (zwraca chunk + `get` + świeżość shelfu), CONTEXT:31–33 (zero trafień na znaną bliznę = błąd metody), HANDOFF:39–53 (przykład z raw outputem).

Krok 3 (raw output, S65):

Freshness: `OK — index covers through 2026-10-17 23:49:27; newest on disk 2026-10-17 23:57:27 (lag 0:08:00)` → shelf świeży, `ingest` niepotrzebny.

Q1 (fraza literalna z HANDOFF): `memory_index.py query "pominiecie odpytania bazy sesji agentow" --type curated --limit 5`:
- `curated::curated::fla::4  score=-47.908  D. A == B == C ...`
- `curated::curated::SCA::30  score=-46.162  ## S75: Pominięcie odpytania bazy sesji agentów przed naprawą nieznanego błędu (`
- `curated::curated::fla::9 / fla::2 / SCA::35`

Q2 (fraza złożona samodzielnie z objawu — **nie** z HANDOFF): `query "agent pominiecie recallu przed naprawa nieznanego bledu" --type curated --limit 5` → rank 1 `curated::curated::SCA::30 score=-38.587 ## S75: ...`; dalej `fla::4 / fla::4 / fla::0 / SCA::34`.

Q3 (fraza EN): `query "session memory recall skipped before fixing unknown failure" --type curated --limit 5` → `SCA::30` (S75) na pozycji 5 (top-5).

Krok 4 (ścieżka sukcesu):
- HANDOFF:50: `curated::curated::SCA::30  score=-46.542  ## S75: Pominięcie odpytania bazy sesji agentów przed naprawą nieznanego błędu`
- CONTEXT:19: `python.exe scripts/memory_index.py query "<query>" --type curated --limit 10`
- Query: `... --type curated --limit 5` → `SCA::30` (top-5 w Q1/Q3, top-1 w Q2) → `get curated::curated::SCA::30` → `heading: ## S75: Pominięcie odpytania bazy sesji agentów przed naprawą nieznanego błędu`, `session_id: curated::SCARS.md`, `raw_path: ...\SCARS.md` = chunk blizny, nie nagłówek `SCA::0`.
- Czas: 3 próby; jedna wystarczała.

Krok 5 (test „gdybym nie znał S75"): objaw podany, CONTEXT daje komendę, fraza złożona z objawu trafia S75 na top-1 (Q2), `get` potwierdza treść. **Cold start: DZIAŁA.**

R16 trace: `query "cold start recall S75 proof" --type curated --limit 3` → `fla::0 / fla::1 / fla::2` (nie `SCA::30` — tokeny „cold start S75 proof" nie pokrywają się z polskim tekstem S75; to zapis trace, nie kryterium).

Uczciwa uwaga (ryzyko rezydualne): sukces częściowo ułatwiony tym, że najnowsza flaga HANDOFF (linie 39–61) sama wkleja raw output z komendą i trafieniem (S65). Ale Q2 pokazuje, że sama fraza z objawu + CONTEXT:19 wystarczają, więc ścieżka nie zależy od tego przykładu. Luka end-to-end: 0% → ~100%. Dokumentacji nie zmieniano — działa, nie psuję.

## Znalezisko przy close (nie dotyczy cold startu)

Close **nie przeszedł za pierwszym razem** — nie z powodu flagi, lecz **generowanego widoku**. `close.py` buduje `HANDOFF.md`/`INDEX.md` przez `build_handoff.py`, który dzieli flagi po `date.today() - INLINE_WINDOW_DAYS` (`build_handoff.py:78`, `INLINE_WINDOW_DAYS = 3`). Sesja przekroczyła **północ 2026-10-17 → 2026-10-18** w trakcie `pre-commit`: hook przebudował i zastagował widok z `today=10-17`, a krok `integrity` kilka sekund później zbudował widok z `today=10-18` → `HANDOFF.md is stale` (flagi `2026-10-14` przeszły z inline do `INDEX.md`).

Raw (S65):
- start: `git log --oneline -1` → `2617369`; `git status --porcelain` → clean.
- close.py → `pre-commit: workspace integrity failed` / `HANDOFF.md is stale` / `CLUSTER handoff/flags/T402-walk-test-2026-10-14.md <-> handoff/flags/cold-start-recall-proof-2026-10-17.md (shared: 10, 2026)`; `git status` po: `M HANDOFF.md`, `M STATE.md`, `A handoff/flags/cold-start-recall-proof-2026-10-17.md`.
- `python.exe scripts/build_handoff.py --check` → `STALE HANDOFF.md` **i** `STALE handoff/flags/INDEX.md`.
- Dowód przesunięcia okna: `git show HEAD:HANDOFF.md | Select-String state-export-levels-v3` → 2 trafienia; `HANDOFF.md` (po przebudowie) → 0; `handoff/flags/INDEX.md` → 1.
- `hooks/pre-commit:21-23`: rebuild `build_handoff.py`+`build_state.py`, ale `git add -- HANDOFF.md STATE.md` (**bez `handoff/flags/INDEX.md`**); `close.py` `allowed`/`add` też bez `INDEX.md` — **znany dług** (HANDOFF:248, flaga `residue-closeout-2026-10-15`: „luka `close.py` (`handoff/flags/INDEX.md` poza `allowed`/`find_strays`) — obejście przez `--include`").

Naprawa (dane, nie bramka — S62): `python.exe scripts/build_handoff.py` (widoki na `today=10-18`) → `--check` OK; re-close z `--include handoff/flags/INDEX.md` (istniejące obejście). **Nie zmieniono `build_handoff.py`, `hooks/pre-commit` ani `close.py`.**

Kandydat na bliznę (S81, **nie dopisany** — poza zakresem tej sesji, §3a): „generowany widok zależny od `date.today()` ⇒ close przekraczający północ / dzień przewinięcia okna (3d) failuje spuriously; `INDEX.md` poza zbiorem stagowanym przez `close.py` i hook".

not checked:
- **Stary flag `recall-protocol-curated-correction-2026-10-17` nadal przestrzeliwuje w `HANDOFF.md`** — mówi „`debug.py` nie jest równoważne `--type curated`" bez rozróżnienia default/`--type`. S79 to koryguje w `SCARS.md`, ale stary flag nie jest edytowany (owner: mateusz) ani wyretirowany. Wymaga decyzji ownera: edit (dopisać „skorygowane przez S79") vs retire. (z `review-debt-named-s80-2026-10-17`)
- **S76 leak w `brain/brain.db`** — `## S76 (candidate):` nieparsowalny przez `ingest_brain.parse_scars` (regex `^##\s+S(\d+)\s*:`); bulle S76 → `id=1023/1024`. Kandydat B: naprawić regex (osobny effort, R21). (`review-debt-named-s80`)
- **S78 (close.py friction) — decyzja ownera** — czwarty close.py scar; merytorycznie poprawny, możliwy szum; nie ruszany. (`review-debt-named-s80`)
- **S80 (kolizja frazy)** — dodane jako candidate, nie wdrożone; czysta fraza działa. Nie naprawiać bm25/tokenizacji (R15). (`review-debt-named-s80`)
- **`python -c`** — w sesji S79 użyto `python.exe -c "print(1)"` (no-op); trywialne naruszenie S8, nie warte blizny. (`review-debt-named-s80`)
- **R14 freshness po shelf-only refresh** — `ingest_curated_shelf` zmienia `sessions_meta` (updated_at), co sztucznie świeżuje R14; nie sprawdzono, czy maskuje realny lag. Kandydat: czy `ingest_curated_shelf` w ogóle powinien aktualizować `sessions_meta`. (`review-debt-named-s80`)

- **Nowo znalezione (nie z `review-debt-named-s80`)**: generowany widok zależny od `date.today()` — close w dniu przewinięcia 3-dniowego okna (tu: północ 10-17→10-18) failuje na `HANDOFF.md is stale`; `handoff/flags/INDEX.md` wciąż poza `allowed`/`add` `close.py` i hooka (obejście `--include`, HANDOFF:248). **Nie naprawiane** (poza zakresem, S62). Kandydat na bliznę S81.

S81: **nie potrzebne dla cold startu** — luka cold-startu nie istnieje, protokół wystarcza. Nie dopisano też S81 dla znaleziska przy close (poza zakresem §3a); zapisane w tym flagu jako kandydat.
