---
flag: skills-wiring-and-unlazy-enable-2026-10-28
since: 2026-10-28
owner: mateusz
agent: opencode
model: omniroute/agy/gemini-3.8-flash-high
origin: session-close
---

`skills-wiring-and-unlazy-enable-2026-10-28` — 2026-10-28: Wpięto katalog `skills/` do konfiguracji OpenCode, jCode i Claude Code przez junctions na dysku (`~/.config/opencode/skills`, `~/.jcode/skills`, `~/.claude/skills`). Usunięto flagę `disable-model-invocation: true` ze skilla `unlazy` (`skills/unlazy/SKILL.md`), dzięki czemu skill jest teraz natywnie wykrywany i ładowalny przez harness OpenCode (wcześniej zwracał `Unable to load skill unlazy`). Weryfikacja: wywołanie narzedzia `skill(id='unlazy')` zakończone sukcesem i załadowaniem pełnej treści skilla.

not checked: test wywołania skilla z poziomu jcode i claude-code CLI (junctions istnieją na poziomie systemu plików).
