---
flag: chain-non-convergence-2026-10-14
since: 2026-10-14
owner: mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: session-close
---

`chain-non-convergence-2026-10-14` — 2026-10-14: 11 sesji, dwa otwarte tematy, zero konwergencji. Eksport: 4 sesje, L1-contracts 506 KB (winowajcy: HANDOFF.md 174 KB + ARL/MAP.md 115 KB w archiwum). Retrieval: sesja 1/10 zmierzyla T18 (MRR@5=0.295, gate oblany), sesja 2/10 (ta) zmierzyla trzy warianty MIN_KEYWORD_MATCHES=1/2/3: zero flips odmowy na 58 pytaniach (36 pytan zmienia n_pokrytych, 0 zmienia odmowa). Galka progu martwa w teście; pokrycie semantyczne (prog_cosine) martwe w measure_trust_set.py (brak arg pytanie -> q_emb None).

Wzorzec: kazda sesja uczciwie raportuje „CZEKAM NA DECYZJE", nastepna dostaje identyczny stan, bo warunek stopu obu tematow (wybor wariantu progu, zgoda na podzial build_handoff) lezy poza uprawnieniami sesji. Lancuch nie konwerguje nie dlatego, ze sesje sa zle — dlatego, ze decyzja nie jest podejmowana.

Ten artefakt zamyka lancuch jako finding. Dalsze sesje w tym samym celu sa zabronione — nastepna sesja w tym temacie musi miec jedno z: (a) decyzje wlasciciela o wariancie progu T18, (b) decyzje wlasciciela o podziale build_handoff, (c) formalne zamkniecie pilota KR jako „terminated, gate not met".

not checked:
- czy wlasciciel chce w ogole kontynuowac pilot KR (decyzja biznesowa, nie techniczna).
- czy L1-contracts ma byc rozwiazany przed czy po T18.
