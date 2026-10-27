---
type: Concept
title: control-protocol
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Protokół kontroli bez narzędzia — dla ŚWIEŻEJ sesji (zero kontekstu Fazy 6)

## Dlaczego ten plik istnieje

Faza 6 falsyfikatora v2 ma 3 filary: Q-ground MATCH 4/4 (stoi), Q-refusal
ODMOWA (stoi), kontrola bez narzędzia (pusta). Q-ground nie odróżnia
„graf zwrócił właściwy dokument" od „model rozpoznał abstrakt", bo oracle
(człowiek, arXiv:2603.25111v2) == źródło korpusu (ingest tego abstraktu).
Tylko ta kontrola rozstrzyga.

## Instrukcja (czytaj dosłownie)

1. NOWA sesja, NOWY agent. Przed uruchomieniem: NIE OTWIERAĆ niczego z
   `pilots/graphrag/` (ani CONTRACT.md, ani proof/, ani tego repo).
   Bez grafu, bez `graph.db`, bez abstraktu w prompcie.
2. Zadać modelowi DOKŁADNIE jedno pytanie:
   „Czym jest SEVerA i jak się ma do self-evolving agents?"
3. Zapisać odpowiedź verbatim + datę + model do `proof/falsifier-v2/control-answer.md`.
3A. BRAMA ADEKWATNOŚCI (PRZED markerami, ślepo — luka znaleziona w werdykcie
   2026-10-10, załatana tutaj): czy odpowiedź PRÓBUJE odpowiedzieć na pytanie
   merytorycznie (≥1 twierdzenie o SEVerA / self-evolving agents)?
   „Nie wiem" / odmowa / odpowiedź nie na temat → STOP: wynik NIEROZSTRZYGNIĘTY
   (nie „grounding udowodniony" — brak markerów w pustej odpowiedzi o niczym
   nie świadczy). Dopiero odpowiedź adekwatna idzie do kroku 4.
4. Ocenić mechanicznie (bez interpretacji, ŚLEPO — bez otwierania proof/):
   - Czy odpowiedź zawiera „FGGM" LUB „Formally Guarded"? (TAK/NIE)
   - Czy zawiera „three-stage" LUB (koniunkcję „Search" + „Verification" +
     „Learning" W ZDANIU O SEVERA, nie jako generyczne słowa)? (TAK/NIE)
     Uwaga: generyczne „search/verification/learning" o agentach w ogóle
     to NIE — marker wymaga powiązania z SEVerA/FGGM/paperem. Fałszywy TAK
     na generyce = FAIL mimo braku znajomości paperu (luka znaleziona
     w weryfikacji protokołu 2026-10-10, załatana tutaj).
   - Czy zawiera „tau2-bench" LUB „tau^2" LUB „zero constraint violations"? (TAK/NIE)
   - Czy zawiera cytat z nodes.body (dłuższy niż 10 słów)? (TAK/NIE)
5. DOPIERO PO kroku 4 wolno otworzyć abstrakt (oracle z CONTRACT.md) i sprawdzić
   skażenie: czy odpowiedź zawiera treść, której nie ma ani w treningu, ani
   w abstrakcie? (TAK = przeciek kontekstu → kontrola skażona). Kolejność
   ŚLEPO-NAJPIERW jest obowiązkowa: ocena markerów przed dopuszczeniem
   abstraktu, bo kotwica działa w obie strony (luka znaleziona w weryfikacji
   protokołu 2026-10-10: krok 4 był ślepy, scenariusz 3 wymagał sądu PO —
   teraz rozdzielone).

5B. PARAFRAZA (po otwarciu abstraktu, razem z krokiem 5): czy adekwatna odpowiedź
   z 4× NIE zawiera merytoryczną parafrazę bloków oracle (ryzyko braku gwarancji /
   FGGM-kontrakt / three-stage / zero-violations) BEZ dosłownych markerów?
   TAK → model zna treść paperu (słowa inne, wiedza ta sama) → traktować jak TAK
   w markerach → **Q-ground FAIL jako test groundingu**. Parafraza to nie
   ogólnikowość; markery łapią słowa, ten krok łapie wiedzę.

## Rozstrzygnięcie

- Odpowiedź nieadekwatna (brama 3A) → **WYNIK NIEROZSTRZYGNIĘTY** — kontrolę
  powtórzyć (inny model / inne sformułowanie); NIC nie zapisuje się do task_plan.md.
- 4× NIE + odpowiedź adekwatna + brak parafrazy (krok 5B) → model ogólnikowy
  mimo próby → graf wniósł treść → **grounding Q-ground UDOWODNIONY**,
  Faza 6 domknięta (zapisać w task_plan.md sekcję terminalną).
- Którekolwiek TAK (poza trywialnym „SEVerA = verified synthesis") → model ma
  paper w treningu → graf nie wniósł treści → **Q-ground FAIL jako test
  groundingu** (przechodzi jako test proweniencji). Nie ukrywać, zapisać.
- Odpowiedź zawiera treść, której nie ma ani w treningu, ani w abstrakcie →
  **kontrola skażona** (przeciek kontekstu) → protokół do przeprojektowania,
  wynik nieważny.

## Zakazy

- Nie zaglądać do proof/falsifier-v2 PRZED oceną (kotwica).
- Nie „poprawiać" odpowiedzi modelu wiedzą z grafu.
- Nie uruchamiać w sesji, która widziała cokolwiek z Fazy 6 (skażenie z definicji —
  tak padła próba w sesji Q-ground 2026-10-10; teatr zamiast dowodu).
