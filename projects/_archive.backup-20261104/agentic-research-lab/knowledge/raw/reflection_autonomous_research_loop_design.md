---
type: Concept
id: reflection_autonomous_research_loop_design
title: "Design: Autonomous Research Loop with Knowledge-Gap Detection & Material Request"
source: "reflection_autonomous_research_loop_design.md"
tags: [reflection, autonomous-research, workflow]
trust_tier: 1
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Design: Autonomous Research Loop with Knowledge-Gap Detection & Material Request

## 1. Motivation

The lab's current pipeline is **reactive**: tasks arrive, stages process, and literature expansion runs manually (`scripts/expand_literature.py --query ...`). There is no automated mechanism for the lab to *notice* when its knowledge corpus lacks coverage for a topic it is investigating, fetch the relevant material, and—if retrieval fails—ask the human for the source.

An autonomous research loop closes that gap by embedding **gap detection**, **retrieval**, and **escalation** into the pipeline itself.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Pipeline Controller                    │
│  (autoresearch_loop.py / stage runners)             │
└──────────┬──────────────────────────────────────────┘
           │ On task receipt / periodic tick
           ▼
┌─────────────────────────────────────────────────────┐
│  Phase 0: Knowledge-Gap Detector                    │
│  (knowledge_gap_detector.py)                        │
│  - Compare task question against corpus via ask.py  │
│  - Score: coverage_score ∈ [0,1]                    │
│  - If score < threshold → emit gap record           │
└──────────┬──────────────────────────────────────────┘
           │ Gap detected
           ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: Intelligent Retrieval                     │
│  (autonomous_retriever.py)                          │
│  - Query expand (vocabulary synonyms, multi-query)  │
│  - Fan out to arXiv API / Jina Reader / web search  │
│  - Deduplicate against existing corpus              │
│  - Score results by relevance + source quality      │
└──────────┬──────────────────────────────────────────┘
           │ Top result: coverage_score < MIN_COVERAGE
           ▼
┌─────────────────────────────────────────────────────┐
│  Phase 2: Material Request                          │
│  (material_request.py)                              │
│  - Build structured request: topic, what's missing,  │
│    why it matters, suggested sources                 │
│  - Post to user via console / file marker            │
│  - Poll for material delivery                        │
└──────────┬──────────────────────────────────────────┘
           │ User provides URL / file
           ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: Ingest & Evict                            │
│  (re-ingest through existing pipeline)               │
│  - deposit → INBOX/<slug>.md                       │
│  - run check_research_quality.py                   │
│  - ingest via scripts/ingest.py                     │
│  - rebuild graph                                    │
└─────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 Knowledge-Gap Detector (`knowledge_gap_detector.py`)

Inputs: `task_question` (string), optional `topic_tags`
Outputs: `GapRecord`

```python
@dataclass
class GapRecord:
    question: str
    coverage_score: float       # 0..1, from ask.py top-k recall
    missing_evidence: list[str] # chunk ids that partially match but lack depth
    tags: list[str]             # topics that should cover this
    severity: str               # "high" | "medium" | "low"
```

**Algorithm:**
1. Run `ask.py "<question>" --limit 10`
2. Count: total chunks returned vs. expected minimum (5)
3. For each top chunk, check if it contains *deep* signal (technical terms, methods, data)
4. Coverage score = `min(1.0, len(deep_chunks) / expected_min)`
5. Severity: high if score < 0.3, medium if < 0.6, low otherwise

**Existing reuse:** This calls the same `knowledge/graph/ask.py` that already powers the ICM context gateway. No new retrieval engine needed for the detector.

### 3.2 Autonomous Retriever (`autonomous_retriever.py`)

Leverages existing infrastructure:
- **arXiv API**: `scripts/expand_literature.py::fetch_arxiv()` — already has multi-query fan-out
- **Jina Reader**: `curl https://r.jina.ai/<URL>` — working backend per prior session
- **Web search**: Reuses `agent-reach` patterns (Exa-backed via mcporter)

New logic added:
- **Intelligent query decomposition**: Given a question like "how do agents handle knowledge gaps", split into:
  1. Foundational: "knowledge gap agent systemat review"
  2. Technical: "LLM self-directed research loop architecture"
  3. Applied: "autonomous literature discovery agent implementation"
- Each sub-query sent in parallel; results deduplicated by title + author fingerprint
- **Source quality scoring**: Primary source (arXiv/DOI) > authoritative blog > secondary summary

### 3.3 Material Request Generator (`material_request.py`)

When retriever returns no adequate sources:

```markdown
## Research Gap Escalation

**Question being investigated:** {task_question}

**Why this matters:** {1-2 sentence justification tied to current task goals}

**What we need:**
- {specific paper/topic, e.g., "A 2024–2026 paper on autonomous research loops"}
- OR a URL / PDF that covers the topic

**Suggested sources to look for:**
- arXiv query: "{expanded_query}"
- GitHub repos: "{keyword} autonomous research"

**Impact of not having this:** {brief note}
```

Output format: written to `INBOX/_pending_request_<timestamp>.md` AND printed to stdout so the pipeline controller can surface it to the user.

### 3.4 Integration Points

| Existing Module | Integration Change |
|----------------|-------------------|
| `autoresearch_loop.py` | Add `run_gap_detection()` call after manifest check, before graph build |
| `stages/00_expand/CONTEXT.md` | Replace manual invocation with auto-trigger on any stage producing a task |
| `pipeline/06_reflect/` | Feed discovered gaps into reflection candidates for future memory updates |
| `skills/research/SKILL.md` | Add "autonomous mode" branch where researcher auto-triggers gap detection |
| `knowledge/graph/ask.py` | Expose `--json` flag for programmatic coverage scoring (optional enhancement) |

---

## 4. Trigger Modes

### Mode A: Task-Prompted (primary)
When a new task enters `inbox/`, run gap detection *before* starting research. If gap is severe (score < 0.3), escalate immediately.

### Mode B: Stage-Triggered (opportunistic)
At the end of each stage run (expand → corpus → graph → reflect), query: *"Does the current corpus adequately cover the topics flagged in today's frontier turns?"* If coverage drops below threshold, trigger a targeted retrieval round.

### Mode C: Periodic Health Check (background)
A cron-like scheduler (or the next `autoresearch_loop.py` invocation) re-runs gap detection across all topics in `knowledge/topics.md`. Finds dormant gaps that accumulate over time.

---

## 5. Escalation Protocol

The user-request protocol must be unambiguous so the human knows exactly what to provide:

1. **Structured format** — Use a fixed markdown template (see §3.3)
2. **Minimal ask** — Only request the *most critical* missing piece, not everything unknown
3. **Auto-resume** — After delivering material (URL or file path), the loop should automatically retry retrieval and proceed without manual intervention
4. **Timeout** — If no response within N hours, degrade gracefully: continue with available knowledge and note the limitation in the task output

---

## 6. Implementation Plan (ordered by dependency)

1. **`knowledge_gap_detector.py`** — Standalone, tests against existing `ask.py`
2. **`autonomous_retriever.py`** — Wraps `expand_literature.py`, adds query decomposition
3. **`material_request.py`** — Template rendering + file I/O
4. **Integration into `autoresearch_loop.py`** — Wiring the phases
5. **`scripts/run_autonomous_research.py`** — Entry point with mode flag (`--mode task|periodic`)
6. **Documentation update** — Add to `stages/00_expand/CONTEXT.md` and `skills/research/SKILL.md`

Estimated effort: 4–6 hours for MVP; 8–12 for full integration with escalation polling.
