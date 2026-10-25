---
ticket: B1
status: resolved
resolved: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
decision: research — drift surface of the 10 non-opencode stores
---

# B1 — drift surface of non-opencode stores

**Pytanie:** które z 10 store'ów poza opencode czytają tabelę/klucz wrażliwy na
migrację schematu (cicha utrata wierszy jak S68)?

**Odpowiedź.** Wszystkie 10 loaderów w `scripts/agent_sessions.py` czytają **stałą**
nazwę tabeli (SQLite) albo **stały** klucz/ścieżkę JSON — żadna migracja nie jest
wykrywana sama. Wzorce:

| Store | Czyta | Wykrywa brak? |
|---|---|---|
| goose | DB tabele `sessions`+`messages` (331-336) | `OperationalError` → outer `except` (głośne, ale 0 wierszy) |
| hermes | DB tabele `sessions`+`messages` (386-391) | jak goose |
| cursor | DB `cursorDiskKV` `LIKE 'composerData:%'` (756) + `composerHeaders` (770) | **bare `except: pass`** (765) — ciche |
| pi / omp | glob `*.jsonl` + klucze `type=="session"/"message"` (442,454-458) | per-line bare `except` (460) — ciche |
| jcode | glob `*.json` + klucze `id/title/messages` (560-569) | ciche |
| antigravity | `transcript*.jsonl` + `type=="USER_INPUT"` (672-688) | fallback nazwy pliku; klucz zdarzenia stały |
| droid | glob `*.jsonl` + `type=="message"` (887,923) | ciche |
| **deepseek** | glob `*.jsonl`/`*.zstd` + dyspatch `type`/`data` (997-1067) | **`if not events: continue`** (1104) — ciche |
| cline | glob `*.messages.json` + klucze `sessionId/messages` | ciche |

Tylko **opencode** sonduje `sqlite_master` (`_opencode_tables`, 141-142) i czyta
tabelę-nadzbiór. **Najwyższe ryzyko: deepseek** — format już raz migrował (nota „v4", 991),
a brak zdarzeń jest połykane przez `continue` (1104): dokładny wzorzec S68.

**Konsekwencja dla mapy.** Motywuje asercję driftu per agent — ticket B2 (typ `task`).
Po decyzji właściciela (2026-10-16) destination tej mapy = decyzje, nie deliverable, więc
B2 zamknięty jako out of scope (handoff wykonawczy).

`not checked:` nie uruchomiono żadnego loadera na realnym store z po-migracyjnym
schematem (weryfikacja statyczna czytania kodu); nie skwantyfikowano, ile wierszy
faktycznie ginie per store; linie wg HEAD `e8d1b08`.
