---
type: Concept
title: inspiration
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Tak. Dodałbym na końcu osobną sekcję **„Research backlog / Deep dives”**, żeby agent nie tylko implementował obecne heurystyki, ale wiedział, **które niepewności warto dalej badać i jakich eksperymentów szukać**.

Poniżej pełna, rozszerzona wersja do podmiany w poradniku.

# Self-Improving Workspace

## Przewodnik projektowy i research backlog dla agenta AI

------

# 1. Cel

Przekształć istniejący workspace w system, który **stopniowo poprawia jakość przyszłych wyników na podstawie rzeczywistych doświadczeń**, bez konieczności aktualizacji wag modelu.

Nie buduj od razu autonomicznej „fabryki samodoskonalenia”.

Zacznij od:

```text
real task
   ↓
agent execution
   ↓
result / tests / feedback
   ↓
experience
   ↓
pattern extraction
   ↓
candidate heuristic / skill
   ↓
validation on new tasks
   ↓
KEEP / REVISE / REJECT
   ↓
workspace update
   ↓
future tasks
```

Najważniejszym celem nie jest zwiększanie ilości pamięci.

**Celem jest zwiększanie użyteczności workspace'u.**

------

# 2. Główna hipoteza

Workspace można traktować jako **zewnętrzny, ewoluujący substrat agenta**.

Model może pozostać zamrożony:

```text
Frozen Model
     +
Evolving Workspace
     +
Execution Feedback
     +
Validation
```

Zmianie podlegają przede wszystkim:

- skills,
- procedury,
- heurystyki,
- instrukcje,
- narzędzia,
- retrieval,
- konfiguracja,
- struktura pamięci.

Każda zmiana jest jednak **hipotezą**, a nie faktem.

------

# 3. Najważniejsza zasada

Nie implementuj:

```text
experience → permanent memory
```

Implementuj:

```text
experience
    ↓
pattern
    ↓
candidate
    ↓
validation
    ↓
active skill
```

Workspace powinien **kompilować doświadczenie**, a nie po prostu je magazynować.

------

# 4. Najpierw zbadaj obecny workspace

Przed modyfikacją ustal:

1. gdzie agent otrzymuje kontekst,
2. gdzie przechowywane są instrukcje,
3. gdzie przechowywane są doświadczenia,
4. jak wykonywane są zadania,
5. jak wykrywany jest sukces/porażka,
6. jakie testy istnieją,
7. które pliki agent może modyfikować,
8. które elementy powinny pozostać stabilne,
9. czy istnieje rollback,
10. czy istnieje benchmark,
11. czy istnieje mechanizm izolacji eksperymentów.

**Nie twórz równoległej architektury, jeśli obecny workspace można rozszerzyć.**

------

# 5. Rozdziel typy wiedzy

Minimalny model:

```text
workspace/
├── experience/
├── candidates/
├── skills/
├── rejected/
└── evaluation/
```

Znaczenie:

### `experience/`

Surowe przypadki:

```text
task
actions
result
failure
tests
feedback
```

### `candidates/`

Proponowane, ale niezatwierdzone zmiany.

### `skills/`

Aktywna, skompilowana wiedza proceduralna.

### `rejected/`

Odrzucone hipotezy i zmiany.

### `evaluation/`

Historia wyników i porównań workspace'ów.

Jeśli obecny system ma już podobny podział, zachowaj jego strukturę.

------

# 6. Experience ≠ Skill

### Experience

```text
Task:
API returned malformed JSON.

Failure:
agent accessed nested field without validation.

Resolution:
validate response before use.
```

### Skill

```yaml
id: H-017
trigger: "consuming external data"
failure_mode: "assuming schema correctness"
action: "validate required fields and types"
verification: "test missing/null/malformed input"
scope: "API and external-data integration"
```

Skill ma być **generalizacją**, nie kopią doświadczenia.

------

# 7. Buduj małe heurystyki

Preferuj:

