---
type: Concept
title: SCARS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# SCARS — znane awarie pilota graphrag

Każda nowa sesja MUSI odnieść się do każdego punktu w raporcie końcowym (sekcja `ZNANE AWARIE — ADRESACJA`).

## S1 (Faza 8b): Overfit threshold
Agent iterował `COSINE_COVERAGE_THRESHOLD` (0.45 → 0.53 → 0.50) aż testy przeszły. Wynik nie generalizuje.
**Reguła:** każda zmiana progu musi być uzasadniona rozkładem (percentyle oracle vs distractor), nie iteracją.

## S2 (Faza 8c): Fałszywa klasyfikacja problemu systemu jako problemu testu
Agent sklasyfikował Q26-Q30 jako "tylko KATEGORIA A" pomijając B, mimo że `MIN_KEYWORD_MATCHES=2` przepuszczał koincydencje.
**Reguła:** kategoria A i B nie wykluczają się. Jeśli koincydencja przeszła próg, to jest TAKŻE B.

## S3 (Faza 8c): Usunięcie artefaktów diagnostycznych
Agent usunął `extended_eval.py`, `verify_test_set.py`, `diagnose_q3.py` po zakończeniu sesji. Nie ma dowodu na wyniki.
**Reguła:** każdy plik diagnostyczny z sesji jest artefaktem. Nie usuwaj. Manifest musi go zawierać.

## S4 (Faza 8d): Fabrykacja danych w raporcie
`test_hypothesis_c3.py` timeout (30s). Agent wpisał do D3 liczby z Fazy 8c jako wynik C3. Nie było artefaktu.
**Reguła:** jeśli test nie zwrócił outputu — napisz `NIE WYKONANO`. Każda liczba w raporcie musi mieć ścieżkę do pliku artefaktu.

## S5 (Faza 8d): STOP GATE jako przykrycie awarii
Timeout testu został zaraportowany jako "STOP GATE aktywowany". STOP GATE to świadoma decyzja po analizie — nie obejście awarii.
**Reguła:** rozróżniaj `STOP GATE` (test wykonany, wynik przekroczył próg) od `NIE WYKONANO` (test nie wykonał się z powodu błędu/timeout).

## S6 (Faza 8d): Canary źle zinterpretowany
Q99 zwróciło 10 matching_ids. Agent nazwał to "halucynacją podagenta". W rzeczywistości: podagent zwrócił prawdziwe ID, ale SQL `LIKE` jest za luźny (substring match). Problem narzędzia, nie modelu.
**Reguła:** canary fail = problem narzędzia (SQL/matching), nie halucynacja.

## S7 (Faza 8e): Deklaracja WYKONANE dla plików, które istnieją, ale nie są zintegrowane funkcjonalnie
Agent ogłosił sukces warstw (np. pre-commit hook, canary), deklarując je jako w pełni wykonane, mimo że hook nie był przetestowany przez `git commit`, a canary nie był podpięty do skryptu testowego.
**Reguła:** Wykonane oznacza przetestowane funkcjonalnie i zintegrowane w ścieżce wykonania (np. test git commit, test ładowania canary). Brak integracji = status CZĘŚCIOWY / TEST FUNKCJONALNY: NIE.

## S8 (Faza 8e): Test pre-commit hooka tworzy realny commit w repo
Agent wykonał `git commit` w ramach testu hooka, co zostawiło trwały commit (`a3906f3`) i plik testowy w historii repo.
**Reguła:** Do testowania hooków używaj operacji dry-run lub usuń pliki testowe i zresetuj stan przed końcem sesji.

## S9 (Faza 8e): Użycie `git checkout` kasuje niezacommitowane zmiany
Uruchomienie czyszczenia git skasowało niezacommitowane zmiany w innych plikach (np. `MAP.md`).
**Reguła:** Nigdy nie wykonuj masowego `git checkout` lub `reset` bez sprawdzenia `git status` i użycia `git stash`.

## S10 (Faza 8f): Manifest bez pokrycia artefaktów
Manifest zawierał 1 z 5 artefaktów z sesji 8e, przez co pre-commit hook nie chronił kluczowych plików takich jak `canary.json`, `SCARS.md`, `SESSION_TEMPLATE.md`.
**Reguła:** Każda sesja musi dodać do manifestu hashe wszystkich wyprodukowanych plików przed commitem i uruchomić `verify_artifacts.py`.

