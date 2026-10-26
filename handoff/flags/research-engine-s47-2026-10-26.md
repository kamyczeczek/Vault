---
type: Concept
flag: research-engine-s47-2026-10-26
since: 2026-10-26
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: research-engine-s47-2026-10-26
generated: { by: okf-enforcer/0.6, at: 2026-10-26T20:56:15Z }
---

`research-engine-s47-2026-10-26` — 2026-10-26: zagnieżdżone repo `research-engine` jest domknięte (dwa commity: 0b08562, 70ce0eb; drzewo czyste). Q9 rozstrzygnięte regułą zapisaną **przed** odczytem liczb: obie polityki okna (stałe 2000 vs expanding) muszą dać tego samego kandydata i te same bramki. Dały — wybór B, te same rangi, 4/6 zwycięstw, 0/6 zmian zwycięzcy na zadaniach — więc stałe 2000 zostaje protokołem, a expanding jest zapisanym testem wrażliwości (`results_s47_expanding.json`, `compare_window_policies.py` → exit 0). Q10: pięć originów W=5 jest spalone dla potwierdzenia, `all_binding=false`, nic nie awansuje. Q11: 26.7 s fixed / 26.2 s expanding, poniżej `<5 min`. `results_s47.json` w HEAD nie mówi już `PROMOTE` — werdykt jest diagnostyczny. Testy 12/12.
Next: protokół FEV w `benchmark-core` — patrz `benchmark-core-fev-honest-2026-10-26`. S-47 zostaje sondą.
not checked: nie ruszano `benchmark-core` w tym commicie; stan `bench.py --fev` opisuje flaga `benchmark-core-fev-honest-2026-10-26`.
