---
type: Concept
flag: session-digest-ab-2026-10-23
since: 2026-10-23
owner: opencode
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: A/B test requested after the inventory review (L0 design vs shipped output)
title: session-digest-ab-2026-10-23
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`session-digest-ab-2026-10-23` — 2026-10-23: **L0 unproven/closed; L1 is a
selection index, not an analysis layer.** A/B on one real question:
*"what happened with `--classify` — candidate count, promotion, cause, next
step?"* Same 3 sessions (review/promotion, classify, commit), three corpora.

| Corpus | Content | Size | Read | Score |
|---|---|---|---|---|
| P (plan A) | L1 cards + 3 full bodies | 270 040 B | 1 828 / 5 670 lines | 4/4 facts |
| Q (plan B) | `did` for the same 3 | 180 308 B | 3 726 / 3 726 | 4/4 + 3 extra |
| R (L1 only) | 3 cards, no bodies | 3 913 B | 147 / 147 | 0/4 — "brak w materiale" |

Scored facts: 6 candidates (4 `open_threads` + 2 `contradictions`); 0/6 true
→ no promotion; cause `session_facts._marker_scan` + `not_checked` in
`OPEN_MARKERS`; next step rules-v2 + `review_ref`. Q additionally found
40 sessions / 93 children, smoke 0 candidates, and the pre-`--classify` state.
L0 contributed nothing: 781 B, all `_brak_`.

Decision: do not build `--profile llm`; do not promote L0. Keep L1 as the
selector (filter `session_cards.json` by `files`/`flags`), then export 2–5
sessions; use `did` or the selected bodies for analysis. Recorded in
`brain/decisions/ADR-005-session-digest-fact-judgment.md` ("Wynik A/B") and
`docs/session-digest-GATES.md` G14.

Reproduction (corpora are one-off, under `%TEMP%`, never committed):

```text
python scripts/session_digest.py 10 --out-dir %TEMP%\digest-probe-10
python scripts/session_digest.py --classify --count 10 --out-dir %TEMP%\digest-probe-10
python scripts/extract_did.py 6 -o %TEMP%\ab-test\did6.md
python scripts/agent_sessions.py export opencode ses_e9ee3df48ffeI2L1QarEEqiSUz -o %TEMP%\ab-test\body-1.md
python scripts/agent_sessions.py export opencode ses_e9ef9abd8ffeilAF4R1y6kPPWq -o %TEMP%\ab-test\body-2.md
python scripts/agent_sessions.py export opencode ses_e9efe1ee0ffeT9xzjalxF9309H -o %TEMP%\ab-test\body-3.md
```

`%TEMP%\ab-test` is disposable; only the numbers above are the evidence.

not checked: n=1 question, 3 sessions, one model; P and Q differ in content
filter (P keeps read-only calls and payloads, Q drops them); scoring was not
fully blind because the formats are recognisable. The design session
(574 KB in `did`) was outside the test, so the "rejected alternatives"
question was not measured; its cost gap would only favour `did` further.
