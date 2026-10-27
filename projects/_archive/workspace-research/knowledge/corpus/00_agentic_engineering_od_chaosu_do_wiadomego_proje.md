---
type: Concept
id: 00_agentic_engineering_od_chaosu_do_wiadomego_proje
title: "Agentic engineering - od chaosu do świadomego projektowania.md (part 1/3)"
source: "Agentic engineering - od chaosu do świadomego projektowania.md"
tags: [agentic, agents, context-engineering, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
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
