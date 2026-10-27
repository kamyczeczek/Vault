---
type: Concept
title: icm_reflection_workflow
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564  phase: 04_reflect  routing: see Routing section below
# Reflection Digest — `icm_reflection_workflow`

**Routing contract applied:** deterministic tag-intersection only, via `knowledge/graph/ask.py --tag`.
Query sets run (graph digest fp `1cf1e4aea87c`, 581 nodes):
- `icm` ∩ `reflection` → 12 canonical ICM sources + 200+ `icm_knowledge_big` parts (full set retrieved, not capped).
- `icm` ∩ `context-engineering` → adds `00_adapt...`, `00_awesome_context_engineering`, `00_icm_map`, `01_icm_map`, `00_plain_text_as_interface`, `00_from_plan_to_action...`, etc.
- `reflection` ∩ `context-engineering` → same canonical set.
- `icm` ∩ `determinism` → **EMPTY** (no chunk co-tags both).

## Claim
In the Interpretable Context Methodology (ICM), **reflection is wired as a filesystem *stage*, not a framework component**. The workflow is "numbered folders = stages; plain markdown carries the prompts/context; one agent reads the right files at the right moment" (`00_interpretable_context_methodology_folder_structu`). Reflection therefore runs as a numbered stage that consumes prior Layer-4 working artifacts and writes a plain-text reflection artifact that becomes the handoff / Review-Gate input for the next cycle. The Five-Layer Context Hierarchy (`00_icm_map`) makes Layer 2 (Stage Contract) the "core control point" and Layer 4 (Working Artifacts) "The Product," with stage output folders as explicit "handoff points ... Review Gates." Design rule #4 — "Every Output is an Edit Surface: Human-in-the-loop at every step" (`00_icm_map`) — is exactly the loop reflection closes: it produces an editable artifact rather than an opaque in-memory state.

Reflection is also **plan-aware**: the plan-compliance literature (`00_from_plan_to_action_how_well_do_agents_follow_th`) shows agents drift from advisory plans as context grows, and that "periodic plan reminders can mitigate plan violations." A reflection stage is the natural mechanism that re-anchors the agent to the plan between cycles. Self-evolving / world-model work (`00_self_evolving_world_models_for_llm_agent_plannin`) frames reflection as the agent self-improvement step in this same staged pipeline.

## Evidence
- `00_interpretable_context_methodology_folder_structu` — "ICM ... replaces framework-level orchestration with filesystem structure. Numbered folders represent stages. Plain markdown files carry the prompts and context ... one agent reads the right files at the right moment."
- `00_icm_map` — Five-Layer hierarchy; Layer 2 Stage Contract = "core control point"; Layer 4 = "The Product"; "Stage output folders are the handoff points for the next stage or a human reviewer. Creates 'Review Gates'"; design rule #4 "Every Output is an Edit Surface."
- `00_plain_text_as_interface` — "Plain Text as Interface: Markdown/JSON as the Universal Communication Layer" (reflection I/O is plain text by construction).
- `00_from_plan_to_action_how_well_do_agents_follow_th` — plan compliance degrades without reminders; periodic reminders mitigate violations → reflection as plan-re-anchoring stage.
- `00_self_evolving_world_models_for_llm_agent_plannin` — reflection as the self-evolution step in staged planning.
- `icm` ∩ `determinism` query → **empty**: the ICM corpus defines the reflection *workflow* but does **not** co-tag it with determinism — reproducibility of reflection is undocumented (see Decision).

## Decision
The `icm_reflection_workflow` is correctly modeled as a **plain-text Review-Gate stage** in the numbered-folder pipeline, consuming Layer-4 artifacts and emitting an editable reflection artifact. This is consistent across the architecture map (`00_icm_map`), the folder-structure paper (`00_interpretable_context_methodology_folder_structu`), and the plain-text interface rule (`00_plain_text_as_interface`). The mechanism is plan-aware (`00_from_plan_to_action_how_well_do_agents_follow_th`) and self-evolving (`00_self_evolving_world_models_for_llm_agent_plannin`).

**Gap:** determinism of the reflection stage is not covered in the KB (`icm`∩`determinism` empty). The reproducible routing used *here* (exact tag-intersection → same id set per digest) is the missing deterministic discipline the reflection stage should adopt.

## Next bet
Promote a candidate that **adds a determinism rule to the reflection stage**: reflection MUST route only by explicit tag-intersection queries against the frozen graph digest (same tags + same fingerprint ⇒ same chunk id set), and MUST write its digest + candidates to fixed paths rather than free-associate. Test by re-running this exact routing on a future digest and verifying the id set is byte-stable. Secondary bet: instrument reflection as a measured Review Gate on a real sequential workflow (per `00_icm_map` "Where ICM Works: sequential, reviewable, repeatable workflows") and record plan-drift before/after.
