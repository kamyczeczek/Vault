---
type: Concept
title: claims_ledger
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Claims Ledger — Antifragile Workspace Design

<!-- Graph-fed ledger (user-directed method, 2026-09-05 23:23–23:30).
     Each source is reduced to provenance-tagged claims (C-NN).
     Before/while appending a cluster, the workspace's own graphs are
     queried (icm_brain = methodology corpus, reflection_brain = scar
     corpus) for prior positions; agreements and tensions are recorded
     as AGREE/CONFLICT/EXTEND entries. Sources are NEVER bulk-loaded
     into session context: big files (skillopt.txt 4.3MB,
     ICM_knowledge_big.md 935KB) enter only via strategic sampling +
     ask.py passage queries. Provenance key: [SRC] = INBOX filename. -->

## Cluster A — Workspace as the trainable state (frozen weights)

- **A1.** The agent's trainable state, when weights are frozen, is the
  workspace: the structured external substrate it reads, writes, and
  tests. Evolution of this substrate = "workspace optimization",
  mirroring weight-space training: artifacts↔parameters, evidence↔data,
  counterexamples↔losses, textual feedback↔gradients.
  [Workspace_Optimization.pdf, NVIDIA, Sarafian/Kaplun/Banner/Soudry/Ginsburg, p.1 §1, p.2 §2.1]
- **A2.** The workspace is not merely memory: it is the machinery that
  decides which observations turn into state, which predictions get
  logged as commitments, and which surprises change future behavior.
  [Workspace_Optimization.pdf, p.2 §1]
- **A3.** Credit assignment is the interesting question: when something
  goes wrong, WHAT gets fixed. Failures must be routed to the artifact
  responsible — misreading what is happening vs mispredicting what will
  happen call for different fixes. Each prediction is emitted by one
  specific interface, so the failure carries the interface's name:
  attribution is an addressing decision, not a similarity retrieval.
  [Workspace_Optimization.pdf, p.2 §2.2, p.2 Contributions]
- **A4.** Every accepted patch is replayed against a retained
  regression set of past transitions BEFORE the next step — a revision
  must remain consistent with prior evidence, not just fix the current
  outcome. Regression breakage becomes a new counterexample for the
  responsible role.
  [Workspace_Optimization.pdf, p.3 §2.1 Evaluation]
- **A5.** DREAMTEAM (six roles: Observer/Simulator/Inductive
  Explorer/Transductive Explorer/Critic/Team Leader, each owning
  exactly one typed surface) improved protocol-matched ARC-AGI-3 SOTA
  from 36% to 38.4% RHAE while using 31% FEWER environment actions per
  game (444 vs 643, mean of 2 runs, 25-game public set).
  [Workspace_Optimization.pdf, p.1 Abstract + p.2 Contributions]
- **A6.** Role-granularity tradeoff: too coarse = one role carries
  everything (per-call cognitive load on every surface); too fine =
  inter-role hand-offs and audits eat the wall-clock budget that
  should pay for real actions. They settled on six roles split along
  "maintaining the world model" vs "acting through it".
  [Workspace_Optimization.pdf, p.3 §3]

### Graph check A (2026-09-05 23:32Z)
- `icm_brain ask "antifragile workspace design..."` → surface hits only
  (level taxonomy, workspace setup for context) — no prior position on
  trained-workspace-as-state. **GAP: this corpus holds ICM practice,
  not the optimization framing. EXTEND, not conflict.**
