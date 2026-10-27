---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# the-pragmatic-programmer-retrieval — CONTEXT.md

grade: candidate

## Open work

- [x] Faza 0.1: Ekstrakcja struktury PDF (`scripts/extract_structure_pdf.py` -> `data/book_structure.json`, 9 rozdziałów, 53 Topics, fingerprint `58c410c0...`)
- [x] Faza 0.2: Weryfikacja `page_offset` (potwierdzono offset = 0, Topic 3 = p.42, Topic 8 = p.75, Topic 9 = p.79)
- [x] Faza 0.3: Walidacja i detektor śmieci (`scripts/validate_chunks.py` -> 0 uszkodzonych)
- [x] Faza 0.4: Chunking semantyczny (`scripts/chunk_semantic.py` -> `data/chunks.json`, 855 chunków, mediana 680 znaków)
- [x] Faza 1.1: Budowa indeksu hybrydowego (`scripts/build_hybrid.py` -> FTS5 BM25 + FastEmbed ONNX vectors w `db/rag.db`)
- [x] Faza 1.2: Retrieval hybrydowy + fuzja RRF (`scripts/recall_hybrid.py`)
- [x] Faza 1.3: Cross-encoder reranker (`scripts/rerank.py` -> BAAI/bge-reranker-base)
- [x] Faza 1.4: Pełny pipeline retrievalu (`full_retrieve()`)
- [x] Faza 2.1: Przygotowanie gold setu (`scripts/build_gold_set.py` -> `eval/gold_set_hard.json`, 30 pytań, fingerprint `c5a0a95f...`)
- [x] Faza 2.2: Pomiar `recall@8` i `MRR` (`scripts/eval_retrieval.py` -> 4 tiery zmierzone)
- [x] Krok 0 (fix): `index_fingerprint` liczony z kanonicznej treści (`scripts/fingerprint.py`, canonical JSON), nie z raw-bytes; wszystkie call-sites (`eval_retrieval.py`, `build_gold_set*.py`) używają wspólnego helpera (commit `34acea4`)
- [x] Zadanie 4: Memoizacja cross-encoder + batch candidate fetch (`scripts/rerank.py`; cache `data/rerank_cache.json`, klucz `model+question+text`, gitignored) (commit `0a1082a`)
- [x] Zadanie 5: Rozstrzygnięte — **Tier 4 @ 100 kandydatów martwy na latencji** (patrz §"Zadanie 5" niżej)
- [~] Zadanie 6 (topic-boost / routing): **POMINIĘTE świadomie** — Krok 1 pokazał 3/9 multi-target queries z dominant ≥5/8 (poniżej progu), a te 3 są już any-topic hitami, więc boost nie ruszyłby Recall@8
- [ ] Decyzja architektoniczna: czy rozszerzać zbiór pytań o generowane (do 60 pytań) i czy wdrażać RAPTOR / Graf wiedzy

## Architecture & Decisions

- Corpus: "The Pragmatic Programmer" (20th Anniversary Edition), 497 stron, 9 rozdziałów, 53 Topics.
- Indeks: SQLite FTS5 (`unicode61`) + FastEmbed ONNX wektory (`BAAI/bge-small-en-v1.5`) + RRF (k=60) + Cross-encoder reranker (`BAAI/bge-reranker-base`).
- Relacja do `retrieval-v2`: `retrieval-v2` mierzył korpus notatek wielu dokumentów i porzucił cross-encoder ze względu na koszt latencji i brak separacji refusal na OOC. W `the-pragmatic-programmer-retrieval` korpus jest zamknięty (monografia), a kluczowym celem jest precyzja cytowania (rozdział, Topic, strona) oraz test czy RAPTOR / Graf CTE są niezbędne dla syntezy multi-hop (D23).

## Environment (temporary)

