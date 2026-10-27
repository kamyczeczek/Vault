---
type: Concept
title: Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym)
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Oto refleksja oparta na tej samej rozmowie, ale skoncentrowana wyłącznie na praktycznych strategiach wydobywania maksymalnej jakości z agentów AI podczas kodowania.

---

### Refleksja: "Sztuka Sterowania Agentem: Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym)"

#### Wstęp: Koniec ery "YOLO Promptingu"

Większość dyskusji o AI w kodowaniu koncentruje się na tym, *co* wpisać w okno czatu. Dex Horthy w swojej rozmowie proponuje fundamentalnie inną, bardziej dojrzałą perspektywę: aby uzyskać naprawdę dobry output od agenta, musimy przestać myśleć o promptowaniu, a zacząć myśleć o **inżynierii kontekstu**. To przejście od roli "pisarza promptów" do roli "reżysera systemu", który projektuje środowisko pracy agenta tak, aby ten nie miał innego wyjścia, jak napisać dobry kod.

Zamiast czekać na GPT-7, Horthy pokazuje, jak już dziś, sterując modelem, uzyskać kod o jakości 99% kodu pisanego ręcznie, ale 2-3 razy szybciej.

#### 1. Specyfikacja jako Dźwignia Sterowania (Leverage)

Pierwszą i najważniejszą lekcją jest zmiana myślenia o specyfikacji. Dla większości z nas specyfikacja to dokument, który "musi być zrobiony". Dla Horthy'ego to narzędzie do sterowania.

> "Nie obchodzi mnie, jaki kształt ma twoja specyfikacja. Ma dawać ci dźwignię."

**Jak to działa w praktyce?** Chodzi o koszt wprowadzania zmian. Poprawienie błędu w 200-liniowym pliku Markdown jest 10 razy tańsze (czasowo i poznawczo) niż poprawianie błędu w 2000 liniach wygenerowanego kodu. Jeśli każesz agentowi od razu pisać kod, "zabetonowuje" on swoje wczesne, często błędne decyzje. Jeśli najpierw wygeneruje plan (specyfikację), Ty masz szansę na szybką korektę na poziomie architektury, zanim agent zejdzie na poziom implementacji.

Kluczowa zasada: **Nie dąż do perfekcji w specyfikacji.** Horthy radzi spędzić 10 minut, aby doprowadzić ją do 80% poprawności. Jeśli doprowadzisz ją do 100% szczegółowości, to nie napisałeś specyfikacji – napisałeś kod. Chodzi o to, by na tyle dobrze nakreślić kierunek, żeby agent, implementując, nie zboczył w ślepy zaułek.

#### 2. Zarządzanie Oknem Kontekstowym (Walka ze "Strefą Głupoty")

Agenci AI gubią się, gdy w ich oknie kontekstowym jest za dużo szumu. Horthy mówi o tym wprost: modele mają swoją "strefę głupoty" (Dumb Zone). Nawet jeśli model ma okno na 1 milion tokenów, jego jakość rozumowania spada drastycznie po przekroczeniu pewnego progu (często jest to 40-60% limitu).

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

Najlepszy output bierze się z mariażu: **dźwigni (specyfikacja) + higieny (zarządzanie kontekstem) + weryfikacji (testy) + ekonomii (dobór modelu).** Jeśli to opanujesz, nie potrzebujesz czekać na AGI. Masz już w ręku narzędzie, które pisze kod jak Ty, tylko 2-3 razy szybciej.