```text
WHEN <trigger>
DO <action>
BECAUSE <failure mode>
VERIFY WITH <test>
```

Unikaj:

```text
"Always write robust, high-quality code."
```

Dobra heurystyka:

- ma wyraźny trigger,
- opisuje konkretny failure mode,
- prowadzi do działania,
- ma sposób weryfikacji,
- ma zakres,
- jest możliwie krótka.

------

# 8. Generalizuj przed promocją

System powinien rozpoznawać, czy kilka przypadków reprezentuje wspólny wzorzec.

Przykład:

```text
API → missing field
CSV → missing column
Webhook → null object
Database → unexpected schema
```

może prowadzić do:

```text
procedural family:
external data validation
```

a następnie:

```text
Validate external data against expected schema
before consuming it.
```

Nie twórz osobnych reguł dla każdego przypadku, jeśli można bezpiecznie stworzyć jedną regułę wyższego poziomu.

------

# 9. Organizuj skills według rodzin proceduralnych

Przykład:

```text
skills/
├── debugging/
├── testing/
├── api-integration/
├── data-processing/
├── repository-navigation/
└── deployment/
```

Nie buduj jednak nadmiernie głębokiej hierarchii.

Zasada:

> najmniejsza struktura, która pozwala znaleźć właściwą procedurę.

------

# 10. Evidence threshold

Nie promuj automatycznie reguły po jednym przypadku.

Możesz przechowywać:

```yaml
evidence_count: 4
successful_uses: 3
failed_uses: 1
```

Jednak **nie zakładaj, że N=3 jest prawidłowym progiem**.

To jest parametr do eksperymentu:

```text
N = 1
N = 2
N = 3
N = 5
```

Porównaj:

- false positives,
- false negatives,
- generalization,
- time-to-learning,
- regression rate.

------

# 11. Każda zmiana jest hipotezą

Przykład:

```yaml
change_id: C-042

hypothesis:
  "This skill reduces schema-related failures."

expected_effect:
  "higher first-pass success"

affected_family:
  "API integration"

validation:
  "20 unseen tasks"

result:
  ...

decision:
  KEEP | REVISE | REJECT
```

Nie oceniaj jakości zmiany na podstawie tego, czy wygenerowany tekst wygląda przekonująco.

------

# 12. Bounded updates

Nie pozwalaj optimizerowi swobodnie przepisywać całego workspace'u.

Preferuj:

```text
small patch
    ↓
validation
    ↓
commit
```

zamiast:

```text
LLM
 ↓
rewrite entire workspace
 ↓
hope
```

Możliwe limity:

```text
max_changed_files
max_changed_lines
max_new_skills
max_deleted_skills
max_modified_sections
```

Każda zmiana powinna mieć ograniczony promień rażenia.

------

# 13. Validation gate

Minimalny mechanizm:

```text
             OLD WORKSPACE
                    │
                    ▼
             validation set
                    │
                    ▼
               score_old

             NEW WORKSPACE
                    │
                    ▼
             validation set
                    │
                    ▼
               score_new

                    ↓

             acceptance gate
```

Nie testuj wyłącznie tasku, który wygenerował heurystykę.

Testuj:

1. przypadki źródłowe,
2. nowe warianty tej samej rodziny,
3. zadania z innych rodzin,
4. regresje na wcześniej rozwiązanych zadaniach.

------

# 14. Held-out tasks

Rozdziel:

```text
experience / training
        ↓
candidate
        ↓
validation
        ↓
hidden evaluation
```

Optimizer nie powinien mieć możliwości wielokrotnego dostosowywania reguły bezpośrednio do hidden setu.

Celem jest generalizacja.

------

# 15. Generalization jest ważniejsza niż memorization

Organizuj benchmark w rodziny.

```text
schema validation

seen:
- API JSON
- CSV

unseen:
- webhook
- database result
- YAML
```

Dobra heurystyka powinna poprawiać wyniki również na unseen variants.

------

# 16. Negative memory

