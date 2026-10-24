---
flag: ask-user-question-fixed
since: 2026-10-11
owner: Mateusz
agent: opencode
model: omniroute/gemini/gemini-flash-lite-latest
origin: fix ask-user-question ui lock bug
---

`ask-user-question-fixed` — 2026-10-11: Plik `ask-user-question.ts` był ucięty w połowie funkcji `execute` (59 linii, brak domknięć i helperów) — to dawało `ParseError` i blokowało start pi. Przebudowano plik na minimalną kompletną wersję (TypeBox params + `ctx.ui.input`/`ctx.ui.select`, bez globalnego mutexa — pi i tak serializuje tool calle). Test: `pi -p "ping"` ładuje rozszerzenia bez `ParseError` (zostaje tylko 401 invalid x-api-key, czyli osobny problem klucza providera, nie rozszerzenia).
not checked: klikalny test `ask_user_question` w żywym TUI (wywołanie narzędzia w interaktywnej sesji).
