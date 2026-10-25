# pstack od poteto — research REVIEW

Pytanie: czym jest „pstack od poteto", jak działa i czy ma sens poza Cursorem?

Krótka odpowiedź: to zestaw gotowych procedur dla agentów kodujących —
piszesz krótko „napraw błąd X", a system sam dobiera checklistę (odtwórz błąd,
znajdź przyczynę, napraw, udowodnij na żywym systemie). Autorką jest
Lauren Tan (@poteto, zespół core Reacta, wcześniej Meta/Netflix, obecnie
Cursor) [1][2]. Działa najlepiej w Cursorze, ale same procedury da się
przenieść gdzie indziej — istnieją gotowe porty [3][4].

Uwaga o wersjach (czytaj przed instalacją): liczby skilli/playbooków różnią
się między portami, bo upstream to v0.14.x vs v0.15.0 — sprawdź `UPSTREAM_COMMIT`
portu, zanim go weźmiesz [6].

## Przebieg etapów (kontrakt §08)

| Etap | Status | Uwaga |
|---|---|---|
| 00_prepare | N/A | run sprzed pipeline — brak manifestu/HEAD |
| 01_web_research | PASS | źródła [1]–[6] realne, w tabeli poniżej |
| 02_ingest | N/A | notatki researchowe, bez ingestu do korpusu |
| 03_graph | N/A | graf nie był budowany |
| 04_retrieval | N/A | dowody z webu, nie z grafu |
| 05_reflection | PASS | synteza + 2 decyzje na końcu |
| 06_implementation | N/A | research-only, bez implementacji |
| 07_verification | N/A | research-only, brak claimów pytest (banner: PASS research-only) |
| 08_review | PASS | niniejszy dokument |

Proponowany werdykt: **PASS (research-only)**.

## Kim jest poteto (prostymi słowami)

Lauren Tan, znana jako @poteto — programistka z zespołu Reacta, pracowała
w Meta i Netfliksie, teraz w Cursorze [2]. Zanim dołączyła do Cursora,
sama budowała sobie warstwę orkiestracji agentów wokół Claude Code —
pstack to spakowanie tych wewnętrznych nawyków w publiczną wtyczkę [2].
Na starcie jej skille miały 9000 użyć w tydzień wewnątrz Cursora [2].

## Co to jest pstack (prostymi słowami)

Zwykły agent dostaje polecenie i pisze kod. pstack dokłada resztę roboty
inżynierskiej: zrozumienie systemu przed zmianą, projekt kształtu,
weryfikację na prawdziwym artefakcie, recenzję i wysyłkę [2].

Używasz zwykle jednej komendy:

```
/poteto-mode napraw X; najpierw odtwórz błąd i udowodnij poprawkę
```

System (tzw. tryb poteto) dobiera gotową checklistę — playbook — do rodzaju
zadania (błąd, funkcja, refaktoring, śledztwo, wolne działanie), kopiuje ją
do listy zadań i wzywa mniejsze skille, gdy ich krok nadejdzie [1][2].
Tryb jest „lepki": kolejne wiadomości typu „ciągnij dalej" zostają w tym
samym planie [5].

## Najważniejsze klocki

**Zrozum, zanim zmienisz.** `/how` śledzi, jak system działa w runtime
(ktoś czyta kod, inny request path, wyniki składa jeden opis) [2].
`/why` szuka, *dlaczego* coś tak wygląda — w historii Gita, ticketach,
czacie zespołu; puste wyniki też raportuje, zamiast zmyślać powód [2].

**Projektuj przed kodem.** `/architect` zaczyna od miejsca użycia
(typy i granice modułów wynikają z wołacza), a gdy implementacja zaczyna
„zgrzytać" (casty, wyjątki spoza szkicu), wyrzuca szkic i projektuje od nowa [2].
`/arena` daje to samo zadanie kilku modelom i składa jeden wynik
(porównanie projektów); `/swarm` dzieli zadanie na kawałki dla pokrycia —
mylenie ich to typowy błąd [1][2].

**Recenzja z kilku modeli.** `/interrogate` wysyła ten sam diff do kilku
modeli; prowadzący grupuje uwagi (do zrobienia / do rozważenia /
odnotowane / odrzucone) — odrzucone widać z powodem, więc możesz zweryfikować
osąd zamiast dostawać tajemniczo przefiltrowaną listę [2].

**Dowód zamiast „build przeszedł".** pstack odrzuca zielony build jako dowód.
Weryfikacja zależy od tego, co się zmieniło: zmiana w CLI odpala prawdziwą
komendę, zmiana UI przechodzi zmieniony flow, migracja odtwarza prawdziwe
dane, zmiana wydajności porównuje tracy [1][2]. Gdy repo nie ma jak tego
robić, komenda `/create-verification-skill` generuje lokalny skrypt weryfikacji
i sama go raz odpala od deski do deski [2].

