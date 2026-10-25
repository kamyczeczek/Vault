---
type: Concept
flag: handoff_flag_per_file_icm
since: 2026-10-03
owner: opencode
agent: build
model: opencode/space-bunny-free
origin: this session (icm-architect, Restructure mode)
title: handoff_flag_per_file_icm
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`handoff_flag_per_file_icm` — 2026-10-03: handoff roota przebudowany wg `icm-architect` (Restructure mode): 22 flagi → `handoff/flags/<flag>.md` (jedna flaga = jeden plik = jeden writer — własność wynika z flagi, nie z agenta, więc wycofanie cudzej flagi to legalny pojedynczy zapis), 4 sekcje prose → `handoff/deep/`, `HANDOFF.md` jest teraz **generowany** przez `scripts/build_handoff.py` (`--check` = forma gate'a, exit 1 gdy widok stary), kontrakt w `handoff/CONTEXT.md`. Bezpieczna kopia przed migracją: `scripts/_scratch/HANDOFF.pre-migration.md` (sha 66320412b98f736f). Pierwsza próba (per-agent pliki + `HANDOFF.generated.md`) odrzucona i usunięta: trzy domy jednego faktu + zmyślona tożsamość agenta (`agnes-flash` przy modelu `nemotron-3-ultra-free`) + detektor kolizji jako plaster na złe ziarnistość. `scripts/_scratch/` dostał ignor w `.gitignore` (dwa deklarowane helpery zostają tracked) — wcześniej debris z `_scratch` wracał do `git status` i karmił root-gate. Next: commit rota bierze `handoff/`, `scripts/build_handoff.py`, `scripts/test_build_handoff.py` (13/13), `.gitignore`, `AGENTS.md`, `CLAUDE.md`, `scripts/check_workspace_integrity.py`.