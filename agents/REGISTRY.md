---
type: Concept
title: REGISTRY
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Rejestr konfiguracji agentów AI

Ostatnia weryfikacja: **2026-10-04** · Maszyna: `Mateusz-PC` (Windows 11)
Weryfikacja: `probe_paths.ps1` (wszystkie ścieżki potwierdzone `Test-Path`)

Folder z backupem i skryptami przeniesiony: `C:\Agents` → `<workspace>\agents\`

---

## Tabela

| Agent | Config | Dane / sesje | Sekrety | Backup | Uwagi |
|---|---|---|---|---|---|
| **opencode CLI** | `%USERPROFILE%\.config\opencode\opencode.jsonc` | `%USERPROFILE%\.local\share\opencode\opencode.db` | `%USERPROFILE%\.local\share\opencode\auth.json` | ✔ | Plik to `.jsonc`, **nie** `.json`; brak wersji Desktop |
| **goose** | `%APPDATA%\Block\goose\config\config.yaml` | ten sam katalog | `%APPDATA%\Block\goose\config\secrets.yaml` | ✔ | Desktop i CLI dzielą ten sam plik; 4 providerów: omniroute, nara, 9router, google-ai-studio |
| **cline (aplikacja/CLI)** | `%USERPROFILE%\.cline\data\globalState.json` + `settings\providers.json` | `%USERPROFILE%\.cline\data\sessions\*\*.messages.json` (+ `*.json` meta, `db\sessions.db`) | `%USERPROFILE%\.cline\data\secrets.json` (`openAiApiKey`) + klucz w `settings\providers.json` | ✔ | Aplikacja `Local\Cline\cline-app.exe` + CLI (`npm i -g cline`); provider `openai-compatible` = aktywny provider goose (nara). Mapa: `agents\cline-providers.md`. Sesje w `scripts/agent_sessions.py` jako agent `cline`. Instalacja (`Local\Cline\bin\`, `icons\`) — nie backupować, odtwarzalna. |
| **Hermes (HERMES_HOME)** | `%LOCALAPPDATA%\hermes\config.yaml` | `%LOCALAPPDATA%\hermes\state.db` + `sessions\` | `%LOCALAPPDATA%\hermes\.env` + `auth.json` | ✔ | `HERMES_HOME` ustawiony na ten katalog — to **żywa** konfiguracja |
| **Hermes (~\.hermes)** | `%USERPROFILE%\.hermes\config.yaml` | — | `%USERPROFILE%\.hermes\.env` | ⚠ | Drugi config (split-brain); brak auth.json tutaj; backupuj osobno |
| **pi** | `%USERPROFILE%\.pi\agent\settings.json` | `%USERPROFILE%\.pi\agent\` (sesje) | `%USERPROFILE%\.pi\agent\auth.json` + `mcp.json` | ✔ | `PI_CODING_AGENT_DIR` przenosi całość |
| **antigravity (global)** | `%USERPROFILE%\.gemini\config\config.json` | `%USERPROFILE%\.gemini\antigravity-ide\` | `%USERPROFILE%\.gemini\config\mcp_config.json` | ✔ | Zawiera pluginy (`plugins\`) i sidecars |
| **antigravity (workspace)** | `<workspace>\.agents\` | — | — | ✔ | Reguły, pluginy i hooki na poziomie projektu; przywracane z repo |
| **jcode (home)** | `%USERPROFILE%\.jcode\config.toml` | `%USERPROFILE%\.jcode\sessions\` | `%USERPROFILE%\.jcode\provider-nara.env` | ✔ | Główny config + sesje + prompt-history |
| **jcode (appdata)** | `%APPDATA%\jcode\` | — | `%APPDATA%\jcode\provider-*.env` | ✔ | Provider API keys (`provider-google-ai-studio-api.env` itd.) |
| **jcode (localappdata)** | `%LOCALAPPDATA%\jcode\` | — | — | — | Binaria, buildy — nie backupować |
| **omniroute** | `%APPDATA%\npm\node_modules\omniroute\.env` | `%USERPROFILE%\.omniroute\storage.sqlite` | `%USERPROFILE%\.omniroute\.env` (STORAGE_ENCRYPTION_KEY) + `.env` instalacji (JWT_SECRET, API_KEY_SECRET) | ✔ | AI gateway; dane w SQLite (~120MB); `OMNIROUTE_API_KEY` w ENV |
| **9router** | `%APPDATA%\9router\` | `%APPDATA%\9router\db\` | `%APPDATA%\9router\jwt-secret` + `9ROUTER_API_KEY` w ENV | ✔ | CLI router; model-catalog ~64KB; auth w `%APPDATA%\9router\auth\` |
| **oh-my-pi** | *(nie wykryto)* | — | — | — | Brak plików konfiguracyjnych; pomiń |
| **Cursor** | `%APPDATA%\Cursor\User\settings.json` | `%APPDATA%\Cursor\User\globalStorage\state.vscdb` | `%APPDATA%\Cursor\User\settings.json` (apiKey w pliku) | ✔ | Providerzy: omniroute, nara, 9router, google-ai-studio (analogicznie do goose). Sesje w `globalStorage\state.vscdb` (tabela `composerHeaders` + `cursorDiskKV`). Conversation search index: `conversation-search.db`. |
| **Droid (Factory AI)** | `%USERPROFILE%\.factory\settings.json` | `%USERPROFILE%\.factory\sessions\` | `%USERPROFILE%\.factory\auth.v2.keyring` | ✔ | Factory CLI agent v0.233.0 (`C:\Users\Mateusz\bin\droid.exe`). Sesje w JSONL per workspace. Używa wyłącznie Factory API — brak custom providerów. Droids (custom agents): `%USERPROFILE%\.factory\droids\`. |
| **DeepSeek Desktop (dsh-desktop)** | *(brak pliku config)* | `%APPDATA%\@deepseek-ai\dsh-desktop\` | `%APPDATA%\@deepseek-ai\dsh-desktop\Network\Cookies` | ⚠ | Aplikacja czatowa Electron (dsh-desktop). Auth w cookies / Local Storage — brak eksportowalnego config. Sesje w IndexedDB (nie backupowalne skryptowo). Używa wyłącznie DeepSeek API. |
| **Open Interpreter** | `agents\oi-omniroute.cmd` (launcher) | `~\.local\bin\interpreter.exe` + `uv tool` venv | `OMNIROUTE_API_KEY` (User env) — **wstrzykiwany przez launcher** | ✔ | Patrz sekcja Notatki. Wersja 0.4.3, instalacja `uv tool install` (izolowany venv w `%APPDATA%\uv\tools\`). Zero własnych plików konfiguracyjnych. |

---

## Notatki

### Hermes — split-brain
`HERMES_HOME` ustawiony na `%LOCALAPPDATA%\hermes` — to żywe centrum. `~\.hermes\` istnieje równolegle (inny `config.yaml`, brak `auth.json`). Może to być konfiguracja CLI/WebUI vs instalatora. **Żywy auth jest w `%LOCALAPPDATA%\hermes\auth.json`.**

### opencode — `.jsonc`, nie `.json`
Plik konfiguracyjny to `opencode.jsonc` (z komentarzami). Skrypt `probe_paths.ps1` z oryginalnego poradnika szukał `.json` — u Ciebie **ten test zwróci `False`**, mimo że config istnieje.

### jcode — trzy katalogi
- `~\.jcode\` — config + sesje + historia promptów (backupować)
- `%APPDATA%\jcode\` — konfiguracja providerów z kluczami API (backupować)
- `%LOCALAPPDATA%\jcode\` — binaria / buildy (nie backupować)

### antigravity
- `~\.gemini\config\` — globalne reguły, pluginy nauki, `mcp_config.json`
- `~\.gemini\antigravity-ide\` — dane IDE (brain, KI, projekty)
- `<workspace>\.agents\` — per-repo guardrails i pluginy; trzymane w repo

### omniroute — dwa miejsca konfiguracji

**omniroute** to lokalny serwer AI gateway (`npm i -g omniroute`). Ma **dwa** oddzielne pliki `.env`:

1. **`%APPDATA%\npm\node_modules\omniroute\.env`** — główny config serwera: `JWT_SECRET`, `API_KEY_SECRET`, `INITIAL_PASSWORD`, porty, storage path. To jest config **instalacji** — nadpisywany przez `npm update`.
2. **`%USERPROFILE%\.omniroute\.env`** — runtime secrets: `STORAGE_ENCRYPTION_KEY` (klucz szyfrowania bazy SQLite). **Krytyczne** — bez niego baza jest nieodczytywalna.

**Dane:** `~\.omniroute\storage.sqlite` (~120MB) — cała baza użytkowników, kluczy API i logów. Nie wchodzi do standardowego backupu (za duże). Jeśli chcesz backupować, osobny skrypt.

**Env:** `OMNIROUTE_API_KEY` ustawiony w systemie (klucz do klientów).

### 9router — config w AppData

**9router** to CLI router łączący agentów z 40+ providerami. Config w `%APPDATA%\9router\`:
- `jwt-secret` — 64-bajtowy sekret JWT
- `machine-id` — unikalny ID maszyny
- `model-catalog.json` — lista modeli (~64KB, odtwarzalna)
- `auth\` — dane autoryzacji
- `db\` — baza danych

**Env:** `9ROUTER_API_KEY` ustawiony w systemie.

### forge-guardrails (Twoja integracja w workspace)
- `.forge\policy.yaml` — single source of truth (w repo)
- `.forge\state.json` — runtime state (nie backupować, nie commitować)

### Cursor — providerzy i sesje
- `settings.json` zawiera `cursor.general.aiProviders` z kluczami API — **SEKRETY**; nie commitować.
- Providerzy skonfigurowaniani analogicznie do goose: omniroute, nara, 9router, google-ai-studio.
- Sesje (Composer) w SQLite `state.vscdb` — tabela `composerHeaders` (indeks) + `cursorDiskKV` (treść jako `composer.content.<hash>`).
- Agent sessions browsable przez `scripts/agent_sessions.py browse --agent cursor`.

### Droid (Factory AI) — config i sesje
- `~\.factory\settings.json` — główny config (favorited models, trusted folders).
- `~\.factory\sessions\` — sesje w JSONL per workspace (katalog = zakodowana ścieżka).
- `~\.factory\droids\` — custom "droids" (role-based agents), pliki `.md`.
- `~\.factory\auth.v2.keyring` — auth token (krytyczne).
- **Brak custom providerów** — droid używa wyłącznie Factory API.
- Agent sessions browsable przez `scripts/agent_sessions.py browse --agent droid`.

### DeepSeek Desktop (dsh-desktop) — ograniczenia
- Aplikacja Electron bez eksportowalnego config.
- Auth w cookies przeglądarki Chromium — nie da się skryptowo backupować.
- Sesje w IndexedDB (`%APPDATA%\@deepseek-ai\dsh-desktop\IndexedDB\`) — format binarny LevelDB.
- **Nie dodawany do przeglądania sesji** — brak API do odczytu.

### Open Interpreter — własnego configa nie ma, config jest w launcherze

**Instalacja:** `uv tool install open-interpreter --with "setuptools<81"`
Venv: `%APPDATA%\uv\tools\open-interpreter\`, binaria `~\.local\bin\` (`i`, `interpreter`, `interpreter-classic`, `wtf`).

**Wymagania, o których łatwo zapomnieć**
- **`setuptools<81` jest obowiązkowy.** OI 0.4.3 importuje `pkg_resources`, który w `setuptools>=81` już nie ma. Bez tego `interpreter` pada na starcie: `ModuleNotFoundError: No module named 'pkg_resources'`. Po naprawie zostaje ostrzeżenie `pkg_resources is deprecated` na stderr — nieszkodliwe.
- **Nie używaj `pip install`** — `pip` na PATH należy do venv Hermesa. Tylko `uv tool install`.
- **Nie ma pliku konfiguracji.** `api_base`/`api_key` idą wyłącznie przez flagi (`-ab`, `-ak`) albo env.Dlatego konfiguracja mieszka w launcherze, nie w pliku.

**Launcher `agents\oi-omniroute.cmd`** — jedyny sposób, w jaki ten agent łączy się z OmniRoute.
Czemu nie przez zmienne środowiskowe: **`OPENAI_API_KEY` jest już zajęty** w env użytkownika przez inne narzędzie (inny klucz `sk-…`, 35 znaków). Nadpisanie zepsułoby tamto narzędzie, a samo ustawienie `OPENAI_API_BASE` globalnie sprawiłoby, że każde wywołanie gołego `interpreter` wysyłałoby tamten obcy klucz do OmniRoute → 401. Launcher więc ustawia `OPENAI_API_BASE` i wstrzykuje `OPENAI_API_KEY` **tylko do procesu potoka**, czytając klucz z istniejącego `OMNIROUTE_API_KEY`. Nic globalnie nie zmienia.

```powershell
agents\oi-omniroute.cmd                                        # interaktywnie, kod leci bez pytania
"prompt" | agents\oi-omniroute.cmd -s                          # jednorazowo
agents\oi-omniroute.cmd -s -safe ask                           # przywróć pytanie o zgodę (argparse bierze ostatnią)
```

**`-safe off -y` są w launcherze na stałe** — agent nie pyta o zgodę na kod. Świadoma decyzja: wygenerowany kod uruchamia się natychmiast w Twoim koncie. Do doraźnych skryptów na własnej maszynie OK; nie używaj tam, gdzie model z zewnątrz może podsunąć destrukcyjny kod. Sama flaga `-y` nie wystarczała — domyślny `safe_mode=ask` blokuje niezależnie, a w trybie `-s` pytania i tak nikt nie obsługuje.

**Endpoint:** `http://localhost:20128/v1` (OmniRoute, OpenAI-compatible).
**Model domyślny:** `openai/cx/gpt-5.6-luna-low`

