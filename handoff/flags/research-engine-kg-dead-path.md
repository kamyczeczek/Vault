---
flag: research-engine-kg-dead-path
since: 2026-10-10
owner: mateusz
agent: pi
model: nara/muse-spark-1.3-contributor-free
origin: session-close
---

`research-engine-kg-dead-path` — 2026-10-10: research-engine/kg.py jest martwe — FileNotFoundError przy każdym resolve (DB = projects/research/agentic-research-lab/knowledge/graph/graph.db, nie istnieje; żywe archiwum w projects/_archive/). Wykryte żywym eksperymentem w sesji falsyfikatora (Faza 6 Q-refusal, proof w KR ec06683), nie z lektury. Precedens 'istnieje kg.py' (KR findings) fałszywy co do używalności. Dla sesji research-engine: naprawić DB path (albo WORKSPACE_ROOT, albo wskazać _archive), potem resolve('scar')/resolve('SEVerA') jako smoke test. Naprawa należy do sesji research-engine (jeden projekt na sesję), ta flaga to dług, nie diagnoza.
not checked: czy inne skrypty research-engine mają tę samą martwą ścieżkę (sprawdzony tylko kg.py); czy coś w workspace woła kg.py i polega na jego działaniu (find_importers nie uruchomiony); R15/R16 po przyszłej naprawie; Q-ground SEVerA (osobny dług, flaga graphrag-falsifier-v2-next).
