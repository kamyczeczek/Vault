---
flag: graphrag-falsifier-v2-qground
since: 2026-10-10
owner: mateusz
agent: pi
model: nara/muse-spark-1.3-contributor-free
origin: session-close
---

`graphrag-falsifier-v2-qground` — 2026-10-10: Faza 6 Q-ground EXECUTED. Człowiek wkleił w review abstrakt arXiv:2603.25111v2 (spoza grafu); wpisany do CONTRACT.md (kondensacja 4-blokowa) + plan.json PRZED query. Żywy eksperyment read-only: ask.py top-1 EXACT (source URL = arXiv ID z oracle), body 2 158 / tier 1 / autorzy = oracle. Zgodność claim-by-claim 4/4 MATCH z cytatami body (ryzyko braku gwarancji / FGGM+FOL+fallback / three-stage Search-Verification-Learning / zero violations + tasks). 1 jawna różnica: oracle ma 'constrained symbolic regression', kondensat korpusu tylko 'symbolic math synthesis' — kondensat, nie sprzeczność. Pokrycie krawędziowe 0 (tylko SEQUENCE + bulk PART_OF): dowód treściowy, nie grafowy. Ustalenie protokołowe: kontrola bez narzędzia NIEWYKONALNA w tej sesji (skażona z definicji — sesja widziała węzeł wcześniej); odmówiono teatru, musi biec PIERWSZA w świeżej sesji. Pełne 'grounding udowodniony' czeka na nią. KR commit a802a32 (7 plików, dokładnie mój zestaw); dług KR nietknięty.
not checked: kontrola bez narzędzia (jedyny brak do pełnego grounding — wymaga świeżej sesji, kolejność jawnie w planie); re-run selftestu graphrag.py po commitach KR (regresja Fazy 5 niepotwierdzona na żywym drzewie); pełne body SEVerA poza abstract/heading (kondensat czytany w całości przez query, ale dowód cytuje abstract — dalsze sekcje korpusu nieporównane); R15/R16 po commicie KR; dług KR (4 modyfikacje + untracked, nazwany w kr-state-ordered).