**Prefiks `openai/` jest obowiązkowy.** litellm parsuje model jako `<provider>/<model>` i zna własną listę providerów. `cx` nie jest na niej, więc `cx/gpt-5.6-luna-low` daje `BadRequestError: LLM Provider NOT provided` — **zanim** cokolwiek wyjdzie do sieci. Prefiks `openai/` znaczy „OpenAI-compatible" (czyli OmniRoute), a litellm obcina go i wysyła `cx/gpt-5.6-luna-low` jako model id. Dlatego `gemini/gemma-4-26b-a4b-it` działał bez prefiksu — `gemini` jest providerem litellm.

**`--llm_supports_functions` jest obowiązkowy — inaczej agent kłamie.** OI 0.4.3 samo dobiera tryb pracy z modelem (wywołania funkcji vs parsowanie bloków kodu). Przy tym modelu wybiera źle: kod się **nie wykonuje**, a model **fabrykuje wynik** i powtarza go w pętli. Zaobserwowane kolejno `CORES: 8`, potem `16`, potem `32` przy prawdziwym 12. Z flagą działa poprawnie. To najgorsza możliwa klasa awarii — ciche, wiarygodnie wyglądające kłamstwo zamiast błędu. Po znalezieniu potwierdzone testem nieodgadywalnym: model poprawnie zwrócił `31` (= `len(str(2**100))`) i `C:\Users\Mateusz\Desktop\root_worksapce` (rzeczywisty cwd).

