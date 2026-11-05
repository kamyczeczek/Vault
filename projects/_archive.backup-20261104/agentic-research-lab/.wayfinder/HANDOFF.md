---
updated: 2026-10-08T05:18:00+02:00
---

# Handoff — decision-brief hypothesis D

## State

Session closed at D-002 implementation decision. Wayfinder map live at `.wayfinder/MAP.md`.

## What was done

- Defined hypothesis D: decision brief grounded in ARL graph improves architectural decisions for weak models
- Created wayfinder map with 6 tickets
- Resolved D-001 (brief format: 4 sections, hard 8K, hybrid citation, no recommendation, file + prepend)
- Resolved D-002 (precedent classification: new `node_type = "precedent"`, `ask.py` filters, hybrid ranking, scars section, non-fatal missing precedents)

## Open questions

- D-003: How to measure decision quality (LLM-judge, distance from ground truth, expert)?
- D-004: How many ADRs in retrospective (n=5, n=10)?
- D-005: Which specific ADRs to include?
- D-006: Promotion threshold to TRANSFER.md

## Next action

Review `.wayfinder/MAP.md`, pick next ticket (D-003 recommended), and continue implementation.
