---
flag: close-py-diff-check-fixes-2026-10-16
since: 2026-10-16
owner: mateusz
agent: pi-bolt
model: nara/deepseek-v4.1-flash-free
origin: session-close
---

`close-py-diff-check-fixes-2026-10-16` — 2026-10-16: Naprawa dwóch defektów `scripts/close.py` ujawnionych w residue-closeout (`1f5e81c`); dokumentacja w `SCARS.md` (S66, S67).

- **S66** — `close.py` obcinał output `run()` do 8 linii przed wypisaniem FAIL. W `1f5e81c` pierwszy FAIL pre-commit pokazał 3 z 13 naruszeń trailing whitespace w `tools/governance_ontology_prototype.py`; pełną listę dał dopiero ręczny `git diff --cached --check`. Fix: kroki `diff-check`/`dry-diff-check` nie trymują outputu (`format_failure`, `FULL_OUTPUT_STEPS`); pozostałe kroki pokazują `... (N more lines)` z podpowiedzią komendy.
- **S67** — `--include` z untracked plikami omijał `diff-check` `close.py` (walidacja `git diff --check` biegła przed `git add`). `1f5e81c` wywalił się dwa razy z tego powodu. Fix: `_intent_to_add()` robi `git add --intent-to-add` na untracked `--include` przed `diff-check` (w `main()` i, z `git reset` po sprawdzeniu, w `dry_run()`).
- **Test regresyjny**: `scripts/test_close.py` +3 testy (`format_failure` pełny dla diff-check / hint dla reszty kroków, `untracked_includes`). 11/11 zielone.
- **Reprodukcja z dowodem**: untracked plik z 13 naruszeniami → przed fixem `dry-run OK` (defekt B), a po ręcznym `intent-to-add` FAIL pokazał 4/13 (defekt A); po fixie ten sam untracked plik bez ręcznego przygotowania → FAIL pokazuje 13/13. Dowód w transkrypcie sesji `01a141be-4882-72fd-bb75-9a6c537d9b1e`; fixtures w `scripts/_scratch/` (gitignored).

not checked:
- Ścieżka `--include` wskazująca plik **gitignored** (np. `scripts/_scratch/*`): `git add --intent-to-add` odmawia z exit 1, więc taki include nadal omija `diff-check`. Nie naprawiono — takiego pliku nie da się też zacommitować bez `-f`, więc to nie krok realnego close.
- Repo bez commita (unborn HEAD): `git reset -- <path>` w `dry_run` nieprzetestowany w tym stanie (repo ma HEAD).
- Nie ruszano `INDEX.md`/`allowed`/`find_strays` — osobny defekt, nie zmaterializował się w `1f5e81c`.
- R18, dług `model: current`, próg K1 — poza zakresem sesji.
