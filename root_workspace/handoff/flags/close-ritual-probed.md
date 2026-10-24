---
flag: close-ritual-probed
since: 2026-10-10
owner: mateusz
agent: pi
model: nara/muse-spark-1.3-contributor-free
origin: session-close
---

`close-ritual-probed` — 2026-10-10: obca sesja (pierwsza niemodyfikująca close.py) zweryfikowała checklistę z close-ritual-coupled na żywym branchu probe/no-ritual-commit (sprzątnięty, master czysty na 710482b): (1) commit spoza rytuału przeszedł mimo hooka — hook przebudował i dostawił STATE.md do commita; (2) padnięty generator (PYTHON=false) zablokował commit na rebuildzie widoków — cena sprzężenia z e78a884 potwierdzona w obie strony; (3) --include: dry-run z zadeklarowanym stray = OK, z literówką = FAIL na [validate] przed bramami (fail-fast działa). Relabel not checked: potwierdzony z diffu e78a884→710482b — treść Next: przeniesiona 1:1, zero nowej przestrzeni negatywnej; finding zapisany tu zamiast naprawiania cudzej flagi. Wzorzec z sesji: testy 8/8 pokrywają tylko helpery, transakcja wyłącznie dogfoodingiem autoreferencyjnym — ten close jest pierwszym nie-autoreferencyjnym testem. Przy okazji odtworzona blizna (a) z SCARS.md we własnej sondzie (echo $? po pipie mierzy tail) — stan zweryfikowany git log, nie pipe'em. Next: --amend albo świadoma decyzja o jego braku; podpowiedź dirty-plików przy --include (check_includes łapie literówki, nie podpowiada zapomnianych).
not checked: pełna transakcja close.py na prawdziwej fladze (ten commit jest pierwszym testem — punkt 1 domyka się dopiero jego sukcesem); --no-verify omija hook jednym przełącznikiem, więc „hook blokuje" znaczy „blokuje commity bez --no-verify" (siła dowodu z pkt 2 ograniczona, luka nazwana tu, nie w Next:); R16 po moim commicie (sesja nie tknęła scripts/**, WARN nieoczekiwany, ale niepotwierdzony); Q-refusal/Q-ground z graphrag-falsifier-v2-next (przeczytany tylko nagłówek); memory-index lag po moim commicie.
