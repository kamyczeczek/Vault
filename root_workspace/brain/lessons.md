# Brain Lessons

- **Warunek porażki:** Bramka integrity failuje na nowym root entry (np. dodanie katalogu/pliku do roota).
- **Przyczyna:** Poprzedni agent dodaje wpis do `ALLOWED_ROOT` w `scripts/check_workspace_integrity.py` bez jednoczesnej edycji tabeli "Where things live" w `CLAUDE.md`, obchodząc założenie bramki.
- **Mechaniczna korekta:** Wymuszenie testu parytetu `ALLOWED_ROOT` ↔ `CLAUDE.md` / `.gitignore` (skrypt `scripts/test_gate_allowlist_parity.py`) oraz zakaz edycji allow-listy bez aktualizacji katalogu.
- **Warunek porażki:** Sesja planistyczna tworzy artefakty (PLAN.md, MAP.md, ADR-y) i ich nie commituje.
- **Przyczyna:** Następna sesja dziedziczy untracked pliki, które zanieczyszczają commit wykonawczy oraz łamią deklarację root entries w CLAUDE.md.
- **Mechaniczna korekta:** Wymuś commit planistyczny jako część zamknięcia każdej sesji planistycznej (nie tylko raport).