Odrzucone hipotezy są również informacją:

```yaml
id: C-031
proposal: "Always avoid library X"

reason_rejected:
  "caused regressions on tasks where X is appropriate"
```

System powinien pamiętać:

```text
what works
```

oraz:

```text
what looked promising but failed
```

Nie traktuj jednak każdego odrzucenia jako absolutnego tabu.

------

# 17. Workspace musi umieć odejmować

Dopuszczalne operacje:

```text
ADD
REVISE
MERGE
DEPRECATE
DELETE
```

Jeśli:

```text
H17
H38
```

opisują prawie ten sam wzorzec:

```text
H17 + H38
      ↓
H51
```

Jeżeli reguła powoduje regresję:

```text
ACTIVE
   ↓
DEPRECATED
   ↓
REMOVED
```

------

# 18. Nie maksymalizuj liczby skills

Cel:

```text
quality ↑
```

nie:

```text
number_of_skills ↑
```

Rozważ:

```text
Utility =
    QualityGain
    - λ ContextCost
    - μ RegressionRisk
    - ν Complexity
```

Najpierw mierz składniki osobno.

Nie trzeba od razu budować pełnego matematycznego optimizera.

------

# 19. Context retrieval

Nie ładuj całego workspace'u.

Preferuj:

```text
task
 ↓
identify relevant procedural family
 ↓
retrieve relevant skills
 ↓
execute
```

zamiast:

```text
task
 ↓
load everything
```

Dodatkowy kontekst może pomagać, ale może też:

- zwiększać koszt,
- rozpraszać agenta,
- powodować konflikty,
- wprowadzać niepotrzebne wymagania.

Dlatego **context selection jest częścią self-improvement**.

------

# 20. Best-known workspace

Nie zakładaj, że najnowsza wersja jest najlepsza.

```text
W0 score=70
W1 score=73
W2 score=71
W3 score=75
W4 score=72

best = W3
```

Eksperyment może pogorszyć wynik.

To nie powinno niszczyć najlepszego stanu.

------

# 21. Oddziel optimizer od target agent

Preferuj:

```text
TARGET AGENT
    ↓
executes tasks
    ↓
trajectory
    ↓
OPTIMIZER
    ↓
proposes change
    ↓
VALIDATOR
    ↓
commit / reject
```

Agent wykonujący zadanie nie powinien samodzielnie decydować:

> „moja własna nowa reguła jest poprawna, więc ją zapisuję”.

------

# 22. Nie używaj LLM jako jedynego oracle

Dla kodu priorytet:

```text
unit tests
integration tests
type checking
linting
build
runtime behavior
hidden tests
```

LLM może być używany do:

- ekstrakcji wzorców,
- klasyfikacji błędów,
- generowania kandydatów,
- analizy trajektorii.

Ale gdzie istnieje wykonywalny test, powinien mieć większą wagę niż estetyczna ocena LLM.

------

# 23. Sleep / consolidation cycle

Można okresowo uruchamiać:

```text
SESSION
   ↓
collect experiences
   ↓
CONSOLIDATION
   ↓
cluster failures
   ↓
extract patterns
   ↓
propose skills
   ↓
validate
   ↓
commit best changes
```

Nie trzeba modyfikować workspace'u po każdym tasku.

------

# 24. Minimalna pętla

Pierwsza wersja powinna być prosta:

```python
for task in tasks:

    result = run_agent(task, workspace)

    experience = record(task, result)

    if result.failed:

        pattern = extract_pattern(experience)

        candidate = propose_skill(pattern)

        if candidate:

            candidate_workspace = apply_candidate(
                workspace,
                candidate
            )

            old_score = evaluate(
                workspace,
                validation_tasks
            )

            new_score = evaluate(
                candidate_workspace,
                validation_tasks
            )

            if passes_gate(old_score, new_score):
                workspace = candidate_workspace
            else:
                rejected.append(candidate)
```

To wystarczy jako pierwszy eksperyment.

