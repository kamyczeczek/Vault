---
flag: owner-decisions-registered-2026-11-06
since: 2026-11-06
owner: mateusz
agent: deepseek-harness
model: nvidia/stepfun-ai/step-5-preview
origin: user request m00245 (icm-architect skill)
---

`owner-decisions-registered-2026-11-06` — 2026-11-06: rejestr decyzji właściciela uruchomiony na prośbę użytkownika (m00245, skill `icm-architect`). Mechanizm `handoff/decisions/` istnieje (kontrakt: jeden plik = jedna decyzja, `status: open`, render przez `scripts/build_status.py` do `handoff/status/STATUS.md` → `## Open decisions`), ale poza pytaniem `plan-md-migration` był pusty — sześć decyzji z 5-sesyjnego planu żyło tylko w prozie flag. Zamigrowałem je jako `status: open`: `openai-key-rotation`, `history-rewrite-filter-repo`, `dead-script-deletions`, `retrieval-v2-preflight`, `agents-md-agent-commit-ref`, `bat-files-eol-crlf`; każda ma `recommendation` + dowód jako LINK do flagi, bez kopii (ICM inv. 8).

Defekt znaleziony po drodze: `scripts/build_status.py` parsował `handoff/decisions/index.md` jako decyzję — widok `## Open decisions` pokazywał phantom `index` (owner: `?`, pusta recommendation). Naprawione: `index.md` skipowany obok `CONTEXT.md` w `collect()` (+komentarz w kodzie). Weryfikacja: `scripts/test_build_status.py` 6/6 OK, `build_status.py --check` wykrył realny STALE renderu przed rebuildem (potwierdza, że widok faktycznie się zmieniał, a nie że gate przeszedł przypadkowo).

Zaktualizowane: `handoff/decisions/CONTEXT.md` (Not-checked), `handoff/decisions/index.md` (6 wierszy), `handoff/status/NEXT.md` — przestaje być stale (verified_at 2026-10-18, limit 7 dni); nowe zdanie: właściciel wybiera spośród 6 decyzji, start od `dead-script-deletions` i `bat-files-eol-crlf` (nie wymagają śledztwa, tylko tak).

not checked: zewnętrzni konsumenci poza repo dla kandydatów do usunięcia (zakres raportu = in-repo grep); same decyzje NIE są podjęte — wszystkie sześć czeka na właściciela (SCARS S33: brak decyzji właściciela = status „czekam na decyzję").

Next: `git push` do `origin/master` (autoryzacja użytkownika w m00245) jako osobny krok po tym commicie, potem decyzje właściciela zaczynając od dwóch „tylko tak".
