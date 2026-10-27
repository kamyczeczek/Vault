---
type: Concept
title: session-2026-10-12-graphrag-trust-set
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# Session report — GraphRAG natural-question trust set

## Status
**BLOKADA — test result: MRR@5=0.295 < 0.4, 48.5% false refusal in-corpus; 18/33 ZAWODNE.**

## Scope
This report closes the natural-question trust-set retest. No retrieval threshold, model, or question was changed in this closing session.

## Raw output from Phase C
Source transcript: `C:/Users/Mateusz/.pi/agent/sessions/--C--Users-Mateusz-Desktop-root_worksapce--/2026-10-11T22-38-51-375Z_01a12d1e-6dee-7690-8d95-9c281e66f3cf.jsonl`

The recorded measurement output was:

```text
=== IN-CORPUS ===
Q00a: MRR@5=1.000 Recall@5=1.000 odmowa=False
Q00b: MRR@5=1.000 Recall@5=1.000 odmowa=False
Q00c: MRR@5=1.000 Recall@5=1.000 odmowa=False
Q01: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q02: MRR@5=0.500 Recall@5=1.000 odmowa=True
Q03: MRR@5=1.000 Recall@5=1.000 odmowa=True
Q04: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q05: MRR@5=0.333 Recall@5=1.000 odmowa=True
Q06: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q07: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q08: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q09: MRR@5=0.500 Recall@5=1.000 odmowa=False
Q10: MRR@5=0.500 Recall@5=1.000 odmowa=True
Q11: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q12: MRR@5=0.333 Recall@5=1.000 odmowa=True
Q13: MRR@5=0.333 Recall@5=1.000 odmowa=True
Q14: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q15: MRR@5=0.250 Recall@5=1.000 odmowa=False
Q16: MRR@5=0.500 Recall@5=1.000 odmowa=False
Q17: MRR@5=1.000 Recall@5=1.000 odmowa=False
Q18: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q19: MRR@5=1.000 Recall@5=1.000 odmowa=False
Q20: MRR@5=0.500 Recall@5=1.000 odmowa=False
Q21: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q22: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q23: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q24: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q25: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q26: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q27: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q28: MRR@5=0.000 Recall@5=0.000 odmowa=True
Q29: MRR@5=0.000 Recall@5=0.000 odmowa=False
Q30: MRR@5=0.000 Recall@5=0.000 odmowa=False

=== OUT-OF-CORPUS ===
O01..O15: odmowa=True (15/15)

=== BOUNDARY ===
B01: odmowa=True
B02: odmowa=True
B03: odmowa=False
B04: odmowa=True
B05: odmowa=False
B06: odmowa=True
B07: odmowa=False
B08: odmowa=True
B09: odmowa=False
B10: odmowa=False

=== ZBIORCZO ===
IN-CORPUS (n=33): MRR@5=0.295 Recall@5=0.455
OOC refusal (n=15): 100.0%
BOUNDARY refusal (n=10): 50.0%
FALSE REFUSAL in-corpus (n=33): 48.5%

Zapisano: .../projects/research/knowledge-retrieval/pilots/graphrag/eval/trust_set_results.json
```

## Bucket summary
- **TRAFIONE:** 15/33.
- **ZAWODNE / poza top-5:** 18/33.
- **OOC refusal:** 15/15.
- **Boundary refusal:** 5/10.

Detailed per-question results are in `pilots/graphrag/eval/trust_set_report.md` and raw results in `pilots/graphrag/eval/trust_set_results.json`.

## Not checked
- `not checked:` whether each ZAWODNE question is caused by wording breadth/narrowness or by the retriever.
- `not checked:` a new C.2 run after manually revising questions.
- `not checked:` functional close/integrity gates in this report itself.

## Decision
Further action is for the repository owner. This session records the failed gate and does not claim validation success.
