---
ticket: E7
status: done
resolved: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
decision: adopted expect_hash per case; fail-loud in eval_brain.py --check
---

# E7 — wykonanie B7: `expect_hash` w anchorach `brain_eval.json`

**Decyzja źródłowa:** `docs/wayfinder-brain-answers/B7-content-hash-anchors.md` (resolved
2026-10-16). Ten plik to **wykonanie** — dowód, że decyzja weszła w życie (zamyka dług
S64/S65: „decyzja bez wykonawcy to dług").

## Co zostało zrobione

1. **`expect_hash` per answerable case** — `scripts/memory/brain_eval.json`: każdy z 10
   answerable case'ów (`expect != null`) dostał `expect_hash` = sha256 wiersza spod `expect`
   w `brain.db`. Refusal case'e (`expect == null`) **nie** dostały pola (nie ma wiersza do
   hashowania; ich bramką są puste trafienia). Wygenerowane skryptem, nie ręcznie.
2. **Jedno źródło prawdy o „wierszu"** — `scripts/memory/eval_brain.py` importuje
   `_row_fingerprint` **z** `scripts/ingest_brain.py` (ta sama funkcja, której używa
   `ingest_brain.py --check`). Brak drugiej definicji payloadu.
3. **Fail-loud** — `eval_brain.py --check` (funkcja `verify_anchors`) czyta wiersz spod
   `expect` z `brain.db`, liczy `_row_fingerprint` i porównuje z `expect_hash`; rozbieżność
   → `exit 1`, z nazwą przypadku, `table:id` i **oczekiwanym oraz aktualnym hashem**. R21 w
   `check_workspace_integrity.py` już woła `eval_brain.py --check` — bramka ma callera.

## Rozwiązanie otwartej pozycji z B7

B7 `not checked` zostawił: „nie potwierdzono, że `_row_fingerprint` ma identyczny payload
liczony ze źródła i z `brain.db` dla `lessons`/`decisions`". **Potwierdzone:** payload jest
identyczny — `ingest_brain.py --check` liczy `expected` z `read_sources()` i `actual` z
`brain.db` tą samą funkcją i przechodzi dla wszystkich tabel (`lessons: 2 row(s) match`,
`decisions: 23 row(s) match`, `problems: 48 row(s) match`). Gdyby payloady się różniły,
`--check` failowałby na `drifted` dla każdego wiersza. Zero driftu = ta sama definicja w obu
miejscach.

## Kryterium sukcesu — trzy mutacje (zapisane **przed** runem, S56/S62)

Mutacje wykonane na żywej bramce, każda w izolacji, z pełnym restore (backup `SCARS.md`,
`Copy-Item` z powrotem, re-`ingest`, kontrola PASS). Surowy output:

### Mutacja 1 — shift: syntetyczny bezimienny `- …` scar wstawiony na górę `SCARS.md`

Wstawienie jednego bezimiennego wiersza przesuwa wszystkie anchory `problems:10XX`.

```
FAIL msys-python-c-ban: want problems:1001, got [problems:1002, problems:1019, problems:1015, decisions:22, problems:1018]
FAIL root-delete-to-pass-gate: want problems:1022, got [problems:1023, problems:62, problems:67]

brain_eval: hit@5=7/10 refusal=3/4 MRR=0.700
FAIL: brain eval anchor drifted — msys-python-c-ban (problems:1001): row content changed — expected 5c4e0e40a50e062491d43de3d01a44154fcc7808d7fe4e4e1dab862b7530dacf, got e51f68f32e65dbeea49e9708bb1bf4270aa7b644d7a5c1c7633738ef9bf03c32
FAIL: brain eval anchor drifted — root-delete-to-pass-gate (problems:1022): row content changed — expected 004ac493e1c293ce88925a2a5436668c938654aae1084dc70aca7495bce8ca6c, got 411e4cb6bec7dde4982820b031001fc42732ed8eda69e6449cadc720a4586f18
FAIL: brain retrieval regressed — hit@5 7/10 < baseline 9/10
Fix the retrieval or the row; do not lower the baseline to pass.
EXIT: 1
```

### Mutacja 2 — kontrola negatywna: bez mutacji (baseline)

```
brain_eval: hit@5=9/10 refusal=3/4 MRR=0.900
OK — brain retrieval is at or above the baseline recorded 2026-10-16
EXIT: 0
```

### Mutacja 3 — reword w miejscu (to samo ID `problems:1001`, inna treść)

Zmieniony wiersz w miejscu (parenthetical w bezimiennym scarze `problems:1001`) — retrieval
nadal trafia rank 1, **metryki zostają zielone**, ale hash wiersza się rozjeżdża. To jest
dokładnie „cicha zmiana mierzonego wiersza", którą B7 nazywa:

```
PASS msys-python-c-ban: rank 1 of 5
brain_eval: hit@5=9/10 refusal=3/4 MRR=0.900
FAIL: brain eval anchor drifted — msys-python-c-ban (problems:1001): row content changed — expected 5c4e0e40a50e062491d43de3d01a44154fcc7808d7fe4e4e1dab862b7530dacf, got 996b7e2f806f4877c1d144d63f93cc5ce41132b8fdbd6895df033edc97b72d16
Fix the retrieval or the row; do not lower the baseline to pass.
EXIT: 1
```

**Wszystkie trzy zgodne z oczekiwaniem zapisanym przed runem.** Restore zamknięty: `SCARS.md`
po mutacjach bit-identyczny z backupem (`Get-FileHash` równy), `ingest_brain.py --check` OK,
kontrola `eval_brain.py --check` → EXIT 0.

## Czego nie zmieniono

- **Próg bramki (S62)** — `expect_hash` to **nowe pole + nowa asercja**, nie zmiana istniejącej.
  `hit_ok`/`answerable`/`refusal_ok`/`refusals`/`mrr` w `brain_eval.json` nietknięte
  (0 usuniętych linii w `git diff --numstat`; metryki 9/10, 3/4, 0.900 bez zmian).
- **`brain_eval.json` baseline opisowy** — string `brain_db` („46 problems …") zostawiony jako
  zapis historyczny pomiaru (reguła 7). Uwaga o jego zestarzeniu: patrz flaga zamknięcia —
  `problems` = 47 przed tą sesją (S68), 48 po dodaniu S69.
- **Refusal case'e** — bez `expect_hash`.

## Pliki

- `scripts/memory/eval_brain.py` — `verify_anchors` + import `_row_fingerprint` + wiring w `--check`.
- `scripts/memory/brain_eval.json` — 10 × `expect_hash`.
- `SCARS.md` — S69 (osobny dług tej sesji, patrz flaga).
