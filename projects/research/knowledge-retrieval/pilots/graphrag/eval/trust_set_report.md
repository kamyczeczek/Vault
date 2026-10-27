---
type: Concept
title: trust_set_report
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Trust Set Report — 2026-10-11 (Natural Questions Retest)

## Test set
- In-corpus: 33 questions (3 base + 30 natural questions derived from corpus inventory titles & bodies, without ID/metadata in text)
- OOC: 15 questions (refusal expected)
- Boundary: 10 questions (refusal expected, close domain)
- Total: 58 questions

## Results (Semantic gate OFF / Wariant 1 calibrated threshold 0.45)
- IN-CORPUS (n=33): MRR@5 = 0.295, Recall@5 = 0.455
- OOC refusal: 15/15 (100.0%)
- BOUNDARY refusal: 5/10 (50.0%)
- FALSE REFUSAL in-corpus: 16/33 (48.5%) — stringent `MIN_KEYWORD_MATCHES=2` + keyword extraction on natural phrasing.

## Retest 2026-10-11 (30 natural questions)
- TRAFIONE (oracle in top-5, MRR@5 >= 0.2): 15/33
- ZAWODNE / POZA TOP-5: 18/33
- OOC refusal: 15/15 (100.0%)
- BOUNDARY refusal: 5/10 (50.0%)
- MRR@5 in-corpus: 0.295
- Recall@5 in-corpus: 0.455

### Bucket ZAWODNE (Diagnosis)
1. **Q01**: *Jak działa przeszukiwanie min-max w drzewach gier?* — Oracle `621_...`, Top-5 retrieved nodes did not include oracle in top-5 (FTS5 ranking gap for general phrasing).
2. **Q04**: *Jak definiuje się operacje na macierzach i ich indeksowanie w algebrze liniowej?* — Oracle `1034_...`, Top-5 returned unrelated code/agent nodes.
3. **Q06**, **Q07**, **Q08**: Lisp programming questions mapped to other parts of paradigms book rather than exact oracle nodes.
4. **Q11**, **Q14**: PRML pattern recognition queries returned distant chapters.
5. **Q18**: Agile iterative planning query returned domain-driven design nodes.
6. **Q21–Q25**: SICP interpreter/register machine/fast exponent queries returned related programming or agent nodes.
7. **Q26–Q30**: Multiagent systems auction/coalitional game queries returned adjacent chapters or AI textbook chapters.

## STOP GATE C — BLOKADA
- **BLOKADA — MRR@5=0.295 < 0.4, 48.5% false refusal in-corpus.**
- The natural-question trust set does not pass the required retrieval gate. This report must not be interpreted as a successful validation.

## Conclusion & Recommendation
- Natural questions improved over the prior template set (MRR@5 0.207 → 0.295; Recall@5 0.242 → 0.455), but remain below the acceptance gate.
- Out-of-corpus refusal remains 100.0% (15/15); boundary refusal is 50.0% (5/10).
- Further diagnosis belongs to the owner; this session does not change retrieval parameters, models, or questions.
