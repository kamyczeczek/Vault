# Oh My Pi (omp) — Workspace Agent Specification

Specyfikacja konfiguracji agenta **Oh My Pi (omp)** dla repozytorium `Vault`.

## 1. Środowisko i lokalizacja plików

- **Globalny profil użytkownika:** `%USERPROFILE%\.omp\agent\`
- **Lokalna konfiguracja w repozytorium:** `.omp/`
  - `.omp/config.yml` — projektowe parametry zachowania agenta, pamięć i auto-compaction (śledzony w git).
  - `.omp/mcp.json` — rejestr serwerów MCP; polecenia używają PATH (śledzony w git).
  - `.omp/agents/*.md` — role agentów i uprawnienia bez przypisania modelu (śledzony w git).
  - `.omp/models.yml` — dostawcy modeli z prywatnymi kluczami API (**ignorowany w git** przez `.gitignore`).
  - `.omp/models.example.yml` — szablon dostawców modeli bez sekretów (śledzony w git).

---

## 2. Serwery MCP (Model Context Protocol)

Zdefiniowane w `.omp/mcp.json`:

1. **`jcodemunch`**:
   - Wywołanie: `jcodemunch-mcp` z PATH (tryb `stdio`); dostępność zależy od lokalnej instalacji.
   - Przeznaczenie: Precyzyjna analiza symboli, graf wywołań, blast radius, detekcja martwego kodu i bezpieczne refaktoryzacje bez wczytywania całych plików źródłowych.

2. **`jdocmunch`**:
   - Wywołanie: `uvx jdocmunch-mcp` (tryb `stdio`).
   - Przeznaczenie: Przeszukiwanie dokumentacji, sprawdzanie linków i nawigacja po sekcjach.

---
## 3. Rozszerzenia i wtyczki (Plugins / Marketplaces)

Agent korzysta z marketplace `omp-cli-tools` (`dathtd119/omp-cli-tools`), gdy lokalnie zainstalowany.

---

## 4. Pamięć długoterminowa (Memory Backend)

- **Backend:** `Mnemopi`
- **Scoping:** `per-project`
- **Mechanizm:** `autoRecall: true`, `autoRetain: true`; istniejąca globalna baza pozostaje na miejscu, a rollback polega na przywróceniu `scoping: global`.
- **Embeddingi:** Model lokalny ONNX (`fast-bge-base-en-v1.5`).

---

## 5. Role agentów i dynamiczny model sesji

Podagent bez pola `model` dziedziczy `activeModelPattern` aktualnej sesji OMP. Dotyczy to researcher, implementer, reviewer, tester i scout, także przy dozwolonej rekurencji. Role definiują odpowiedzialność i narzędzia, nie dostawcę modelu.

| Agent | Uprawnienia | Delegowanie |
|---|---|---|
| researcher | read-only | brak |
| implementer | edycja i testy | brak |
| reviewer | read-only | tester, scout |
| tester | uruchamianie testów, bez edycji | brak |
| scout | read-only | brak |

### Budżety myślenia
- Minimal: 512 tokenów
- Low: 1024 tokeny
- Medium: 4096 tokenów
- `defaultThinkingLevel: auto`; `task.maxEffort` nie jest ustawiony projektowo, więc pozostaje domyślne `max` OMP.

### Zarządzanie kontekstem
- Próg: `thresholdPercent: 75`, skalowany względem okna modelu; brak sztywnego `thresholdTokens`.
- Kolejność: `shake` → `remote` → `soft` → `snapcompact`. `remote` i `snapcompact` są opcjonalne; OMP przechodzi dalej, gdy metoda nie jest dostępna.

### Delegowanie
- `task.maxRecursionDepth` pozostaje domyślnie `2`.
- `spawns: "none"` blokuje dalsze delegowanie; jawna lista ogranicza agentów, których worker może uruchomić.
