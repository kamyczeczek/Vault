# Protokół Weryfikacji (Verification Protocol)

1. **Cel**: Zapewnienie, że każda zmiana w kodzie, dokumentacji lub konfiguracji jest weryfikowana merytorycznie i technicznie przed uznaniem zadania za zakończone.
2. **Kroki weryfikacji**:
   - **Pre-check**: Sprawdzenie stanu repozytorium (`git status`, wymagane flagi, integrity checks).
   - **Inkrementalność**: Wprowadzanie zmian przez precyzyjne edycje (`edit`) zamiast przepisujących całe pliki (`write`).
   - **Testowanie / Integracja**: Uruchomienie skryptów weryfikacyjnych i testów spójności (np. `check_workspace_integrity.py`, testy jednostkowe lub ewaluacyjne pilota).
   - **Handoff & States**: Aktualizacja flag wynikowych w `handoff/flags/`, przebudowa widoków (`build_handoff.py`, `build_state.py`) i weryfikacja czystości workspace (`git diff --check`).
3. **Zasada zero-regression**: Żadne zmiany nie mogą psuć integralności workspace ani pozostawiać niespójnych ścieżek.
