---
flag: phase2b_result
since: 2026-10-05
owner: mateusz
agent: droid
model: cx/gpt-5.6-luna-low
origin: closure of the Phase 2b workstream (ses_ef8db8f8 + Krok-0 probe); supersedes flags phase2b_autonomy_check + phase2b_goose_gemini_diagnosis
---

`phase2b_result` — 2026-10-05: **Phase 2b (Goose × graf-MCP) zamknięta jako
wynik negatywno-infrastrukturalny.** Twierdzenia dwóch składowych flag
(`phase2b_autonomy_check`, `phase2b_goose_gemini_diagnosis`) zostały tu
przejęte, a flagi wycofane (kontrakt 03.10: flaga, której twierdzenie
przestało trzymać, jest usuwana; stan, nie dziennik).

Ustalenia (sesja 2b `ses_ef8db8f8` + Krok-0):

- **H2-MCP („Goose sam sięga po graf przez narzędzie MCP") jest
  nietestowalna w obecnej konfiguracji** — dwa zweryfikowane niezależnie
  bloki: (1) rozszerzenie z `config.yaml` nie ładuje się w
  `goose run --no-session` (probe "list tools" bez flagi daje zero
  `graph_*`; ten sam probe z `--with-extension` pokazuje
  `graph_query_graph|graph_route_tags` — wpis w config jest inert);
  (2) ścieżka `--with-extension` wiesza się na realnych zadaniach
  (3 runy, 240–300 s, zero outputu poza bannerem; trywialny prompt
  kończy się w sekundach — deadlock/wybuch kosztu przy MCP-stdio, nie
  wolny model).
- **Ostatnia autonomia idzie kanałem shell, nie MCP**: jedyny ukończony
  run autonomii zrobił 0 wywołań narzędzi MCP (narzędzia niezaładowane),
  28 wywołań `shell` — w tym bezpośrednie
  `ask.py "citation concentration" --expand` — i odpowiedź ugruntowana w
  treści grafu (HippoRAG+PPR, critic gate). To **udokumentowany wynik**:
  leczenie „MCP autonomy" nie jest dowożalne tą ścieżką, obserwowalna
  autonomia idzie przez shell.
- **Kroki 5–7 (harness 9×2 runów) zostały anulowane przez samą sesję 2b**
  („projektuj kryterium, nie odpalaj harnessu") — budżet poszedł w
  proby, nie w harness.
- **Znany bug Goose+Gemini (puste odpowiedzi po tool callu) NIE
  reprodukuje się** na `gemini/gemini-flash-lite-latest` przez omniroute
  (`localhost:20128`, goose 1.53.0): Krok-0 dał `toolRequest` → `shell` →
  `PROBE_OK` i niepustą odpowiedź po tool callu. Tool calling działa.

Artefakt: `scripts/graph_mcp.py` (FastMCP wrapper: `query_graph` +
`route_tags` nad `knowledge/graph/ask.py` i `pipeline/06_reflect/route.py`)
**commitnięty do ARL** (`14e254d`) wraz z cofnięciem tymczasowej
deklaracji option-c w `.gitignore` (`7b951a9`). Wrapper jest sprawny
(parse OK, dwa narzędzia) — zostaje w historii repo jako reużywalny
artefakt dla przyszłego klienta MCP, gdy Goose kiedyś naprawi ładowanie
MCP. `MAP.md` odświeżony (`75222ca`, 464 moduły; stale-WARN root gate
czyta) — ARL czyste.

Next (właściciel): jeśli test autonomii ma być kontynuowany, otwiera się
**nowy** workstream (np. `phase2c`: shell-injection jako kanał autonomii,
jak w Phase 2) — 2b testowała H2-MCP i jest domknięta, nie wznawiać.