------

# 25. Porównuj strategie

Nie zakładaj, że jedna strategia jest najlepsza.

Porównaj:

```text
A. No learning

B. Append-only memory

C. Every failure → heuristic

D. Evidence threshold

E. Procedural consolidation

F. Bounded SkillOpt-style updates

G. Bounded updates + negative memory

H. Bounded updates + procedural families

I. H + selective retrieval
```

Utrzymuj identyczne:

- modele,
- taski,
- budżet,
- validation,
- warunki wykonania.

------

# 26. Mierz

Minimum:

```text
task success rate
first-pass success
repeat-failure rate
regression rate
generalization score
context/token cost
execution cost
active skills
rejected candidates
```

Szczególnie ważne:

### Repeat-failure rate

Czy system przestaje popełniać ten sam typ błędu?

### Generalization

Czy poprawia unseen tasks?

### Regression

Czy nowa wiedza psuje stare zdolności?

### Context cost

Ile kosztuje aktywowanie wiedzy?

------

# 27. Benchmark

Nie opieraj całego eksperymentu na jednym publicznym benchmarku.

Buduj własne zadania:

```text
family A
 ├── train
 ├── validation
 └── hidden

family B
 ├── train
 ├── validation
 └── hidden
```

W miarę możliwości utrzymuj hidden set poza procesem optymalizacji.

Celem jest:

```text
learn pattern
```

a nie:

```text
memorize task
```

------

# 28. Kryterium sukcesu

Self-improving workspace działa, jeśli:

```text
future task quality ↑

while:

context cost controlled
regression controlled
complexity controlled
```

Nie jest dowodem sukcesu:

```text
workspace has more files
```

ani:

```text
LLM generated better-looking instructions
```

Prawdziwy sukces:

> Agent wykonuje przyszłe, wcześniej niewidziane zadania lepiej dzięki zmianom workspace'u.

------

# 29. Kolejność implementacji

## Phase 0 — Audit

Zmapuj obecny workspace.

## Phase 1 — Experience capture

Niezawodnie zapisuj wykonania i rezultaty.

## Phase 2 — Candidate extraction

Experience → pattern → candidate.

Bez automatycznej promocji.

## Phase 3 — Validation gate

Candidate → held-out validation → KEEP/REJECT.

## Phase 4 — Procedural consolidation

Łącz podobne przypadki w procedural families.

## Phase 5 — Bounded updates

Ogranicz rozmiar pojedynczych zmian.

## Phase 6 — Negative memory

Zapamiętuj odrzucone hipotezy.

## Phase 7 — Merge/delete

Pozwól redukować workspace.

## Phase 8 — Selective retrieval

Ładuj tylko relewantne skills.

## Phase 9 — Sleep consolidation

Okresowo konsoliduj doświadczenia.

------

# 30. Research backlog — co zbadać głębiej

Nie traktuj poniższych punktów jako wymagań implementacyjnych. To **otwarte pytania badawcze**, które powinny prowadzić kolejne eksperymenty.

------

## R1. SkillOpt — zbadać mechanizm, nie tylko wyniki

Przeanalizuj dokładnie:

- jak definiowany jest bounded update,
- jak działa validation gate,
- jak przechowywany jest rejected-edit buffer,
- jak działa best-known skill,
- jak wybierana jest wielkość zmiany,
- jak często wykonywane są meta-updates,
- które ablation studies pokazują rzeczywistą przyczynę gainu.

Pytanie:

> Które elementy SkillOpt są konieczne, a które tylko implementacyjne?

Szczególnie porównaj:

```text
SkillOpt
vs
SkillOpt bez negative buffer
vs
SkillOpt bez bounded edits
vs
SkillOpt bez held-out gate
```

------

## R2. CODESKILL — jak wygląda dobra konsolidacja?

Zbadaj:

- jak trajektorie są przekształcane w skills,
- jak system wybiera poziom abstrakcji,
- jak obsługiwane są skills wielopoziomowe,
- jak usuwane są redundant skills,
- jak mierzona jest jakość proceduralnej wiedzy.

