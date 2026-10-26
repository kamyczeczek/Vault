---
flag: research-engine-s47-2026-10-26
since: 2026-10-26
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`research-engine-s47-2026-10-26` — 2026-10-26: zagnieżdżone repo `research-engine` jest domknięte (dwa commity: 0b08562, 70ce0eb; drzewo czyste). Q9 rozstrzygnięte regułą zapisaną **przed** odczytem liczb: obie polityki okna (stałe 2000 vs expanding) muszą dać tego samego kandydata i te same bramki. Dały — wybór B, te same rangi, 4/6 zwycięstw, 0/6 zmian zwycięzcy na zadaniach — więc stałe 2000 zostaje protokołem, a expanding jest zapisanym testem wrażliwości (`results_s47_expanding.json`, `compare_window_policies.py` → exit 0). Q10: pięć originów W=5 jest spalone dla potwierdzenia, `all_binding=false`, nic nie awansuje. Q11: 26.7 s fixed / 26.2 s expanding, poniżej `<5 min`. `results_s47.json` w HEAD nie mówi już `PROMOTE` — werdykt jest diagnostyczny. Testy 12/12.
Next: świeża, nieujawniona ewaluacja w `benchmark-core` na niewidzianych realnych zadaniach (FEV) — tylko ona może cokolwiek promować; S-47 zostaje sondą.
not checked: nie ruszano `benchmark-core`; `bench.py --fev` nadal ma martwe URL-e i cichy fallback do synthetic, a `main_fev()` dopasowuje raz na pierwszym oknie i ignoruje multivariate.
