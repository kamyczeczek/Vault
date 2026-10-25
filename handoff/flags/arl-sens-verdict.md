---
type: Concept
flag: arl-sens-verdict
since: 2026-10-08
owner: mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
title: arl-sens-verdict
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`arl-sens-verdict` — 2026-10-08: NotebookLM run `handoff/notebook-runs/2026-10-08-sens-arl/`
(problem + answer, pack project L2 agentic-research-lab + 5 sesji, notebook `root_workspace`).
Werdykt: TAK, ale tylko jako warunkowy eksperyment weryfikacyjny — zamrozić rozbudowę
infrastruktury/korpusu, jeden pomiar falsyfikujący hipotezę B; przy braku liftu archiwizacja.
Ranking: (a) extended-n rerun hipotezy B [NAJWYŻSZY] > (d) archiwizacja jako research-prototype >
(b) Phase 4-diversity [niski, Goodhart] > (c) phase2c shell-injection [najniższy, anty-wzorzec].
Najsłabsze ogniwo: budżet kontekstu 2500 znaków (perf ON 0.083 = truncation artifact) + moc (n=9).
Next: tani re-scoring rodziny `perf` przy 8000 znaków via `score_ablation_content.py`;
falsyfikacja: brak wzrostu 0.083 -> >=0.400 obala hipotezę dławienia => workstream (d),
anulować plan n>=25.

Follow-up narzędziowy (answer2.md, to samo pytanie w ramie transferu do innych
projektów/rootu): PRZENIEŚĆ — ICM L0-L4 + flagi handoff, deterministyczne gate'y
testowane mutacyjnie (egzekucja via core.hooksPath, nie konwencja), higiena D5/ADR-0003
(library adresowana haszami, pochodne odtwarzane deterministycznie), ewaluator regex +
echo-guard. NIE PRZENOSIĆ — hybrydowe embeddings (FTS5 0.958 vs embeddings 0.0),
integracje MCP dla autonomii (2b: deadlocki), metryki tautologiczne, syntetyczny
meta-learning bez nadzoru (orphan-decision 0.667, dry-retrieval 0.846), guardraile na
trywialnych zadaniach (efekt sufitu). NIEROZSTRZYGNIĘTE: hipoteza B (re-scoring perf
8k jak wyżej), ralph-loop reviewer-LLM vs bramka deterministyczna (micro-run 3 iteracje,
metryki: tokeny + false-SHIP), pamięć sesji (technicznie 15/15, praktycznie
prevented_repeat 0/7 — tani test: twardy hook debug.py po 2. failu, po 10 sesjach
sprawdzić stats --usage).
