---
type: Concept
title: trace
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# trace.md — Faza 6, Q-refusal (executed 2026-10-10, agent pi)

Oracle-first: oczekiwanie zapisane w plan.json PRZED pierwszym query na graph.db.
Baza otwierana wyłącznie read-only (uri mode=ro). Żaden plik nie modyfikowany.

## Krok 0 — pytanie + SCOPE (nazwane wprost)
"Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?"
Oczekiwanie: ODMOWA z uzasadnieniem braku pokrycia.
SCOPE: to NIE jest pilot. `graphrag.py` ma zaszyty mini-graf (D-002) i nie
brał udziału w tym teście. Testowany jest ARL retriever (`ask.py` na archiwum
`graph.db`, read-only). Udowodnione zdanie brzmi: 'ARL retriever poprawnie
odmawia na pytaniu o fakty workspace\'u', nie 'pilot działa na archiwum'.
Faza 6 w CONTRACT.md mówi 'uruchom pilot na archiwum' — ten krok jest nadal
przed nami; ten dowód to jego przesłanka (warstwa dowodowa nad rankingiem).

## Krok 1 — seed FTS (ask.py, limit 5)
Top-1: `reflection_rule_of_scars` ("Reflection: The Rule of Scars in Agentic Workflow").
Top-2..5: keyword-matche (Cerebras, Dex Horthy, ICM_knowledge) — szum FTS.
UWAGA: top-1 to dokument tematycznie adjacent (Rule of Scars), ale to streszczenie
literatury (Liu 2026, arXiv:2607.11226), nie fakt o workspace.

## Krok 2 — kontrola pozytywna (narzędzie żywe?)
Q1 z VERA (trust tiers): `ask.py` top-3 zawiera seed 00_okf_methodology_research.
Narzędzie żyje — pustka w Q-refusal to brak odpowiedzi, nie martwy retriever.
Dodatkowo: top-1 Q1 to `02_the_five_level_verification_ladder` — dokładnie distractor
z QUESTIONS.md. Surowy FTS stawia adjacent-but-wrong na top-1 w obu pytaniach.

## Krok 3 — warstwa węzłów (resolve na nodes)
- resolve('scar') → 1 hit: reflection_rule_of_scars (literatura, jw.)
- resolve('R13') → 0 hits. resolve('CRLF') → 0 hits.
- Body reflection_rule_of_scars (10 347 znaków): R13/CRLF/SCARS.md/Where to go/
  AGENTS.md/sesja 04 — po 0 trafień każde.
- FTS direct '"SCARS.md"' → 0 dokumentów.

## Krok 4 — charakter korpusu (czy graf ma fakty o workspace?)
Top sources: podręczniki (Russell&Norvig 1123, Norvig Lisp 828, Bishop 736...).
source_family ze słowami workspace/session/handoff/scar: 7 rodzin, wszystkie to
dokumenty o architekturze workspace'u jako TEMACIE badawczym (reflection,
session_compaction, workspace_rapid_understanding) — nie fakty o sesjach tego
workspace'u. Żadna nie zawiera wpisu R13 z linii 20 root SCARS.md.

## Krok 5 — martwy precedens (finding, nie naprawa)
`research-engine/kg.py` → FileNotFoundError: szuka bazy pod
`projects/research/agentic-research-lab/...` (nie istnieje); żywe archiwum jest w
`projects/_archive/`. Precedens "istnieje kg.py" (findings.md:14,61) fałszywy co do
używalności. Nie naprawiam: obcy projekt, jeden projekt na sesję.

## Krok 6 — odmowa (uzasadniona)
Brak pokrycia twierdzeń dowodami na każdym poziomie: 0 węzłów R13/CRLF,
0 dokumentów SCARS.md w FTS, top-1 FTS to literatura bez treści odpowiedzi.
Surowa odpowiedź FTS zamiast odmowy = FAIL per CONTRACT.md (halucynacja/wyciek).
