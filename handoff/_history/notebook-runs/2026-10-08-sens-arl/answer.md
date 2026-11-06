---
type: Concept
title: answer
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

### 1. Czy kontynuować projekt i w jakiej formie?
* **Werdykt:** **TAK, ale wyłącznie w ściśle zawężonej, warunkowej formie eksperymentu weryfikacyjnego (zamrożenie rozbudowy infrastruktury i korpusu)** [1, 2].
* **Uzasadnienie (odróżnienie wyniku negatywnego od braku wyniku):**
  * Wynik pilota Phase 2 to **brak wyniku (INCONCLUSIVE)**, a nie dowiedziony rezultat negatywny [1, 3]. Próba o wielkości \\(n=9\\) par nie posiadała mocy statystycznej (rzetelny test wymaga \\(n \ge 25\\)) [1, 2, 4].
  * Pierwszy pomiar pilota (ON 9/9 vs OFF 0/9) był tautologiczny, ponieważ zaliczenie zadania wymagało podania identyfikatorów chunków, których ramię bazowe (OFF) z definicji nie mogło znać [1, 3]. Dopiero w sesji B wdrożono właściwe kryterium merytoryczne (25 niezależnych faktów z oracle chunks wraz z filtrem `echo-guard`) [1, 3]. W tym ujęciu ramię ON osiągnęło wynik makro **0.380 vs 0.222** dla OFF, wygrywając zdecydowanie w rodzinie zadań `bug-fix` (**0.833 vs 0.278**) [1, 3].
  * Jednocześnie próby rozbudowy narzędziowej ugrzęzły w problemach technicznych: w Phase 2b integracja Goose x graf-MCP okazała się ślepą uliczką (deadlocki, inert config, brak testowalności narzędziowej) [1], a test Forge A/B (15/ramię) nie przyniósł liftu (14/15 vs 14/15) przez efekt sufitu na zbyt trywialnym zadaniu z bazową skutecznością ~93% [1, 5].
* **Forma kontynuacji:** Całkowite zamrożenie powiększania grafu (liczącego już ponad 10k węzłów i 13k krawędzi) oraz pisania nowych adapterów [1]. Projekt należy ograniczyć do pojedynczego pomiaru falsyfikującego hipotezę B [4, 6]. Jeśli rozszerzony test nie wykaże przewagi, projekt należy zarchiwizować [2, 7].

---

### 2. Ranking workstreamów (a, b, c, d) z uzasadnieniem

| Pozycja | Workstream | Oczekiwany zysk badawczy i uzasadnienie |
| :--- | :--- | :--- |
| **1.** | **(a) Extended-n rerun hipotezy B** (\\(n \ge 25\\) par + szerszy budżet kontekstu \\(2500 \to 8000\\) znaków) [2, 4] | **NAJWYŻSZY.** Bezpośrednio adresuje sedno pytania badawczego [1, 6]. Istnieje już gotowy, deterministyczny ewaluator `score_ablation_content.py` przetestowany mutacyjnie [3]. Próba \\(n \ge 25\\) zapewnia 80% mocy statystycznej dla testu parowanego, a zwiększenie bufora likwiduje sztuczne dławienie gęstych odpowiedzi [4]. |
| **2.** | **(d) Zamknięcie/adnotacja jako research-prototype** [2] | **DRUGI.** W przypadku braku zasobów na krok (a) lub jego negatywnego wyniku, jest to optymalny ruch inżynierski [2]. Zbudowany korpus, graf oraz wnioski metodologiczne (np. mechanizmy `echo-guard` i unikanie metryk tautologicznych) są udokumentowane [1, 3]. Przeniesienie do katalogu `projects/_archive/` uchroni workspace przed długiem utrzymaniowym bez utraty wiedzy [7]. |
| **3.** | **(b) Phase 4-diversity** (enforcement różnorodności cytowań) [2] | **NISKI.** Regulowanie entropii cytowań (udziału top-3 chunków) stanowi optymalizację metryki wtórnej [6]. Wymuszanie różnorodności przed udowodnieniem, że wstrzykiwany kontekst w ogóle podnosi poprawność faktograficzną, grozi ukaraniem modelu za korzystanie z najbardziej trafnych źródeł [1, 6]. |
| **4.** | **(c) Phase 2c** (shell-injection jako kanał autonomii) [2] | **NAJNIŻSZY / ANTY-WZORZEC.** Skupia się na obchodzeniu ograniczeń harnessu zamiast na metodologii [1]. Doświadczenia z Phase 2b pokazały, że walka z deadlockami infrastruktury pochłania całe sesje robocze bez generowania wartości naukowej [1]. |

---

### 3. Najsłabsze ogniwo metodologiczne
* **Werdykt:** **Zbyt wąski budżet kontekstu (2500 znaków) w połączeniu z brakiem mocy statystycznej (\\(n=9\\))** [1, 2, 4].
* **Dlaczego:**
  * Kryterium ewaluacji zostało poprawnie naprawione w sesji B: odrzucono tautologiczny wymóg znajomości chunk-ID na rzecz 25 obiektywnych faktów semantycznych z testami antystronniczymi (`echo-guard`) [1, 3].
  * Rzeczywistą deformacją metodologiczną okazał się **limit 2500 znaków** [2, 4]. W rodzinie zadań wydajnościowych (`perf`) ramię ON osiągnęło średni wynik zaledwie **0.083**, ponieważ kluczowe fakty z oracle chunks fizycznie nie mieściły się w tak ciasnym buforze [3, 4]. Zmierzono więc artefakt ucięcia tekstu (truncation artifact), a nie rzeczywistą wartość poznawczą grafu [4].

---

### 4. Jeden tani, falsyfikowalny następny krok (<1 sesji roboczej)
* **Krok:** **Deterministyczny re-scoring rodziny `perf` przy buforze kontekstu rozszerzonym z 2500 do 8000 znaków na istniejącym zbiorze zadań (bez uruchamiania pełnego \\(n=25\\))** [2, 4].
* **Sposób wykonania:**
  1. Wybrać 4 zadania z rodziny `perf` z benchmarku Phase 2 [4].
  2. Wygenerować odpowiedzi dla ramienia ON ze zwiększonym limitem wstrzykiwanego kontekstu do 8000 znaków [2, 4].
  3. Przeliczyć wynik za pomocą gotowego skryptu `scripts/score_ablation_content.py` bez konieczności ponownego scoringu całego zbioru [3].
* **Kryterium falsyfikacji:**
  * Jeśli przy 8000 znaków wynik ramienia ON w rodzinie `perf` **nie wzrośnie z poziomu 0.083 do co najmniej 0.400**, hipoteza o „dławieniu przez zbyt wąski budżet” upada, a graf nie dostarcza przydatnych faktów operacyjnych [3, 4].
  * W takim scenariuszu natychmiast anulujemy plan kosztownego badania \\(n \ge 25\\) i wdrażamy **workstream (d)** – formalną archiwizację projektu do `projects/_archive/agentic-research-lab/` [2, 7].

---

💡 *Czy chcesz przygotować gotowy szablon uruchomieniowy pod ten eksperyment re-scoringowy dla rodziny `perf`, uwzględniający regułę promocji ustaleń do ADR lub flagi handoffu?*