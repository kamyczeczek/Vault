---
type: Concept
title: preregistration-v2
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Pre-registration v2 — answer-layer pilot sesja 3 (2026-10-18, przed pierwszym spawnem)

Zamrożone przed spawn #1 (S56). Po zobaczeniu wyników nie zmienia się lista terminów, progi, reguła dopasowania (S62). Jeśli metryka okaże się wadliwa — to jest wynik, nie problem do naprawy w tej sesji.

## Wejście
- Dump: Tier 3 `retrieve` (RRF top-8, bez rerankera), timing zatwierdzony: p50=90.9 ms, p95=105.2 ms, total 2.6 s — dump na produkcji, nie Tier 4.
- Próbka: 15 answerable q001–q015 (deterministycznie pierwsze 15) + 8 unanswerable u001–u008 + 1 canary.
- Interpreter: `C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (Python 3.11.15) — ten sam do dumpa i do gradera.

## Input-stage check (z dumpa)
q014 miss (gold topic 45 poza top-8; top-8 = [27,11,9,52,4,49,8,20]) — pozostałe 14 answerable hit. Jak w sesji 1. q014 nie spawnowany, osobna kategoria, nie liczy się do progu.

## Reguła dopasowania (strict, zamrożona)
norm(term) in norm(answer), gdzie norm = NFKD + lowercase. Zero semantic mapy, zero synonimów, zero rozszerzeń. Stemy polskie z reference_answer. Odpowiedź refusal („BRAK W KSIĄŻCE") na answerable = fail answerable (i kategoria opisowa: answer-layer failure, jeśli top-8 zawierał gold topic).

## Progi (jak sesja 2)
- answerable: ≥10/14 z wszystkimi wymaganymi terminami.
- unanswerable: refusal ≥6/8 z markerem dokładnie `BRAK W KSIĄŻCE`.
- canary (q001 pytanie + chunki q003): refusal. Odpowiedź z pamięci = ostrzeżenie o kontaminacji.

## Termy wymagane (14 z gold chunkiem)

| qid | stemy (rdzenie, odmiana zawiera) |
|---|---|
| q001 | wiedz, intenc, duplikac, reprezentac |
| q002 | szkielet, prototyp, wyrzuc, tracer |
| q003 | coupling, delegow, mixin, interfejs |
| q004 | warto, zasad, zmian |
| q005 | napraw, zaraz |
| q006 | precond, postcond, caller, invariant |
| q007 | obserwat, pub, reaktywn, automata |
| q008 | martw, uszkod, supervisor |
| q009 | asercj, testow, zostaw |
| q010 | duplikac, ortogonal, współzależ, zmian |
| q011 | binarn, połow, zawęż |
| q012 | aktor, blackboard, wiadomost |
| q013 | przypadk, świadom, szczęści |
| q015 | kontrol, test, automatyz |

(q014: brak — input-stage miss. u001–u008: brak termów progu — refusal.)

## Zasady spawnu (reuse sesji 2)
Jeden spawn = jedno pytanie; podagent nie widzi metryk/terminów/historii; brief samowystarczalny; chunki verbatim top-8 z Tier 3 z nagłówkami „Topic N"; model `opencode/glm-5.3-flash-free` (config .opencode/agents/answerpilot.md, asset sesji 2).
