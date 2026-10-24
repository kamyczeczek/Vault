# Przywracanie konfiguracji agentów AI

Backup z: `<workspace>\agents\backup\<data>.zip`
Rejestr: `REGISTRY.md`

---

## Szybka ścieżka (nowa maszyna, te same ścieżki)

1. Zainstaluj agentów: opencode, goose, Hermes, pi, antigravity, jcode, Cursor, Droid.
2. Uruchom każdego **raz** — żeby utworzył domyślne katalogi.
3. Zamknij wszystkich agentów.
4. Rozpakuj backup:
   ```powershell
   Expand-Archive <workspace>\agents\backup\<data>.zip -DestinationPath C:\temp\restore
   ```
5. Skopiuj pliki wg tabeli poniżej.
6. Uruchom każdego agenta — sprawdź czy widzi klucze API.

---

## Tabela przywracania

| Label w backupie | Docelowa ścieżka |
|---|---|
| `opencode-cli-config\opencode.jsonc` | `%USERPROFILE%\.config\opencode\opencode.jsonc` |
| `opencode-cli-auth` | `%USERPROFILE%\.local\share\opencode\auth.json` |
| `goose-config` | `%APPDATA%\Block\goose\config\config.yaml` |
| `goose-secrets` | `%APPDATA%\Block\goose\config\secrets.yaml` |
| `hermes-localappdata-config` | `%LOCALAPPDATA%\hermes\config.yaml` |
| `hermes-localappdata-env` | `%LOCALAPPDATA%\hermes\.env` |
| `hermes-localappdata-auth` | `%LOCALAPPDATA%\hermes\auth.json` |
| `hermes-localappdata-providers` | `%LOCALAPPDATA%\hermes\providers.json` |
| `hermes-localappdata-models` | `%LOCALAPPDATA%\hermes\model-definitions.json` |
| `hermes-localappdata-soul` | `%LOCALAPPDATA%\hermes\SOUL.md` |
| `hermes-home-config` | `%USERPROFILE%\.hermes\config.yaml` |
| `hermes-home-env` | `%USERPROFILE%\.hermes\.env` |
| `hermes-home-skills\` | `%USERPROFILE%\.hermes\skills\` |
| `hermes-home-plugins\` | `%USERPROFILE%\.hermes\plugins\` |
| `pi-agent-settings` | `%USERPROFILE%\.pi\agent\settings.json` |
| `pi-agent-auth` | `%USERPROFILE%\.pi\agent\auth.json` |
| `pi-agent-mcp` | `%USERPROFILE%\.pi\agent\mcp.json` |
| `agy-global-config\` | `%USERPROFILE%\.gemini\config\` |
| `jcode-home-config` | `%USERPROFILE%\.jcode\config.toml` |
| `jcode-home-mcp` | `%USERPROFILE%\.jcode\mcp.json` |
| `jcode-home-servers` | `%USERPROFILE%\.jcode\servers.json` |
| `jcode-home-provider-env` | `%USERPROFILE%\.jcode\provider-nara.env` |
| `jcode-home-keymap` | `%USERPROFILE%\.jcode\keymap-snapshot.json` |
| `jcode-appdata-providers\` | `%APPDATA%\jcode\` (pliki `provider-*.env`) |
| `omniroute-home-env` | `%USERPROFILE%\.omniroute\.env` (**krytyczne** — klucz szyfrowania SQLite) |
| `omniroute-install-env` | `%APPDATA%\npm\node_modules\omniroute\.env` (po `npm i -g omniroute`) |
| `9router-config\` | `%APPDATA%\9router\` (auth, jwt-secret, model-catalog.json) |
| `cursor-settings` | `%APPDATA%\Cursor\User\settings.json` (**zawiera klucze API!**) |
| `droid-settings` | `%USERPROFILE%\.factory\settings.json` |
| `droid-droids\` | `%USERPROFILE%\.factory\droids\` |
| `droid-auth` | `%USERPROFILE%\.factory\auth.v2.keyring` |
| `open-interpreter-launcher` | `<workspace>\agents\oi-omniroute.cmd` |

---

## Uwagi po przywróceniu

- **omniroute** — przywracać w kolejności:
  1. Zainstaluj: `npm i -g omniroute`
  2. Skopiuj `omniroute-install-env` → `%APPDATA%\npm\node_modules\omniroute\.env`
  3. Skopiuj `omniroute-home-env` → `%USERPROFILE%\.omniroute\.env` (**obowiązkowo przed startem serwera**)
  4. Baza SQLite (`storage.sqlite`) — jeśli masz backup osobny, wgraj przed startem; jeśli nie, serwer zbuduje nową.
- **9router** — po przywróceniu `%APPDATA%\9router\` uruchom `9router` i sprawdź czy auth działa. Jeśli nie, zrób re-login.
- **Hermes** — po przywróceniu ustaw lub zweryfikuj `HERMES_HOME`:
  ```powershell
  [System.Environment]::SetEnvironmentVariable("HERMES_HOME","$env:LOCALAPPDATA\hermes","User")
  ```
- **opencode** — config to `opencode.jsonc`, nie `opencode.json`. Nie zmieniaj rozszerzenia.
- **jcode** — `provider-*.env` w `%APPDATA%\jcode\` zawierają klucze API różnych providerów; po przywróceniu sprawdź każdy.
- **antigravity** — workspace-level `<workspace>\.agents\` przywracasz razem z repo (jest w git).
- **Cursor** — `settings.json` zawiera `cursor.general.aiProviders` z kluczami API. **Po przywróceniu:** zrestartuj Cursor, otwórz Settings → Models i sprawdź czy providerzy są widoczni. Jeśli omniroute/9router działają lokalnie, najpierw uruchom ich serwery.
- **Droid** — po przywróceniu `auth.v2.keyring` uruchom `droid doctor` i sprawdź auth. Jeśli token wygasł, zaloguj się ponownie przez `droid` (otworzy browser).
- **DeepSeek Desktop** — brak eksportowalnego backup; zaloguj się ponownie po reinstalacji.
- **Open Interpreter** — kolejność:
  1. Zainstaluj `uv` (albo użyj istniejącego).
  2. `uv tool install open-interpreter --with "setuptools<81"` — **pin jest obowiązkowy**, bez niego `interpreter` pada na starcie (`ModuleNotFoundError: No module named 'pkg_resources'`).
  3. Skopiuj `open-interpreter-launcher` → `<workspace>\agents\oi-omniroute.cmd`.
  4. Upewnij się, że `OMNIROUTE_API_KEY` jest w env użytkownika — launcher bierze z niego klucz. **Nie ustawiaj `OPENAI_API_KEY`** — jest zajęty przez inne narzędzie, a launcher celowo go nie tyka.
  5. Włącz OmniRoute i sprawdź: `"probe" | agents\oi-omniroute.cmd -s`
  - Venv `%APPDATA%\uv\tools\open-interpreter\` **nie jest backupowany** — odtwarza się krokiem 2.
- **Sekrety** — po przywróceniu sprawdź `.gitignore` w każdym projekcie:
  ```
  auth.json
  .env
  secrets.yaml
  provider-*.env
  settings.json  ← Cursor!
  ```
- **Hermes split-brain** — `~\.hermes\` i `%LOCALAPPDATA%\hermes\` to **dwa oddzielne konfigi**. Przywróć oba jeśli chcesz, ale żywym źródłem prawdy jest `%LOCALAPPDATA%\hermes\` (tam jest `HERMES_HOME`).

---

## Skrypt jednorazowy: przywróć z backupu

```powershell
param([string]$BackupZip)

