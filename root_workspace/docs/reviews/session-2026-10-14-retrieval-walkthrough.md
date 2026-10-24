# Retrieval walkthrough — jak to działa na przykładach (2026-10-14)

<!-- audit:begin -->
## Po co to
Nie jest to test metrykowy. To jest pokazanie, jak retrieval i synteza
zachowują się na różnorodnych pytaniach: in-corpus łatwe, parafrazy,
cross-lingual, wieloetapowe, OOC, boundary, własne. Każde pytanie: retrieval
(top-5), synteza (odpowiedź albo odmowa), werdykt subiektywny. Pytania
poniżej zapisano przed uruchomieniem — verbatim, bez dobierania pod wynik.
Pipeline: `zbuduj_plan` (hybryda wektorowa ON) → `retrieve` → `oblicz_pokrycie`
→ `syntezuj_odpowiedz`, przez `scripts/_scratch/walkthrough_one.py`.

## Lista pytań (przed uruchomieniem)
A. in-corpus łatwe:
`1.` "Czym jest SEVerA i jak sie ma do self-evolving agents?"
`2.` "Jak działa przeszukiwanie min-max w drzewach gier?"
`3.` "Co to jest framework Disciplined Agile Delivery i jakie ma zasady?"
B. in-corpus trudne (parafraza):
`4.` "czy agent może sam siebie ulepszać?"
`5.` "jak komputer wybiera najlepszy ruch w grze planszowej?"
C. cross-lingual (PL pytanie, EN korpus):
`6.` "jak działa wygładzanie obrazu filtrem Gaussa?"
`7.` "czym jest naiwny klasyfikator Bayesa?"
D. in-corpus wieloetapowe:
`8.` "porównaj podejście iteracyjne z planowaniem predykcyjnym w inżynierii oprogramowania"
`9.` "dlaczego alfa-beta działa lepiej niż zwykły min-max w grach?"
E. OOC (poza korpusem, oczekiwana odmowa):
`10.` "Jaka będzie pogoda w Warszawie jutro?"
`11.` "Kto wygrał wybory w 2028?"
F. boundary (ta sama dziedzina, brak w korpusie, oczekiwana odmowa):
`12.` "Jak skonfigurować GraphRAG w Kubernetes?"
`13.` "Jak zintegrować agent memory hierarchies z Redis?"
G. własne:
`14.` "jak zaimplementować kolejkę w Scheme za pomocą domknięć?"

## Wyniki

### Pytanie `1.` [typ: in-corpus łatwe] "Czym jest SEVerA i jak sie ma do self-evolving agents?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Czym jest SEVerA i jak sie ma do self-evolving agents?
SLOWA KLUCZOWE: ['severa', 'self-evolving', 'agents']
TYP: edge_proveniencia | N WYNIKOW: 10
TOP-5:
  1. 00_severa_verified_synthesis_of_self_evolving_agent  |  "SEVerA: Verified Synthesis of Self-Evolving Agents"
  2. 00_a_comprehensive_survey_of_self_evolving_ai_agent  |  "A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foun
  3. 00_self_improvements_in_modern_agentic_systems_a_su  |  "Self-Improvements in Modern Agentic Systems: A Survey"
  4. 00_self_evolving_world_models_foresight_web_researc  |  "Self-Evolving World Models and Foresight for LLM Agents"
  5. 192_beyond_vibe_coding_from_coder_to_ai_era_develope  |  "Addy Osmani (part 193/233)"
POKRYTE: 6 z 10
ODMOWA: False
N_POKRYTYCH: 6 | CONFIDENCE: wysoka
ODPOWIEDZ: **Odpowiedź na pytanie:** Czym jest SEVerA i jak sie ma do self-evolving agents?

