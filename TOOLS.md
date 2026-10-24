# TOOLS.md — tool lifecycle

A tool is a project (D1). This file holds only the part that is *not* a
project: the bar a tool must clear, and what happens to it after. A tool that
needs its own home has one under `projects/research/`.

Vocabulary: `GLOSSARY.md`. Where tools sit relative to each other:
`CONTEXT-MAP.md`. Why the lifecycle is shaped this way, and what was rejected:
`DECISIONS.md` (D1–D3).

## The three verdicts

Same vocabulary the forecasting models use (D2). A tool is not promoted on
impression; it is promoted on recorded measurements plus a stated bar.

| Verdict | Means | What survives | Where it goes |
|---|---|---|---|
| **PROMOTE** | Meets the bar, with the measurements recorded | The code and the evidence | Copied into the target project, source deleted **in the same commit** (D3) |
| **REJECT** | Does not work | The negative result and why | Stays a project, marked `grade: candidate`, evidence in place. Not deleted — the measurement is the value |
| **DEMOTED** | Worked, no longer earns its place | The code, demoted, plus the measurement that demoted it | Stays, marked `grade: demoted` |

REJECT and DEMOTED differ only in the *reason* the tool stopped being
interesting. A rejected tool failed; a demoted one succeeded and was
superseded. Both keep their evidence. That is what "the workspace carries its
own negative results" means in practice.

## The bar

A tool is promoted only if **all** of these are recorded in its own project:

1. **A stated bar, written before the measurement.** Not "it felt better" —
   a number, or a named comparison against a baseline.
2. **A measurement against that bar.** The actual run, with the data it ran on.
3. **A named target project** — where the code goes if it is promoted. A tool
   that does not know its destination is not ready to be graded.
4. **The negative case.** What the tool does *not* do. A tool with no known
   failure mode has not been tested.

Recording the bar before measuring is the part that matters. A bar written
after the result is always satisfied.

## Worked example

`knowledge-retrieval` is the one project in the portfolio built to this shape
already. Its retired metric, with the three proofs that retired it, is in
`projects/research/knowledge-retrieval/references/measurements.md` — that file *is* the
standard: a measurement, the bar it was measured against, and what replaced it.

## Register

Every tool's current verdict, in one line each. Add a row when a project is
graded; never delete one.

| Tool | Project | Verdict | Bar | Evidence |
|---|---|---|---|---|
| _(none yet)_ | — | — | — | — |

Small tools (form 0: one file = one job = one `--selftest`) live in `tools/` —
router: `tools/README.md`. No verdict yet: grading (bar + named target project)
applies when a tool gains its second consumer. Standing 2026-10-08: 4/4
`--selftest` PASS (precedent_index 5 ADR + 13 scar; brief 1924 chars / 4
sections; brief_eval hits 5/5 vs bar 3/5; scar round-trip).

## After the verdict (D10)

- **DEMOTED → in place first.** Mark `grade: demoted`, keep the measurement. Still gated.
- **Then `_archive/`.** After cooling or explicit call, move the folder to `projects/_archive/` (ungated graveyard, unrouted). One home: lowercase only.
- Experience stays local (D11): the project's `docs/adr/` + `## Open work` move with it. Root never copies.
