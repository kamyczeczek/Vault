---
flag: archive-provenance-2026-11-06
since: 2026-11-06
owner: Mateusz
agent: deepseek-harness
model: nvidia/stepfun-ai/step-5-preview
---

`archive-provenance-2026-11-06` — 2026-11-06: Sesja 2 planu (archive investigation) zamknięta bez zmian w drzewie. Pochodzenie dużych blobów wyjaśnione, rozbieżności między audytami rozstrzygnięte dowodowo.

## Wykonane (pomiary na HEAD, `git ls-tree -r -l HEAD projects/_archive`)

- `projects/_archive/` = **3154 śledzonych plików, 255,5 MB** sumy po ścieżkach / **244 MB** po deduplikacji treści. Repo na dysku: 6 paków, 193 MiB (`git count-objects -vH`).
- Największe bloby — wszystkie z legitnym pochodzeniem (archiwa projektów, nie śmieci):
  - `projects/_archive/agentic-research-lab/subprojects/ecc/history.bundle` 51,7 MB (git-bundle historii subprojektu ECC)
  - `projects/_archive/workspace-research/knowledge/graph/graph_index.json` 37,5 MB (graf wiedzy)
  - `projects/_archive/agentic-research-lab/history.bundle` 34,2 MB (git-bundle ARL)
  - `projects/_archive/workspace-research/knowledge/graph/graph.db` 28,7 MB (baza grafu)
  - `projects/_archive/agentmemory-20261001-210803/iii.exe.bak` 28,1 MB (backup binarny exe)
  - `projects/_archive/ts-diverse-pre-split/history.bundle` 11,0 MB; `timeseries_model_discovery_project/history.bundle` 7,0 MB; plus 2 puste (0 B) bundły
- Kopie w archiwum: jedyna prawdziwa kopia treści to PDF „From Plan to Action…” (8,5 MB) w 2 ścieżkach — `projects/_archive/ai_workspace/` i `projects/_archive/workspace-research/knowledge/raw/` — **ten sam blob** `8148b917`; git trzyma treść raz. Reszta duplikatów to stubsy `index.md` (93×/53×/15× te same blob-y) — bez realnej wagi.
- Rozbieżności audytów z 2026-11-05 — rozstrzygnięte: `docs/audit-vault-simplification-final-2026-11-05.md` (0 wspólnych plików między `_archive` a `_archive.backup-20261104`) miał **rację**; `docs/audit-vault-simplification-2026-11-05-corrigendum.md` l.12 („DUPLIKATE – ten sam zbiór") miał **błąd**. Backup (`projects/_archive.backup-20261104/`, 3152 pliki, 291 MB) został usunięty commitem `e5eaa4c` (2026-11-05, „not used by active projects, 0 common files with _archive") — stąd audyty wcześniejsze twierdziły, że katalog istnieje, a bieżące drzewo go nie ma. Sprzeczność była czasowa, nie merytoryczna.
- filter-repo: usunięcie dużych blobów z HEAD same nie kurczy repo (paki trzymają je przez historię); redukcja wymaga przepisania refs — nadal decyzja właściciela, osobny commit (wszystkie SHA się zmieniają).
- Obserwacja konserwacyjna (bez działania): `git count-objects -vH` zgłasza `garbage: .git/objects/f4/tmp_obj_rUS5zQ` (196 KiB) — tymczasowy obiekt, do posprzątania przy okazji `git gc --prune=now`.

## Ryzyka / not checked

not checked:
- Pochodzenie poza samymi blobami: eksport ZIP backupu (`backup-export-20261105.zip` z audytu) nie zweryfikowany na dysku poza repo.
- Czy bundły `history.bundle` zawierają sekrety — objęte skanem z sesji 1 (0 trafień), ale tylko regexami skanera.
- Faktyczne użycie blobów przez aktywne projekty (0 referencji kodu poza ścieżką — zgodnie z mapą zależności z `91a7f6a`).

## Następny krok

Decyzja właściciela: (a) redukcja archiwum przez filter-repo/gc osobny commit, (b) zostawić. Równolegle Sesja 3: raport martwych skryptów na podstawie mapy z `91a7f6a` — analiza bez kasowania.
