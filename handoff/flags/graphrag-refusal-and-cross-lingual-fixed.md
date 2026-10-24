---
flag: graphrag-refusal-and-cross-lingual-fixed
since: 2026-10-11
owner: mateusz
agent: jcode
model: jcode-v0.94.0
---

# GraphRAG — naprawa mechanizmu Refusal (OOC EN) i Cross-Lingual Coverage (in-corpus PL)

- State: Zdiagnozowano i naprawiono wady pilota `graphrag.py`: (1) Wprowadzono słownikowe mapowanie słów kluczowych PL→EN (`PL_TO_EN_MAP`) w `zbuduj_plan`, podnosząc coverage dla in-corpus PL (refusal spadł z 5/10 do 0/10, Recall@5 wzrosł z 0.650 do 0.900, MRR@5 z 0.408 do 0.783). (2) Rozszerzono `STOPWORDS` o generyczne terminy angielskie i polskie (OOC EN i OOC PL), uzyskując 5/5 (100%) refusal dla OOC EN (spadek z 0/5) bez degradacji abstynencji na Canary (5/5) i OOC PL (5/5). Selftest PASS, integrity check OK.
- Next step: Zachować bieżący stan jako wzorcowy baseline odporności/abstynencji GraphRAG; opcjonalnie wdrożyć do finalnej integracji z repozytorium KR.
