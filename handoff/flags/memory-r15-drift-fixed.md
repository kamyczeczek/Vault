---
type: Concept
flag: memory-r15-drift-fixed
since: 2026-10-10
owner: Mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
title: memory-r15-drift-fixed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`memory-r15-drift-fixed` — 2026-10-10: R15 green 15/15 (hit@5=1.000) po dopisaniu 5 zweryfikowanych non-cause confounders do exclude_session_ids case'u "provider error" (procedura z 1cf7355; zwycięzcy BM25 nie zawierają target error o cx/gpt-5.6-luna-low — tool-dump, extension-lista, minified-JS, LiteLLM-docs). Oczekiwane sesje bez zmian, obie istnieją w indeksie. Root commit 32b1ad1 + KR commit 752e8e1 (falsyfikator GraphRAG v2).

Next: jeśli drift będzie nawracać (keyword-noise wypycha exact-error), to problem rankingu do KR (retrieval-quality), nie kolejne exclusions w nieskończoność.
