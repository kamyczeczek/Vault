---
flag: brain-memory-v1-landed-2026-10-16
since: 2026-10-16
owner: mateusz
agent: opencode
model: nara/deepseek-v4.1-flash-free
origin: session-close
---

`brain-memory-v1-landed-2026-10-16` — 2026-10-16: Warstwa brain jest realna — ingest → door → bramka, wszystkie trzy w jednej sesji (nie rozbite na trzy, jak nakazywał brief).

- `scripts/ingest_brain.py` (nowy, wyprowadzony z `scripts/_scratch/`): odbudowuje `brain/brain.db` z `SCARS.md` / `DECISIONS.md` / `brain/lessons.md`. Idempotentny; `--check` to świeżość i pokrycie w jednym pytaniu.
- Usunięto **12 fabrykowanych** wierszy (`fix='Mention of S<n> in SCARS.md'` — wiersz twierdzący treść, której nie ma; `S32`/`S33` nie są nawet wpisami, a wzmiankami w prozie innego scara). `problems`: 24 → **46** wierszy; tekst 14 883 → **24 053** znaków. Wcześniej ~37% pliku było poza bazą (0/10 próbkowanych fragmentów bulletów obecnych).
- Fix po drodze: marker reguły w `SCARS.md` to `**Reguła:**` (dwukropek **wewnątrz** pogrubienia) — pierwszy parser rozdzielał 0/22 nieutytułowanych blizn.
- Door: `python.exe scripts/brain.py "<temat>"` — cienka warstwa nad `retrieval_v1.py` **bez zmian**. Przy braku trafienia kieruje do drugiej bramki, sesyjnej (`memory_index.py`), bo warstwy odpowiadają na różne pytania.
- Bramka **R21** (twarda, `check_workspace_integrity.py`): `ingest_brain.py --check` + `eval_brain.py --check` (regresja poniżej zapisanego baseline). Degraduje do WARN tylko gdy `brain.db` nie istnieje (świeży klon); gdy istnieje — nigdy nie przepuszcza milcząco.
- **Dowód, że bramka umie failować:** po skasowaniu `problems:1022` z bazy `R21` zgłasza `1 source row(s) absent from brain.db: [1022]`, po re-ingest wraca do zieleni. Po drodze naprawiłem własny defekt: `check()` drukowało zieloną linię „46 rows match" także przy brakującym wierszu — dokładnie „green line that verified nothing" z docstringu R14.
- Pomiar (14 pytań, `scripts/memory/brain_eval.json`, `--limit 5`): **hit@5 2/10 → 9/10, refusal 3/4, MRR 0.200 → 0.900**. Baseline + `known_gaps` zapisane w pliku ewaluacji.
- Kontrakt: `brain/CONTEXT.md` (nowy). Wiersz `brain/` w `CLAUDE.md` podniesiony do standardu wiersza `scripts/memory/` — to jest powierzchnia routingu, bo `AGENTS.md` jest zablokowany (patrz niżej).

Następny krok — jeśli ruszasz `SCARS.md`, uruchom `python.exe scripts/ingest_brain.py`; R21 i tak tego wymusi.

not checked:
- **Wiersz routingu w `AGENTS.md` NIE dodany** — `AGENTS.md` pilnuje R13 (`audit_agents_md.py --check`, baseline 133 linii), więc dodanie wiersza to kaskada ≥3 plików (baseline + raport w `docs/reviews/` + archiwizacja poprzednika), czyli dokładnie scar „AGENTS.md routing row = R13 cascade". Door jest routowany przez `CLAUDE.md` + `brain/CONTEXT.md`. Osobny ticket z planem R13; świadoma decyzja, nie przeoczenie.
- Dwie znane luki retrievera, **nie naprawiane**: pytanie PL „integralności" nie trafia w angielski token `integrity` z `lessons:1` (leksykalny K1, brak stemmera PL↔EN); `refuse-risotto` odpowiedziane mimo braku dowodu (1/4 odmów). Oba w `brain_eval.json#known_gaps` i drukowane przez bramkę.
- Granularność `DECISIONS.md` — decyzja właściciela, nietknięta; `DECISIONS.md` jest kompletne (25 nagłówków → 22 id, brakujące wg briefu nie istnieją).
- `brain/problems/` nadal puste (tylko `README.md`) — nie było czego ingestować.
- `model: current`/`default` w 14 flagach (3 `current`, 11 `default`) — dług zastany, nietknięty.
- Nie mierzono warstwy na pytaniach spoza `brain_eval.json`; refusal 3/4 to sufit leksykalny, nie zmierzony głębiej.
- `handoff/state_description/exports.md` jest zmodyfikowany w worktree (regenerowany manifest eksportu z cudzej sesji) — **nie wciągnięty** do tego commita i nie skasowany.
