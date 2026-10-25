---
type: report
title: Synteza OKF-rag — od surowego materiału do użytecznej wiedzy
description: Roboczy model przekształcania materiałów o organizacji workspace i wiedzy w koncepty, decyzje oraz eksperymenty.
status: draft
tags: [knowledge-management, synthesis, okf, vault]
sources:
  - SPEC.md
  - open-knowledge-format.md
  - ontoship.md
  - llm-wiki.md
  - napkin.md
  - okf-rag.md
  - okforge.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Pytanie

Jak przekształcać surowe materiały w vaultcie w wnioski, które można później
znaleźć, ocenić i zastosować?

# Zakres

`Notes/OKF-rag` nie jest jeszcze jedną spójną bazą wiedzy. Zawiera specyfikacje,
opisy narzędzi, importy repozytoriów i fragmenty implementacji. Dlatego nie
należy streszczać wszystkich plików naraz. Należy zachować je jako materiał
źródłowy i budować nad nimi krótką, kuratorowaną warstwę syntezy.

# Powtarzające się twierdzenia

## 1. Źródłem prawdy powinien być czytelny Markdown

Markdown wraz z indeksem i historią Git pozostaje podstawowym artefaktem, który
może czytać człowiek, agent i zwykłe narzędzie tekstowe. Wyszukiwarka, graf,
embeddingi i widoki HTML są warstwami pochodnymi, które można odbudować.

Źródła: [OntoShip](ontoship.md) (README, linie 89–103), [OKF](SPEC.md)
(sekcja 4, linie 159–215).

Konsekwencja: najpierw poprawiamy notatkę źródłową, a dopiero potem przebudowujemy
indeksy i wyszukiwanie.

## 2. Surowy materiał i wiedza pochodna to różne warstwy

Import repozytorium, transcript lub dokumentacja narzędzia nie jest jeszcze
wnioskiem. Wniosek powstaje dopiero po wybraniu twierdzeń, porównaniu źródeł i
zapisaniu implikacji dla własnego workspace'u. [inferred]

Źródła: [llm-wiki](llm-wiki.md) (linie 54–82, 113–122),
[okf-rag](okf-rag.md) (linie 445–527), [okforge](okforge.md)
(linie 760–825).

Konsekwencja: nie edytujemy masowych importów tylko po to, żeby wyglądały
ładniej; tworzymy osobną notatkę syntezy z linkami do materiału źródłowego.

## 3. Metadane są częścią użyteczności wiedzy

Typ, tytuł, jednozdaniowy opis, tagi, źródła, status, zaufanie i świeżość
pozwalają filtrować oraz oceniać notatki bez czytania całego korpusu.

Źródła: [SPEC](SPEC.md) (linie 167–214, 283–430),
[Open Knowledge Format](open-knowledge-format.md) (sekcja frontmatter),
[OntoShip](ontoship.md) (linie 838–930).

Konsekwencja: każda nowa trwała notatka powinna mieć przynajmniej `type`,
`title`, `description`, `status` i `sources`.

## 4. Warto kompilować wiedzę przed momentem zapytania

Zamiast za każdym razem rekonstruować sens z surowych fragmentów, można raz
wydobyć koncepty, relacje, cytowania i stan weryfikacji, a później korzystać z
tej stabilnej warstwy przy wyszukiwaniu i odpowiadaniu.

Źródło: [llm-wiki](llm-wiki.md) (linie 54–78, 113–122).

Konsekwencja: dla materiałów wielokrotnego użytku tworzymy małe strony
konceptowe, zamiast przechowywać wyłącznie duże dumpy.

## 5. Synteza ma kodować sposób rozumowania, nie tylko temat

Dobra synteza odpowiada: „co ekspert zrobiłby w konkretnej sytuacji?”, a nie
tylko: „o czym są te materiały?”. Powinna zawierać reguły wyboru, wyjątki,
procedurę i znane luki.

Źródło: [okforge](okforge.md) (prompt `skill_create`, około linie 21058–21204).

Konsekwencja: w notatce syntezy zapisujemy reguły i decyzje deklaratywnie, np.
„najpierw sprawdź istniejący koncept, potem utwórz nowy”, zamiast opisu rozmowy.

## 6. Pochodzenie i poziom zaufania muszą być widoczne

Czytelnik powinien móc odróżnić twierdzenie bezpośrednio potwierdzone w źródle,
wniosek wyprowadzony z kilku źródeł oraz hipotezę wymagającą testu.

Źródła: [SPEC](SPEC.md) (linie 283–430), [llm-wiki](llm-wiki.md)
(linie 54–78), [napkin](napkin.md) (linie 3782–3900).

