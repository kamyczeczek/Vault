# ADR-002: Wymuszenie testów i bramek (Unlazy & pre-commit)

## Status
Zatwierdzony

## Kontekst
Workspace cierpiał z powodu fałszywych sukcesów („done” bez dowodu), braku automatycznych testów przed zatwierdzeniem zmian oraz pomijania weryfikacji integralności.

## Decyzja
Wprowadzamy bezwzględne reguły weryfikacji:
1. Każde zadanie o charakterze implementacyjnym lub strukturalnym musi posiadać plik `GATES.md` (zgodnie ze skillem `unlazy`), definiujący testy i oczekiwane rezultaty (`CHECK` / `EXPECT`).
2. Żadna zmiana nie może być zatwierdzona bez przejścia skryptu weryfikacji integralności (`python scripts/check_workspace_integrity.py`).
3. Obowiązuje Zasada Dowodu: brak dowodu z logu testu lub `git diff` oznacza stan PENDING.
4. Hook pre-commit automatycznie weryfikuje skan sekretów, budowanie handoffu oraz integralność workspace'u.

## Konsekwencje
- Koniec z deklaratywnymi sukcesami bez pokrycia w testach.
- Przewidywalny i powtarzalny cykl weryfikacji każdej zmiany.