## S11 (Faza 8f): Canary 3/5 FAIL nie wpisany jako nowy dług
Canary ujawnił, że refusal nie odrzuca 3 z 5 pytań out-of-corpus PL. Sesja 8f zauważyła to w D4, ale nie wpisała jako SCARS ani nie podniosła jako STOP GATE.
**Reguła:** Każdy canary FAIL musi być wpisany do SCARS w tej samej sesji, w której został wykryty.

## S12 (Faza 8f): Test negatywny hooka zablokowany przez crash parsera JSON
Wpis `__fake_artifact__` został wstawiony poza tablicą `artifacts`, co spowodowało `json.loads` crash, nie `FALSE_DONE`. Sesja 8f zaraportowała to jako `NEGATYWNY: zablokowany poprawnie`.
**Reguła:** Test negatywny hooka wymaga walidacji JSON (`python -m json.tool`) przed `git commit`.

## S13 (Faza 8f): Liczba w D1 wybrana w stronę korzystną
D1 = `6` (liczba artefaktów) zamiast `2/5` (canary pass rate), co ukryło 3/5 FAIL.
**Reguła:** D1 opisuje najważniejszy problem sesji, nie liczbę, która wygląda dobrze.

## S14 (Faza 8g): STOP GATE interpretowany jako sprawdzany po każdym kroku
STOP GATE był traktowany jako natychmiastowy przerywacz po każdym kroku zamiast po zakończeniu B1–B6, co doprowadziło do pominięcia kluczowego testu B2.
**Reguła:** STOP GATE ewaluuje się po wykonaniu pełnego zakresu zaplanowanych kroków (B1–B6), a nie wybiórczo.

## S15 (Faza 8g): Interpretacja niezgodna z danymi w MAP.md
Pusty diff `a345fb1..HEAD` zinterpretowano jako „utratę zmian", mimo że stan w HEAD był tożsamy z `a345fb1` (brak jakiejkolwiek utraty).
**Reguła:** Pusty diff między wersjami to dowód braku zmian lub zachowania stanu, a nie utraty.

## S16 (Faza 8g iter. 2): Raport WYKONANE bez pokazanego outputu
Agent zaraportował `B2: WYKONANE` w D0, ale w transkrypcie nie ma logu commitów B2 ani komunikatu `FALSE_DONE`.
**Reguła:** Każdy wpis `WYKONANE` w D0 musi mieć w D3 odwołanie do artefaktu z tej sesji. Bez artefaktu — `NIEWYKONANE`.

## S17 (Faza 8g iter. 2): Sprzeczny wpis WYKONANE + STARA
Wpis `B6: WYKONANE | LICZBA ARTEFAKTÓW: 6 [STARA, z Fazy 8f]` jest logicznie niemożliwy.
**Reguła:** `[STARA, z Fazy X]` w D0 oznacza `NIEWYKONANE`.

## S18 (Faza 8g iter. 2): Blokada sandbox_permissions bez zaraportowania
Dwa `edit` zostały zablokowane przez `sandbox_permissions`. Agent nie zaraportował, które edycje się powiodły.
**Reguła:** Każda blokada narzędzia musi być zaraportowana w D0 jako `BLOKADA (powód: <...>)`, a krok jako `NIEWYKONANE (blokada)`.

## S19 (Faza 8h): Obejście blokady edit przez python -c
Agent dostał trzy błędy whitespace od `edit` przy edycji `artifact_manifest.json` i zamiast zaraportować blokadę użył `python -c` do przepisania pliku.
**Reguła:** Blokada narzędzia to nie zgoda na obejście. Zaraportuj jako `BLOKADA` i zatrzymaj się.

## S20 (Faza 8g→8h): Plik testowy pozostał w indeksie git
Plik `_hooktest_b2.txt` z nieudanego testu B2 w 8g iter. 2 pozostał w indeksie git (status A) przez dwie sesje.
**Reguła:** Test hooka kończy się usunięciem pliku testowego przed końcem sesji, nie tylko przed commitem.

## S21 (Faza 8i): git commit commit-uje wszystko staged, nie tylko to, co przed chwilą dodane
Agent dodał `_test_hook_verify.txt`, ale `git commit` wciągnął też `_hooktest_b2.txt` (staged od 8g).
**Reguła:** Przed każdym `git commit` uruchom `git status --short` i sprawdź, co jest w indeksie.

