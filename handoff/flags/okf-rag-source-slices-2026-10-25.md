---
type: Concept
flag: okf-rag-source-slices-2026-10-25
since: 2026-10-25
owner: codex
agent: codex
model: openai/gpt-5
title: okf-rag-source-slices-2026-10-25
origin: Notes/OKF-rag/EXPERIMENT-source-slices-2026-10-25.md
generated: { by: okf-enforcer/0.6, at: 2026-10-25T04:22:03Z }
---

`okf-rag-source-slices-2026-10-25` — 2026-10-25: wdrożono deterministyczny generator source slices dla `okf-rag.md`, manifest z hashami oraz świeży reindeks Smart Connections; po usunięciu starych wektorów scoped retrieval dał `4/5` top-1 i `5/5` top-5, ale globalny folder nadal preferuje syntezy i decyzje. Następny krok: stosować slice'y tylko dla powtarzalnych missów dużych importów i powtórzyć ten sam test na jednym kolejnym imporcie.
