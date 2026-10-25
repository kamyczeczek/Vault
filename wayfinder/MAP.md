# Wayfinder Map: Przebudowa Workspace'u

## Destination
Workspace, który nie powtarza problemów: jedno źródło prawdy, mechanizmy egzekwujące, pętla uczenia się z błędów. Cel osiągnięty oznacza mały, spójny rdzeń ICM odporny na duplikację, fałszywe sukcesy i brak testów.

## Notes
- Domena: Inżynieria oświetlenia kontekstowego, ICM (Interpretable Context Methodology), rygorystyczne testowanie i automatyzacja sesyjna.
- Kluczowe skille: `wayfinder`, `grill-with-docs`, `unlazy`, `icm-architect`, `token-hygiene`.
- Zasada nadrzędna: Zasada dowodu (brak twierdzenia o sukcesie bez artefaktu i logu testu).

## Decisions so far
- [ADR-001: Jedna baza brain.db](brain/decisions/ADR-001-single-brain-db.md): Zastąpienie rozproszonych magazynów jedną relacyjną bazą SQLite (`brain/brain.db`) na wiedzę, sesje i błędy.
- [ADR-002: Wymuszenie testów i bramek](brain/decisions/ADR-002-enforcing-gates-and-tests.md): Wprowadzenie rygorystycznych bramek przedcommitem (`unlazy` gates, testy hermetyczne).
- [ADR-003: Zamknięcie sesji i handoff](brain/decisions/ADR-003-session-closure-and-handoff.md): Obowiązkowy protokół flaga-handoff i automatyczne generowanie `HANDOFF.md` oraz `STATE.md`.
- [ADR-004: Separacja fabryki od produktu](brain/decisions/ADR-004-icm-factory-separation.md): Czysty podział na warstwę fabryczną (narzędzia, reguły, szablony) i produktową (artefakty runu).

## Not yet specified
- Szczegółowy schemat tabel w `brain.db` dla powiązania embeddingów i grafu wiedzy.
- Mechanizm automatycznej rotacji i archiwizacji starych flag handoff.
- Konkretne progi wydajnościowe dla skanerów integrity check.

## Out of scope
- Migracja kodu i danych historycznych z zarchiwizowanego katalogu `projects/_archive/` (pozostaje nietknięty zgodnie z regułą archiwum).
- Zmiana głównego modelu LLM lub providera w trakcie trwania sesji (zabronione przez reguły token efficiency).
