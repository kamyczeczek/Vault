---
type: Concept
flag: phase2_session_b_done
since: 2026-10-05
owner: mateusz
agent: droid
model: cx/gpt-5.6-luna-low
title: phase2_session_b_done
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

2026-10-05: **sesja B Phase 2 wykonana, werdykt INCONCLUSIVE** (domyka
otwarty Next z flagi `phase2_result`; ARL `5df9edb`).

Non-tautologiczne kryterium treści zaimplementowane TDD (reguły ARL:
oracle-first, mutation-checked, evidence-logged):
`benchmark/content_criterion.json` (25 faktów transkrybowanych WYŁĄCZNIE z
chunków oracle każdego zadania; echo-guard odrzuca pattern pasujący do
pytania; off-oracle sourcing odrzucony; `--build-check` wymusza oba) +
`scripts/score_ablation_content.py` (rescore uszczelkowanych transkryptów
pilota `d6ca9b2` deterministycznie, BEZ nowych wywołań LLM) +
`tests/test_score_ablation_content.py` (14 testów; 22/22 zielone z pilot
scorerem). Guard wyłapał 3 realne defekty w moim pierwszym kryterium:
2 echa (pattern pasujący do pytania) + 1 źródło poza oraclem.

**Wynik rescoru** (`scripts/_scratch/ablation/content_verdict.json`):
ON macro 0.380 vs OFF 0.222; ON wygrywa 1/3 rodzin (bug-fix 0.833 vs
0.278; feature 0.222 remis; perf 0.083 vs 0.167 — ON przegrywa). Pre-
zarejestrowana reguła (on_macro > off_macro ORAZ >=2/3 rodzin) ->
**INCONCLUSIVE**. Co to zmienia: OFF ma non-zero score tam, gdzie zna
treść (np. OFF `perf-costinversion` 2/4 vs ON 0/4, bo ON cytował chunki
bez treści) — kryterium mierzy treść, nie posiadanie ID. Widoczny
mechanizm: ON przegrywa perf, bo 2500-char budżet wstrzykniętego
kontekstu jest zbyt wąski dla fact-dense perf tasks.

Nie jest to dowód hipotezy B (n=9, 1 run/ramię) — to dowód, że pipeline
mierzy treść. ARL `CONTEXT.md` dostał wpis handoff + Open work item
(`3cb04d6`).

**Next (właściciel):** (a) extended-n rerun: >=25 par (80% power,
por. `forge_ab_design`) i/lub szerszy budżet kontekstu ON (2500 ->
~8000 char) — dopiero wtedy werdykt o hipotezie B; (b) wpisanie
kryterium treści do design docu (zlecenie mówi
`docs/research/kg-icm-integration.md`, którego jeszcze nie ma; design
żyje dziś w `handoff/deep/deep-research-kg-icm.md`); (c) czy czyste
kryterium regex wystarczy, czy dodać LLM-judge jako drugą, droższą
metrykę.

**Konsekwencje implementacyjne (feedback post-mortem 2026-10-05) —
zamknięte 2026-10-05 (decyzje właściciela):** (1) 2b domknięte jako
wynik negatywno-infrastrukturalny — `phase2b_result` + ARL `14e254d`
(wrapper commitnięty, deklaracja option-c cofnięta). (2)
`disk_usage_top_level.py` (cudzy, zastały plik z roota workspace,
zgłoszony przez root gate; przeniesiony w `eba080f`) **zaakceptowane
2026-10-05** — plik zostaje w `scripts/_scratch/` (gitignored, konwencja
one-shot helperów z ARL `CLAUDE.md`); nie wrotować, nie usuwać. Bez
otwartych owner-itemów w tej sekcji.

**Preventive measures (2026-10-05, ze feedbacku do przebiegu sesji):**
tarcie wykonawcze tej sesji zostało zabetonowane zamiast zanotowane
pamięciowo: (a) defekt maszyny — `agent_commit.py` po FAIL zostawiał
własny staging w indeksie (splątane commity, reset + powtórka); fix
`unstage()` + TDD `tests/test_agent_commit.py::StagedResidueTests`
(5/5 green); (b) blizna w ARL `EXPERIENCE.md` §8 (czytaj indeks przed
commit; stale MAP.md od pierwszego sygnału, nie od końca sesji) i §9
(timeout suity = większy limit lub background, NIGDY zawężanie zakresu —
"N/22 green" to claim o tych 22, nie o projekcie); (c) klasy
mechaniczne (re-read po missie edycji, --help przed first-call) są już
w root `SCARS.md` (b)/(c) — nie duplikowane.