- `reflection_brain ask "workspace learns from mistakes reflection
  scars prevention"` → S-00-reflection-rules P2 (every work item ends
  in a reflection routing prevention to owning docs), S-s15 P1
  (deterministic corpus must reach the agent via harness-native
  channels). **AGREE: this workspace already implements A2/A3/A4 in
  miniature — surprises (tool failures) are captured (failure ledger),
  routed to owner docs (prevention_rules), replayed (gates re-run on
  every commit; red-path validation = A4's regression replay analog).**

## Cluster B — Skills as evolving external memory (Memento)

- **B1.** Frozen LLMs need external memory: with θ fixed, all
  adaptation must come from the input — prompt, context, or memory.
  Memento-Skills: a generalist agent-designing agent that constructs,
  adapts, and improves task-specific agents through experience.
  [Memento-Skills.pdf, Memento-Team, §1.1]
- **B2.** Skills (structured markdown files) serve as persistent,
  evolving memory encoding both behaviour AND context — Read–Write
  Reflective Learning: read = a behaviour-trainable router selects the
  relevant skill conditioned on the stateful prompt; write = the agent
  updates/expands its skill library from new experience. Continual
  learning without parameter updates.
  [Memento-Skills.pdf, Abstract + §1 Fig.3]
- **B3.** Measured self-evolution: GAIA +26.2% and HLE +116.2%
  relative accuracy improvements over reflective learning rounds; skill
  memory grew 41 → 235 skills, organized into semantic clusters.
  [Memento-Skills.pdf, Abstract + Fig.1]
- **B4.** The Write operation is not simple append: it encapsulates
  failure attribution and file-level rewriting to mutate the prompt or
  code inside the skill — state (s, M) stays Markovian as memory
  evolves.
  [Memento-Skills.pdf, §1.2 Def. + Thm 1.3 discussion]

### Graph check B (2026-09-05 23:32Z)
- `skills_brain` digest (auto-loaded): 41 skills, routing-signal table
  regenerated at commit — **AGREE: this workspace's skills + skills_brain
  digest IS a B2 instance** (markdown skills as memory, deterministic
  router, rebuilt from experience).
- `reflection_brain`: 74 scars from 44 reflections, auto-injected as
  routing signals. **AGREE + EXTEND: scars are B2's "write" phase
  generalized to invariants; the scar digest is the read-phase router
  (deterministic, not behaviour-trained — divergence noted in C-EXTEND).**

## Cluster C — Filesystem as the orchestration substrate (ICM + Atomic Agents)

- **C1.** ICM replaces framework-level orchestration with filesystem
  structure: numbered folders = stages, plain markdown carries
  prompts/context, local scripts do mechanical work; one agent reading
  the right files at the right moment does the work of a multi-agent
  framework. Applies Unix pipeline design, modular decomposition,
  multi-pass compilation, literate programming to context structuring.
  [Interpretable Context Methodology....pdf, Van Clief/McDermott, Abstract + §1]
- **C2.** Control-surface comparison (framework vs ICM): reorder
  stages = rename folders; modify a prompt = edit a file; add a stage
  = add a folder; inspect intermediate state = open the folder; hand
  off = copy the folder; anyone with a text editor can change it.
  Frameworks win at: error recovery mid-pipeline, conditional
  branching, concurrent execution, external service integration.
  [ICM paper, Table 1]
- **C3.** Atomic Agents: an agent is a contract in plain language plus
  a card that permits it to work — profiles (contract, trade-noun),
  skills (know-how, verb-noun), cards (work unit + production permit),
  board (folders as bus), blind deterministic dispatcher (string
  matching, no model), vault (knowledge base). Same profile + same
  card = reproducible result.
  [Atomic Agents....md, Marcos Emowe v1.0, Core idea + The pieces]
- **C4.** "When the system doesn't know what to do, it doesn't guess.
  It waits and it shows." Unmatched card sits in pending/ costing
  nothing — either a profile needs a new descriptor, or you've found
  the next agent you need to write. Blind matching preserves
  determinism: same board routes the same every day.
  [Atomic Agents, Why blind matching]
- **C5.** Every scar ends in a test: "Each real incident leaves its
  round with an automated check, not just a paragraph. A scar without
  a test reopens."
  [Atomic Agents, Integrity rules]
- **C6.** State is the folder, not a database: claiming a card =
  moving a file (atomic); two workers can never claim the same card.
  Pull, not push — idle capacity beats accumulated inventory.
  [Atomic Agents, The board]
- **C7.** Cerebro house doctrine (chief-of-staff-crew): five text
  files orchestrate a chief + 4 specialists; each owns its own files;
  the auditor "checks everyone and fixes nothing" (separation of
  checking from fixing).
  [glitch_cat_club/chief-of-staff-crew.txt, README]

### Graph check C (2026-09-05 23:31–32Z)
- `icm_brain` (the workspace IS an ICM instantiation): C1/C2 describe
  this workspace's own architecture — **AGREE by construction**; the
  ICM_knowledge_big.md corpus (already ingested, verified duplicate)
  is the practice library behind it.
- `reflection_brain` S-s12/S-s13: every routing surface must be
  deterministic + gate-verified against disk (skills catalog, workflow
  rows, research catalog). **AGREE with C4: blind/deterministic
  routing + fail-loud verification is this workspace's established
  doctrine; C5's "scar without a test reopens" matches the red-path
  validation requirement (gate-shape scar S-s20-validation-round4 P1).**

## Cluster D — Session rituals + enforcement layers (practitioner docs)

- **D1.** Two bookend rituals every session: initialization (read
  handoff first, load only what the project needs, load hard rules
  every time, brief then stop) and handoff (update what's done/next/
  blocked, update health log, confirm clean baseline by running tests,
  tag the known-good point). "Tired is exactly when the boring step
  gets skipped." Token discipline: initialization budget 5–10k, a
  40k init is a mistake.
  [How I keep my AI workspace clean...md, Rituals 1–2]
- **D2.** Intent-first SDLC: Discovery creates intent.md → spec.md →
  plan.md → test → human-gated deployment → monitoring; an error in
  maintenance loops back to a NEW intent.md. The bottleneck moved from
  writing code to holding INTENTION through the process.
  [Intent is Everything - Agentic Operator Report.md]
- **D3.** Instruction vs mechanism (multi-agent git safety):
  "Instruction tells the agent what it should do. The enforcement
  mechanism defines what it CANNOT do." Soft constraints (never work
  on main) are readable-and-ignorable; hooks/pre-commit are mechanical
  enforcement. Layered defense: worktree isolation → startup branch
  check → git hook → permission/approval layer → CI/protected branch →
  adversarial tests.
  [Stopping Conflicting Saves From Multiple Agents.md, PL]
