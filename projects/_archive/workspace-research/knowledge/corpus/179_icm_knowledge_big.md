---
type: Concept
id: 179_icm_knowledge_big
title: "ICM_knowledge.md (part 180/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

<every error that occurred, factually. What broke, the message or symptom, how it was caught, whether it was fixed in this job or left open. Include errors the job recovered from, not just fatal ones, because the recovered ones are where the build map teaches the most. If none, say "none".> Per-error, set at write time: status: open | recovered (open = left unresolved and action-needed; recovered = fixed within this same job)

## Map flags              [structured format — feeds PENDING_MAP_UPDATES.md]

For each of the five maps your job changed, OR read and found an error in. If no map was touched or checked, write "none." If flags exist, each must have exactly three fields on three consecutive lines. A flag missing any field is invalid and must not be written. Errors noticed in MAP_folders while orienting at job start count here, routed to PENDING_MAP_UPDATES, not ISSUES.

Map: MAP_storage | MAP_data | MAP_pipeline | MAP_features | MAP_folders Claim: [exact current map text] → [exact proposed replacement text] Evidence: path:line confirming the change is live on disk right now

The loop (`pipeline/loop_harvest.py`) harvests these flags into PENDING_MAP_UPDATES.md, on its own cadence, for the next verification run.

## _tmp outputs            [human-read — Queen reads _tmp at boot]

List each file the job wrote to _tmp, tagged discardable (safe to delete) or needs-a-home (a real output in _tmp only because it has no home yet; flag for promotion). Write "- none" if nothing was written to _tmp. Queen reads _tmp at boot and uses this field to decide what to clear and what to promote.

\-    none

## CONTEXT.md feedback         [structured — gap lines route to coordination/CONTEXT_FEEDBACK.md]

One line per CONTEXT.md read. Adequate means nothing was missing. Use the gap form only when something needed was absent. The literal token ` gap: ` is the routing marker; keep it exact. Write "- none" if no CONTEXT.md was read.

\-    /CONTEXT.md: adequate

\-    /CONTEXT.md: gap: | found: | add:

\-    none

------

Note: the worker bee (the desktop chat) does NOT write one of these. It writes one journal at

the end of the feature, on the separate journal path. The job touchdowns are the build record;

the journal is the narrative. The

field is what ties every job back to its worker bee,

so the whole feature's jobs are reconstructable by reading the title, without the bee tracking

------

2026-06-28 -- Changelog section added.

2026-06-28 -- Broadened map-flag trigger to maps read-and-found-wrong; added _tmp outputs and CONTEXT.md feedback fields.

2026-07-03 -- Reworded the harvest description from "Queen at prime time" to the loop (

pipeline/loop_harvest.py

) on its own cadence, independent of priming (audit §2.7 item c); retired the dead

frontmatter field, never touched by loop_harvest.py (item g).

2026-07-03 -- Added
