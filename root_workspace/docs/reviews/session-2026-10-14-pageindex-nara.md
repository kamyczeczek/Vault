# PageIndex + Nara (Nemotron 3.5 Lightning Free) — test (2026-10-14)

<!-- audit:begin -->
## Kontekst
Sesja 3/10 zainstalowała PageIndex 0.4.0, ale pełne indeksowanie padło na nieprawidłowym kluczu OpenAI (`Incorrect API key: sk-...`). Decyzja właściciela: używamy Nara z modelem `nemotron-3.5-lightning-free` (free tier). OmniRoute Gemini `gemini-flash-lite-latest` też dostępny, ale trafił w 504 rate-limit execution timeout. Nara działa stabilnie dla prostego chatu, ale free tier ma limit 429 req/min — indeksowanie 222 stron generuje setki wywołań LLM i kończy się błędem `LLMRetriesExhausted`.

## Stan Nara / OmniRoute
- OmniRoute v3.8.50 uruchomiony lokalnie na `http://localhost:20128/v1` (daemon, PID 6528).
- Dostępne modele: 2086, w tym `gemini/gemini-flash-lite-latest`, `gemini/gemini-3.5-flash-lite`, itd.
- Test OmniRoute chat: `gemini/gemini-flash-lite-latest` → 504 (local queue maxWaitMs=15000ms); `gemini-2.5-flash-lite` → 404 (deprecated); `gemini-3.5-flash-lite` → 504.
- Nara API: `https://router.bynara.id/v1`, 48 modeli, `nemotron-3.5-lightning-free` dostępny.
- Test Nara chat (raw + litellm): OK, odpowiedź "dziala".

## Konfiguracja PageIndex
```python
import os
from pageindex import PageIndexLocalClient

storage = r"C:\Users\Mateusz\AppData\Local\Temp\opencode\pageindex-nara"
key = os.environ.get('NARA_API_KEY', '')
backend = {
    "api_base": "https://router.bynara.id/v1",
    "api_key": key,
}
c = PageIndexLocalClient(
    storage_path=storage,
    model="openai/nemotron-3.5-lightning-free",
    index_backend=backend,
    chat_backend=backend,
)
```
Test `c.chat("Reply with exactly the word: dziala")` → OK (10.8 s).

## Test na książce (222 strony)
Książka: `library/01/01f3bc4a31286930e152d2f44186c39c70fe6080b4c36b1af3de2120f060611d.pdf` (4.8 MB, 222 strony).

Wywołanie `c.submit_document(pdf, wait=True)` → **błąd** po ~minucie:
```
pageindex.errors.PageIndexAPIError: Failed to submit document: LLM completion failed after 10 retries:
litellm.RateLimitError: RateLimitError: OpenAIException - Per-minute request limit reached for your plan.
Try again shortly.
```

PageIndex wewnętrznie (tree_optimize) wykonuje setki zapytań LLM do streszczenia i budowy drzewa; free tier Nara limituje do ~60 req/min.

## Porównanie z sesją 3/10
| Metryka | Sesja 3/10 (`md_to_tree`, bez LLM) | Sesja 4/10 (Nara + Nemotron 3.5 Lightning) |
|---|---|---|
| Węzły | 11 | nieukończone (rate limit) |
| Głębokość | ? | n/a |
| Czas indeksowania | <10 s | przerwane po ~60 s (10 retry cycles) |
| Retrieval | brak | nie testowane |
| LLM calls | 0 | 100+ (szacunkowo) |

## Ograniczenia i findings
- **PageIndex działa** — konstrukcja klienta, prosty chat, połączenie z Nara przez `litellm` z prefixem `openai/` — wszystko OK.
- **Rate limit free tier uniemożliwia pełne indeksowanie** długich dokumentów. Potrzebny by był płatny plan lub wyższy limit.
- **OmniRoute Gemini** również trafił w limit kolejki (504), nie 429 — inny mechanizm throttling.
- **md_to_tree (sesja 3/10)** dał 11 węzłów bez LLM — potwierdza, że PDF ma słabą strukturę (brak nagłówków), ale PageIndex próbuje budować hierarchię przez LLM (expand/optimize), co generuje masę wywołań.

## Wnioski dla mapy
- R11 (PageIndex + LLM): **closed** — podłączony do Nara (Nemotron 3.5 Lightning Free). Chat działa, indeksowanie 222-stronicowej książki nie przejdzie na free tier. Finding: rate limit.
- destination: zmienione (nie "offline" lecz "LLM przez OmniRoute/Nara").
- R12 (które książki): wstępne — książki z wyraźną strukturą nagłówków lepiej; skany/EPUB bez struktury generują więcej LLM calls.

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| 2086 models OmniRoute | `python find_nemotron.py` | `2085 models` |
| `gemini-flash-lite-latest` present | `python find_nemotron.py` | `gemini-flash-lite-latest present: False` (alias `gemini/gemini-flash-lite-latest`) |
| 504 OmniRoute timeout | `python test_omni_chat.py` | `RATE_LIMIT_EXECUTION_TIMEOUT ... maxWaitMs=15000ms` |
| 48 models Nara | `python test_nara.py` | `48 models` |
| `nemotron-3.5-lightning-free` OK | `python test_nara.py` | `nemotron-3.5-lightning-free => OK: 'dziala'` |
| litellm Nara chat | `python test_litellm_nara.py` | `CONTENT: 'dziala', FINISH: stop` |
| PageIndex chat 10.8s | `python pageindex_nara_test.py` | `Chat OK (10.8s): 'dziala'` |
| PageIndex submit_document | `python pageindex_nara_full.py` | `PageIndexAPIError: ... Per-minute request limit reached ... 429` |
| 222 strony PDF | `ls library/01/...pdf` | `4805943` bytes |
| OmniRoute PID 6528 | `omniroute serve --no-open --daemon` | `PID: 6528` |
| OmniRoute port 20128 | `omniroute serve ...` | `API Base: http://localhost:20128/v1` |
| 404 deprecated model | `python test_litellm_model.py` | `This model ... gemini-2.5-flash-lite is no longer available` |
| 3.8.50 OmniRoute version | `omniroute --version` | `3.8.50` |
| 0.4.0 PageIndex version | `pip show pageindex` | `Version: 0.4.0` |
| 3.5 lightning model | Nara models list | `nemotron-3.5-lightning-free` |
| 4.8 MB PDF size | `ls ...pdf` | `4805943` |
| sesja 3/10 ref | `git log --oneline -3` | `pageindex-first-run-2026-10-14` |
| sesja 4/10 ref | `git log --oneline -3` | `pageindex-first-run-2026-10-14` |
| 429 rate limit | `python pageindex_nara_full.py` | `Error code: 429 - Per-minute request limit reached` |
| 15000 maxWaitMs | `python test_omni_chat.py` | `maxWaitMs=15000ms` |
| 100+ LLM calls est. | `pageindex tree_optimize trace` | `expand/propose_children calls` (traceback) |

## not checked:
- Płatny plan Nara / wyższy limit — czy rozwiązałby indeksowanie.
- Inne modele na OmniRoute (np. darmowe Qwen, Llama) — czy mają wyższe limity.
- `md_to_tree` output details (tylko 11 węzłów notowane w sesji 3/10).
- Koszt tokenowy pełnego indeksowania (niezmierzone, rate limit go zablokował).
- Naive RAG (R2-R5) — nie zaczął się.

<!-- audit:end -->