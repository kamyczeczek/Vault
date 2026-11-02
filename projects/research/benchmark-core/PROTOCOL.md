# Protokół benchmarku generalizacji v2 (normatywny)

Dokument stanowi normatywny protokół ewaluacji wielodomenowej w projekcie `benchmark-core`. Wszystkie decyzje zostały zamrożone w drodze ustrukturyzowanego wywiadu architektonicznego i analizy kodu `fev 0.10.0` oraz publikacji *fev-bench: A Realistic Benchmark for Time Series Forecasting* (arXiv:2509.26468).

---

## 0. Cel i hierarchia normatywna

- **Cel główny**: Wyłonienie metody prognozowania szeregów czasowych, która wykazuje powtarzalną i statystycznie istotną generalizację na wielu heterogenicznych domenach przy zachowaniu niskiego narzutu obliczeniowego (trening CPU, $\le 20$ min ściany), oraz potwierdzenie tej przewagi w pojedynczym, prerejestrowanym teście na zapieczętowanym zbiorze Lockbox. Wyniki na pojedynczych zbiorach (w tym ETTh1) nie stanowią celu projektu.
- **Hierarchia normatywna** (konflikt rozstrzyga wyższa warstwa):
  1. **Warstwa 1 — Protokół**: definicje danych, metryka, bramki decyzyjne, rygor lockboxa. Normatywny, zamrożony kryptograficznie (`manifest_sha256`), modyfikowalny wyłącznie przez formalny wpis `amendment` w ledgerze.
  2. **Warstwa 2 — Proces**: karta cyklu, populacja $N \le 8$, role metod, budżet czasu, dyscyplina agenta.
  3. **Warstwa 3 — Raport**: widok read-only nad ledgerem; nie podejmuje decyzji, nie zmienia statusów modeli.

---

## 1. Faza 0: Domknięcie linii ETTh1 H720 (poprzednik)

- **Status**: Linia ETTh1 H720 posiada odrębny, dedykowany artefakt normatywny: `projects/research/etth1-h720/GATES-s44-calibration.md` (z pre-rejestracją i poprawką Amendment A1 z 2026-11-01). Kontrola reprodukcji S44 na obu plikach danych została zaliczona z błędem względnym $4{,}2 \times 10^{-11}$ (`results/s44_calibration_reproduction.json`). Ledger v2 startuje w Fazie 1.
- **Wartość 1,7229**:
  - Pochodzenie: pierwszy, przerwany przebieg kalibracji na starym kodzie (in-sample stacking, origin 8640, seed 42, czas ~844 s, awaria na poziomie `BrokenProcessPool`).
  - Zabezpieczenie artefaktu: log wykonawczy został odnaleziony w `$env:TEMP\s44_calib.log` i zabezpieczony w `projects/research/etth1-h720/results/s44_calib_insample_failed.log` wraz z obliczeniem sumy kontrolnej SHA-256.
  - Interpretacja: w `GATES-s44-calibration.md` wartość ta jest formalnie oznaczona jako *„historyczna wartość widziana z nieważnego wariantu (in-sample stacking), inny estymand, nie stanowi punktu odniesienia ani bramki dla wyniku out-of-sample”*.
- **Weryfikacja parametrów**: Protokół kalibracji wymaga 12 originów (8640..16560 co 720 h), horyzontu $H=720$, okna treningowego 8640, seed setu 42, 43, 44, 45, 46 dla PatchTST-Delta oraz alpha=30000 bez wyrazu wolnego. Jakakolwiek rozbieżność względem pre-rejestracji wymaga formalnego wpisu Amendment A2 w GATES przed uruchomieniem pomiaru.
- **Zamknięcie**: Po zakończeniu pomiaru następuje weryfikacja bramek G0–G6 i formalne zamknięcie linii skryptem `close.py`. ETT przechodzi do puli Dev v2 jako część `fev-bench-mini`, z zakazem wystąpienia w Lockboxie.

---

## 2. Dane, podział zbiorów i manifest

