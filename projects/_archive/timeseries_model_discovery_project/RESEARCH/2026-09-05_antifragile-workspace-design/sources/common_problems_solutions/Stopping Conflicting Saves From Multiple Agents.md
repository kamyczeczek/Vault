---
type: Concept
title: Stopping Conflicting Saves From Multiple Agents
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Tak naprawdę ten post jest o **warstwowaniu zabezpieczeń w środowisku, w którym kilka agentów AI jednocześnie modyfikuje repozytorium Git**.

### Co autor faktycznie zrobił

Schemat jest mniej więcej taki:

```text
                 Agent A ──┐
                 Agent B ──┼──> wspólne repo
                 Agent C ──┘
                           │
                    ┌──────▼──────┐
                    │ Git worktree│
                    │  per agent  │
                    └──────┬──────┘
                           │
                    branch != main
                           │
                    ┌──────▼──────┐
                    │ Git hook    │
                    │ "NO COMMIT  │
                    │  TO MAIN"   │
                    └──────┬──────┘
                           │
                    permission layer
                    / approval gate
                           │
                         human
```

Problemem nie jest więc samo Git, tylko **kontrola autonomicznych agentów wykonujących operacje w tym samym repo**.

Git ma do tego natywne mechanizmy: `git worktree` pozwala mieć wiele niezależnych working trees dla jednego repozytorium, a Git pilnuje m.in., żeby zwykłe `worktree add` nie pozwoliło dwóm worktree'om jednocześnie checkoutować tej samej gałęzi. ([Git](https://git-scm.com/docs/git-worktree?utm_source=chatgpt.com))

### Najważniejsza obserwacja autora jest słuszna

Instrukcja:

> „Never work directly on main.”

jest **soft constraint**.

Agent może ją przeczytać, zinterpretować i mimo wszystko uznać, że „tym razem to tylko dokument, więc nic się nie stanie”.

Hook jest czymś innym: to **mechanical enforcement**.