- **D4.** "Hook exists" ≠ "hook works": repo config (core.hooksPath,
  executability) can silently disable a hook. The correct test is
  adversarial — deliberately break the rule and confirm the system
  refuses — not `ls .git/hooks`.
  [Stopping Conflicting Saves..., PL]
- **D5.** Worktree isolation does not solve logical conflicts: two
  agents changing the same API consumer both commit cleanly and the
  problem appears only at merge. "Don't try to make the agent remember
  critical rules. Enforce them at the infrastructure level."
  [Stopping Conflicting Saves..., PL]

### Graph check D
- `reflection_brain` S-s20-validation-round6 P1/P2 + S-s19 ledger
  standard: dispositions/narratives must be transcribed from stores,
  audit probes verified against raw artifacts. **AGREE with D4 —
  adversarial red-path validation is already the workspace's gate
  doctrine (pack gates, catalog gates, workflow gate all red-path
  validated).**
- Overlay git-discipline section: anchor before structural moves,
  CRLF churn guard, selective staging (never stage another agent's
  WIP). **AGREE with D3/D5: this workspace layers AGENTS.md rules +
  hooks (pre-commit gates) + memory. D5's merge-conflict limit is
  exactly why the harness handles multi-agent git natively (worktree
  per agent) — noted in overlay harness posture.**

## Cluster E — First-party SDK memory primitives (OpenAI Agents SDK)

- **E1.** OpenAI Agents SDK sandbox Memory (beta, v0.22.0): memory
  distills lessons from prior runs into FILES in the sandbox workspace —
  explicitly separate from conversational session memory (message
  history). It reduces three cost kinds: agent cost (less exploration
  next run = fewer tokens), user cost (remembered corrections/
  preferences = less human intervention), context cost (prior task
  context = shorter task descriptions).
  [Agent memory - OpenAI Agents SDK.html, intro]
- **E2.** Two-phase generation at session close: Phase 1 conversation
  extraction (a model summarizes each accumulated conversation file,
  omitting system/developer/reasoning content, long-conversation
  truncation preserving beginning+end, plus a raw memory extract);
  Phase 2 layout consolidation (a consolidation agent reads raw
  memories per layout, opens conversation summaries when more evidence
  is needed, extracts patterns into MEMORY.md + memory_summary.md —
  with intermediate artifacts raw_memories.md, phase_two_selection.json
  kept in the workspace).
  [same source, Generate memory]
- **E3.** Memory isolation is layout-config-based, not agent-name-based:
  same layout + same memory conversation ID → shared consolidated
  memory; different layouts (memories/gtm vs memories/engineering) →
  separate MEMORY.md per agent even in one sandbox workspace. Live
  memory update (default on) lets the agent update stale MEMORY.md; a
  read-only Memory() is available for checkers/subagents that "do not
  add much signal"; generate-only for runs that should not be
  influenced by existing memory.
  [same source, layouts + Enable memory]

