# Gates: transfer-lab

GATES: listed below

OWNS: projects/research/agentic-research-lab/.ralph/runs/2026-10-08_transfer-lab/, projects/research/agentic-research-lab/TRANSFER.md

Scope: ARL jako laboratorium przenośnych rozwiązań workspace; zamrożenie badań B poza tanim testem perf; promocja 4 wzorców do roota

- [x] G1: Test perf 8000 wykonany, wynik zapisany w LEARNINGS.md
  CHECK: scripts/_scratch/run_perf_8k.py → scripts/_scratch/perf_8k/verdict.json
  EXPECT: Iteracja 1A odnotowana z wynikiem perf ON 8000
  EVIDENCE: 2026-10-08 perf ON 8000 avg = 0.0 vs baseline 0.083 (3 zadania: perf-ppr 0.0, perf-costinversion 0.0, perf-queryexpand 0.0); verdict.json zapisany

- [x] G2: TRANSFER.md istnieje, ma 4 wiersze i uzupełnionych ownerów
  CHECK: test -f projects/research/agentic-research-lab/TRANSFER.md
  EXPECT: Plik istnieje i zawiera 4 wiersze tabeli
  EVIDENCE: TRANSFER.md istnieje, 4 wiersze, ownerzy: opencode (ICM, gate'y mutacyjne, D5/ADR-0003), mateusz (regex + echo-guard)

<!-- Keep every gate honest. Do not remove an impossible gate; use ABANDON with a reason and handoff.
     Declaring `GATES: none` also means deleting every placeholder checkbox above, or the controller will count them as unmet. -->
