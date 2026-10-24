---
flag: governance-ontology-prototype-2026-10-15
since: 2026-10-15
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`governance-ontology-prototype-2026-10-15` — 2026-10-15: Prototyp ontologii governance w `tools/out/governance-ontology.db` został sfalsyfikowany. Werdykt: STOP.

Nie rozszerzać na R1–R16. Werdykt STOP jest ostateczny dla tego kierunku; powrót tylko z nowym argumentem, dlaczego tym razem miałoby zadziałać.
Różnorodne typy reguł (strukturalna R1, tekstowa R13, czasowo-stanowa R14) nie posiadają jednego, wspólnego zestawu predykatów.
Selftest był tautologiczny: sprawdzał, że w outpucie są stringi, które sam wpisał, zamiast że traversal SQL działa.
Niespójność: kwerenda zwróciła `R14` i `R16`, a raport wymieniał `R1`, `R13`, `R14` — dwa różne zestawy wymieszane.

not checked:
- R1-R16 (poza zakresem po werdycie STOP)
