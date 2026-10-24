# E6 — `close.py --verify-claims`: OUTPUT

**Verdict:** `--verify-claims` jest wdrożone i gate'owane. Re-derywuje tylko twierdzenia z
wykonywalnym artefaktem (decyzja B3, 2026-10-16). W `--dry-run` FAIL = exit 1, w real close
FAIL = WARN. 4/4 mutacje po żądanej stronie, 14/14 nowych testów zielonych, korpus 168 flag:
0 fałszywych FAIL-ów po guardach.

Kontrakt B3 nadrzędny nad wrapperem: advisory-only z execution-map §7 odrzucony.

---

## 1. Co zaimplementowano w `scripts/close.py` (+202 linie)

| element | rola |
|---|---|
| `CLAIM_COMMIT_RX` | claim `commit <hash>` → rezerwacja: `_commit_repo()` (root, potem repo zagnieżdżone pod `projects/`) |
| `CLAIM_COUNTER_RX` | `<N> <unit>` → `_counter_artifact()` mapuje na `handoff/flags/*.md` albo `brain.db:<tabela>` |
| `CLAIM_EXIT0_RX` + `GATE_NOUN_RX` | claim o gate'cie → `gate_covered`, **nie** re-uruchamiany (płatny drugi integrity run) |
| `ClaimsReport` | `(findings, re_derived, gate_covered)` — NamedTuple, czysty, testowalny |
| `nested_repos()` | `projects/**/.git` — bez tego 14/33 claimów o commitach false-FAILuje |
| `verify_claims()` | re-derywacja + findings; `gate_note()` drukuje stopkę |

Scope w `main()`: `--verify-claims` + `--dry-run` → jakikolwiek FAIL = `fail("verify-claims")`
exit 1. W real close i w samym `dry_run()` → WARN na stdout, nigdy nie blokuje.

## 2. Adversarial case przed runem (S56/S62)

`scripts/_scratch/e6/corpus.py` (gitignored, usunięty przed close — jego logika
przeniesiona do guardów w `verify_claims()` i do `VerifyClaimsTests`) — skan wszystkich
168 flag przez `verify_claims()` przed wpisaniem gate'a w `main()`. Wynik pierwszej wersji:
**5 FALSE FAILs**, z których 3 okazały się fałszywie-dodatnimi. To ten adversarial case,
który uratował gate przed commit — patrz S72.

## 3. Cztery mutacje (B3 + mapa)

Każda: `python.exe scripts/close.py --flag e6-<mut> --model test/model --dry-run --verify-claims --body-file scripts/_scratch/e6/<mut>.md --include scripts/close.py scripts/test_close.py`

```
===== mut1-control (true hash 9f14e85) =====
close.py: verify-claims OK — 1 claim(s) re-derived, none contradicted
close.py: dry-run OK — a real close would proceed to write + commit
EXIT=0

===== mut2-false-hash (deadbeefdeadbeef) =====
close.py FAIL at [verify-claims]: flag body claims something the worktree contradicts (B3: fail-loud in --dry-run):
  FAIL: claim `commit deadbeefdeadbeef` — no such commit in the root repo or any nested projects/ repo
EXIT=1

===== mut3-counter-no-artifact (162 plikow, ASCII) =====
close.py WARNING: counter claim `162 plikow` names no recomputable artifact — not re-derived
close.py: verify-claims OK — 0 claim(s) re-derived, none contradicted
close.py: dry-run OK — a real close would proceed to write + commit
EXIT=0

===== mut4-narrative (+ gate claim) =====
close.py: verify-claims OK — 0 claim(s) re-derived, none contradicted; 1 gate claim(s) enforced by this transaction's own integrity step
close.py: dry-run OK — a real close would proceed to write + commit
EXIT=0
```

Stan po czterech runach — `--dry-run` nic nie zapisuje, więc „restore" = brak zmian:

```
$ git status --porcelain
 M scripts/close.py
 M scripts/test_close.py
```

## 4. Korpus 168 flag po guardach

```
$ python.exe scripts/_scratch/e6/corpus.py
flags scanned: 168
nested repos discovered: 11 ['projects\\_archive\\agentic-research-lab', ...]
re-derived claims: 34 | gate-covered: 7
FALSE FAILs (claim contradicted by artifact): 2
    wayfinder-brain-e7-expect-hash-2026-10-16.md -> FAIL: claim `48 problems` — brain.db:problems holds 50
    workflow-verification-fix-2026-10-13.md -> FAIL: claim `commit fd9cb99` — no such commit in the root repo or any nested projects/ repo
WARN findings (no artifact): 90 across 47 flag(s)
max WARNs on one flag: 9
hash 476b3c7: root-only lookup rc=128 (non-zero = absent in root)
resolved to: C:\Users\Mateusz\Desktop\root_workspace\projects\research\knowledge-retrieval
```

