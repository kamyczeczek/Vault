---
type: Concept
title: answer2
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

### 1. Co realnie działa i warto przenieść

* **Architektura kontekstu ICM (warstwy L0–L4 i jawne punkty handoffu):**
  * **Dlaczego działa:** Zapewnia pełną obserwowalność stanu systemu bez narzutu frameworków („observability by default” – stanem jest struktura katalogów i plików Markdown) [1]. W roocie i podprojektach doskonale sprawdza się podział na:
    * **L0:** zwięzły router (`AGENTS.md`, <2K tokenów) [2, 3],
    * **L1/L2:** kontrakty i mapy ładowane wyłącznie na żądanie (`CONTEXT.md`, `MAP.md`) [4, 5],
    * **L4:** bezstanowe punkty przekazywania pracy między agentami (`HANDOFF.md`, flagi w `handoff/flags/`) [5-7].
  * **Co przenieść:** Wzorzec dyscypliny kontekstowej L0–L4 oraz zasadę konfiguracji środowiska zamiast sterowania produktem (*configure the factory, not the product*) [6].

* **Niezmienniki i deterministyczne bramki z testami mutacyjnymi (Quality Gates):**
  * **Dlaczego działa:** Bramki sprawdzające twarde relacje w strukturze plików (np. `check_workspace_integrity.py` w roocie jako Q0, `check_citation_integrity.py` jako Q16 czy `check_graph_determinism.py` jako Q17) skutecznie blokują błędy regresyjne [8-10].
  * **Kluczowa reguła:** Każda bramka musi być **przetestowana mutacyjnie** przed wdrożeniem (musi udowodnić, że potrafi zakończyć się kodem błędu `exit != 0` przy typowej pomyłce) [10].
  * **Co przenieść:** Egzekwowanie bramek przez natywny mechanizm Gita (`git config core.hooksPath hooks`) zamiast nieformalnych konwencji w dokumentacji [11-13].

* **Higiena repozytorium i separacja pochodnego korpusu (Decyzja D5 / ADR-0003):**
  * **Dlaczego działa:** Trzymanie wygenerowanych chunków w systemie kontroli wersji prowadziło do puchnięcia repozytorium (z 10 939 plików zredukowano śledzenie do 602) [14, 15].
  * **Co przenieść:** Architekturę, w której surowe źródła są trzymane w dedykowanej bibliotece (`library/`) adresowanej haszami treści (z ignorowaniem binariów i wersjonowaniem indeksu `index.json`) [14, 15], natomiast pochodne bazy i chunki (np. `graph.db`, `memory.db`, `knowledge/corpus/`) są odpięte z Gita i deterministycznie odtwarzane ze źródeł [9, 15, 16].

* **Rygor ewaluacji z mechanizmem `echo-guard`:**
  * **Dlaczego działa:** Odrzuca metryki tautologiczne na rzecz obiektywnych faktów semantycznych [17, 18]. Walidator `score_ablation_content.py` automatycznie odrzuca wzorce będące powtórzeniem pytania (`echo pattern`) oraz fakty niesprowadzalne do materiału wzorcowego (*oracle chunks*) [18].
  * **Co przenieść:** Wzorzec ewaluatora regex z filtrem antystronniczym do wszelkich zadań weryfikacji groundingów w innych projektach [18].

---

### 2. Co nie działa (anty-wzorce i ślepe uliczki)

* **Rozbudowa grafu o hybrydowe embeddings i grafy relacyjne bez zysku z retrievalu:**
  * **Dlaczego nie działa:** W testach na korpusie retrieval FTS5 osiągał pokrycie na poziomie 0.958, a próby wdrażania hybrydowych wektorów embeddings dały zmierzoną wartość 0.0 przy jednoczesnym wzroście skomplikowania [10]. Próby wdrażania krawędzi semantycznych `REFERS_TO` czy przyrostowego przebudowywania grafu zwiększały ryzyko naruszenia determinizmu bez rozwiązania problemu relacyjnego zakłamania [10].

* **Integracje narzędziowe MCP dla autonomicznych agentów (Phase 2b Goose x graf-MCP):**
  * **Dlaczego nie działa:** Ślepa uliczka infrastrukturalna. W Phase 2b integracja Goose z serwerem MCP skończyła się deadlockami na parametrze `--with-extension`, martwą konfiguracją i brakiem możliwości testowania narzędzia, przez co autonomia agenta i tak musiała uciekać do kanału shella [17].

* **Metryki tautologiczne i ocena przez pryzmat tożsamości narzędzia:**
  * **Dlaczego nie działa:** Pierwszy pomiar pilota Phase 2 (wynik ON 9/9 vs OFF 0/9) mierzył jedynie obecność identyfikatorów chunków, których ramię bazowe z definicji nie mogło podać [17, 18]. Podobny defekt miał stary harness `memory_eval.py`, który fałszywie raportował błędy przez brak filtru typów i cichy fallback z AND do OR w FTS5 [12, 19, 20].

