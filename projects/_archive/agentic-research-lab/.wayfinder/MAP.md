# Wayfinder map — decision-brief hypothesis D

## Destination

Udowodnij, że brief ugruntowany w grafie (precedensy z ADR-ów, scars, wzorce) poprawia jakość decyzji architektonicznych słabego modelu, w ramach istniejącego workflow `improve-codebase-architecture`.

## Notes

- Domain: ARL jako laboratoryjny projekt do badań nad agentic research
- Skills to load per ticket: `improve-codebase-architecture`, `grill-with-docs`, `icm-architect`
- Standing constraint: kod testowy tylko w `scripts/_scratch/decision_support/`, nie w main runnerze
- Ground truth: 5 historycznych ADR-ów ARL jako retrospektywny zbiór testowy
- Graf: FTS5 w `knowledge/graph/`, jedna warstwa, bez budowy nowego silnika

## Decisions so far

(none yet)

## Not yet specified

- Jak klasyfikować "architektoniczny precedens" w grafie (tagi? typy węzłów?)
- Jak mierzyć "jakość decyzji architektonicznej" (odległość od ground truth, LLM-judge, ekspert?)
- Ile historycznych ADR-ów w retrospektywie (n=5? n=10?)
- Które ADR-y włączyć do testu (wszystkie czy filtr po typie?)
- Kiedy promować do TRANSFER.md (próg poprawy?)

## Out of scope

- Budowa nowego silnika grafu / migracja poza FTS5
- Ralph-loop jako testowy workflow (używamy improve-codebase-architecture)
- Eksperymenty na żywych modelach przed dowodem retrospektywnym
- Promocja wzorca do TRANSFER.md bez dowodu
