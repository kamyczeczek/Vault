---
type: Concept
title: preregistration
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Pre-registration — answer-layer EN pilot, sesja 6 (2026-10-18, przed spawnem #1)

Zamrożone przed spawn #1 (S56). Po zobaczeniu wyników nie zmienia się lista termów, progi, reguła dopasowania, wersja spaCy (S56/S62). Jeśli metryka okaże się wadliwa — to jest wynik, nie problem do naprawy w tej sesji.

## Wejście
- Dump: Tier 3 `retrieve()` (RRF top-8, bez rerankera; NIE `full_retrieve`), interpreter `C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (Python 3.11.15), cwd projektu.
- Model FastEmbed: `BAAI/bge-small-en-v1.5` (EN-only) — potwierdzone z `build_hybrid.py` („default: BAAI/bge-small-en-v1.5").
- **Pinowanie:** `spacy==3.8.16`, `en_core_web_sm==3.8.0`.
- Surowe odpowiedzi PL gold setu NIE są tłumaczone; `reference_answer` czytane z `gold_set_extended.json` **wyłącznie w celu wyprowadzenia termów** (jawny cel: „wiem, co dobra odpowiedź powinna zawierać"), walidacja termów przeciw top-8 **przed** spawnem.

## Timing (FAZA 3.2)
p50 = 87.6 ms, p95 = 99.05 ms, n = 23 — **sanity 1 PASS** (mediana < 500 ms). q012 top-8 topics = `[32,36,35,35,35,36,36,35]` — sygnatura Tier 3 (nie 5× Blackboards; sanity 2 PASS).

## Próbka (FAZA 3.1)
- 15 answerable q001–q015 (deterministycznie, jak sesja 3), 8 unanswerable u001–u008, 1 canary (pytanie q001 + chunki q003).
- Rozkład kategorii q001–q015 (z EN gold setu): factual/definition 2 (q001, q006), comparison 3 (q002, q007, q012), reasoning 2 (q003, q013), relational 3 (q004, q010, q015), false-premise 4 (q005, q009, q014) + q005 false-premise → łącznie 15: factual 2, comparison 3, reasoning 2, relational 3, false-premise 4, factual+procedure 1 (q011).

## Input-stage check per multi-topic (FAZA 3.4, poprawka #3)
Reguła: `len(gold_topics)==1 → any`; `==2 → all`; `>=3 → >= ceil(n/2)`.
- **Wynik (z walidacji `scripts/validate_terms_session6.py`): 13 hit, 2 miss.**
- Missy: **q008** (gold [24,25], top-8 zawiera tylko 24), **q015** (gold 9 tematów, top-8 zawiera 48,50,51 = 3 < ceil(9/2)=5). q012 i q007 = HIT (niepowtarzalność błędów sesji 3). q014 = HIT (top-8 zawiera topic 45).
- Missy NIE są spawnowane, nie liczą się do progu.
- known_limitation: topic-level proxy — nie gwarantuje, że konkretny chunk z odpowiedzią jest w top-8 (chunk-level sufficiency = deferred).

## Termy wymagane — lematy spaCy EN, zwalidowane przeciw top-8 (poprawka #1)
Reguła dopasowania (zamrożona):
```python
def lemmatize(text):
    doc = nlp(text.lower())
    return set(tok.lemma_ for tok in doc if not tok.is_stop and not tok.is_punct)
def match(term, answer_text):
    return term in lemmatize(answer_text)
```
Walidacja: term ∈ lematy co najmniej jednego z 8 chunków top-8 danego pytania; nieobecne usunięte **przed spawnem** (zapis poniżej jako „removed: not locatable in top-8").

| qid | termy (frozen) | removed (pre-spawn) |
|---|---|---|
| q001 | knowledge, intent, duplication | representation |
| q002 | tracer, prototype, skeleton, disposable | — |
| q003 | inheritance, coupling, delegation, mixin, interface | — |
| q004 | value, rule, change, principle | — |
| q005 | broken, window, fix | repair |
| q006 | precondition, postcondition, invariant, caller | — |
| q007 | observer, event, coupling | state, publish, subscribe |
| q009 | assertion, turn, production, net | — |
| q010 | duplication, knowledge, orthogonality | interdependence |
| q011 | binary, chop, half | — |
| q012 | actor, blackboard, mailbox, message | — |
| q013 | coincidence, accident, luck | — |
| q014 | requirement, want, surface | discover (sign, policy walidowane, niespawnowane jako zbędne — decision pre-spawn: surface) |
| (q008) | input-stage MISS — brak spawnu | crippled był walidowany, nieistotny (brak spawnu) |
| (q015) | input-stage MISS — brak spawnu | — |

- known_limitation: `delegation` i `delegate` to różne lematy spaCy; termy uwzględniają formę z chunków (`delegation` w q003 — obie formy łapane przez `delegation` + kontekst).
- known_limitation: `tok.is_stop` wyrzuca „off"/„on" itp. z odpowiedzi; term `turn` (q009) wymaga formy „turning off" → lemat `turn` obecny.

## Progi (pre-registered)
- Answerable: **≥ 70% spawnych** ze wszystkimi wymaganymi lematami. Spawn = 13 → próg **≥ 10/13**.
- Unanswerable: refusal **≥ 6/8**, marker dokładnie `NOT IN THE BOOK`.
- Canary (pytanie q001 + chunki q003): refusal. Odpowiedź z pamięci = ostrzeżenie o kontaminacji.

## Zasady spawnu
- Jeden spawn = jedno pytanie; brief EN samowystarczalny; chunki verbatim z dumpa (z nagłówkami „Topic N"); brak cięcia.
- Izolacja: config `.opencode/agents/answerpilot.md` (deny-all + read allow poza korpusem; probe-verified sesja 2, re-use bez re-weryfikacji). Model `opencode/glm-5.3-flash-free`.
- **Mechanika tej sesji (odchylenie zapisane):** fragmenty podane plikiem `C:\Users\Mateusz\AppData\Local\Temp\opencode\session6\<qid>.txt` (eksport `scripts/export_briefs_session6.py`, 1:1 z dumpa, verbatim) — pytanie inline w briefie, plik poza drzewem projektu, deny rules nie blokują. Cel: chunki verbatim bez przepompowywania przez kontekst parenta. Podagent widzi wyłącznie pytanie + ścieżkę z fragmentami; nie widzi metryk, termów, historii.
- Grading: skrypt `scripts/grade_answer_pilot_v3.py` (fresh grader — bez historii, bez dostrojenia). Zakaz zmian termów po zobaczeniu wyników.

## Interpretacja (zapisana przed runem)
- ≥ 70% spawnych: answer-layer EN działa na tej próbce.
- 50–69%: częściowy sukces; sesja 7 = analiza failów (bez tuningu).
- < 50%: answer-layer EN słaby; sesja 7 = diagnoza (lematyzacja vs treść vs kontekst — bez zmiany metryki).
