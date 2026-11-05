---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Is This Already Built By Someone?

Only questions that prior art does not answer. Anything resolved by §1–§4 of
`findings.md` is deliberately not listed here.

## Q1 — Is the 27% recurrence number a stable property, or an artifact of one capture?

The one open delta (§5 of findings.md) rests on a single measurement: 69/256 live
ledger entries (27%) are recurrences of already-scarred trap classes, from record
R-04. Prior art does not measure recurrence at all, so there is no external number to
compare against — which means this is either the most interesting finding in the
audit or a one-time artifact of how that ledger was captured.

- **Why it matters:** if 27% is stable, the accumulation model is measurably
  partially-failing and the correct next build is a recurrence-rate gate, not another
  prevention rule. If it is an artifact of capture timing, the model is fine and this
  whole delta dissolves.
- **What would settle it:** a second, independent capture window. The ledger is
  currently **stale (last capture 2026-09-07, id 534 — 9 days)**, so this cannot be
  answered until the capture itself is repaired (see `open_risks` in the session
  reflection). This is the single question the audit raises that requires new
  machinery to answer.
- **Owner:** this workspace. No external source addresses it.

## Q2 — Does an edit-time gate (Agent-Proof Stage 1) actually catch class 3, or only class 2?

`Agent-Proof` places a gate at `PostFileEdit` with a `<50ms` SLA on a single modified
file. Its Stage 1 engine list (Biome, Ruff, Hadolint, Zizmor, ast-grep) is
*deterministic AST/lint* — the same category as my compile gate, just earlier.

- **Why it matters:** if Stage 1 is AST/lint only, then repositioning my gate to
  edit-time buys me class-2 coverage *earlier* but still does not catch class 3 (a
  dropped line that parses fine). ChangeGuard catches class 3 only by *executing*
  both versions, which cannot be done in `<50ms`.
- **Unresolved because:** the Stage-1 position's class-3 coverage is not stated in the
  source I read, and I did not run Agent-Proof. Reading about it is not the same as
  measuring it.
- **What would settle it:** either run Agent-Proof on a real class-3 edit from this
  session, or read its `tests/ai-agent-scenarios.test.ts` to see whether any scenario
  is a parses-fine-but-wrong edit rather than a lint-visible one.

## Q3 — Is there a lighter class-3 signal than full pairwise execution?

ChangeGuard proves class 3 is *detectable* (77.1% precision / 69.5% recall) but at the
cost of a fine-tuned CodeT5 model, value injection, and seconds of runtime per change.
That is far too heavy for an every-commit gate, let alone an every-edit one.

- **Why it matters:** the honest invariant I currently assert ("edited Python is
  executed before the session yields") is cheap but non-mechanical — it depends on me
  remembering to run the code, and this session's 7 errors prove that memory is
  unreliable. ChangeGuard is mechanical but too heavy.
- **Unresolved because:** nobody has published a cheap proxy. The arXiv paper offers
  two *test-free* signals that partially recover validity — 3-gram loop detection
  (100% recall, 0% FP on Gemini's abstention tasks) and short-trajectory flags
  (r = −0.26, p<0.001) — but those are *trajectory* signals, not *edit* signals, and
  they predict silent failure rather than detecting a specific bad edit.
- **What would settle it:** measuring whether a hybrid works — cheap trajectory signal
  to *triage* which edits need validation, then pairwise execution only on the
  triaged subset. Unbuilt anywhere I found.
