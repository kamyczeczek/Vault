---
type: Concept
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
disable-model-invocation: true
title: SKILL
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:33Z }
---

# Research

Spin up a **background agent** to do the research, so you keep working while it reads.

## Core principle

Research is a **verification process**, not a search-and-summarize process. The goal is to answer a specific question with evidence, not to collect as much related material as possible.

## Methodology

### 1. Define the question precisely

Before searching, write down:
- The exact question to answer
- What "answered" looks like (verifiable claim or decision)
- What's already known (check existing corpus via `knowledge/graph/ask.py`)

### 2. Check existing coverage first

Before searching external sources:
```bash
python knowledge/graph/ask.py "<topic>" --tag <relevant-tag> --raw
```
If the corpus already covers the question adequately, report that instead of fetching more.

### 3. Search with depth, not just breadth

For each source:
- Read the **original paper/document**, not a summary of it
- Extract: exact claims, methodology, data, limitations
- Note the source with stable identifier (DOI, arXiv ID, URL with date accessed)

### 4. Verify, don't paraphrase

- Cross-check claims across multiple sources when possible
- Flag contradictions explicitly
- Distinguish between:
  - Direct quotes / data from the source
  - Paraphrase of the source
  - Your own interpretation

### 5. Synthesize, don't concatenate

Structure findings by:
- Theme or claim (not by source)
- Confidence level (verified / inferred / speculative)
- Open questions that remain

## Source quality criteria

Prioritize in this order:
1. **Primary sources**: Original papers, official docs, source code, first-party specifications
2. **Peer-reviewed**: Academic papers with DOI, conference proceedings
3. **Authoritative secondary**: Books from reputable publishers, official blog posts from project maintainers
4. **Community**: Well-moderated forums, Stack Overflow with high votes, established technical blogs

Reject or down-weight:
- Marketing copy
- Unverified social media claims
- Outdated documentation (check publication/last-modified date)
- Content farms and AI-generated aggregators

## Output format

Write a single Markdown file with:

```markdown
# [Question]:

## Summary
[2-3 sentence direct answer]

## Evidence

### [Source 1 title]
- **Claim**: [exact finding]
- **Source**: [DOI/URL/stable identifier]
- **Confidence**: [verified / inferred / speculative]
- **Limitation**: [if any]

### [Source 2 title]
...

## Synthesis
[How the evidence connects, contradictions, open questions]

## Open Questions
[What remains unanswered]
```

## Verification checklist

Before delivering:
- [ ] Every claim traces to a specific source
- [ ] Sources are primary or high-trust secondary
- [ ] Existing corpus was checked for prior coverage
- [ ] Contradictions between sources are flagged
- [ ] Confidence levels are assigned
- [ ] File is saved in the repo's established convention for research notes

## Anti-slop guardrails

- **No shallow summaries**: A one-paragraph abstract of a 20-page paper is not research. Extract specific claims, data, and methodology.
- **No source stacking**: Listing 10 sources without reading them is not research. Read the sources, then cite them.
- **No speculation as fact**: Distinguish between what the source says and what you infer.
- **No filler**: If the answer is "no good source exists," say that directly.

## Save location

Match the repo's existing convention for research notes. Common locations:
- `INBOX/<topic_slug>.md` (for raw research awaiting ingestion)
- `research/<topic_slug>.md` (for standalone research)
- `reflection/findings/<topic_slug>.md` (for synthesis output)

If no convention exists, ask where to save it.

## Integration with other skills

- Use **ponytail** to avoid over-researching: stop when the question is answered adequately
- Use **karpathy-guidelines** to avoid scope creep: answer the specific question asked
- Use **grill-with-docs** for deep-dive interviews on a single source
- Use **tdd** for verification: if the research answers a specific question, write a testable claim
- Use the **autonomous research loop** (`python autoresearch_loop.py --mode task --question "..."`) to automate gap detection, literature retrieval, and ingestion end-to-end

## Quality gate enforcement

Before a research note is considered complete:

1. Save the note to `INBOX/` with frontmatter (`title:`, `source:`, `tags:`).
2. Run `python scripts/check_research_quality.py`.
3. Exit 0 means the note passes all checks. Exit 1 means hard errors must be fixed before ingestion. Exit 2 means warnings should be reviewed; the note can still be ingested, but the warnings should be addressed in a follow-up revision.
4. After ingestion, `python scripts/quality_check.py` runs gate `Q12 research_quality` against `INBOX/` automatically. This gate is configured as a warning-level gate: it records metrics but does not fail the overall quality suite.

## Trendable research quality metrics

Run `python scripts/check_research_quality.py --report` to emit baseline metrics in JSON. Track these over time:

- `wdeep_coverage_pct`: percentage of checked files passing W-DEEP depth
- `source_stable_pct`: percentage with stable academic/publisher URLs
- `duplicate_rate_pct`: percentage flagged as duplicates
- `marketing_ese_rate_pct`: percentage with marketing language
- `below_min_length_pct`: percentage below minimum body length

Targets (initial):
- W-DEEP coverage: ≥70% within 30 days
- Stable source identifiers: ≥80% within 30 days
- Duplicate rate: ≤5%
- Marketing language: ≤2%
- Below-minimum length: ≤3%

These targets are enforced as warnings in `check_research_quality.py` and as gate `Q12` in `quality_check.py`. Adjust targets in `check_research_quality.py` constants.