### Podział zbiorów
- **Dev (eksploracja, dobór i strojenie)**:
  - Oficjalny podzbiór `fev-bench-mini` (20 zadań / 20 unikalnych konfiguracji / 15 rodzin datasetowych). Zero subiektywnego doboru zadań.
- **Lockbox (potwierdzenie końcowe)**:
  - 42 zadania z pełnego zbioru `fev-bench` (100 zadań) wyselekcjonowanych po **twardym odcięciu rodzeństwa**:
    - Każda rodzina datasetu obecna w Dev (15 rodzin, w tym ETT, boomlet, rossmann, hospital, epf, rohlik) jest bezwzględnie usunięta z puli Lockboxa.
    - 38 odciętych zadań pokrewnych (np. `ETT_1D`, `ETT_1W`, warianty częstotliwościowe i geograficzne) trafia do kategorii `unused_sibling_quarantine` w manifeście (zakaz użycia w jakiejkolwiek warstwie).
  - W Lockboxie pozostaje 42 niezależne zadania reprezentujące 21 rodzin.
  - **Suma kontrolna podziału**: 20 Dev + 38 kwarantanna + 42 Lockbox = 100 zadań pełnego zbioru (wartość zamrożona w `results/manifest.json`, klucz `counts`).
  - **Ograniczenie pokrycia domenowego Lockboxa**: po twardym odcięciu rodzeństwa Lockbox reprezentuje **5 z 7 domen** — `retail` (14 zadań / 7 rodzin), `energy` (13 / 4), `econ` (8 / 6), `mobility` (5 / 2), `healthcare` (2 / 2). Domeny `cloud` i `nature` nie są w Lockboxie reprezentowane, więc Bramka 3 nie może potwierdzić generalizacji w tych dwóch domenach.
- **Test integralności podziału**: Test jednostkowy weryfikuje bezwzględny brak przecięcia rodzin:
  $$\text{rodziny}(\text{Dev}) \cap \text{rodziny}(\text{Lockbox}) = \emptyset \quad \wedge \quad \text{ETT} \notin \text{Lockbox}$$

### Okna ewaluacyjne (originy)
- Wybór okien: **dokładnie ostatnie 3 okna ewaluacyjne** zadeklarowane w YAML-u danego zadania (indeksy okien `[-3:]`).
- Rygor: Wybór jest czysto deterministyczny. Liczba 3 i reguła „ostatnie” są zamrożone w manifeście.
- Ograniczenie porównywalności: Wybór 3 okien (zamiast wszystkich zadeklarowanych 5–20) oznacza częściową porównywalność z publicznym leaderboardem FEV, podyktowaną budżetem obliczeniowym.
- Konsekwencja: Temporalny lockbox na seriach dev znika — podział jest ściśle jednowymiarowy (po zadaniach/rodzinach).

### Mapowanie 7 domen FEV
- Źródło normatywne: Artykuł *fev-bench* (arXiv:2509.26468), **Appendix E, Tabela 15** (dla 20 zadań Dev) oraz **Appendix A, Tabele 6–12** (dla zadań Lockboxa).
- Klasyfikacja Dev (20 zadań / 15 rodzin):
  - `cloud` (4 zadania, 2 rodziny: BOOMLET [3], BizITObs [1])
  - `energy` (5 zadań, 4 rodziny: EPF-NP [1], ETT [2], GFC14 [1], Solar with Weather [1])
  - `healthcare` (3 zadania, 2 rodziny: Hospital Admissions [2], UK COVID [1])
  - `nature` (2 zadania, 2 rodziny: Jena Weather [1], UCI Air Quality [1])
  - `retail` (3 zadania, 2 rodziny: Rohlik [1], Rossmann [2])
  - `econ` (2 zadania, 2 rodziny: US Consumption [1], World CO2 [1])
  - `mobility` (1 zadanie, 1 rodzina: M-DENSE [1])
- Adnotacja o mocy: Domeny o liczności < 2 zadań w danej warstwie (np. `mobility` w Dev) są w raportach oznaczane jako *„sygnał, nie dowód domenowy”*.

