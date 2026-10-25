---
type: source-slice
title: "okforge — initialize a knowledge base and ingest a document"
generated: true
origin: "Notes/OKF-rag/okforge.md"
origin_hash: 3a448dec704beef9ba37f7746e33b110e0c71025c55dd2703930ef91ba81c657
source_lines: [760, 798]
source_heading: "Step 5: Initialize a Knowledge Base (okforge)"
slice_hash: bbe2dbb4e66a69803698388d17fa76b1bee9d10d8456a285578e4afa0976d16a
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# okforge — initialize a knowledge base and ingest a document

## Source excerpt

## Step 5: Initialize a Knowledge Base (okforge)

okforge compiles your documents into a wiki with cross-linked concepts and entities.

### Initialize the KB

```bash
okforge init --model openai/Qwen3.6-27B-MTP --language en --json
```

Replace the model with whatever you're actually using. For a local llama.cpp server, the `openai/` prefix is correct (it's a generic OpenAI-compatible endpoint, pointed at by `OPENAI_API_BASE`). For OpenRouter, use the `openrouter/` prefix with the same model you set as `OKFORGE_VISION_MODEL` in Step 3:

```bash
okforge init --model openrouter/qwen/qwen3.5-32b-uncensored --language en --json
```

### Add your OCR output

```bash
okforge add source/mydoc.md
```

(Or, for a text-layer PDF you didn't need to OCR: `okforge add source/mydoc.pdf` directly.)

This runs the compile pipeline:
1. **Summary** — the model reads the document and writes a per-document summary, citing pages where `mydoc.pages.json` is available.
2. **Concept plan** — identifies which cross-document concepts and named entities this document touches, and whether each is new or should merge into an existing page.
3. **Generate** — writes (or updates) each concept/entity page.
4. **Index** — updates `wiki/index.md` and the `[[wikilink]]` cross-references between pages.

### Check the result

```bash
okforge status
okforge list
```

---

## Provenance

- Origin: `Notes/OKF-rag/okforge.md:760-798`
- Origin hash: `3a448dec704beef9ba37f7746e33b110e0c71025c55dd2703930ef91ba81c657`
- Regenerate with `python scripts/generate_source_slices.py`.
