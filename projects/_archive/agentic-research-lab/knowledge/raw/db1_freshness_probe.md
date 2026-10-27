---
type: Concept
id: 00_db1_freshness_probe
title: "DB-1 Freshness Probe Marker Chunk"
source: "VERA DB-1 experiment, 2026-09-24 — ingested to measure time-to-visible through the single-graph read path"
tags: [agentic, retrieval, freshness, db1-probe]
trust_tier: 3
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Freshness Probe Marker

This chunk exists only to test ingestion-to-retrieval latency for the VERA DB-1 experiment.

**Probe fact (DB1-P1):** the marker value is `DB1-FRESHNESS-2026-09-24`, retrievable only after
the ingest + `build_graph.py` + `watch.py` pipeline has run for this chunk.

**Expected retrieval behavior:** `ask.py "DB1-FRESHNESS-2026-09-24"` returns 0 matches while the
chunk is uningested, and ≥1 match (this chunk) after rebuild. Any agent reading stale results
post-rebuild has a stale-read incident to log.
