---
type: Concept
title: Agentic engineering - od chaosu do świadomego projektowania
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Oto ustrukturyzowana refleksja na temat wywiadu z Dexterem (Dexem), byłym inżynierem NASA, dotyczącego jego przepływu pracy w inżynierii agentowej.

---

### Refleksja: Powrót do Podstaw Inżynierii w Erze Agentów AI

**Wprowadzenie: Zderzenie euforii z dyscypliną**

Refleksja nad wywiadem z Dexterem natychmiast konfrontuje nas z fundamentalnym napięciem dzisiejszego świata programowania: z jednej strony mamy euforię związaną z niesamowitymi możliwościami agentów AI, którzy potrafią "przenosić góry", a z drugiej strony realne ryzyko stworzenia "slop code" – kodu, który jest niespójny, niemożliwy do utrzymania i w dłuższej perspektywie stanowi ogromne obciążenie. Dex nie neguje mocy agentów; on proponuje ramy, w których ta moc jest wykorzystywana w sposób przemyślany, a nie chaotyczny.

Kluczowym wnioskiem z rozmowy jest to, że samo posiadanie niesamowicie zdolnego "pracownika" (agenta AI) nie zwalnia nas z roli "architekta" i "menedżera". Wręcz przeciwnie, to my musimy dostarczyć kontekst, kierunek i kontrolę, aby uniknąć stworzenia produktu, który okaże się pułapką.

---

### 1. Istota Program Design: Od "Co" do "Jak"

Najmocniejszym punktem wypowiedzi Dexa jest koncepcja **Program Design**. To coś więcej niż tylko zaawansowany prompting. To celowy, ustrukturyzowany proces podejmowania decyzji *zanim* agent zacznie działać. Jest to antidotum na główną bolączkę pracy z agentami: ich tendencję do podejmowania decyzji, które są technicznie poprawne, ale strategicznie lub architektonicznie błędne.

Proces ten, jak go opisuje Dex, składa się z warstw:

- **Produkt (PRD):** Zaczyna się od problemu użytkownika i mierzalnego celu (np. "zwiększ konwersję o X%"). To uziemia pracę agenta w realnej wartości biznesowej.
- **Architektura Systemu:** Definiowanie, jak usługi, endpointy i tabele będą ze sobą współpracować. To poziom, na którym wielu zaawansowanych użytkowników już pracuje.
- **Program Design (Sedno):** To warstwa, którą "większość ludzi pomija". Nie chodzi o definiowanie typów i sygnatur metod, ale o określenie *struktury* rozwiązania – gdzie będą pliki, jak będzie wyglądał call stack, jakie będą testy. To świadome kierowanie agentem, aby nie "wymyślił koła na nowo" w niepożądany sposób.
- **Vertical Slices (Pionowe Plasterki):** To kluczowa technika wdrożeniowa. Zamiast pozwalać modelowi na budowanie aplikacji "horyzontalnie" (cała baza danych, potem całe API, potem cały frontend), co uniemożliwia testowanie w trakcie, Dex zaleca budowanie "pionowych plasterków" funkcjonalności. Najpierw najprostsza, działająca od początku do końca wersja (np. mockowany endpoint i stubowany frontend), a potem dodawanie do niej logiki i obsługi błędów. To pozwala na ciągłą weryfikację i korektę kursu, gdy jest to jeszcze tanie.

**Refleksja:** Program Design to w istocie sformalizowanie tego, co robili dobrzy inżynierowie przed AI – myślenia o architekturze i strukturze przed pisaniem kodu. Dex pokazuje, że te umiejętności stały się jeszcze ważniejsze, a nie mniej. To odróżnia inżyniera od "promptera".

---

### 2. Pułapki "Lights-Off Factory" i Granice Benchmarków

Dex przestrzega przed wizją "fabryki oprogramowania", która działa całkowicie autonomicznie, bez nadzoru człowieka nad kodem. Jego własne doświadczenie ("lights-off factory" w lipcu 2025) jest tu najlepszym przykładem. Efektem był błąd, którego agenci nie potrafili naprawić przez tygodnie, a powrót do zaniedbanego, "sloppy" kodu okazał się koszmarem. To prowadzi do kluczowej tezy: **agenci są świetni w rozwiązywaniu problemów, ale nie potrafią pisać kodu, który jest łatwy w utrzymaniu (maintainable), bez udziału człowieka.**

Ta obserwacja jest genialnie uzasadniona w części dotyczącej benchmarków. Dex argumentuje, że benchmarki takie jak SWE-bench nie karzą za zły projekt (slop). Nagradzają tylko za to, czy testy przechodzą. Model może napisać setki linii zbędnego kodu (np. niepotrzebne `try-catch`, które logują i ponownie rzucają wyjątek), aby osiągnąć cel testu.

