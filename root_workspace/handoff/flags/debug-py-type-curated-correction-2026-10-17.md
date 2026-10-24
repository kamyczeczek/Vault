---
flag: debug-py-type-curated-correction-2026-10-17
since: 2026-10-17
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`debug-py-type-curated-correction-2026-10-17` — 2026-10-17: Domknięto jedyną lukę z review — pominięty test `debug.py "<query>" --type curated`. Wynik: **jest równoważne** `memory_index.py query "<query>" --type curated` (identyczny call: `chunk_type_filter='curated'`, `boost_curated=False`; **te same `chunk_id`**). Dopisano **S79** (korekta S77: S77 dotyczy tylko `debug.py` **default** — the door), doprecyzowano `scripts/memory/CONTEXT.md`. S77 i S76 nietknięte (zapis tego, co poprzednie sesje sądziły). Next step: nic — recall blizny = `--type curated` (w `debug.py` **lub** `memory_index.py`) na **świeżym** shelfi + `get <chunk_id>`.

Weryfikacja wejścia: HEAD `bb9b6d7`, drzewo czyste, `check_workspace_integrity.py` OK (EXIT=0).

Świeżość shelfu (kontrola przed testem, `ingest_curated_shelf` — shelf-only, bez ingestu sesji, R15 nietknięty):
`SHELF S7x: SCA::25=S70 … SCA::30=S75 SCA::31=S76 (candidate) SCA::32=S77 SCA::33=S78` → shelf był **świeży**, wynik nieskażony.

Raw output (S65, nie streszczenie), fraza `session database recall before fixing failure`:

A. `debug.py "<fraza>" --type curated` (default `--limit 5`):
   `[memory] tokens: session database recall` / `query: 'session database recall' type=curated` / `1 hit(s):` / `curated::curated::SCA::32 2026-10-17 23:34:00 [curated] ## S77: debug.py nie jest równoważne --type curated dla …`

B. `debug.py "<fraza>" --type curated --limit 10`:
   `[memory] tokens: session database recall` / `1 hit(s):` / `curated::curated::SCA::32 … ## S77: …`
   (identyczne z A — `--limit` nie zmienia zbioru, filtr `curated` już zawęża pulę)

C. `memory_index.py query "<fraza>" --type curated --limit 10`:
   `curated::curated::SCA::32 score=-15.083 ## S77: debug.py nie jest równoważne --type curated dla recallu blizn — cura`

D. A == B == C: **ten sam `chunk_id` (`curated::curated::SCA::32`)**. `SCA::32` = **S77**, bo S77 sama cytuje testowaną frazę i wyprzedza S75 bm25. Kontrola bez tej kolizji (`pominiecie odpytania bazy sesji agentow`):
   E1. `debug.py "<fraza>" --type curated --limit 5` → `tokens: pominiecie odpytania bazy` / `1 hit(s): curated::curated::SCA::30 … ## S75: Pominięcie odpytania bazy sesji agentów przed napraw…` (= **S75**)
   E2. `memory_index.py query "<fraza>" --type curated --limit 5` → `curated::curated::SCA::30 score=-46.825 ## S75: …` → **E1 == E2, `SCA::30`**.
   F. `get curated::curated::SCA::30` → `session_id: curated::SCARS.md`, `raw_path: …\SCARS.md` → chunk blizny, nie nagłówek.

Mechanizm (zweryfikowany kodem): `debug.py:123-129` → `query_memory(chunk_type_filter=args.type, boost_curated=(args.type is None))`; `memory_index.py:425-427` dodaje `chunk_type = ?` gdy filtr ustawiony, `memory_index.py:441` wyklucza curated tylko gdy `chunk_type_filter is None and not boost_curated`. Dla `--type curated` **oba** narzędzia robią identyczne zapytanie — brak osobnej ścieżki kodu.

Spójność S77 (§3): Zasada S77 mówi „recall blizny to `--type curated` … **nie `debug.py`**" — nie rozróżnia defaultu od `--type`. Problem S77 słusznie mówi „0 curated na **żadnym** `--limit`" (wersja o „wymaga większego `--limit`" nie weszła do finalnego S77) — ta część jest spójna z testem B z poprzedniej sesji i z kodem. Przestrzelenie jest jedno: brak „default vs `--type`". Nie edytowano S77 (hard rule) — S79 zawęża jego zakres.

Decyzja: `debug.py "<query>" --type curated` = **równoważne** `memory_index.py query "<query>" --type curated` → **S79 dodane**; `scripts/memory/CONTEXT.md` doprecyzowane (linia o `debug.py` mówi teraz „**default** … (S77)", plus akapit o `--type curated` = S79).

S76 (§5): decyzja **C + kandydat B** — zostawione jak jest (S76 nie w `brain.db`, bulle jako `id=1023/1024`), `parse_scars` w `ingest_brain.py` **nie** ruszane (osobny effort, R21 hard gate). S78 nietknięte. Stary flag `recall-protocol-curated-correction-2026-10-17` **nie** edytowany ani nie usunięty (owner: mateusz — nie edytuję cudzej flagi); jego twierdzenie o `debug.py` zawężone przez S79.

Bramki: `ingest_brain.py` rebuild → `problems <- SCARS.md 59 row(s)` (było 58; S79 sparsowane, heading `## S79:` bez parenthetical); `ingest_brain.py --check` OK; `eval_brain.py --check` OK (`hit@5=9/10 refusal=3/4 MRR=0.900`, baseline `brain_eval.json` nietknięty); `check_workspace_integrity.py` EXIT=0; `git diff --check` EXIT=0.
R16 trace: `memory_index.py query "debug.py type curated recall S79" --type curated --limit 3` → `curated::curated::SCA::34 score=-44.465 ## S79: debug.py --type curated **jest** równoważne`.

Zmiany: `SCARS.md` +S79; `scripts/memory/CONTEXT.md` (2 zdania o `debug.py`).

not checked:
- fraza `session database recall before fixing failure` zwraca dziś `SCA::32` (S77), nie `SCA::30` (S75) — bo S77 cytuje tę frazę; nie badano, czy to trwałe zjawisko dla fraz pojawiających się w kolejnych bliznach (kolejne S<n> będą wypychać starsze) — kandydat do obserwacji, nie do fixu.
- dalsze frazy PL/EN poza `pominiecie odpytania bazy sesji agentow` i frazą z flagi — nietestowane (dwie frazy wystarczyły do rozstrzygnięcia równoważności przez tożsamość kodu).
- `debug.py --type error|decision|tool|content` z curated-adjacent zapytaniami — nietestowane (poza celem).
- `debug.py --tokens` != 3 (`extract_tokens` cap) vs pełna fraza w `memory_index.py query` — składnia tokenów różna, ale przy `--type curated` oba i tak zwracają te same top chunki dla obu testowanych fraz; nie badano przypadków granicznych.
- wpływ shelf-only refresh (`ingest_curated_shelf`) na R14 freshness — nie badany (jak w poprzedniej sesji).
- `parse_scars` w `ingest_brain.py` (regex nie toleruje `## S<n> (candidate):`) — S76 leak `id=1023/1024` nadal obecny; **kandydat B na osobny effort** (zmiana `ingest_brain.py`, R21 hard gate), świadomie nie zrobione w tej sesji.
- czy inne pliki mają nagłówki `## S<n> (…)`, które `ingest_brain` gubi — sprawdzono tylko SCARS.md.
