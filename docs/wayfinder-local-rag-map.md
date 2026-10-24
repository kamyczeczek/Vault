# Wayfinder Map: Lokalny RAG na osobistej bibliotece książek (PL+EN)

## Destination

Lokalny RAG na osobistej bibliotece książek (PL+EN), który odpowiada na pytania właściciela w języku polskim z cytatami z książek; działa offline, bez API; baseline — nie system.

**Rozszerzenie (sesja 2/10):** porównanie dwóch metod — naive RAG (chunk + embed + top-k) i PageIndex (vectorless, reasoning-based) — na tej samej bibliotece i tych samych pytaniach.

**Rozstrzygnięcie (sesja 3/10):** budujemy oba systemy — naive vector RAG i PageIndex. Gotowe narzędzia (AnythingLLM, Khoj, GPT4All, Zim Pro) są out of scope. Cel: porównać obie metody na tej samej bibliotece i tych samych pytaniach.

**Korekta destination (sesja 4/10):** LLM przez OmniRoute (lokalny gateway do Gemini `gemini-flash-lite-latest`), nie lokalny model. Reszta stosu (chunking, embeddingi, drzewo PageIndex, storage) pozostaje lokalna. Czysty offline (Ollama) out of scope.

## Notes

- Kontekst KR: 18 sesji, over-engineering, pilot `terminated`. Nie powtarzać.
- Znane gotowe rozwiązania: AnythingLLM, Khoj, GPT4All, Zim Pro (do rozważenia jako alternatywa dla budowania).
- Znane modele embeddingowe wielojęzyczne: PolDense, EuroDense, `bge-m3`.
- Znane lokalne LLM: Ollama, LM Studio, Bielik, PLLuM.
- Sesja 18/10 (walkthrough na 14 pytaniach): cross-lingual tokenizacja to główny problem; naive RAG tego nie rozwiązuje sam z siebie.
- Preferencja właściciela: naive RAG (chunk + embed + top-k + LLM), nie złożony pipeline.
- Ograniczenie: lokalnie, bez API, bez SaaS.
- Decyzja "build vs configure" jest otwarta — nie zakładać z góry, że budujemy.
- Skille do konsultacji: `wayfinder`, `unlazy`.
- Reguła: każda liczba w raporcie ma artefakt tool calla; zero `env`/`printenv`.
- Dowód KR walkthrough: `docs/reviews/session-2026-10-14-retrieval-walkthrough.md` (2 trafione / 1 częściowo / 5 pudeł / 1 odmowa słuszna / 5 odmów błędnych na 14 pytań).
- **PageIndex (VectifyAI):** vectorless, reasoning-based RAG. `pip install -U pageindex` daje tryb lokalny (Python 3.10+, LLM API key, brak vector DB, brak GPU). Buduje hierarchiczne drzewo dokumentu; LLM reasonuje po drzewie. Idealny dla długich, ustrukturyzowanych dokumentów (podręczniki, raporty, dokumentacja techniczna). Słaby dla krótkich dokumentów, skanów (wymaga Cloud OCR) i zapytań keyword/exact-match.
- **Porównanie metod:** naive RAG = similarity search; PageIndex = relevance przez reasoning. Obie mają sens dla różnych typów pytań. Cel: zmierzyć, która lepiej odpowiada na pytania właściciela do książek.
- **Koszt PageIndex:** każde zapytanie = wywołanie LLM (reasoning po drzewie). Indeksowanie = jednorazowy koszt LLM na streszczenia węzłów. Dla lokalnego LLM (Ollama/Bielik) koszt = czas, nie pieniądze.

## Decisions so far

- [Map-created]: mapa utworzona (sesja planistyczna). Destination do potwierdzenia przez właściciela (G0). 10 ticketów otwartych (R1-R10). GATES.md utworzony w `docs/local-rag-GATES.md`.
- [Pageindex-added]: mapa rozszerzona o PageIndex (vectorless RAG) i porównanie z naive RAG. Nowe tickety: R11-R15 (PageIndex local, dopasowanie książek, instalacja, metoda porównania, strategia równoległa vs jedna). Nowe bramki: G7-G12.
- [R1-resolved-build-both]: właściciel rozstrzygnął R1 — budujemy oba systemy (naive vector RAG + PageIndex). Gotowe narzędzia out of scope. Kolejny krok: instalacja PageIndex lokalnie i test na 1-2 książkach.
- [R11-resolved-omniroute]: PageIndex podłączony do Nara (Nemotron 3.5 Lightning Free) przez `litellm` (OpenAI-compatible endpoint). Test chat: OK. Pełne indeksowanie 222-stronicowej książki zablokowane rate-limitami free tier (429 req/min). R11 closed z findingiem.
- [destination-changed-omniroute]: destination zmienione z "offline, bez API" na "LLM przez OmniRoute/Nara". Powód: decyzja właściciela w sesji 4/10.

