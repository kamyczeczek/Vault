---
type: Concept
title: okf_methodology_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Open Knowledge Format (OKF) Methodology & Architecture Specification (v0.2)

## Overview & Disambiguation
The Open Knowledge Format (OKF) specification (v0.1 / v0.2) and associated Lore methodology define a standardized, machine-readable, and graph-native format for structuring human and autonomous agent knowledge. It must be disambiguated from the Open Knowledge Foundation (OKF / okfn.org). OKF v0.2 provides an authoritative blueprint for decentralized research repositories, combining strict YAML frontmatter ontologies, graph semantics, verifiable provenance, and trust-tiered execution.

## Core Architectural Pillars
1. **Frontmatter Ontology**: Every knowledge chunk or node requires a strictly validated schema containing unique identifiers (`id`), descriptive titles (`title`), source provenance (`source`), and rich semantic tags (`tags`).
2. **Graph Semantics & Edges**: Beyond simple hierarchical markdown files, OKF represents knowledge as a directed acyclic or cyclic graph where nodes are linked via explicit semantic edge types (e.g., `derives_from`, `supports`, `refutes`, `contradicts`, `extends`).
3. **Provenance & Trust Tiers**: OKF distinguishes between raw intake documents (Tier 0), synthesized corpus notes (Tier 1), peer-reviewed or verified literature (Tier 2), and cryptographically attested computations or agentic traces (Tier 3).
4. **Attested Computations**: Execution runs, reasoning traces, and benchmark evaluations are stored as verifiable artifacts, ensuring reproducibility and complete auditability across multi-agent research labs.

## Ecosystem Implementations
- **Lore**: CLI and orchestration engine for managing OKF repositories.
- **okf-ingest**: Ingestion pipeline converting unstructured raw documents (PDFs, Markdown, Web dumps) into valid OKF chunked markdown files.
- **OKFgraph / neo4j-okf**: Graph database synchronization layers that map OKF markdown frontmatter and inline citations into Neo4j or SQLite FTS5 graph backends.
- **openknowledge.sh**: Community registry and protocol for sharing OKF-compliant research bundles.

## Architectural Implications for Agentic Research Workspaces
When comparing OKF v0.2 + Lore methodology against our current `agentic-research-lab` workspace:
1. **Alignment**: Both architectures utilize YAML frontmatter, SQLite FTS5 knowledge graphs, automated build watches (`watch.py`), and quality check gates.
2. **Divergence & Evolution Areas**:
   - **Explicit Edge Semantics**: While our graph builds edges via shared tags or citations, OKF formalizes explicit graph edge files or frontmatter reference arrays (`references: [...]`, `edges: [...]`).
   - **Provenance Tracking**: OKF maintains strict trust-tier metadata in frontmatter, whereas our corpus relies primarily on source family mapping.
   - **Progressive Disclosure**: OKF emphasizes granular chunking with cryptographic/hash fingerprints for change detection.