Oba pozostałe FAIL-y to **prawdziwy dryf**, sprawdzony ręcznie: `fd9cb99` nie istnieje w
żadnym z 15 repo workspace (sprawdzone `cat-file -e` w każdym `.git`), a brain.db ma teraz
50 problems, nie 48. Guardy usunęły 3 fałszywie-dodatnie z 5 — patrz §5.

## 5. Trzy mechanizmy fałszywie-dodatnich — naprawione (S72)

| # | claim | mechanizm | guard |
|---|---|---|---|
| 1 | `(9 plików z eval/); untracked … i handoff/flags/` | okno ±90 znaków przelewało się przez granicę zdania | `_clause_around()` — claim scopowany do własnego zdania (`;`, `\n`, kropka przed spacją) |
| 2 | `22 flagi → handoff/flags/<flag>.md` | licznik opisuje *historyczną* zmianę, nie stan | `TRANSITION_RX` (`→`, `was`, `było`, `przed`) → WARN |
| 3 | `root w \`e61d8c8\` (41 plików, +1881/-179)` | licznik diffa commita, nie worktree | `COMMIT_CITE_RX` (hash w klauzuli) → WARN |

Dodatkowo: kropka wewnątrz tokenu (`brain.db`, `SCARS.md`, `close.py`) **nie** jest końcem
zdania — bez tego `baseline bez zmian w \`SCARS.md\` (48 problems)` przestawało być
re-derywowalne, czyli guard #1 najpierw ukrył prawdziwy dryf. Efekt netto: 2 prawdziwe,
0 fałszywych.

Piąty defekt: `dry_run()` liczył WARN-y, ale ich nie drukował — claim bez artefaktu przechodził
po cichu (S56/S62). Naprawione; `mut3` to teraz pokrywa testem.

## 6. Testy

```
$ python.exe scripts/test_close.py
............................
----------------------------------------------------------------------
Ran 28 tests in 2.273s

OK
EXIT=0
```

14 nowych w `VerifyClaimsTests` (3 mutacje B3 + mutacja 4 mapa + guardy + gate + `gate_note` +
`_clause_around`). Fixtures: throwaway repo git + brain.db w tmpdir — nic nie dotyka workspace.

## 7. Bramki

```
$ python.exe scripts/memory/eval_brain.py --check
brain_eval: hit@5=9/10 refusal=3/4 MRR=0.900
known gap — new-root-entry-breaks-integrity: ...
known gap — refuse-risotto: 'risotto alla milanese' shares an accidental token with the corpus.
OK — brain retrieval is at or above the baseline recorded 2026-10-16
EVAL_EXIT=0

$ python.exe scripts/ingest_brain.py --check
  - lessons: 2 row(s) match brain/lessons.md
  - decisions: 23 row(s) match DECISIONS.md
  - problems: 51 row(s) match SCARS.md
OK — brain.db is the parse of the current lessons/decisions/scars sources
INGEST_EXIT=0
```

Baseline `brain_eval.json` **nietknięty** (append S72 nie zmienił hit@5/MRR). Progi żadnej
bramki nie zmienione.

## 8. Blizna

`SCARS.md` S72 (append; `ingest_brain.py` → problems 50 → 51, ID stabilne, `--check` OK).

---

## not checked:

- **Real close z `--verify-claims`** — nie wykonany. Wszystkie 4 mutacje szły `--dry-run`,
  żeby nie kosztować drugiego ~96 s integrity run i nie zaśmiecać historii. Real close
  (WARN-only, bez blokowania) nie jest dowodzone na żywo; ścieżka jest ta sama funkcja,
  inny próg.
- **`check_workspace_integrity.py` po tym commicie** — output w HANDOFF/SESSION-TOKEN, nie
  tutaj (close go uruchamia).
- **Claimy licznikowe poza `handoff/flags/` i `brain.db`** — tylko te dwa artefakty są
  re-derywowalne. Licznik o `docs/reviews/*.md`, `scripts/**` albo `_scratch/` daje WARN.
- **Claimy w flagach spoza `handoff/flags/*.md`** (`handoff/deep/`, notatki projektów) —
  skan korpusu obejmował tylko katalog flag.
- **Regresja na przyszłych flagach** — guardy są wyprowadzone z 168 historycznych flag;
  nowy kształt zdania może dać fałszywie-dodatni, którego tu nie ma.
- **E2–E5, merge brain/+knowledge-retrieval** — poza zakresem ticketu.
