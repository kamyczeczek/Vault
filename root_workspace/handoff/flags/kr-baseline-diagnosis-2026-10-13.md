---
flag: kr-baseline-diagnosis-2026-10-13
since: 2026-10-13
owner: mateusz
agent: opencode
model: gemini/gemini-flash-lite-latest
origin: session-close
---

`kr-baseline-diagnosis-2026-10-13` — 2026-10-13: baseline MRR@5=0.295, false refs=48.5%, hipoteza: Głównym wąskim gardłem retrievera KR jest brak dopasowania naturalnych zapytań do słów kluczowych i FTS5 (Recall@10=0.515), a nie ranking czy embeddingi.
not checked: ręczna kwalifikacja 18 pytań ZAWODNE oraz ponowny pomiar po ewentualnej korekcie pytań; etapy rerankingu (brak w pipeline).
To jest sesja badawcza, nie governance. Zero zmian w kodzie.