### Zamrożenie manifestu
- Manifest (`manifest.json`) zawiera pełną listę zadań Dev i Lockbox, przypisanie rodzin i domen, indeksy ostatnich 3 okien, wartości $m$, wersję `fev 0.10.0`, wykluczone kolumny/zadania oraz listę 38 zadań kwarantanny.
- Manifest jest zamrażany kryptograficznie (`sha256`) w Fazie 1b i stanowi nienaruszalny punkt odniesienia.

---

## 3. Metryka, obsługa zer i agregacja

- **Silnik metryk**: Ścisła zgodność z biblioteką `fev 0.10.0` (`fev.metrics.MASE`, `fev.analysis.leaderboard`, `fev.analysis.pairwise_comparison`).
- **Skalowanie**: Okres sezonowości $m = \text{seasonality}$ pobierany bezpośrednio z konfiguracji YAML zadania. Brak arbitralnych tabel i brak cichych fallbacków.
- **Obsługa zer i anomalii mianownika**:
  - Mianownik MASE (in-sample seasonal error) zależy wyłącznie od historii szeregu, a nie od testowanego modelu.
  - Wszystkie serie o zerowym błędzie sezonowym (dające `inf`/`nan`) są identyfikowane **raz w Fazie 1b** na podstawie ewaluacji `Seasonal Naive` i zamrażane w `manifest.json` (jako wykluczone kolumny targetu lub unieważnione zadania).
  - Żaden przebieg testowanego modelu w Fazie 3 nie może otrzymać statusu FAIL z powodu właściwości mianownika danych.
- **Relatywizacja i obcięcie (clipping)**:
  - Model referencyjny: `Seasonal Naive` (dopasowany per-origin na historii okna).
  - Iloraz błędu per zadanie $t$: $r_t = \text{MASE}_{\text{model}, t} / \text{MASE}_{\text{SNaive}, t}$.
  - Zgodnie ze standardem FEV iloraz jest obcinany do zakresu $[0{,}01; 100{,}0]$.
- **Główny estymator (Skill Score)**:
  $$\text{skill\_score} = 1 - \left( \prod_{t=1}^{T} r_t \right)^{1/T}$$
  (Wartość $> 0$ oznacza przewagę nad Seasonal Naive).
  Dodatkowo raportowane: średnia geometryczna $r$, mediana, najgorsza domena, najgorsze zadanie i odsetek wygranych zadań ($r < 1$).

---

## 4. Trzy bramki decyzyjne

### Bramka 1: Wejście do populacji (każdy cykl)
1. Zarejestrowana karta cyklu w ledgerze przed uruchomieniem kodu.
2. Jawny falsyfikator hipotezy i uzasadnienie mechanizmu.
3. Brak FAIL budżetu czasu (timeouty $\le 2\%$ wszystkich dopasowań).
4. Wskazanie usuwanej metody (`replaces`), jeśli populacja osiągnęła $N=8$.

### Bramka 2: Promocja na Championa (rzadko)
1. **Niestratyfikowany bootstrap klastrowy po 15 rodzinach datasetów**:
   - Resampling: losowanie ze zwracaniem $B = 10\,000$ prób klastrowych na poziomie **rodzin datasetów** (zadania w ramach rodziny wchodzą do próby łącznie, zapobiegając zaniżaniu wariancji przez skorelowane dane i kalendarze).
   - Kontrast liczony względem dotychczasowego Championa:
     $$\text{skill\_score}(M \text{ vs Champion}) = 1 - \text{gmean}\left(\frac{\text{MASE}_M}{\text{MASE}_{\text{Champion}}}\right)$$
   - Kryterium: **dolna granica jednostronnego 95% CI > 0** (istotność na poziomie $\alpha = 0{,}05$).
2. **Twarde punktowe filtry domenowe (bez wyjątków)**:
   - Żadna domena nie może wykazać pogorszenia geometrycznego: $\text{gmean}_{t \in d}(M_t / \text{Champion}_t) \le 1{,}05$ (+5%).
   - Co najwyżej jedno zadanie w całym Dev może mieć pogorszenie punktowe $M_t / \text{Champion}_t > 1{,}20$ (+20%).
   - Domeny niepokryte w Dev (jeśli występują) są oznaczane jako niepokryte, a nie jako zaliczone.
