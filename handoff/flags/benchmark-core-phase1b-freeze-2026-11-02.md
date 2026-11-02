---
flag: benchmark-core-phase1b-freeze-2026-11-02
since: 2026-11-02
owner: mateusz
agent: opencode
model: omniroute/agy/claude-opus-4-6-thinking
---

`benchmark-core-phase1b-freeze-2026-11-02` — 2026-11-02: Phase 1 + 1b of the v2
multi-domain generalization protocol is complete and frozen.

Stan:
- **PROTOCOL.md** (304 linie, §0–§15): normatywny dokument v2 zamrożony. Hierarchia
  normatywna (Protokół > Proces > Raport), 3 bramki decyzyjne, populacja N≤8,
  budżet czasu 20 min/metoda, lockbox 42 zadań z limitem 3 użyć, reguły STOP,
  audyt niezależny w §9, rejestr poprawek A1–A4.
- **Manifest zamrożony** (`manifest_sha256 = 34b35abc…b42da`): 20 Dev / 38 kwarantanna /
  42 Lockbox = 100 zadań pełnego zbioru fev-bench. Twarde odcięcie rodzeństwa (15 rodzin
  Dev ∩ Lockbox = ∅, ETT ∉ Lockbox). Lockbox pokrywa 5 z 7 domen (brak cloud, nature).
  247 kolumn targetu × 3 okna = 741 jednostek; 2767 serii, 8301 ewaluacji item × okno.
- **Ledger** (`ledger.jsonl`): Genesis + A1–A4, łańcuch SHA-256 integralny (audit_v2 CLEAN).
- **Moduły bazowe**: `manifest.py` (klasyfikacja rodzin/domen, odcięcie rodzeństwa,
  3 ostatnie okna), `metrics.py` (MASE, clipping [0.01,100], skill score),
  `bootstrap.py` (klaster po 15 rodzinach B=10000, iid, stratyfikowany),
  `ledger.py` (append-only kanoniczny JSON, SHA-256 chain), `guards.py` (Gate 1–3,
  populacja, STOP), `audit_v2.py` (niezależny audyt proceduralny §9).
- **Skan mianowników MASE** (`scan_denominator_anomalies.py`): 20/20 zadań, 0 itemów
  z zerowym błędem sezonowym → brak wykluczeń w manifeście.
- **Testy**: 11 passed (`test_benchmark_v2.py`), czas <4s.
- **Poprawki docs**: CLAUDE.md (9 nowych wpisów w tabelach Where/Route), CONTEXT.md
  (bench.py --fev RESOLVED), MAP.md (10 nowych modułów w mapie).
- Dwie wycofane flagi: `benchmark-core-fev-honest-2026-10-26` (zastąpiona pełną fazą 1b),
  `benchmark-core-full-tests-2026-10-29` (zastąpiona bieżącą fazą).
- Wszystkie punkty z recenzji planu v2 wprowadzone: r=100 dla timeoutów (§6), kontrast
  vs Champion (§4 Bramka 2/3), §9 „ma zakaz", MDE w Fazie 1b (§14), Amendment A2,
  „46 konfiguracji" → 42 zadania (A1).

Weryfikacja:
- `python audit_v2.py` → verdict: CLEAN (0 hard findings), chain intact, partition 100.
- `pytest test_benchmark_v2.py` → 11 passed in 3.13s.
- `python scripts/check_workspace_integrity.py` → OK (36 declared entries, 7 projects).
- `git diff --check` → exit 0.

not checked: mapowanie domen vs papier fev-bench (Appendix E/Tabela 15) — weryfikacja
manualna; pełen suchy przebieg SNaive/NLinear/DLinear na Dewie (Faza 1b checklist §14);
analiza mocy i MDE; budżet ściany Lockboxa; `s44_calib_insample_failed.log` nie został
skopiowany z $env:TEMP do etth1-h720/results/ (plik istnieje, 4520B, nie jest w repozytorium).

Next step: suchy przebieg Seasonal Naive + NLinear + DLinear na 20 zadaniach Dev (3 okna
każde), pomiar czasu i wyznaczenie MDE. To otwiera Fazę 2 (populacja startowa, dashboard).
