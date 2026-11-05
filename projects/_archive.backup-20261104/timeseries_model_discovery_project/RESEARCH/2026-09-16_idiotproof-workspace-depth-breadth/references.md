---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Idiotproof Workspace

Flat list of every external source consulted. URL + access date + one-line summary.


## Primary papers (peer-reviewed / arXiv)

1. **Van Clief, J. & McDermott, D. — "Interpretable Context Methodology: Folder Structure as Agentic
   Architecture" (Model Workspace Protocol).** arXiv 2603.16021, 2026-03-17.
   <https://arxiv.org/abs/2603.16021> · accessed 2026-09-16 · *The paper this workspace implements:
   numbered folders as stages, markdown as prompts, local scripts for mechanics; replaces multi-agent
   framework orchestration with filesystem structure.*

2. **He, Y., Zhao, Y., Wang, J. & Chen, H. — "Is Progressive Disclosure All You Need for Long-Context
   Agents?"** arXiv 2607.17598, 2026-07-20.
   <https://arxiv.org/abs/2607.17598> · accessed 2026-09-16 · *First controlled study: progressive
   disclosure buys context not intelligence; a second routing level never helps and can collapse accuracy
   0.91→0.64; flat one-level is decisive at 20-book scale (0.26→0.46).*

3. **Kim, H. et al. — "The Amazing Agent Race: Strong Tool Users, Weak Navigators."** arXiv 2604.10261,
   2026-04. <https://arxiv.org/abs/2604.10261> · accessed 2026-09-16 · *1,400 DAG puzzles; navigation
   errors 27–52% of failures vs tool-use <17%; best agent only 37.2%; linear benchmarks masked the
   weakness entirely.*

4. **Mehtiyev, T. & Assunção, W. — "Beyond Resolution Rates: Behavioral Drivers of Coding Agent Success
   and Failure."** arXiv 2604.02547, 2026-04.
   <https://arxiv.org/abs/2604.02547> · accessed 2026-09-16 · *9,374 trajectories / 19 agents / 500
   tasks; 12 simple-patch tasks never solved by any agent — architectural reasoning gaps, not code
   complexity.*

5. **"Formal Architecture Descriptors as Navigation Primitives for AI Coding Agents."** arXiv 2604.13108,
   2026-04. <https://arxiv.org/abs/2604.13108> · accessed 2026-09-16 · *Explicit architectural context:
   33–44% fewer navigation steps (p=0.009, d=0.92); 100% vs 80% accuracy; 52% less behavioural variance
   across 7,012 Claude Code sessions.*

6. **"Filesystem-Based Memory for LLM Agents: Organization, Evolution, and Sustainability."**
   arXiv 2607.26637, 2026. <https://arxiv.org/html/2607.26637> · accessed 2026-09-16 · *Formalizes agent
   memory as a rooted file hierarchy `(path, description, content)`; agents self-organize into wildly
   different shapes under the same contract; stores consolidate into headings as scale grows; file
   counts misdescribe depth.*


## Secondary / practitioner sources

7. **Anthropic — "The new rules of context engineering for Claude 5 generation models."** 2026-07-24.
   <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models> ·
   accessed 2026-09-16 · ***The counterpoint finding:** removed 80%+ of Claude Code's system prompt for
   Opus 5 / Fable 5 with no measurable loss; diagnosed their own constraints as conflicting and
   overconstraining; constraints were compensating for limitations older models had.*

8. **Gabriel, R. — "The Rise of Worse Is Better."** 1991 (accessed 2026-09-16).
   <https://www.dreamsongs.com/RiseOfWorseIsBetter.html> · *MIT "right thing" vs New Jersey
   worse-is-better: implementation simplicity over interface simplicity; completeness must be sacrificed
   whenever implementation simplicity is jeopardized; better survival characteristics.*

9. **Karpathy, A. — "LLM Wiki."** GitHub Gist, 2026-09-13.
   <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f> · accessed 2026-09-16 · *Raw /
   wiki / schema three-layer knowledge base; index.md + parseable log.md; "Obsidian is the IDE, the LLM
   is the programmer, the wiki is the codebase" — one artifact, two readers.*

10. **Vaughan, D. — "Why Coding Agents Fail at Navigation (and How AGENTS.md File Maps Fix It)."**
    Codex Knowledge Base, 2026-04-19, updated 2026-09-15.
    <https://codex.danielvaughan.com/2026/04/19/why-coding-agents-fail-at-navigation-agents-md-file-maps/>
    · accessed 2026-09-16 · *Synthesizes sources 3–5; adds the 2,500-repo analysis — six effective
    sections, 371-line empirical upper bound, describe-patterns-not-paths, "never commit secrets" as the
    most common helpful constraint; architectural overviews do not reduce navigation time.*

11. **"Convention Over Configuration for Agent Workflows."** Agent Patterns.
    <https://www.agentpatterns.ai/instructions/convention-over-configuration/> · accessed 2026-09-16 ·
    *Every agent choice is a chance for a wrong answer; determinism from inputs removes the need for
    memory of prior choices; rigidity is the cost and signals over-narrow specification.*

12. **"The framework trap: why LangChain, CrewAI, and the next graph abstraction collapse at scale."**
    Prix, 2026-06-03. <https://prix.dev/blog/the-framework-trap/> · accessed 2026-09-16 · *Week-one
    leverage → month-three debugging the framework instead of the agent; three failure modes (abstraction
    mismatch, frozen-too-early mental model, observability loss); the simplest loop wins after rewrite.*

13. **"Context Engineering Techniques: Progressive Disclosure vs RAG for Skill Library Design."**
    Traversaal, 2026-09-10. <https://blog.traversaal.ai/context-engineering-techniques-progressive-disclosure-vs-rag-skill-library-design/>
    · accessed 2026-09-16 · *The invocation boundary: instructions load only at invocation; RAG surfaces
    evidence fragments while Skills deliver complete self-contained operating instructions.*

14. **SkillFed Research — "Flat skill packs lift 20-book QA accuracy from 0.26 to 0.46."** 2026-07-25.
    <https://skillfed.io/research/flat-skill-packs-lift-20-book-qa-accuracy-from-0-26-to-0-46-a-second-routing>
    · accessed 2026-09-16 · *Accessible summary of source 2's numbers with the caveats stated plainly:
    English open-QA only, MC subset has a pretraining confound.*

15. **Warden, J. — "Type Driven Development: Total Function."** 2026-06-01.
    <https://jessewarden.com/2026/06/type-driven-development-total-function.html> · accessed 2026-09-16 ·
    *Partial vs total functions; "ensure the inputs are good instead" — making impossible states
    impossible rather than handling bad input at runtime.*

16. **ktnCodes/icm-template.** GitHub.
    <https://github.com/ktnCodes/icm-template> · accessed 2026-09-16 · *Public ICM scaffold: the five
    layers with their token budgets (800 / 300 / 200–500 / 500–2k / varies); "the LLM is a compiler, not a
    chatbot"; quick mode 3 layers vs full mode 5 layers.*


## Sources internal to this workspace (cited in findings as local evidence)

17. **`scripts/check_stage_contracts.py`** — the gate that refuses a bare 12-hex fingerprint literal in a
    stage contract; cited in findings §6 as an existing total-function constraint. Local path.

18. **`stages/04_reflect/CONTEXT.md`** — the stage contract whose "single disclosure level (one-level
    progressive disclosure)" rule is the subject of findings §4. Local path.