### Graph check E
- `icm_brain ask "single responsibility..."` → the corpus holds the ICM
  practice stream (session persistence via files, markdown as cheap
  stateful context) but NOT the two-phase extraction design.
  **EXTEND: E2's two-phase pipeline (per-conversation extract →
  cross-run consolidation into one MEMORY.md) is a formalization of
  what this workspace does manually (reflections → scar cards →
  digest). The 'reads summaries when it needs more evidence' loop is
  exactly the claims-ledger + ask.py pattern of this research.**
- `reflection_brain` S-s19 (forget-first re-seed): near-identical
  remember() REINFORCES the old card and drops the new content —
  OpenAI's Phase 2 consolidation agent faces the same update-vs-append
  problem this workspace solved with forget-first + verify_reflection_sync.
  **AGREE + this workspace supplies a missing piece: consolidation
  needs a staleness check, not just append.**

## Cluster F — SkillOpt: the skill document as trainable state (Microsoft)

- **F1.** SkillOpt (microsoft/skillopt, arXiv 2605.23904) "treats the
  skill document as the trainable state of a frozen agent" and trains
  it with weight-space discipline: a separate OPTIMIZER model turns
  scored rollouts into bounded add/delete/replace edits on a single
  skill document; an edit is accepted only when it strictly improves a
  held-out validation score; a textual learning-rate budget, a
  rejected-edit buffer, and epoch-wise slow/meta updates make training
  stable with zero inference-time model calls at deployment.
  [skillopt.txt, README Overview]
- **F2.** Deployed artifact = compact best_skill.md (300–2,000 tokens)
  against the unchanged target model. Across 6 benchmarks × 7 target
  models × 3 harnesses (direct chat, Codex CLI, Claude Code CLI),
  best-or-tied-best on all 52 evaluated cells; on GPT-5.5 average
  no-skill accuracy lifted +23.5 (direct) / +24.8 (Codex loop) / +19.1
  (Claude Code) points. Optimized skills transfer across model scales,
  harnesses, and nearby benchmarks without re-optimization.
  [skillopt.txt, README Overview]
- **F3.** Blog (July 2026, Zhou/Gong/Yang): 499 analyzed runs —
  Skill-Aware Reflection (SAR) "interpret a trajectory against the
  current skill before deciding" updates + memory consolidation;
  SkillOpt-Sleep (deployment-oriented plugin); expanded update-policy
  ablations distinguishing validation-selected vs final checkpoints.
  [skillopt.txt, blog/gating-reflection-safe-updates/index.html]
- **F4.** Repo structure shows the full DL-training analogue as
  infrastructure: ckpt/ (per-benchmark trained skills), configs/
  (per-benchmark + feature/soft_gate.yaml — the validation gate as
  config), data/ split_manifests (train/val/test splits for SKILL
  training), hermetic CI (real-backend tests opt-in gated).
  [skillopt.txt, directory structure + CI tail]

### Graph check F
- `reflection_brain` S-s12/S-s16 (routing surfaces verified against
  disk; live-query gates): **AGREE — SkillOpt's validation-gated edit
  acceptance (F1) is the same invariant this workspace enforces on
  workspace edits: a change lands only when the gate (held-out check /
  red-path validation) passes. Soft-gate config (F4) = gate behavior
  declared as data, matching this workspace's doctrine that gates are
  first-class artifacts.**
- Divergence noted: SkillOpt optimizes ONE skill document by gradient-
  discipline edit loops; this workspace accumulates MANY small scars +
  skills with deterministic (non-learned) routing. CONFLICT-5 below.

## Cluster G — ICM principle expansions (new corpus material, slice-verified not in icm_brain)

- **G1.** One Stage, One Job (single responsibility per folder): each
  stage folder owns exactly one transformation; compiler-analogy (each
  pass reads previous pass output, well-defined interfaces); stage
  size guidance; when to bend the rule.
  [INBOX/One Stage, One Job.md — expansion of ICM paper principle 1]
- **G2.** Plain Text as Interface (markdown/JSON as universal
  communication layer): no-database principle, literate-programming
  connection, human+AI document workflow; includes a worked example
  (Research: AI Agent Orchestration stage outputs as Inputs/Process/
  Outputs in plain text).
  [INBOX/Plain Text as Interface.md — expansion of ICM principle 2]
- **G3.** ICM_map.md: mindmap of the whole methodology (problem/core
  idea → principles → architecture → evidence → compiler analogy →
  future directions).
  [INBOX/ICM_map.md]
