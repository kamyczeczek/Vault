---
folder: docs/wayfinder-brain-answers/
role: per-ticket answers for docs/wayfinder-brain-map.md
contract: one resolved ticket = one file; the map links it, never copies
---

# `wayfinder-brain-answers/` — where the map's answers live

The map (`docs/wayfinder-brain-map.md`) is an **index, not a store** (wayfinder). Each
resolved ticket's answer lives here, one file per ticket. The map's `## Decisions so far`
carries one line per closed ticket — a name, a link, a gist — and nothing else.

## Convention

- **Name:** `B<N>-<slug>.md`, where `B<N>` is the ticket id in the map's Tickets table.
- **Execution tickets (E<N>):** answers for `docs/wayfinder-brain-execution-map.md`
  live here too, named `E<N>-<slug>.md`.
- **Frontmatter:** `ticket`, `status`, `resolved`, `owner`, `agent`, `model`, `decision`.
- **Body:** the question; the decision; the alternatives rejected and by whom; the evidence.
- **Evidence, not claims:** every number has a file path or a pasted raw output. A success
  criterion carries an **adversarial case written before the run** (S56, S62) — a gate that
  was never shown failing is not a gate.
- **`not checked:`** is required: what was *not* verified.
- No tracker is configured (`docs/agents/issue-tracker.md` absent), so this directory **is**
  the local-markdown ticket store for `docs/wayfinder-brain-map.md`.

## Files

| Ticket | File | Status |
|---|---|---|
| B1 — drift surface of non-opencode stores | `B1-drift-surface.md` | resolved (research) |
| B3 — `close.py --verify-claims` (scope + failure mode) | `B3-verify-claims.md` | resolved (grilling) |
| B7 — content-hash in `brain_eval.json` anchors | `B7-content-hash-anchors.md` | resolved (grilling) |
| B9 — isolated reflection worker | `B9-reflection-worker.md` | resolved (research) |
