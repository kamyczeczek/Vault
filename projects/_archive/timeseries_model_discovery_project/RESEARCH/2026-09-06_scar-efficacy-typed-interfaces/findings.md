---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Scar Efficacy and Typed Interfaces

<!-- Synthesis from directly-computed store measurements (probes
     `_dbg_evidence_pack*.py`, `_dbg_direction_probe*.py`, run
     2026-09-06 00:44–01:02Z) + the prior record's claims ledger.
     Every number below is transcribed from probe output, not memory.
     Stores: .jcode/session-state/failure_ledger.jsonl (391 entries),
     dispositions.jsonl (396), brains/reflection_brain/reflection_index.json
     (76 scars), brains/reflection_brain/digest.md (12,616 chars). -->

## 0. Provenance of every number in this file

- Ledger: 391 entries, of which **135 baseline** (retro-deployed 2026-09-04,
  covering 118 back-entries from 09-03 + 17 from 09-04) and **256 live**
  captures since deployment (09-04: 113, 09-05: 132, 09-06 partial: 11).
  Live by tool: bash 204, edit 21, read 14, todo 13, batch 3, multiedit 1.
- Dispositions: 396 records = 135 baseline + 257 benign + 4 problem.
- Scar index: 76 scars / 45 reflections / 64 distinct owning docs; digest
  12,616 chars ≈ 3.2K tokens injected into every session.
- Same-day disposition rate: 252/391 = 64%.

## 1. The founding result: scars do not prevent their own class

The antifragility thesis (prior record, findings §1) predicts each failure
class stops recurring after its invariant lands. **The workspace's own
ledger refutes this for interaction-shape traps.** Live (post-baseline)
recurrences of scar-known classes:

| Trap class | Scar born | Live recurrences after | By day (04/05/06) |
|---|---|---|---|
| edit-anchor-mismatch | 2026-09-02 (S-h720-temporal-knn-sweep P1/P3 "re-read the block before the next edit") | **19** | 6 / 11 / 2 |
| tool-call-schema (todo/multiedit arg shape) | 2026-09-04 (S-s19 #216) | 16 | 8 / 8 / 0 |
| python-c-traceback (multiline `-c` no-op) | 2026-09-04 (S-s19 #224) | 14 | 1 / 13 / 0 |
| todo-schema (enum/null-args) | 2026-09-04 (#216/#282) | 13 | 1 / 9 / 3 |
| run-before-write (probe file missing) | 2026-09-03 (#141 family) | 7 | 1 / 5 / 1 |
| **TOTAL mechanizable** | | **69** | |

69 of 256 live entries (27%) are recurrences of classes whose prevention
rule was already written, injected (scar digest), and committed. The
prevention layer is recall-shaped — "read this rule before acting" — and
the failures happen at tool-composition time, microseconds before the rule
could apply. **Recall cannot prevent interaction-shape errors; only an
interface that refuses the malformed action can.** This is the prior
record's D3 claim (mechanism-over-instruction, practitioner corpus) and
DREAMTEAM's typed-slot insight (A3: prediction errors route to a NAMED
interface that validates shape) now proven necessary by our own exhaust —
the first data point where the workspace's ledger CONTRADICTS the pure
accumulation model (CONFLICT-5's hidden assumption).

## 2. What the failure mass actually is (definitive taxonomy, 391 entries)

| Group | n | % | Content |
|---|---|---|---|
| Self-validation / loop's own noise | 108 | 27.6% | gate blocks, verification runs, red-path validations, measurement exits (findstr/diff no-match) |
| Interaction traps (mechanizable) | 95 | 24.3% | the five classes above + robocopy exit-semantics, shell-quoting |
| Environment / harness | 70 | 17.9% | module-not-found (54, one bad interpreter path family), harness-tool errors (16) |
| Residual shell exits | 118 | 30.2% | probe-dev iterations, python errors in throwaway code, mixed measurement |

Two structural facts follow. **(a)** More than a quarter of all captured
"failures" are the workspace correctly refusing or correctly measuring —
the ledger records its own immune system's activity as incidents. The
disposition pipeline (benign-with-evidence) handles this at ~64%
same-day latency, but the signal is diluted: a future automated
classifier should separate expected-exit classes at capture time
(pre-registered verdicts), not at disposition time. **(b)** The
single biggest environmental class (module-not-found, 54 entries,
13.8%) collapsed after 09-04 — it was one interpreter-path family
(python3 Store stub), fixed by the S-jcode-native-rework phase-1
invariant. One mechanism killed 54 entries' entire class. That is the
typed-interface effect at environment scale, and it is the strongest
existence proof in the ledger that **mechanisms eliminate classes while
scars only inform about them.**

## 3. D1 — typed interfaces: the five preflights, with measured targets

Each recurring class maps to a pre-call check that can refuse the action
BEFORE execution (design: a pre_tool gate or tool-wrapper, S-s18's
harness pattern):

1. **Edit preflight** (19 live recurrences): `old_string` must exist in
   the target file (and `new_string != old_string`). A read-index or
   cheap re-read at edit time. Kills the whole edit-anchor class,
   including the whitespace-variant (probe: check after
   leading/trailing-trim match = the round-4/this-session trap).
2. **Tool-call schema preflight** (16 + 13 = 29): arguments must be a
   JSON object with the declared enum fields (todo ConfidenceState,
   IntentUnderstanding enum, multiedit file_path). The harness already
   validates this — the fix is making the CLIENT (me) unable to emit the
   malformed call: a typed call template, or an agent-side lint over the
   outgoing JSON. Cheapest class to kill; all 29 are self-inflicted.
3. **python-c → probe-file discipline** (14): the trap is cmd.exe's
   line handling of multiline `-c` strings. Mechanical fix candidates: a
   `probe` tool that writes the file THEN runs it, or a session-state
   convention enforced by a hook (any `python -c` containing `\n` or
   quote-heavy literals → refuse with "write a probe file").
4. **Existence preflight** (7): file path referenced by a run command
   must exist (the run-before-write class, 3 hits THIS session).
5. **robocopy wrapper** (1) + shell-quoting (3): minor; a
   run-wrapper that translates `if errorlevel 8` and refuses
   bash-heredoc syntax on cmd.exe.

Falsifiable prediction (the record's testable core): after preflights
1–4 land, their classes' live recurrence counts go to zero within two
sessions; the scar-digest injection rate for those classes becomes
noise. If recurrences persist, the mechanism is wrong, not the
philosophy — same red-path discipline as gate validation.

## 4. D2 — scar efficacy as the merge criterion (deepens prior R1)

The prior record's R1 gap (digest budget without a merge rule) gets its
missing decision procedure from this data. Merge/prune by measured
efficacy, not age or size:

- **Class extinct after its mechanism** (e.g. module-not-found post
  interpreter fix) → the scar's invariant is discharged; MERGE into one
  historical line or DROP from the digest (keep in index).
- **Class recurrences → 0 after scar birth** (robocopy: 0/1) → scar is
  working as recall; KEEP but candidate for digest demotion (frequency
  weighting, not deletion).
- **Class recurs after scar birth** (edit-anchor: 19!) → the scar's FORM
  is wrong for that class; REWRITE as a mechanism requirement ("edits
  MUST pass preflight X") or re-route to the owning tool, not the doc.

This converts the digest from a size-bounded append-log into a
quality-bounded one: SkillOpt's validation-gated deletion (F1: a skill
doc edit survives only if the benchmark cell improves) applied to scars
— a scar survives the digest only while its class is alive OR its rule
is load-bearing for a live mechanism. The 76-scars/64-owning-docs
atomization (near 1:1) is the symptom this fixes.

## 5. D3 — failure epidemiology: the workspace metric (answers prior open Q3)

The benchmark Memento (+116.2% HLE, B3) and SkillOpt (52/52 cells, F2)
had that this workspace lacked is now computable from the ledger:

- **Incidence** (live entries/day): 113 → 132 → (11 partial). Flat-to-
  rising in gross terms — but decompose: mechanizable traps 27%,
  self-validation noise 28% (should be EXCLUDED from incidence — it is
  the immune system working, not disease), environment 18% (collapses
  after fixes), residual probe-dev 30% (inherent to red-path
  methodology, bounded by it).
- **The true incidence to track** = mechanizable-trap rate per session.
  It should step to ~0 as D1 lands — that is the workspace's first
  measurable "less slop over time" curve.
- **Cost**: same-day disposition 64%, zero OPEN at every recent close —
  recovery is cheap and getting cheaper; the deficit is entirely on the
  prevention side.

Proposed standing metric (S1 candidate, not research): a close-of-day
probe computing (live-entries, mechanizable-share, extinct-classes,
digest-tokens) into PROGRESS.md — one line, replayable, the
epidemiological curve the antifragility thesis predicts should bend
down.

### 5a. Post-record addendum: D3 is BUILT and the first reading taken
(2026-09-06, same session as D1 — the gate gets its efficacy number
immediately, not after three days)

The probe is `.jcode/hooks/epidemiology.py` (suite 25/25, 3 red-path
shape proofs; every classification signature verified against a
hand-checked raw ledger row — three signature corrections were made
AFTER inspecting actual rows, all in the direction the S-s20-r6-P2
scar predicts: first verdicts were wrong on commit-echo shapes, on
the `python -X utf8 -c` flag form, and on the single-line vs multiline
`-c` split).

**First measurement (2026-09-06, EPI line in PROGRESS.md):**
live=292 (97.3/day over 3 days), mech=83 (28% of live), and — the
record's testable core — **post-birth recurrences for ALL FIVE gated
classes = 0**: edit-anchor 0, multiline python-c 0, run-before-write
0, robocopy 0, read-schema 0 (P5's birth boundary placed at ledger
#410: #409 at 02:47Z was the last ungated read-schema hit; the fix
preceded #410). D1's zero-recurrence prediction is CONFIRMED at first
measurement — with the honest caveat of open Q3 (one day, one
session-mix, small n post-birth: ~29 live entries in the window).

The measurement also exposes what recall still leaves on the table:
**tool-schema = 21 live, ungated** (todo/batch/multiedit argument
rejects — the P6 candidate; the workspace's own two malformed todo
calls during the D3 open landed in this class within the hour), and
**python-c-line = 16 live, ungated** (single-line `python -c` raising
real tracebacks — probe-dev residual; the probe-file discipline covers
it, no gate does). Self-validation is 43/292 = 15% of live entries —
counted separately as immune-system activity, per §2's finding (a).
Digest-tokens measured (not estimated) at 1815 on gen_digest's own
tok basis (open Q6: the overlay block IS the injected budget; markers
excluded).

Standing use: run `python .jcode/hooks/epidemiology.py --write` at
every session close; the EPI line is idempotent per day (re-runs
replace, history is append-only). The extinct-class list is D2's
merge input: a class extinct after its mechanism's birth is a scar
whose digest line is a candidate for demotion (§4's first rule).

## 6. What this record changes about the prior record's conclusions

- Prior mechanism 4 (distillation tiers) and the scar channel are
  CONFIRMED for knowledge that benefits recall (env classes, protocol
  classes) and REFUTED AS SUFFICIENT for interaction-shape classes —
  they need mechanism 1-style typed routing (interface refuses) instead.
- CONFLICT-5 resolution gets teeth: the budget is not "digest size" but
  "digest mass of live classes" — efficacy-weighted (§4).
- The thesis sentence gains a second clause: failures make the workspace
  stronger **iff each failure class terminates in a mechanism when one
  is constructible, and in a scar otherwise** — scars are the residual
  category, not the default one.

## 7. Post-record addendum: D1 is BUILT, WIRED, and live-fire validated
(2026-09-06, same session as the record — open question 1 resolved)

The record's blocking unknown was whether a pre-call interception point
exists. It does: Jcode's `pre_tool` GATE hook (docs/HOOKS.md — exit 2
blocks the call with the hook's stderr returned to the model; anything
else fails open; 5 s default timeout). The live config had wired only
`post_tool`; the pre-call slot was empty and is now occupied.

- **Gate**: `.jcode/hooks/tool_preflight.py` — P1 (edit/multiedit:
  target exists, exact-or-whitespace-variant anchor present,
  `new != old`), P2 (multiline `python -c` → probe-file hint), P3
  (`python <script.py>` missing on disk, resolved against the command's
  own `cd` targets), P4 (bare robocopy without `if errorlevel 8`),
  P5 (`read` string offsets for start_line/limit — a class that
  recurred 3x in this session alone before the gate existed).
  Fail-open on every unmodeled shape, per the harness contract.
  P2/P3/P4 token analysis is quote-aware (`.jcode/hooks/cmd_quoting.py`).
- **Validation, three layers** (S-s20-round-4 gate doctrine):
  1. differential suite `tests/test_tool_preflight.py`: 31/31,
     14 red-path blocks proven, 17 allow-shapes — the suite caught
     2 defects during development (ROOT parents[2] off-by-one; P3
     false-positive on `cd <dir> && python s.py`, fixed with
     cd-target resolution);
  2. live-fire RED: 4 deliberate violations each blocked with a
     `[preflight]` message returned to the model (no-op edit,
     anchor miss, multiline `python -c`, missing script — ledger
     #400–#403, dispositioned benign as near-misses BY DESIGN);
  3. live-fire GREEN: a valid edit passed through and landed
     (pass-through verified, not just blocking).
- **Production findings (first hours, ~2 of them)**: the gate caught
  3 real malformed edit anchors in the wild (each would have been a
  burned call); it also produced 1 false positive (P4 matched "robocopy"
  in a commit-message prose mention — fixed with command-position
  matching) and 1 false negative (a `;` inside a quoted `-c` string
  sliced the naive segment split, letting a multiline `python -c`
  silently no-op — fixed with quote-aware segmentation in
  `cmd_quoting.py`). Both live defects are frozen as suite regression
  cases. The pattern: gate failures are CHEAP and VISIBLE (exit-2
  with a fix hint, ledger-captured) — exactly the mechanism-over-scar
  thesis of section 6, now demonstrated on the gate itself.
- **Prediction handed to D3**: the five gated classes should now show
  zero live recurrences (blocks will appear as near-misses instead).
  §5's metric can measure this directly — recurrence-after-gate-birth
  becomes the efficacy signal for the gate, exactly as
  recurrence-after-scar-birth is for scars.
