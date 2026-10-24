---
flag: gate-advisories-deferred-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`gate-advisories-deferred-2026-10-24` — 2026-10-24: pięć otwartych pozycji zostaje **świadomie odłożonych**, nie zamkniętych. (1) R16 advisory: commit dotykający `scripts/**` bez świeżego `queries.jsonl` i bez „query” w temacie — jedyne uczciwe domknięcie to realne zapytanie do pamięci sesji, więc advisory zostaje do najbliższej sesji, która tej bramy faktycznie użyje. (2) R19 `did-sessions-default-5`: commit `1f1937f` ma temat bez roku, więc dopasowanie tokenów nie łapie go; bramka **nie jest** zmieniana (S62), a przepisanie historii byłoby droższe niż ostrzeżenie. (3) `direction_changes` w `session_digest.py:542` zwraca `brak reguły w rules-v1`, bo `classify_cards` nie ma dla niego gałęzi — sekcja istnieje i nigdy się nie wypełni; dopóki nie ma reguły opartej na polach karty i cytacie z `ending_evidence`, jawne `not_checked` jest uczciwsze niż dorabianie osądu. (4) `losses.dup` jest jawnie `not_extracted` (`session_digest.py:697`), zgodnie z ADR-005 — ciche zero byłoby kłamstwem; ekstrakcja wymaga definicji „dupa” w transkrypcie. (5) `--classify` działa tylko na rules-v1 (`CLASSIFIER_BACKEND="rules"`, `model_calls: 0`); backend modelowy odłożony świadomie.

not checked:
- czy R19 da się wyciszyć bez zmiany progu — nie: jedyne legalne wyjście to commit z tematem zawierającym token flagi, a `1f1937f` jest już w historii.
- czy reguła `direction_changes` jest w ogóle wyprowadzalna z obecnego schematu karty — nie sprawdzono; wymaga przeglądu `make_judgment` i pól `ending_evidence`, co jest osobną sesją.
- definicja `losses.dup` — brak; bez niej licznik mierzyłby coś innego niż nazwa.
