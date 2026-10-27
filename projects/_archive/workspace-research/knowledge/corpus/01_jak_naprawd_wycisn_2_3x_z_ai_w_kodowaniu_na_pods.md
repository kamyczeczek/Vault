---
type: Concept
id: 01_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods
title: "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym).md (part 2/3)"
source: "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym).md"
tags: [agentic, agents, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Jak uzyskać lepszy output?**
1.  **Sub-agenci jako MapReduce:** To najskuteczniejsza technika. Zamiast karmić głównego agenta milionem tokenów kodu źródłowego, wyślij sub-agenta, aby przeczytał repozytorium i wrócił z 50-tysięcznym streszczeniem. Izolujesz "czytanie" od "myślenia".
2.  **Świadomość kompakcji:** Automatyczne streszczanie konwersacji (compaction) poprawia się, ale nadal jest czarną skrzynką. Jeśli zależy Ci na kontroli, każ agentowi zapisać kluczowe ustalenia do pliku Markdown i sam przejrzyj ten plik, zanim rozpoczniesz nową sesję. Daje Ci to pewność, że agent nie "zapomniał" o krytycznym wymogu biznesowym.

#### 3. Pętle Weryfikacji (Backpressure)

To chyba najważniejsza technika pozwalająca na "zostawienie agenta samego". Horthy mówi, że jedynym sposobem, aby agent pracował bez nadzoru i nie produkował śmieci, jest stworzenie mu pętli sprzężenia zwrotnego.

> "Naucz się backpressure. Zasadniczo chodzi o to, aby jak najbardziej ułatwić modelowi sprawdzanie własnej pracy."

Jeśli agent dostanie zadanie: "Napraw ten bug", a po naprawie musi uruchomić testy i zobaczy, że nie przechodzą, to ma szansę się poprawić. Jeśli napisze kod, który nie jest niczym weryfikowany, jego pewność siebie będzie wysoka, ale jakość kodu niska. **Output agenta jest wprost proporcjonalny do jakości narzędzi weryfikacyjnych, które mu dasz.** Daj mu przeglądarkę, bash, lintery i testy jednostkowe, a sam zacznie łatać dziury, zanim Ty wrócisz do komputera.

#### 4. Strategiczne Użycie Modeli (Nie zawsze Frontier)

Częstym błędem jest używanie najdroższego modelu do wszystkiego, co szybko wyczerpuje budżet i nie daje przewagi. Horthy proponuje podejście znane z optymalizacji: **"Make it run, make it right, make it fast, make it cheap."**

**Jak to przekłada się na agentów?**
- **Planowanie (Research/Design):** Użyj najdroższego i najmądrzejszego modelu (np. Opus/Fable/GPT-5.x), aby zbadać bazę kodu i opracować strategię. Tutaj głębokie rozumowanie ma największą wartość.
- **Implementacja (Execution):** Jeśli plan jest naprawdę dobry i podzielony na małe kroki, możesz przełączyć się na tańszy, szybszy model (np. Sonnet), aby wykonał mechaniczną pracę. Różnice w jakości będą znikome, a koszty spadną.
- **Sub-agenci:** Idealne miejsce na tanie modele. Jeśli sub-agent ma po prostu przeszukać logi lub sformatować dokument, nie potrzebujesz do tego modelu klasy premium.

#### Podsumowanie: Intuicja i Sprawczość

Na końcu rozmowy pada stwierdzenie, że największym wrogiem dobrego outputu jest "YOLO-pilled" podejście, czyli wrzucanie promptu i czekanie na cud.

Aby otrzymywać najlepszy output od agenta AI, musisz zbudować **intuicję LLM**. Oznacza to, że wiesz, kiedy model zaczyna konfabulować (np. gdy nagle nie potrafi naprawić prostego testu – to znak, że okno kontekstowe jest przepełnione i trzeba zacząć od nowa).