**Pułapki przy uruchamianiu nieinteraktywnym**
- `-s/--stdin` to tryb jednorazowy. **Nie ma `--message`.**
- `-cw` ustaw jawnie — OI nie zna okna kontekstowego i cicho ciąży do 8000.
- kod wykonuje się bez pytania (`-safe off -y` w launcherze) — patrz sekcja launchera wyżej.

**Wybór modelu: pinuj, nie ufaj routerowi.** `auto/fast` (własny router OmniRoute) bywa zawodny — raz odpowiedział, raz zawiesił się na 15 min. `oc/deepseek-v4-flash-free` i `openrouter/google/gemma-4-26b-a4b-it:free` nie odpowiedziały w 120 s. Zwykły kontakt `openrouter/anthropic/claude-haiku-4.5` zwraca **402 Insufficient credits** (konto openrouter bez kredytów).

**Rodzina modeli `cx/` na tym omniroute** (2066 modeli w katalogu): trzy tiery × pięć poziomów wysiłku —
`cx/gpt-5.6-{luna,terra,sol}-{low,medium,high,xhigh,max}`. Istnieje też lustrzane `codex/gpt-5.6-*` z tymi samymi nazwami.

**Zweryfikowane zadanie diagnostyczne** (2026-10-04, model `openai/cx/gpt-5.6-luna-low`): model wygenerował i wykonał Python raportujący liczbę rdzeni i wolne miejsce na C:. Wynik zgadł się co do wartości z niezależnym odczytem PowerShell — `CORES: 12`, `C_FREE_GB: 1115.62`.