- Interpreter: `C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (venv harnessu)
- Python version: `Python 3.11.15` (matching `uv cpython-3.11-windows-x86_64-none`)
- Status: brak lokalnego podprocesu `.venv` z powodu błędu sandboxa `0xC0000142` (`STATUS_DLL_INIT_FAILED`, scar z sesji `retrieval-v2` / `real_case_62b1e12d.jsonl`).
- Zależności: `requirements.txt` precyzuje wersje, lecz na tej maszynie środowisko uruchomieniowe wymaga korzystania z głównego interpretera harnessu z powodu blokady subprocessów venv.

## Metrics Baseline (Pomiar z 2026-10-16, n=30 hard gold set, strict topic-match)

| Konfiguracja | Any-Topic Recall@8 | Primary-Topic Recall@8 | MRR | Latencja (mediana) | Latencja (p95) |
|---|---|---|---|---|---|
| **1. Pure FTS5 BM25** | 0.733 (22/30) | 0.700 (21/30) | 0.683 | **1.8 ms** | 2.9 ms |
| **2. Pure FastEmbed Vector** | 0.833 (25/30) | 0.700 (21/30) | 0.541 | **99.5 ms** | 125.8 ms |
| **3. Hybrid RRF (FTS5 + Vector)** | **0.900 (27/30)** | **0.833 (25/30)** | **0.732** | **102.9 ms** | 201.6 ms |
| **4. Hybrid + CrossEncoder** | **0.933 (28/30)** | **0.867 (26/30)** | **0.806** | **9020.7 ms** | 14568.7 ms |

## Extended Metrics Baseline (Pomiar z 2026-10-16, n=60 pełny gold set: 52 answerable + 8 unanswerable)

Rozszerzony gold set (`eval/gold_set_extended.json`, fingerprint `sha256:43e408d4...`) pokrywa wszystkie 53 Topics książki oraz pytania podchwytliwe i odmowne:
- 30 pytań trudnych z bazy (`gold_set_hard.json`)
- 12 pytań false-premise (5 z bazy + 7 nowych: fp001–fp007)
- 15 pytań tematycznych uzupełniających brakujące Topics (q031–q045)
- 8 pytań unanswerable / out-of-corpus (u001–u008: Kubernetes, React, AWS, SQL injection, Docker, Git rebase, OAuth, GraphQL)

| Konfiguracja | Answerable Any Recall@8 | Answerable Primary Recall@8 | MRR | Latencja (mediana) | Latencja (p95) | OOC Refusal (n=8) |
|---|---|---|---|---|---|---|
| **1. Pure FTS5 BM25** | 0.654 (34/52) | 0.635 (33/52) | 0.586 | **2.5 ms** | 4.9 ms | OOC med: 2.0 ms |
| **2. Pure FastEmbed Vector** | 0.808 (42/52) | 0.731 (38/52) | 0.512 | **89.0 ms** | 135.3 ms | OOC med: 87.4 ms |
| **3. Hybrid RRF (FTS5 + Vector)** | **0.827 (43/52)** | **0.788 (41/52)** | **0.648** | **93.0 ms** | 107.5 ms | OOC med: 88.9 ms |
| **4. Hybrid + CrossEncoder @ 40** | **0.865 (45/52)** | 0.827 (43/52) | **0.715** | **9621 ms** | 17842 ms | Wykluczony z realtime |

### Wnioski z pełnej ewaluacji (Faza 2.2):
- **Diagnostyka pytań False-Premise:** Zapytania z błędnymi założeniami wprowadzają mylące słowa kluczowe (np. sugerując pozostawienie broken windows dla flow zespołu). W takich przypadkach czysty leksykalny BM25 drastycznie traci skuteczność (Recall@8 spada do **0.286**), podczas gdy gęsty wektor FastEmbed zachowuje intencję semantyczną na poziomie **0.714**. Fuzja RRF stabilizuje wynik.
- **Odporność na zapytania spoza domeny (Unanswerable):** Wszystkie 8 zapytań o technologie niewystępujące w książce (Docker, Kubernetes, React, OAuth itp.) zostały zweryfikowane pod kątem separacji sygnału. Wektor i RRF przetwarzają je w czasie ~88 ms bez zakłócania indeksu bazowego.
- **Ostateczna dyskwalifikacja produkcyjna Tier 4:** Pomiar wykazał latencję na poziomie 11.8 s na CPU na pojedyncze zapytanie przy 20 kandydatach. Reranker jest trwale wykluczony ze ścieżki produkcyjnej.
- **`--wide` (100 kand.) odrzucony (2026-10-16):** przy 40 → 100 kandydatach MRR praktycznie nie drga (0.715 → 0.716, próg decyzyjny był ≥0.05), Recall@8 spada (0.865 → 0.846), nDCG@8 też (0.751 → 0.748), a latencja rośnie ~1.9× (9621 → 17867 ms mediana). Brak zysku przy podwójnym koszcie → 40 kand. to górna sensowna granica; `--wide` nieużywane.
- **Konfiguracja produkcyjna:** **Tier 3 (Hybrid RRF)** stanowi domyślny, w pełni responsywny silnik wyszukiwania (mediana latencji 93 ms, p95 107 ms, Recall@8 = 0.900 na gold secie problemowym i 0.827 na pełnym 52-pytaniowym teście syntetycznym).

## Latencja ogona Tier 3 (pomiar 2026-10-18, S56 pre-registered przed runem)

Kryterium zapisane przed runem: p95 ≤ 500 ms na 52 pytaniach answerable, top-8. p50/p99 raportowane obok; decyduje p95.

Pomiar (po pierwszym uzgodnieniu wyniku z §Extended Metrics): **p50 = 88.0 ms, p95 = 108.2 ms** (skrypt eval);
p99 pomiar pomocniczy (wrapper, zero zmian w repo): **p50 = 87.4 ms, p95 = 105.6 ms, p99 = 117.9 ms, max = 393.8 ms, mean = 95.4 ms, n = 52**.
Overlay: max 393.8 ms < próg 500 ms. Pomiar, nie wniosek: ogon Tier 3 mieści się pod progiem „szybki".

## Luka any-vs-primary 2/52 (czytanie ręczne, 2026-10-18, FAZA 3)

Pytania: `q010` (topics [9,10], primary 9 = DRY) i `q012` (topics [35,36], primary 35 = Actors and Processes). Odczyt ręczny, bez modelu, bez zmiany metryki:

- **q010:** chunk topic 9 z treścią DRY istnieje w indeksie (`data/chunks.json` topic 9: 28 chunków) i wychodzi na **#7 przy top_k=20**; przy top_k=8 slot #7 zajmuje chunk topic 10. Ranking zależny od k (RRF); właściwy chunk jest na granicy top-8 i wypada.
- **q012:** chunki topic 35 (Actors, 16 chunków w korpusie) rankują **poza top-20**; top-8 zawiera 2× topic 36 (Blackboards) + szum (3× Estimating).
- **Naming defektu (poprawione 2026-10-18, po recenzji):** **podział na dwa różne defekty:**
  - **q010 — adnotacja / primary-assignment dla comparison:** chunk #1 (`"Orthogonality is closely related to the DRY principle. With DRY … whereas with orthogonality …"`) **jest odpowiedzią** na pytanie porównawcze, a jest oznaczony topic 10, choć gold primary = 9 (DRY). To ten wzorzec, dla którego projekt już retired recall@5 (`T13`/`S64`): metryka mierzy adnotację, nie treść. **Metryka do retire/dyskusji, nie ticket rankingowy.**
  - **q012 — granularność / ranking:** chunki topic 35 (Actors, 16 w korpusie) rankują poza top-20 przy istnieniu poprawnych chunków Blackboards w top-8; top-8 zawiera szum (3× Estimating). Osobny ticket rankingowy.
- **Czynność:** brak zmiany metryki i bramki w tej sesji (S62); q010 → decyzja o statusie metryki (właściciel), q012 → osobny ticket.
- ** Korekta do wcześniejszej wersji:** poczytano, że ranking zależny od k (chunk topic 9 na #7 przy top_k=20, poza top-8 przy top_k=8) — kwestia techniczna, lecz **nie zmienia etykiety q010**: treść odpowiedzi dla comparison jest w kontekście od rank 1.

## Zadanie 7 — answer-layer (status 2026-10-18)

- **Pilot z lokalnym 0.5B odrzucony — answer-layer = agent, nie lokalny model.** Run Qwen2.5-0.5B-Instruct (CPU, budżet A) ubity po 4 odpowiedziach: (a) metryka „Źródło: Topic N" **tautologiczna** — „Topic N" był dosłownie w kontekście podany z etykietą chunka, odpowiedź mierzy format-following, nie jakość; (b) 0.5B po polsku generuje nonsens ( przykład: pytanie o ETC → „Zdrowe, Etc."), mierzy ładowanie modelu, nie odpowiedź; (c) limit 2500 znaków to powtórka truncation artifact z graphrag (root: `handoff/flags/arl-sens-verdict.md`) i tak ucinał poniżej naturalnej wielkości top-8 (8 × mediana 680 znaków ≈ 5.4k znaków); Kryteria poniżej niezwalidowane, bez wartości (S56: zapisano przed runem, ale run nie dotyczył realnego komponentu).
- **Architektura:** answer-layer to **nie osobny model** — agent (ten, co prowadzi sesję) dostaje top-8 chunków Tier 3 i układa odpowiedź. Koszt = tokeny agenta już w pętli; retrieval kończy się na ~90 ms (p95 108 ms) — zmierzone.
- **Ticket na osobną sesję — lekki answer-layer pilot (izolacja świeżym podagentem):**
  - **Skrypt tylko dumpuje** top-8 chunków per pytanie do pliku (retrieval ~90 ms × 23 ≈ 2 s); kontekst = top-8 chunków **verbatim, w całości** (bez cięcia ~5.4k znaków, bez stripowania nagłówków „Topic N" — tuning inputu pod metrykę jest zakazany).
  - **Jeden spawn = jedno pytanie** (15 answerable + 8 unanswerable; brak batcha = brak kontaminacji i „zawsze odpowiadaj" przy refusaliu).
  - **Podagent nie widzi metryki ani historii sesji** — brief samowystarczalny: „odpowiedz w 1–3 zdaniach po polsku na podstawie podanych fragmentów; jeśli fragmenty nie zawierają odpowiedzi, napisz dokładnie: BRAK W KSIĄŻCE". Bez narzędzi retrieval.
  - **Podagent nie ocenia i nie commituje.** Parent wyciąga terminy konieczne z gold chunków **przed** spawnem, trzyma u siebie, grade'uje output deterministycznie na obecności terminów (nie kopiowanie etykiety) + próg refusal na unanswerable. Kryterium i lista terminów zapisane **przed** spawnem (S56).

## Answer-layer pilot v2 (sesja 3, pomiar 2026-10-18, Tier 3, strict pre-registered)

Poprawiony pomiar po sesji 2 (która była nieinterpretowalna: Tier 4 + metryka post-hoc, patrz korekta wyżej). Dump: `retrieve()` (RRF top-8, bez rerankera), timing: **p50 = 90.9 ms, p95 = 105.2 ms, total 2.6 s** na 24 zapytania — sanity gate < 500 ms przeszedł, q012 top-8 = [15,36,15,41,6,38,15,36] = 3× Estimating (sygnatura Tier 3, jak w sesji 1). Interpreter: `C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`.

Pre-registration v2 (`handoff/pilot-answer-layer-2026-10-18/preregistration-v2.md`, frozen before spawn #1): 14×3–6 polskich stemów z reference_answer, reguła `norm(term) in norm(answer)` (NFKD+lowercase), strict only, zero mapy.

Pomiar (23 spawny, jeden spawn = jedno pytanie, `opencode/glm-5.3-flash-free`, brief samowystarczalny, chunki verbatim top-8 Tier 3):

- **Answerable: strict 3/14** (q002, q004, q015) — próg ≥10/14 **niespełniony**. Brakujące termy per pytanie (grader `scripts/grade_answer_pilot_v2.py` → `grading-results-v2.json`, raw `answers-raw-v2.json`): q001 reprezentac; q003 delegow (odpowiedź „delegację" — stemy rdzeniowe nie schwytały odmiany); q005 zaraz („od razu"); q006 caller („wywołujący"); q008 supervisor (treść supervisor trees nieobecna w top-8 — ograniczenie inputu, nie modelu); q009 testow („testy"); q010 ortogonal/współzależ/zmian (model pisał o „wzajemnych zależnościach"); q011 zawęż („wyizolujesz"); q013 świadom („deliberately"). q007 i q012 = **refusal na answerable** (answer-layer failure: top-8 zawierał gold topic 29/36, model stwierdził brak; zgodne z przewidywaniem FAZY 5 instrukcji).
- **Unanswerable: 8/8 refusal** (marker `BRAK W KSIĄŻCE`) — próg ≥6/8 spełniony.
- **Canary: refusal** — brak kontaminacji pamięci.
- Pomiąd jako pomiar: strict-language metryka vs polska fleksja jest bardzo surowa (3/14 przy obiektywnie sensownych 12/14 odpowiedziach zgodnych z treścią dumpów); jej zbadanie/wymiana to decyzja właściciela, nie naprawa w tej sesji.
- **Korekta 2026-10-18 (sesja 4): strict 3/14 jest nieinterpretowalne jako metryka terminowa.** Stemy nie spełniały własnej reguły fleksyjnej (delegow vs „delegację", testow vs „testy", caller vs „wywołujący"); supervisor nieobecny w top-8 — termin niemożliwy do złapania niezależnie od jakości odpowiedzi. Refusal 8/8 i canary = prawdziwe wyniki. Metryka terminowa = **invalid, do przeprojektowania (lematyzacja + walidacja termów przed spawnem)** w sesji 5.
- **Pytanie do właściciela (CZEKAM NA DECYZJĘ):** Primary-Topic Recall dla comparison — retired (precedens T13/S64) czy przedefiniowany (primary = zbiór topiców)? Podniesione, nie blokuje pilota.

Sesja 5 weryfikuje, czy 0.981 jest realne — przez klasyfikację chunków + filtrowany Recall@8 + audyt n-gram overlap. Wynik sesji 4 pozostaje jako zapis; nie jest jeszcze podstawą produkcji.

## Sesja 5 — walidacja 0.981 (pomiar 2026-10-18, trzy sekcje pod sekcją "EN vs PL")

### 5.1 Klasyfikacja chunków (P0 z audytu)

Pre-rejestrowane reguły priorytetowe (pierwszy match wygrywa) w `scripts/classify_chunks.py`; `data/chunks.json` nietknięte, wynik w nowym pliku `data/chunks_classified.json` (chunky z `RELATED SECTIONS INCLUDE` są w źródle typowane różnie — 33× src `prose`, 13× `definition`, 6× `list`, 4× `code` — więc klasyfikacja programatyczna była konieczna).

- chunks total=855: **prose=795 (93.0%), related-sections=56 (6.5%), heading-only=3 (0.4%), code-listing=0 (0.0%), challenge=1 (0.1%)** (sanity suma=855).
- W top-8 sesji 4 (proxy ważony per-topic, bo `results.json` przechowuje topics a nie chunk-ids): wariant A — prose 91.9%, related-sections **7.7%**, heading-only 0.4%; wariant B — prose 91.9%, related-sections **7.5%**, heading-only 0.6%. Chunki-śmieci **były** w top-8 sesji 4 (~7–8% slotów), ale poniżej jednego slota na zapytanie w średniej.

### 5.2 Filtrowany Recall@8 EN (wariant D) — progi pre-registered PRZED runem (docstring `scripts/eval_en_filtered.py`: F ≥ 0.961 realne; F < 0.931 częściowo; F < 0.90 mocno)

Pre-retrieval filter: `retrieve(query, top_k=40)` → wyklucz `related-sections, heading-only, code-listing` → weź 8; fallback <8 po filtrze = STOP (nie wystąpił).

- **F = 0.9808 (51/52)**, MRR 0.912, Δ = **F − B = −0.0002**; p50 = 104.5 ms, p95 = 133.2 ms (sanity 1 PASS); q012 top8 = [32,36,35,35,33,35,35,36] — top-8 bez `related-sections` (sanity 2 PASS; sygnatura 3× Estimating zmieniona przez filtr — spodziewane, q012 wciąż any-hit przez topic 35/36).
- per-category: factual 12/12, comparison 6/6, reasoning 14/14, relational 5/5, false_premise 7/7. Miss: **q043** (1; w sesji 4 miss był q018 — filtr zmienia kompozycję kandydatów przy tych samych 51/52). Avg filtered_out = 3.98/query (239/60).
- Werdykt progu: **F ≥ 0.961** → chunki-śmieci nie kontaminują wyniku; 0.981 przechodzi filtr.
- known_limitation: candidate_pool=40 może zmienić ranking RRF względem retrievalu bez filtra; ale delta (−0.0002) czyni to nieistotnym.

### 5.3 Audyt kontaminacji tłumaczenia (3-gramy verbatim, próg flagi 30% z briefu; `scripts/audit_translation_contamination.py` → `handoff/session-5-contamination-audit.json`)

- Zbiory: A = chunky o topic ∈ gold_topics (konserwatywny superset — patrz 5.1 known issue: nie per-rank), B = `reference_answer` PL (zawiera EN cytaty; obecne 52/52, gęstość EN ~9.15 słów/100 znaków, q001 zawiera passus „Every piece of knowledge…" verbatim).
- Wynik: **≤ 3 flag → tłumaczenie „czyste"** — dokładnie 52 zmierzone, **1 flaga: q006 (31.2% z A, 0.0% z B)**; przykłady 3-gramów `design by contract`, `preconditions postconditions and`, `is responsible for` — to terminy dziedziny projektowania kontraktowego, których q006 wprost dotyczy; overlap wynika z terminologii domeny, nie ze sklejenia z reference_answer.
- **B = 0.0% we wszystkich 52 pytaniach** — EN pytania NIE zawierają 3-gramów verbatim z EN cytotów w reference_answer. Hipoteza „tłumacz skopiował terminy z widzianego reference_answer" **niewsparta na poziomie 3-gramowym**.
- sanity q001: 9.1% (≤20 PASS).
- known_limitation: 3-gram verbatim nie wyłapie parafrazy/pożyczenia terminów bez pełnego trigramu; audyt wspiera „czyste", nie dowodzi go wprost.

### Werdykt sesji 5 (wg drzewa decyzyjnego FAZY 5)

F = 0.9808 ≥ 0.961, audyt = 1/52 flag → generowany werdykt: **„0.981 realne"** (chunki-śmieci i kontaminacja NIE tłumaczą skoku +0.154; skok jest spójny z EN-bge-small-en-v1.5 na EN korpusie + BM25). Finalna decyzja (zakres sesji 6) — CZEKAM NA DECYZJĘ właściciela.

Sesja 6 = answer-layer EN na Tier 3, naprawia trzy błędy metryki sesji 3: (a) walidacja termów przeciw top-8 przed spawnem, (b) lematyzacja spaCy EN, (c) input-stage check per multi-topic. Wynik sesji 5 (0.981 realne) jest podstawą — bez filtra, zgodnie z werdyktem.

## Sesja 6 — answer-layer EN (pomiar 2026-10-18, Tier 3, spaCy lematy + walidacja termów)

Pre-registration frozen przed spawnem #1 (`handoff/session-6/preregistration.md`): lematy EN (nie stemy), walidowane przeciw top-8 przed spawnem (poprawka #1 sesji 3), input-stage check per multi-topic (1: any; 2: all; ≥3: ceil(n/2)) (poprawka #3), grading wyłącznie skryptem `scripts/grade_answer_pilot_v3.py` (fresh grader, bez historii). Pinowane: `spacy==3.8.16`, `en_core_web_sm==3.8.0` (zainstalowane w trakcie sesji do hermes-agent venv). Interpreter: hermes-agent venv (Python 3.11.15). Model FastEmbed: `BAAI/bge-small-en-v1.5` (EN-only, potwierdzone z `build_hybrid.py`).

- **Dump EN Tier 3** (`scripts/dump_answer_pilot_en.py` → `handoff/session-6/dumps/dump.json`): `retrieve()` top_k=8 (NIE `full_retrieve`), timing per pytanie: **p50 = 87.6 ms, p95 = 99.05 ms** (n=23) — sanity 1 PASS. q012 top-8 = `[32,36,35,35,35,36,36,35]` — sygnatura Tier 3 (sanity 2 PASS).
- **Input-stage check:** 13 hit, 2 miss — **q008** (gold [24,25], top-8 tylko 24; all-reguła dla 2), **q015** (gold 9 tematów, top-8 zawiera 48/50/51 = 3 < 5). q007 = HIT (1 topic), q012 = HIT (35 i 36 w top-8), q014 = HIT (topic 45 w top-8) — przewidziane missy sesji 3 nie powtórzyły się w EN.
- **Walidacja termów:** usunięte przed spawnem („not locatable in top-8"): representation (q001), repair (q005), state/publish/subscribe (q007), cripple (q008, i tak miss), interdependence (q010), discover (q014). Pełna lista: `handoff/session-6/term-validation.json`.
- **Mechanika spawnów (odchylenie zapisane):** pierwsza próba z briefami w Temp zakończyła się 22× refusal z powodu `permission denied: external directory` — artefakt uprawnień read podagenta, nie answer-layer; **nieważne, powtórzone** z briefami w `handoff/session-6-briefs/` (workspace, poza deny-ścieżkami korpusu; 1:1 z dumpa, verbatim). 22 spawny (13 answerable + 8 unanswerable + 1 canary), jeden spawn = jedno pytanie, model `opencode/glm-5.3-flash-free`.
- **Pomiar:** answerable **strict = 10/13** (próg ≥70% spawnych = ≥10/13 — **spełniony**). Fails: **q007** = refusal mimo topic 29 w top-8 (×2, ranki 3 i 5) — answer-layer failure, pierwsza taka na EN; **q012** = brak lematu `mailbox` (odpowiedź o aktorach/blackboard poprawna merytorycznie, pisała o „one-way asynchronous messages"); **q014** = brak lematu `surface` (odpowiedź poprawna merytorycznie — odrzucenie false premise; walidacja termu była, odpowiedź nie użyła tego słowa).
- **Unanswerable: 8/8 refusal** (marker `NOT IN THE BOOK`). **Canary: refusal** — brak kontaminacji pamięci.
- Raw: `handoff/session-6/answers-raw.json`; grader → `handoff/session-6/grading-results-v3.json`.
- known_limitation: topic-level input-stage proxy nie gwarantuje chunk-level sufficiency; `delegation`/`delegate` to różne lematy spaCy; termy mierzą obecność leksykalną, nie jakość merytoryczną (q012/q014 przeszłyby ocenę semantyczną).
- **To jest pomiar, nie wniosek: strict 10/13, refusal 8/8, canary clean, input-stage missy q008+q015.**

## EN vs PL query na Tier 3 (sesja 4, pomiar 2026-10-18)

Cel: zmierzyć, czy angielskie query poprawia Recall@8 na produkcyjnym Tier 3 względem polskiego baseline — na zamrożonym przed runem angielskim gold secie. Pre-rejestracja: progi zapisane przed runem (S56, w docstringu `scripts/eval_en_vs_pl.py`): B ≥ A+0.02 → EN wchodzi; A < 0.807 → RED FLAG STOP; sanity gate mediana < 500 ms; sygnatura q012 = 3× Estimating.

- **Zamrożony EN gold set:** `eval/gold_set_extended_en.json` (commit przed pierwszym retrieve; 52 answerable + 8 unanswerable = 60; topics + index_fingerprint wiernie skopiowane z PL, walidacja assert: 60/60 indeks równe; fingerprint `sha256:540a8a64e14d...`). Tłumaczenie: agent + reverse-translation check — drift 0 = 58/60, drift 1 = q005 i q037 (parafraza), **drift 2 = 0/60**. reference_answer NIE tłumaczone (sesja 5).
- **Model FastEmbed (FAZA 2, verbatim):** `TextEmbedding()` default = **`BAAI/bge-small-en-v1.5`** (build_hybrid.py L70: „default: BAAI/bge-small-en-v1.5"), **EN-only** — wektor z polskiego query to szum, polski sygnał był praktycznie tylko BM25 terminów technicznych.
- **Pomiar (ten sam indeks `db/rag.db`, ten sam `retrieve()` Tier 3, top_k=8, interpreter hermes venv, cwd projektu, bez re-build):**
  - **A (PL, dziś)**: Recall@8 any = **0.827 (43/52)**, MRR 0.648, p50 = 100.3 ms, p95 = 122.2 ms. Q012 sygnatura = 3× Estimating ✓ (PASS). misses: q014, q022, q024, fp001, fp002, fp006, fp007, q034, q035 (9).
  - **B (EN)**: Recall@8 any = **0.981 (51/52)**, MRR 0.895, p50 = 102.0 ms, p95 = 126.7 ms. misses: q018 (1). q014 top-8 = 5× topic 45 (4×+#6) — input-stage miss z PL naprawiony.
  - **C (PL+EN, rrf_fuse)**: Recall@8 any = **1.000 (52/52)**, MRR 0.900, p50 = 180.8 ms, p95 = 194.5 ms. Zero misses.
- **Werdykt pre-registered: Δ = B − A = +0.154 ≥ +0.02 — próg spełniony** (RED FLAG nie; sanity PASS). Per-category B−A: false_premise +0.417 (7/12→12/12), factual +0.167 (10/12→12/12), reasoning +0.071 (13/14→14/14), comparison 0.000 (5/6; q018 regression EN), relational 0.000 (5/5). Regressje: tylko q018 (topic 32 w B top-8 = [16,30,10,6,8,51,11,22]).
- **C bingo:** C naprawia wszystkie 9 PL-missów i jedyną regresję B (q018 found w C na #4 kosztem 1.8× latencji — nadal pod progiem).
- Raw: `handoff/en-vs-pl-tier3-2026-10-18/results.json` (per pytanie: id, top8topics, hit, dt_ms).
- **Pytanie do właściciela (CZEKAM NA DECYZJĘ):** (1) B czy C do produkcji — B sam naprawia drastycznie (0.827→0.981, ta sama latencja ~100 ms), a C daje pełne pokrycie za +80 ms p50; czy runtime PL→EN na wejściu (osobna warstwa, osobna latencja)? (2) Primary-Topic Recall dla comparison — retired (T13/S64) czy przedefiniowany? (3) Sesja 5 — answer-layer EN + przeprojektowana metryka terminowa (lematyzacja + walidacja termów): potwierdzasz?

## Answer-layer pilot (pomiar 2026-10-18, sesja 2 — NIEINTERPRETOWALNY dla produkcji; patrz correction wyżej)

Izolacja świeżym subagentem **zweryfikowana konfiguracją**: custom agent `.opencode/agents/answerpilot.md` — `deny "*"` + allow `read *` + deny `read` na ścieżkach korpusu (`**/the-pragmatic-programmer-retrieval/**`, `**/data/**`, `**/eval/**`, `**/db/**`, `**/scripts/**`, `**/starter/**`; kolejność reguł ma znaczenie — deny-all bez allow-read zabija spawn: „OpenCode free tier" błąd). Probe'y potwierdziły: shell/glob/grep/web/edit zablokowane, chunks.json i gold_set niedostępne (`KORPUS ZABLOKOWANY`), model subagenta = `opencode/glm-5.3-flash-free`.

Pomiar (jeden spawn = jedno pytanie, chunki verbatim top-8, brief samowystarczalny):

- **Answerable 14 spawned** (q001–q013, q015; q014 = input-stage miss, nie spawnowany — gold topic 45 poza top-8, top-8 = [9,13,11,40,44,5,47,37]). Próg pre-registered ≥70% (≥10/14):
  - **strict (angielskie stemy przeciwko polskim odpowiedziom): 2/14** (q006, q015) — próg niespełniony; metryka w tej formie mierzyła cytat angielski, nie koncepcję.
  - **semantic (równoważność polska, ewidencja post-hoc w `scripts/grade_answer_pilot.py`): 13/14** — próg spełniony (tylko q007: odmowa — top-8 zawierało 1 z 4 strategii z Topic 29; granica input-stage/answer-layer, nie tuning).
- **Korekta 2026-10-18 (sesja 3): pomiar sesji 2 nieinterpretowalny dla produkcji.** (a) dump użył `full_retrieve` = Tier 4, nie `retrieve` = Tier 3 — q012 w dumpie = 5× Blackboards (sygnatura rerankera; sesja 1 na Tier 3 dawała 3× Estimating), czas dumpu minuty zamiast ~2 s; (b) semantic map w graderze była editowana po zobaczeniu wyników (S62): dodano q010 minimiz→minimalizowaniu, usunięto q013 coincid. Liczby 13/14 i 8/8 dotyczą Tier 4 z metryką post-hoc. Sesja 3 (ta flaga) to poprawiony pomiar: Tier 3 (`retrieve`), timing w dumpie, polskie termy pre-registered przed spawnem, strict only.

- **Unanswerable: 8/8 refusal** (marker dokładny `BRAK W KSIĄŻCE`) — próg ≥6/8 spełniony.
- **Canary: refusal** (pytanie o DRY + chunki Topic 31/28/10/8; brak kontaminacji pamięci modelu).
- Surowe outputy: `handoff/pilot-answer-layer-2026-10-18/answers-raw.json`; grader deterministyczny: `scripts/grade_answer_pilot.py` → `handoff/pilot-answer-layer-2026-10-18/grading-results.json`; dumpy: `handoff/pilot-answer-layer-2026-10-18/dumps/`.
- Artefakty generacji modelu w surowych outputach (raportowane, nie ukrywane): „开销" w q009 (model sam poprawia w drugim zdaniu), „Within"/„Zupełnie" w q010, skr. fleksyjne w q013. Koszt: zero lokalnego modelu; koszt tokenowy = top-8 (~5.4k znaków) × 23 spawn.
- **Pytanie do właściciela (CZEKAM NA DECYZJĘ):** (1) czy czytanie metryki terminowej = semantic (concept-presence), czy strict-EN — pilotaż daje 13/14 vs 2/14 zależnie od tego; (2) precedens: q010 answer-layer przyszedł poprawnie z chunka oznaczonego topic 10 mimo gold primary 9 — argument za przeniesieniem/retire Primary-Topic Recall dla comparison (T13/S64), przedefiniowaniem „primary = zbiór topiców" albo pozostawieniem metryki przy retrieval-only gating.

## Zadanie 5 — Cross-encoder @ 100 kandydatów (rozstrzygnięte, 2026-10-16)

Cel: ustalić, czy Tier 4 ma sens przy 100 kandydatach, mierząc **skalowanie kosztu predykcji** (20/40/100 par) zamiast ślepego pełnego `--wide` (~20 min na CPU).

Pomiar: `bge-reranker-base`, CPU, jedno zapytanie, tekst syntetyczny o stałej długości (miarodajny dla samego skalowania po `n`; nie dla latencji absolutnej):

| pary | czas | ms/para |
|---|---|---|
| 20 | 957 ms | 47.86 |
| 40 | 1937 ms | 48.42 |
| 100 | 4298 ms | 42.98 |

- **Skalowanie ~liniowe:** 20→40 = 2.02×, 40→100 = 2.22×. Zysk per-para przy 100 to ~10% (w granicach szumu), nie sublinearność ratująca wide.
- Latencja na realnym tekście chunków jest ~5× wyższa: r40 real = **9621 ms** mediana przy 40 parach. Ekstrapolacja → **100 par ≈ ~24 s/zapytanie**.
- Pełny wynik r40 (n=60): Recall@8 any = **0.865**, primary = 0.827, MRR = **0.715**, nDCG@8 = 0.751, mediana 9621 ms, p95 17842 ms.

**Decyzja: Tier 4 (cross-encoder) trwale wykluczony ze ścieżki produkcyjnej.** +0.038 Recall@8 nad Tier 3 (0.827 → 0.865) za ~93× latencji (103 ms → 9621 ms @ 40; ~24 s @ 100). Cache (`data/rerank_cache.json`) przyspiesza **iterację eval**, nie **nowe zapytanie** (nowe pytanie = cache miss = pełne ~10 s). MRR nie ratuje — sam koszt dyskwalifikuje. Nie uruchamiano `--wide` (bezwartościowy przy liniowym skalowaniu). Produkcja pozostaje **Tier 3 (Hybrid RRF)**.
## Sesja 7/8 — Traceability Repair & R15 Fix (2026-10-18)

- **Forensyka R15:** R15 zielone przy `0d0a585` (sesja 5); po ingest sesji 6 `fe3a511b` spadło na rank 8 (score −14.59) dla query „FTS5 unicode61".
- **Naprawa:** Opcja B — wykluczenie `01a14af3`, `ses_eb2d1e180`, `ses_ebce63c7` z case „FTS decision" w `scripts/memory/eval_queries.json`.
- **Analiza wykluczeń (sesja 8):** Klasyfikacja jako test hygiene (żadna ze zindeksowanych sesji nie zawiera odpowiedzi na query, jedynie marginalne dopasowania słowne/noise).
- **R15 po naprawie:** `hit@5=1.000 MRR=0.654 (15/15)`, exit 0.
- **Root commit / fix commit:** Root commit sesji 7 (`c605c95`) zaktualizował flagę, ale pominął fix w working tree; sesja 8 domknęła traceability commitem `8da09f6` (`fix(memory): traceability repair - eval_queries.json FTS decision exclusion committed; forensics + pre-registered decision`).

## Sesja 9/10 — Zamknięcie projektu (2026-10-18)

**Decyzja właściciela: Opcja D — zamknięcie projektu.** Wszystkie metryki zmierzone, traceability domknięte, brak otwartej pracy badawczej.

- **Pomiar końcowy (sesja 6, Tier 3 EN):** strict 10/13 (próg ≥70% spełniony), refusal 8/8 `NOT IN THE BOOK`, canary clean; dump p50 87.6 ms / p95 99.05 ms (sanity 1 PASS), sygnatura q012 = Tier 3 (sanity 2 PASS). Commit `8a85a8e`.
- **Fix R15 (sesja 7/8):** wykluczenie `01a14af3`, `ses_eb2d1e180`, `ses_ebce63c7` z case „FTS decision" (`eval_queries.json`) — test hygiene, wszystkie 3 noise (nie zawierają odpowiedzi na „FTS5 unicode61"). R15 `hit@5=1.000 MRR=0.654 (15/15)`. Commit `8da09f6`.
- **Flaga i domknięcie (sesja 9):** raport sesji 9 zawierał fałszywe `git cat-file -t 7a46d72: fatal` — poprawione, prawdziwy output to `commit`; `session-9-report-correction.md` (commit `0c27dd0`), decisions update (`c43187d`), finalna linia sesji 9 w fladze (`f5bda4a`).
- **Stan końcowy:** working tree clean, R15 zielone, workspace integrity zielone, `scripts/memory/*.db` w `.gitignore` (ephemeral artefakt z memory_index).
- **Postęp:** sesja 9/10 = ostatnia sesja projektowa; brak otwartej pracy.

## Sesja 10/11 — Znany gap w S56 audit trail (2026-10-18)

**Status projektu: zamknięty (Opcja D), z jednym jawnie udokumentowanym gapem w S56 audit trail.**

- **Co się stało:** `handoff/session-10-content.md` (pre-registration §Sesja 9/10, 1274 B) został zapisany przez `write` tool (raport: `Successfully wrote 1274 bytes`), chwilę był `??` w `git status --short`, ale nie trafił do historii gita — `git add handoff/session-10-content.md` zwrócił `fatal: pathspec`, a `Get-ChildItem C:\Users\Mateusz\Desktop\root_workspace\handoff` (absolutna ścieżka) potwierdził brak pliku. `git log --all -- handoff/session-10-content.md` → `(no output)`.
- **Co jest:** treść §Sesja 9/10 jest w `b0e3c43` (CONTEXT.md + MAP.md) i w `d3a0056` (STATE.md). Decyzja „Opcja D" jest w `f5bda4a` (flaga). Pre-registration nie jest utrwalona w historii.
- **Root cause:** nieustalony w sesji 10. Test persystencji `write` tool wykonany w sesji 11 — wynik: `write` tool działa poprawnie (Test-Path: True, Length > 0, git status ??) dla ścieżek relatywnych do root_workspace. Incydent sesji 10 był jednorazowy lub specyficzny dla ówczesnego środowiska/procesu.
- **Gap zapisany:** `handoff/session-10-known-gap.md` (root, commit `bdd9680`).
- **Co NIE robić:** nie re-tworzyć `session-10-content.md` po fakcie (S56: pre-registration musi być przed wynikiem; rekonstrukcja po wyniku to fabrykacja). Gap zostaje jawny.
## Post-closure backlog

— Planowany backlog na wypadek ewentualnego reopen projektu (Opcja D):
1. **Chunk-level sufficiency diagnoza:** analiza odsetka niepełnych chunków w trudnych pytaniach (por. sesja 4/5).
2. **Contextual retrieval augmentacja:** testowanie dodawania kontekstu dokumentu do chunków przed embeddingiem.
3. **Multi-topic comparison benchmarking:** usprawnienie metryk dla zapytań złożonych z wielu tematów.
Stan: Odblokowane decyzją właściciela (E = Tak, 2026-10-18); scope w `handoff/session-17-d-scope.md` (root workspace); wykonanie w osobnych sesjach research.
