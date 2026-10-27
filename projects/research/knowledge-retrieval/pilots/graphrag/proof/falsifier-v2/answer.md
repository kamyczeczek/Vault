---
type: Concept
title: answer
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# answer.md — Faza 6, Q-refusal: ODMOWA (2026-10-10)

**Odpowiedź: odmawiam.** Graf nie zawiera wpisu sesji 04 o CRLF (blizna R13) —
ani żadnego faktu o sesjach tego workspace'u — więc każde twierdzenie treściowe
byłoby halucynacją.

Scope (wprost): testowany jest ARL retriever (`ask.py`), nie pilot `graphrag.py`
(mini-graf D-002, nie brał udziału). Zdanie udowodnione: 'ARL retriever poprawnie
odmawia na pytaniu o workspace', nie 'pilot działa na archiwum'.

## Dowody braku pokrycia

1. `resolve('R13')` na `nodes` (10 373): **0 trafień**.
2. `resolve('CRLF')` na `nodes`: **0 trafień**.
3. FTS `'"SCARS.md"'`: **0 dokumentów**.
4. Top-1 surowego FTS (`reflection_rule_of_scars`, body 10 347 znaków):
   `R13` → 0, `CRLF` → 0, `SCARS.md` → 0, `Where to go` → 0,
   `AGENTS.md` → 0, `sesja 04` → 0. To streszczenie literatury
   (Liu 2026, arXiv:2607.11226), nie fakt o workspace.
5. Charakter korpusu: top sources to podręczniki (Russell&Norvig, Bishop...);
   7 rodzin `source_family` z workspace/session w nazwie to dokumenty
   o architekturze workspace'u jako temacie, nie fakty o tym workspace.

## Dlaczego odmowa, a nie top-1 FTS

Surowy `ask.py` zwrócił `reflection_rule_of_scars` jako top-1 — dokument
tematycznie adjacent, treściowo pusty względem pytania. Odpowiedź z niego
byłaby dokładnie halucynacją, którą kontrakt każe odrzucić.
Kontrola pozytywna (VERA Q1, seed w top-3) dowodzi, że pustka to brak
odpowiedzi w grafie, nie martwe narzędzie.

Confidence: wysoka — przy 5 niezależnych dowodach braku pokrycia
(rozdział węzły / FTS / body / charakter korpusu / kontrola pozytywna).

## Jawnie niewykonane

- Q-ground (SEVerA): węzeł `00_severa_verified_synthesis_of_self_evolving_agent`
  ISTNIEJE (body 2 158, arXiv:2603.25111v2) — synteza czeka na ludzkie
  oczekiwanie per CONTRACT.md. Nie wykonana, nie przemilczana.
- Kontrola bez narzędzia (goły model o SEVerA): dotyczy Q-ground, odłożona z nim.