3. **Analiza wrażliwości (Sensitivity)**:
   - Równolegle w raporcie przedstawiany jest bootstrap stratyfikowany oraz surowy bootstrap i.i.d. po zadaniach z FEV. O werdykcie decyduje wyłącznie wariant klastrowy po rodzinach.

### Bramka 3: Ewaluacja w Lockboxie (wyłącznie po pomyślnej promocji)
1. **Zasada pojedynczego wykonania**: Lockbox uruchamiany jest wyłącznie dla nowo promowanego Championa.
2. **Kontrast względem poprzedniego Championa**:
   - Wynik w Lockboxie liczony jest jako bezpośredni kontrast względem poprzedniego championa (dla pierwszego kandydata punktem odniesienia jest `DLinear`).
   - Obie metody są dopasowywane i ewaluowane przez ten sam zapieczętowany skrypt w jednym przebiegu.
   - Skrypt wypisuje wyłącznie **kontrast z przedziałem ufności bootstrapu**; absolutne wyniki referencji na Lockboxie nigdy nie są pokazywane ani liczone osobno.
3. **Poziom istotności i kontrola FWER**:
   - Ze względu na limit 3 użyć Lockboxa, na każde użycie (w tym pierwsze) obowiązuje stały poziom istotności Bonferroniego:
     $$\alpha_{\text{lockbox}} = \frac{0{,}05}{3} \approx 0{,}01667 \quad (\text{jednostronny przedział ufności } 98{,}33\%)$$
   - Kryterium: dolna granica 98,33% CI dla kontrastu $> 0$ w klastrowym bootstrapie po 21 rodzinach Lockboxa.
   - Obok wyniku raportowana jest liczba sprawdzonych wariantów dev w danym cyklu ($M$) oraz łączny licznik prób dev od początku projektu.

---

## 5. Zarządzanie populacją ($N \le 8$)

- **Pojemność**: $N \le 8$ aktywnych metod.
- **Role w populacji**:
  - `champion` (aktualny lider benchmarku).
  - `anchor` (nieusuwalne kotwice z literatury: `DLinear`, `NLinear`).
  - `challenger` (metody, które weszły do populacji, lecz nie pobiły championa).
  - `experiment` (aktywne hipotezy badawcze).
- **Rola łączona**: Dopuszczalne jest pełnienie przez jedną metodę roli `champion + anchor` (np. startowy `DLinear`). Populacja startowa w Fazie 2 liczy $N = 2$ metody: `DLinear` (champion + anchor) oraz `NLinear` (anchor).
- **Punkt odniesienia**: `Seasonal Naive` stanowi referencję metryki, nie jest członkiem populacji i nie zajmuje slotu.
- **Zasada warunkowej eksmisji**:
  - Przy $N = 8$ karta cyklu wskazuje `replaces: "nazwa_metody"` (zakaz wskazywania anchorów oraz aktualnego championa).
  - Wskazana metoda zostaje usunięta z aktywnej populacji wyłącznie wtedy, gdy kandydat zostanie przyjęty (`adopt`).
  - W przypadku odrzucenia (`reject`), przekroczenia budżetu (FAIL) lub zaparkowania (`park`), wskazana metoda **pozostaje w populacji nienaruszona**.

---

## 6. Budżet czasu i infrastruktura