**Dowody z grafu (nodes.body, cytaty exact):**
- [# SEVerA: Verified Synthesis of Self-Evolving Agents **Source:** http://arxiv] — źródło: `00_severa_verified_synthesis_of_self_evolving_agent` ("SEVerA: Verified Synthesis of Self-Evolving Agents", tier 1)
- [25111v2 **Tags:** `agentic, scientific-discovery` ## Core Methodology & Findings **Authors:** Debangshu Banerjee, Changming Xu, Eugene Ie, Ming Zhang, Daiyi Peng ### Abstract Recent advances have s...] — źródło: `00_severa_verified_synthesis_of_self_evolving_
```
**Werdykt:** TRAFIONE
**Komentarz:** Top-jeden to oracle, sześć węzłów z pokryciem, odpowiedź z cytatami exact — tak wygląda happy path.

### Pytanie `2.` [typ: in-corpus łatwe] "Jak działa przeszukiwanie min-max w drzewach gier?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Jak działa przeszukiwanie min-max w drzewach gier?
SLOWA KLUCZOWE: ['dzia', 'przeszukiwanie', 'min-max', 'drzewach', 'gier']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 158_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 159/1123)"
  2. 46_automated_machine_learning_methods_systems_chall  |  "The Springer Series on Challenges in Machine Learning (part 47/210)"
  3. 138_multiagent_systems_algorithmic_game_theoretic_an  |  "MULTIAGENT SYSTEMS (part 139/510)"
  4. 173_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 174/1123)"
  5. 157_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 158/1123)"
POKRYTE: 0 z 10
ODMOWA: True
PRZYCZYNA: Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi 'Jak działa przeszukiwanie min-max w drzewach gier?'.
```
**Werdykt:** ODMOWA BŁĘDNA
**Komentarz:** Oracle z trust setu nie ma w top-pięć, pokrycie zero, więc system odmawia na pytanie in-corpus — polskie słowa kluczowe nie trafiają w angielskie body.

### Pytanie `3.` [typ: in-corpus łatwe] "Co to jest framework Disciplined Agile Delivery i jakie ma zasady?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Co to jest framework Disciplined Agile Delivery i jakie ma zasady?
SLOWA KLUCZOWE: ['framework', 'disciplined', 'agile', 'delivery', 'zasady']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 484_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 485/647)"
  2. 629_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 630/647)"
  3. 497_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 498/647)"
  4. 449_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 450/647)"
  5. 438_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 439/647)"
POKRYTE: 7 z 10
ODMOWA: False
N_POKRYTYCH: 7 | CONFIDENCE: wysoka
ODPOWIEDZ: **Odpowiedź na pytanie:** Co to jest framework Disciplined Agile Delivery i jakie ma zasady?

**Dowody z grafu (nodes.body, cytaty exact):**
- [506 ❘ CHAPTER 19 RAD DISCIPLINED AGILE DELIVERY In the words of its inventor Scott Ambler, “The Disciplined Agile Delivery (DAD) decision process framework is a people- first, learning- oriented hy...] — źródło: `484_beginning_software_engineering_2nd_edition_rod_s` ("BEGINNING (part 485/647)", tier 1)
- [It has a risk- value delivery life cycle, is goal driven, is enterprise aware, and is scalable] — źródło: `484_beginning_software_engineering_2nd_edi
```
**Werdykt:** TRAFIONE
**Komentarz:** Angielskie słowa kluczowe trafiają wprost w angielski korpus — top-jeden to oracle i odpowiedź cytuje rozdział o DAD.

### Pytanie `4.` [typ: parafraza] "czy agent może sam siebie ulepszać?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: czy agent może sam siebie ulepszać?
SLOWA KLUCZOWE: ['agent', 'agents', 'siebie', 'ulepsza']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 01_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods  |  "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horth
  2. 52_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 53/1123)"
  3. 182_harness_starter_kit  |  "Repository: harnessworks/harness-starter-kit (part 183/456)"
  4. 328_multiagent_systems_algorithmic_game_theoretic_an  |  "MULTIAGENT SYSTEMS (part 329/510)"
  5. 84_harness_starter_kit  |  "Repository: harnessworks/harness-starter-kit (part 85/456)"
POKRYTE: 10 z 10
ODMOWA: False
N_POKRYTYCH: 10 | CONFIDENCE: wysoka
ODPOWIEDZ: **Odpowiedź na pytanie:** czy agent może sam siebie ulepszać?

