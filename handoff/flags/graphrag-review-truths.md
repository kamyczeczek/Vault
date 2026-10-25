---
type: Concept
flag: graphrag-review-truths
since: 2026-10-10
owner: mateusz
agent: pi
model: nara/muse-spark-1.3-contributor-free
origin: session-close
title: graphrag-review-truths
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`graphrag-review-truths` — 2026-10-10: review Fazy 6 wpisane do plików (nie tylko do rozmowy). (1) Niewygodne prawdy w answer-qground.md: oracle == źródło korpusu (MATCH dowodzi proweniencji, nie groundingu; Q-refusal mocniejszy bo oracle z SCARS.md) + body != graf (pokrycie krawędziowe 0, dowód dokumentowy jak ask.py --raw, obok struktury z D-001). (2) Protokół kontroli bez narzędzia jako samowystarczalny control-protocol.md: świeża sesja, zero kontekstu Fazy 6, jedno pytanie, ocena 4× TAK/NIE, trzy rozstrzygnięcia (ogólnikowy=grounding UDOWODNIONY / szczegółowy=Q-ground FAIL jako grounding / przeciek=kontrola skażona) + zakazy (kotwica, teatr). Kontrola niewykonalna w tej sesji z definicji (pełny kontekst Fazy 6). (3) D-005 addendum: warunek wznowienia przepisany z KR na research-engine (bez żywego kg.py nie ma na czym parametryzować; kolejność: fix kg.py → parametryzacja → regresja → archiwum). KR commit 19ced37 (3 pliki, dokładnie mój zestaw); dług KR nietknięty. Nieruszone: close-ritual-coupled (właściciel mateusz), kg.py, higiena KR.
not checked: wynik kontroli bez narzędzia (serce falsyfikatora, wymaga świeżej sesji — ta flaga przygotowuje, nie zastępuje); sekcja terminalna w task_plan.md (czeka na wynik kontroli per CONTRACT.md); re-run selftestu graphrag.py (regresja Fazy 5 nadal niepotwierdzona); R15/R16 po commicie KR; czy control-protocol.md jest czytelny dla obcego agenta (pisany bez testu na żywym odbiorcy).
