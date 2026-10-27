---
type: Concept
title: CONTRACT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# CONTRACT.md — pilot graphrag (Faza 2 transferu ARL)

Pilot w projekcie-kandydacie dla Fazy 2 z flagi `arl-transfer-pivot`
(2026-10-08): "Faza 2 pilot w 1 projekcie-kandydacie (NIE root)".
`knowledge-retrieval` jest tym kandydatem; ten pilot jest jego pierwszym
pilotem. Rozstrzygnięcie trasy: użytkownik wybrał trasę A (2026-10-10).

## One job

Deterministyczna warstwa planowania i orkiestracji zapytań do grafu wiedzy:
pytanie → plan JSON → zweryfikowane dowody → odpowiedź wyłącznie z grafu.
Zero halucynacji, pełny ślad wykonania. Spec: sesja `goose 20261008_3`
("Projekt Agenta GraphRAG", transkrypt w root
`scripts/_scratch/graphrag_session.md` — derived, gitignored).

## Inputs

- Working (ten pilot): `task_plan.md`, `findings.md`, `progress.md`
  (planning-with-files; szablon: root `skills/planning-with-files/SKILL.md`)
- Working (ten pilot): `.wayfinder/MAP.md` + `tickets/D-001..D-005.md`
  (decyzje otwarte; forma: ARL `.wayfinder/MAP.md` jako precedens)
- Reference (każdy krok): instrukcja systemowa z sesji 05 — 8 narzędzi,
  7-krokowy workflow (Krok 0 analiza → Krok 7 ślad+cytowania), format planu
  JSON, format odpowiedzi, obsługa błędów, kryteria sukcesu
  (transkrypt, linie 11–155)
- Reference: archiwalny `graph.db`
  (`../../_archive/agentic-research-lab/knowledge/graph/graph.db`,
  read-only) — TYLKO jeśli D-002 rozstrzygnie "read-only na archiwum".
  Do tego czasu żaden kod pilota nie otwiera tej bazy.

## Process

1. **Decyzje najpierw.** Bilety D-001..D-005 są otwarte; żaden kod
   implementacyjny nie powstaje przed rozstrzygnięciem D-002 (backend)
   i D-003 (seed). Rusztowanie nie decyduje po cichu.
2. **Plan na dysku.** `task_plan.md` prowadzi fazy; po każdych 2 operacjach
   odczytu zapis do `findings.md`; po każdej akcji update `progress.md`.
3. **Scaffold, nie produkt.** Done to NIE "projekt powstał". Done to dowód:
   jedno pytanie → plan JSON → trace → odpowiedź z dowodami + confidence
   (test oracle-first: wartość oczekiwana ze specyfikacji, nie z kodu).
4. **Loader skilli jest zepsuty** (ten sam błąd co w sesji 05: `load_skill`
   zwraca "not found"). Skille czyta się z dysku (`../../../skills/<name>/SKILL.md`).
   Vendoring do `skills/` + wpis w MANIFEST.md dopiero przy pierwszym użyciu.

## Outputs

- `proof/<slug>/` — dowód: `plan.json`, `trace.md`, `answer.md` z dowodami
  (triple/ścieżki) i confidence. Jeden katalog na pytanie.
- Rozstrzygnięcia D-001..D-005 jako komentarze-resolution w biletach
  + wpisy w mapie "Decisions so far".
- Raport pilota w `../reports/` (nazwa: `graphrag-pilot_<finding>.md`)
  zgodnie z kontraktem KR.

## Human check

Przeczytaj odpowiedź dowodową i zapytaj: czy każde twierdzenie ma triple
lub ścieżkę z grafu? Twierdzenie bez pokrycia w dowodach to halucynacja —
odrzuć je, nie tłumacz. Potem sprawdź confidence: wysoki przy <2 dowodach
to kłamstwo skali, nie ostrożność.

## Open work

- D-001..D-005 otwarte (szczegóły: `.wayfinder/tickets/`).
- D-004 (JSON schema) czeka na D-001 (słownik relacji) i D-002 (backend).
- Gate D transferu (flaga pivotu): brak poprawy cold-start/handoff
  => brak promocji. Ten pilot mierzy grounding (0 nieuzasadnionych
  twierdzeń), nie szybkość.
- Wiersz w AGENTS.md (D-005) dopiero po dowodzie — blizna R13: wiersz
  w AGENTS.md to zmiana ≥3-plikowa z nową wersją raportu.
## Fazy 6: Falsyfikator (dowód groundingu) — v2 (2026-10-10)

### SUPERSEDED — v1 (oracle-second, nie używać jako testu)

V1 pytała: „Które dokumenty są scarrane przez scar:vera-expa-001?" z oczekiwaniem
(3 triple SCARRED_FROM, conf=0.7) opisanym jako „znane z sesji, nie z grafu".
Powody superseded (2026-10-10):
- Oczekiwanie skopiowano z wyniku query na `graph.db` — oracle-second, test nie mógł zawieść.
- Węzeł `scar:vera-expa-001` pochodzi z korpusu ARL, nie z sesji `goose 20261008_3`
  (transkrypt go nie wspomina) — adnotacja „znana z sesji" fałszywa.
- Pytanie krawędziowe (`SELECT dst WHERE src=X AND kind`) testuje enumerację, nie grounding.

### v2 — pytanie treściowe + odmowa (oracle-first)