- **Środowisko obliczeniowe**: 16 GB RAM, CPU, 4 procesy robocze, 1 wątek na proces. Zakaz uruchamiania innych ciężkich zadań w tle.
- **Budżet wykonawczy Dev**:
  - Twardy limit ściany (wall-clock): **20 minut na pojedynczą metodę na cykl**.
  - Jednostka rozliczeniowa budżetu: **kolumna targetu $\times$ okno**. Dev ma 247 kolumn targetu (20 zadań, w tym zadania wielowymiarowe) $\times$ 3 okna = **741 jednostek** (zweryfikowane kolumna po kolumnie wobec `manifest.json`).
  - Ujawnienie skali itemowej: te 247 kolumn niesie łącznie **2 767 serii (itemów)**; na poziomie itemu $\times$ okno daje to 8 301 ewaluacji. Liczba 741 pozostaje jednostką progu awarii, ponieważ fev liczy MASE jako średnią po itemach w obrębie kolumny, a próg $2\%$ dotyczy przebiegów modelu, nie pojedynczych serii.
  - Twardy timeout na dopasowanie: 30 sekund.
  - Obsługa timeoutu: w przypadku przekroczenia 30 s dopasowanie zostaje przerwane, a w miejsce wyniku podstawia się **maksymalną karę błędu: $r = 100$** (górny clip FEV; podstawienie $r=1$ jest zabronione, gdyż nagradzałoby modele gorsze od SNaive).
  - Dopuszczalny próg awarii: przekroczenie $> 2\%$ porażek (liczonych od łącznej liczby dopasowań: $> 14$ z 741) oznacza natychmiastowy status FAIL dla danego przebiegu.
- **Budżet wykonawczy Lockboxa**:
  - Szacowany budżet ściany dla 42 zadań Lockboxa zostaje ustalony i zamrożony w Fazie 1b na podstawie suchego przebiegu.

---

## 7. Ledger append-only

- **Format**: `ledger.jsonl`, zapis wyłącznie za pośrednictwem skryptu orkiestratora.
- **Kryptograficzny łańcuch hashy**:
  - Każdy rekord zapisywany jest w kanonicznym JSON (klucze posortowane alfabetycznie, separatory `","` i `":"`, kodowanie UTF-8).
  - Pole `"prev_sha256"` zawiera SHA-256 bajtów poprzedniego wiersza w pliku.
  - Blok Genesis (wiersz 0): zawiera `"prev_sha256": null` oraz `"manifest_sha256": "<hash zamrożonego manifest.json>"`.
  - Integralność łańcucha jest weryfikowana testem jednostkowym w CI.
- **Typy wpisów w ledgerze**:
  1. `cycle_card` — prerejestracja zamiaru badawczego przed uruchomieniem kodu (rodzic, zmiana, falsyfikator, budżet, wskazanie `replaces`).
  2. `run_result` — podsumowanie przebiegu Dev, metryki zagregowane, czasy, werdykt (`adopt` / `reject` / `park`) oraz `artifact_sha256` wskazujący na plik ze szczegółowymi wynikami 741 dopasowań.
  3. `lockbox_registration` — zamrożenie commita z kodem kandydata promowanego do Lockboxa.
  4. `lockbox_result` — pojedynczy wynik z Lockboxa (kontrast i CI).
  5. `amendment` — formalna zmiana protokołu badawczego z uzasadnieniem.
- **Znacznik czasu**: Każdy wpis w ledgerze stanowi osobny commit git wypchnięty do zdalnego repozytorium (`git push`).

---

## 8. Protokół lockboxa i zasady pieczętowania

- **Zasada jawności**: Dane zbioru FEV są publiczne na HuggingFace. Protokół wprost uznaje, że techniczne zablokowanie pobrania danych jest niemożliwe. Integralność opiera się na separacji procesowej, dyscyplinie commit-then-reveal oraz niezależnym audycie.
- **Mechanizm weryfikacji**:
  1. Zamrożenie kandydata w commicie git po zaliczeniu bramki promocji na Dev.
  2. Rejestracja wpisu `lockbox_registration` w ledgerze.
  3. Uruchomienie dedykowanego skryptu ewaluacyjnego posiadającego listę 42 zadań Lockboxa.
  4. Skrypt oblicza równolegle dopasowania kandydata i poprzedniego Championa, wypisując wyłącznie **kontrast ze statystyką bootstrapu**.
  5. Rejestracja wyniku wpisem `lockbox_result`.
- **Budżet i degradacja (spalenie Lockboxa)**:
  - Twardy limit: **dokładnie 3 użycia Lockboxa w całym projekcie**.
  - Każde uruchomienie (niezależnie od wyniku) bezwzględnie zużywa 1 próbę.
  - Kontrola istotności: stałe $\alpha = 0{,}01667$ (98,33% jednostronne CI).
  - Po 3. użyciu Lockbox ulega bezpowrotnemu spaleniu. W przypadku braku sukcesu projekt traci możliwość formułowania twierdzeń konfirmacyjnych, a metody degradują się do statusu *„dev-only, bez potwierdzenia”*.