**Dowody z grafu (nodes.body, cytaty exact):**
- [Zamiast karmić głównego agenta milionem tokenów kodu źródłowego, wyślij sub-agenta, aby przeczytał repozytorium i wrócił z 50-tysięcznym streszczeniem] — źródło: `01_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods` ("Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym).md (part 2/3)", tier 1)
- [Jeśli zależy Ci na kontroli, każ agentowi zapisać kluczowe ustalenia do pliku Markdown i sam przejrzyj ten plik, zanim rozpoczniesz nową sesję] — źródło: `01_j
```
**Werdykt:** PUŁO
**Komentarz:** Surveje o self-evolving agents zniknęły z top-pięć, a synteza z wysoką pewnością odpowiada cytatami o kodowaniu — pokrycie mierzy obecność słów, nie sens.

### Pytanie `5.` [typ: parafraza] "jak komputer wybiera najlepszy ruch w grze planszowej?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: jak komputer wybiera najlepszy ruch w grze planszowej?
SLOWA KLUCZOWE: ['komputer', 'wybiera', 'najlepszy', 'ruch', 'grze', 'planszowej']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 02_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods  |  "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horth
  2. 138_multiagent_systems_algorithmic_game_theoretic_an  |  "MULTIAGENT SYSTEMS (part 139/510)"
  3. 01_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods  |  "Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horth
  4. 543_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 544/647)"
  5. 115_multiagent_systems_algorithmic_game_theoretic_an  |  "MULTIAGENT SYSTEMS (part 116/510)"
POKRYTE: 1 z 10
ODMOWA: False
N_POKRYTYCH: 1 | CONFIDENCE: niska
ODPOWIEDZ: **Odpowiedź na pytanie:** jak komputer wybiera najlepszy ruch w grze planszowej?

**Dowody z grafu (nodes.body, cytaty exact):**
- [" Jeśli agent dostanie zadanie: "Napraw ten bug", a po naprawie musi uruchomić testy i zobaczy, że nie przechodzą, to ma szansę się poprawić] — źródło: `01_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods` ("Jak naprawdę wycisnąć 2-3x z AI w kodowaniu (na podstawie rozmowy z Dexem Horthym).md (part 2/3)", tier 1)
- [** Daj mu przeglądarkę, bash, lintery i testy jednostkowe, a sam zacznie łatać dziury, zanim Ty wrócisz do komputera] — źródło: `01_jak_naprawd_wycisn
```
**Werdykt:** PUŁO
**Komentarz:** Jeden pokrywający węzeł wystarczył, by odpowiedzieć — cytatem o naprawianiu bugów na pytanie o wybór ruchu w grze.

### Pytanie `6.` [typ: cross-lingual] "jak działa wygładzanie obrazu filtrem Gaussa?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: jak działa wygładzanie obrazu filtrem Gaussa?
SLOWA KLUCZOWE: ['dzia', 'adzanie', 'obrazu', 'filtrem', 'gaussa']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 900_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 901/1123)"
  2. 103_llm_engineers_handbook_iusztin_paul_labonne_z_li  |  "LLM Engineer’s Handbook (part 104/416)"
  3. 944_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 945/1123)"
  4. 898_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 899/1123)"
  5. 14_pattern_recognition_and_machine_learning_christo  |  "Information Science and Statistics (part 15/736)"
POKRYTE: 0 z 10
ODMOWA: True
PRZYCZYNA: Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi 'jak działa wygładzanie obrazu filtrem Gaussa?'.
```
**Werdykt:** ODMOWA BŁĘDNA
**Komentarz:** Ranking znalazł oracle na pozycji jeden, ale tokenizer rozciął polskie diakrytyki i pokrycie liczone na ułamkach słów dało zero — odmowa mimo trafionego retrievalu.

### Pytanie `7.` [typ: cross-lingual] "czym jest naiwny klasyfikator Bayesa?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: czym jest naiwny klasyfikator Bayesa?
SLOWA KLUCZOWE: ['naiwny', 'klasyfikator', 'bayesa']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 86_the_book_of_why_the_new_science_of_cause_and_eff  |  "ALSO BY JUDEA PEARL: (part 87/369)"
  2. 418_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 419/1123)"
  3. 467_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 468/1123)"
  4. 87_the_book_of_why_the_new_science_of_cause_and_eff  |  "ALSO BY JUDEA PEARL: (part 88/369)"
  5. 112_the_book_of_why_the_new_science_of_cause_and_eff  |  "ALSO BY JUDEA PEARL: (part 113/369)"
POKRYTE: 0 z 10
ODMOWA: True
PRZYCZYNA: Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi 'czym jest naiwny klasyfikator Bayesa?'.
```
**Werdykt:** ODMOWA BŁĘDNA
**Komentarz:** Polskie słowa nie występują w angielskim korpusie, więc nawet ranking dryfuje ku książce o przyczynowości — tu odmowa jest uczciwa, ale pytanie dotyczy treści z korpusu.