* **Syntetyczny, niekontrolowany meta-learning i autonomiczne pętle refleksji:**
  * **Dlaczego nie działa:** Generowanie „łatek naprawczych” przez LLM bez ludzkiego nadzoru zostało odrzucone jako powierzchowny mechanizm zafałszowujący wskaźniki (prawo Goodharta) [21]. Analiza śladów (`eval_traces.py`) wykazała, że autonomiczne procesy refleksji produkowały aż 66,7% osieroconych decyzji (`orphan-decision rate 0.667`) i 84,6% pustych wywołań retrievalu (`dry-retrieval rate 0.846`) [22].

* **Narzędzia guardrailowe na zbyt prostych zadaniach (Forge A/B):**
  * **Dlaczego nie działa:** W teście Forge A/B (15 przebiegów/ramię) wstrzyknięcie guardraili ratunkowych dało wynik 14/15 vs 14/15, ponieważ bazowy model osiągał ~93% skuteczności [17, 23]. Zastosowanie guardraili na trywialnym zadaniu nie przynosi żadnego liftu, a jedynie mierzy efekt sufitu [17, 23].

---

### 3. Co jest nierozstrzygnięte i jak tanio to rozstrzygnąć

| Mechanizm | Stan faktyczny / nierozstrzygnięcie | Tani, falsyfikowalny krok weryfikacyjny |
| :--- | :--- | :--- |
| **Wpływ grafu wiedzy FTS5 na decyzje agenta (Hipoteza B)** | Wynik pilota po wdrożeniu obiektywnych 25 faktów to **INCONCLUSIVE** (ON: 0.380 vs OFF: 0.222) [17, 18]. Ramię ON wygrało wyraźnie tylko w kategorii `bug-fix` (0.833 vs 0.278) [17, 18]. W kategorii `perf` wynik wynosił zaledwie 0.083, lecz mogło to wynikać ze sztucznego dławienia wstrzykiwanego kontekstu limitem 2500 znaków [18, 24]. | **Deterministyczny re-scoring 4 zadań rodziny `perf` przy buforze rozszerzonym do 8000 znaków:** Uruchomić generator tylko dla tych 4 zadań i przeliczyć wynik istniejącym skryptem `score_ablation_content.py` [18, 24]. **Kryterium:** Jeśli wynik ON nie wzrośnie z 0.083 do \\(\ge 0.400\\), hipoteza o wartości grafu upada i należy zrezygnować z kosztownego badania \\(n \ge 25\\) [17, 24]. |
| **Pętla wykonawcza Ralph-loop (Reviewer LLM vs Bramka deterministyczna)** | W eksperymencie c2 wykazano, że recenzent LLM dziedziczy halucynacje agenta wykonawczego, a ocena negatywnej próby kontrolnej pływała (dawała wynik 0.50 przed ręcznym dostrojeniem) [25]. Choć wdrożono hybrydę c3 (recenzent LLM zatrzymuje pętlę, a bramka jest doradcza) [26], nie rozstrzygnięto, czy recenzent LLM przewyższa czysto deterministyczny kontrakt bramek logicznych [25, 27]. | **Porównawczy micro-run (3 iteracje zadania naprawczego):** Sprawdzić zachowanie pętli w trybie deterministycznym (zatrzymanie wyłącznie na podstawie kodu wyjścia z testu) vs recenzent LLM [25, 26]. Zmierzyć liczbę zużytych tokenów oraz ryzyko przedwczesnego zatwierdzenia błędnego kodu (*false SHIP*) [26]. |
| **Praktyczna użyteczność pamięci sesji (`scripts/memory/`)** | Baza FTS5 działa bezbłędnie technicznie (101k chunków, test `eval_memory_retrieval.py` przechodzi 15/15) [28-30]. Jednak telemetria wykazała, że agenci w ogóle z niej nie korzystają (zaledwie 6 zapytań debugowych w historii i wskaźnik zapobiegania powtórkom błędów `prevented_repeat: 0/7`), ponieważ odpytanie bazy opiera się na biernej konwencji w `AGENTS.md` [7, 19, 31, 32]. | **Wymuszenie twardego hooka na błędzie:** Zamiast zapisu w dokumentacji, dodać automatyczne wywołanie `scripts/debug.py` po drugim nieudanym poleceniu w sesji roboczej [19, 33]. Po 10 sesjach sprawdzić w `memory_index.py stats --usage`, czy `prevented_repeat` wzrośnie powyżej zera [32]. |

---

💡 *Czy chcesz, abym przygotował gotowy skrypt weryfikacyjny (Python/bash) pod re-scoring 4 zadań rodziny `perf` ze zwiększonym limitem 8000 znaków?*