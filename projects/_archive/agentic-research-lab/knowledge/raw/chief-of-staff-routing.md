---
type: Concept
title: "Chief-of-Staff Routing: Supervisor + Specialist Crew via House File"
source: "https://github.com/glitch-cat-club/chief-of-staff-crew + https://www.agentpatternscatalog.org/patterns/routing/ + https://code.claude.com/docs/en/sub-agents"
tags: [context-engineering, icm, routing, agents, agentic, planning, anti-leakage]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Chief-of-staff is the Supervisor pattern: one coordinating agent classifies work and routes to specialists. Agent Patterns Catalog (routing, 2026-05-22) defines routing as classifying heterogeneous requests and dispatching to the lane/model/prompt best suited — cost drops when cheap deterministic lanes absorb 80% of traffic, but misrouting costs more than not routing, and the classifier needs visibility into downstream capabilities. Used-by: Supervisor, Dynamic Scaffolding.

Glitch Cat Club's chief-of-staff-crew (github glitch-cat-club/chief-of-staff-crew, 16 files, 9k tokens) is a concrete Claude Code instantiation: five text files do it — `CLAUDE.md` (house file) + `.claude/agents/chief-of-staff.md, designer.md, copywriter.md, builder.md, auditor.md` plus `.claude/settings.json` + `.claude/hooks/board.py`. No installs, no API key. Demo: `claude --agent chief-of-staff` then "fix the Vinyl Room site" — chief reads `site/`, lists problems, writes TodoWrite board first, dispatches four specialists in parallel in one message, collects reports.

Steering wheel is `CLAUDE.md`: palette/type/design rules, real business facts (never invent), layout constraints, ownership table (file → owner). Agents are generic; specificity lives only in the house file — sharpen the house file when output drifts. Each agent frontmatter sets `model` and `maxTurns` (cost/cap dials). `420Hippie/agent-routing-template` generalizes the same shape: `TEMPLATE-apex.md` + `TEMPLATE-specialist.md` + `routing-rules.md` (CLAUDE.md block) + `escalation-protocol.md` — the escalation path everyone forgets to write down.

Implication for ICM brain: this is L1 routing (who handles what) implemented as `CLAUDE.md` + `.claude/agents/` + `route.py --tag` classifier, not prompt prose. Mirrors ICM's L0 identity → L1 routing → L2 stage contract hierarchy; keeps routing deterministic and file-scoped. Map to workspace-research: `extension/workspace-research.ts` digest injection is the shared house file, `spawn_recursive.py` leaves are specialists by topic tag.

Provenance: Exa "chief of staff agent pattern routing specialist agents" → agentpatternscatalog.org/routing + 420Hippie/agent-routing-template + glitch-cat-club repo + code.claude.com sub-agents, retrieved 2026-09-15 via agent-reach Exa (mcporter).