### Pytanie `8.` [typ: wieloetapowe] "porównaj podejście iteracyjne z planowaniem predykcyjnym w inżynierii oprogramowania"
**Retrieval + synteza (verbatim):**
```
PYTANIE: porównaj podejście iteracyjne z planowaniem predykcyjnym w inżynierii oprogramowania
SLOWA KLUCZOWE: ['wnaj', 'podej', 'iteracyjne', 'planowaniem', 'predykcyjnym', 'ynierii', 'oprogramowania']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 02_agentic_engineering_od_chaosu_do_wiadomego_proje  |  "Agentic engineering - od chaosu do świadomego projektowania.md (part 3/3)"
  2. 57_domain_driven_design_tackling_complexity_in_the  |  "INTENTION- (part 58/454)"
  3. 01_agentic_engineering_od_chaosu_do_wiadomego_proje  |  "Agentic engineering - od chaosu do świadomego projektowania.md (part 2/3)"
  4. 26_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 27/647)"
  5. 159_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 160/647)"
POKRYTE: 1 z 10
ODMOWA: False
N_POKRYTYCH: 1 | CONFIDENCE: niska
ODPOWIEDZ: **Odpowiedź na pytanie:** porównaj podejście iteracyjne z planowaniem predykcyjnym w inżynierii oprogramowania

**Dowody z grafu (nodes.body, cytaty exact):**
- [--- ### Podsumowanie Wywiad z Dexterem to mistrzowska lekcja dla każdego, kto poważnie myśli o wykorzystaniu AI w inżynierii oprogramowania] — źródło: `02_agentic_engineering_od_chaosu_do_wiadomego_proje` ("Agentic engineering - od chaosu do świadomego projektowania.md (part 3/3)", tier 1)
- [To właśnie jest nowa, dojrzała era inżynierii agentowej] — źródło: `02_agentic_engineering_od_chaosu_do_wiadomego_proje` ("Agentic engineering -
```
**Werdykt:** CZĘŚCIOWO
**Komentarz:** W top-pięć są węzły z tej samej rodziny co oracle, ale odpowiedź to ogólnik o inżynierii agentowej — porównania iteracyjne kontra predykcyjne w niej nie ma.

### Pytanie `9.` [typ: wieloetapowe] "dlaczego alfa-beta działa lepiej niż zwykły min-max w grach?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: dlaczego alfa-beta działa lepiej niż zwykły min-max w grach?
SLOWA KLUCZOWE: ['alfa-beta', 'dzia', 'lepiej', 'zwyk', 'min-max', 'grach']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 158_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 159/1123)"
  2. 46_automated_machine_learning_methods_systems_chall  |  "The Springer Series on Challenges in Machine Learning (part 47/210)"
  3. 546_paradigms_of_artificial_intelligence_programming  |  "Paradigms of (part 547/828)"
  4. 545_paradigms_of_artificial_intelligence_programming  |  "Paradigms of (part 546/828)"
  5. 157_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 158/1123)"
