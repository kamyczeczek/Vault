---
type: Concept
flag: graphrag-session-1-commit-pending
since: 2026-10-11
owner: mateusz
agent: jcode
model: jcode-v0.94.0
title: graphrag-session-1-commit-pending
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Sesja 1 — pakiet do commita (Korekta 2b)

## Stan weryfikacji artefaktu (`ARTIFACT_VERIFIED`)
Uruchomiono skrypt weryfikacyjny `verify_fixed_v2.py` względem `graphrag_fixed_v2.json`. Wszystkie 5 grup (`in_corpus_pl`, `in_corpus_en`, `ooc_pl`, `ooc_en`, `canary`) zostały zweryfikowane pomyślnie z tolerancją 1e-3 (`VERDICT: OK: all groups match D2`).

## Rozstrzygnięcie K1, K2, K3
- **K1 (Pliki `handoff/real_case_62b1e12d.*`)**: Pliki nigdy nie były commited w historii git (`never committed`). ID `62b1e12d` koresponduje z zewnętrzną sesją w systemie. Rekomendacja: wykluczyć z commita naprawczego GraphRAG i pozostawić jako untracked lub przenieść do `handoff/deep/`.
- **K2 (Skrypt `scripts/move_state_description.py`)**: Skrypt zawierał `shutil.rmtree`. Wybór opcji (b): przenieść skrypt do `scripts/oneoff/` z nagłówkiem `"""Executed 2026-10-11. Do not re-run."""` i zastąpić w `scripts/` bezpiecznym shimem bez usuwania plików.
- **K3 (Dług w `knowledge-retrieval/CONTEXT.md`)**: Tabela referencyjna w `CONTEXT.md` (linie 68–76) wskazuje, że `mean_family_precision` 0.746 (z wiadomości commitu C-6) nie ma przypisanego artefaktu na dysku (artefakt ma 0.629 przy fingerprintie `0a5b47437367`). Rekomendacja: pozostawić jako otwartość badawczą do rozstrzygnięcia w Sesji 3.

## Zmiany w projekcie knowledge-retrieval
```text
 M CONTEXT.md
 M MAP.md
 M pilots/graphrag/SCARS.md
 M pilots/graphrag/eval/artifact_manifest.json
 M pilots/graphrag/graphrag.py
 pilots/graphrag/proof/graphrag/czym-jest-severa-i-jak-sie-ma-do-self-evolving-agents/answer.md
 pilots/graphrag/proof/graphrag/czym-jest-severa-i-jak-sie-ma-do-self-evolving-agents/plan.json
 pilots/graphrag/proof/graphrag/czym-jest-severa-i-jak-sie-ma-do-self-evolving-agents/trace.md
 pilots/graphrag/proof/graphrag/jaki-wpis-dodala-sesja-04-do-scarsmd-w-sprawie-crlf/plan.json
 pilots/graphrag/proof/graphrag/jaki-wpis-dodala-sesja-04-do-scarsmd-w-sprawie-crlf/trace.md
```

## Zmiany w workspace root
```text
 M CLAUDE.md
 M HANDOFF.md
 M MAP.md
 M STATE.md
 ?? handoff/flags/graphrag-refusal-and-cross-lingual-fixed.md
 ?? handoff/flags/graphrag-session-1-commit-pending.md
 ?? handoff/real_case_62b1e12d.jsonl
 ?? handoff/real_case_62b1e12d_report.md
 ?? handoff/state_description/
 ?? scripts/move_state_description.py
```

## Proponowany podział commitów (spójny z `git log`)
1. `graphrag: naprawa coverage PL i refusal OOC EN bez bibliotek zewnętrznych` — ścieżki: `projects/research/knowledge-retrieval/pilots/graphrag/graphrag.py`, `pilots/graphrag/eval/artifact_manifest.json`, `pilots/graphrag/SCARS.md`.
2. `chore: aktualizacja handoff, state, map i flag sesyjnych` — ścieżki: root `HANDOFF.md`, `STATE.md`, `MAP.md`, `CLAUDE.md`, `handoff/flags/`.

## Decyzja wymagana
- [ ] Zaakceptuję podział commitów
- [ ] Odrzucam / zmieniam zakres
