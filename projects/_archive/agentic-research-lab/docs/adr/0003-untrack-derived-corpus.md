---
type: Concept
title: 0003-untrack-derived-corpus
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Untrack knowledge/corpus/ — a derived projection does not belong in version control

`knowledge/corpus/` is 10,337 chunk files projected from ~110 raw sources: a
21:1 ratio, 94% of everything the repository tracks. The repository is
effectively a database dump, and reviewing a change to it means reading 10,000
files that no human reads. Untracked 2026-09-28, executing the D5 decision that
has been deferred since 2026-09-19. Tracked files: 10,939 -> 602.

## Considered Options

- **Leave the corpus tracked.** Rejected on the evidence in ADR-0002: git was
  already the source of the damage, holding derived output while the inputs were
  deleted. Tracking a projection invites the same drift.
- **Delete the corpus from history.** Rejected: it is irreversible, it is not
  what the entropy problem calls for, and the chunks are the only surviving
  record of four project-authored write-ups whose subjects were archived.
- **Untrack, keep on disk and in history (chosen).** The files stay, `git log`
  still reaches every one of them, and `git checkout <rev> -- knowledge/corpus/`
  restores any of them. The index stops listing them; nothing is destroyed.

## Consequences

A fresh clone gets 602 files, of which `knowledge/corpus/` is empty until
rebuilt. Rebuild is `python scripts/ingest.py` with sources staged in `INBOX/`.

Chunking is deterministic — no timestamps, no RNG — and was verified rather
than assumed: a source was copied to `INBOX/`, re-ingested, and the resulting
chunk diffed byte-identical against the committed one, modulo CRLF, which
`.gitattributes` (`* text=auto eol=lf`) normalises on checkin. A fresh clone on
Windows will therefore show churn after rebuild until the attributes are
applied; that is pre-existing, not introduced here.

`knowledge/raw/manifest.jsonl` (568 KB) stays tracked. It is the reverse index
— source to chunk ids, with the raw file's sha256 — and it is what lets a clone
know which sources its corpus is missing. Without it the corpus is not
verifiable, only rebuildable.

The D5 rejection of a file-count gate still stands: this is not a rule that
projects may not exceed, it is one project refusing to version a projection.
The gate would have pushed the corpus into an archive; the gate's stated
alternative was to leave it alone, and this is a third path it did not name.