## Not yet specified

- Konkretna architektura pipeline'u (zależy od R1, R2, R4).
- Sposób integracji z istniejącym workspace (zależy od R8).
- Metryki i próg akceptacji (zależy od R6, R9).
- Liczba i format książek w bibliotece (zależy od R5 — "książki" niepoliczone, formaty PDF/EPUB/MOBI nieznane).
- Czy notatki właściciela (np. Obsidian) też wchodzą do korpusu, czy tylko książki (propozycja: tylko książki; do potwierdzenia w G0).
- Jak porównać wyniki obu metod na pytaniach właściciela (zależy od R14)
- Czy PageIndex ma sens dla książek bez wyraźnej struktury (zależy od R12)
- Czy PageIndex i naive RAG mają dzielić ten sam interfejs (zależy od R7, R15)

## Out of scope

- Reranker (naive RAG go nie potrzebuje; jeśli pomiary wykażą konieczność — nowa mapa).
- Hybryda FTS5+wektory (KR to miał i poległ).
- Family-aware refusal, semantic coverage, proof/trace (KR-specific, nie przenosimy).
- Cross-lingual translation na wejściu (chyba że R2 wykaże, że wielojęzyczny embedding nie wystarcza — wtedy nowa decyzja).
- Fine-tuning modeli.
- Korpus książek poza osobistą biblioteką właściciela.
- PageIndex Cloud (używamy tylko trybu lokalnego)
- PageIndex File System (skalowanie na miliony dokumentów — niepotrzebne dla osobistej biblioteki)
- PageIndex MCP server (chyba że R7 wykaże, że to jest pożądany interfejs)
- Gotowe narzędzia RAG: AnythingLLM, Khoj, GPT4All, Zim Pro (rozstrzygnięte w sesji 3/10: budujemy własne)
- Ollama i lokalne modele LLM (rozstrzygnięte w sesji 4/10: LLM przez OmniRoute / Nara)

---

## Tickets (Child Issues)

| ID | Typ | Pytanie | Blocked by |
|---|---|---|---|
| R1 | research | Build vs configure: czy istniejące narzędzie (AnythingLLM / Khoj / GPT4All / Zim Pro) spełnia destination, czy trzeba budować własne? | closed (sesja 3/10): build both — naive RAG + PageIndex |
| R2 | research | Który model embeddingowy dla PL+EN: PolDense / EuroDense / `bge-m3` / inny? Porównaj na 10 pytaniach właściciela. | R1 |
| R3 | research | Który lokalny LLM (Ollama / LM Studio) i który model (Bielik / Llama / Qwen / inny)? | — |
| R4 | research | Jaki chunking: rozmiar, overlap, po akapitach czy po sekcjach? Co mówi literatura dla książek? | R1 |
| R5 | task | Jakie książki, ile, jakie formaty (PDF/EPUB/MOBI), gdzie żyją? | — |
| R6 | grilling | Czy refusal ("nie wiem" gdy odpowiedzi nie ma) jest wymagany, czy akceptowalne jest odpowiadanie zawsze top-1? | — |
| R7 | grilling | Jaki ma być interfejs: CLI (`python ask.py "pytanie"`), web UI, wtyczka do Obsidian, MCP? | — |
| R8 | research | Gdzie mają żyć dane: root workspace (`projects/`?), osobny repo, `library/`? | — |
| R9 | task | Jak będziemy oceniać: 20 pytań właściciela, jaka metryka (trafienie w top-3? odpowiedź użyteczna? obie)? | R6 |
| R10 | grilling | Jak obsłużyć fakt, że KR poległ na cross-lingual — czy w tym RAG-u tłumaczymy pytania PL→EN, czy używamy wielojęzycznego embeddingu, czy oba? | R2 |
| R11 | research | Czy PageIndex działa lokalnie z Ollama/Bielik (zamiast OpenAI)? Jakie modele są obsługiwane przez `litellm`? | — |
| R12 | research | Które książki z biblioteki nadają się do PageIndex (tekstowe PDF, >50 stron, hierarchia)? Które nie (skany, EPUB bez struktury)? | R5 |
| R13 | task | Jak zainstalować i skonfigurować PageIndex lokalnie (Python SDK + `litellm` + model)? Gdzie ma żyć konfiguracja? | R8 |
| R14 | research | Jak porównać obie metody? Ten sam zestaw pytań, ta sama biblioteka, jakie metryki (trafność odpowiedzi, obecność cytatu, czas, koszt)? | R9 |
| R15 | grilling | Czy chcemy, żeby obie metody działały równolegle (dwa systemy, użytkownik wybiera), czy jedna wygrywa i zastępuje drugą? | R14 |
