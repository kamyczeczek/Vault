---
flag: single-repo-codegraph-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`single-repo-codegraph-2026-10-28` — 2026-10-28: monorepo zweryfikowany, CodeGraph indeksuje `projects/` bez `includeIgnored`; `close.py` bez martwego `nested_repos()`.

Stan: plan „jeden prosty monorepo" opisywał pracę wykonaną 2026-10-24/27 — w repo nie ma żadnego zagnieżdżonego `.git` (tylko root), `projects/` jest śledzone i nie jest w `.gitignore`, `library/` (225 MB) ignorowane przez własny `library/.gitignore`, `brain/` to projekt, nie baza. Zamiast powtarzać migrację: `python.exe scripts/memory_index.py ingest` naprawił jedyny FAIL bramki (`memory_index freshness`, lag 1d9h). W `scripts/close.py` usunięto `nested_repos()` i domyślne odkrywanie repo — `repos=` zostaje jako jawne opt-in dla historii odtworzonej z `history.bundle` (D24); odświeżono też `--explain` i docstring `--verify-claims`. CodeGraph 1.6.2 zainstalowany, `codegraph init` → 955 plików / 16514 węzłów / 46811 krawędzi w 8 s; `codegraph query "run_g4"` znajduje `run_g4` w `projects/research/etth1-h720/run_amr_h720_final.py`, czyli `projects/` jest w indeksie bez `includeIgnored`. `.codegraph/` dopisane do `.gitignore`.

Next: opcjonalnie `codegraph install` (MCP do opencode — nie robione, bo dokłada stały koszt prefixu) albo `codegraph telemetry off`.

not checked: pełny CodeGraph query na wszystkich symbolach — sprawdzono `check_includes`, `run_g4`, `run_amr` i `callers check_includes`; zachowanie Obsidiana — danych nie przenoszono; `codegraph deps` nie istnieje w 1.6.2 (użyto `callers`/`impact`); push do GitHuba i świeży `git clone`; `deprioritize` nie ustawiono, bo nie ma zmierzonego problemu z rankingiem.