Konsekwencja: twierdzenia syntetyczne oznaczamy jako `[inferred]`, a każdą
ważną tezę łączymy z konkretnymi plikami źródłowymi.

## 7. Wniosek powinien kończyć się decyzją albo eksperymentem

Sama obserwacja nie zmienia workspace'u. Użyteczny dokument mówi, co przyjmujemy,
jakie będą konsekwencje i jaki mały test może potwierdzić lub obalić założenie.

Źródła: [OntoShip — decyzje](ontoship.md) (linie 985–1155),
[napkin](napkin.md) (linie 3782–3900).

Konsekwencja: każda większa synteza kończy się sekcjami `Decyzja`, `Konsekwencje`
i `Eksperyment` albo jawnie wskazuje, że decyzji jeszcze nie ma.

## 8. Porządkowanie powinno być konserwatywne i iteracyjne

Najpierw naprawiamy kilka konkretnych problemów: broken links, oczywiste
duplikaty, sieroty i błędne lokalizacje. Nie robimy jednego wielkiego
przemeblowania na podstawie podobieństwa „vibe”.

Źródło: [napkin — Tend](napkin.md) (linie 3916–3983).

Konsekwencja: testujemy model na małej próbce i dopiero potem stosujemy go do
całego vaultu.

## 9. Jakość wyszukiwania trzeba mierzyć, nie zakładać

To, że narzędzie zwróciło podobny tekst, nie oznacza jeszcze, że znalazło
właściwe źródło. Warto mieć kilka prawdziwych pytań i sprawdzać, czy właściwa
notatka trafia do top 1 lub top 5.

Źródło: [OntoShip — benchmark](ontoship.md) (linie 343–399, 1027–1062).

Konsekwencja: po uporządkowaniu małej próbki zapisujemy kilka pytań kontrolnych
i porównujemy wyniki przed oraz po zmianie.

# Wniosek syntetyczny

Vault powinien być traktowany jako wersjonowany przepływ wiedzy, a nie jako
jedna płaska lista notatek:

```text
surowy materiał
    → wybrane twierdzenia
    → koncept z metadanymi i źródłami
    → synteza między źródłami
    → decyzja albo eksperyment
    → indeks / wyszukiwanie / graf jako warstwa pochodna
```

Najmniejszą sensowną jednostką pracy nie jest „posprzątać folder”, tylko
odpowiedzieć na jedno konkretne pytanie i zapisać odpowiedź tak, aby za trzy
miesiące dało się odtworzyć jej pochodzenie oraz konsekwencje. [inferred]

# Robocza decyzja

## Kontekst

`Notes/OKF-rag` zawiera wartościowe materiały, ale ich forma miesza źródła,
specyfikacje i implementacje. Globalne przemeblowanie teraz grozi utratą
pochodzenia oraz pomieszaniem rekomendacji z opisem istniejącego narzędzia.

## Decyzja

Na tym etapie zachowujemy istniejące pliki jako korpus źródłowy. Wnioski tworzymy
w osobnych, krótkich notatkach syntezy, z linkami do źródeł i wyraźnym statusem
`draft`/`active`. Każda synteza odpowiada na jedno pytanie i kończy się decyzją
lub eksperymentem.

## Konsekwencje

- nie trzeba najpierw ręcznie porządkować wszystkich dużych plików;
- można poprawiać model na małych, odwracalnych przykładach;
- łatwo odróżnić opis narzędzia od rekomendacji dla własnego vaultu;
- indeksy i wyszukiwanie można budować dopiero wokół sprawdzonych konceptów.

## Poza zakresem

Ta decyzja nie rozstrzyga jeszcze, czy docelowym narzędziem będzie OKF-RAG,
llmwiki, napkin, Obsidian CLI czy inny system. Najpierw testujemy przepływ
pracy, niezależnie od konkretnego narzędzia.

# Pierwszy eksperyment

Przetworzyć następujący mały zestaw:

- [SPEC.md](SPEC.md) — kontrakt formatu;
- [ontoship.md](ontoship.md) — organizacja i decyzje;
- [napkin.md](napkin.md) — destylacja i utrzymanie.

Sukces oznacza, że z tych trzech źródeł powstaje jedna krótka decyzja, a czytelnik
potrafi wskazać źródło każdej ważnej tezy, odróżnić fakt od `[inferred]` oraz
wykonać opisany następny krok bez ponownego czytania całych importów.

# Następny krok

Po zaakceptowaniu tego modelu można utworzyć osobne katalogi lub prefiksy dla
`decisions`, `concepts` i `experiments`. Nie należy tworzyć ich wcześniej tylko
dlatego, że wyglądają porządnie — struktura ma wynikać z powtarzalnego przepływu
pracy.
