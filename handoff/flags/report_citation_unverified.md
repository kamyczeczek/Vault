---
type: Concept
flag: report_citation_unverified
since: 2026-10-03
owner: opencode
agent: opencode
model: opencode/space-bunny-free
origin: architecture review (improve-codebase-architecture x icm-architect)
title: report_citation_unverified
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---
`report_citation_unverified` — 2026-10-04: **zamknięte — trzecia noga doszła.**
Sonda, która w `5ec7f68` znalazła żywe `137` i dopełnienie `:1-:54, :106-:137`,
jest teraz skommitowana jako `scripts/audit_prose_numbers.py` i wołana przez R13
obok `--report-check`. Zamknięcie trzech warstw naraz: blok (`8282dd1`), baseline
(`a15ebf4`, `931aac5`), proza (`--prose-numbers`).

**Claim, który tu zostawał otwarty, był zawężony do zera.** Poprzednia wersja
mówiła „~205 tokenów, których ręczna klasyfikacja jest zadaniem autora raportu,
sonda jednorazowa w %TEMP%". To dokładnie F1 w opisie naprawy F1: liczba, która
wygląda na zmierzoną, a była oszacowana z pierwszych 60 wypisanych pozycji przy
217 (udokumentowane w `5ec7f68` i `06e31f0`). Teraz nie ma nic do zmierzyć
ręcznie — residuum jest **wyliczone przez gate**: 60 wpisów `EXEMPT`, każdy z
klasą i powodem, plus 22 nazwy kształtów mechanicznych (badge, `:76-98`, `v7`,
`R13`, `4 step 1`, `phase-5`, `2 → 3`, jednotokenowy `<code>`). Wpis, którego
proza już nie cytuje, **sam powoduje fail** — tabela nie rośnie w nieskończoność,
bo to byłby drugi koperty prozy, dryfujący. `--by-value` to tryb pisania wpisów
(uruchom, przeczytaj numery linii, napisz powód).

Dowód na G1, nie deklaracja: `DriftProofTests` rośnie `AGENTS.md` o trzy linie,
przepuszcza `--write-block`, dostaje zielony `--report-check` — i **czerwony**
`--check` prose'u z wskazaniem `137`. Wcześniej ten sam dokument przechodził.

Granice, wypisane bo bramka, która je ukrywa, jest gorsza od bramki: `EXEMPT`
pozwala kilka klas na wartość (`50` to `35 + 15 = 50` na liczbach wycofanych
w jednym miejscu i `51 − 1 = 50` w wierszu mutacji w innym — jedna klasa byłaby
kłamstwem w tabeli), a `quoted-ags-evidence` obsługuje liczby cytowane z własnego
bulleta dowodowego `AGENTS.md`, gdzie `--check` łapie **usunięcie linii, nie
zmianę liczby w niej**. Cytat gnije, dopóki ktoś nie przeczyta pliku; tej luki nie
zamyka żadna bramka.

Next: `docs/reviews/README.md` ma teraz sekcję „The prose half" i sekcję
„What is still ungated here" (README sam jest niegated — ale R13 sprawdza teraz,
że każdy `*.html` ma wiersz w jego tabeli). Kandydaci 2 → 3, 4-steps-1–2, 1
raportu nieobsadzone; candidate 4 step 3 to ludzka decyzja wartościowa na
mianowniku 17 linii. Szczegóły: `report_numbers_became_gate`,
`gate_has_no_automatic_caller`.