---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Antifragile Workspace Design

All sources are local documents delivered via `INBOX/` on
2026-09-05 (the user's research commission). Originals are
preserved in this record's `sources/` folder (moved from INBOX per
Rule 5). Access date = 2026-09-05 for every entry.

1. **Workspace Optimization: How to Train Your Agent** — Sarafian,
   Kaplun, Banner (NVIDIA), Soudry (NVIDIA & Technion), Ginsburg
   (NVIDIA). arXiv:2605.09650v1, 10 May 2026. 3 pp.
   Workspace optimization: frozen-model agents adapt by editing a
   structured workspace of typed artifacts; DREAMTEAM ARC-AGI-3
   36%→38.4% RHAE at −31% actions.
   `sources/Workspace_Optimization.pdf`

2. **Memento-Skills: Let Agents Design Agents** — Memento-Team.
   arXiv:2603.18743v1, 19 Mar 2026. 1 p. (extended abstract with
   results). Agent-designing agent; skills as persistent evolving
   memory; Read–Write Reflective Learning; GAIA +26.2%, HLE
   +116.2% relative. Code: github.com/Memento-Teams/Memento-Skills.
   `sources/Memento-Skills Let Agents Design Agents.pdf`

3. **Interpretable Context Methodology: Folder Structure as Agent
   Architecture** — Van Clief, McDermott (Eduba, University of
   Edinburgh). arXiv:2603.16021v2, 18 Mar 2026. 1 p. (+4 shown).
   ICM: filesystem structure replaces framework orchestration for
   sequential human-reviewed workflows; control-surface comparison.
   Protocol: github.com/RinDig/Interpretable-Context-Methodology-ICM
   (MIT).
   `sources/Interpretable Context Methodology Folder Structure as Agent.pdf`

4. **Atomic Agents: a harness-agnostic standard for AI agents that
   live as text** — Marcos Emowe, v1.0, production since Aug 2026.
   Profiles/skills/cards/board/dispatcher/vault; blind
   deterministic matching; state-is-the-folder; every scar ends in
   a test. emowe.com/cerebro-digital/por-que-atomizamos.
   `sources/common_problems_solutions/Atomic Agents a harness-agnostic standard for AI agents that live as text.md`

5. **How I keep my AI workspace clean, accurate, and safe** —
   practitioner post (author unnamed in file). Two session rituals:
   initialization (read handoff first, load only what's needed, hard
   rules every time) + handoff (update state, run tests, tag
   known-good). Token budgets for init (5–10k).
   `sources/common_problems_solutions/How I keep my AI workspace clean accurate and safe.md`

6. **Intent is Everything — Agentic Operator Report** — practitioner
   post. Intent.md-first SDLC: discovery→spec→plan→test→deploy→
   maintenance loops back to a new intent on error.
   `sources/common_problems_solutions/Intent is Everything - Agentic Operator Report.md`

7. **Stopping Conflicting Saves From Multiple Agents** — Polish-
   language practitioner analysis of multi-agent git safety.
   Instruction vs mechanism; layered enforcement (worktree →
   startup check → hook → approval layer → CI); "hook exists" ≠
   "hook works" (adversarial testing required).
   `sources/common_problems_solutions/Stopping Conflicting Saves From Multiple Agents.md`

8. **How to Use AI as a Team** — implementation-oriented adaptation
   of Tal Raviv, "How to use AI as a team" (April 2026,
   talraviv.co). 16 sections; org-context levels; instruction file
   as product; compounding-knowledge thesis.
   `sources/common_problems_solutions/How to Use AI as a Team.md`

9. **Agent memory — OpenAI Agents SDK** (v0.22.0 docs page,
   saved HTML). Sandbox Memory capability (beta): memory as
   workspace files separate from session memory; two-phase
   generation (conversation extraction → layout consolidation);
   layout-config memory isolation.
   `sources/Agent memory - OpenAI Agents SDK.html` (+ `_files/` assets)

10. **microsoft/skillopt repo pack** (435 files, 4.3 MB, 1.1M tokens
    — sampled, never bulk-loaded). SkillOpt: the skill document as
    trainable state of a frozen agent; optimizer model + held-out
    validation gating + textual learning-rate budget; 52/52
    best-or-tied cells across 6 benchmarks × 7 models × 3
    harnesses. arXiv:2605.23904; microsoft.github.io/SkillOpt.
    Includes technical blog: "Expanded SkillOpt Ablations,
    Skill-Aware Reflection, and SkillOpt-Sleep" (Zhou, Gong, Yang,
    July 14 2026; 499 analyzed runs).
    `sources/skillopt.txt`

11. **glitch-cat-club/chief-of-staff-crew repo pack** (16 files,
    9.0k tokens). Five text files orchestrate a chief + 4
    specialists; each owns its files; auditor checks-and-fixes-
    nothing.
    `sources/glitch_cat_club/chief-of-staff-crew.txt`

12. **glitch-cat-club/graph-memory-starter repo pack** (53 files,
    19.8k tokens). Corpus→digest→graph knowledge memory with
    session-end hooks. Already analyzed in record R-02
    (2026-09-03_knowledge-architecture-research); referenced, not
    re-derived.
    `sources/glitch_cat_club/graph-memory-starter.txt`

13. **glitch-cat-club/prompt-router-starter repo pack** (66 files,
    131.4k tokens). Deterministic prompt-shape routing + Stop gate
    refusing false done. Already in R-02.
    `sources/glitch_cat_club/prompt-router-starter.txt`

14. **ICM expansion documents** (3 files, slice-verified NOT in
    icm_brain corpus 2026-09-05 23:20Z — new material, candidate
    future corpus chunks):
    - `sources/ICM_map.md` — methodology mindmap (7 sections).
    - `sources/One Stage, One Job.md` — single-responsibility-per-
      folder principle expansion (8 sections incl. compiler
      analogy, stage sizing, when to bend).
    - `sources/Plain Text as Interface.md` — markdown/JSON as
      universal communication layer (5 sections incl. no-database
      principle, literate programming).
    Plus `sources/ICM_knowledge_big.md` (935 KB merged-notes
    collection, "part 1") — VERIFIED duplicate of the existing
    icm_brain corpus (slice probes 2026-09-05 23:17Z: mid-doc and
    5k-offset slices both present in corpus blob; corpus holds it
    as 96 chunks). Preserved for provenance; not re-ingested.

**Internal cross-references (workspace's own graph, queried not
re-read):**
- `RESEARCH/2026-09-03_knowledge-architecture-research/` (R-02) —
  inject-vs-query, multi-brain management, hook roles; the
  hybrid-injection doctrine this record builds on.
- `brains/reflection_brain/` scar corpus (74 scars) — prior
  positions checked per cluster (see claims_ledger.md graph
  checks).
- `brains/icm_brain/` corpus (ICM practice library) — duplicate
  check + context for clusters C/E/H.
