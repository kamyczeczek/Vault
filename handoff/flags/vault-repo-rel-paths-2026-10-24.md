---
type: Concept
flag: vault-repo-rel-paths-2026-10-24
since: 2026-10-24
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
title: vault-repo-rel-paths-2026-10-24
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`vault-repo-rel-paths-2026-10-24` — 2026-10-24: przygotowanie `scripts/**` na repo, którego root jest o poziom wyżej (ADR-006). Nowy `scripts/git_paths.py` (`repo_prefix`, `repo_rel`) normalizuje wyjście gita: `git status --short` i `--name-only` drukują ścieżki względem **repo root**, a `ls-files` i pathspecs względem **cwd** — dopóki ROOT był repo rootem, obie bazy się pokrywały. Podłączone w `close.py` (`find_strays`, `_is_staged_deletion`), `pre_close_check.py` (uncommitted work vs `--include`), `scan_secrets.py` (`staged_files`) i bramce R19 (nowe flagi). Bez tego po migracji `find_strays` widziałby `root_workspace/handoff/flags/x.md` i każdy commit byłby czerwony, a R19 po cichu przestałby widzieć nowe flagi (advisory, więc bez błędu). Test `scripts/test_git_paths.py` buduje repo z podkatalogiem w tempie i dowodzi asymetrii: z `sub/` status zwraca `rootfile.txt` i `sub/inner.txt`, `ls-files` zwraca `inner.txt`. `--include` przyjmuje teraz katalog: `find_strays` dopasowuje zawartość po prefiksie, więc 686 ścieżek nie musi wejść w jeden argv.

not checked:
- `build_state.py`, `upgrade_sessions_report.py`, `verify_session_claims.py` czytają `git status` bez normalizacji — używają wyniku tylko do wyświetlania/hasha, nie do porównania ze ścieżką workspace'u; nie ruszane.
- pełny przebieg `pre_close_check.py` i `scan_secrets.py --staged` na żywym repo po migracji — dopiero po przeniesieniu `.git`, bo dziś prefiks jest pusty i ścieżka nowa i stara dają ten sam wynik.
