# Session Review: Weryfikacja T3 — rozbieżność `in_db=False` vs „oracle istnieje" (2026-10-13)

## Cel
Rozstrzygnąć rozbieżność w raporcie T3: toolcall zwracał `in_db=False`, a raport stwierdzał „Oracle istnieje? tak".

## Metoda (diagnosing-bugs: feedback loop → reproduce → hipotezy → weryfikacja)
- **Feedback loop:** `scripts/_scratch/check_oracles.py` (determinystyczny, sekundy, red-capable) — sprawdza 18 exact ID wprost w SQLite.
- **Reprodukcja:** `graph.db` w `pilots/graphrag/` ma **0 bajtów** (pusty). T3 sprawdzał ten plik → `in_db=False` było artefaktem pustej bazy.
- **Hipotezy:** (H1) oracles nie ma w bazie → sfalsyfikowana. (H2) T3 sprawdzał złą bazę → potwierdzona. (H3) „embedding mismatch" z raportu T3 → wątpliwa, do rozstrzygnięcia w T13.

## Surowy output weryfikacji (`check_oracles_v2.py` → `fixtures/graph_vec.db`)
```
621_artificial_intelligence_a_modern_approach_4th_ed => 1
1034_artificial_intelligence_a_modern_approach_4th_ed => 1
364_paradigms_of_artificial_intelligence_programming => 1
22_paradigms_of_artificial_intelligence_programming => 1
293_paradigms_of_artificial_intelligence_programming => 1
376_pattern_recognition_and_machine_learning_christo => 1
651_pattern_recognition_and_machine_learning_christo => 1
425_beginning_software_engineering_2nd_edition_rod_s => 1
292_structure_and_interpretation_of_computer_program => 1
212_structure_and_interpretation_of_computer_program => 1
244_structure_and_interpretation_of_computer_program => 1
405_structure_and_interpretation_of_computer_program => 1
46_structure_and_interpretation_of_computer_program => 1
354_multiagent_systems_algorithmic_game_theoretic_an => 1
383_multiagent_systems_algorithmic_game_theoretic_an => 1
405_multiagent_systems_algorithmic_game_theoretic_an => 1
10_multiagent_systems_algorithmic_game_theoretic_an => 1
00_multiagent_systems_algorithmic_game_theoretic_an => 1
TOTAL_EXISTS=18/18
TOTAL_NODES=10373
```

## Defect class 4 — potwierdzony (family match, nie embedding mismatch)
Liczba wariantów tego samego sluga z różnymi prefiksami numerycznymi:
```
artificial_intelligence_a_modern_approach_4th_ed => 1123
paradigms_of_artificial_intelligence_programming => 828
pattern_recognition_and_machine_learning_christo => 736
beginning_software_engineering_2nd_edition_rod_s => 647
structure_and_interpretation_of_computer_program => 518
multiagent_systems_algorithmic_game_theoretic_an => 510
```
Gold exact ID istnieje, ale retrieval może zwrócić **inny chunk tego samego dokumentu** — „an id that resolves proves nothing about *what* it resolves to".

## Werdykt: Scenariusz A z adnotacją
- Raport T3 merytorycznie poprawny (oracles istnieją 18/18), ale **bez pokrycia w toolcallu** — S59.
- Przyczyna `in_db=False`: **pusta `graph.db` (0 bajtów)**, nie brak oracla. Właściwa baza to `fixtures/graph_vec.db` (10 373 węzły).
- Hipoteza „embedding mismatch" z T3 jest **wątpliwa** — do rozstrzygnięcia w T13.
- **T3: confirmed closed, z adnotacją. Nie retired.**
- **T13 (nowy):** weryfikacja gold IDs w Trust Secie względem aktualnego re-ingestu — czy retrieval zwraca exact gold, czy inny chunk tego samego sluga?

## Bramki
- G1: `TOTAL_EXISTS=18/18` — zaliczona (`check_oracles_v2.py`).
- G2: raport istnieje — zaliczona.

## not checked:
- `pilots/graphrag/eval/_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json` (9 plików roboczych z eval/)
- `scripts/_scratch/GATES.md`, `scripts/_scratch/check_oracles.py`, `scripts/_scratch/check_oracles_v2.py` (gitignore — artefakty robocze)
- R19: świadomy dług (retired w T10)

## R18 / governance
0 commitów governance-only w tej sesji (1 commit badawczy: raport + S63 + mapa).

## Commit zamknięcia (rzeczywisty `git log -1 --format=%B`)
```
kr-t3-verification-2026-10-13: `kr-t3-verification-2026-10-13` — 2026-10-13: rozstrzygnięto rozbieżność T3 (`in_db=False` w too[…ucięty subject, S60…]
```
Hash: flaga `kr-t3-verification-2026-10-13` (pełny hash zob. `git log` — S60: subject ucięty do 96 znaków).
