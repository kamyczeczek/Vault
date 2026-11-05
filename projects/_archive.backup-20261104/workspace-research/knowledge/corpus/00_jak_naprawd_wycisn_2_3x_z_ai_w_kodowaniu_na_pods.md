---
type: Concept
id: 00_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods
title: "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym).md (part 1/3)"
source: "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym).md"
tags: [agentic, agents, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
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
