# Guard wiring audit — 2026-10-14

**Status końcowy: CZEKAM NA DECYZJĘ WŁAŚCICIELA.** Guardy istnieją jako pliki i mają
zdrową logikę, ale żaden nie jest wywoływany przez kod, hook ani wrapper. Pak
rewiewowy miał raczę co do wiring (krok 0, warunek STOP osiągnięty) i mylił się
co do `verify_report.py` — ten plik istnieje, działa i ma przechodzący test suite.

Środowisko pomiaru: Git Bash na Windows (bash equivalents komend PowerShell
z packa); `python` = `python.exe` z PATH. Data pomiarów: 2026-10-14 wieczór.

## Krok 0 — rekonesans (verbatim)

```
$ ls -la scripts/root_deletion_guard.py scripts/commit_gate_guard.py hooks/pre-commit .git/hooks/pre-commit
ls: cannot access '.git/hooks/pre-commit': No such file or directory
-rwxr-xr-x 1 Mateusz 197121  927 Oct 13 11:38 hooks/pre-commit
-rw-r--r-- 1 Mateusz 197121 1211 Oct 11 18:26 scripts/commit_gate_guard.py
-rw-r--r-- 1 Mateusz 197121 1448 Oct 11 18:26 scripts/root_deletion_guard.py

$ git config core.hooksPath
hooks

$ git config --show-origin core.hooksPath
file:.git/config	hooks
```

Oba selftesty przechodzą (output verbatim):

```
$ python scripts/root_deletion_guard.py --selftest
Running Root Deletion Guard selftest...
Root Deletion Guard selftest PASSED.
(exit: 0)

$ python scripts/commit_gate_guard.py --selftest
Running Commit Gate Guard selftest...
Commit Gate Guard selftest PASSED.
(exit: 0)
```

Uwaga metodyczna: `--selftest` napisany przez autora guarda nie jest dowodem
wiring — dlatego kroki 1–3 audytu opieram na grepach, probe zewnętrznym i
czytaniu hooka.

## Finding 1 — guardy są dekoracją: zero wywołań w kodzie (warunek STOP z packa)

Grep po workspace (`*.py,*.sh,*.json,*.md,*.jsonc,*.toml,*.cfg,*.txt`,
bez `.git`, `node_modules`, `__pycache__`) po wzorcach
`root_deletion_guard|commit_gate_guard|commit-approved` zwraca wyłącznie
trafienia **dokumentacyjne** w `handoff/` (m.in. `real_case_62b1e12d_report.md`,
`handoff/state_description/sessions/*.md`, `session-2c-master-plan.md`).
Zero trafień w hooku, wrapperze, configu lub skrypcie, który by guardy wołał.

`hooks/pre-commit` (tracked w git, executable, aktywny przez
`core.hooksPath=hooks` ustawiony lokalnie w `.git/config`) woła kolejno:
`git diff --cached --check`, `scripts/scan_secrets.py --staged`,
`scripts/build_handoff.py`, `scripts/build_state.py`,
`scripts/check_workspace_integrity.py`. **Nie woła** `root_deletion_guard.py`
ani `commit_gate_guard.py`.

**Precedens — ten workspace już to przeżył.** Flaga
`handoff/flags/gate_has_no_automatic_caller.md` (since 2026-10-03) opisuje
 Dokładnie ten wzorzec dla `check_workspace_integrity.py`: „potwierdzone, nie
domknięte", „to konwencja, nie automatyzacja", i dwie opcje dla właściciela
(hook vs jawna konwencja). Hook potem powstał — ale nowe guardy dodano
**bez** wiring, czyli wzorzec rekurencyjnie wrócił. Nowa flaga odnosi się do
tej.

## Finding 2 — korekta packa: `verify_report.py` ISTNIEJE (pack się mylił)

Pack twierdził: „`scripts/verify_report.py` — nie ma go w strukturze". W
drzewie jest:

```
$ ls -la scripts/verify_report*
-rwxr-xr-x 1 Mateusz 197121 8145 Oct 11 18:25 scripts/verify_report.py
-rwxr-xr-x 1 Mateusz 197121 4970 Oct 13 11:51 scripts/verify_report_evidence.py

scripts/verify_report_tests:
total 36
drwxr-xr-x ... fixtures
-rw-r--r-- 1 Mateusz 197121 1061 Oct 11 18:25 run_tests.py
```

Zewnętrzny test suite przechodzi:

```
$ python scripts/verify_report_tests/run_tests.py
Discrepancies found: 1
ROZBIEŻNOŚĆ [Line 2]: Wdrożono i przetestowano nowy model hybrydowy w konfiguracji `config.yaml`.
  Powód: No transcript action found referencing files: ['config.yaml']
----------------------------------------
4/4 passed
(tests exit: 0)
```

