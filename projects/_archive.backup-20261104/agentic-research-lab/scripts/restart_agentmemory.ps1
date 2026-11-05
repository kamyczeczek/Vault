# restart_agentmemory.ps1 — stop + respawn the agentmemory engine (detached).
#
# Usage:
#   powershell -File scripts/restart_agentmemory.ps1
#   powershell -File scripts/restart_agentmemory.ps1 -Elevated   # UAC for the kill step
#
# Context (scar 2026-09-30): the engine tree may run elevated (session 12),
# in which case a plain taskkill gets "Access denied". -Elevated routes the
# kill through Start-Process -Verb RunAs. The respawn is always non-elevated
# and detached, so after the first -Elevated restart the tree is owned by the
# invoking context and plain restarts work again.
param([switch]$Elevated)

$ErrorActionPreference = "Continue"

# 1) locate the cli.mjs in the npx cache (newest package version wins)
$candidates = Get-ChildItem "$env:LOCALAPPDATA\npm-cache\_npx" -Recurse `
    -Filter "cli.mjs" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match [regex]::Escape("\@agentmemory\agentmemory\dist\cli.mjs") }
if (-not $candidates) {
    Write-Error "no @agentmemory/agentmemory cli.mjs found under $env:LOCALAPPDATA\npm-cache\_npx (run: npx -y @agentmemory/agentmemory)"
    exit 1
}
$cli = ($candidates | Sort-Object Parent.Parent.FullName -Descending | Select-Object -First 1).FullName
Write-Output "cli: $cli"

# 2) find the current :3111 listener (engine) and any node cli launchers
$enginePid = (Get-NetTCPConnection -LocalPort 3111 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique)
$launchers = @(Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "agentmemory.*cli\.mjs" -and $_.CommandLine -notmatch "taskkill" })
$launcherPids = @($launchers | Select-Object -ExpandProperty ProcessId)
Write-Output ("engine pid: " + ($enginePid -join ", "))
Write-Output ("launcher pids: " + ($launcherPids -join ", "))

# 3) kill the tree (engine children die with it; kill launchers too)
$toKill = @($enginePid + $launcherPids | Where-Object { $_ })
if ($toKill.Count -gt 0) {
    if ($Elevated) {
        foreach ($p in $toKill) {
            Start-Process -FilePath "taskkill" -ArgumentList ("/F /T /PID $p") -Verb RunAs -Wait
        }
        Write-Output "killed via UAC"
    } else {
        foreach ($p in $toKill) { taskkill /F /T /PID $p 2>&1 | Out-Null }
        Write-Output "killed (non-elevated)"
    }
    Start-Sleep -Seconds 2
    $alive = @($toKill | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
    if ($alive.Count) {
        Write-Error ("still alive: " + ($alive -join ", ") + " - retry with -Elevated")
        exit 1
    }
}
$portDown = $true
for ($i = 0; $i -lt 10 -and -not $portDown; $i++) {
    Start-Sleep -Seconds 1
    $portDown = -not (Get-NetTCPConnection -LocalPort 3111 -State Listen -ErrorAction SilentlyContinue)
}
if (-not $portDown) { Write-Error ":3111 still held after kill"; exit 1 }
Write-Output "port :3111 free"

# 4) detached respawn (reads ~/.agentmemory/.env at boot)
$p = Start-Process -FilePath "node" -ArgumentList "`"$cli`"" -WindowStyle Hidden `
    -RedirectStandardOutput "$env:USERPROFILE\.agentmemory\boot.log" `
    -RedirectStandardError  "$env:USERPROFILE\.agentmemory\boot.err.log" -PassThru
Write-Output ("new launcher pid: " + $p.Id)

# 5) wait for the engine
$up = $false
for ($i = 0; $i -lt 25; $i++) {
    Start-Sleep -Seconds 1
    if (Get-NetTCPConnection -LocalPort 3111 -State Listen -ErrorAction SilentlyContinue) { $up = $true; break }
}
if (-not $up) { Write-Error "engine did not come up on :3111 within 25s (see boot.log/boot.err.log)"; exit 1 }
$newEngine = (Get-NetTCPConnection -LocalPort 3111 -State Listen | Select-Object -First 1).OwningProcess
Write-Output ("engine up on :3111 (pid $newEngine). Verify: agentmemory status  (expect Provider: llm, Circuit: closed)")