- *(G1–G3 are expansions of the ICM paper's own principles; the
  workspace's AGENTS.md/PROCESS tree is the living instance. Not
  re-derived claim-by-claim: the paper (C1/C2) carries the primary
  claims; these docs are study material for future icm_brain
  ingestion — candidate corpus chunks, see findings §5.)*

## Cluster H — AI-as-team org context (Tal Raviv adaptation)

- **H1.** The bottleneck moved: "the competitive advantage isn't
  merely having access to the same frontier models. It's giving those
  models better organizational context and creating a system in which
  that context gets better over time." Ten principles incl.: give AI
  the same context people need; centralize shared knowledge rather
  than distributing copies; keep private/team/department/company
  context separate; maintain a short explicit instruction file;
  **continuously improve that instruction file based on failures**;
  design for compounding knowledge (one person's AI improvement
  should eventually help everyone).
  [How to Use AI as a Team.md, §16 + thesis, adapted from Tal Raviv]
- **H2.** Rollout as 4 weeks: establish workspace → establish AI
  instructions → run real work → capture improvements; instruction
  file treated as a PRODUCT (owned, versioned, improved).
  [same source, §7/§14]

### Graph check H
- `icm_brain` corpus: workspace-setup-for-context stream. **AGREE with
  H1's separation-of-context-scopes: this workspace already separates
  project-scope memory (native) vs global brains vs per-record
  research folders vs stage contracts — H1's four levels map onto
  scope-native stores.**
- H1 principle 8 ("improve instruction file based on failures") =
  this workspace's reflection loop (Rule 6 + R9b). AGREE by
  construction.

## CONFLICTS + TENSIONS (running list — resolution in findings.md)

- **CONFLICT-1 (B2 vs C3):** Memento's skill router is
  *behaviour-trained* (a learned retrieval policy µ with convergence
  guarantees); Atomic Agents' dispatcher is *blind string-matching*
  (deterministic, no model, "letting a model decide routing destroys
  determinism"). Both claim their routing is what makes the system
  improve safely. Tension: trainable routing vs auditable routing.
  This workspace resolved it: deterministic digest routing at the
  injection layer (S-s13/S-s15), semantic recall only as a hint that
  never overrides. Resolution to be argued in findings.md.
- **CONFLICT-2 (C2 vs this workspace):** ICM Table 1 concedes
  framework advantage at error recovery, branching, concurrency. But
  this workspace implements error recovery (failure ledger + problem
  lifecycle), branching (WORKFLOW.md scenario routing S1–S7), and
  multi-agent concurrency (harness-native worktrees) ON the filesystem
  substrate — the ICM "lacks" column is dated 2026-03; the workspace's
  2026-09 state refutes the permanent version of that claim. EXTEND.
- **CONFLICT-3 (A5 vs B3):** DREAMTEAM attributes gains to typed-slot
  failure routing + regression replay; Memento attributes gains to
  similarity-retrieved skill memory + reflective rewriting. Different
  mechanisms, same direction (frozen model + evolving external state).
  Not a contradiction — two complementary loops (addressing vs
  retrieval); this workspace runs BOTH (scars = addressed by owning_doc;
  skills_brain = retrieved by query). Note in findings.
- **TENSION-4 (D1 vs graph-fed method):** the rituals doc budgets
  5–10k tokens for session init; the user's 23:23 directive (don't put
  it all in context; query the graph) is the stronger form of the same
  discipline. The workspace's overlay digest is already the
  deterministic core (~74 one-line scars); bulk knowledge stays in
  brains behind ask.py. AGREE — D1 is the manual-sequence ancestor of
  the graph-fed ledger method.
- **CONFLICT-5 (F1 vs this workspace's scar model):** SkillOpt trains
  ONE skill document with a learned optimizer + held-out validation
  gate; this workspace accumulates MANY small invariant-scars across
  many owning docs, routed deterministically, each red-path validated
  at birth. SkillOpt's edited skill replaces its predecessor
  (best-skill-wins); this workspace's scars are append-mostly
  (each problem's invariant is ADDITIVE — the doc grows). Trade-off:
  SkillOpt gets optimization pressure (compacting toward what works)
  at the cost of a benchmark-defined objective; this workspace keeps
  auditability and no-benchmark generality at the cost of growth
  (74 scars and counting; overlay digest size is the budget).
  Resolution direction in findings §4: bounded scar lifetimes +
  digest budget as the analogue of SkillOpt's learning-rate budget
  (prune/merge superseded scars at reflection time — already done
  ad-hoc via forget-first; needs a doctrine).
