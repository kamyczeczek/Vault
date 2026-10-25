---
type: Concept
flag: forge_ab_design
since: 2026-10-03
owner: unassigned
agent: unknown
model: unknown
origin: migrated 2026-10-03 from HANDOFF.md §Status
title: forge_ab_design
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`forge_ab_design` — 2026-10-03: the hooks ON/OFF measurement is **designed and
pre-registered**, nothing scored yet. Design (single home):
`projects/research/agentic-research-lab/docs/research/forge-guardrails-ab.md`;
artifacts: `scripts/forge_ab_power.py` (exact paired-McNemar power/MDE,
`--selftest` green), `.forge-ab/tasks.yaml` (2 task families, metrics by
channel, decision rule), `.forge-ab/arm_off.yaml` (OFF-arm switch),
`.agents/plugins/forge-ab-observe` + `scripts/_scratch/forge_ab_observe.py`
(read-only `PreToolUseResult` audit, `--selftest` green). The handoff's
"N>=5/arm, needs baseline failure rate > 0" is **retired as wrong on both
counts**: at n<=20 no lift of any size reaches 80% power (floor ~25 pairs), and
for a paired test the baseline level does not enter the power calculation at
all — the binding quantity is discordance φ, and a marginal lift can never
exceed φ (today φ~=0.13, which cannot express a 15-point lift). Also retired:
**turn count as a quality metric** (a Stop block does not end the turn and Stop
re-runs suites, so the ON arm is mechanically penalised); primary metrics now
come from channels the treatment does not write, since `state.json` and the
journal are agent-writable (an agent already hand-edited `state.json`).
Known ceiling: goose's Stop payload has no tool trace and no advise tier
(aaif-goose/goose#10358), so `_reverify_suites` judges current tree state, not
what the agent did — any conclusion is scoped to deny-only enforcement on
flash-lite. Next step: human call on stage 1 = 50 goose runs (~4 h) for n=25
pairs, which catches only a 30-point swing; extend to n=105 only on evidence.
Also open: delete `.forge/context.md` (stale fabricated self-cert residue,
harmless — SessionStart overwrites it).
