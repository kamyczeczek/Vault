---
ticket: B3
status: resolved
resolved: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
decision: re-derive only executable-artifact claims; fail-loud in --dry-run, WARN in close; 3 mutations
---

# B3 — `close.py --verify-claims`: które twierdzenia re-derywować, jaki failure mode?

**Pytanie.** `close.py --verify-claims`: które twierdzenia flagi re-derywować, i jaki
failure mode?

## Decyzja (właściciel, 2026-10-16)

1. **Zakres = tylko twierdzenia z wykonywalnym artefaktem.** Re-derywuj te, których
   prawdziwość da się przeliczyć, nie ocenić:
   - `commit <hash>` → hash musi istnieć w `git log`;
   - `N wierszy` / licznik (`N plików`, `N wierszy`) → komenda przelicza wartość;
   - `gate exit 0` → re-run bramki.
   Twierdzenia **narracyjne** („system działa", „rozstrzygnięto X") są pomijane — nie
   mają artefaktu, więc deterministyczna bramka nie ma czego failować (a bramka, która
   nie umie failować, to dokumentacja — S56/S62).
2. **Failure mode = fail-loud w `--dry-run`, WARN w `close`.** `close.py --dry-run
   --verify-claims` kończy się `exit 1` przy rozjeździe; właściwe `close` tylko `WARN`.
   Powód: dry-run jest bezpieczną bramką (nigdy nie kończy sesji), a close nie może
   blokować zamknięcia sesji na błąd weryfikacji (ryzyko false-positive przy
   niejednoznacznym twierdzeniu).
3. **Kryterium sukcesu = 3 mutacje** (zapisane **przed** implementacją, S56/S62):

   | # | Mutacja | Oczekiwanie |
   |---|---|---|
   | 1 | flaga z fałszywym `commit <hash>` | `--verify-claims` **FAIL** |
   | 2 | flaga z prawdziwym hashem (kontrola) | **PASS** |
   | 3 | flaga z liczbą bez artefaktu (np. „162 plików" bez komendy) | **WARN** (nie FAIL) |

## Dlaczego

`close.py` dziś sprawdza tylko **kształt** ciała flagi (`check_body`, linie 78-89:
`startswith \`flag\``, obecność `not checked:`). Nie parsuje żadnego twierdzenia — nie
ma `--verify-claims`. Twierdzenia „na żywo" w ciele flagi dryfują dokładnie jak liczba
plików w mapie (patrz stale fact `handoff/flags/` 161 → 162, naprawiony tą samą sesją):
flaga mówi `commit abc1234` albo `162 plików`, a po tygodniu twierdzenie jest fałszywe, a
nikt tego nie widzi. Ze 162 flag 140 linii zawiera hashe commitów i 147 liczby/exit-kody
— to nie przypadek brzegowy, to klasa.

Pomijanie twierdzeń narracyjnych jest świadome: `--verify-claims` jest deterministyczne
(bez LLM), więc zakres = to, co da się przeliczyć. Narracja zostaje w `not checked:`.

## Odrzucone alternatywy

- **Wszystkie liczby i hashe (nie tylko znany format)** — grozi false-FAIL na liczbach
  narracyjnych (np. „3/10 cases"), które nie mają jednej wykonywalnej derywacji.
- **Także narracyjne (LLM-check)** — niedeterministyczne i kosztowne; sprzeczne z
  „bramka musi umieć failować" jako deterministyczna bramka.
- **fail-loud wszędzie** — blokuje zamknięcie sesji przy false-positive; ryzyko większe
  niż korzyść, skoro dry-run już daje twardą bramkę.
- **advisory wszędzie** — bramka bez trybu FAIL; dokładnie to, co krytykuje S56/S62.

## Handoff

Implementacja `close.py --verify-claims` to `task`, nie decyzja → poza destination mapy
decyzyjnej (`docs/wayfinder-brain-map.md`). Wykonanie w nazwanym efforcie
`docs/wayfinder-brain-execution-map.md` — wygraduje się tam jako **E6** (create-then-wire
przy starcie tego effortu), zgodnie z regułą mapy: `task` bez execute-in-map → handoff
wykonawczy do nazwanego effortu (dług S64/S65, którego nie wolno zostawić bez wykonawcy).

`not checked:` nie zaimplementowano `--verify-claims` (to decyzja, nie deliverable); nie
uruchomiono 3 mutacji na żywej bramce (brak implementacji — kryterium zapisane przed
runem); nie zmierzono, ile fałszywych twierdzeń `commit`/liczników faktycznie dryfowało
historycznie w 162 flagach; nie ustalono, czy re-run `gate exit 0` ma być re-runem
całego `check_workspace_integrity.py` czy pojedynczej bramki z ciała (do doprecyzowania
przy E6).
