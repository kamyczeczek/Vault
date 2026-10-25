---
type: Concept
flag: root_committed_931aac5
since: 2026-10-03
owner: opencode
agent: build
model: opencode/space-bunny-free
origin: this session (continuing report_citation_unverified)
title: root_committed_931aac5
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`root_committed_931aac5` — 2026-10-03: root w `931aac5` (5 commity: `9a8e105`
`8282dd1` `19253e4` `a15ebf4` `931aac5`) — domknięty wątek „review quoting numbers
it does not own". `scripts/audit_agents_md.py` (`9a8e105`, now with
`scripts/test_audit_agents_md.py`, 26 testów hermetycznych) + `--report-check` /
`--write-block` i raport v7 w repo (`8282dd1`, `docs/reviews/` zadeklarowane w
`CLAUDE.md` + `ALLOWED_ROOT`) + **R12** handoff staleness i **R13** citation +
baseline (`19253e4`, `a15ebf4`, `931aac5`). Gate zielony, `pytest scripts/` 54/54,
`git diff --cached --check` czyste.

Trzy rzeczy, których ta sesja nauczyła się na drodze (koszt: pół godziny, wszystkie
z klasy „skonfigurowany check nie jest sprawdzonym checkiem"):
(1) **Nowy gate = własny commit z własnym uzasadnieniem.** `--report-check` nie
poszedł w commit, który go wprowadzał; R12, R13 i poprawka R13 mają osobne commity.
(2) **Skonfigurowany check, który sam potrzebuje wyjścia na zewnątrz.** Pierwsze
R13 egzekwowało baseline `AGENTS.md` tylko jako efekt uboczny `--report-check` —
usunięcie raportów wyłączałoby guard, zostawiając tylko WARN. Zweryfikowane
probe'ami: pusty `docs/reviews/` → rc=0 (WARN), dodana linia w `AGENTS.md` → rc=1,
`git checkout -- AGENTS.md` → rc=0 i czyste drzewo.
(3) **Whitespace: lepiej naprawić źródło niż-exemptować gate.** Wygenerowany blok
niósł spacje końcowe na pustych liniach (`  . :56`), więc `git diff --check` (rc=2)
blokował commit — i to jest *surowe wyjście gate'a w pliku, który trafi do repo*.
Naprawione w `render()` (`rstrip`) + `--write-block` pisze `newline="\n"` (LF per
`.gitattributes`), zamiast dodawać wyjątek.

Poza paczką: `scripts/agent_sessions.py` (praca innego agenta, w locie —
nieodejmowana, celowo nie-staged). Otwarte decyzje właściciela: `pytest.ini`
(`testpaths = scripts`), katalog `library/` (27 MB nietrackowany, candidate 1
raportu), forge-ab stage 1 (50 runów), D-005 (model/budżet).