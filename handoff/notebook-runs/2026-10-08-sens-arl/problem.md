---
type: Concept
title: problem
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Problem: sens projektu agentic_research_lab

## Kontekst
Projekt agentic-research-lab (ARL, grade: active) bada "how to perform agentic research well" —
metodologia ICM: zweryfikowany korpus markdown -> graf FTS5 -> refleksja -> meta-learning workflow.
Stan faktyczny (pack L2 + 5 sesji w notebooku root_workspace):
- Phase 1 domknięta: 3 sondy literaturowe + 8 seedów arXiv, synteza, rebuild grafu (10k nodes / 13k edges).
- Phase 2 ablation (agent z grafem vs bez, n=9): wynik pilota ON 9/9 vs OFF 0/9 okazał się
  tautologiczny (kryterium "solved" wymagało znajomości chunk-ID); sesja B wprowadziła
  kryterium treści (25 faktów, echo-guard) z werdyktem INCONCLUSIVE (ON macro 0.380 vs OFF 0.222,
  ON wygrywa tylko 1/3 rodzin).
- Phase 2b (Goose x graf-MCP) domknięta jako wynik negatywno-infrastrukturalny:
  MCP nietestowalne (config inert + deadlock na --with-extension); autonomia szła kanałem shell.
- Forge A/B (15/ramię, łatwe zadanie): brak liftu (OFF 14/15, ON 14/15) — baseline już ~93%.

## Decyzje do podjęcia
1. Czy projekt ma sens kontynuacji — tak / nie / w jakiej zawężonej formie?
2. Który workstream ma największy oczekiwany zysk: (a) extended-n rerun hipotezy B
   (n>=25 par + szerszy budżet kontekstu 2500->8000 char), (b) Phase 4-diversity
   (enforcement różnorodności cytowań), (c) phase2c (shell-injection jako kanał autonomii),
   (d) zamknięcie/adnotacja jako research-prototype?
3. Co jest dziś najsłabszym ogniwem metodologicznym (kryterium, moc statystyczna,
   budżet kontekstu, kanał tool-use)?

## Ograniczenia
- Odpowiedź po polsku, konkretnie, z cytowaniami źródeł z notebooka.
- Uczciwie: odróżnij wynik negatywny od braku wyniku; n=9 pilot to nie powered trial.
- Jeden następny krok ma być tani (<1 sesji) i falsyfikowalny.
