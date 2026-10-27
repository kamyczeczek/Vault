---
type: Concept
id: 01_agentic_engineering_od_chaosu_do_wiadomego_proje
title: "Agentic engineering - od chaosu do świadomego projektowania.md (part 2/3)"
source: "Agentic engineering - od chaosu do świadomego projektowania.md"
tags: [agentic, agents, context-engineering, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

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
