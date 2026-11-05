# Oh My Pi (omp) — Workspace Agent Specification

Specyfikacja konfiguracji agenta **Oh My Pi (omp)** dla repozytorium `Vault`.

## 1. Środowisko i lokalizacja plików

- **Globalny profil użytkownika:** `%USERPROFILE%\.omp\agent\`
- **Lokalna konfiguracja w repozytorium:** `.omp/`
  - `.omp/config.yml` — główne parametry zachowania agenta, role modeli, pamięć, auto-compaction (śledzony w git).
  - `.omp/mcp.json` — rejestr serwerów MCP (śledzony w git).
  - `.omp/models.yml` — dostawcy modeli z prywatnymi kluczami API (**ignorowany w git** przez `.gitignore`).
  - `.omp/models.example.yml` — szablon referencyjny dostawców modeli bez sekretów (śledzony w git).

---

## 2. Serwery MCP (Model Context Protocol)

Zdefiniowane w `.omp/mcp.json`:

1. **`jcodemunch`**:
   - Wywołanie: `C:\Users\Mateusz\.local\bin\jcodemunch-mcp.exe` (tryb `stdio`).
   - Przeznaczenie: Precyzyjna analiza symboli, graf wywołań, blast radius, detekcja martwego kodu i bezpieczne refaktoryzacje bez wczytywania całych plików źródłowych.
2. **`jdocmunch`**:
   - Wywołanie: `uvx jdocmunch-mcp` (tryb `stdio`).
   - Przeznaczenie: Przeszukiwanie bazy dokumentacji markdown/rst/pdf, sprawdzanie integralności linków, health radar, ekstrakcja wycinków i nawigacja po strukturze sekcji.

---

## 3. Rozszerzenia i wtyczki (Plugins / Marketplaces)

Agent korzysta z marketplace `omp-cli-tools` (`dathtd119/omp-cli-tools`):

1. **`omp-rtk`** (`v0.1.0`):
   - Automatyczne przepisywanie komend shella przez RTK w celu minimalizacji liczby tokenów w wynikach poleceń CLI.
2. **`omp-witr`** (`v0.1.0`):
   - Inspekcja uruchomionych procesów i portów sieciowych.

---

## 4. Pamięć długoterminowa (Memory Backend)

- **Backend:** `Mnemopi`
- **Scoping:** `global`
- **Mechanizm:** Automatyczne odpytywanie pamięci przed działaniami (`autoRecall: true`) oraz zapisywanie kluczowych faktów po sesji (`autoRetain: true`).
- **Embeddingi:** Model lokalny ONNX (`fast-bge-base-en-v1.5`).

---

## 5. Role modeli i budżety myślenia

Zdefiniowane w `.omp/config.yml`:

| Rola | Model | Zastosowanie |
|---|---|---|
| `default` | `omniroute/agy/gemini-3.8-flash-low:low` | Główny model roboczy sesji |
| `smol` | `omniroute/gemini/gemini-3.5-flash-lite` | Lekkie zapytania, preflight, szybkie klasyfikacje |
| `fast` | `omniroute/gemini/gemini-3.5-flash-lite` | Szybkie operacje narzędziowe |
| `plan` | `google-ai-studio/gemini-3.7-flash` | Planowanie wieloetapowe i dekompozycja |
| `slow` | `omniroute/cx/gpt-5.6-luna-medium` | Głęboka analiza, trudne błędy i falsyfikacje |
| `commit`| `omniroute/gemini/gemini-3.5-flash-lite` | Generowanie wiadomości commitów |

### Budżety myślenia (Thinking Budgets)
- Minimal: 512 tokenów
- Low: 1024 tokeny
- Medium: 4096 tokenów

### Zarządzanie kontekstem (Compaction)
- Próg kompresji (`thresholdTokens`): 160 000 tokenów
- Bufor rezerwowy (`reserveTokens`): 32 000 tokenów
- Kolejność metod: `snapcompact` → `shake` → `remote` → `soft`
