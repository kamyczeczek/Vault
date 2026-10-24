---
flag: brain-fresh-agent-section-v2-2026-10-16
since: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`brain-fresh-agent-section-v2-2026-10-16` — 2026-10-16: `brain/CONTEXT.md` `## For a fresh agent` przepisana na wersję pełniejszą (+106 linii wobec v1) — wersja kurowana, nie 1:1. Zastępuje i wycofuje `brain-fresh-agent-section-2026-10-16`.

- Źródło: dokument „Instrukcje dla świeżego agenta — warstwa `brain`" (wersja zweryfikowana, opcje A/B/C). Właściciel wybrał opcję A (podmiana sekcji w `brain/CONTEXT.md`) i język angielski, spójny z resztą pliku. `brain.db` gitignored; nie dotknięty.
- Doszło wobec v1: dwie warstwy z rozmiarami (46 / 22 / 2 vs sesje) i kolejność wymuszana przez door; pełna lista komend (brain + session, `get <chunk_id>`); ścieżka retrievalu (`brain.py -> retrieval_v1.py -> brain.db`), pipeline K1 i silnik B1; brak warstwy decyzyjnej + odrzucenie H5 (72.7% vs 81.8%); R21 jako dwie bramki (świeżość/pokrycie + regresja pomiaru), ostrzeżenie tylko przy braku `brain.db`; tabela stanu pomiaru; dwie znane luki; trzy zasady warstwy; lista „czego nie robić".
- Zweryfikowane komendą przed wklejeniem: 46 problems / 22 decisions / 2 lessons (`ingest_brain.py --check`); `eval_brain.py --check` → hit@5=9/10 refusal=3/4 MRR=0.900, obie luki jako `KNOWN-GAP`; `retrieval_v1.py` docstring → family_recall@5 81.5% (22/27), refusal 81.8% (9/11), MRR 0.778; `audit_agents_md.py` `EXPECTED = {routing 8, evidence 23, heading 1, blank 5, total 37}`; `model: current|default` = 12 flag / 13 wierszy (3 current, 10 default); `brain.py` 118 linii; `brain/problems/` tylko `README.md`. Bramka `check_workspace_integrity.py` → OK (34 root entries, 6 projects).

not checked:
- Dokument pisze „1489 sesji / 195 964 chunki"; `memory_index.py stats` na 2026-10-16 → **1508 sesji / 197 944 chunki**. W sekcji jest liczba żywa **i** komenda `stats` jako źródło, żeby ta sama liczba nie zestarzała się po cichu.
- Nie uruchomiono destrukcyjnego dowodu R21 (kasowanie wiersza z `brain.db`) — w sekcji jest przepis, nie re-run. Rekord prawdziwego czerwonego R21: flag `brain-memory-v1-landed-2026-10-16`.
- Liczba „12 flag / 13 wierszy `model:`" w tabeli długów zestarzeje się — to dług, nie pomiar z bramką.
- Nie mierzono, czy sekcja wystarcza świeżemu agentowi — brak testu „czy nowy agent trafia w brain"; to nadal konwencja, nie bramka.
