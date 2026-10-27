---
type: Concept
title: _template
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Reflection — <YYYY-MM-DD_HHMM_S-XX-slug>
Date: <YYYY-MM-DD>
Status: <complete | yielded-partial | blocked>
Invoking rule: REFLECTION_RULES.md (T<n>)

## work_summary
<1–3 sentences: what work finished, and its state>

## problems
### P1: <short problem id>
- **symptom:** <observable fact — what the user saw or what broke>
- **root_cause:** <fact about why, grounded in logs/source>

### P2: <short problem id>
- **symptom:**
- **root_cause:**

## solutions
### P1
- **solution:** <what was done>
- **verification_evidence:** <log path | re-runnable command | tool artifact>
- **files_changed:**
  - `<path>`

### P2
- **solution:**
- **verification_evidence:**
- **files_changed:**
  - `<path>`

## prevention_rules
### P1
- **invariant:** <deterministic, falsifiable rule>
- **owning_doc:** <path>
- **owning_doc_updated:** <Y | N>

### P2
- **invariant:**
- **owning_doc:**
- **owning_doc_updated:**

## next_action_routing_changes
- <routing/contract updates applied this session, or `none`>

## open_risks
- <not verified / deferred / expected-but-empty items, or `none`>