Pytanie:

> Czy „skill compilation” jest lepsze od klasycznej episodic memory dlatego, że kompresuje wiedzę, czy dlatego, że zmienia jej reprezentację?

------

## R3. SkillGLoW — procedural families

Zbadaj dokładnie:

- jak powstają rodziny proceduralne,
- kiedy dwa doświadczenia są uznawane za podobne,
- jak działa consolidation,
- jak mierzony jest transfer na unseen tasks,
- jak ograniczana jest liczba aktywnych procedur.

Kluczowe pytanie:

> Jaka jest właściwa jednostka wiedzy: pojedynczy skill, rodzina skillów czy hierarchia procedur?

------

## R4. Evidence threshold

To pozostaje dużą niewiadomą.

Eksperyment:

```text
threshold = 1
threshold = 2
threshold = 3
threshold = 5
```

Mierz:

```text
learning speed
false promotion
generalization
regression
memory size
```

Być może optymalny próg zależy od rodzaju heurystyki.

------

## R5. Czy wszystkie heurystyki powinny mieć ten sam próg?

Prawdopodobnie nie.

Porównaj:

```text
low-risk procedural hint
vs
high-impact workspace change
```

Możliwe, że:

```text
small local skill → low evidence threshold

global workspace rule → high evidence threshold
```

To może prowadzić do **risk-weighted promotion**.

------

## R6. Context optimization

Zbadaj:

```text
all skills
vs
retrieved skills
vs
top-k skills
vs
procedural family only
vs
summary + selected details
```

Mierz:

```text
quality
context tokens
latency
regressions
```

To może być równie ważne jak samo generowanie skills.

------

## R7. Skill granularity

Jaka długość procedury jest najlepsza?

Porównaj:

```text
micro-rules
medium procedures
large playbooks
```

Hipoteza:

> Istnieje optymalny poziom abstrakcji, przy którym skill jest wystarczająco ogólny, ale nadal operacyjny.

------

## R8. Add vs rewrite vs merge vs delete

Zbadaj osobno:

```text
ADD-only
ADD + REVISE
ADD + DELETE
ADD + MERGE
full mutation
```

Mierz długoterminowo:

```text
workspace size
quality
regression
redundancy
```

------

## R9. Negative memory

Sprawdź:

```text
no negative memory
vs
raw rejected candidates
vs
compressed rejection rules
```

Pytanie:

> Czy pamięć błędnych hipotez rzeczywiście zmniejsza ponowne próby złych zmian, czy sama staje się źródłem szumu?

------

## R10. Decay

Porównaj:

```text
never delete
time-based decay
usage-based decay
performance-based decay
periodic revalidation
```

Szczególnie sprawdź rzadko używane, ale wartościowe skills.

------

## R11. Causal attribution

To trudny, ale ważny problem.

Jeżeli po zmianie workspace'u wynik wzrósł, nie wiadomo automatycznie:

> czy wzrost spowodowała właśnie ta zmiana?

Badaj:

```text
A/B workspace versions
paired tasks
rollback experiments
component ablations
```

Celem jest odróżnienie:

```text
correlation
```

od:

```text
causal improvement
```

------

## R12. Interference między skills

Dwie dobre reguły osobno mogą być złe razem.

Testuj:

```text
H1 alone → +5%
H2 alone → +4%
H1 + H2 → -2%
```

Potrzebny może być model:

```text
skill interaction
```

a nie tylko indywidualnego skill score.

------

## R13. Skill composition

Zbadaj, czy agent może bezpiecznie łączyć:

```text
debugging skill
+
API skill
+
testing skill
```

w nową procedurę.

Pytanie:

> Czy self-improvement powinien przede wszystkim odkrywać nowe skills, czy komponować istniejące?

------

## R14. Retrieval jako część uczenia

Możliwe, że agent nie potrzebuje nowych skills.

