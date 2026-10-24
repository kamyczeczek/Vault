---
name: grill-recorded
description: A relentless grilling interview that records every turn to the hash-chained session ledger, then writes the settled decisions to ADRs and the resolved vocabulary to CONTEXT.md. Use when the user wants a design conversation whose outcome must survive the session.
disable-model-invocation: true
---

This is `grill-with-docs` plus a ledger. The interview is unchanged — same
`grilling` rounds, same `domain-modeling` vocabulary discipline — but every turn
is written down as it happens, so the conversation is provenance rather than
something to reconstruct from memory afterwards.

## Open the ledger first

Before asking anything:

```bash
cd projects/agentic-research-lab
SID=$(python scripts/record_turn.py start <workspace-name>)
```

Keep `$SID` for the whole session. The ledger is
`knowledge/graph/sessions.db` unless you pass `--db`.

## Record every turn

Write the question, the user's answer, and any decision or term as its own turn.
Do not batch them at the end — a summary written from recall is not a record.

```bash
python scripts/record_turn.py turn "$SID" question --actor agent --round 1 \
  --question-id Q1 --text "<the question, including your recommendation>"

python scripts/record_turn.py turn "$SID" answer --actor user --round 1 \
  --question-id Q1 --text "<the user's answer, in their words>"

python scripts/record_turn.py turn "$SID" decision --actor agent \
  --decided-by user --text "<what was settled>"

python scripts/record_turn.py term/insight --actor agent --text "<...>"
```

The event vocabulary is closed. The eight types are `user_message`, `answer`,
`agent_message`, `question`, `decision`, `term`, `insight`, `open_question`. The
agent may not write `user_message` or `answer`, and the user may not write
`decision`, `term`, or `insight`: a turn records who actually said it, so a
misattributed turn is refused rather than stored. If a turn is long or full of
quotes, pipe it — `--text-file` and stdin both work, and shell quoting mangles
neither:

```bash
cat > /tmp/turn.txt <<'EOF'
...the full text...
EOF
python scripts/record_turn.py turn "$SID" decision --actor agent --text-file /tmp/turn.txt
```

Record an unresolved thread as `open_question` rather than leaving it implied.
An unrecorded gap reads later like a decision nobody made.

## Close the session

```bash
python scripts/record_turn.py close "$SID"
```

This verifies the hash chain before sealing the session, and refuses to finish a
session whose history was edited. Exit non-zero means the ledger is wrong —
investigate rather than retry.

## Then write the artifacts

The ledger is provenance; these are the product. On close:

- A decision that is hard to reverse, surprising, and had a real trade-off gets
  a file in `docs/adr/`, following `ADR-FORMAT.md`.
- A term that was ambiguous gets resolved inline into `CONTEXT.md`.
- Anything that does not meet the ADR bar stays in the ledger only.

Do not manufacture artifacts to look thorough. The bar is in
`domain-modeling`; the ledger records everything, the docs record what earns
them.