---

## 9. Rola agenta i audyt niezależny

- **Dyscyplina agenta**:
  - Agent proponuje hipotezy, pisze kod metod, zarządza populacją Dev.
  - Agent **ma bezwzględny zakaz wglądu w dane Lockboxa**, pliki zadań Lockboxa oraz uruchamiania modeli na zadaniach spoza Dev.
  - Agent nie podejmuje autonomicznych decyzji o modyfikacji bramek ani manifestu.
- **Niezależny audyt proceduralny**:
  - Realizowany w **świeżej sesji agenta pozbawionej dotychczasowej pamięci i kontekstu rozmowy**.
  - Wejście: wyłącznie zamrożone artefakty na dysku (`ledger.jsonl`, `manifest.json`, commity git, logi).
  - Rubryka audytowa weryfikuje:
    1. Spójność łańcucha kryptograficznego ledgera (`prev_sha256`).
    2. Chronologię wpisów (`cycle_card` zawsze przed `run_result`).
    3. Przestrzeganie bramek decyzyjnych i limitów budżetu czasu.
    4. Brak w kodzie odwołań do zbiorów Lockboxa i zadań kwarantanny.
  - Wynik: lista ewentualnych zarzutów dowodowych; audytor nie wydaje werdyktów uznaniowych.

---

## 10. Reguły STOP projektu

Orkiestrator automatycznie przerywa cykl eksperymentalny i przekazuje sterowanie człowiekowi w przypadku wystąpienia **któregokolwiek** z poniższych warunków:
1. **Sukces potwierdzony**: Kandydat pomyślnie przechodzi ewaluację w Lockboxie z zachowaniem $\alpha = 0{,}01667$.
2. **Wyczerpanie Lockboxa**: Wykonano 3 ewaluacje w Lockboxie.
3. **Stagnacja Dev**: 6 kolejnych cykli badawczych bez wyłonienia Championa przechodzącego promocję. (Promocja zeruje licznik; odrzucenie w Lockboxie **nie zeruje** licznika).
4. **Twardy bezpiecznik cykli**: Osiągnięcie 20 cykli łącznie od startu projektu (ochrona przed nieskończonym resetowaniem stagnacji marginalnymi zmianami).

Wznowienie pracy po zatrzymaniu wymaga wpisu typu `amendment` w ledgerze, zatwierdzonego przez człowieka.

---

## 11. Raportowanie (`report.py`)

- Skrypt generuje pojedynczy, autonomiczny dashboard HTML odczytywany wyłącznie z `ledger.jsonl` i powiązanych artefaktów JSON.
- W nagłówku: hash ledgera, commit HEAD, wersja `fev 0.10.0`, liczniki cykli, zużycie lockboxa i poziom stagnacji.
- Panele raportu:
  1. *Panel świateł (Traffic Light)*: Macierz Metoda $\times$ Domena ze stanem zysku/straty.
  2. *Forest Plot*: Prezentacja estymatorów punktowych i przedziałów ufności bootstrapu vs Champion i vs SNaive.
  3. *Tabela populacji*: Prezentacja metod posortowana według pełnionej **roli** (`champion`, `anchor`, `challenger`, `experiment`), a nie chwilowego wyniku na Dev.
  4. *Panele izolowane*: Wyniki Lockboxa oraz historyczne wyniki ETTh1 zaprezentowane w odrębnych sekcjach z wyraźnymi bannerami metodologicznymi.

---

## 12. Pozycja GIFT-Eval

- Benchmark zewnętrzny GIFT-Eval nie bierze udziału w pętli optymalizacyjnej, strojeniu ani selekcji modeli.
- Może zostać uruchomiony wyłącznie jednorazowo, po pomyślnym zakończeniu projektu (zaliczeniu Lockboxa), z deduplikacją serii po hashu danych.
- Jakiekolwiek wcześniejsze użycie unieważnia status GIFT-Eval jako niezależnego testu transferu zewnętrznego.

