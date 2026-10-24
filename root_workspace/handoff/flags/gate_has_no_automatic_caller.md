---
flag: gate_has_no_automatic_caller
since: 2026-10-03
owner: opencode
agent: review
model: opencode/space-bunny-free
origin: external review ses_efc8b83bbffeWpNlA3N0EGHv3s (F2) + own verification
---
`gate_has_no_automatic_caller` — 2026-10-03: **potwierdzone, nie domknięte.** Root gate
ma dwa hard checki, których nikt nie musi uruchomić. Verified, nie zgadnięte:
`.git/hooks/` zawiera wyłącznie `*.sample` (brak `pre-commit`), `git config
--get core.hooksPath` puste, brak `.github/`, `ci/`, `.gitlab-ci.yml`. Jedyne
wzmianki `check_workspace_integrity.py` w repo to proza: `AGENTS.md:53` („Gate
before done"), `handoff/CONTEXT.md:47` (krok 5), `CONTEXT-MAP.md:163`. To
konwencja, nie automatyzacja — a `CLAUDE.md` twierdziło „Runs as gate Q0 on every
commit", co było **fałszywym twierdzeniem w katalogu**; poprawione na „by
convention, not by a hook" z odesłaniem do tej flagi.

Dlaczego to nie jest kosmetyka: R12 (handoff staleness) i R13 (citation +
baseline) zostały uzasadnione słowami „jedynym czytającym jest następna zimna
sesja" i „to jest błąd, który ten workspace ciągle rediscoveruje w prozie". Oba
argumenty zakładają, że check jest uruchamiany. Bez hooka pre-commit check jest
`refuses correctly but nothing calls it` — dokładnie zarzut, który review
postawił `restamp_provenance.py`, przeniesiony o poziom wyżej, w commit, który
ten zarzut właśnie naprawiał.

Decyzja właściciela (dwie opcje, obie po jednej komendzie):
(1) **hook** — `hooks/pre-commit` w repo + `git config core.hooksPath hooks`
(wymaga zgody na zmianę git config; hook musi być portable przez `sh`, który
dostarcza Git-for-Windows, i nie może dublować `pytest` jako obowiązkowego
kroku); albo (2) **konwencja, jawnie** — zostawić jak jest, ale wtedy R12/R13
są *detekcją*, nie *egzekwacją*, i ich commit messages powinny to mówić. Opcja (2)
kosztuje uczciwość, opcja (1) kosztuje jedną komendę i hook do utrzymania.

Nie zainstalowałem hooka sam: `core.hooksPath` to zmiana konfiguracji git, a to
nie moja decyzja. Next: właściciel wybiera (1) albo (2).