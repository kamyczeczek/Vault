---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Stage 00_expand — Scientific Literature Discovery

Targeted scientific research to broaden knowledge coverage on agentic research methodologies, depositing structured paper summaries into `INBOX/`.

## Inputs
- Topic or research question from `knowledge/topics.md`
- Coverage gaps identified via `knowledge/graph/ask.py`

## Process
1. Inspect current coverage using `python knowledge/graph/ask.py "<topic>"`.
2. Check for duplicates: grep `knowledge/corpus/*.md` and `INBOX/` for the paper title, authors, or arXiv ID. Skip if already covered.
3. Query academic sources (arXiv, OpenAlex, Semantic Scholar, peer-reviewed AI venues) using `scripts/expand_literature.py` or science skills.
4. For each retrieved paper, read the abstract and key sections (methodology, results, limitations). Do NOT ingest based on title alone.
5. Synthesize findings into atomic research documents adhering to the frontmatter schema and W-DEEP technical depth requirements:
   - `title`: paper title and primary findings
   - `source`: DOI or arXiv URL (stable identifier required)
   - `tags`: relevant topic tags from `knowledge/topics.md`
   - Body MUST include: exact algorithms/data structures, threat models, limitations, and how this paper differs from or extends existing corpus coverage
6. Deposit synthesized notes or downloaded paper text into `INBOX/<paper_slug>.md`.

## Outputs
- `INBOX/<paper_slug>.md` (ready for ingestion)

## Invoke

**Manual:**
```bash
python scripts/expand_literature.py --query "autonomous literature search agents" --tags literature-search,scientific-discovery
```

**Autonomous (preferred):**
```bash
python autoresearch_loop.py --mode task --question "<your research question>"
```
The loop performs gap detection → retrieval → ingestion automatically. If sources are unavailable, it generates an escalation request (`INBOX/_pending_request_<ID>.md`) and exits with code 2 for human review.

When materials are delivered (e.g., user places a file in `INBOX/`), re-run the loop — it will detect `_*_delivered.md` files, auto-ingest, rebuild the graph, and continue.

## Contract
- **Source attribution:** Every synthesized document must carry a non-empty `source:` frontmatter field listing arXiv/DOI URLs.
- **Controlled vocabulary:** Tags must match `knowledge/topics.md`.
- **Determinism caveat:** Read the live corpus fingerprint from `knowledge/graph/.graph_fingerprint`.
- **No duplication:** Before depositing, grep `knowledge/corpus/*.md` and `INBOX/` for paper slug, title, or arXiv ID. Duplicates are rejected, not duplicated.
- **Primary-source requirement:** Papers must be read from the source (arXiv abstract page, PDF, or publisher page), not summarized from secondary sources (blog posts, tweets, AI summaries).

## Handoff
Outputs in `INBOX/` feed `stages/01_inbox` (`python scripts/ingest.py`).


## Evolved Protocol Rule (Grounded Multi-Query Decomposition for Literature Retrieval)
<!-- meta-evolved: Grounded Multi-Query Decomposition for Literature Retrieval -->
- **Origin Evidence:** `00_seed_react`, `00_seed_tree_of_thoughts`
- **Requirement:** Before ingesting papers on ambiguous research topics, agents must decompose the query into at least 2 distinct academic search dimensions (e.g. foundational method + empirical validation) to ensure balanced coverage.


## Evolved Protocol Rule (MCTS and Tree-Search Branch Evaluation)
<!-- meta-evolved: MCTS and Tree-Search Branch Evaluation -->
- **Origin Evidence:** `00_self_consistency_and_tree_search_code_generation`, `00_direct_preference_optimization_for_reasoning_age`
- **Requirement:** Complex multi-step reasoning tasks should employ explicit tree-search branch exploration and self-consistency voting prior to finalizing synthesis outputs.

## Evolved Protocol Rule (Research Depth and Source Quality)
<!-- meta-evolved: Research Depth and Source Quality -->
- **Origin Evidence:** `skills/research/SKILL.md`, existing `Mandatory In-Depth Technical Analysis of Sources`
- **Requirement:** Every paper deposited to `INBOX/` must be read from the primary source (arXiv, DOI, publisher page). Agents MUST check `knowledge/corpus/` and `INBOX/` for duplicate coverage before depositing. Papers must be synthesized with technical depth: exact algorithms/data structures, threat models, limitations, and differentiation from existing corpus coverage. Titles and abstracts alone are insufficient.

## Evolved Protocol Rule (Reuse-First Ladder)
<!-- meta-evolved: Reuse-First Ladder (Ponytail) -->
- **Origin Evidence:** `skills/ponytail/SKILL.md`
- **Requirement:** Before writing any new code in this stage's artifacts or supporting scripts, agents must climb the reuse-first ladder: YAGNI → reuse existing codebase → stdlib → native platform → installed dependency → one-line solution → minimum new code. The ladder runs after understanding the problem, never instead of it.

## Evolved Protocol Rule (Root-Cause-Before-Symptom)
<!-- meta-evolved: Root-Cause-Before-Symptom -->
- **Origin Evidence:** `skills/ponytail/SKILL.md`, existing `Root-Cause-Targeted Correction`
- **Requirement:** Bug fixes and root-cause corrections must grep every caller of the function being edited before making changes. A guard in the shared function beats guards in every caller. Patching only the reported path leaves sibling callers broken.
