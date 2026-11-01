---
flag: etth1-h720-s44-calibration-2026-10-30
since: 2026-11-01
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`etth1-h720-s44-calibration-2026-10-30` — 2026-11-01: The ADR 0001 threshold-comparability
caveat is now a number. The S44 blend (NLinear L336 a=1 + NLinear L336 a=10 +
PatchTST-Delta P24 D32 2L, per-horizon ridge, no intercept, alpha=30000, frozen) scores
4.1255 mean raw MAE on the S49 protocol (12 locked origins, step 720 h, 8640..16560),
5-seed mean 4.1721. BigDictELM L96 2.4777, DLinear 2.5384. Rule fixed before the run:
4.1255 >= 2.4777, so 1.9781 was a protocol artifact (2161 dense step-1 origins), not a
level reachable on 12 sparse step-720 origins.

The blend is also worse than each of its own members (2.61-2.70). Mechanism recorded, not
tuned away: with no intercept the ridge can only express a level multiplier, and the
multiplier learned on a biased-low out-of-sample region (-5.24 bias, member MAE 6.09)
over-corrects at the scored origin (member MAE 2.79) — 1.3249x pushes the level to 25.3
against an actual 21.1. The disjoint second-half sensitivity reproduces the failure
(3.1041), so it is not one unlucky split.

Two corrections were made to an earlier attempt in this session, both before the reported
run. (1) Ridge weights in S44 were fitted on OUT-OF-SAMPLE member forecasts; the earlier
"in-sample ridge" claim was wrong and is removed. (2) The first calibration harness trained
members on s[o-8640:o] and then fed the ridge their forecasts from the last 2880 rows of
that same window — in-sample stacking, which S44 never did. Fixed: members frozen at row
5760 produce the ridge's design matrix over the 2161 out-of-sample tail origins, members
are refit on all 8640 rows for the scored forecast. Recorded as Amendment A1 in
GATES-s44-calibration.md before the run.

Consistency control: the identical S44 frozen test reproduces 1.978126 (rel diff 4.2e-11)
on both data files. Gate evidence for this close: the workspace integrity gate
`check_workspace_integrity.py` exit 0, and `python -m pytest projects/research/etth1-h720
-q` green at 31 passed. S49 stays closed, no model promoted, nothing tuned.

not checked: S44's dense 2161-origin test was not re-scored with seeds 43-46; S44's ridge
was not fitted once and reused (impossible across disjoint origins); alpha was not re-tuned
for the 8640-row window; BigDictELM/DLinear were re-derived, not diffed bit-for-bit against
S49's stored JSON; the two ETTh1 copies were not reconciled (<=3.6e-15, immaterial).

Next step: nothing on this line. Any further H720 work needs a new hypothesis, fresh dev
origins and a protocol registered before the run. The root/config follow-ups from the
CodeGraph G3 FAIL (disable jcodemunch or keep one code-index tool, shorten the CodeGraph
rule in root CLAUDE.md, keep the index for manual queries) remain open and are out of this
project's scope.
