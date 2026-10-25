# PageIndex — pierwszy lokalny test (2026-10-14)

<!-- audit:begin -->
## Kontekst
Sesja `3/10` mapy `local-rag`. R1 rozstrzygnięte przez właściciela:
budujemy oba systemy (naive RAG + PageIndex), gotowe narzędzia
(AnythingLLM, Khoj, GPT4All, Zim Pro) out of scope. Ta sesja:
instalacja PageIndex lokalnie i test na jednej książce.

## Instalacja
- `pip install -U pageindex` → sukces, wersja **0.4.0**
  (zależności: `litellm 1.105.0`, `openai 2.54.0`, PyPDF2, pypdfium2).
  Efekt uboczny: resolver pip zgłosił konflikty z `hermes-agent`
  (`cryptography`, `openai==2.24.0`, `python-dotenv`, `rich`) — do odnotowania,
  nie blokuje.
- `import pageindex` → działa (brak `__version__`, wersja z `pip show`).
- Główne API: `PageIndexClient`, `PageIndexLocalClient`,
  `PageIndexCloudClient`, `LocalIndexConfig` / `CloudIndexConfig` /
  `IndexConfig`, `submit_document(file_path, wait)`,
  `submit_query(doc_id, query)`, `get_tree`, `md_to_tree`,
  `optimize_tree`, `local_chat`, `mcp_bridge`.
- Wymaga LLM API key: **TAK** dla pełnego pipeline'u
  (`page_index_flash` woła LLM przez litellm, domyślnie OpenAI).
  litellm wspiera provider `ollama` / `ollama_chat`, więc PageIndex
  może wskazać lokalny model — ale Ollama nie jest zainstalowane.

## Test na książce
- Biblioteka: `library/` — 24 pliki PDF (hashe + tytuły czytelne).
- Książka testowa: `library/01/01f3bc….pdf` — 222 strony,
  tekst ekstrahowalny (PyPDF2, `~2.4k znaków` na 3 stronach próbnych).
- `submit_document(..., wait=True)` (storage w Temp, nie w repo):
  PDF sparsowany, pipeline doszedł do streszczeń LLM i padł:
  `PageIndexAPIError: Failed to submit document:
  litellm.AuthenticationError — Incorrect API key provided:
  sk-6ca52…002e` (klucz w env nieprawidłowy).
- Retrieval na 1 pytaniu: **nie wykonany** — brak drzewa (blokada LLM).
- Bez-LLM kontrola: `md_to_tree` na surowym tekście z PyPDF2
  (`8316` linii) działa lokalnie bez klucza: drzewo `1328` znaków,
  11 płaskich węzłów z jednego listingu kodu (brak nagłówków
  markdown w surowym tekście, więc struktura uboga — zgodnie
  z oczekiwaniami, pełne drzewo daje dopiero pipeline z LLM).

## Ograniczenia zaobserwowane
- Pełny PageIndex lokalnie = dokumenty lokalne + **własny model**.
  Bez Ollama i bez ważnego klucza API nie ma indeksowania ani retrievalu.
- Konflikt zależności pip z `hermes-agent` (`openai 2.54.0` vs `2.24.0`).
- `md_to_tree` jest korutyną (trzeba `asyncio.run`).

## Wnioski dla mapy
- R11 (PageIndex local z Ollama): częściowo — litellm ma provider
  ollama/ollama_chat, więc ścieżka istnieje; blokada: brak Ollama
  i brak ważnego klucza. Następny krok: instalacja Ollama + model.
- R12 (które książki nadają się): wstępnie — tekstowe PDF z
  ekstrahowalnym tekstem (testowa: 222 strony, OK); skany nieznane.
- R13 (instalacja i konfiguracja): instalacja rozstrzygnięta
  (0.4.0 działa); konfiguracja LLM w toku (blokada).

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| Python 3.11.15, pip 26.2.1, Ollama brak, pageindex brak | `python --version; pip --version; ollama --version; pip show pageindex` | `Python 3.11.15`, `ollama: not recognized`, `Package(s) not found: pageindex` |
| pip install sukces, 0.4.0 | `pip install -U pageindex` | `Successfully installed ... pageindex-0.4.0 ... litellm-1.105.0 openai-2.54.0` |
| import działa, API | `python -c "import pageindex; print(dir(pageindex))"` | `['PageIndexClient', 'PageIndexLocalClient', ..., 'submit_document', 'submit_query', 'md_to_tree', ...]` (wersja 0.4.0 z `pip show`) |
| 24 PDF w library/ | `Get-ChildItem library/ -Recurse -Filter *.pdf \| Measure` | `24` |
| książka 222 strony | `PyPDF2.PdfReader` len(pages) | `pages: 222`, próba 2420 znaków / 3 strony |
| blokada LLM | `submit_document(..., wait=True)` | `PageIndexAPIError: ... Incorrect API key provided: sk-6ca52…002e` |
| drzewo bez LLM | `asyncio.run(md_to_tree(book.md))` | `TREE CHARS: 1328`, 11 węzłów, `line_count: 8316` |

## not checked:
- retrieval z cytatem na prawdziwym drzewie (blokada LLM, R11)
- instalacja Ollama i wskazanie `ollama/<model>` przez litellm
- która książka ma najlepszą strukturę do drzewa (R12, pełne)
- koszt indeksowania (liczba wywołań LLM, tokeny) — bez ważnego LLM
- wpływ konfliktu `openai 2.54.0` vs `hermes-agent 2.24.0` na agenta

<!-- audit:end -->
