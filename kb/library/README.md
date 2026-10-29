---
type: Concept
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Library — raw source material

Source documents (books, papers, transcripts) that projects cut their corpora
from. One copy per content hash, shared by every project that cites it.

This is the answer to a concrete loss, not a tidy-up. `knowledge/corpus/` holds
10,337 chunks derived from 154 raw sources, and 6,544 of those chunks (63%)
have a source that exists nowhere — not on disk, not in git, not recoverable.
Six `.md` sources were never committed at all, and seven PDFs were deleted
outright in commits `0d075d7` and `74b922e` (2026-09-21). For those documents a
chunk is the only surviving copy.

## Layout

```
library/
  index.json                 # committed; title, sha256, size, citing projects
  <sha256[:2]>/<sha256>.pdf # the bytes; never committed
```

Content-addressed rather than filed by title because a 40 MB book re-downloaded
from a different mirror is the same bytes, and a title-based layout would let
the duplicate in silently. The address is the hash, so identical content is
stored once by construction.

## Why the bytes are not in git

The material here is books, much of it z-library. Committing it would put
tens of megabytes of copyrighted work into permanent history, unrecoverably.
`index.json` is committed instead: it is small, it diffs meaningfully, and it
makes "which sources exist, and which project cites each" a reviewed fact
rather than tribal knowledge. Losing the bytes is recoverable — re-download
them from `index.json`. Losing them from history is not.

## Adding a source

```bash
python library/add.py "path/to/book.pdf" --title "Book Title"
```

The script hashes the file, stores it under its digest, and adds an entry to
`index.json`. Re-adding identical content is a no-op, not a duplicate.

## How projects cite it

Chunks keep a bare filename in their `source:` frontmatter — 10,337 files are
not being rewritten to gain a property the index already answers. Resolution
order in `projects/agentic-research-lab/scripts/check_entropy.py` is: the
project's own `knowledge/raw/`, then git-tracked files, then this index.