Flaga `verify_report_closed.md` zatem **nie** over-claimuje — jest to finding
wprost przeciwwny do twierdzenia packa („albo to kolejny over-claim").
Zastrzeżenie: `verify_report.py` sam nie ma automatycznego wywoływacza
(flag Next step: „use as baseline check on future sessions" — nikt go nie
woła); to osobny dług klasy Finding 1, nie fałsz flagi.

## Krok 1 — audyt trzech brakujących guardów (jedno zdanie każdy)

1. **Stop Gate Enforcer** — NIE ZAIMPLEMENTOWANY — brak kodu, brak śladu
   implementacji w transkrypcie; jedyny ślad to *propozycja* trybu
   `--gate-check` w `scripts/_scratch/sessions/last_session.txt`, której
   `scripts/close.py` nie zawiera (grep po `close.py` pusty).
2. **Read-After-Edit Enforcer** — NIE ZAIMPLEMENTOWANY — brak kodu w
   repo (grep `read.after.edit|read_after_edit` po `scripts/` i `hooks/`
   pusty) i brak wpisu w `SCARS.md` (grep pusty), więc twierdzenie sesji DSH
   „utrwalone w SCARS.md" było fałszywe w chwili pisania.
3. **Self-Modification Audit** — NIE ZAIMPLEMENTOWANY JAKO NOWY KOD — jego
   rolę przejął istniejący `scripts/check_workspace_integrity.py`
   (wywoływany z hooka); to gate integrity, nie guard samomodyfikacji, i
   sam w tej sesji wypada FAIL (Finding 6).

Korekta do tabeli packa: claim „Test: `--selftest` → PASSED" **bez outputu w
transkrypcie" — dziś selftesty przechodzą (output powyżej), a sprostowanie
`real_case_62b1e12d_report.md` zawierało je verbatim; problemem był moment
deklaracji, nie aktualny stan. Claim „5/5 guardów" jest fałszywy i po
sprostowaniu: realnie 2 pliki + 3 niezaimplementowane.

## Krok 3 — probe adversarialne (poza plikiem guarda)

Probe: `scripts/_scratch/probe_root_deletion_guard.py` (gitignored —
`.gitignore:20 scripts/_scratch/*`). Importuje `check_path_safe` z zewnątrz,
nie ufa `--selftest`. Pierwsze uruchomienie padło na **bugu probe**
(`ModuleNotFoundError` — zła ścieżka w `sys.path`), nie guarda; po naprawie:

```
$ python scripts/_scratch/probe_root_deletion_guard.py
OK: ...\root_workspace\projects -> safe=False (oczekiwano False) [protected root dir]
OK: ...\root_workspace\CLAUDE.md -> safe=False (oczekiwano False) [protected root file]
OK: ...\root_workspace\nowy_plik.tmp -> safe=True (oczekiwano True) [harmless new root file]
OK: ...\root_workspace\handoff -> safe=False (oczekiwano False) [protected root dir (handoff)]
OK: ...\root_workspace\scripts -> safe=False (oczekiwano False) [protected root dir (scripts)]
OK: ...\root_workspace\projects\research -> safe=True (oczekiwano True) [child of protected dir is allowed by design]
OK: ...\root_workspace\scripts\close.py -> safe=True (oczekiwano True) [child of protected dir is allowed by design]
OK: C:\Windows\System32 -> safe=True (oczekiwano True) [outside workspace root]
OK: ...\root_workspace\PROJECTS -> safe=False (oczekiwano False) [case variation on case-insensitive Windows FS]
OK: ...\root_workspace\claude.md -> safe=False (oczekiwano False) [case variation on protected file]

probe summary: 10/10 OK, 0 FAIL
(probe exit: 0)
```

Werdykt: logika `root_deletion_guard` jest zdrowa (warianty case na
case-insensitive FS trzymają się dzięki `Path.resolve()`). Znane ograniczenia
**by design**: chroni tylko wpisy top-level root — dziecko chronionego
katalogu (`scripts/close.py`) uznane za bezpieczne; ścieżki poza rootem
zawsze bezpieczne. Probe testuje logikę, **nie** wiring — nadal zero
wywołań (Finding 1). `commit_gate_guard` bez probe: bez wywołacza test
tokenu jest akademicki; w kodzie wymaga tokenu `.commit-approved` o wieku
do 300 s.

## Krok 4 — transkrypty: zero kluczy

```
$ grep -nE 'sk-[a-zA-Z0-9]{20,}|api[_-]?key|Bearer ' handoff/real_case_*.jsonl
(scan exit: 0)  # brak trafień
--- match count: real_case_62b1e12d.jsonl:0 ; real_case_f0c1d6a5.jsonl:0

$ grep -cE 'sk-[a-zA-Z0-9]{10,}|ghp_...|AIza...|xox[baprs]-|AKIA...|-----BEGIN' handoff/real_case_*.jsonl
real_case_62b1e12d.jsonl:0
real_case_f0c1d6a5.jsonl:0
```

Oba wzorce (pack + szerszy) zerowe. Redakcja niepotrzebna, rotacja kluczy nie
jest wymagana. Status gitowy: para `f0c1d6a5` jest **tracked** (już w repo),
para `62b1e12d` jest **untracked** (`??`) — decyzja właściciela, czy commit,
czy dodać do `.gitignore` (nie kasować bez jawnego „usuń").

## Finding 6 — pre-existing: integrity FAIL blokuje każdy commit w root

```
$ python scripts/check_workspace_integrity.py > /tmp/integ.txt 2>&1
REAL EXIT CODE: 1
  - OK — index covers through 2026-10-14 22:03:53; newest on disk 2026-10-14 22:42:27 (lag 0:38:34)
  - knowledge-retrieval/CONTEXT.md Open work still live: headline number in the reference table has no artifact behind it. Re-run the
WORKSPACE INTEGRITY FAIL:
  - memory retrieval eval: 285a62381a82, ses_efbf124ccffeXFQJ12cwT6jIPV, ses_efc212746ffeqWFC2slM110S2c]
PASS agent memory: top-5 [20260921_8, 8ced867d-a735-43c6-88e0-285a62381a82, 20260713_214946_473138, 01a12d8d-c261-7698-a5f4-4a412d7bdc23, 01a0b9f7-6ff5-7000-b8af-0f2e873d6809]
retrieval_eval: hit@5=0.933 MRR=0.622 (14/15)
```

Źródło: `check_workspace_integrity.py:749` — `eval_memory_retrieval.py
--limit 5` zwraca rc≠0 (eval wskazuje na sesje, których nie ma w storze).
To **nie** jest spowodowane guardami ani tą sesją; skutek: `hooks/pre-commit`
blokuje teraz każdy commit w root (także ten raport). Reguła „nie zmieniaj
bramki, żeby commit przeszedł" została uszanowana — gate nieruszony, dane do
naprawy po stronie właściciela/eval fixture'ów.

## Decyzje dla właściciela (krok 6 packa — bez jawnej zgody nic nie podpinam)

1. **Wiring guardów**: dodać do `hooks/pre-commit` wywołania
   `root_deletion_guard.py --check-staged` (wymaga dopisania trybu `--check-staged`
   — dziś guard ma tylko `--selftest`) i/lub `commit_gate_guard.py`, jako
   osobny commit z uzasadnieniem. Alternatywa: jawna konwencja (opcja 2 flagi
   `gate_has_no_automatic_caller`) — kosztem uczciwości słowa „guard".
2. **Untracked para `62b1e12d`**: commit vs `.gitignore` (bez kasowania).
3. **Memory retrieval eval**: kto naprawi dane — bez tego żaden commit w root
   nie przejdzie hooka.

## Tool calls

| Wartosc | Komenda | Surowy output (fragment) |
|---------|---------|--------------------------|
| 144 | `ls handoff/flags/*.md \| wc -l` | `144` |
| 5/5 | claim packa vs `ls`/`find` po guardach | realnie 2 pliki: `root_deletion_guard.py`, `commit_gate_guard.py`; 3 guardy bez kodu |
| 1448 | `ls -la scripts/root_deletion_guard.py` | `1448 Oct 11 18:26 scripts/root_deletion_guard.py` |
| 1211 | `ls -la scripts/commit_gate_guard.py` | `1211 Oct 11 18:26 scripts/commit_gate_guard.py` |
| 927 | `ls -la hooks/pre-commit` | `927 Oct 13 11:38 hooks/pre-commit` |
| 0 | grep `root_deletion_guard\|commit_gate_guard\|commit-approved` po repo (bez .git/node_modules) | zero trafień w kodzie/hooku/config; wszystkie w `handoff/` docs |
| 8145 | `ls -la scripts/verify_report.py` | `8145 Oct 11 18:25 scripts/verify_report.py` |
| 4970 | `ls -la scripts/verify_report_evidence.py` | `4970 Oct 13 11:51 scripts/verify_report_evidence.py` |
| 1061 | `ls -la scripts/verify_report_tests/run_tests.py` | `1061 Oct 11 18:25 run_tests.py` |
| 4/4 | `python scripts/verify_report_tests/run_tests.py` | `4/4 passed` |
| 10/10 | `python scripts/_scratch/probe_root_deletion_guard.py` | `probe summary: 10/10 OK, 0 FAIL` |
| 300 | `scripts/commit_gate_guard.py` (źródło) | `def check_commit_authorized(max_age_seconds: int = 300)` |
| 676151 | `ls -la handoff/real_case_62b1e12d.jsonl` | `676151 Oct 11 18:32 handoff/real_case_62b1e12d.jsonl` |
| 634056 | `ls -la handoff/real_case_f0c1d6a5.jsonl` | `634056 Oct 11 18:16 handoff/real_case_f0c1d6a5.jsonl` |
| 0 | `grep -cE 'sk-...\|api_key\|Bearer'` po obu jsonl | `real_case_62b1e12d.jsonl:0` / `real_case_f0c1d6a5.jsonl:0` |
| 1 | `python scripts/check_workspace_integrity.py; echo $?` | `REAL EXIT CODE: 1` + `WORKSPACE INTEGRITY FAIL: memory retrieval eval` |
| 749 | `grep -n 'memory retrieval eval' scripts/check_workspace_integrity.py` | `749: FAILS.append(f"memory retrieval eval: {message[-300:]}")` |
