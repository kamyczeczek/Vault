---
flag: graphrag-pilot-scaffolded
since: 2026-10-10
owner: Mateusz
agent: opencode
model: muse-spark-1.3-contributor-free
origin: user "no solve GraphRAG agent" 2026-10-10; spec: goose 20261008_3 (sesja 05)
---

`graphrag-pilot-scaffolded` — 2026-10-10: rusztowanie pilota GraphRAG stoi
w `projects/research/knowledge-retrieval/pilots/graphrag/`. Trasa A (pilot
w KR, nie osobny projekt) — decyzja użytkownika; KR jest kandydatem z flagi
`arl-transfer-pivot` (Faza 2), GraphRAG jego pierwszym pilotem.

Scaffold: `CONTRACT.md` (kontrakt pilota) + `task_plan.md` (fazy 1–4
complete z transcriptu sesji 05, 5–6 pending) + `findings.md` + `progress.md`
+ `.wayfinder/MAP.md` + bilety D-000 (resolved: trasa A) .. D-005 (open).
Wpis w KR `CONTEXT.md ## Open work`. Kod implementacyjny dopiero po D-002
(backend) i D-003 (seed) — rusztowanie nie decyduje po cichu.

Bramy: `diff --check` czysty; MAP `--check` current; KR preflight READY.
Root integrity FAIL wyłącznie na stanie zastanym (6 śmieci root po sesji
NotebookLM 08-10 + lag indeksu R14) — pilot nie dokłada żadnego FAIL.

Next: rozstrzygnąć D-002 (read-only na archiwalnym graph.db vs własny
mini-graf) — od niego zależy D-003 i cała Faza 5. Done to NIE "projekt
powstał" — done to dowód na 1 pytaniu (plan JSON → trace → odpowiedź
z dowodami + confidence, 0 nieuzasadnionych twierdzeń).
