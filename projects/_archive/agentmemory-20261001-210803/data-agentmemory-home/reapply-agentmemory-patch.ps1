<#
.SYNOPSIS
    Reapplies the patched standalone.mjs for agentmemory MCP server in the npx cache.
#>
$ErrorActionPreference = "Stop"

$BackupPath = "$HOME\.agentmemory\patched-standalone.mjs"
if (-not (Test-Path $BackupPath)) {
    Write-Error "Backup file not found at $BackupPath"
    exit 1
}

$NpxCacheRoot = "$HOME\AppData\Local\npm-cache\_npx"
if (-not (Test-Path $NpxCacheRoot)) {
    Write-Error "NPX cache root not found at $NpxCacheRoot"
    exit 1
}

$TargetFiles = Get-ChildItem -Path $NpxCacheRoot -Recurse -Filter "standalone.mjs" -ErrorAction SilentlyContinue | Where-Object { $_.FullName -like "*agentmemory*" }

if (-not $TargetFiles) {
    Write-Warning "No agentmemory standalone.mjs found under npx cache."
    exit 0
}

foreach ($file in $TargetFiles) {
    Write-Host "Overwriting $($file.FullName) with $BackupPath"
    Copy-Item -Path $BackupPath -Destination $file.FullName -Force
    Write-Host "Successfully patched: $($file.FullName)"
}

Write-Host "Done! Remember to restart pi / MCP client so the new server process loads the patched code."
