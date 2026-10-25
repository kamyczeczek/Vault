---
type: Concept
flag: graphrag-falsifier-v2-next
since: 2026-10-10
owner: Mateusz
agent: opencode
model: opencode/muse-spark-1.3-contributor-free
title: graphrag-falsifier-v2-next
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`graphrag-falsifier-v2-next` — 2026-10-10: falsyfikator v2 gotowy w CONTRACT.md (Q-refusal wykonywalny dziś, Q-ground czeka na ludzkie oczekiwanie). Dla człowieka: wpisać oczekiwanie Q-ground (SEVerA vs self-evolving agents) ze źródła spoza grafu, np. abstrakt z arXiv zweryfikowany ręcznie. Dla następnego agenta: uruchomić Q-refusal + Q-ground, wyprodukować proof/falsifier-*/, ocenić grounding per warunek z CONTRACT.md; jeśli R15 padnie ponownie — iść do memory_index.py, nie do eval_queries.json. Alternatywnie: zamknąć pilot jako „kontrakt zweryfikowany, grounding odłożony" i iść do bramy transferowej ARL.