---

## Ścieżki szybkiego kopiowania (PowerShell)

```powershell
$env:USERPROFILE\.config\opencode\opencode.jsonc
$env:USERPROFILE\.local\share\opencode\auth.json
$env:APPDATA\Block\goose\config\config.yaml
$env:APPDATA\Block\goose\config\secrets.yaml
$env:USERPROFILE\.cline\data\globalState.json
$env:USERPROFILE\.cline\data\secrets.json
$env:USERPROFILE\.cline\data\settings\providers.json
$env:USERPROFILE\.cline\data\settings\models.json
$env:LOCALAPPDATA\hermes\config.yaml
$env:LOCALAPPDATA\hermes\.env
$env:LOCALAPPDATA\hermes\auth.json
$env:USERPROFILE\.hermes\config.yaml
$env:USERPROFILE\.hermes\.env
$env:USERPROFILE\.pi\agent\settings.json
$env:USERPROFILE\.pi\agent\auth.json
$env:USERPROFILE\.pi\agent\mcp.json
$env:USERPROFILE\.gemini\config\config.json
$env:USERPROFILE\.gemini\config\mcp_config.json
$env:USERPROFILE\.jcode\config.toml
$env:USERPROFILE\.jcode\provider-nara.env
$env:APPDATA\jcode\provider-google-ai-studio-api.env
$env:APPDATA\jcode\provider-nara.env
$env:APPDATA\jcode\provider-omniroute.env
$env:APPDATA\jcode\provider-opencode-zen-api.env
$env:APPDATA\jcode\provider-orcarouter-api.env
$env:APPDATA\jcode\provider-tokenrouter.env
$env:APPDATA\Cursor\User\settings.json
$env:USERPROFILE\.factory\settings.json
$env:USERPROFILE\.factory\auth.v2.keyring
$env:USERPROFILE\.factory\droids
```

### Odrzucone

| Agent | Powód odrzucenia (2026-10-04) |
|---|---|
| **Marvis (腾讯马维斯)** | Asystent OS od Tencentu, v1.60.28.11 — **odinstalowany**. Powody: zamknięty CEF, brak angielskiego UI w natywnych warstwach Qt (`i18n\` zawiera wyłącznie `zh_cn.qm` — angielki nie ma w instalatorze), login wyłącznie WeChat/QQ (konto chińskie), Custom Models tylko przez GUI z kluczami szyfrowanymi poza SQLite (`marvis_seckv\marvis_agent.mskv`, magic `MSKVMSKV`), brak lokalnego API do modeli (port 5151 = knowledgebase, 10123 = MarvisHost z 401, 6161 = agent — tokenów w plikach `.ini` nie ma, są same numery portów). Zastąpiony przez Open Interpreter. |
