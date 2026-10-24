# Phase 10A — test hipotezy tłumaczenia (PL→EN przed retrievalem)

## Cel
Zmierzyć, co się dzieje, gdy zapytania PL są tłumaczone na EN przed retrievalem.

## Metoda
- Retriever: pilots/graphrag/graphrag.py, wersja z Fazy 8S (bez modyfikacji).
- Baseline: oryginalne zapytania (PL i EN).
- Translated: te same zapytania PL, przetłumaczone PL→EN przez agenta.
- Pomiar w tej samej sesji, ten sam stan kodu.
- Fingerprint korpusu: session 8f manifest (`eval/artifact_manifest.json`)

## Wyniki

### In-corpus PL (13 pytań)
| Metryka | Baseline (PL) | Translated (EN) | Delta |
|---|---|---|---|
| MRR@5 | 0.507 | 0.778 | +0.271 |
| Recall@5 | 0.708 | 0.875 | +0.167 |

### OOC PL (5 pytań)
| Metryka | Baseline (PL) | Translated (EN) | Delta |
|---|---|---|---|
| refusal | 5/5 (100%) | 1/5 (20%) | -4/5 (-80%) |

### Canary (5 pytań)
| Metryka | Baseline (PL) | Translated (EN) | Delta |
|---|---|---|---|
| refusal | 5/5 (100%) | 1/5 (20%) | -4/5 (-80%) |

### In-corpus EN (10 pytań) — kontrola
| Metryka | Baseline (EN) | Kontrola |
|---|---|---|
| MRR@5 | 0.771 | 0.771 |
| Recall@5 | 1.000 | 1.000 |

## Tabela tłumaczeń (pytanie PL → pytanie EN)

| # | Pytanie PL | Pytanie EN |
|---|---|---|
| 1 | Jakie sa metody kompresji sesji agentow? | What are the methods for compressing AI agent sessions? |
| 2 | Czym jest agentic engineering i jak prowadzi od chaosu do świadomego projektowania? | What is agentic engineering and how does it lead from chaos to deliberate design? |
| 3 | Dlaczego ponowne wymyślanie koła w vibe coding jest problemem? | Why is reinventing the wheel in vibe coding a problem? |
| 4 | Jakie są techniki, żeby wycisnąć 2-3x wydajności z AI w kodowaniu? | What are the techniques for squeezing 2-3x efficiency out of AI in coding? |
| 5 | Jak działa routowanie narzędzi oparte na grafie z samonaprawą? | How does graph-based tool routing with self-healing work? |
| 6 | Do czego służy message passing w analizie i odpornym projektowaniu systemów samonaprawczych? | What is message passing used for in the analysis and resilient design of self-healing systems? |
| 7 | Jak działa rozproszona detekcja zmian o odporności bizantyjskiej? | How does distributed change detection with Byzantine fault tolerance work? |
| 8 | Czym charakteryzuje się energetycznie oszczędne uczenie federacyjne z kwantyzacją? | What characterizes energy-efficient federated learning with quantization? |
| 9 | Jak wygląda taksonomia błędów agentów i frameworki debugowania? | What does the taxonomy of agent errors and debugging frameworks look like? |
| 10 | Jak realizowana jest niskonarzutowa odporność na błędy dla kwantowej uniwersalności? | How is low-overhead fault tolerance for quantum universality implemented? |
| 11 | Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)? | What entry did session 04 add to SCARS.md regarding CRLF (scar R13)? |
| 12 | Co powiedzial Jan Kowalski na spotkaniu 2026-09-15? | What did Jan Kowalski say at the meeting on 2026-09-15? |
| 13 | Jaka będzie prognoza pogody w Warszawie jutro o 14:00? | What will be the weather forecast in Warsaw tomorrow at 14:00? |
| 14 | Jaki jest tradycyjny przepis na domowe pierogi ruskie? | What is a traditional recipe for homemade Russian pierogi? |
| 15 | Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia? | What was the score in the last volleyball match Poland - Brazil? |
| 16 | Jaki jest numer telefonu do dzialu HR firmy XYZ? | What is the phone number of the HR department of XYZ company? |
| 17 | Kiedy urodzila sie babcia Krystyna z Sierpca? | When was Krystyna from Sierpc born? |
| 18 | Ile kosztuje bilet miesieczny w komunikacji miejskiej w Atlantis? | How much does a monthly public transport ticket cost in Atlantis? |
| 19 | Jaki jest numer NIP firmy Widmo Sp. z o.o.? | What is the VAT number (NIP) of Widmo Sp. z o.o. company? |
| 20 | Podaj wspolrzedne geograficzne miasta Eldoria. | Give the geographic coordinates of the city of Eldoria. |

## Surowe dane
- Baseline PL: projects/research/knowledge-retrieval/pilots/graphrag/eval/phase10a/phase10a_results.json
- Translated EN: projects/research/knowledge-retrieval/pilots/graphrag/eval/phase10a/phase10a_results.json
- Kontrola EN: projects/research/knowledge-retrieval/pilots/graphrag/eval/phase10a/phase10a_results.json

## Czego ten pomiar NIE rozstrzyga
- Czy tłumaczenie poprawia OOC EN refusal.
- Czy tłumaczenie poprawia in-corpus PL w produkcji.
- Jaki jest koszt latencji tłumaczenia.
