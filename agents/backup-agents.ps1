# backup-agents.ps1
# Backup konfiguracji i sekretów agentów AI.
# Dane sesji (opencode.db, hermes/state.db, jcode/sessions) są pomijane — za duże.
#
# Użycie:
#   powershell -NoProfile -ExecutionPolicy Bypass -File agents\backup-agents.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File agents\backup-agents.ps1 -BackupRoot D:\secure-backup\agents
#
param(
    [string]$BackupRoot = "$PSScriptRoot\backup"
)

$date   = Get-Date -Format "yyyy-MM-dd_HHmmss"
$dest   = Join-Path $BackupRoot $date
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# ──────────────────────────────────────────────────────────
# Lista elementów do backupu.
# Każdy wpis: Name (label w backupie), Path (co kopiować), Exclude (opcjonalne wzorce do pominięcia)
# ──────────────────────────────────────────────────────────
$items = @(
    # opencode CLI — plik jsonc + auth (baza opencode.db pominięta celowo)
    @{ Name = "opencode-cli-config"         ; Path = "$env:USERPROFILE\.config\opencode"                          ; Exclude = @("node_modules","package-lock.json") }
    @{ Name = "opencode-cli-auth"           ; Path = "$env:USERPROFILE\.local\share\opencode\auth.json"           ; Exclude = @() }

    # goose
    @{ Name = "goose-config"                ; Path = "$env:APPDATA\Block\goose\config\config.yaml"                ; Exclude = @() }
    @{ Name = "goose-secrets"               ; Path = "$env:APPDATA\Block\goose\config\secrets.yaml"               ; Exclude = @() }

    # Hermes — HERMES_HOME (żywy config + auth); state.db i sessions pominięte
    @{ Name = "hermes-localappdata-config"  ; Path = "$env:LOCALAPPDATA\hermes\config.yaml"                       ; Exclude = @() }
    @{ Name = "hermes-localappdata-env"     ; Path = "$env:LOCALAPPDATA\hermes\.env"                              ; Exclude = @() }
    @{ Name = "hermes-localappdata-auth"    ; Path = "$env:LOCALAPPDATA\hermes\auth.json"                         ; Exclude = @() }
    @{ Name = "hermes-localappdata-desktop" ; Path = "$env:LOCALAPPDATA\hermes\desktop.json"                      ; Exclude = @() }
    @{ Name = "hermes-localappdata-soul"    ; Path = "$env:LOCALAPPDATA\hermes\SOUL.md"                           ; Exclude = @() }
    @{ Name = "hermes-localappdata-providers"; Path = "$env:LOCALAPPDATA\hermes\providers.json"                   ; Exclude = @() }
    @{ Name = "hermes-localappdata-models"  ; Path = "$env:LOCALAPPDATA\hermes\model-definitions.json"            ; Exclude = @() }
    # Hermes — ~/.hermes (split-brain copy; inny config)
    @{ Name = "hermes-home-config"          ; Path = "$env:USERPROFILE\.hermes\config.yaml"                       ; Exclude = @() }
    @{ Name = "hermes-home-env"             ; Path = "$env:USERPROFILE\.hermes\.env"                              ; Exclude = @() }
    @{ Name = "hermes-home-skills"          ; Path = "$env:USERPROFILE\.hermes\skills"                            ; Exclude = @() }
    @{ Name = "hermes-home-plugins"         ; Path = "$env:USERPROFILE\.hermes\plugins"                           ; Exclude = @() }

    # pi
    @{ Name = "pi-agent-settings"           ; Path = "$env:USERPROFILE\.pi\agent\settings.json"                   ; Exclude = @() }
    @{ Name = "pi-agent-auth"               ; Path = "$env:USERPROFILE\.pi\agent\auth.json"                       ; Exclude = @() }
    @{ Name = "pi-agent-mcp"                ; Path = "$env:USERPROFILE\.pi\agent\mcp.json"                        ; Exclude = @() }

    # antigravity (global config — reguły, pluginy, mcp)
    @{ Name = "agy-global-config"           ; Path = "$env:USERPROFILE\.gemini\config"                            ; Exclude = @() }
    # antigravity appdata — knowledge items, brain (duże — skippuj jeśli chcesz tylko config)
    # @{ Name = "agy-appdata"              ; Path = "$env:USERPROFILE\.gemini\antigravity-ide"                    ; Exclude = @("brain") }

    # jcode — home (config.toml + provider env + prompt-history)
    @{ Name = "jcode-home-config"           ; Path = "$env:USERPROFILE\.jcode\config.toml"                        ; Exclude = @() }
    @{ Name = "jcode-home-mcp"              ; Path = "$env:USERPROFILE\.jcode\mcp.json"                           ; Exclude = @() }
    @{ Name = "jcode-home-servers"          ; Path = "$env:USERPROFILE\.jcode\servers.json"                       ; Exclude = @() }
    @{ Name = "jcode-home-provider-env"     ; Path = "$env:USERPROFILE\.jcode\provider-nara.env"                  ; Exclude = @() }
    @{ Name = "jcode-home-keymap"           ; Path = "$env:USERPROFILE\.jcode\keymap-snapshot.json"               ; Exclude = @() }
    @{ Name = "jcode-home-prompt-history"   ; Path = "$env:USERPROFILE\.jcode\prompt-history.jsonl"               ; Exclude = @() }
    # jcode — appdata (provider API keys — SEKRETY)
    @{ Name = "jcode-appdata-providers"     ; Path = "$env:APPDATA\jcode"                                         ; Exclude = @("live-tests","openai_model_catalog_cache.json") }

    # omniroute — runtime secrets (KRYTYCZNE: bez tego baza nieodczytywalna)
    @{ Name = "omniroute-home-env"           ; Path = "$env:USERPROFILE\.omniroute\.env"                           ; Exclude = @() }
    # omniroute — config instalacji (JWT_SECRET, API_KEY_SECRET, INITIAL_PASSWORD)
    # UWAGA: nadpisywany przez npm update — backupuj PRZED aktualizacją
    @{ Name = "omniroute-install-env"        ; Path = "$env:APPDATA\npm\node_modules\omniroute\.env"               ; Exclude = @() }
    # omniroute storage.sqlite (~120MB) — POMINIĘTY celowo (za duże; backup osobnym skryptem jeśli potrzeba)
    # @{ Name = "omniroute-db"              ; Path = "$env:USERPROFILE\.omniroute\storage.sqlite"                  ; Exclude = @() }

    # 9router — config + secrets (jwt-secret, machine-id, auth, model-catalog)
    @{ Name = "9router-config"               ; Path = "$env:APPDATA\9router"                                       ; Exclude = @("logs","runtime","mitm","headroom","bin","model-catalog-raw.json") }

    # Cursor — settings (zawiera klucze API providerów!) + globalStorage config
    # UWAGA: state.vscdb pomijany (za duże, ~9MB; zawiera sesje Composera)
    @{ Name = "cursor-settings"              ; Path = "$env:APPDATA\Cursor\User\settings.json"                     ; Exclude = @() }
    # @{ Name = "cursor-state-db"           ; Path = "$env:APPDATA\Cursor\User\globalStorage\state.vscdb"         ; Exclude = @() }

    # Droid (Factory AI) — settings + droids (custom agents) + auth
    # sessions\ pominięte (JSONL per workspace, za duże)
    @{ Name = "droid-settings"               ; Path = "$env:USERPROFILE\.factory\settings.json"                    ; Exclude = @() }
    @{ Name = "droid-droids"                 ; Path = "$env:USERPROFILE\.factory\droids"                           ; Exclude = @() }
    @{ Name = "droid-auth"                   ; Path = "$env:USERPROFILE\.factory\auth.v2.keyring"                  ; Exclude = @() }
    # droid sessions (~JSONL) — pominięte celowo (backupuj osobno jeśli potrzeba)
    # @{ Name = "droid-sessions"            ; Path = "$env:USERPROFILE\.factory\sessions"                          ; Exclude = @() }
    # droid plugins
    @{ Name = "droid-plugins-stamp"          ; Path = "$env:USERPROFILE\.factory\plugins\sync_stamp.json"          ; Exclude = @() }

    # DeepSeek Desktop — brak eksportowalnych sekretów (auth w cookies Chromium, sesje w IndexedDB)
    # Backupuj ręcznie przez eksport z aplikacji jeśli potrzeba.

    # Open Interpreter — nie ma własnych plików konfiguracyjnych, więc nie ma czego
    # backupować poza launcherem poniżej. Klucz OmniRoute jest już objęty pozycją
    # omniroute-home-env (OMNIROUTE_API_KEY w env użytkownika).
    @{ Name = "open-interpreter-launcher" ; Path = "$PSScriptRoot\oi-omniroute.cmd"          ; Exclude = @() }
    # POMINIĘTE celowo: %APPDATA%\uv\tools\open-interpreter\ (venv, odtwarzalny przez
    # `uv tool install open-interpreter --with "setuptools<81"` — patrz REGISTRY.md)
)