**Długa praca nocna.** Warunek końca musi być sprawdzalny („zero starych
wołaczy + wszystkie fixtury zielone"), nie czasowy („pracuj 4 godziny").
Każda iteracja: sprawdź warunek → jedna uzasadniona zmiana → weryfikacja →
zostaw albo odrzuć → jeden wiersz dziennika decyzji (TSV) [2][5].

## Czy działa poza Cursorem

Tak, z zastrzeżeniami. Skille to pliki `SKILL.md` — ten sam format ładują
Claude Code, Codex i inne harnessy, więc procedury (playbooki, zasady,
`/how`, `/why`, `/interrogate`) przenoszą się jako instrukcje [2].
Gubisz kawałki tylko-Cursorowe: przypisywanie różnych modeli do podagentów,
`/setup-pstack` z zapisem do `~/.cursor/rules`, `/loop`, automatyzacje [2].

Gotowe porty (przykłady, stan na research):

| Port | Platforma | Uwagi | Sprawdzone |
|---|---|---|---|
| michael-denyer/pstack-claude | Claude Code, Codex, OpenCode, Gemini | 650 gwiazdek, 77 forków; tłumaczy prymitywy Cursora, zasady MIT [3] | 2026-10-03 |
| potetos-for-everyone | uniwersalny (npx) | deklaruje 100% zgodności z upstream v0.15.0+ (47 skilli, 23 playbooki, 23 zasady) [4] | 2026-10-03 |
| HustleCoding/pstack-codex | Codex | 44 skille, skrypt `check-upstream.sh` do śledzenia upstream [6] | 2026-10-03 |

Uwaga o liczbach: źródła podają różne rozmiary (np. 23 vs 24 skille,
22 vs 23 playbooki), bo opisują różne wersje upstream (v0.14.x vs v0.15.0).
To dryf wersji, nie sprzeczność — przy instalacji sprawdź `UPSTREAM_COMMIT`
portu [6].

## Kiedy to ma sens, a kiedy nie

Autor deep dive'a: bierz pstack tam, gdzie sensowny diff to za mało —
webhook z podwójnym mailem, migracja, twardy problem wydajnościowy, nocny
run z testowalnym warunkiem końca [2]. Nie bierz do przesunięcia daty
o jedno pole ani małej zmiany konfiguracji — kilka modeli, arena i dziennik
decyzji kosztują tokeny [2]. Do drobiazgów ten sam autor woli krótszą pętlę
(fstack): człowiek blisko każdej decyzji [2].

## Źródła

| # | Co | Adres |
|---|---|---|
| [1] | daily.dev: A deep dive into pstack (streszczenie + FAQ: arena vs swarm, weryfikacja) | https://daily.dev/posts/a-deep-dive-into-pstack-evqbnto9j |
| [2] | Flavio Copes: A deep dive into pstack (pełny, ~22 min: architektura, wszystkie playbooki, zasady, błędy, ocena) | https://flaviocopes.com/pstack |
| [3] | michael-denyer/pstack-claude (port: 650★, instalacja, zakres) | https://github.com/michael-denyer/pstack-claude |
| [4] | potetos-for-everyone (port uniwersalny, parzystość v0.15.0+) | https://www.npmjs.com/package/potetos-for-everyone (repo: TheOnlyFusionCube/potetos-for-everyone) |
| [5] | Cloeille/pstack — fork dla Hermes Agent (playbooki: investigation, bug-fix, feature, perf-issue, autonomous-run…) | https://github.com/Cloeille/pstack (README z raw.githubusercontent, commit ac5e5ab) |
| [6] | HustleCoding/pstack-codex (port Codex: 44 skille, UPSTREAM_COMMIT, audyt) | https://github.com/HustleCoding/pstack-codex |

Upstream (nie otwierany w tym researchu, do następnego kroku):
`https://github.com/cursor/plugins/tree/main/pstack`.

## Czego tu nie ma (uczciwe ograniczenia)

- Nie czytałem upstream `cursor/plugins/pstack` ani pliku `poteto-mode/SKILL.md`
  — opisy playbooków pochodzą z omówień [1][2][5], nie ze źródła.
- Nie weryfikowałem instalacji żadnego portu (gwiazdki i deklaracje parzystości
  to oświadczenia autorów, nie moje pomiary).
- Liczby skilli/playbooków zależą od wersji — patrz uwaga wyżej.

## Decyzje dla Ciebie

1. Czy taki format odpowiedzi researchowej jest tym, o co chodziło
   (prosty polski + źródła pod każdym twierdzeniem)?
2. Czy iść głębiej: otworzyć upstream i porównać deklaracje portów
   ze źródłem (parzystość, UPSTREAM_COMMIT)?
