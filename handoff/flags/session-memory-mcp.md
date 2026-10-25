---
type: Concept
flag: session-memory-mcp
since: 2026-10-07
owner: mateusz
agent: deepseek-harness
model: muse-spark-1.3-contributor-free
origin: memory-usability-test + Poziom 0 plan (MCP server)
title: session-memory-mcp
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

`session-memory-mcp` — 2026-10-07: MCP server `scripts/memory_mcp.py` (stdio, 2025-06-18 po bump z 2024-11-05, stdlib only) owija `memory_index.query_memory/open_db/log_usage`: 3 tools `memory_query`/`memory_get`/`memory_stats`, koszt schematu ~402 tokny/request, weryfikacja end-to-end (init→list→query→get→dead-chunk isError→stats) + gate OK. Zarejestrowany w DSH: wpis `mcp-session-memory` w `~/.dsh/profiles/web/cordis.patch.yml` (format `- insert:`, interpreter hermes-venv `python.exe`, serverName `sessionmemory` → narzędzia `mcp__sessionmemory__memory_*`), mostek zweryfikowany spod docelowego interpretera (stats: 701/101642). Commity `d84eca7` + `0755977`. Next step: restart DSH web + test z nowej sesji (`memory_stats` → 701/101642), potem Poziom 1 (auto-ingest/SessionStart).
