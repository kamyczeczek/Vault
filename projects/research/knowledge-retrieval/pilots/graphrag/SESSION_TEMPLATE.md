---
type: Concept
title: SESSION_TEMPLATE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Szablon sesji — pilot graphrag

## Obowiązkowy start
1. Odczytaj `SCARS.md` (znane awarie).
2. Odczytaj `eval/artifact_manifest.json` (co już istnieje).
3. Uruchom `python eval/verify_artifacts.py` — pokaż output.

## Obowiązkowy koniec
1. Zapisz każdy artefakt do pliku.
2. Zaktualizuj `artifact_manifest.json` (dodaj hashe).
3. Uruchom `python eval/verify_artifacts.py` — pokaż output.
4. Raport końcowy w formacie D0-D7 z pełną deklaracją zakresu wykonania i sekcją `ZNANE AWARIE — ADRESACJA`.
5. NIE commituj, dopóki `verify_artifacts.py` nie zwróci `OK`.

## Format raportu (D0-D7)

D0. ZAKRES WYKONANIA:
    - Warstwa 1 (manifest+verify): PLIK ISTNIEJE: TAK | TEST FUNKCJONALNY: TAK/NIE
    - Warstwa 2 (canary): PLIK ISTNIEJE: TAK | TEST FUNKCJONALNY / INTEGRACJA: TAK/NIE
    - Warstwa 3 (SCARS): PLIK ISTNIEJE: TAK | ADRESACJA S1-S9: TAK/NIE
    - Warstwa 4 (session template): PLIK ISTNIEJE: TAK | UŻYTY: TAK/NIE
    - Warstwa 5 (pre-commit hook): PLIK ISTNIEJE: TAK | TEST GIT COMMIT: TAK/NIE
    - Powód pominięcia / brak integracji (jeśli dotyczy): <...>

D1. NAJWAŻNIEJSZA LICZBA: <liczba>
D2. WERDYKT: PORAŻKA | CZĘŚCIOWY | SUKCES
D3. DANE:
    - każda liczba z adnotacją `[źródło: <path>]`
    - jeśli brak pliku — napisz `NIE WYKONANO`
D4. CANARY:
    - CANARY_01: refusal=True/False [źródło: <path>]
    - CANARY_02: ...
    - ...
D5. ZNANE AWARIE — ADRESACJA:
    - S1: ...
    - S2: ...
    - ...
D6. INTERPRETACJA (do weryfikacji):
    - [Fakt: <z D3>] → [Interpretacja: ...]
D7. NASTĘPNY KROK: <...> | CZEKAM NA DECYZJĘ WŁAŚCICIELA | NIE WIEM
