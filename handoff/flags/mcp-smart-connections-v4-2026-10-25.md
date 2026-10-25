---
type: Concept
flag: mcp-smart-connections-v4-2026-10-25
since: 2026-10-25
owner: mateusz
agent: codex
model: gpt-5
title: mcp-smart-connections-v4-2026-10-25
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:44Z }
---

MCP `smart-connections` jest enabled w globalnej konfiguracji Codexa i wskazuje
na `C:\Users\Mateusz\Desktop\vault`. Zmieniono serwer z pakietu npm v2,
który oczekuje starego katalogu `.smart-env\multi`, na kompatybilny z
Smart Connections v4 serwer `cusster/smart-connections-mcp` uruchamiany przez
`npx --package=https://github.com/cusster/smart-connections-mcp/archive/refs/heads/main.tar.gz smart-connections-mcp`.
Ustawiono także `SMART_EMBED_MODEL=TaylorAI/bge-micro-v2`, osobny cache npm i
cache modelu. Rejestracja jest poprawna (`codex mcp get`), a tarball uruchamia
się bez błędu `spawn EPERM`; bieżący proces rozmowy nadal nie ma załadowanych
narzędzi Smart Connections. Po ponownym restarcie Codexa trzeba potwierdzić
`index_status` i wykonać wyszukiwanie; pierwszy start wymaga pobrania modelu.