**Q-ground (treściowe, wymaga syntezy z `nodes.body`):**
„Czym jest SEVerA i jak się ma do self-evolving agents?"
- Źródło oczekiwania treściowego: ZDEFINIOWANE 2026-10-10 — człowiek wkleił
  w sesji review abstrakt arXiv:2603.25111v2 (Banerjee/Xu/Ie/Zhang/Peng),
  zweryfikowany ręcznie, spoza grafu. Kondensacja oracle (wierna, przed query):
  (1) self-evolving agents: planner LLM syntezuje program agenta (modele
  parametryczne + narzędzia, np. SMT solvery), tunowane per task — ale BEZ
  gwarancji formalnych safety/correctness, co przy autonomicznym wykonaniu
  na unseen inputs rodzi ryzyko; (2) FGGM (Formally Guarded Generative Models):
  formalny kontrakt wyjścia (first-order logic) dla każdego wywołania modelu,
  rejection sampler + verified fallback, output spełnia kontrakt dla dowolnego
  inputu i parametrów; (3) SEVerA three-stage: Search (kandydaci z FGGM),
  Verification (dowód względem hard constraints dla WSZYSTKICH parametrów →
  redukcja do unconstrained learning), Learning (gradient-based, GRPO-style,
  soft objective przy zachowanej poprawności); (4) ewaluacja: constrained
  symbolic regression, invariant generation (Dafny), symbolic math synthesis,
  policy-compliant tool use (τ2-bench) — zero constraint violations + lepsza
  performance niż unconstrained/SOTA; constraints przycinają przestrzeń
  kandydatów, sterując syntezę ku lepszym agentom.
  Status: ZDEFINIOWANE — Q-ground wykonywalny.
- Kryterium mechaniczne (definiowalne bez patrzenia w graf): odpowiedź musi
  zawierać ≥1 cytat z `nodes.body`, a każde twierdzenie musi mieć pokrycie
  triple/ścieżką. Twierdzenie bez pokrycia → halucynacja (FAIL).
  Confidence wysoka przy <2 dowodach → kłamstwo skali (FAIL).
  Każdy dowód (answer.md) MUSI zawierać sekcję „Czego ten dowód NIE odróżnia"
  z ≥1 wpisem (negatywna przestrzeń artefaktu — jak `not checked:` we fladze,
  ale dla dowodu). Dowód bez tej sekcji → FAIL (kształt bez funkcji).
  Reguła z review #4 (2026-10-10): 3× z rzędu review znajdowało brakujące
  pytanie po fakcie (oracle==korpus, markery generyczne, warunek wznowienia) —
  sekcja wymusza pytanie PRZED zapisem wyniku, nie po.

**Q-refusal (oracle-first, wykonywalny dziś):**
„Jaki wpis dodała sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?"
- Źródło oczekiwania: root `SCARS.md` linia 20 (R13: wpis o cascade przy
  dodaniu wiersza do tabeli `Where to go` w AGENTS.md), zweryfikowane ręcznie
  2026-10-10 BEZ otwierania `graph.db`. Podstawa odmowy: archiwum to korpus
  literatury (10 373 nodes = tytuły papers; HANDOFF NODES: [] — ustalenie
  z poprzedniej sesji, nie z nowego query), więc nie zawiera faktów o sesjach
  workspace'u.
- Oczekiwana odpowiedź: ODMOWA z uzasadnieniem braku pokrycia (refusal = brak
  pokrycia twierdzeń dowodami, D-003). Odpowiedź treściowa lub enumeracyjna
  zamiast odmowy → FAIL.

**Kontrola bez narzędzia (konkret):**
Pytanie: Q-ground o SEVerA, zadane modelowi BEZ dostępu do grafu.
Oczekiwany wynik kontroli: odpowiedź ogólnikowa (SEVerA ≈ verified synthesis
dla self-evolving agents — wiedza z treningu), BEZ szczegółów korpusu
(bez triple'i, bez powiązania z entropy-001, bez cytatów z `nodes.body`).
Jeśli kontrola zwróci szczegóły korpusu → kontrola skażona, wynik Fazy 6 nieważny.
Różnica mierzalna: odpowiedź z grafem ma cytaty+triple, kontrola ich nie ma.

**Porażka (v2):**
- odpowiedź bez pokrycia w grafie → halucynacja
- brak odmowy na Q-refusal → halucynacja lub wyciek (graf nie ma tej odpowiedzi)
- confidence wysoka przy <2 dowodach → kłamstwo skali
- brak sekcji „Czego ten dowód NIE odróżnia" → FAIL (dowód bez negatywnej przestrzeni)

**Warunek grounding udowodniony:**
Q-ground: odpowiedź zgodna z ludzkim oczekiwaniem + pełne pokrycie dowodami;
Q-refusal: odmowa z uzasadnieniem; kontrola bez narzędzia: ogólnikowa
(rozjazd z odpowiedzią z grafem mierzalny brakiem cytatów/triple'i).

**Warunek pilot done:**
grounding udowodniony LUB świadomie zamknięty jako „kontrakt zweryfikowany,
grounding odłożony" (z zapisem w task_plan.md).

## Does not own

- Jakość rankingu/cytowań jako taka (to sam projekt KR).
- Budowę korpusu i indeksu (to ARL, zamrożone).
- Loader skilli w DSH (defekt platformy, nie tego pilota).
