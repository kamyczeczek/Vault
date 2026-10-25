---
type: experiment
title: Smoke test kontraktu odpowiedzi retrieval
description: Pięć realnych pytań sprawdzających przejście od huba semantycznego do źródła i dowodu.
status: complete
tags: [okf-rag, retrieval, evidence, benchmark]
sources:
  - EXPERIMENT-retrieval-2026-10-25.md
  - DECISION-kontrakt-odpowiedzi-retrieval.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Sprawdzić, czy kontrakt `claim → source → locator → passage → status →
confidence` działa na pięciu pytaniach, dla których Smart Connections znalazło
warstwę kuratorską.

To jest smoke test ścieżki dowodowej, a nie nowy benchmark rankingu. Wynik
semantyczny wskazuje hub; źródło i fragment zostały następnie zweryfikowane
odczytem właściwego pliku.

# Wyniki

| ID | Pytanie | Hub semantyczny | Źródło dowodu | Status | Pewność |
|---|---|---|---|---|---|
| Q01 | Jak wygląda przepływ od materiału do decyzji? | `SYNTHESIS.md:137–168` | `DECISION-minimalny-przeplyw-wiedzy.md:33–52` | `direct` | `high` |
| Q02 | Co jest źródłem prawdy i kto publikuje koncepty? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md:39–49` | `okf-rag.md:445–447` | `direct` | `high` |
| Q03 | Kiedy koncept wymaga review, provenance i kontroli świeżości? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md:76–85` | `llm-wiki.md:54–78` | `direct` | `high` |
| Q04 | Jakie są ograniczenia ekstrakcji i deduplikacji? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md:97–106` | `okf-rag.md:1134–1140` | `direct` | `high` |
| Q05 | Kiedy kompilacja wiki i retrieval są przesadą? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md:108–117` | `llm-wiki.md:59–67, 122–124` | `direct` | `high` |

# Rekordy dowodowe

## Q01 — przepływ od materiału do decyzji

- Claim: praca przechodzi od surowego materiału przez wybrane twierdzenia i
  koncept lub syntezę do decyzji albo eksperymentu.
- Source: `Notes/OKF-rag/DECISION-minimalny-przeplyw-wiedzy.md`.
- Locator: sekcja `# Decyzja`, linie `33–52`.
- Passage: „surowy materiał → wybrane twierdzenia → koncept lub synteza ze
  źródłami → decyzja albo eksperyment”.
- Status: `direct`.
- Confidence: `high`; przepływ jest zapisany wprost, a warstwa semantyczna
  prowadzi do notatki, która go formalizuje.

## Q02 — źródło prawdy i publikacja konceptów

- Claim: kompilator tworzy propozycje konceptów i linków, ale reconciler
  decyduje o opublikowanym zbiorze; output kompilatora nie jest sam w sobie
  prawdą.
- Source: `Notes/OKF-rag/okf-rag.md`.
- Locator: `## Generate OKF with llm-wiki-compiler`, linie `445–447`.
- Passage: „Automatic generation is a proposal-to-truth pipeline” oraz
  „The compiler output is never treated as final truth directly”.
- Status: `direct`.
- Confidence: `high`; źródło opisuje mechanizm bez potrzeby interpretacji.

## Q03 — review, provenance i świeżość

- Claim: trwała warstwa wiedzy wymaga cytowań, provenance, review queue,
  freshness checks i quality gates.
- Source: `Notes/OKF-rag/llm-wiki.md`.
- Locator: `What llmwiki does` i `What you get`, linie `54–78`.
- Passage: opis zawiera „source citations, review queues, freshness checks,
  and quality gates” oraz walidację cytowań i wykrywanie stron starych.
- Status: `direct`.
- Confidence: `high`; wymagane mechanizmy są wymienione w źródle.

## Q04 — ograniczenia ekstrakcji i deduplikacji

- Claim: ekstrakcja konceptów nie jest deterministyczna, a pruning duplikatów
  może pozostawić historyczne strony; automatyczna reorganizacja wymaga
  dodatkowej warstwy kontroli.
- Source: `Notes/OKF-rag/okf-rag.md`.
- Locator: sekcja `Findings`, linie `1134–1140`.
- Passage: ten sam materiał dał pięć, a potem sześć konceptów; po zmianie i
  cofnięciu źródła pozostały trzy near-duplicate pages.
- Status: `direct`.
- Confidence: `high`; wynik jest opisany jako konkretne finding, nie jako
  ogólna obietnica narzędzia.

## Q05 — kiedy ciężki pipeline jest przesadą

- Claim: kompilowany wiki/retrieval ma sens dla trwałego, cytowalnego i
  wielokrotnie używanego korpusu; jednorazowy odczyt lub szybko zmieniające się
  logi powinny pozostać przy prostym wyszukiwaniu.
- Source: `Notes/OKF-rag/llm-wiki.md`.
- Locator: `When to use this repo`, linie `59–67`, oraz `Agent decision guide`,
  linie `122–124`.
- Passage: „Do not use llmwiki ... as a replacement for ad-hoc search over
  fast-changing raw logs” oraz „A one-off file read ... does not need a wiki”.
- Status: `direct`.
- Confidence: `high`; kryterium wyboru jest zapisane explicite.

# Werdykt

Smoke test przeszedł: `5/5` hubów doprowadziło do sprawdzalnego źródła,
lokalizatora i passage; `5/5` rekordów ma status `direct` i osobny cytat.

Nie oznacza to, że Smart Connections zawsze znajdzie właściwy passage. Oznacza
tylko, że po znalezieniu huba można wymusić drugą fazę weryfikacji i nie mylić
trafienia semantycznego z dowodem.

# Następny test

Powtórzyć ten format dla pięciu pytań, których raw-only retrieval nie znalazł
w top-10. Tam spodziewamy się statusu `supported` albo `unknown`, co sprawdzi
czy kontrakt prawidłowo obsługuje odmowę zamiast wymyślonego cytowania.