Jego analiza jest głębsza, bo sięga do mechanizmu uczenia przez wzmacnianie (RL):
- **Brak szybkiego "oracle" dla jakości:** Łatwo jest sprawdzić, czy test przechodzi (to szybki, deterministyczny sygnał zwrotny). Niezwykle trudno jest stworzyć sygnał zwrotny dla "jakości architektury", bo jej koszt jest rozłożony w czasie (tygodnie, miesiące). Nie da się tego efektywnie zrobić w pętli RL.
- **Jednorazowość problemów:** Benchmarki nie testują zdolności modelu do utrzymywania kodu w dobrym stanie przez 20 kolejnych funkcji. Nie pokazują, czy kod staje się "łatwiejszy do zmiany" z czasem.

**Refleksja:** To obala mit, że lepsze benchmarki oznaczają, że możemy całkowicie zaufać agentom. Pokazuje, że istnieje fundamentalna luka w obecnym paradygmacie uczenia modeli, która sprawia, że ludzka intuicja i doświadczenie w ocenie jakości kodu są nadal niezastąpione.

---

### 3. Context Engineering: Nowa Dyscyplina

Dex, jako jeden z autorów terminu "Context Engineering", definiuje go jako fundamentalne zrozumienie, że **jedynym interfejsem do modelu jest okno kontekstu**. Wszystko – RAG, pamięć, prompt engineering – sprowadza się do tokenów.

Ewolucja tego myślenia jest widoczna:
- **Od "12 Factor Agents" (2025):** Nacisk na posiadanie własnego okna kontekstu i rozumienie, że to stan w programie.
- **Do pragmatyzmu (2026):** Zrozumienie, że modele mają większe okna i lepszą kompakcję, więc nie trzeba być ortodoksyjnym "token maxxerem". Kluczowe jest posiadanie intuicji ("vibe"), kiedy model wchodzi w "dumb zone" i należy zrestartować sesję z nowym, czystym kontekstem.

**Refleksja:** To podkreśla, że umiejętność zarządzania kontekstem to nowa, kluczowa kompetencja inżyniera. Nie chodzi tylko o pisanie dobrych promptów, ale o zrozumienie, jak informacje przepływają do modelu, jak go to obciąża i jak to wpływa na jakość wyników. To jest operowanie na "fizyce" modelu.

---

### 4. Strategia i Meta-Umiejętności: Problem Wąskiego Gardła

Fragment o książce "The Goal" i koncepcji wąskiego gardła jest kluczowy dla zrozumienia mentalności Dexa. To przestroga przed optymalizowaniem dla samej optymalizacji ("token maxing", budowanie idealnego systemu multi-agentów), które nie ma przełożenia na dostarczanie wartości.

- **Wąskie gardło:** Jeśli wąskim gardłem jest przegląd kodu (code review), to dodanie pięciu kolejnych agentów piszących kod nic nie da. To tylko zwiększy stos pracy do przejrzenia.
- **Oczekiwany ból:** Meta-umiejętnością jest rozpoznawanie, które "pożary" (problemy) są tymi, które spalą całe miasto (np. awaria produkcji), a które są tylko małymi ogniskami, które można na razie zignorować.
- **Postawa "True Believer":** Dex i prowadzący wywiad dotykają też idei, że sukces w tej dziedzinie wymaga autentycznej wiary w technologię, a nie tylko gonienia za hype'em. To ludzie, którzy testują, eksperymentują i są gotowi na porażki, będą kształtować przyszłość.

**Refleksja:** To przenosi dyskusję z poziomu technicznego na poziom strategicznego myślenia o produkcie i biznesie. Agentic engineering to nie tylko pisanie kodu; to zarządzanie całym łańcuchem dostarczania wartości. Największym wyzwaniem nie jest okiełznanie modelu, ale okiełznanie własnego entuzjazmu i skupienie się na tym, co naprawdę ma znaczenie.

---

### Podsumowanie

Wywiad z Dexterem to mistrzowska lekcja dla każdego, kto poważnie myśli o wykorzystaniu AI w inżynierii oprogramowania. Jego przesłanie jest jasne:

> **Przestań bawić się swoimi agentami kodującymi i wróć do pracy.**

Praca ta polega na:
1.  **Projektowaniu (Program Design),** zanim zlecisz agentowi zadanie.
2.  **Utrzymywaniu zrozumienia kodu i logiki systemu,** aby nie stracić kontroli.
3.  **Byciu świadomym ograniczeń modeli** (wynikających z RL) i nieufaniu ślepo benchmarkom.
4.  **Rozumieniu i zarządzaniu kontekstem** jako kluczowym zasobem.
5.  **Skupieniu się na prawdziwym wąskim gardle** w procesie dostarczania wartości, a nie na fascynujących, ale drugorzędnych optymalizacjach.

Dex nie jest pesymistą. Jest realistą, który widzi ogromny potencjał, ale też rozumie, że jego wykorzystanie wymaga od nas, ludzi, wejścia na wyższy poziom dyscypliny, myślenia projektowego i strategicznego. To właśnie jest nowa, dojrzała era inżynierii agentowej.