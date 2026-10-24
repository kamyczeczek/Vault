# Problem: weryfikacja retrievalu root corpus przez NotebookLM (wariant A)

## Kontekst
Notebook `root_workspace` (a49ff8cb-31e0-470e-b747-3f2a0ded1699) zawiera pack root L1 (2026-10-10) + 5 sesji. To NIE jest korpus ARL (papers: SEVerA) — to root corpus (sesje, decyzje, handoff). Pytanie dotyczy wyłącznie root corpus.

## Pytanie Q-root (oracle-first, oczekiwanie z flag handoff, nie z notebooka)
Co ustaliła sesja 2026-10-08 o sens projektu agentic-research-lab? Podaj: (1) werdykt kontynuacji, (2) ranking workstreamów a/b/c/d, (3) najsłabsze ogniwo metodologiczne.

Oczekiwanie (z flag `arl-sens-verdict` / `arl-gate-a-result`, zweryfikowane bez otwierania notebooka):
- Werdykt: TAK, tylko jako warunkowy eksperyment weryfikacyjny, zamrozić rozbudowę.
- Ranking: (a) extended-n rerun NAJWYŻSZY > (d) archiwizacja > (b) diversity niski > (c) phase2c najniższy.
- Najsłabsze ogniwo: budżet kontekstu 2500 znaków (perf ON 0.083 = truncation artifact) + moc n=9.

## Kryterium
- PASS: odpowiedź zgodna z oczekiwaniem + cytaty ze źródeł notebooka (pack/sesje). Każde z 3 twierdzeń ma pokrycie.
- FAIL: brak cytatów, sprzeczny ranking, lub odpowiedź o SEVerA/papers (zły korpus) zamiast o sens ARL.
- Odpowiedź po polsku, z numerami cytowań (zachować).

## Ograniczenia
- Nie pytamy o ARL graph (SEVerA, entropy-001) — tego korpusu notebook nie ma.
- To test retrievalu root corpus, nie test grafu ARL.
