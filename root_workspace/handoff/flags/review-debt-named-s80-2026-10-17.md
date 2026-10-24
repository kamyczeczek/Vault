---
flag: review-debt-named-s80-2026-10-17
since: 2026-10-17
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`review-debt-named-s80-2026-10-17` — 2026-10-17: Domknięto dług nazwany w review `ses_eb43216f` — dodano S80 (kolizja frazy) i jawnie nazwano otwarte długi, żeby następna sesja nie czytała tylko starego flagu. Next step: decyzja ownera o starym flagu (edit vs retire), S76 leak, S78 retire.

Weryfikacja wejścia: HEAD `b8261fd` (S79), drzewo czyste, `check_workspace_integrity.py` OK (EXIT=0). Test decydował, nie instrukcja — każdy dług sprawdzony osobno (A–E poniżej).

Raw output (S65, nie streszczenie):

A. `Select-String -Path HANDOFF.md -Pattern "recall-protocol-curated-correction" -SimpleMatch` → linie 32–33 (stary flag żyje w widoku):
   `` `recall-protocol-curated-correction-2026-10-17` — 2026-10-17: ... `debug.py` **nie** jest równoważne `--type curated` dla recallu blizn ... ``
   `Select-String -Path HANDOFF.md -Pattern "debug.py.*nie.*równoważne"` → ta sama linia 33. Stary flag **nadal przestrzeliwuje** (brak rozróżnienia default vs `--type`).

B. `python.exe scripts/memory_index.py query "session database recall before fixing failure" --type curated --limit 5` (świeży shelf):
   `curated::curated::fla::2  score=-23.807  Raw output (S65, nie streszczenie), fraza `session database recall before fixing`
   `curated::curated::fla::5  score=-20.392  not checked:`
   `curated::curated::SCA::32  score=-15.080  ## S77: `debug.py` nie jest równoważne `--type curated` dla recallu blizn — cura`
   `curated::curated::SCA::34  score=-13.380  ## S79: `debug.py --type curated` **jest** równoważne `--type curated` — S77 dot`

C. `python.exe scripts/memory_index.py query "pominiecie odpytania bazy sesji agentow" --type curated --limit 5`:
   `curated::curated::SCA::30  score=-46.542  ## S75: Pominięcie odpytania bazy sesji agentów przed naprawą nieznanego błędu (`
   `curated::curated::fla::2  score=-26.009  ...`
   `curated::curated::SCA::34  score=-20.621  ## S79: ...`
   Kontrola parzystości narzędzi: `scripts/debug.py "<B>" --type curated --limit 5` → `fla::2`, `fla::5`, `SCA::32`, `SCA::34` (identycznie jak B); `scripts/debug.py "<C>" --type curated --limit 5` → `SCA::30`, `fla::2`, `SCA::34` (identycznie jak C). B=SCA::32 (S77) / C=SCA::30 (S75) → **kolizja frazy potwierdzona**.

D. `brain/brain.db` (skrypt w `%TEMP%\opencode\s76_leak_check.py`, nie `python -c`):
   `rows: [(1024, '**Zasada**: recall blizny/decyzji wymaga'), (1023, '**Problem**: `query_memory` (`scripts/me'), (1022, 'Nieuprawnione kasowanie katalogów na roo'), (1021, '`STATUS: OK` przy otwartych decyzjach wł'), (1020, 'Sfabrykowana wartość weryfikacji gdy wzo'), (1019, '`edit` zakończony bez weryfikacji zawart')]`
   `count>=1000: [(24,)]` → leak S76 (`id=1023/1024` jako niesparowane bulle) **nadal obecny**.

E. `Select-String -Path SCARS.md -Pattern "^## S80"` → **brak przed edycją**; po edycji linia 164: `## S80: Kolizja frazy — nowsze blizny cytujące frazę starszych wyprzedzają je w bm25 (candidate, 2026-10-17)`. Heading parseable (`^##\s+S(\d+)\s*:` trafia w `## S80:` — parenthetical po dwukropku, nie przed nim jak w S76).

Mechanizm (S80): bm25 dopasowuje tokeny — gdy nowsza blizna/flag cytuje frazę testową starszej, wyprzedza ją; fraza przestaje być „czystym" zapytaniem. To nie regresja indeksu: czysta fraza (C) trafia w S75 na obu narzędziach. Nie naprawiano tokenizacji ani `query_memory` default (R15), nie dodano `exclude_session_ids` (gaming).

Zmiany: `SCARS.md` +S80 (candidate) — 1 nowa blizna, bez edycji S77/S78/S79 i bez zmian w `scripts/**`.

Bramki: `ingest_brain.py` rebuild (S80 sparsowane), `--check` OK; `eval_brain.py --check` OK (baseline `brain_eval.json` nietknięty); `check_workspace_integrity.py` EXIT=0; `git diff --check` EXIT=0; `SCARS.md` kończy się dokładnie jednym `\n`.

not checked:
- **Stary flag `recall-protocol-curated-correction-2026-10-17` nadal przestrzeliwuje w `HANDOFF.md`** — mówi „`debug.py` nie jest równoważne `--type curated`" bez rozróżnienia default/`--type`. S79 to koryguje w `SCARS.md`, ale stary flag nie jest edytowany (owner: mateusz) ani wyretirowany. **Wymaga decyzji ownera**: (a) edit przez ownera (dopisać „skorygowane przez S79"), (b) retire (`rm` + re-close — ścieżka w `handoff/CONTEXT.md:55`), (c) zostaw i licz na to, że S79 jest czytane. Nowa flaga (ta) **nazywa** dług, nie naprawia go.
- **S76 leak w `brain/brain.db`** — `## S76 (candidate):` nieparsowalny przez `ingest_brain.parse_scars` (regex `^##\s+S(\d+)\s*:`), bulle S76 → `id=1023/1024` jako śmieci. **Kandydat B**: naprawić regex w `ingest_brain.py` (tolerancja `(candidate)`). **Nie w tej sesji** (R21 hard gate; `parse_scars` nietknięte).
- **S78 (close.py friction) — do decyzji ownera** — czwarty close.py scar (S66/S67/S69/S70 już pokrywają częściowo). Merytorycznie poprawne, ale możliwy szum. **Nie ruszane** w tej sesji.
- **S80 (kolizja frazy)** — dodane jako candidate, nie wdrożone. Testy A/B/C pokazały kolizję; czysta fraza (E1/E2) działa. **Nie naprawiaj** bm25/tokenizacji (R15).
- **`python -c`** — w sesji S79 użyto `python.exe -c "print(1)"` (no-op). Trywialne naruszenie S8. **Nie warte blizny** — odnotowane tutaj.
- **R14 freshness po shelf-only refresh** — `ingest_curated_shelf` zmienia `sessions_meta` (updated_at), co **sztucznie** świeżuje R14. Nie sprawdzono, czy to maskuje realny lag. **Kandydat**: sprawdzić, czy `ingest_curated_shelf` powinien aktualizować `sessions_meta` w ogóle.
