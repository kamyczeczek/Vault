---
type: Concept
flag: kr-pilot-terminated-2026-10-14
since: 2026-10-14
owner: mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: session-close
title: kr-pilot-terminated-2026-10-14
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`kr-pilot-terminated-2026-10-14` — 2026-10-14: pilot GraphRAG w knowledge-retrieval zamkniety jako terminated, gate not met. Mur #2 (pokrycie semantyczne) naprawiony technicznie i zmierzony apple-to-apple na biezacym kodzie: semantic OFF vs ON (pytanie= przekazane do oblicz_pokrycie, q_emb aktywne, indeks_gotowy=True, embedding 384-dim).

Dane (trust set 33 in-corpus + 15 OOC + 10 boundary, hybryda ON w obu ramionach):
- MRR@5 = 0.295 < 0.4 (gate oblany czwarty raz: trust_set_report 2026-10-11, sesja 1/10, sesja 2/10, sesja 3/10; ranking nietkniety fixem).
- Semantic OFF: false refusals 27.3% (9/33), OOC refusal 66.7% (10/15), BOUNDARY refusal 0.0%.
- Semantic ON: false refusals 0.0% (0/33), OOC refusal 40.0% (6/15), BOUNDARY refusal 0.0%.
- Delta: 13 flipow, wszystkie refuse->answer (9x Q-in-corpus naprawione, 4x OOC O02/O06/O10/O14 zlamane — OOC odpowiada zamiast odmawiac).
- Warianty MIN_KEYWORD 1/2/3: 0 flips odmowy na 58 pytan (galka martwa — sesja 2/10).
- Mechanizm regresji: semantyczne_pokrycie omija bramke MIN_KEYWORD i wymusza has_cov=True przez prog_cosine=0.45; progu nie wolno ruszac (S62), strojenie niedozwolone w tej sesji.

Wniosek: nie istnieje punkt akceptowalny — OFF ma 27% false refusals, ON lamie straznika OOC o 26.7pp (prog akceptacji: max 10pp). Przy MRR@5=0.295 ponizej gate'u pilot nie ma sciezki do przejscia bez nowego retrievera.

Ten artefakt zamyka pilot. Dalsze sesje w tym temacie sa zabronione — wymagana decyzja wlasciciela o nowym kierunku (np. inny retriever, inny gate, inny cel).

not checked:
- czy wlasciciel chce w ogole kontynuowac retrieval w KR (decyzja biznesowa).
- czy gate MRR@5=0.4 jest wlasciwy dla tego zastosowania.
- czy prog_cosine=0.45 dalby sie nastroic na punkt akceptowalny (strojenie progu poza zakresem sesji, S62).