POKRYTE: 0 z 10
ODMOWA: True
PRZYCZYNA: Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi 'dlaczego alfa-beta działa lepiej niż zwykły min-max w grach?'.
```
**Werdykt:** ODMOWA BŁĘDNA
**Komentarz:** Oracle o alfa-beta nie ma w top-pięć, a angielskie body o przycinaniu nie zawiera polskich słów z pytania — porównanie ginie na tokenizacji.

### Pytanie `10.` [typ: OOC] "Jaka będzie pogoda w Warszawie jutro?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Jaka będzie pogoda w Warszawie jutro?
SLOWA KLUCZOWE: ['dzie', 'pogoda', 'warszawie', 'jutro']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 36_the_goal_a_process_of_ongoing_improvement_revise  |  "THE GOAL (part 37/326)"
  2. 159_the_goal_a_process_of_ongoing_improvement_revise  |  "THE GOAL (part 160/326)"
  3. 537_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 538/647)"
  4. 121_beginning_software_engineering_2nd_edition_rod_s  |  "BEGINNING (part 122/647)"
  5. 13_the_creative_act_a_way_of_being_rick_rubin_z_lib  |  "PENGUIN PRESS (part 14/130)"
POKRYTE: 0 z 10
ODMOWA: True
PRZYCZYNA: Brak pokrycia body: FTS5 zwrócił wyników, ale żaden nie zawiera zdania z słowami kluczowymi 'Jaka będzie pogoda w Warszawie jutro?'.
```
**Werdykt:** ODMOWA SŁUSZNA
**Komentarz:** Losowe fragmenty o niczym, zero pokrycia, czysta odmowa — tak ma działać bramka na pytania spoza korpusu.

### Pytanie `11.` [typ: OOC] "Kto wygrał wybory w 2028?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Kto wygrał wybory w 2028?
SLOWA KLUCZOWE: ['wygra', 'wybory', '2028']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 55_icm_knowledge_big  |  "ICM_knowledge.md (part 56/259)"
  2. 648_artificial_intelligence_a_modern_approach_4th_ed  |  "F or Loy, Gordon, Lucy, George, and Isaac— S.J.R. (part 649/1123)"
  3. 316_graph_engineering_for_agentic_ai_systems_ken_hua  |  "GRAPH ENGINEERING (part 317/345)"
  4. 265_multiagent_systems_algorithmic_game_theoretic_an  |  "MULTIAGENT SYSTEMS (part 266/510)"
  5. 266_multiagent_systems_algorithmic_game_theoretic_an  |  "MULTIAGENT SYSTEMS (part 267/510)"
POKRYTE: 0 z 10
ODMOWA: False
N_POKRYTYCH: 0 | CONFIDENCE: niska (family-match)
ODPOWIEDZ: **Odpowiedź:** Znaleziono powiązane materiały w tej samej rodzinie, ale nie udało się uzyskać pełnego pokrycia treści (exact body match). Weryfikacja: ograniczona.
```
**Werdykt:** PUŁO
**Komentarz:** Zero pokrycia, ale fallback family-match odpowiada mglistym komunikatem zamiast odmówić — bramka OOC przecieka.

### Pytanie `12.` [typ: boundary] "Jak skonfigurować GraphRAG w Kubernetes?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Jak skonfigurować GraphRAG w Kubernetes?
SLOWA KLUCZOWE: ['skonfigurowa', 'graphrag', 'kubernetes']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 29_graph_engineering_for_agentic_ai_systems_ken_hua  |  "GRAPH ENGINEERING (part 30/345)"
  2. 52_llm_engineers_handbook_iusztin_paul_labonne_z_li  |  "LLM Engineer’s Handbook (part 53/416)"
  3. 12_graph_databases_new_opportunities_for_connected  |  "Ian Robinson, (part 13/191)"
  4. 163_graph_engineering_for_agentic_ai_systems_ken_hua  |  "GRAPH ENGINEERING (part 164/345)"
  5. 65_graph_databases_new_opportunities_for_connected  |  "Ian Robinson, (part 66/191)"
POKRYTE: 0 z 10
ODMOWA: False
N_POKRYTYCH: 0 | CONFIDENCE: niska (family-match)
ODPOWIEDZ: **Odpowiedź:** Znaleziono powiązane materiały w tej samej rodzinie, ale nie udało się uzyskać pełnego pokrycia treści (exact body match). Weryfikacja: ograniczona.
```
**Werdykt:** PUŁO
**Komentarz:** Korpus nie zawiera wdrażania na Kubernetes, a system udaje, że znalazł powiązane materiały — ten sam przeciek co w pytaniu jedenastym.

