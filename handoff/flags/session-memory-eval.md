---
type: Concept
flag: session-memory-eval
since: 2026-10-05
owner: mateusz
agent: droid
model: cx/gpt-5.6-luna-low
origin: session-memory evaluation
updated: 2026-10-07 (R16 docstring correction — substring + inert .dsh/ — by agnes-3-flash)
title: session-memory-eval
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`session-memory-eval` — 2026-10-05: domyślny ingest obejmuje całą historię, freshness sprawdza pokrycie per agent, a eval filtruje błędy/decyzje po typie.

**2026-10-07 R15 fix (data drift, NIE regres kodu).** Dwa padające przypadki
(`provider error` + `provider error variant`) dały 13/15, bo 5 świeższych
sesji droid z bajtowo identycznym pierwszym wiadomością `cx/gpt-5.6-luna-*`
provider-error wypychało oczekiwane kanoniczne sesje `8ced867d-a735` /
`c5c82ede-91fc` z top-5. Rozstrzygnięcie (Opcja A z briefu): dodano
`exclude_session_ids` do obu przypadków w `scripts/memory/eval_queries.json`
(5 droid-duplikatów: `212103a0-392c`, `9b838833-1e8d`, `6c6fc914-7b63`,
`29ef7349-ba67`, `57b869b1-ad78`) oraz support tego pola w
`scripts/eval_memory_retrieval.py` (fetch limit+len(excluded), odrzuć prefiksy,
obkrój do limit). Do expected wariantu dodano antigravity `061d7295-9263`
("Structure of a Custom Provider JSON" — zweryfikowane ciałem chunka).

**Nowy baseline: 15/15, hit@5=1.000, MRR=0.733.** Progu gate NIE obniżano —
naprawiono dane.

OPEN:
- `freshness()` stracił per-agent coverage — raportuje teraz OK/UNVERIFIED po
  "czy loader z dysku cokolwiek w ogóle czyta", a nie po liczbie per agent,
  bo design `--include-runtime` (DSH) sprawia, że loader z dysku zawiera sesje
  runtime, których domyślny `ingest` nie indeksuje. Przywrócenie liczników
  dałoby fałszywe INCOMPLETE. Zanotowane, nie naprawiane w tej sesji.
- R16 advisory check — **zaimplementowany** (2026-10-07) w
  `scripts/check_workspace_integrity.py` jako `check_r16_session_memory_usage`
  (wyłącznie `WARNS`, nigdy nie blokuje commitu): commit dotykający
  `scripts/**`,`hooks/**`,`skills/**`,`.dsh/**` w ostatnich 30 min wymaga
  świeżego wpisu `scripts/_scratch/sessions/queries.jsonl` (last ~30 min)
  LUB słowa `query` w subject commitu. **2026-10-07 (commit b4cfb1c): zwięzono
  claimy — gałąź zaspokajająca to podciąg `"query" in subject`, nie zweryfikowany
  cytat `query "..."`; prefiks `.dsh/` jest inertyjny (magazyn DSH żyje w
  `~/.dsh`, poza tym repo), więc łapie dziś 3 z 4 prefiksów. Docstring + WARN
  poprawione, zero zmiany zachowania.** Zweryfikowane wszystkie
  gałęzie: WARN wystrzelił na żywo (ostatni commit poprzedniej sesji, bez
  świeżej telemetrii), świeża telemetria i cytat gaszą WARN.

Next: utrzymuj indeks przez `python.exe scripts/memory_index.py ingest`.