---

## 13. Jawne ograniczenia statystyczne

1. **Wybór wielokrotny na Dev**: Selekcja kandydata spośród wielu eksperymentów obciąża estymator optymizmem. Rzeczywisty stopień eksploracji jest transparentnie raportowany parametrem $M$ (liczba wariantów cyklu) oraz globalnym licznikiem prób Dev obok każdego wyniku Lockboxa.
2. **Moc wnioskowania wąskodomenowego**: Ze względu na obecność 2–5 zadań w poszczególnych domenach Dev, filtry domenowe chronią przed katastrofalnym pogorszeniem, lecz nie stanowią ostatecznego dowodu adaptacji wąskodomenowej.
3. **Reprezentacja domeny Mobility**: W podzbiorze Dev domena `mobility` reprezentowana jest przez 1 zadanie (`M-DENSE`), co stanowi jawne ograniczenie bramki domenowej w tej domenie.

---

## 14. Kolejność wdrożenia i Definition of Done (DoD)

### Faza 0: Domknięcie ETTh1 H720 (otwarta)
- [ ] Zabezpieczenie `$env:TEMP\s44_calib.log` do `projects/research/etth1-h720/results/s44_calib_insample_failed.log` wraz z obliczeniem sha256.
- [ ] Uzupełnienie `GATES-s44-calibration.md` o status 1,7229 (wartość historyczna z nieważnego wariantu in-sample).
- [ ] Weryfikacja zgodności parametrów S49 (12 originów, seed set 42–46); w razie jakichkolwiek różnic wpis Amendment A2.
- [ ] Uruchomienie właściwej kalibracji out-of-sample S44 i weryfikacja bramek G0–G6.
- [ ] Formalne zamknięcie linii ETTh1 H720 skryptem `close.py`.
- **DoD**: `python scripts/close.py --verify-claims` przechodzi z kodem 0; tree czyste.

### Faza 1: Protokół i fundamenty techniczne (greenfield)
- [ ] Zapisanie niniejszego pliku jako `projects/research/benchmark-core/PROTOCOL.md`.
- [ ] Implementacja modułów bazowych i testów jednostkowych:
  1. `manifest.py` (struktura zadań, rodziny, odcięcie rodzeństwa, 3 ostatnie okna, mapowanie domen).
  2. `metrics.py` (kalkulacja MASE, clipping FEV, obsługa zer/NaN, $m = \text{seasonality}$).
  3. `bootstrap.py` (niestratyfikowany klastrowy bootstrap po 15 rodzinach, $B = 10\,000$, jednostronny test istotności).
  4. `ledger.py` (append-only JSONL, kanoniczny JSON, weryfikacja łańcucha sha256, typy wpisów).
  5. `guards.py` (budżet czasu 20 min, timeout 30 s z podstawieniem $r=100$, monitor FAIL $> 2\%$ dopasowań).
- **DoD**: `pytest` zielony dla wszystkich testów jednostkowych.

### Faza 1b: Suchy przebieg, analiza mocy i zamrożenie
- [ ] Uruchomienie suchego przebiegu baseline'ów (`Seasonal Naive`, `NLinear`, `DLinear`) na Dev.
- [ ] Rozstrzygnięcie zerowych mianowników MASE na podstawie SNaive i zapisanie wykluczeń do manifestu.
- [ ] Pomiar średniego czasu i p95 per zadanie (szczególnie `boomlet_1676`).
- [ ] Wyznaczenie naturalnej zmienności zadań między oknami i ewentualna korekta filtrów (+5% / +20%).
- [ ] **Analiza mocy i MDE**: bootstrap `NLinear` vs `DLinear` na Dev w obu wariantach i wyznaczenie szerokości CI (Minimalny Wykrywalny Efekt przy $\alpha = 0{,}05$ na Dev i $\alpha = 0{,}01667$ na Lockboxie). Ewentualna decyzja o liczbie okien w Lockboxie przed zamrożeniem.
- [ ] Ustalenie budżetu ściany dla Lockboxa (42 zadań).
- [ ] Kryptograficzne zamrożenie `manifest.json` (`sha256`) i inicjalizacja `ledger.jsonl` blokiem Genesis.
- **DoD**: Manifest zamrożony, test integralności przechodzi.