### Pytanie `13.` [typ: boundary] "Jak zintegrować agent memory hierarchies z Redis?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: Jak zintegrować agent memory hierarchies z Redis?
SLOWA KLUCZOWE: ['zintegrowa', 'agent', 'agents', 'memory', 'hierarchies', 'redis']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 00_agent_memory_hierarchies  |  "agent-memory-hierarchies.md"
  2. 00_persistent_memory_hierarchies_agents  |  "persistent-memory-hierarchies-agents.md"
  3. 03_transferable_expertise_for_autonomous_agents_via  |  "Transferable Expertise for Autonomous Agents via Real-World Case-Based Learning
  4. 180_graph_engineering_for_agentic_ai_systems_ken_hua  |  "GRAPH ENGINEERING (part 181/345)"
  5. 08_transferable_expertise_for_autonomous_agents_via  |  "Transferable Expertise for Autonomous Agents via Real-World Case-Based Learning
POKRYTE: 9 z 10
ODMOWA: False
N_POKRYTYCH: 9 | CONFIDENCE: wysoka
ODPOWIEDZ: **Odpowiedź na pytanie:** Jak zintegrować agent memory hierarchies z Redis?

**Dowody z grafu (nodes.body, cytaty exact):**
- [Agent memory turns a stateless generator into a persistent agent] — źródło: `00_agent_memory_hierarchies` ("agent-memory-hierarchies.md", tier 1)
- [1145/3748302 (first dedicated memory survey)] — źródło: `00_agent_memory_hierarchies` ("agent-memory-hierarchies.md", tier 1)
- [Textual form dominates for interpretability; hierarchical (MemGPT virtual memory paging between RAM/disk via archival_memory_search / core_memory_append, JARVIS-1 multimodal stores) enables verti
```
**Werdykt:** PUŁO
**Komentarz:** Najgroźniejszy przypadek: wysoka pewność i dziewięć pokryć o hierarchiach pamięci, ale o integracji z Redis nic — synteza odpowiada na pytanie, którego korpus nie zawiera.

### Pytanie `14.` [typ: własne] "jak zaimplementować kolejkę w Scheme za pomocą domknięć?"
**Retrieval + synteza (verbatim):**
```
PYTANIE: jak zaimplementować kolejkę w Scheme za pomocą domknięć?
SLOWA KLUCZOWE: ['zaimplementowa', 'kolejk', 'scheme', 'pomoc', 'domkni']
TYP: fts_body | N WYNIKOW: 10
TOP-5:
  1. 674_paradigms_of_artificial_intelligence_programming  |  "Paradigms of (part 675/828)"
  2. 328_structure_and_interpretation_of_computer_program  |  "1 (part 329/518)"
  3. 718_paradigms_of_artificial_intelligence_programming  |  "Paradigms of (part 719/828)"
  4. 390_structure_and_interpretation_of_computer_program  |  "1 (part 391/518)"
  5. 670_paradigms_of_artificial_intelligence_programming  |  "Paradigms of (part 671/828)"
POKRYTE: 0 z 10
ODMOWA: False
N_POKRYTYCH: 0 | CONFIDENCE: niska (family-match)
ODPOWIEDZ: **Odpowiedź:** Znaleziono powiązane materiały w tej samej rodzinie, ale nie udało się uzyskać pełnego pokrycia treści (exact body match). Weryfikacja: ograniczona.
```
**Werdykt:** PUŁO
**Komentarz:** Oracle o kolejkach w SICP nie ma w top-pięć, a zamiast odmowy albo odpowiedzi dostajemy pusty komunikat family-match — ani to, ani to.

## Podsumowanie
| # | Typ | Pytanie (skrót) | Werdykt |
|---|---|---|---|
| `1` | in-corpus łatwe | SEVerA | TRAFIONE |
| `2` | in-corpus łatwe | min-max | ODMOWA BŁĘDNA |
| `3` | in-corpus łatwe | DAD | TRAFIONE |
| `4` | parafraza | samoulepszanie agenta | PUŁO |
| `5` | parafraza | najlepszy ruch | PUŁO |
| `6` | cross-lingual | Gauss | ODMOWA BŁĘDNA |
| `7` | cross-lingual | Bayes | ODMOWA BŁĘDNA |
| `8` | wieloetapowe | iteracyjne kontra predykcyjne | CZĘŚCIOWO |
| `9` | wieloetapowe | alfa-beta | ODMOWA BŁĘDNA |
| `10` | OOC | pogoda | ODMOWA SŁUSZNA |
| `11` | OOC | wybory | PUŁO |
| `12` | boundary | GraphRAG plus K8s | PUŁO |
| `13` | boundary | memory plus Redis | PUŁO |
| `14` | własne | kolejka w Scheme | PUŁO |

**Rozkład:** dwa trafione, jedno częściowo, pięć pudeł, jedna odmowa słuszna, pięć odmów błędnych.

**Co widać:** Działa tylko dosłowne trafienie angielskich słów w angielski korpus — cała reszta psuje się na tokenizacji polskich diakrytyków albo na braku mapowania synonimów. Pokrycie liczy obecność słów, nie sens, więc synteza odpowiada z wysoką pewnością nie na temat. Fallback family-match przecieka w obie strony: zamienia słuszne odmowy w mgliste odpowiedzi i mydli oczy tam, gdzie retrieval chybił. Przypadek trzynasty to czerwona flaga: pewna odpowiedź na pytanie spoza korpusu.

## Tool calls
| Wartość | Komenda | Surowy output (fragment) |
|---|---|---|
| `2028` | `python scripts/_scratch/walkthrough_one.py "Kto wygrał wybory w 2028?"` | `SLOWA KLUCZOWE: ['wygra', 'wybory', '2028']` |
| `POKRYTE: 6 z 10` | `python scripts/_scratch/walkthrough_one.py "Czym jest SEVerA i jak sie ma do self-evolving agents?"` | `POKRYTE: 6 z 10` |
| `POKRYTE: 0 z 10` | `python scripts/_scratch/walkthrough_one.py "Jak działa przeszukiwanie min-max w drzewach gier?"` | `POKRYTE: 0 z 10` |
| `POKRYTE: 7 z 10` | `python scripts/_scratch/walkthrough_one.py "Co to jest framework Disciplined Agile Delivery i jakie ma zasady?"` | `POKRYTE: 7 z 10` |
| `POKRYTE: 10 z 10` | `python scripts/_scratch/walkthrough_one.py "czy agent może sam siebie ulepszać?"` | `POKRYTE: 10 z 10` |
| `POKRYTE: 1 z 10` | `python scripts/_scratch/walkthrough_one.py "jak komputer wybiera najlepszy ruch w grze planszowej?"` | `POKRYTE: 1 z 10` |
| `POKRYTE: 9 z 10` | `python scripts/_scratch/walkthrough_one.py "Jak zintegrować agent memory hierarchies z Redis?"` | `POKRYTE: 9 z 10` |
| `N_POKRYTYCH: 6` | `python scripts/_scratch/walkthrough_one.py "Czym jest SEVerA i jak sie ma do self-evolving agents?"` | `N_POKRYTYCH: 6 \| CONFIDENCE: wysoka` |
| `N_POKRYTYCH: 0` | `python scripts/_scratch/walkthrough_one.py "Kto wygrał wybory w 2028?"` | `N_POKRYTYCH: 0 \| CONFIDENCE: niska (family-match)` |
| `N_POKRYTYCH: 1` | `python scripts/_scratch/walkthrough_one.py "jak komputer wybiera najlepszy ruch w grze planszowej?"` | `N_POKRYTYCH: 1 \| CONFIDENCE: niska` |

## not checked:
- czy przykłady są reprezentatywne dla właściciela (subiektywny wybór pytań).
- czy oracle z trust setu to ground truth (pytanie `2.` i `9.` zakładają, że odpowiedź jest w korpusie).
- czy family-match fallback ma uzasadnienie produktowe (raport tylko pokazuje jego działanie).

<!-- audit:end -->
