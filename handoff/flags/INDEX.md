# INDEX — archived flags

> Generowane przez `python scripts/build_handoff.py`. Flagi starsze niż 3 dni (po `since`, malejąco).

| flag | since | owner | agent | summary |
| --- | --- | --- | --- | --- |
| `vault-single-repo-2026-10-24` | 2026-10-24 | mateusz | opencode | rozstrzygnięty spór o root vaulta. `Desktop\vault` jest jedynym vaultem i jedynym repo; `root_workspace` staje się… |
| `vault-repo-rel-paths-2026-10-24` | 2026-10-24 | mateusz | opencode | przygotowanie `scripts/**` na repo, którego root jest o poziom wyżej (ADR-006). Nowy `scripts/git_paths.py`… |
| `vault-migrated-2026-10-24` | 2026-10-24 | mateusz | opencode | `Desktop\vault` został single-vault single-repo. `.git` przeniesiony z `root_workspace/` do `vault/`; `root_workspace`… |
| `vault-layout-root-2026-10-24` | 2026-10-24 | mateusz | opencode | adopt vault = root_workspace layout in ALLOWED_ROOT, CLAUDE.md, and STATUS.md; include pending .gitignore +… |
| `vault-layout-and-git-bootstrap-2026-10-24` | 2026-10-24 | mateusz | opencode | root workspace re-bootstrapped after the vault move. `.projects/` renamed back to `projects/` (CLAUDE.md, AGENTS.md and… |
| `obsidian-repro-needed-2026-10-24` | 2026-10-24 | mateusz | opencode | trzy awarie po stronie Obsidiana są **nadal niepotwierdzone** i nie są „naprawione”. (1) Grey screen (sesje 6, 8): krok… |
| `gate-vault-owned-xor-2026-10-24` | 2026-10-24 | mateusz | opencode | bramka przestaje traktować `.git`, `.obsidian`, `.smart-env` i `Notes` jako wpisy workspace'u. Nowy zbiór `VAULT_OWNED`… |
| `gate-advisories-deferred-2026-10-24` | 2026-10-24 | mateusz | opencode | pięć otwartych pozycji zostaje **świadomie odłożonych**, nie zamkniętych. (1) R16 advisory: commit dotykający… |
| `codex-loader-2026-10-24` | 2026-10-24 | mateusz | codex | `scripts/agent_sessions.py` rozszerza loader o Codex Desktop (`~/.codex/sessions/`, JSONL + Zstandard fallback),… |
| `close-include-whole-tree-2026-10-24` | 2026-10-24 | mateusz | opencode | `close.py --include` rozumie katalog i całe drzewo. `find_strays` dopasowuje zawartość katalogu po prefiksie (bez… |
| `test-memory-index-format-restored-2026-10-23` | 2026-10-23 | opencode | opencode | **`test_memory_index.py` is green (33/33).** The 2026-10-21 restructure removed `format_results`, `format_brief`,… |
| `session-digest-ab-2026-10-23` | 2026-10-23 | opencode | opencode | **L0 unproven/closed; L1 is a |
| `session-brief-valuable-2026-10-23` | 2026-10-23 | opencode | opencode | **`session_brief.py` built; |
| `memory-meta-session-exclusion-durable-2026-10-23` | 2026-10-23 | opencode | opencode | **B landed; |
| `did-sessions-default-5-2026-10-23` | 2026-10-23 | opencode | opencode | **1f1937f gets its flag |
| `session-digest-design-2026-10-22` | 2026-10-22 | opencode | opencode | digest sesji zaprojektowany |
| `obsidian-vault-2026-10-22` | 2026-10-22 | opencode | opencode | vault Obsidiana zbudowany jako podfolder |
| `sessions-lab-icm-restructure-2026-10-21` | 2026-10-21 | mateusz | opencode | `scripts/_scratch/sessions/` przebudowane na ICM (one folder, one job), 740 MB → 389 MB, martwizy wyczyszczone,… |
| `raw-did-session-extractors-2026-10-20` | 2026-10-20 | mateusz | opencode | dwa deterministyczne eksportory sesji agentów dostarczone i zweryfikowane na live store'ach. |
| `transcript-fix-p1-p6-2026-10-19` | 2026-10-19 | mateusz | opencode | P1–P6 domknięte i rozszerzone o rekomendacje review fazy 3 (R1–R6). Nowe pliki generatora i testów są w repo;… |
| `ticket-scratch-test-bat-runs-exports-on-import-2026-10-19` | 2026-10-19 | mateusz | opencode | Ticket otwarty przy fixie transkryptu (P1–P6). **Korekta atrybucji z review fazy 3**: `exports.md` mutuje nie… |
| `merged-session-loss-declarations-2026-10-19` | 2026-10-19 | Mateusz | opencode | target variant implemented. Default is now the split layout (`--monolith` opts out): a 31 KB `last_sessions_merged.md`… |
| `close-py-final-2026-10-18` | 2026-10-19 | mateusz | opencode | final close for contract close-py-2026-10-18. |
| `close-py-correction-path-2026-10-18` | 2026-10-19 | mateusz | opencode | close.py correction path implemented and verified. R19/R16 verified via integrity in this close. |
| `ticket-s84b-check-includes-git-rm-trap-2026-10-18` | 2026-10-18 | mateusz | opencode | Ticket otwarty decyzją ownera (łańcuch E4 zamknięty na `8af7e77`). |
| `ticket-s76-parse-scars-leak-2026-10-18` | 2026-10-18 | mateusz | opencode | Ticket otwarty decyzją ownera (łańcuch E4 zamknięty na `8af7e77`). |
| `ticket-r14-sessions-meta-shelf-freshness-2026-10-18` | 2026-10-18 | mateusz | opencode | Ticket otwarty decyzją ownera (łańcuch E4 zamknięty na `8af7e77`). |
| `the-pragmatic-programmer-retrieval-zadanie3-2-answerpilot-2026-10-18` | 2026-10-18 | mateusz | opencode | p95 Tier 3 zmierzone (108.2 ms ≤ 500 ms, commit `978d108`), luka 2/52 przeczytana i rozdzielona na dwa defekty (q010 =… |
| `the-pragmatic-programmer-retrieval-answerpilot-run-2026-10-18` | 2026-10-18 | mateusz | answerpilot | `the-pragmatic-programmer-retrieval-answerpilot-run-2026-10-18` — 2026-10-18 (sesja 6, answer-layer EN): **strict 10/13… |
| `session-16-closure` | 2026-10-18 | mateusz | opencode | session-12 gates approved and passed via unlazy (`gate-check.mjs --approve`), report-fix created, CONTEXT.md backlog… |
| `r18-parser-scope-fix-2026-10-18` | 2026-10-18 | mateusz | opencode | Naprawa S84a (korekta w S85): R18 parser fałszywie flagował `status: WYKONANE` wpisy, których closing prose zawierała… |
| `owner-decisions-2026-10-18-v2` | 2026-10-18 | mateusz | opencode | Sprostowanie — poprzednia flaga `owner-decisions-2026-10-18` (commit `975b8f1`, model `omp/nara-step-5-preview`)… |
| `open-tickets-s76-s84b-r14-2026-10-18` | 2026-10-18 | mateusz | opencode | Zgodnie z rekomendacją ownera — łańcuch E4→close zamknięty na `8af7e77` (10 sesji od `01a14af`, każda naprawiała dług… |
| `handoff-status-p4-repair-and-check-r24-2026-10-18` | 2026-10-18 | mateusz | opencode | P0 check_r24 code quality cleaned; P1 superseded added to build-status first version; P2 check_r24 failure path tested… |
| `handoff-status-folder-created-2026-10-18` | 2026-10-18 | mateusz | opencode | Created handoff/status/ folder. Skill discovery fixed via compact index. Gates OK. |
| `handoff-status-flags-refresh-2026-10-18` | 2026-10-18 | mateusz | opencode | P0 dead code removed; P1 folder-created not checked refreshed; P2 build_status --check added to integrity; P3… |
| `handoff-status-exit-code-and-scar-doc-2026-10-18` | 2026-10-18 | mateusz | opencode | P0 check_r24 failure path EXIT=1 verified directly (not grep-inferred); P1 previous scar documented in flag; P2… |
| `handoff-status-context-refresh-4-2026-10-18` | 2026-10-18 | mateusz | opencode | Documented PLAN.md pointer rationale and 34->35 anomaly root cause. |
| `handoff-status-context-refresh-3-2026-10-18` | 2026-10-18 | mateusz | opencode | Corrected test exit code note: 49 tests OK, EXIT=0 (pipe artifact). |
| `handoff-status-context-refresh-2026-10-18` | 2026-10-18 | mateusz | opencode | Refresh stale close.py dry-run note in handoff/status/CONTEXT.md. |
| `handoff-status-context-refresh-2-2026-10-18` | 2026-10-18 | mateusz | opencode | Updated Not checked: backup created, tests run (49 OK), anomaly noted. |
| `handoff-status-build-status-cleanup-2026-10-18` | 2026-10-18 | mateusz | opencode | Removed volatile HEAD/commit lines from STATUS.md Gates section to keep build_status --check stable across commits;… |
| `handoff-status-build-status-2026-10-18` | 2026-10-18 | mateusz | opencode | Landed build_status.py + decisions/ contract; STATUS.md generated; anomaly 34->35 clarified. |
| `cold-start-recall-proof-2026-10-17` | 2026-10-18 | mateusz | opencode | Cold-start walk test recallu wykonany end-to-end — świeży agent, czytając tylko `HANDOFF.md` +… |
| `close-py-git-rm-trap-fixed-2026-10-18` | 2026-10-18 | mateusz | opencode | fixed `check_includes` in scripts/close.py so a staged deletion (`git rm`) is accepted as a valid `--include` path;… |
| `close-py-correct-flag-landed-2026-10-18` | 2026-10-18 | mateusz | opencode | implemented `close.py --correct <flag>` (edit-in-place + rebuild views + gate + commit, same transaction guarantees) as… |
| `close-pipeline-determinism-2026-10-18` | 2026-10-18 | mateusz | opencode | Naprawiono dwa udowodnione bugi close pipeline (midnight determinism + `INDEX.md` staging) — close przechodzi **bez**… |
| `close-artifacts-s82-s83-2026-10-18` | 2026-10-18 | mateusz | opencode | Domknięcie trzech artefaktów po S81: `handoff/CONTEXT.md` mówi „all three generated views" (było przestarzałe „both… |
| `review-debt-named-s80-2026-10-17` | 2026-10-17 | mateusz | opencode | Domknięto dług nazwany w review `ses_eb43216f` — dodano S80 (kolizja frazy) i jawnie nazwano otwarte długi, żeby… |
| `recall-protocol-curated-2026-10-17` | 2026-10-17 | mateusz | opencode | Zweryfikowano hipotezę recallu S75/S73 (problem w metodzie query, nie w indeksie) i naprawiono protokół w… |
| `e4-rescue-model-contract` | 2026-10-17 | mateusz | opencode | E4 rescue completed. S73 added, brain re-ingested, R15 eval fixed, R23 narrowed, session-decision repaired, integrity… |
| `debug-py-type-curated-correction-2026-10-17` | 2026-10-17 | mateusz | opencode | Domknięto jedyną lukę z review — pominięty test `debug.py "<query>" --type curated`. Wynik: **jest równoważne**… |
| `agent-session-memory-recall-s75` | 2026-10-17 | mateusz | opencode | Audyt nieużycia bazy wiedzy sesji (memory_index.py) ukończony. Zapisano skar S75 w SCARS.md. Brain przebudowany do 54… |
| `wayfinder-brain-e7-expect-hash-2026-10-16` | 2026-10-16 | mateusz | opencode | Pierwsza egzekucja w `docs/wayfinder-brain-execution-map.md` — E7 (B7 `expect_hash`) wykonany i zielony; R18 streak… |
| `wayfinder-brain-e6-verify-claims-2026-10-16` | 2026-10-16 | mateusz | opencode | `close.py --verify-claims` wdrożone (decyzja B3). Re-derywuje tylko twierdzenia z wykonywalnym artefaktem: `commit… |
| `wayfinder-brain-e1-schema-drift-2026-10-16` | 2026-10-16 | mateusz | opencode | Druga egzekucja w `docs/wayfinder-brain-execution-map.md` — E1 (asercja driftu schematu per store, generalizacja S68)… |
| `wayfinder-brain-e1-drift-regression-2026-10-16` | 2026-10-16 | mateusz | opencode | Follow-up do reviewu sesji E1 (`2990b85`) — cztery długi z reviewu domknięte w jednym commicie; zero zmian loaderów.… |
| `wayfinder-brain-answers-execution-convention-2026-10-16` | 2026-10-16 | mateusz | opencode | Dług B domknięcia E7 — konwencja `docs/wayfinder-brain-answers/README.md` (`## Convention`) odnotowywała tylko answer… |
| `the-pragmatic-programmer-retrieval-zadanie5-2026-10-16` | 2026-10-16 | mateusz | opencode | Zadanie 5 rozstrzygnięte — Tier 4 (cross-encoder) trwale wykluczony na latencji; decyzja zapisana w projekcie… |
| `residue-closeout-2026-10-15` | 2026-10-16 | mateusz | pi-bolt | Domknięcie resztek po sesjach `01a14154` (brain ingest/versioning) i `01a13cf0` (governance ontology). Jeden commit,… |
| `opencode-v2-store-loader-2026-10-16` | 2026-10-16 | mateusz | opencode | `agent_sessions.py::load_opencode_sessions` czyta teraz `session_v2`, a 2.0 renderuje przez `session_message` — sesje… |
| `kr-dirty-tree-resolved-2026-10-16` | 2026-10-16 | mateusz | opencode | Brudne drzewo knowledge-retrieval rozstrzygnięte (Opcja A). Dodano `.gitignore` i skommitowano zaległe artefakty w repo… |
| `kr-0746-artifact-resolved-2026-10-16` | 2026-10-16 | mateusz | pi | knowledge-retrieval Open work resolved against the artifact — 0.746 retired, 0.654 stands; next step is the owner's… |
| `e6-verify-claims-session-2026-10-16` | 2026-10-16 | mateusz | opencode | E6 executed. `close.py --verify-claims` (B3) shipped in commit c2c5d82: re-derives executable-artifact claims only,… |
| `close-py-diff-check-fixes-2026-10-16` | 2026-10-16 | mateusz | pi-bolt | Naprawa dwóch defektów `scripts/close.py` ujawnionych w residue-closeout (`1f5e81c`); dokumentacja w `SCARS.md` (S66,… |
| `brain-memory-v1-landed-2026-10-16` | 2026-10-16 | mateusz | opencode | Warstwa brain jest realna — ingest → door → bramka, wszystkie trzy w jednej sesji (nie rozbite na trzy, jak nakazywał… |
| `brain-fresh-agent-section-v2-2026-10-16` | 2026-10-16 | mateusz | opencode | `brain/CONTEXT.md` `## For a fresh agent` przepisana na wersję pełniejszą (+106 linii wobec v1) — wersja kurowana, nie… |
| `workspace-gate-exclusion-audit-2026-10-15` | 2026-10-15 | Mateusz | pi-bolt | Audyt naprawy eval z `66fdb50`. Werdykt: exclusion case'u `workspace gate` nie byl gamingiem (expected `01a0f9c0-113b`… |
| `review-and-guard-closure-2026-10-15` | 2026-10-15 | mateusz | opencode | Domknięcie review sesji, weryfikacja guardów i czyszczenie _tmp_* w eval/. |
| `retro-close-01a13cf0-2026-10-15` | 2026-10-15 | mateusz | pi | Retroaktywne zamknięcie sesji `01a13cf0` — dedup przy ingest + korekta gold setu case'u `workspace gate`. |
| `retrieval-v1-deployed-2026-10-15` | 2026-10-15 | mateusz | pi | Wdrożono K1 jako `scripts/memory/retrieval_v1.py`. |
| `meta-loop-stopped-2026-10-15` | 2026-10-15 | mateusz | opencode | Łańcuch 6 sesji wokół guardów + grill session |
| `memory-eval-and-guards-decision-2026-10-15` | 2026-10-15 | Mateusz | pi-bolt | Naprawiono eval memory retrieval (hit@5=1.000, 15/15), uzyskano decyzję właściciela o guardach (Opcja A), zweryfikowano… |
| `guard-implementation-option-a` | 2026-10-15 | mateusz | opencode | Zaimplementowano Opcję A (Stop Gate, Read-After-Edit, Self-Modification Audit) wraz z testami adversarialnymi i… |
| `guard-implementation-corrective-2026-10-15` | 2026-10-15 | assistant | agent | Zweryfikowano sfabrykowany T1 z sesji 01a13c73, dodano scar S65 w SCARS.md, zaimplementowano Opcję A właściciela (Stop… |
| `guard-implementation-2026-10-15` | 2026-10-15 | mateusz | opencode | Zaimplementowano Opcję A ochrony guardów — podłączono `root_deletion_guard.py` (--check-staged) oraz… |
| `governance-ontology-prototype-2026-10-15` | 2026-10-15 | mateusz | opencode | Prototyp ontologii governance w `tools/out/governance-ontology.db` został sfalsyfikowany. Werdykt: STOP. |
| `brain-ingest-versioning-measurement-2026-10-15` | 2026-10-15 | mateusz | pi-bolt | Migracja schematu brain.db, ingest plików MD, pomiar FTS5. Werdykt: A (Działający system). |
| `state-export-levels-v3` | 2026-10-14 | mateusz | opencode | domknięcie eksportu. retrieval-v2/L1-full 31.65 MB → 82,336 B (exclude corpus/). L1-contracts zdiagnozowany: winowajca… |
| `state-export-levels-v2` | 2026-10-14 | mateusz | opencode | chirurgiczny fix eksportu. base.json przywrócone `useGitignore: true` + `**/.git/**`; projects.json (nowy) dla… |
| `state-export-final` | 2026-10-14 | mateusz | opencode | domknięcie eksportu stanu. Fix D10 w levels.json (`projects/*/*/` → `projects/research/*/`), L1-contracts ~496 KB.… |
| `retrieval-walkthrough-2026-10-14` | 2026-10-14 | mateusz | opencode | pokaz działania retrievalu na 14 pytaniach (in-corpus łatwe/trudne, cross-lingual, OOC, boundary). Rozkład: 2 trafione… |
| `retrieval-paradox-2026-10-14` | 2026-10-14 | mateusz | opencode | paradoks 0.938 vs 0.295 rozstrzygnięty jako C (różne metryki). mean_family_recall mierzy trafienie w slug na 8… |
| `retrieval-active-recall-slice-shim-2026-10-14` | 2026-10-14 | mateusz | opencode | Implemented Slice 3 (`scripts/ask.py` graph query shim with selftest) and Slice 1 (`forge_hook.py` Active Recall… |
| `planning-debt-2026-10-14` | 2026-10-14 | agent | pi-bolt | Domknięcie długu po sesjach planistyczno-review (01a13ba3–01a13bbf). |
| `plan-audit-verify-2026-10-14` | 2026-10-14 | mateusz | pi-bolt | Weryfikacja zamknięcia planu (T201–T402) w TASKS.md. T201, T202, T203, T204 oraz T401 zweryfikowane pomyślnie z… |
| `plan-audit-2026-10-14` | 2026-10-14 | mateusz | pi-bolt | Audyt spójności TASKS.md i PLAN.md vs rzeczywistość. 4 z 6 ticketów (T201, T202, T203, T204) były już wdrożone w… |
| `pageindex-nara-2026-10-14` | 2026-10-14 | mateusz | opencode | PageIndex podłączony do Nara (`nemotron-3.5-lightning-free`). Chat działa, pełne indeksowanie 222 str. zablokowane… |
| `pageindex-first-run-2026-10-14` | 2026-10-14 | mateusz | opencode | PageIndex 0.4.0 zainstalowany lokalnie, przetestowany na 1 książce (222 str.). R1: budujemy oba (naive RAG +… |
| `memory-index-verify-2026-10-14` | 2026-10-14 | mateusz | opencode | ticket T4 z domeny historii sesji zamknięty dowodami (sesja 11/10, po werdykcie FAZY 1 że L1-contracts nie ma… |
| `local-rag-plan-2026-10-14` | 2026-10-14 | mateusz | opencode | mapa wayfinder + gates unlazy dla lokalnego RAG na bibliotece książek. Destination: lokalny naive RAG PL+EN z cytatami,… |
| `local-rag-pageindex-plan-2026-10-14` | 2026-10-14 | mateusz | opencode | mapa local-rag rozszerzona o PageIndex (vectorless RAG) i porównanie z naive RAG. Nowe tickety: R11-R15 (PageIndex… |
| `kr-pilot-terminated-2026-10-14` | 2026-10-14 | mateusz | opencode | pilot GraphRAG w knowledge-retrieval zamkniety jako terminated, gate not met. Mur #2 (pokrycie semantyczne) naprawiony… |
| `kr-closed-2026-10-14` | 2026-10-14 | mateusz | opencode | KR dopięty. KR repo: 15 plików scommitowanych (family_recall@5 + vec_index + proof from sessions 1-3/10);… |
| `kr-benchmark-scope-2026-10-14` | 2026-10-14 | mateusz | opencode | T7 zamknięty. Benchmark KR: ranking hybrydowy na 33 in-corpus + odmowy 15 OOC/10 boundary. Rozbieżności: recall@5… |
| `handoff-inline-window-2026-10-14` | 2026-10-14 | mateusz | opencode | `build_handoff.py` inline'uje tylko flagi z ostatnich 3 dni; starsze do `handoff/flags/INDEX.md` (linkowane z… |
| `guard-wiring-audit-2026-10-14` | 2026-10-14 | Mateusz | pi | **CZEKAM NA DECYZJĘ WŁAŚCICIELA.** |
| `close-py-ls-files-flag-fix-retrospective-retired-2026-10-14` | 2026-10-14 | mateusz | opencode | formalne domknięcie retrospektywy z sesji 2/3. Flaga opisuje zmianę `scripts/close.py` (`--error-match` →… |
| `chain-non-convergence-2026-10-14` | 2026-10-14 | mateusz | opencode | 11 sesji, dwa otwarte tematy, zero konwergencji. Eksport: 4 sesje, L1-contracts 506 KB (winowajcy: HANDOFF.md 174 KB +… |
| `chain-closed-2026-10-14` | 2026-10-14 | mateusz | opencode | łańcuch 12 sesji zamknięty jako finding governance. Trzy tematy zamknięte: |
| `T402-walk-test-2026-10-14` | 2026-10-14 | fresh-agent | worker | # T402: Walk Test Report |
| `T102` | 2026-10-14 | mateusz | pi-bolt | Zweryfikowano strukturę workspace w ramach T102, uzupełniono brakujący katalog `brain/problems/` z plikiem `README.md`,… |
| `T101` | 2026-10-14 | mateusz | pi-bolt | Zaimplementowano inicjalizację bazy SQLite `brain/brain.db` ze schematem FTS5 i triggerami dla tabel `lessons`,… |
| `workflow-verification-retired-2026-10-13` | 2026-10-13 | mateusz | opencode | Flaga `workflow-verification-2026-10-13.md` została wycofana. Powód: brak commita w `git log --since=2026-10-13` o… |
| `workflow-verification-fix-2026-10-13` | 2026-10-13 | mateusz | opencode | Zweryfikowano twierdzenia poprzedniej sesji (commit fd9cb99, flaga, close.py) przez jawne tool calls; wykryto… |
| `workflow-fix-hardening-2026-10-13` | 2026-10-13 | mateusz | opencode | query: Zakończono naprawę workflow po 10 sesjach. Wprowadzono walidacje w close.py (--explain, --include zagnieżdżonych… |
| `workflow-enforcement-2026-10-13` | 2026-10-13 | mateusz | opencode | cztery mechanizmy egzekwujące SCARS: scan_secrets + pre-commit hook, pre_close_check, verify_report_evidence, close.py… |
| `workflow-debt-verification-2026-10-13` | 2026-10-13 | mateusz | opencode | zweryfikowano 5 twierdzeń z workflow-debt-closure (2 POTWIERDZONE, 3 OBALONE); T10 closed; cutoff 2026-10-13; walk test… |
| `workflow-debt-closure-2026-10-13` | 2026-10-13 | mateusz | opencode | R19 naprawione, R16 rozstrzygnięte, verify_report_evidence podłączone, docs/workflow/ walkable. |
| `state-export-levels-fix` | 2026-10-13 | mateusz | opencode | naprawa wielopoziomowego eksportu i rozdzielenie długu procesowego. |
| `state-export-levels` | 2026-10-13 | mateusz | opencode | folder eksportów po (target × poziom). Workspace L0/L1/L2, projekt L0/L1. Root repomix.config.json usunięty. Driver… |
| `state-export-and-t18` | 2026-10-13 | mateusz | opencode | `state-export-and-t18`: 2026-10-13 — Faza 1+2 (state export + T18). False refusals ↓44%. Done. |
| `kr-t3-verification-2026-10-13` | 2026-10-13 | mateusz | opencode | rozstrzygnięto rozbieżność T3 (`in_db=False` w toolcallu vs „oracle istnieje" w raporcie). Przyczyna: T3 sprawdzał… |
| `kr-t3-false-refusals-2026-10-13` | 2026-10-13 | mateusz | opencode | `kr-t3-false-refusals-2026-10-13` — T3 diagnosis of 48.5% false refusals across 18 cases: 16 cases outside top-10 due… |
| `kr-t2-measure-script-2026-10-13` | 2026-10-13 | mateusz | opencode | ustalono, że measure_trust_set.py mierzy hybrydę, T2 zamknięty, T1 gotowy. |
| `kr-t13-gold-id-verification-2026-10-13` | 2026-10-13 | mateusz | opencode | T13 rozstrzygnięte — 16/18 ZAWODNE to family-match-only (88.9%); metryka recall@5 mierzy annotację -> retired w… |
| `kr-t1-rerank-baseline-2026-10-13` | 2026-10-13 | mateusz | opencode | vectors+rerank MRR@5=0.376 na Trust Secie (odtworzone z historycznym 0.376). |
| `kr-t1-debt-2026-10-13` | 2026-10-13 | mateusz | opencode | `kr-t1-debt-2026-10-13` — T1 closure & debt resolution: mtime check confirmed fresh run, MRR@5=0.376, added S62 to… |
| `kr-stage-isolation-2026-10-13` | 2026-10-13 | mateusz | opencode | baseline Recall@10=0.515, FTS5-only Recall@10=0.182, vectors-only Recall@10=0.500. Wąskie gardło: FTS5 (czysty FTS5 ma… |
| `kr-simplification-2026-10-13` | 2026-10-13 | mateusz | opencode | vectors-only MRR@5=0.334 + rerank BAAI/bge-reranker-base MRR@5=0.376, metadata filtering MRR@5=0.400, age decay BLOKADA… |
| `kr-security-hype-real-2026-10-13` | 2026-10-13 | mateusz | opencode | zredagowano 15 kluczy w pliku sesji; HyPE 500/10373 węzłów z gemini-flash-lite-latest (MRR@5=0.377); S60 bug close.py. |
| `kr-retrieval-map-2026-10-13` | 2026-10-13 | mateusz | opencode | Wayfinder map and 12 decision tickets created for retrieval architecture planning across 3 domains. Next: execute… |
| `kr-lqr-hyrag-pilot-2026-10-13` | 2026-10-13 | mateusz | opencode | baseline vectors+rerank MRR@5=0.376, HyPE MRR@5=0.121 (odpada), router MRR@5=0.336 (odpada). Docelowy szkielet: wektory… |
| `kr-hype-real-2026-10-13` | 2026-10-13 | mateusz | opencode | Prawdziwe HyPE z LLM MRR@5=0.379 (odrzucenie strawmana 0.121); fragility metadata filter (0.400 vs 0.336); domknięcie… |
| `kr-hype-final-r19-closed-2026-10-13` | 2026-10-13 | mateusz | opencode | HyPE 50/500 z LLM (450 szablonów); R19 retired; S61 w SCARS. |
| `kr-baseline-diagnosis-2026-10-13` | 2026-10-13 | mateusz | opencode | baseline MRR@5=0.295, false refs=48.5%, hipoteza: Głównym wąskim gardłem retrievera KR jest brak dopasowania… |
| `graphrag-1to1-report-fix-retired-2026-10-13` | 2026-10-13 | mateusz | opencode | Flaga `graphrag-1to1-report-fix-2026-10-13` została wycofana (retired) z powodu błędnej diagnozy commitu f8f43a9.… |
| `graphrag-1to1-report-fix-2026-10-13` | 2026-10-13 | mateusz | opencode | Naprawa błędów wykonawczych i merytorycznych raportu interpretacji 1:1. (1) Poprawiono liczbę trafień w raporcie z… |
| `graphrag-1to1-flag-number-debt-2026-10-13` | 2026-10-13 | mateusz | opencode | Dług liczbowy historycznej flagi graphrag-1to1-interpretation-2026-10-12. Flaga ta zawiera nieaktualne liczby (10/12, 2… |
| `graphrag-1to1-diagnosis-fix-and-close-py-debt-2026-10-13` | 2026-10-13 | mateusz | opencode | Supersedes the conflicting claim in `graphrag-1to1-report-fix-2026-10-13` regarding commit f8f43a9. (1) Poprawiono… |
| `graphrag-trust-set-natural-questions` | 2026-10-12 | mateusz | opencode | BLOKADA: MRR@5=0.295 < 0.4; 48.5% false refusal in-corpus; 18/33 ZAWODNE. Decyzja o dalszych krokach należy do… |
| `graphrag-trust-set-freeze` | 2026-10-12 | mateusz | opencode | Zamknięto i zamrożono pilot graphrag (Trust Set 58 pytań, bramka semantyczna Wariant 1 z prog_cosine = 0.45). Wszystkie… |
| `graphrag-1to1-interpretation-2026-10-12` | 2026-10-12 | mateusz | opencode | Domknięcie trzech luk interpretacyjnych eksperymentu 1:1. (1) Surowy output verify_report.py przeanalizowany i… |
| `graphrag-1to1-experiment-2026-10-12` | 2026-10-12 | mateusz | pi | sukces pomiarowy. Zamrożono goldy f7d6966 (8 EN); graphrag-hybryda family_recall 0.906 vs ask.py 0.938 (delta w szumie… |
| `cerebras-integration-2026-10-12-review` | 2026-10-12 | mateusz | opencode | Review przyjęty. Raport uzupełniono o jawne porównanie P1–P4 (GraphRAG MRR 0.303 vs Cerebras hybrid 0.57; Recall@1… |
| `cerebras-integration-2026-10-12` | 2026-10-12 | mateusz | opencode | Dodano i zmierzono Recall@1/3/10 oraz MRR dla GraphRAG, zachowując MRR@5. Wynik: Recall@1=0.159, Recall@3=0.417,… |
| `verify_report_closed` | 2026-10-11 | Mateusz | DeepSeek Harness Agent | # verify_report closed — closed-loop helpfulness bias detection |
| `session-discipline-hardening` | 2026-10-11 | mateusz | opencode | korekta po ocenie sesji naprawczej. Wycofano duplikat discipline z AGENTS.md (kaskada R13, v9 usunięty, v8… |
| `session-decision` | 2026-10-11 | mateusz | pi-bolt | DECYZJA (format z wykonawcą i statusem — decyzja bez wykonawcy nie istnieje): |
| `session-3-verification-and-blockage-rule` | 2026-10-11 | mateusz | jcode | # Session 3/5 — Verification, Blockage Handling & Feedback Integration |
| `session-2c-master-plan` | 2026-10-11 | mateusz | jcode | # Master plan — Sesja 2c |
| `self_configuration_autonomy_discipline` | 2026-10-11 | mateusz | deepseek-harness | ## Stan |
| `phase-9b-outcome` | 2026-10-11 | mateusz | pi | ## Stan |
| `phase-10a-outcome` | 2026-10-11 | mateusz | pi | ## Stan |
| `graphrag-session-1-commit-pending` | 2026-10-11 | mateusz | jcode | # Sesja 1 — pakiet do commita (Korekta 2b) |
| `graphrag-refusal-and-cross-lingual-fixed` | 2026-10-11 | mateusz | jcode | # GraphRAG — naprawa mechanizmu Refusal (OOC EN) i Cross-Lingual Coverage (in-corpus PL) |
| `graphrag-phase8-semantic-coverage` | 2026-10-11 | Mateusz | pi-bolt | # Handoff Flag: GraphRAG Trust Set (55 questions) & Semantic Gate Decision (Wariant 1) |
| `graphrag-frozen` | 2026-10-11 | root | ? | # Pilot graphrag — zamrożony (Faza 8S) |
| `graphrag-control-result-audit` | 2026-10-11 | mateusz | opencode | domkniecie Fazy 6 po sesjach pi, |
| `goose-iterations-outcome` | 2026-10-11 | mateusz | pi | ## Stan |
| `ask-user-question-fixed` | 2026-10-11 | Mateusz | opencode | Plik `ask-user-question.ts` był ucięty w połowie funkcji `execute` (59 linii, brak domknięć i helperów) — to dawało… |
| `research-engine-kg-dead-path` | 2026-10-10 | mateusz | pi | research-engine/kg.py jest martwe — FileNotFoundError przy każdym resolve (DB =… |
| `notebooklm-cannot-verify-retrieval` | 2026-10-10 | Mateusz | opencode | Pipeline `scripts/notebook/CONTEXT.md` nie może służyć do weryfikacji retrievalu. `problem.md` jest pushnięty jako… |
| `memory-r15-drift-fixed` | 2026-10-10 | Mateusz | opencode | R15 green 15/15 (hit@5=1.000) po dopisaniu 5 zweryfikowanych non-cause confounders do exclude_session_ids case'u… |
| `kr-state-ordered` | 2026-10-10 | mateusz | pi | stan repo KR domknięty po sesji falsyfikatora. (1) Kod pilota w historii: commit 476b3c7 (graphrag.py +… |
| `graphrag-verdict-p0-protocol` | 2026-10-10 | mateusz | pi | werdykt review rozliczony. (1) P0: eksport sesji zawierał linie kluczy o realistycznych długościach… |
| `graphrag-terminal-state-defined` | 2026-10-10 | Mateusz | opencode | # GraphRAG Pilot — Faza 6 ready v2 (falsyfikator odkażony) |
| `graphrag-review4-mechanical` | 2026-10-10 | mateusz | pi | review #4 rozliczone mechanicznie, nie słownie. (1) Teza strukturalna (3x artefakt → review znajduje pytanie → dopisek)… |
| `graphrag-review-truths` | 2026-10-10 | mateusz | pi | review Fazy 6 wpisane do plików (nie tylko do rozmowy). (1) Niewygodne prawdy w answer-qground.md: oracle == źródło… |
| `graphrag-review-fixes` | 2026-10-10 | mateusz | pi | review najnowszej iteracji rozliczone w plikach. (1) Rozjazd D-005 naprawiony W PLIKU (nie w commit message): addendum… |
| `graphrag-pilot-scaffolded` | 2026-10-10 | Mateusz | opencode | rusztowanie pilota GraphRAG stoi |
| `graphrag-phase5-proof` | 2026-10-10 | Mateusz | opencode | Faza 5 pilota GraphRAG zakończona |
| `graphrag-falsifier-v2-qrefusal` | 2026-10-10 | mateusz | pi | Faza 6 Q-refusal EXECUTED protokołem z close-ritual-probed (oracle-first: oczekiwania w proof/falsifier-v2/plan.json… |
| `graphrag-falsifier-v2-qground` | 2026-10-10 | mateusz | pi | Faza 6 Q-ground EXECUTED. Człowiek wkleił w review abstrakt arXiv:2603.25111v2 (spoza grafu); wpisany do CONTRACT.md… |
| `graphrag-falsifier-v2-next` | 2026-10-10 | Mateusz | opencode | falsyfikator v2 gotowy w CONTRACT.md (Q-refusal wykonywalny dziś, Q-ground czeka na ludzkie oczekiwanie). Dla… |
| `graphrag-d002-minigraph` | 2026-10-10 | Mateusz | opencode | D-002 RESOLVED. Backend Fazy 5 to |
| `graphrag-control-result` | 2026-10-10 | mateusz | opencode | Faza 6 kontrola bez narzędzia wykonana. Model: gemini/gemini-3.5-flash-lite. Wynik: 4× NIE (brak… |
| `close-ritual-probed` | 2026-10-10 | mateusz | pi | obca sesja (pierwsza niemodyfikująca close.py) zweryfikowała checklistę z close-ritual-coupled na żywym branchu… |
| `close-ritual-coupled` | 2026-10-10 | mateusz | opencode | iteracja po review warstw: (1) body flagi MUSI zawierać linię `not checked:` (walidowane; puste `—` dozwolone,… |
| `notebooklm-popup-fixed` | 2026-10-09 | Mateusz | agnes-2.5-flash | Terminal popup from NotebookLM refresh disabled. |
| `notebooklm-auth-fixed` | 2026-10-09 | Mateusz | agnes-2.5-flash | NotebookLM auth working via `nlm` CLI (jacob-bd). |
| `codex-omniroute-fixed` | 2026-10-09 | Mateusz | laguna-s-2.1 | Codex CLI non-functional due to OmniRoute proxy not running + broken `OMNIROUTE_API_KEY` env var. Two root causes fixed: |
| `tools-first-arl-split` | 2026-10-08 | Mateusz | goose | ARL w `_archive/` (`grade: demoted`); 4 narzedzia `tools/` 4/4 `--selftest` PASS; R13 ZIELONY (`--check`,… |
| `decision-brief-hypothesis-D` | 2026-10-08 | Mateusz | goose | 2026-10-08: Closed session at D-002 implementation decision. |
| `arl-transfer-pivot` | 2026-10-08 | mateusz | opencode | ARL przekształcony z projektu badawczego |
| `arl-sens-verdict` | 2026-10-08 | mateusz | opencode | NotebookLM run `handoff/notebook-runs/2026-10-08-sens-arl/` |
| `arl-gate-a-result` | 2026-10-08 | mateusz | opencode | Tani test hipotezy B (perf ON @ 8000 znaków) wykonany. Wynik: ON macro = 0.0 vs baseline 0.083. Werdykt: hipoteza B… |
| `session-memory-r16-docstring-closeout` | 2026-10-07 | mateusz | agnes-3-flash | ## Stan |
| `session-memory-r15-resolved` | 2026-10-07 | mateusz | agnes-3-flash | ## Stan |
| `session-memory-mcp` | 2026-10-07 | mateusz | deepseek-harness | MCP server `scripts/memory_mcp.py` (stdio, 2025-06-18 po bump z 2024-11-05, stdlib only) owija… |
| `notebook_pack_landed` | 2026-10-07 | mateusz | opencode | przepływ NotebookLM przełączony ze zepsutego `notebooklm-py` (Chrome 127+ App-Bound Encryption: `token_fetch: false`)… |
| `agent-sessions-jcode-hours-and-journal` | 2026-10-07 | mateusz | agnes-3-flash | ## Stan |
| `dsh_sessions_parser_and_zstd` | 2026-10-06 | mateusz | deepseek-harness | State: Implemented DSH v4 event parser and Zstandard streaming decompression in `scripts/agent_sessions.py`.… |
| `session_memory_level1_telemetry_and_eval_clarity` | 2026-10-05 | mateusz | deepseek-harness | Recorded decision D18 (`scripts/_scratch/sessions/queries.jsonl`) and D19 (mixed-type evaluation rationale with… |
| `session-memory-eval` | 2026-10-05 | mateusz | droid | domyślny ingest obejmuje całą historię, freshness sprawdza pokrycie per agent, a eval filtruje błędy/decyzje po typie. |
| `phase2b_result` | 2026-10-05 | mateusz | droid | **Phase 2b (Goose × graf-MCP) zamknięta jako |
| `phase2_session_b_done` | 2026-10-05 | mateusz | droid | 2026-10-05: **sesja B Phase 2 wykonana, werdykt INCONCLUSIVE** (domyka |
| `docs_reviews_stale_quote` | 2026-10-05 | mateusz | droid | commit gate był blokowany przez nieaktualny raport v7 i martwe wyjątki `63`/`101`; blokada została naprawiona przez… |
| `workspace_guardrails_hardened` | 2026-10-04 | droid | droid | 2026-10-04: **guardrails hardened and verified.** Builders now write LF on |
| `phase2_result` | 2026-10-04 | mateusz | opencode | 2026-10-04: Phase 2 ablation wynik (ARL `d6ca9b2`, 9 zadań x 2 ramiona, |
| `phase2_hypothesis` | 2026-10-04 | mateusz | opencode | 2026-10-04: Hipoteza Phase 2 deep-research (KG + ICM): |
| `l0_router_deepened` | 2026-10-04 | opencode | opencode | Root L0 router pogłębiony w trzech commitach. |
| `deep_research_phase1_done` | 2026-10-04 | mateusz | opencode | 2026-10-04: Deep-research (KG + ICM) — Phase 1 domknięta i zacommitowana |
| `verification_tool_scars` | 2026-10-03 | opencode | build | **blizny (d)–(g) zapisane i domknięte; punkt (2) świadomie otwarty.** Poprzednia wersja tej flagi mówiła „domknięte",… |
| `state_snapshot_live` | 2026-10-03 | unassigned | unknown | `STATE.md` w roocie (ICM inv. 9: generowany skan, nie ręka) — HEAD, brudne pliki, ostatnie commity, tabela runów +… |
| `session_tool_landed` | 2026-10-03 | unassigned | unknown | `scripts/session.py` — jedno narzędzie wyciągające historię sesji opencode z SQLite… |
| `root_committed_e61d8c8` | 2026-10-03 | opencode | build | root w `e61d8c8` (41 plików, +1881/-179) — handoff jako maszyna stanu (flaga = plik = jeden writer, `HANDOFF.md`… |
| `root_committed_ce5aeeb` | 2026-10-03 | unassigned | unknown | root w `ce5aeeb` (22 pliki: review workflow + forge-guardrails plugin + evidence runs z DECISION PASS + STATE snapshot;… |
| `root_committed_931aac5` | 2026-10-03 | opencode | build | root w `931aac5` (5 commity: `9a8e105` |
| `review_workflow_live` | 2026-10-03 | unassigned | unknown | łańcuch odbioru to jedna komenda: `python scripts/review.py .dgc-evidence/runs/<run-id>/` (znajduje REVIEW.md, odpala… |
| `report_numbers_became_gate` | 2026-10-03 | opencode | review | **landed** as root `9a8e105`, with |
| `report_citation_unverified` | 2026-10-03 | opencode | opencode | **zamknięte — trzecia noga doszła.** |
| `pstack_research_test` | 2026-10-03 | unassigned | unknown | pierwszy research w nowym workflow (pstack od poteto): websearch + deep dive Copes + porty; REVIEW prostym polskim ze… |
| `plain_language_meter_d003` | 2026-10-03 | unassigned | unknown | D-003 froze the deterministic fixture and public CLI contract in ARL; focused tests are 4/4 green, CLI returns two… |
| `open_human_calls` | 2026-10-03 | unassigned | unknown | forge_ab stage 1 (50 runów); D-005 (model/budżet); G3 (werdykt); upstream-vs-porty deep-dive; **nowe**: zlecenie… |
| `handoff_flag_per_file_icm` | 2026-10-03 | opencode | build | handoff roota przebudowany wg `icm-architect` (Restructure mode): 22 flagi → `handoff/flags/<flag>.md` (jedna flaga =… |
| `goose_workflow_hardening_planned` | 2026-10-03 | unassigned | unknown | ICM design now lives at `WORKFLOW_GOOSE_ICM.md` (root). It defines a nested Pipeline: prepare → web research →… |
| `goose_pstack_impl_test` | 2026-10-03 | unassigned | unknown | goose/omniroute/gemini-flash-lite-latest (nara 404 na gemini-3.5, omniroute/gemini-3.5 bez kredytów;… |
| `gate_has_no_automatic_caller` | 2026-10-03 | opencode | review | **potwierdzone, nie domknięte.** Root gate |
| `forge_guardrails_integration` | 2026-10-03 | unassigned | unknown | forge-guardrails v0.9.5 as a |
| `forge_ab_design` | 2026-10-03 | unassigned | unknown | the hooks ON/OFF measurement is **designed and |
| `arl_committed_5330266` | 2026-10-03 | unassigned | unknown | ARL w `5330266` (90 plików: poteto-mode-lite z 4 playbookami, skill_router z 19 wpisami, plain-language meter + eval… |
| `tooling_scars_hardened` | 2026-10-02 | unassigned | unknown | post-mortem of the ingest/graph chore |
| `root_reorg_arl_side_landed` | 2026-10-02 | unassigned | unknown | the root reorg's ARL-side |
| `ralph_run_closed` | 2026-10-02 | unassigned | unknown | the only ralph run that has ever existed, |
| `ralph_plain_language_meter_run_open` | 2026-10-02 | unassigned | unknown | ralph run |
| `plain_language_thread_ready` | 2026-10-02 | unassigned | unknown | research question "make the agent |
| `hermes_perf_d17` | 2026-10-02 | unassigned | unknown | Hermes runtime tuned for tokens-per-task |
| `arl_trees_committed` | 2026-10-02 | unassigned | unknown | both repos' working trees were clean of |
| `research_group_moved` | 2026-10-01 | unassigned | unknown | all six active projects are now under |
| `ralph_loop_upgraded` | 2026-10-01 | unassigned | unknown | `skills/ralph-loop` rebuilt around the |
| `gate_trimmed` | 2026-10-01 | unassigned | unknown | ceremony cut after user critique (one move cost |
