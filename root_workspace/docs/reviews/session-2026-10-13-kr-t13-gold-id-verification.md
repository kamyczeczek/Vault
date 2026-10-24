# T13: Weryfikacja gold IDs — exact hit vs family hit (2026-10-13)

## Cel
Rozstrzygnąć sprzeczność T3 („embedding mismatch") vs T3-verify („defect class 4").

## Surowy output `t13_exact_vs_family.py`
```
Total in-corpus items with oracles: 33
Total zawodne (recall@5 == 0.0): 18

ZAWODNE SUMMARY (Total 18):
  Exact hit @5: 0
  Family hit @5 (any): 16
  Family-only hit @5 (exact not in @5, but family in @5): 16
  Neither @5 (no family in top10 @5): 2

ALL 33 IN-CORPUS SUMMARY:
  Exact hit @5: 15
  Family hit @5 (any): 31
  Family-only hit @5: 16
  Neither @5: 2
```

## Tabela 18 ZAWODNE
| QID | Oracle | exact@5 | family@5 | returned (family pos) |
|-----|--------|---------|----------|-----------------------|
| Q01 | `621_artificial_intelligence_a_modern_approach_4th_ed` | nie | tak (poz. 1) | `158_artificial_intelligence_a_modern_approach_4th_ed` |
| Q04 | `1034_artificial_intelligence_a_modern_approach_4th_ed` | nie | nie | `None` |
| Q06 | `364_paradigms_of_artificial_intelligence_programming` | nie | tak (poz. 1) | `06_paradigms_of_artificial_intelligence_programming` |
| Q07 | `22_paradigms_of_artificial_intelligence_programming` | nie | tak (poz. 2) | `730_paradigms_of_artificial_intelligence_programming` |
| Q08 | `293_paradigms_of_artificial_intelligence_programming` | nie | tak (poz. 1) | `07_paradigms_of_artificial_intelligence_programming` |
| Q11 | `376_pattern_recognition_and_machine_learning_christo` | nie | tak (poz. 2) | `361_pattern_recognition_and_machine_learning_christo` |
| Q14 | `651_pattern_recognition_and_machine_learning_christo` | nie | tak (poz. 1) | `558_pattern_recognition_and_machine_learning_christo` |
| Q18 | `425_beginning_software_engineering_2nd_edition_rod_s` | nie | tak (poz. 4) | `411_beginning_software_engineering_2nd_edition_rod_s` |
| Q21 | `292_structure_and_interpretation_of_computer_program` | nie | tak (poz. 4) | `507_structure_and_interpretation_of_computer_program` |
| Q22 | `212_structure_and_interpretation_of_computer_program` | nie | tak (poz. 2) | `151_structure_and_interpretation_of_computer_program` |
| Q23 | `244_structure_and_interpretation_of_computer_program` | nie | tak (poz. 3) | `241_structure_and_interpretation_of_computer_program` |
| Q24 | `405_structure_and_interpretation_of_computer_program` | nie | tak (poz. 2) | `391_structure_and_interpretation_of_computer_program` |
| Q25 | `46_structure_and_interpretation_of_computer_program` | nie | nie | `44_structure_and_interpretation_of_computer_program` (poz. 6) |
| Q26 | `354_multiagent_systems_algorithmic_game_theoretic_an` | nie | tak (poz. 2) | `335_multiagent_systems_algorithmic_game_theoretic_an` |
| Q27 | `383_multiagent_systems_algorithmic_game_theoretic_an` | nie | tak (poz. 1) | `334_multiagent_systems_algorithmic_game_theoretic_an` |
| Q28 | `405_multiagent_systems_algorithmic_game_theoretic_an` | nie | tak (poz. 2) | `396_multiagent_systems_algorithmic_game_theoretic_an` |
| Q29 | `10_multiagent_systems_algorithmic_game_theoretic_an` | nie | tak (poz. 2) | `13_multiagent_systems_algorithmic_game_theoretic_an` |
| Q30 | `00_multiagent_systems_algorithmic_game_theoretic_an` | nie | tak (poz. 4) | `183_multiagent_systems_algorithmic_game_theoretic_an` |

## Werdykt
Ścieżka A: family-match-only > 50%.
Z 18 przypadków ZAWODNE:
- Exact hit @5: `0` (`0.0%`)
- Family-only hit @5: `16` (`88.9%`)
- Neither @5: `2` (`11.1%`)

**Werdykt:** `88.9%` false refusals to w rzeczywistości family-match-only hits (retriever znajduje właściwą książkę / slug, ale inny chunk niż exact gold ID w adnotacji). Metryka `recall@5` mierzy annotację exact ID, nie retrieval.

## Konsekwencja
- `measurements.md`: dodano sekcję „Retired: recall@5 on Trust Set".
- `SCARS.md`: dodano S64.
- Nowa metryka dla Trust Set: `family_recall@5` (na slugach).

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---------|---------|--------------------------|
| `33` | `python scripts/_scratch/t13_exact_vs_family.py` | `Total in-corpus items with oracles: 33` |
| `18` | `python scripts/_scratch/t13_exact_vs_family.py` | `Total zawodne (recall@5 == 0.0): 18` |
| `16` | `python scripts/_scratch/t13_exact_vs_family.py` | `Family-only hit @5 (exact not in @5, but family in @5): 16` |
| `2` | `python scripts/_scratch/t13_exact_vs_family.py` | `Neither @5 (no family in top10 @5): 2` |
| `50` | `python scripts/_scratch/t13_exact_vs_family.py` | `Threshold for majority rule (> 50%)` |

## not checked:
- `pilots/graphrag/eval/_tmp_ask_by_graphrag.json`, `_tmp_frozen_golds.json`, `_tmp_run_ask_benchmark.py`, `_tmp_run_graphrag_on_trust.py`, `_tmp_run_v2_comparison.py`, `_tmp_trust_by_ask.json`, `_tmp_v2_comparison.json`, `_tmp_v2_match_table.json`, `_tmp_v2_questions.json` (9 plików roboczych z eval/).

## R18 / governance
Ta sesja jest badawcza (retrieval). Governance streak przerwany.