### Faza 2: Środowisko eksperymentalne i dashboard
- [ ] Zapisanie w cache wyników bazowych (`Seasonal Naive`, `NLinear`, `DLinear`).
- [ ] Inicjalizacja populacji startowej ($N=2$: `DLinear` jako champion+anchor, `NLinear` jako anchor).
- [ ] Implementacja dashboardu HTML `report.py`.
- **DoD**: `python report.py` generuje poprawny dashboard z populacją początkową.

### Faza 3: Cykle badawcze i ewaluacja końcowa
- [ ] Pętla iteracyjna z rejestracją kart cyklu (`cycle_card`).
- [ ] Weryfikacja bramek wejścia, warunkowa rotacja populacji ($N \le 8$).
- [ ] Promocja na Championa w klastrowym bootstrapie po rodzinach.
- [ ] W przypadku wyłonienia stabilnego Championa: zapieczętowana ewaluacja w Lockboxie ($\alpha = 0{,}01667$) względem poprzedniego Championa.
- [ ] Kontrola warunków STOP (sukces / 3 użycia lockboxa / 6 cykli stagnacji / 20 cykli łącznie).
- **DoD**: Niezależny audyt proceduralny w świeżej sesji agenta i raport końcowy.

---

## 15. Rejestr poprawek (Amendment register)

Protokół jest zamrożony kryptograficznie; każda zmiana normatywna wymaga wpisu `amendment` w `ledger.jsonl`. Poniższa tabela jest czytelnym dla człowieka widokiem tych wpisów; w razie konfliktu rozstrzyga ledger.

| # | Data | Sekcje | Zmiana | Dowód |
|---|---|---|---|---|
| A1 | 2026-11-01 | §2, §4, §6, §8 | Lockbox **46 → 42** zadania; kwarantanna **30 → 38** zadań; rodziny Lockboxa **24 → 21** | Pomiar na `results/manifest.json` (sha256 `34b35abc…b42da`): 20 Dev + 38 kwarantanna + 42 Lockbox = 100. Pierwotne liczby były oszacowaniem sprzed zbudowania manifestu. |
| A2 | 2026-11-01 | §6 | „20 zadań × 3 okna = 741 dopasowań" → „247 kolumn targetu × 3 okna = 741 jednostek"; dodano skalę itemową (2 767 serii; 8 301 ewaluacji item × okno) | Równanie 20 × 3 = 741 było arytmetycznie błędne; 741 zweryfikowano dokładnie kolumna po kolumnie wobec manifestu. |
| A3 | 2026-11-01 | §2 | Dodano ograniczenie pokrycia domenowego Lockboxa: **5 z 7 domen** (brak `cloud`, `nature`) | Konsekwencja twardego odcięcia rodzeństwa; pomiar z manifestu (retail 14/7, energy 13/4, econ 8/6, mobility 5/2, healthcare 2/2). |
| A4 | 2026-11-01 | §3 | Rozstrzygnięcie mianowników MASE w Fazie 1b: **0 itemów z zerowym błędem sezonowym, 0 itemów z NaN** na wszystkich 20 zadaniach Dev — brak wykluczeń w manifeście | `results/denominator_anomaly_scan.json`: skan 20/20 zadań, per-item, zgodny z `fev.metrics._seasonal_error_per_item`. Pierwsza wersja skanera nie iterowała po `datasets.Column` (traktowała całą kolumnę jako jeden item) i została poprawiona **przed** zamrożeniem; wiążący jest wynik poprawiony. |

**Status zamrożenia**: `manifest_sha256 = 34b35abc12652a43306b9c976d007a6fa70762c13ec32e039b933180936b42da`. Wszystkie liczby w §2, §4, §6 i §8 pochodzą z tego pliku; odpowiadające wpisy `amendment` A1–A4 są zapisane w `ledger.jsonl` bezpośrednio po bloku Genesis.
