---
flag: graphrag-verdict-p0-protocol
since: 2026-10-10
owner: mateusz
agent: pi
model: nara/muse-spark-1.3-contributor-free
origin: session-close
---

`graphrag-verdict-p0-protocol` — 2026-10-10: werdykt review rozliczony. (1) P0: eksport sesji zawierał linie kluczy o realistycznych długościach (OMNIROUTE/NARA/GOOGLE/GEMINI/OPENAI + Bearer w pliku 04) w dwóch katalogach scripts/out/sessions-20261009-2356 i 20261010-1532; nigdy nie commitowane do gita (git log pusty), scripts/out/ gitignored; wartości zredagowane lokalnie markerami [REDACTED-*-2026-10-10], re-scan czysty (zostały tylko nazwy zmiennych + localhost URL + TERMINAL_ENV=local). Człowiek musi unieważnić/obrócić aktywne klucze — tego agent nie może zrobić. (2) Luka protokołu z werdyktu załatana w pliku: brama adekwatności 3A (Nie wiem/odmowa/off-topic = NIEROZSTRZYGNIĘTY, stop przed markerami) + krok parafrazy 5B po otwarciu abstraktu (4x NIE + parafraza bloków oracle = FAIL jako grounding). Gałąź UDOWODNIONY wymaga odtąd adekwatności + braku parafrazy. KR commit 49373b6 (1 plik, dokładnie mój); dług KR nietknięty. Kontrola bez narzędzia nadal czeka na świeżą sesję z załatanym protokołem.
not checked: rotacja kluczy przez człowieka (redakcja lokalna zrobiona, unieważnienie nie); wykonanie kontroli (świeża sesja); sekcja terminalna task_plan.md (po kontroli); re-run selftestu graphrag.py; R15/R16; KR debt; kg.py; close-ritual-coupled + --amend (właściciel).
