---
ticket: B7
status: resolved
resolved: 2026-10-16
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
decision: adopt expect_hash per case; fail-loud in eval_brain.py --check
---

# B7 — content-hash w anchorach `brain_eval.json`

**Pytanie.** Content-hash w anchorach (#15): przyjąć `expect_hash` per case?

## Decyzja (właściciel, 2026-10-16)

1. **Adopt `expect_hash` per case** — każdy answerable case (`expect != null`) dostaje
   `expect_hash` = sha256 wiersza spod `expect`, liczone tym samym
   `scripts/ingest_brain.py::_row_fingerprint`, którego używa `ingest_brain.py --check`
   (jedna definicja „wiersza", brak drugiego źródła prawdy).
2. **Fail-loud** — `eval_brain.py --check` kończy się `exit 1`, gdy wiersz spod `expect`
   nie zgadza się z `expect_hash`. R21 w `check_workspace_integrity.py` już woła
   `eval_brain.py --check`, więc bramka ma automatycznego callera (bramka bez callera to
   dokumentacja).
3. **Kryterium sukcesu = trzy mutacje** (zapisane **przed** implementacją, S56/S62):

   | # | Mutacja | Oczekiwanie |
   |---|---|---|
   | 1 | wstaw syntetyczny bezimienny `- …` scar do `SCARS.md` | `eval_brain.py --check` **FAIL** — nazywa case i ID, które się rozjechały |
   | 2 | bez wstawki (kontrola negatywna) | `--check` **PASS** |
   | 3 | przeredaguj wiersz in place (to samo ID, inna treść) | `--check` **FAIL** (hash obejmuje treść, nie tylko ID) |

## Dlaczego

`problems:<n>` = numer S dla nazwanych scarów (`## S<n>`, `- S<n>:`), ale
`1000 + kolejność` dla **bezimiennych jednolinijkowców** (`ingest_brain.py:233`,
`UNNAMED_ID_BASE = 1000`). `lessons:<n>` = kolejność pliku — też niestabilne. Tylko
`decisions:<n>` (numer D) jest stabilny. Wstawienie jednego bezimiennego scara
re-targetuje **wszystkie** anchory `10XX`. `eval_brain.py --check` porównuje **liczby**
(hit/refusal/MRR), nigdy nie sprawdza, czy `expect` nadal wskazuje zamierzony wiersz →
**cicha zmiana mierzonego wiersza** (fałszywa zieloność).

W `brain_eval.json` na niestabilnych ID wisi **3/10** answerable cases: `problems:1001`
(`msys-python-c-ban`), `problems:1022` (`root-delete-to-pass-gate`), `lessons:1`
(`new-root-entry-breaks-integrity`).

## Dowód — surowy output

Eksperyment (bez edycji `SCARS.md`): parsuje realny `SCARS.md`, potem ten sam tekst z
jedną syntetyczną bezimienną linią wstawioną na górę, i różnicuje mapę `id -> title`.

```
unnamed one-line scars: before=22 after=23

anchors pinned in brain_eval.json:
  problems:1001
    before -> 'Windows tooling scars'
    after  -> 'B7 synthetic unnamed insertion'
    retargeted: True
  problems:1022
    before -> 'Nieuprawnione kasowanie katalogów na rootcie w celu przejścia bramki integrity'
    after  -> '`STATUS: OK` przy otwartych decyzjach właściciela'
    retargeted: True

total unnamed anchors that change target: 22/22
```

Skrypt: `C:\Users\Mateusz\AppData\Local\Temp\opencode\b7_anchor_shift_demo.py`
(poza repo — świadomie, żeby nie robić churnu w `scripts/_scratch/`; odtwarzalny:
`from ingest_brain import parse_scars` + insert jednej linii `- …`).

## Odrzucone alternatywy

- **Nadać każdemu bezimiennemu scarowi stały numer S** — usuwa przyczynę, ale zmienia
  treść `SCARS.md` i wymusza re-baseline wszystkich `problems:10XX` + dokumentów, które je
  cytują; większy churn niż detekcja. Materiał na świeży effort, gdy pojawi się konsument
  stabilnych ID.
- **Oba (stałe ID + `expect_hash`)** — podwójne zabezpieczenie, największy churn.
- **Nic, tylko `known_gaps`** — akceptuje cichą zmianę mierzonego wiersza; sprzeczne z
  „bramka musi umieć failować" (S56, S62).

## Handoff

Implementacja (`expect_hash` w `brain_eval.json` + pre-flight w `eval_brain.py --check`)
to `task`, nie decyzja → poza destination tej mapy (mapa decyzji, nie deliverable;
właściciel, 2026-10-16). Wykonanie w osobnym effortcie.

`not checked:` nie zaimplementowano `expect_hash` ani pre-flightu (to decyzja, nie
deliverable); nie uruchomiono mutacji na żywej bramce (brak implementacji — kryterium
zapisane przed runem); nie potwierdzono, że `_row_fingerprint` ma identyczny payload
liczony ze źródła i z `brain.db` dla `lessons`/`decisions` (do sprawdzenia przy
implementacji).