Być może problem brzmi:

```text
skill already exists
        ↓
agent failed to retrieve it
```

Wtedy właściwą zmianą nie jest:

```text
ADD skill
```

tylko:

```text
IMPROVE retrieval
```

To bardzo ważne rozróżnienie.

------

## R15. Learning from success, nie tylko failure

Nie ograniczaj extraction do:

```text
failure → lesson
```

Badaj:

```text
successful trajectory
        ↓
what made it successful?
        ↓
reusable procedure
```

Szczególnie wartościowe mogą być:

- dobre sekwencje narzędzi,
- skuteczne strategie debugowania,
- dobre kolejności testów,
- skuteczne sposoby eksploracji repozytorium.

------

## R16. Learning from near-misses

Interesujące są przypadki:

```text
task eventually solved
but:
- 20 unnecessary actions
- repeated tool calls
- avoidable error
- excessive context
```

Self-improvement nie musi optymalizować wyłącznie:

```text
success / failure
```

Może optymalizować:

```text
success
+
efficiency
+
robustness
```

------

## R17. Multi-day / sleep learning

Zbadaj prace dotyczące:

- continual learning agentów,
- multi-session coding agents,
- persistent skills,
- long-horizon software development,
- harness evolution.

Pytanie:

> Czy konsolidacja po sesji daje lepsze rezultaty niż ciągłe aktualizowanie workspace'u?

------

## R18. Harness engineering

Zbadaj dokładnie podejście Agentic Harness Engineering.

Szczególnie:

```text
component observability
experience observability
decision observability
```

Sprawdź, które z tych trzech są rzeczywiście potrzebne w małym workspace.

------

## R19. Benchmark contamination

Zbadaj aktualny stan:

- SWE-bench,
- SWE-bench Verified,
- SWE-bench Pro,
- Terminal-Bench,
- prywatnych benchmarków agentów.

Nie zakładaj, że wzrost wyniku publicznego benchmarku oznacza rzeczywistą generalizację.

Preferuj:

```text
fresh tasks
private tasks
held-out tasks
continuously regenerated tasks
```

------

## R20. Model dependence

Sprawdź:

```text
same workspace
    ↓
Model A
Model B
Model C
```

Jeżeli skill poprawia tylko jeden model, może być zbyt mocno dopasowany do jego zachowania.

Jeżeli poprawia kilka modeli:

> jest to silniejszy sygnał, że procedura opisuje właściwość zadania, a nie quirks konkretnego modelu.

------

## R21. Harness dependence

Analogicznie:

```text
same skill
    ↓
Codex
Claude Code
custom harness
```

To pozwala odróżnić:

```text
task knowledge
```

od:

```text
harness-specific instruction
```

------

## R22. Human-written vs LLM-written knowledge

Porównaj:

```text
human heuristic
LLM heuristic
human + LLM refinement
execution-derived heuristic
```

Pytanie:

> Czy najlepsza wiedza jest generowana przez model, czy przez model kierowany przez wykonywalny feedback?

------

## R23. Automated heuristic quality

Zbadaj, czy można automatycznie przewidywać:

```text
will this heuristic help?
```

przed pełną walidacją.

Potencjalne sygnały:

- evidence count,
- novelty,
- specificity,
- similarity to existing skills,
- historical success of source pattern,
- expected context cost,
- scope,
- risk.

To może stworzyć **pre-validation filter**.

------

## R24. Risk-weighted self-improvement

Nie wszystkie workspace changes są równoważne.

Rozważ klasy:

```text
R0 — local wording
R1 — local skill
R2 — retrieval rule
R3 — global instruction
R4 — tool behavior
R5 — execution / deployment logic
```

Im wyższy risk:

```text
→ większy evidence requirement
→ silniejsza walidacja
→ mniejszy update budget
→ mocniejszy rollback
```

------

## R25. Czy potrzebujemy „trust tiers”?

Obecna architektura może nie potrzebować pełnych sześciu poziomów.

