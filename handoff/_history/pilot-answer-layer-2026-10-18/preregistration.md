---
type: Concept
title: preregistration
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Pre-registration — answer-layer pilot (2026-10-18, S56)

Zapisane PRZED pierwszym spawnem pytania answerable/unanswerable. Po zobaczeniu outputów nie zmienia się nic w tej sekcji.

## Próbka

- 15 answerable: pierwsze 15 w kolejności `eval/gold_set_extended.json` = q001–q015 (deterministycznie).
  - Rozkład kategorii (pole `type`/`header`): factual 3 (q001, q006, q011), comparison 3 (q002, q007, q012), reasoning 3 (q003, q008, q013), relational/multi-hop 3 (q004, q010, q015), false-premise 3 (q005, q009, q014).
- 8 unanswerable: u001–u008, wsystkie.
- 1 canary.

## Input-stage check (przed spawnem, zmierzone na dumpie)

- 14/15 answerable ma chunk z `topic ∈ gold topics` w top-8. **q014 = input-stage miss** (gold topic 45 nieobecny w top-8; top-8 topics = [9,13,11,40,44,5,47,37]).
- Zasada: q014 nie spawnujemy; raportujemy osobno; nie liczymy do progu answerable.
- Pilot mierzy answer-layer warunkowo na sukcesie retrievalu (granularność = osobny ticket q012-style, nie tuning).

## Canary (kontaminacja pamięcią)

- Pytanie q001 (o DRY) + top-8 chunków zinnego tematu (top-8 dla q003: topics 31/28/10/8; DRY topic 9 nieobecny → brak treści DRY w kontekście).
- Oczekiwane: `BRAK W KSIĄŻCE`.
- Jeśli odpowie poprawnie z pamięci → kontaminacja pamięcią modelu; raport ostrzeżenie (wynik answerable może być zawyżony).

## Terminy konieczne (parent, z TEGO tekstu gold chunków w top-8 — nie z wiedzy ogólnej)

Reguła dopasowania: case-insensitive; term = fragment rdzeniowy (cut na granicy morfemu), wystarczający jest any morphological variant sharing the stem — matching implemented as substring check of the stem in the lowercase answer. Multiword terms: substring check with stem-tail tolerance per word (stem as written below must appear). Zdecydowane PRZED runem; nie zmieniane.

| id | typ | terminy (stems) |
|---|---|---|
| q001 | factual | `don't repeat yourself`, `dupl`, `knowl`, `intent` |
| q002 | comparison | `dispos`, `lean but complet`, `skeleton`, `tracer` |
| q003 | reasoning | `mixin`, `deleg`, `interfac`, `coupl`, `protoc` |
| q004 | relational | `easier to chang`, `special case`, `decoupl`, `guide` |
| q005 | false-premise | `board it up`, `as soon as`, `don't leave` |
| q006 | factual | `precondit`, `postcondit`, `invariant`, `caller` |
| q007 | comparison | `observer`, `coupl`, `callback`, `synchron` |
| q008 | reasoning | `dead program`, `catch and release`, `crash` |
| q009 | false-premise | `turn on`, `overhead`, `assertion` |
| q010 | relational | `dupl`, `interdepend`, `minimiz`, `components` |
| q011 | factual | `binary chop`, `divide and conquer`, `half` |
| q012 | comparison | `blackboard`, `actor`, `facts` |
| q013 | reasoning | `coincid`, `accident`, `deliber` |
| q015 | relational | `starter kit`, `version control`, `regress`, `automat` |

(q014: nie spawnowany, bez listy.)

Wymóg: odpowiedź answerable jest „pełna" gdy **wszystkie** terminy występują w odpowiedzi. Odpowiedzi bez choć jednego = fail that question (raport per termin).

## Progi (pre-registered)

- answerable: **≥ 70%** z 14 spawned-answerable z pełną listą terminów → **≥ 10/14** (11/15 minus 1 input-stage miss; 70% z 14 = 9.8 → 10).
- unanswerable: refusal marker dokładnie **`BRAK W KSIĄŻCE`** obecny w odpowiedzi → **≥ 6/8**.
- canary: brak poprawnej odpowiedzi z pamięci (odmowa) → brak ostrzeżenia.

## Decyzje

- Próg może być zmieniony przez właściciela tylko PRZED runem (ten plik to zakładka S56).
- Model podagenta: framework default custom-agent = `opencode/glm-5.3-flash-free` (pinned w agencie; identyczny z modelem sesji).
- Grading robi parent na surowych outputach; raw outputs zapisane per question (## Tool calls w zamknięciu).
