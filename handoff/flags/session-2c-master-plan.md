---
type: Concept
flag: session-2c-master-plan
since: 2026-10-11
owner: mateusz
agent: jcode
model: jcode-v0.94.0
title: session-2c-master-plan
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Master plan — Sesja 2c

## 0. Stan wejściowy

- `check_workspace_integrity.py`: **OK** (`OK: workspace root holds 28 declared entries, 6 projects, all routing links resolve`).
- `git status --short`:
  ```text
  M HANDOFF.md
  M STATE.md
  ?? handoff/flags/graphrag-refusal-and-cross-lingual-fixed.md
  ?? handoff/flags/graphrag-session-1-commit-pending.md
  ?? handoff/real_case_62b1e12d.jsonl
  ?? handoff/real_case_62b1e12d_report.md
  ?? handoff/state_description/
  ?? scripts/move_state_description.py
  ?? projects/research/knowledge-retrieval/pilots/graphrag/eval/verify_fixed_v2.py
  ```

## A. Self-configuration review

### A.1 Inwentaryzacja
- `~/.jcode/config.toml`: Przeanalizowany (kluczowe sekcje: `[server]`, `[display]`, `[features]`, `[tools]`, `[provider]`, `[agents]`, `[hooks]`, `[gateway]`, `[compaction]`).
- `%APPDATA%\jcode\`: Pliki środowiskowe (nie odczytywane bezpośrednio ze względów bezpieczeństwa kluczy).
- `~/.jcode/skills/`: Dostępne globalne skille i reguły.

### A.2 Tabela defekt → klucz
| # | Defekt (dowód) | Kandydat na klucz | Obecna | Proponowana | Ryzyko | Test |
|---|---|---|---|---|---|---|
| 1 | Zmyślone/niedokumentowane liczby w D2 (Sesja 2/5) | `NOT_FOUND` (brak klucza w `config.toml` kontrolującego formatowanie D2; kwestia promptu/procedury) | `ABSENT` | `ABSENT` | Niskie | - |
| 2 | Brak wymaganego `git log` w raporcie (Sesja 2/5) | `NOT_FOUND` (wymóg instrukcji sesyjnej, brak wsparcia natywnego w config.toml) | `ABSENT` | `ABSENT` | Niskie | - |
| 3 | Pętla `[auto] Do more validation` ×5 (Sesja 1/5) | `NOT_FOUND` (autovalidation trigger sterowany przez silnik sesyjny jcode) | `ABSENT` | `ABSENT` | Średnie | - |
| 4 | `shutil.rmtree` w skrypcie migracyjnym (Sesja 1/5) | `NOT_FOUND` (ochrona plików w workspace realizowana przez skrypty typu `root_deletion_guard`, nie config jcode) | `ABSENT` | `ABSENT` | Niskie | - |
| 5 | Duplikat `def zbuduj_plan` w kodzie (Sesja 1/5) | `NOT_FOUND` (błąd edycji kodu przez model) | `ABSENT` | `ABSENT` | Niskie | - |
| 6 | PRZEDWCZESNE `ZAMKNIĘTE Z DOWODAMI` (Sesja 1/5) | `NOT_FOUND` (interpretacja instrukcji przez agenta) | `ABSENT` | `ABSENT` | Niskie | - |

### A.3 Wnioski: co naprawialne configiem
Żaden z wymienionych defektów proceduralnych i behawioralnych nie jest bezpośrednio adresowalny za pomocą kluczy w `~/.jcode/config.toml`. Harness jcode odpowiada za zarządzanie pętlą wykonawczą, MCP i providerami, natomiast dyscyplina raportowania (D0–D5), unikanie `shutil.rmtree` czy dbałość o dokładność liczb są regulowane przez instrukcje workspace (`AGENTS.md`, `SCARS.md`, instrukcje sesyjne). Poprawa leży w warstwie promptów i rygorze instrukcji, a nie w konfiguracji harnessu.

### A.4 Propozycje zmian (NIE zastosowane)
Brak bezpośrednich propozycji zmian w `config.toml`. Rekomendacja: utrzymać obecny `config.toml` bez modyfikacji.

## B. Korekty K1–K3

### B.1 K1 — status i weryfikacja
- **Status**: `never committed`. Pliki `handoff/real_case_62b1e12d.*` nie występują w historii git. ID `62b1e12d` pochodzi z zewnętrznej sesji systemowej.
- **Decyzja**: Wykluczyć z commita naprawczego GraphRAG.

### B.2 K2 — warianty A/B wykonania
- **Wariant A**: Wykonać teraz w Sesji 2c (utworzyć `scripts/oneoff/`, przenieść `move_state_description.py`, dodać bezpieczny shim w `scripts/`).
- **Wariant B**: Zostawić jako odroczone — plik pozostaje jako untracked w root, wykonanie w Sesji 3 po akceptacji pakietu commitów.

### B.3 K3 — warianty A/B dla Sesji 3
- **Wariant A**: Sesja 3 = wyrównanie `references/measurements.md` z faktycznym artefaktem `retrieval_benchmark_results.json` (aktualizacja `mean_family_precision` z 0.746 na 0.629).
- **Wariant B**: Sesja 3 = pełne dochodzenie historyczne w logach i commitach, skąd wzięła się wartość 0.746 w wiadomości commitu C-6.

### B.4 Styl komunikatów commitów — warianty A/B/C
- **Wariant A (polski)**:
  1. `graphrag: naprawa coverage PL i refusal OOC EN bez bibliotek zewnętrznych`
  2. `chore: aktualizacja handoff, state, map i flag sesyjnych`
- **Wariant B (angielski, spójny z `git log`)**:
  1. `graphrag: fix PL coverage and OOC EN refusal without external libs`
  2. `handoff: update session flags and rebuild views`
- **Wariant C (mieszany / rozdzielony)**: Tylko pierwszy commit teraz, reszta w osobnym etapie.

## C. Pakiet commitów (wariantowy)

### C.1 Wariant „polski, wykonanie teraz” (A + A dla B.2)
- Commit 1: `graphrag: naprawa coverage PL i refusal OOC EN bez bibliotek zewnętrznych`
- Commit 2: `chore: aktualizacja handoff, state, map i flag sesyjnych` (wraz z zamknięciem K2 wariantu A).

### C.2 Wariant „angielski, wykonanie teraz” (B + A dla B.2)
- Commit 1: `graphrag: fix PL coverage and OOC EN refusal without external libs`
- Commit 2: `handoff: update session flags and rebuild views` (wraz z zamknięciem K2 wariantu A).

### C.3 Wariant „polski, odroczenie do Sesji 3” (A + B dla B.2)
- Commit 1: `graphrag: naprawa coverage PL i refusal OOC EN bez bibliotek zewnętrznych`
- Commit 2: `chore: aktualizacja handoff, state, map i flag sesyjnych` (K2 odroczone do Sesji 3).

### C.4 Wariant „angielski, odroczenie do Sesji 3” (B + B dla B.2)
- Commit 1: `graphrag: fix PL coverage and OOC EN refusal without external libs`
- Commit 2: `handoff: update session flags and rebuild views` (K2 odroczone do Sesji 3).

## D. Proponowany zakres Sesji 3/5

- **Jeśli B.3 = A**: Sesja 3 realizuje synchronizację tabeli referencyjnej `references/measurements.md` z dyskowym artefaktem `retrieval_benchmark_results.json` (0.629).
- **Jeśli B.3 = B**: Sesja 3 wykonuje audyt historyczny commitu C-6 i weryfikuje źródło liczby 0.746.

## E. Checklist decyzji dla właściciela

- [ ] **A.4**: Akceptuję brak zmian w `config.toml` (brak naprawialnych kluczy dla defektów behawioralnych).
- [ ] **B.2**: Wybór wykonania K2: **A** (wykonać teraz) / **B** (odroczyć do Sesji 3).
- [ ] **B.3**: Wybór zakresu K3 dla Sesji 3: **A** (wyrównać do 0.629) / **B** (dochodzenie historyczne 0.746).
- [ ] **B.4 / C**: Wybór pakietu commitów i stylu komunikatów: **C.1** (polski, teraz) / **C.2** (angielski, teraz) / **C.3** (polski, odroczone K2) / **C.4** (angielski, odroczone K2).
- [ ] **D**: Akceptuję proponowany zakres Sesji 3 zależny od B.3.