$restore = "C:\temp\restore_agents"
Expand-Archive $BackupZip -DestinationPath $restore -Force

function cp-item($label, $src, $dst) {
    $from = Join-Path $restore $label
    if (Test-Path $from) {
        New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
        Copy-Item $from $dst -Recurse -Force
        Write-Host "[OK  ] $label -> $dst"
    } else {
        Write-Host "[SKIP] $label (nie ma w backupie)"
    }
}

cp-item "opencode-cli-config\opencode.jsonc"  "$env:USERPROFILE\.config\opencode\opencode.jsonc"
cp-item "opencode-cli-auth"                   "$env:USERPROFILE\.local\share\opencode\auth.json"
cp-item "goose-config"                        "$env:APPDATA\Block\goose\config\config.yaml"
cp-item "goose-secrets"                       "$env:APPDATA\Block\goose\config\secrets.yaml"
cp-item "hermes-localappdata-config"          "$env:LOCALAPPDATA\hermes\config.yaml"
cp-item "hermes-localappdata-env"             "$env:LOCALAPPDATA\hermes\.env"
cp-item "hermes-localappdata-auth"            "$env:LOCALAPPDATA\hermes\auth.json"
cp-item "hermes-home-config"                  "$env:USERPROFILE\.hermes\config.yaml"
cp-item "hermes-home-env"                     "$env:USERPROFILE\.hermes\.env"
cp-item "pi-agent-settings"                   "$env:USERPROFILE\.pi\agent\settings.json"
cp-item "pi-agent-auth"                       "$env:USERPROFILE\.pi\agent\auth.json"
cp-item "pi-agent-mcp"                        "$env:USERPROFILE\.pi\agent\mcp.json"
cp-item "agy-global-config"                   "$env:USERPROFILE\.gemini\config"
cp-item "jcode-home-config"                   "$env:USERPROFILE\.jcode\config.toml"
cp-item "jcode-home-mcp"                      "$env:USERPROFILE\.jcode\mcp.json"
cp-item "jcode-appdata-providers"             "$env:APPDATA\jcode"
cp-item "cursor-settings"                     "$env:APPDATA\Cursor\User\settings.json"
cp-item "droid-settings"                      "$env:USERPROFILE\.factory\settings.json"
cp-item "droid-droids"                        "$env:USERPROFILE\.factory\droids"
cp-item "droid-auth"                          "$env:USERPROFILE\.factory\auth.v2.keyring"
cp-item "open-interpreter-launcher"           "$PSScriptRoot\oi-omniroute.cmd"

Write-Host "Gotowe. Sprawdź HERMES_HOME, klucze API i uruchom droid doctor."
Write-Host "Open Interpreter: uruchom 'uv tool install open-interpreter --with setuptools<81'"
```
