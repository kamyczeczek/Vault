---
type: Concept
title: 2026-09-16_corpus-chunk-ids-not-unique
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Reflection — corpus chunk ids are no longer unique keys

Date: 2026-09-16
Project: projects/workspace-research
Trigger: T4 (a structural defect found while extending the corpus)

## Problem

After ingesting 4 new findings, corpus chunk ids stopped being unique. Each multi-part
source is written as `00_<slug>` / `01_<slug>` using a **per-source part index**, so the
`NN_` prefix carries no source identity — it only says "this is part N of something".
The corpus now has 12 files matching `06_*`, 12 matching `07_*`, 12 matching `08_*`, and
12 matching `09_*.

Concretely, `06_self_evolving_world_models_for_llm_agent_plannin.md` (part 6 of a 28-part
source) and `06_self_correction_grounding_requirement.md` (part 1 of a 2-part source) are
different documents that share a prefix. The slug disambiguates the *file*, but the id
namespace is flat and the prefix is meaningless as a key.

## Root cause

`ingest.py:write_chunk` builds `cid = f"{seq}_{slug}"` where `seq` is the part number
within one source, then writes to a flat `knowledge/corpus/` directory. Two assumptions
broke: that `NN` was globally unique, and that a flat directory of `<part>_<slug>` names
would not collide. Both held while the corpus had few multi-part sources, and both fail
once several sources each produce parts with the same index.

The collision is invisible to the manifest gate, which resolves by `source:` frontmatter,
and to the graph, which indexes on the file path. It is visible to anything that treats
the id as a stable reference — which is exactly what `reflection/` citations and
`ask.py` output do.

## Impact

- Citations like `04_honest_lying_memory_confabulation` still resolve because their slugs
  are unique across the corpus. The risk is future ingest of a source whose slug collides
  with an existing one, which would **overwrite** chunks silently.
- Id-based lookups are prefix-ambiguous. `ask.py` returns paths, so retrieval keeps
  working, but a consumer matching on bare id can match the wrong chunk.
- Any renumbering fix re-stamps every existing citation, since chunk ids are embedded in
  all 9 reflection digests and candidate files.

## Decision

**Left unfixed deliberately.** This is not a silent suppression — the options are:

1. **Global source index**: prefix by source insertion order (`ingest.py` already has a
   sorted-source loop; the index exists, it is just not used in the id). Breaks every
   existing id and citation.
2. **Source-hash prefix**: id derived from the source name, so parts of one source share a
   namespace. Same breakage cost.
3. **Unique-slug guard**: reject or disambiguate at ingest time when a generated id
   already exists. Backwards-compatible, prevents *new* collisions, does not fix the
   existing 44 ambiguous prefixes.

Option 3 is the safe incremental step; 1 or 2 is the correct fix but costs a full
re-stamp of the reflection layer. That tradeoff needs a human decision because it trades
current citation stability against long-term key integrity.

## Prevention rules

- **R1 — an id is a key, not a label.** If a field is used to reference a record from
  elsewhere, its generator must guarantee global uniqueness by construction, not rely on
  the string happening to differ. A per-source counter in a flat namespace cannot do that.
- **R2 — the gate must check the invariant it depends on.** The manifest gate validates
  provenance and coverage, both of which still pass here. Uniqueness of `id` across
  `knowledge/corpus/*.md` is a separate invariant and is currently untested — add it to
  `check_manifest.py` so the next ingest that collides fails loud instead of overwriting.
- **R3 — distinguish "derived index" from "stable reference".** The manifest correctly
  derives from `source:` frontmatter and so survived the collision. Anything *cited* needs
  the same property: citations should resolve through a field that cannot collide, or the
  collision must be made impossible upstream.
