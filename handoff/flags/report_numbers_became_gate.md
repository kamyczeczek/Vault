---
type: Concept
flag: report_numbers_became_gate
since: 2026-10-03
owner: opencode
agent: review
model: opencode/space-bunny-free
origin: architecture review (improve-codebase-architecture x icm-architect)
title: report_numbers_became_gate
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`report_numbers_became_gate` — 2026-10-03: **landed** as root `9a8e105`, with
`--report-check` + the v7 report in `8282dd1`, and both gates wired in `a15ebf4` /
`931aac5`. `scripts/audit_agents_md.py` (stdlib only) classifies the `AGENTS.md`
token-efficiency section by rule, not by line number: routing 17 / evidence 24 /
heading 1 / blank 9 = 51 = `:61-:111`. Span is derived from the headings, so it
cannot silently truncate. Duplicate detection is a separate finding, not a
category: `:110` is byte-identical to `:72`, `:91` a substring of it once the `- `
bullet marker is stripped. R13 (hard) now runs `--check` plus `--report-check`
over `docs/reviews/`, so the classification and every report quoting it are both
enforced at commit time; 29 hermetic tests
(`scripts/test_audit_agents_md.py`) pin both drift directions.

Why: the review reached v6 because every count lived in prose. Five revisions,
five hand-counts, five different answers — and each error ran in the direction
that flattered the candidate under discussion. The review charged
`restamp_provenance.py` with "refuses correctly but nothing calls it" and then did
the same thing: claimed "counted line by line" without shipping anything
checkable. This script is that artifact, and the "nothing calls it" half was
closed by R13.

Two bugs the script caught in its own first draft, both by running it rather than
reading it: (1) `section_span` stopped at `:91`, treating `## Token efficiency
skill` as the next section — it dropped 14 of the 51 lines and reported 37; (2) the
duplicate predicate was `t != u and (t == u or t in u)`, self-contradictory, so
exact duplicates were unreachable. Both are the scar class in `AGENTS.md` § Rules:
a configured check is not a verified check.

**And the author of the gate repeated the exact error the gate exists to prevent.**
The first version of `test_audit_agents_md.py` hand-counted its own fixture
(routing 6 / blank 3 / total 14); the script said 7 / 8 / 19. It took a probe to
read the truth, and the tests now carry the script's printed counts with the
comment "derived, not hand-counted". Two consequences kept as rules here: (a)
fixture expectations come from the artifact, never from counting; (b) a column
width is never re-typed in a test either — the `derived_sums` test compares
words, because hand-typed padding failed the same way the hand-count did.

Figures withdrawn across the review's versions, for the record: "working in
production" (no caller anywhere), a token-measurement gate (trivially passes, and
no baseline existed to subtract from), "~35 lines" (block boundaries), "~610
lines" (bytes ÷ an assumed 63 B/line; really 141 + 359 = 500), "22 evidence" (a
hand-split that summed right but mislabelled which lines were which), and "18"
(v6's own defect, three times, no arithmetic path — see
`report_citation_unverified`). Corrected self-claim: v5 said every v4 correction
favoured its candidate; of v4's four, one did.

Next: nothing here. The report lives in-repo at
`docs/reviews/architecture-review-20261003-v7.html`; if `AGENTS.md`'s section is
edited on purpose, run `python scripts/audit_agents_md.py --check`, update
`EXPECTED`, then `--write-block` the report — the gate will refuse anything else.