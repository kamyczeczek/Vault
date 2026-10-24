---
flag: session-discipline-hardening
since: 2026-10-11
owner: mateusz
agent: opencode
model: opencode/muse-spark
origin: session-close
---

`session-discipline-hardening` — 2026-10-11: korekta po ocenie sesji naprawczej. Wycofano duplikat discipline z AGENTS.md (kaskada R13, v9 usunięty, v8 przywrócony); R18 zmiękczony (WARN >3d, FAIL >14d); R19 dopisany wg specyfikacji (flag-without-commit: git log --since vs temat flagi); APPEND_SYSTEM.md uzupełniony (zakaz inline -c, jedno miejsce na fakt, AGENTS.md/R13, backup); S54 i session-decision sprostowane. Bramy: diff --check czysty, build_handoff --check OK (85 flag), audit_agents_md --check OK, integrity gate OK (R19 WARN na flagach z poprzednich sesji).
not checked: cudze pliki untracked (ask-user-question-fixed, real_case_*, state_description/) — nie moje, nietknięte; kalibracja progu cosine D-2026-10-11-01 (sesja projektowa).