Najpierw sprawdź prostszy model:

```text
IMMUTABLE
    ↓
ACTIVE
    ↓
CANDIDATE
    ↓
REJECTED
```

Dopiero jeśli eksperymenty pokażą potrzebę, dodawaj więcej warstw.

------

# 31. Priorytet researchu

Nie badaj wszystkiego naraz.

### P0 — najważniejsze

```text
SkillOpt bounded updates
SkillOpt validation gate
SkillGLoW procedural families
CODESKILL skill compilation
held-out generalization
context/retrieval cost
```

### P1

```text
negative memory
skill granularity
add vs merge vs delete
evidence thresholds
skill interference
best-known workspace
```

### P2

```text
decay
causal attribution
multi-day learning
model/harness transfer
risk-weighted promotion
```

------

# 32. Najważniejszy eksperyment

Po implementacji minimalnej wersji uruchom:

```text
                    SAME TASK STREAM
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
       baseline        simple memory     SkillOpt-style
          │                │                │
          └────────────────┼────────────────┘
                           ↓
                  held-out evaluation
                           ↓
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
       quality        generalization    context cost
```

Następnie wykonaj ablation:

```text
SkillOpt-style
     ↓
- bounded updates
- validation
- negative memory
- procedural families
- selective retrieval
```

To pokaże, **co rzeczywiście powoduje poprawę**.

------

# 33. Docelowy model

Najbardziej obiecująca architektura na podstawie obecnych wyników researchu:

```text
                    REAL TASK
                        │
                        ▼
                 ┌─────────────┐
                 │ TARGET AGENT│
                 └──────┬──────┘
                        │
                  execution
                        │
                        ▼
                 ┌─────────────┐
                 │ EXPERIENCE  │
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   PATTERN   │
                 │   MINING    │
                 └──────┬──────┘
                        │
                        ▼
               procedural family
                        │
                        ▼
                 ┌─────────────┐
                 │ CANDIDATE   │
                 │    SKILL    │
                 └──────┬──────┘
                        │
                 bounded update
                        │
                        ▼
                 ┌─────────────┐
                 │ VALIDATION  │
                 └──────┬──────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           REJECT                KEEP
              │                   │
              ▼                   ▼
       negative memory       BEST WORKSPACE
                                  │
                                  ▼
                           selective retrieval
                                  │
                                  ▼
                              NEXT TASK
                                  │
                                  └──────→ feedback
```

------

# 34. Ostateczne zasady

```text
1. Learn from execution, not imagination.

2. Experience is not a skill.

3. Generalize before promoting.

4. Small changes beat unrestricted rewrites.

5. Validate on unseen tasks.

6. Keep a best-known workspace.

7. Rejected changes are evidence.

8. Skills can be merged, revised and deleted.

9. More context is not automatically better.

10. Measure downstream performance, not memory size.

11. Separate optimizer from target agent.

12. Prefer executable tests over LLM judgement.

13. Optimize for useful knowledge, not maximum knowledge.

14. Preserve rollback.

15. Treat every workspace modification as a hypothesis.

16. Test generalization, not memorization.

17. Measure context cost.

18. Investigate retrieval failures separately from knowledge failures.

19. Prefer procedural compression over episodic accumulation.

20. Let experiments decide which heuristics survive.
```

# 35. Ostateczny cel

Nie buduj systemu, który:

> „sam sobie zmienia instrukcje”.

Buduj system, który potrafi:

```text
DO
→ OBSERVE
→ GENERALIZE
→ PROPOSE
→ TEST
→ KEEP / REJECT
→ CONSOLIDATE
→ RETRY
```

i który z czasem ma coraz lepszy **stosunek jakości wyników do ilości wiedzy, kosztu kontekstu i ryzyka regresji**.

Najważniejszą własnością systemu nie jest autonomia.

Jest nią **zdolność do udowodnienia, że konkretna zmiana workspace'u poprawiła przyszłe wykonanie**.