# ──────────────────────────────────────────────────────────
# Kopiowanie
# ──────────────────────────────────────────────────────────
$ok   = 0
$skip = 0
$warn = 0

foreach ($item in $items) {
    if (-not (Test-Path $item.Path)) {
        Write-Host "[SKIP] $($item.Name.PadRight(36)) ← nie istnieje: $($item.Path)"
        $skip++
        continue
    }

    $target = Join-Path $dest $item.Name

    try {
        if ($item.Exclude.Count -gt 0) {
            # Kopiowanie z wykluczeniami (tylko dla katalogów)
            Copy-Item -Path $item.Path -Destination $target -Recurse -Force
            foreach ($ex in $item.Exclude) {
                $exPath = Join-Path $target $ex
                if (Test-Path $exPath) { Remove-Item -Recurse -Force $exPath }
            }
        } else {
            Copy-Item -Path $item.Path -Destination $target -Recurse -Force
        }
        Write-Host "[OK  ] $($item.Name.PadRight(36)) ← $($item.Path)"
        $ok++
    } catch {
        Write-Host "[ERR ] $($item.Name.PadRight(36)) ← $($_.Exception.Message)"
        $warn++
    }
}

# ──────────────────────────────────────────────────────────
# ZIP
# ──────────────────────────────────────────────────────────
$zip = "$dest.zip"
Write-Host ""
Write-Host "Pakowanie do ZIP..."
Compress-Archive -Path "$dest\*" -DestinationPath $zip -Force
Remove-Item -Recurse -Force $dest

$sizeMB = [math]::Round((Get-Item $zip).Length / 1MB, 2)
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Backup: $zip"
Write-Host "OK: $ok  SKIP: $skip  WARN: $warn  Rozmiar: $sizeMB MB"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "[!] ZIP zawiera sekrety (auth.json, .env, provider-*.env, cursor settings.json, droid auth)."
Write-Host "    Trzymaj go poza repo, na zaszyfrowanym dysku lub w password managerze."
