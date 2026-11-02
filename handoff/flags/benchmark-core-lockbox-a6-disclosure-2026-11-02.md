---
flag: benchmark-core-lockbox-a6-disclosure-2026-11-02
since: 2026-11-02
owner: mateusz
agent: opencode
model: omniroute/agy/claude-opus-4-6-thinking
---

`benchmark-core-lockbox-a6-disclosure-2026-11-02` — 2026-11-02: A6 ujawnia
skażenie Lockboxa (36/42 zadań) i unieważnia możliwość przesegregowania.

Stan:
- **A5 kłamało w punkcie (ii)**: twierdziło, że nie da się ustalić, co policzył
  przerwany legacy przebieg `--fev-full` z 2026-10-30. Da się — log przeżył
  w `%TEMP%/fev-full.log` (959 linii, zapis 00:26–01:50), z nagłówkami
  `-- task N/100` do pozycji 74. Przebieg policzył 73 zadania w całości
  i zadanie 74 częściowo.
- **Skala skażenia**: po `task_id` z `results/manifest.json` (indeks == pozycja−1)
  to **36 z 42 zadań Lockboxa**, 17 z 21 rodzin, wszystkie 5 domen. Skażone
  indeksy: 7–9, 17–30, 35–37, 40–42, 45–49, 56, 62, 63, 65–69.
  Nietknięte: `task_id` 76, 92, 93, 94, 95, 99 (4 rodziny: `ecdc_ili`,
  `fred_md`, `fred_qd`, `gvar`; 2 domeny: econ, healthcare).
- **Przesegregowanie jest niewykonalne** i nie zostało wykonane: `verify_manifest`
  wymaga, by kwarantanna zawierała wyłącznie rodzeństwo rodzin Dev, a Lockbox
  wyłącznie rodziny nie-Dev (plus zakaz ETT). Skażone zadanie Lockboxa nie może
  więc trafić do kwarantanny, a w kwarantannie nie ma czym uzupełnić Lockboxa.
  Próba obejścia tego wymagałaby zmiany niezmiennika, nie danych — dlatego STOP.
- **A6 w ledgerze** (7 wpisów, łańcuch SHA-256 zweryfikowany, manifest
  `34b35abc…b42da` bez zmian) + wiersz A6 w rejestrze §15 `PROTOCOL.md`
  i akapit o zakazie używania Lockboxa do czasu A7.
- Skrypt zapisujący A6 leży w `projects/_archive/benchmark-core-apply-a6.py`,
  bo audyt `isolation.no_lockbox_configs_in_runtime` słusznie zgłosił nazwy
  konfiguracji Lockboxa w kodzie runtime — audyt **nie** został poszerzony.

Weryfikacja:
- `python audit_v2.py` → `verdict: CLEAN (0 hard findings)`, 56 plików runtime.
- `pytest test_benchmark_v2.py` → 18 passed in 2.97s.
- `ledger.verify_integrity(expected_manifest_sha256=…)` → OK, 7 wpisów.
- `git diff --check` → exit 0.

Next: decyzja właściciela o §8 jako A7, jeden z trzech wariantów:
(a) Lockbox = 6 nietkniętych zadań, świadomie bez mocy statystycznej;
(b) 42 zadania zostają jako diagnostyka post-hoc, bez prawa do twierdzenia
konfirmacyjnego; (c) nowe dane spoza fev-bench-100 odbudowują ślepy Lockbox.
Niezależnie od wyboru: zaległy suchy przebieg Fazy 1b na Dev
(SNaive/NLinear/DLinear, 3 okna, czas p95, MDE) — jedyny pomiar, który
odblokowuje Fazę 2.

not checked: mapowanie domen vs papier fev (Appendix E/Tabela 15) — nadal manualne;
czas p95 na `boomlet_1676`; budżet ściany Lockboxa; brak guarda w `bench.py`
przed ponownym `--fev-full` (audyt zgłasza to jako ryzyko proceduralne,
świadomie nietknięte w tym commicie, bo to zmiana zachowania, nie dysclosure).
