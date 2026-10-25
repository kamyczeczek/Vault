# Concepts

* [SPEC](SPEC.md)

# Files

* [doctree-mcp](doctree-mcp)
* [benchmark-questions.json](benchmark-questions.json)
* [benchmark-results-20.json](benchmark-results-20.json)

# Untyped

* [knowledge-catalog](knowledge-catalog.md)
* [kosha](kosha.md)
* [llm-wiki](llm-wiki.md)
* [lore](lore.md)
* [napkin](napkin.md)
* [okf-generator](okf-generator.md)
* [okf-rag](okf-rag.md)
* [okforge](okforge.md)
* [ontoship](ontoship.md)
* [open-knowledge-format](open-knowledge-format.md)
* [uplink](uplink.md)

# Reports

* [Synteza OKF-rag — od surowego materiału do użytecznej wiedzy](SYNTHESIS.md) - Roboczy model przekształcania materiałów o organizacji workspace i wiedzy w koncepty, decyzje oraz eksperymenty.
* [Synteza — kompilacja, wyszukiwanie i narzędzia](SYNTHESIS-kompilacja-i-wyszukiwanie.md) - Co naprawdę daje pipeline OKF/llmwiki/okforge oraz które elementy warto odłożyć do czasu potwierdzenia potrzeby.
* [Eksperyment — ręczne i semantyczne wyszukiwanie w OKF-rag](EXPERIMENT-retrieval-2026-10-25.md) - Pierwszy pięciopytaniowy test tego, czy warstwa syntezy i Smart Connections pomagają znaleźć właściwy materiał.
* [Benchmark retrieval — 15 pytań z oczekiwanym źródłem](EXPERIMENT-retrieval-benchmark-2026-10-25.md) - Test rankingu Smart Connections po dodaniu warstwy syntez i decyzji nad surowymi materiałami OKF-rag.
* [Benchmark retrieval — plik i fragment źródłowy](EXPERIMENT-retrieval-benchmark-20-2026-10-25.md) - Dwudziestopytaniowy test Smart Connections po dodaniu precyzyjnych wskazań plików i zakresów źródłowych.
* [Control raw-only — retrieval bez warstwy kuratorskiej](EXPERIMENT-retrieval-raw-only-2026-10-25.md) - Kontrolny ranking tych samych 20 pytań po odfiltrowaniu syntez, decyzji, raportów i indeksu.
* [Kontrola brakujących trafień retrieval](EXPERIMENT-retrieval-misses-2026-10-25.md) - Ręczna kontrola dziesięciu pytań oraz test trzech wariantów zapytania dla pięciu missów.
* [Smoke test kontraktu odpowiedzi retrieval](EXPERIMENT-retrieval-answer-contract-2026-10-25.md) - Pięć pytań sprawdzających przejście od huba semantycznego do źródła, lokalizatora i cytatu.
* [Source slices dla dużych importów](EXPERIMENT-source-slices-2026-10-25.md) - Test małych, pochodnych slice'ów jako warstwy nawigacyjnej retrieval.

# Decisions

* [Minimalny przepływ od materiału do decyzji](DECISION-minimalny-przeplyw-wiedzy.md) - Roboczy sposób zamieniania surowych materiałów w koncepty, syntezy, decyzje i eksperymenty.
* [Kontrakt odpowiedzi retrieval](DECISION-kontrakt-odpowiedzi-retrieval.md) - Minimalny format łączący tezę z dowodem, cytatem i poziomem pewności.

# Generated source slices

* [Manifest](_slices/okf-rag/manifest.json) - Hash źródła, zakresy linii i lista wygenerowanych slice'ów.
* [Proposal to truth](_slices/okf-rag/okf-rag--proposal-to-truth.md) - Granica między propozycją kompilatora a opublikowaną prawdą.
* [Persistent pipeline state](_slices/okf-rag/okf-rag--pipeline-state.md) - Podział trwałego stanu pipeline'u.
* [End-to-end knowledge flow](_slices/okf-rag/okf-rag--end-to-end-flow.md) - Przepływ od raw Markdown do hybrid recall.
* [Benchmark metrics](_slices/okf-rag/okf-rag--benchmark-metrics.md) - Recall/Hit@K, MRR i latencja.
* [Extraction findings](_slices/okf-rag/okf-rag--extraction-findings.md) - Niedeterministyczna ekstrakcja i niepełne pruning.

# Napkin source slices

* [Manifest](_slices/napkin/manifest.json) - Hash źródła, zakresy linii i lista trzech wygenerowanych slice'ów.
* [Distill — Conversation to Vault](_slices/napkin/napkin--distill-conversation-to-vault.md) - Gate, ekstrakcja, grupowanie tematów oraz merge lub create.
* [Tend — Vault Upkeep](_slices/napkin/napkin--tend-vault-upkeep.md) - Inspekcja, bezpieczne priorytety i porządkowanie vaulta.
* [Agent Memory System — Progressive Disclosure](_slices/napkin/napkin--agent-memory-progressive-disclosure.md) - Cztery poziomy ujawniania kontekstu agentowi.

# Okforge source slices

* [Manifest](_slices/okforge/manifest.json) - Hash źródła, zakresy linii i dwa wygenerowane slice'y.
* [Initialize a Knowledge Base](_slices/okforge/okforge--initialize-knowledge-base.md) - Inicjalizacja bazy i pipeline dodawania dokumentu.
* [Recompile](_slices/okforge/okforge--recompile.md) - Ponowne generowanie oraz ostrzeżenie o nadpisaniu ręcznych edycji.

# Subdirectories

* [_slices](_slices/index.md)
* [source-slices](source-slices/index.md)