Np. `pre-commit` może sprawdzić bieżącą gałąź i zakończyć się kodem != 0, przez co Git nie utworzy commita. Git oficjalnie opisuje właśnie taki mechanizm dla `pre-commit`. ([Git](https://git-scm.com/docs/githooks?utm_source=chatgpt.com))

To jest generalnie bardzo dobra zasada dla agentów:

> **Instrukcja mówi agentowi, co powinien zrobić. Mechanizm egzekwujący określa, czego nie może zrobić.**

### Ale jest istotna dziura w rozwiązaniu

Autor trochę przecenia `pre-commit`.

Taki hook chroni przed:

```bash
git commit
```

ale **nie chroni przed samym zmodyfikowaniem `main`**.

Agent może zrobić:

```bash
git checkout main
echo "..." > important-file.md
```

i `pre-commit` jeszcze się nie uruchomi.

Może też próbować ominąć hook przez:

```bash
git commit --no-verify
```

Git wprost dokumentuje, że `pre-commit` można ominąć przez `--no-verify`. Git FAQ wręcz ostrzega, że lokalne hooki nie powinny być traktowane jako rzeczywisty mechanizm egzekwowania polityki. ([Git](https://git-scm.com/docs/gitfaq?utm_source=chatgpt.com))

Dlatego zrobiłbym to **warstwowo**.

### Lepsza architektura

**1. Worktree = izolacja**

Każdy agent dostaje:

```text
repo/
├── main/          ← stabilny stan
├── agent-a/       ← feature/agent-a
├── agent-b/       ← feature/agent-b
└── agent-c/       ← feature/agent-c
```

To jest dokładnie przypadek użycia `git worktree`. ([Git](https://git-scm.com/docs/git-worktree?utm_source=chatgpt.com))

**2. Agent startup check = wykrywanie błędu**

Przed rozpoczęciem pracy:

```bash
test "$(git branch --show-current)" != "main"
```

Jeżeli jesteś na `main` → agent ma się zatrzymać.

**3. Git hook = dodatkowa bariera**

`pre-commit`:

```text
if branch == main:
    reject
```

To chroni przed przypadkowym commitem.

**4. Permission layer = ochrona operacji wysokiego ryzyka**

Operacje typu:

```bash
git reset --hard
git clean -fd
git checkout .
git push --force
```

powinny wymagać approval albo być całkowicie zabronione agentowi.

I właśnie ten fragment z posta jest ciekawy: agent został zatrzymany **nie przez instrukcję w kontekście, lecz przez niższą warstwę kontroli**.

**5. Remote/CI = ostateczna granica**

Jeżeli naprawdę chcesz zagwarantować:

> „nikt nie może zmienić main”

to lokalny hook nie wystarcza. Politykę należy egzekwować na serwerze/CI — Git sam wskazuje `pre-receive`/CI jako właściwe miejsce dla rzeczywistego enforcementu. ([Git](https://git-scm.com/docs/gitfaq?utm_source=chatgpt.com))

------

## I jest jeszcze jeden ważny problem: „hook istnieje” ≠ „hook działa”

To moim zdaniem **najciekawsza część całego posta**.

Autor odkrył, że konfiguracja repo powodowała, że hook przestał być wykonywany. Git podaje, że hooki muszą być executable, a ich lokalizacja może być zmieniona przez `core.hooksPath`. ([Git](https://git-scm.com/docs/githooks?utm_source=chatgpt.com))

Czyli potencjalnie miał:

```text
.git/hooks/pre-commit
        ↓
plik istnieje
        ↓
"wszystko wygląda dobrze"
        ↓
hook w rzeczywistości NIE działa
```

Dlatego test:

```text
spróbuj celowo złamać regułę
        ↓
system powinien odmówić
        ↓
jeżeli odmówił → fence działa
```

jest znacznie lepszy niż:

```text
ls .git/hooks
        ↓
plik jest
        ↓
"OK"
```

To jest w praktyce **negative testing / adversarial testing**.

------

# Czy to jest dobre rozwiązanie dla wielu agentów?

**Tak, ale nie jako pojedynczy hook.**

Najlepszym wzorcem jest:

| Warstwa                   | Funkcja                                             |
| ------------------------- | --------------------------------------------------- |
| `git worktree`            | fizyczna izolacja agentów                           |
| osobna branch per agent   | izolacja historii                                   |
| agent instructions        | informowanie agenta                                 |
| startup validation        | wykrywanie złego środowiska                         |
| Git hooks                 | automatyczne blokowanie części błędów               |
| permission/approval layer | blokowanie niebezpiecznych operacji                 |
| CI / protected branch     | ostateczne egzekwowanie polityki                    |
| adversarial tests         | sprawdzanie, czy zabezpieczenia faktycznie działają |

To jest zresztą zgodne z szerszym kierunkiem rozwoju agentic coding: współczesne środowiska coraz częściej traktują **worktrees, izolację, approval gates i mechanizmy weryfikacji** jako element infrastruktury agenta, a nie tylko instrukcje promptowe. ([Cursor](https://cursor.com/blog/agent-best-practices?utm_source=chatgpt.com))

### Jedna rzecz, z którą bym polemizował w poście

Zdanie:

> „this is the answer, not a workaround”

jest trochę zbyt mocne.

To jest **dobry element rozwiązania**, ale nie pełne rozwiązanie problemu konfliktów między agentami.

Worktree rozwiązuje przede wszystkim **izolację filesystemu/branchy**. Nie rozwiązuje automatycznie konfliktów logicznych:

```text
Agent A → zmienia API
Agent B → zmienia tego samego konsumenta API
```

Oba mogą pracować perfekcyjnie w swoich worktree'ach, zrobić poprawne commity, a problem pojawi się dopiero przy merge'u.

Dlatego właściwym określeniem byłoby:

> **„Nie próbuj zmuszać agenta do pamiętania krytycznych reguł. Egzekwuj je na poziomie infrastruktury.”**

I to jest sedno tego posta.

Jeżeli przez **„ICM structure”** autor ma na myśli konkretną architekturę/produkt (a nie po prostu strukturę repo), mogę też rozebrać ten post na części i pokazać **dokładnie, jak zbudować taki multi-agent + worktree + hooks setup, włącznie z przykładowym `.git/hooks/pre-commit` i strukturą katalogów**.