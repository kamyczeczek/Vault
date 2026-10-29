---
type: source-slice
title: "okforge — recompile generated wiki pages and protect manual edits"
generated: true
origin: "Notes/OKF-rag/okforge.md"
origin_hash: 3a448dec704beef9ba37f7746e33b110e0c71025c55dd2703930ef91ba81c657
source_lines: [4718, 4735]
source_heading: "`recompile` — regenerate wiki pages"
slice_hash: 0bdc5204ffe1474634754682ae8b11adc18828ebbfc4c5540fa792cf4450da9c
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# okforge — recompile generated wiki pages and protect manual edits

## Source excerpt

## `recompile` — regenerate wiki pages

Re-runs the compile step against already-ingested content (no re-conversion, no
re-indexing):

```bash
openkb recompile attention                      # one document
openkb recompile --all --dry-run                # preview the full set
openkb recompile --all --yes                    # rebuild everything
openkb recompile --all --refresh-schema         # also refresh wiki/AGENTS.md
```

> ⚠️ Recompiling **overwrites** generated summaries and concept pages — any manual
> edits to those are lost. `--refresh-schema` backs up the old `AGENTS.md` to
> `AGENTS.md.bak` before replacing it.

---

## Provenance

- Origin: `Notes/OKF-rag/okforge.md:4718-4735`
- Origin hash: `3a448dec704beef9ba37f7746e33b110e0c71025c55dd2703930ef91ba81c657`
- Regenerate with `python scripts/generate_source_slices.py`.
