---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Idiotproof Workspace: Depth, Breadth, Simplicity

<!-- Every claim cited to a URL, file path, or local document. No unsourced claims.
     Stop on contradiction: record both sides, route the conflict to the user;
     do not pick a side silently. -->


## 1. The architecture this workspace uses has a name and a paper

**Interpretable Context Methodology (ICM)** / Model Workspace Protocol (MWP). Van Clief & McDermott,
arXiv 2603.16021, 2026. The abstract states the trade precisely: multi-agent frameworks "work well for
complex, concurrent systems. But for sequential workflows where a human reviews output at each step, they
introduce engineering overhead that the problem does not require." MWP replaces framework-level
orchestration with **filesystem structure**: numbered folders are stages, plain markdown carries the prompts
and context, local scripts handle mechanical work that needs no AI at all.
<https://arxiv.org/abs/2603.16021>

The design lineage is explicit in the paper: Unix pipeline design, modular decomposition, multi-pass
compilation, and literate programming. This matters for the "idiotproof" question — the pattern inherits
from Unix, which is a *worse-is-better* lineage (see §5), not a right-thing lineage.

A public implementation exists as a skill-based scaffold: `IDENTITY.md` (Layer 0, "Where am I?", ~800
tokens) + root `CONTEXT.md` (Layer 1, "Where do I go?", ~300 tokens) + stage `CONTEXT.md` (Layer 2,
"What do I do?", 200–500 tokens) + `_config/` (Layer 3, "What rules apply?", 500–2k tokens) + `output/`
(Layer 4, "What am I working with?"). Its stated budget: "typically 2,000–8,000 focused tokens instead of
a bloated 30,000–50,000 token monolithic prompt."
<https://github.com/ktnCodes/icm-template>


## 2. The token claim is real and it is *prevention, not compression*

The ICM paper measures it. Layers 0–2 deliver roughly **1,300–1,600 tokens** of identity, routing, and
stage instruction. Layer 3 adds 500–2,000 tokens of reference material. Layer 4 adds working material,
"rarely exceeding a few thousand tokens when the previous stage has done its job of condensing and
structuring." Total per stage: **2,000–8,000 tokens**. The monolithic alternative: **30,000–50,000
tokens**, "most of it irrelevant to the current task."
<https://arxiv.org/html/2603.16021v2>

The mechanism is stated as a deliberate choice: *"a simpler approach is to avoid loading irrelevant context
in the first place. Stage-specific context loading, where each stage only sees the files it needs, prevents
the problem rather than treating it after the fact."* This is positioned against Jiang et al.'s prompt
compression (up to 20× token reduction with minimal loss) — ICM says don't compress, just don't load.

The underlying reason is Liu et al. (2024): models perform significantly worse when relevant information is
buried mid-context. More irrelevant material → worse performance on what matters. Cited as `liu2024`
within the ICM paper.


## 3. Navigation is the dominant agent failure mode — and folder contracts fix it measurably

Three April-2026 studies converge, summarized with full citations at
<https://codex.danielvaughan.com/2026/04/19/why-coding-agents-fail-at-navigation-agents-md-file-maps/>:

- **The Amazing Agent Race** (Kim et al., arXiv 2604.10261): 1,400 DAG puzzles. **Navigation errors account
  for 27–52% of all trial failures**; tool-use errors stayed **below 17%**. Best agent: only 37.2%
  accuracy. Linear benchmarks *masked the weakness entirely* — it only appeared with branching paths.
  <https://arxiv.org/abs/2604.10261>
- **Beyond Resolution Rates** (Mehtiyev & Assunção, arXiv 2604.02547): 9,374 trajectories, 19 agents, 8
  frameworks, 14 LLMs, 500 tasks. 12 tasks never solved by *any* agent despite needing only simple
  patches — difficulty was **architectural reasoning gaps, not code complexity**.
  <https://arxiv.org/abs/2604.02547>
