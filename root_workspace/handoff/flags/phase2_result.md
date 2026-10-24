---
flag: phase2_result
since: 2026-10-04
owner: mateusz
agent: opencode
model: muse-spark
---

2026-10-04: Phase 2 ablation wynik (ARL `d6ca9b2`, 9 zadań x 2 ramiona,
model `gemini/gemini-flash-lite-latest`, seed 20261004):

**Wynik:** ON 9/9 solved, OFF 0/9 solved. Resolve rate ON 1.0 (6 zadań
eligible ≥3 cytowania) vs OFF null (9/9 wykluczonych — zero cytowań).
Concentration ON 0.82 vs OFF null. Dead-route rate ON 0.0.

**Werdykt vs flaga `phase2_hypothesis`:** kryterium sukcesu spełnione na
3/3 rodzinach (każda 3/0 dla ON); żaden warunek porażki nie zaszedł
(brak poprawy-tylko-dead-route; ON cytuje WIĘCEJ — 22 vs 0, więc to nie
unikanie). Ściśle: OFF nie ma mierzalnego resolve rate (total citation
avoidance), więc "wygrana na resolve rate" to forma mocna — ON 1.0 przy
pełnym cytowaniu vs OFF niemierzalny przy zerowym.

**Caveats (uczciwe):** N=9, jeden run na zadanie-ramię, jeden model —
skala pilota, nie powered trial (por. forge n=15/ramię). Leczenie to
wstrzyknięty kontekst (nie tool-use agenta) — mierzy "retrieval rozszerza
osąd", nie autonomiczne sięganie po graf. Concentration 0.82 wciąż wysokie
(oracle to top-hity — metryka działa zgodnie z designem).

**Incydent w locie:** pierwszy full run padł w 9/18 przez `KeyError:
'context'` (placeholder w system prompt bez prompt_vars) — naprawione,
rerun na tym samym seedzie (to samo mapowanie A/B).

**Ograniczenie kryterium (dopisane po review 2026-10-04):** kryterium
"solved" (≥1 oracle cite + wszystkie resolvują) jest tautologiczne względem
ramienia — OFF nie zna ID chunków, więc nie może zdać z definicji, niezależnie
od merytorycznej jakości odpowiedzi. Wynik ON 9/9 vs OFF 0/9 mierzy pipeline
(kontekst dociera, model cytuje, brak halucynacji ID, dead-route 0.0), NIE
mierzy hipotezy B (grounding → lepsze decyzje). Test hipotezy wymaga kryterium,
które OFF może zdać: deterministyczne dopasowanie TREŚCI odpowiedzi do
kluczowych faktów oracle chunka (nie do jego ID).

Next: sesja B — non-tautologiczne kryterium treści (regex/fakt-check na
kluczowych twierdzeniach oracle chunka), rerun na tych samych 9 zadaniach.
Dopiero wtedy design doc `docs/research/kg-icm-integration.md` dostaje wynik
o hipotezie; obecny wynik to pilot infrastrukturalny.