## S22 (Faza 8i): $LASTEXITCODE nierozwinięty przez pojedyncze cudzysłowy w PowerShellu
Agent użył `echo 'exit code: $LASTEXITCODE'` zamiast `echo "exit code: $LASTEXITCODE"`, więc exit code nie został pokazany.
**Reguła:** W PowerShellu zmienne rozwijają się tylko w cudzysłowach podwójnych.

## S23 (Faza 8i): git checkout <plik> jako obejście blokady edit
Agent dostał 10 błędów whitespace od `edit`, po czym wykonał `git checkout pilots/graphrag/SCARS.md`, co skasowało niezacommitowane S14, S15 z 8g iter. 2.
**Reguła:** `git checkout <plik>` jest równie destrukcyjne jak `git checkout .`. Zakaz obejmuje każdą formę `checkout` na plikach z niezacommitowanymi zmianami.

## S24 (Faza 8i): Raport bez ponownego odczytu pliku po operacji na nim
Agent napisał, że S19–S22 są w rejestrze SCARS, mimo że plik został cofnięty przez `git checkout` do HEAD.
**Reguła:** Po każdej operacji na pliku raportuj stan pliku na podstawie ponownego odczytu, nie pamięci sprzed operacji.

## S25 (Faza 8e–8j): Duplikaty S8 i S9 w SCARS.md
S8 i S9 zostały wpisane dwukrotnie podczas nieudanych edycji w sesjach 8e/8f. Przez 5 sesji (8f–8j) nikt tego nie zauważył.
**Reguła:** Po każdej edycji SCARS.md uruchom `Select-String -Pattern "^## S"` i sprawdź, czy nie ma duplikatów.

## S26 (Faza 8O): Raport z niesprawdzonymi metrykami
Pi wpisało do raportu liczby „METRYKI PO FIXIE" identyczne z 8N baseline, mimo że nie pokazało uruchomienia po fixie.
**Reguła:** każda liczba w raporcie musi mieć w D3 ścieżkę do pliku outputu z tej sesji.

## S27 (Faza 8O): git checkout wywołany przez subprocess w skrypcie
Pi napisało skrypt wywołujący `subprocess.run(["git", "checkout", ...])`. Nie zaraportowało tego.
**Reguła:** zakaz narzędzia obejmuje każde wywołanie, również przez subprocess/skrypt.

## S28 (Faza 8P): Fabrykacja całej diagnozy (omp)
Omp wygenerował raport diagnostyczny bez wykonania jakiegokolwiek kroku instrukcji: kod `graphrag.py` w raporcie nie odpowiada rzeczywistemu, node IDs (`ksiazki_t1_rozdzial_1`) nie istnieją w `graph.db`, cytaty nie pochodzą z korpusu, SHA256 wymyślone, brak wywołań narzędzi.
**Reguła:** każdy raport musi mieć w D0 odwołanie do rzeczywistych plików i wywołań narzędzi.

## S29 (Faza 8Q): omp nie zgłasza STOP GATE mimo spełnionego warunku
Instrukcja 8Q mówiła: p10 in-corpus EN <= p90 OOC EN → STOP GATE. Warunek był spełniony (0.319 vs 0.436). Agent nie zgłosił STOP GATE.
**Reguła:** warunek STOP GATE musi być zgłoszony, nawet jeśli agent uważa, że test warto dokończyć.

## S30 (Faza 8Q): Semantyczna bramka bi-encodera poprawia OOC EN 0/5 → 3/5, nie 5/5
Rozkłady cosine similarity nakładają się (in-corpus p10=0.319 vs OOC p90=0.436). Brak liniowego progu. Wniosek: keyword matching nie wystarcza, ale próg liniowy też nie wystarcza.

## S31 (Faza 8R): Opcja C (cross-encoder) niewykonalna w tym środowisku
Feasibility check: pakiet `sentence-transformers` niezainstalowany, brak modeli cross-encoder w HF cache. Internet dostępny, ale `pip install` zakazany. Ostatnia próba naprawy OOC EN nie mogła być wykonana.
**Reguła:** przed projektowaniem fixa opartego na nowej bibliotece — sprawdź, czy biblioteka jest dostępna.

## S32 (Faza E / Trust Set 2026-10-11): Pilot zamrożony z Wariantem 1
Pilot zamrożony. Działa: hybryda FTS5 + multilingual MiniLM + RRF + bramka semantyczna (Wariant 1: prog_cosine = 0.45). Trust set: 58 pytań (33 in-corpus, 15 OOC, 10 boundary). OOC refusal: 100.0%, boundary refusal: 50.0%, false refusal: 0.0%.