- **Formal Architecture Descriptors** (arXiv 2604.13108): explicit architectural context **reduces
  navigation steps by 33–44%** (Wilcoxon p=0.009, Cohen's d=0.92). Auto-generated descriptor hit **100%
  accuracy vs 80% unaided** (p=0.002). Across **7,012 Claude Code sessions**, a **52% reduction in agent
  behavioural variance**. <https://arxiv.org/abs/2604.13108>

**The design rule that falls out:** a `CONTEXT.md` in every folder is not documentation — it is the
intervention that removes the exploration phase. An agent that reads a stage contract has been handed the
map instead of having to draw one. The variance reduction is the part that matters for "idiotproof":
same input → same navigation, across 7,012 sessions.


## 4. One level of disclosure is enough. Two levels is measurably worse.

The single most design-constraining finding. First controlled study of progressive disclosure for
agentic long-document reasoning, across 3 harnesses (Codex, Pi, Claude-Code) × 3 model families on
InfiniteBench. <https://arxiv.org/abs/2607.17598>

- **Single book:** the gain depends entirely on the harness. Large when the agent navigates raw text poorly
  (Pi, Claude-Code); **near zero under Codex**, whose bare agent already greps the named entities and reads
  only matched passages. Progressive disclosure "buys context, not intelligence."
- **Multi-book (20 books):** raw navigation **collapses to 0.26** on English open-book QA while flat
  one-level disclosure holds at **0.46** — a rescue that reproduced across 2 harnesses and 2 model
  families. Flat summary at <https://skillfed.io/research/flat-skill-packs-lift-20-book-qa-accuracy-from-0-26-to-0-46-a-second-routing>
- **Second routing level: never helps, sometimes breaks.** A hierarchical pack where every chunk becomes
  its own skill under a meta-router: one Pi/model pairing saw **multiple-choice accuracy collapse 0.91 →
  0.64**. The stated reason is the exact thing a deep folder tree recreates: *"the always-loaded child
  descriptions eat exactly the context budget the structure was meant to save."*

**Implication for this workspace:** the "single disclosure level" rule is the empirically load-bearing
constraint. Depth of folders must be bought deliberately, one level at a time, because the second routing
tier has a demonstrated failure mode that is *worse than having no structure at all*.

**Caveats recorded by the authors:** gain is sharpest on English open-QA and largely absent on Chinese QA
(where the base model sets the ceiling). Multiple-choice subset carries a pretraining confound — canonical
novels the models likely already know. "Read the 0.26-to-0.46 rescue as an open-QA, English-language
result, not a blanket endorsement."


## 5. The simplicity lineage: worse-is-better, and it survived

Richard Gabriel, "The Rise of Worse Is Better." The two philosophies differ on *which* simplicity matters:
<https://www.dreamsongs.com/RiseOfWorseIsBetter.html>

- **MIT / "the right thing":** simplicity in *interface* matters more than implementation; correctness is
  non-negotiable; consistency may be bought with simplicity; completeness must not be sacrificed.
- **New Jersey / worse-is-better:** **implementation simplicity matters more than interface simplicity.**
  "It is slightly better to be simple than correct." Consistency can be sacrificed for simplicity.
  **"Completeness must be sacrificed whenever implementation simplicity is jeopardized."**

Gabriel's own conclusion after watching both play out: *"worse-is-better, even in its strawman form, has
better survival characteristics than the-right-thing."* Early Unix and C delivered "about 50%–80% of what
you want" and won.

**Why this is the right frame for "idiotproof":** the Unix approach made the *system* simple enough that a
mediocre programmer could hold it in their head and recover from failure — the error-code-and-retry story
Gabriel recounts is literally about making the *wrong state recoverable* rather than impossible. That is a
different idiotproofing strategy from "make wrong states unrepresentable" (§6), and the two are in tension.


## 6. Making wrong states impossible — the complementary strategy

"Making Impossible States Impossible" as a design principle. The mechanism is narrowing types so that
invalid input cannot be expressed, rather than handling it at runtime.
<https://jessewarden.com/2026/06/type-driven-development-total-function.html>

The useful contrast: a *partial function* throws or returns nonsense for some inputs (division by zero);
a *total function* returns a sensible value for every input. Two ways to get there — handle the bad case
(`Result` type, error checking "Blech... math requires error checking now?"), or **"ensure the inputs are
good instead"** so the bad case cannot occur.

**Mapping to a workspace:** an `INBOX/` that must be empty at session close is a total-function constraint
— there is no valid end state with stale intake. A corpus chunk whose `id` must equal its filename stem is
the same kind of constraint. This is the *strong* form of idiotproofing: structure so the error cannot be
written, rather than auditing for it after. This workspace already does it; the corpus fingerprint gate
(`check_stage_contracts.py` refusing a bare 12-hex literal) is a total-function constraint on contracts.


## 7. THE FINDING THAT POINTS THE OTHER WAY — the frontier is deleting context

This is the most important result in the whole body of research, and it is a caveat on everything above.

Anthropic, on prompting Claude 5-generation models (Opus 5, Fable 5):
<https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>

> "We removed over 80% of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5
> with no measurable loss on our coding evaluations."

Their diagnosis of what they had wrong: *"we were overconstraining Claude Code, both through our system
prompt and in our CLAUDE.md files and skills."* They found **conflicting messages in a single request** —
"leave documentation as appropriate" vs "DO NOT add comments" — as system prompt, skills, and user requests
clashed. Their conclusion: *"while these constraints were once needed to avoid worst case scenarios, we
have since found we can delete many of them and let the model use surrounding context and judgement
instead."*

They also note the *reason* the old guardrails existed: without them, older models wrote comments that
were frequently incorrect. **The constraint was compensating for a model limitation that no longer holds.**

**Tension with §2/§3:** the layered-context results (2k–8k tokens beats 30k–50k) were measured against a
world where more organization beat less. Anthropic's result says the ceiling itself has moved — for
frontier models, *less context, fewer rules* is now the better-organized option. A `CONTEXT.md` in every
folder is a cost, and the cost is rising as models get better at finding things themselves.

**The honest read:** structure compensates for navigation weakness (§3, measured at 33–44% fewer steps).
But constraints that a model could satisfy on its own are now net-negative. The design question is not
"how much structure" but "which of my constraints are compensating for a limitation that no longer
exists?" — and that set grows with every model generation.


## 8. Convention over configuration — idiotproofing by removing the decision

"Every choice an agent makes is a chance for a wrong answer... When the answer is not obvious, an agent
guesses. Inconsistent guesses compound over time into a codebase that is hard to navigate."
<https://www.agentpatterns.ai/instructions/convention-over-configuration/>

The mechanism is **determinism from inputs**: "When naming and placement are deterministic — derivable
from the issue number, content category, or file type — an agent needs no context about what previous
agents chose, because the answer is **discoverable from the inputs rather than remembered**."

The stated boundary is the useful part: *"Conventions reduce decision errors but introduce rigidity. A
convention that requires exceptions at every turn is a signal it was specified too narrowly."* Enough
convention to eliminate common decision points; enough flexibility for edge cases without breaking the
scheme.

This is the idiotproofing lever that is *not* in tension with §7: a deterministic filename rule costs
nothing at inference and removes a whole class of guesses. It survives model improvement.


## 9. Karpathy's LLM knowledge base — the read/write asymmetry

<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

Three layers: **raw sources** (immutable, "the LLM reads from them but never modifies"), the **wiki**
(LLM-owned markdown: summaries, entity pages, concept pages, synthesis — "You read it; the LLM writes
it"), and the **schema** (CLAUDE.md/AGENTS.md — "what makes the LLM a disciplined wiki maintainer rather
than a generic chatbot").

Key operational details: `index.md` is content-oriented (catalog with one-line summaries; "works
surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and **avoids the need for
embedding-based RAG infrastructure**"); `log.md` is chronological and append-only, and if each entry
starts with a consistent prefix it becomes **parseable with simple unix tools**.

**The line that matters for a workspace serving a human and an agent:** *"Obsidian is the IDE; the LLM is
the programmer; the wiki is the codebase."* Same artifact, two entirely different access patterns — the
human browses links and graph view, the agent edits files. This is the depth/breadth answer: **one
artifact, two readers, no duplication.** Progressive disclosure serves the agent; interlinked pages serve
the human; they are the same files.


## 10. The filesystem is where practice actually converged — and it self-organizes unpredictably

arXiv 2607.26637 formalizes agent memory as a rooted path hierarchy of files, each a triple
`(path, description, content)`. "Folders are the shared prefixes of paths and carry no content of their
own." The formalization deliberately mirrors deployed practice: Anthropic's memory tool exposes memory as
"a directory of files behind six generic file operations." <https://arxiv.org/html/2607.26637>

The counterintuitive empirical result — **agents left to organize do not agree on a shape, and the
disagreement is not noise:**

- Under one model, LoCoMo put nearly all hierarchy *inside files* (3 files, 116 headings, depth 5,
  cross-linked by 151 in-store pointers). REALTALK did the opposite: 41 topic files in 2 folders, nearly
  flat inside. **Both satisfied the same taxonomy contract.**
- **Scale makes stores consolidate, not shard:** going from 32k to 128k (~55 → 271 chunks) moved hierarchy
  *out of* folders and files *into* headings — 3 folders/12 files → 1 folder/2 files, sections 53 → 210.
- **The model changes the shape by an order of magnitude:** the same 128k conversation became **122 files
  in 12 folders under nano, 2 files under mini, 105 files in 4 folders under gpt-5.4.**
- **File counts misdescribe organization:** the "two-file" store was depth 6, mean fanout 11 — *deeper
  than most many-file stores.*

**Implication for "different levels of depth and breadth":** depth is not a property you design once.
What reads as "flat" at the file layer can be deep at the heading layer, and agents will reorganize across
those layers as volume grows. A workspace contract should therefore state its *invariants* (chunk id ==
filename stem; INBOX empty at close) and let shape migrate, rather than fixing the shape.


## 11. The framework trap — simplicity as the end state, not the starting state

<https://prix.dev/blog/the-framework-trap/>

The failure trajectory: "Week one: LangChain, CrewAI, or the new graph abstraction feels like leverage...
Month three: the team is debugging the framework instead of the agent." The diagnosis: *"The framework is
not helping you survive complexity. It is creating a second system you now have to understand before you
can touch your own product."*

Three named failure modes, each relevant to a folder-contract workspace:

1. **Abstraction mismatch.** A support agent starts as four nodes; then retries, approval, human review,
   conditional tool ordering. "The graph grows, but the core behavior does not get clearer. It gets harder
   to inspect."
2. **Wrong mental model, frozen too early.** "Framework authors keep trying to freeze the right
   abstraction one year before the model vendors change the primitive." Chains → graphs → role-playing
   agents → subagent planners, "while the model APIs keep collapsing toward the same boring shape:
   messages in, tools out, structured output back."
3. **Observability loss.** *"The worst production bug is not a crash. It is a bad decision you cannot
   explain."* Once a prompt is assembled through templates, wrappers, middleware, memory injection,
   callback managers, and hidden retries, "you lose the one thing agent systems demand: a clean view of
   what the model actually saw and why it chose the tool it chose."

**Why ICM is on the right side of this:** plain markdown in numbered folders is the "boring shape." There
is no wrapper layer to debug — a stage contract *is* the prompt, in a file, readable by both the human and
the agent. The framework-trap critique is an argument *for* filesystem structure, and it is the strongest
such argument found.


## 12. What an effective file map actually contains — measured, not guessed

Analysis of **2,500+ repositories** with `AGENTS.md` files identified six sections that consistently
appear in high-performing configurations. <https://codex.danielvaughan.com/2026/04/19/why-coding-agents-fail-at-navigation-agents-md-file-maps/>

1. **Commands** — executable build/test/lint commands with full flags, placed early
2. **Testing protocols** — how and where to run tests
3. **Project structure** — the file map
4. **Code style** — "one representative code snippet beats three paragraphs of description"
5. **Git workflow** — branch naming, commit conventions
6. **Boundaries** — what the agent should never touch

**Anti-patterns, with measured bounds:**

- **Over-documentation:** the `maas` repository's **371-line AGENTS.md is the empirical upper bound**
  before splitting into nested files becomes necessary.
- **Static path lists are brittle:** listing `src/api/users.ts`, `orders.ts`, `products.ts` "breaks when
  files change." Describe capabilities and patterns instead: "`src/api/` — one handler file per resource."
- **Missing boundaries:** "Never commit secrets" is *the most common helpful constraint* across all 2,500+
  repos. "Without explicit boundaries, agents will happily modify `.env` files, vendor directories, and
  production configurations."

**Notably, architectural overviews do NOT reduce navigation time** — what works is "a concise, functional
map that tells the agent where things live and what they do."


## 13. Cross-cutting synthesis: what "idiotproof" actually means here

Three strategies were found, they are **not** the same thing, and two of them are in tension:

| Strategy | Mechanism | Cost | Model-proof? |
|---|---|---|---|
| **Remove the decision** (§8) | deterministic naming/placement; answer derivable from inputs | ~0 at inference | **Yes** — survives model improvement |
| **Make wrong states impossible** (§6) | structure so invalid input can't be written | rigid; narrows expressiveness | **Yes** — invariant, not inference |
| **Pre-load the map** (§3) | `CONTEXT.md` per folder; agent reads instead of explores | tokens per stage; maintenance | **No** — §7 shows this cost is rising |

The first two are permanent wins. The third is the one that has to be **justified per folder**, because
Anthropic's 80% deletion result means its value is depreciating against model capability. The design
implication is concrete: **put a contract where navigation is genuinely hard, not everywhere.** An
`INBOX/` contract that must be empty at close (§6) and a deterministic chunk-id rule (§8) do more
idiotproofing than ten descriptive `CONTEXT.md` files whose content a frontier model could derive by
listing the directory.

The deepest tension in the research: §10 shows agents reorganize hierarchy as volume grows, and §4 shows a
second routing level can *collapse* accuracy. So a workspace that wants to stay idiotproof should fix
**invariants, not shape.**
