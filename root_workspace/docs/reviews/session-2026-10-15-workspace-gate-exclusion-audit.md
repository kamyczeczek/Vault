# Workspace-Gate Exclusion Audit — review of commit `66fdb50` — 2026-10-15

**Werdykt: naprawa nie była gamingiem, ale też nie była udokumentowanym dryfem.**
Exclusion jest obronny w zasadzie (expected to faktycznie jedyna sesja
*zaimplementowana*, nie *opisywana*), ale reguła wykluczenia nie została
ani zapisana, ani zastosowana konsekwentnie, a okno metryki się kurczy.
**Revert `66fdb50` nie jest potrzebny.** Potrzebna jest hartacja case'a.

Kontynuacja `session-2026-10-15-memory-eval-and-guards-decision.md` (raport
sesji naprawy) i `session-2026-10-14-guard-wiring-audit.md` (audyt guardów) —
nie duplikuje ich; tutaj tylko audyt decyzji exclusion.

## 1. Pomiar przed/po — delata MRR w pełni explained

Zmierzono replikując logikę eval na pliku case'ów z wykluczeniami
zachowanymi (A) i usuniętymi dla case'u `workspace gate` (B).

| Stan | hit@5 | MRR | pass | RR case'u |
|---|---|---|---|---|
| A — po `66fdb50` | 1.000 | 0.689 | 15/15 | 1.0 (rank 1) |
| B — przed `66fdb50` | 0.933 | 0.622 | 14/15 | 0.0 (poza oknem) |

Różnica MRR to dokładnie 1.0/15 = 0.0667 ≈ zaobserwowane 0.067. **Cały skok
MRR pochodzi z tego jednego case'u**, żaden inny case się nie ruszył.
To zamyka pytanie z poprzedniego review, czy skok 0.067 może maskować
zmiany gdzie indziej — nie może.

## 2. Które sesje wykluczono i czy są confounderami

Cztery `session_ids` dla case'u `workspace gate`:
`01a13bd8-c860…`, `01a13bb8-f36b…`, `fe3a511b-90cd…`, `01a13271-f5f3…`

Kryterium z instrukcji: sesja jest confounderem, jeśli ma keyword, ale
**nie** zawiera opisu/definicji/odpowiedzi. Sprawdzono zawartość chunków
każdej wykluczonej sesji (nie tylko heading, który trafił do top-5):

| Sesja | Chunki z oboma słowami | Zawiera opis/definicję? | Werdykt |
|---|---|---|---|
| `01a13bd8` | 13 | **TAK** — cel `check_workspace_integrity.py` („wszechstronny skrypt sprawdzający spójność workspace'u: bramki Q0/Q1, stan handoff, brak kolizji case-folded") + kryteria akceptacji exit 0/exit 1 + pełne źródło hooka `pre-commit` | **nie jest czystym confounderem** |
| `01a13bb8` | 20 | **TAK** — kontrakt bramki („musi przechodzić bez wpisów w `ALLOWED_ROOT`, których nie ma w `CLAUDE.md`") + procedura naprawy + realny output FAIL bramki | **nie jest czystym confounderem** |
| `01a13271` | 15 | **TAK** — procedura weryfikacji R20 wewnątrz bramki + oczekiwane zachowanie (cicho przejdzie / FAIL) | **nie jest czystym confounderem** |
| `fe3a511b` | 43 | **NIE** — wywołania bramki jako tool call i listy plików; jeden chunk to meta-dyskusja retrievalowa (czy `check_workspace_integrity` ma być frazą czy workiem podtokenów) | **najbliższy prawdziwemu confounderowi**, ale sesja ta też modyfikowała skrypt |

Wniosek: kryterium „NIE zawiera opisu/definicji/odpowiedzi" z instrukcji
**nie jest spełnione dla trzech z czterech** wykluczonych sesji.

## 3. Ale expected ma coś, czego nie ma żadna z nich

`01a0f9c0-113b` zawiera **źródło samej bramki** — `def main() -> int:`
z listą wywołań `check_rN_*` (w tym `check_r10_open_work_integrity()`)
oraz maszynę `FAILS`/`WARNS`. Żadna z czterech wykluczonych sesji tego nie
ma: one bramkę *odwołują, wywołują, weryfikują lub opisują*, ale jej nie
*definiują*.

To jest realne, obronne rozróżnienie — implementacja vs. referencja. Właśnie
ono uzasadnia exclusion. **Sesja go nigdy nie zapisała.**

## 4. Dwa defekty samej naprawy

### 4a. Okno metryki zmalało z 5 do 4 bez zapisu

Eval pobiera `limit + len(excluded)` wierszy, potem filtruje. Tu
`01a13bd8` zajmuje **dwa** miejsca w rankingu (dwa chunki), więc cztery
wykluczone ID usunęły **pięć** wierszy, a ewaluowanych zostało **cztery**.
Case deklaruje `hit@5`, a mierzy `hit@4`. Dla MRR tego case'u to bez znaczenia
(expected jest na rank 1), ale etykieta metryki jest nieprawdziwa i bufor
`limit + len(excluded)` jest heurystyką, nie gwarancją.

### 4b. Reguła wykluczenia niespójna — to jest najpoważniejszy finding

Heading `# Import ALLOWED_ROOT from check_workspace_integrity.py` jest
niesiony przez **trzy** sesje z tej samej nocy:

| Sesja | Data | Status |
|---|---|---|
| `01a13bb8-f36b…` | 2026-10-14 20:46 | EXCLUDED |
| `01a13bbf-0283…` | 2026-10-14 20:52 | kept |
| `01a13bc5-2b83…` | 2026-10-14 20:59 | kept |

Wykluczono **najstarszą** z trzech, a dwie nowsze zostawiono — przy czym
`01a13bc5` siedzi w ewaluowanym oknie na ranku 3, tuż pod expected.
Jeśli `01a13bb8` jest confounderem, to jej rodzeństwo z bajtowo identycznym
headingu też. Jeśli nie — wykluczenie było arbitralne. **Nie ma reguły,
która wyklucza jedno rodzeństwo i zostawia drugie.**

To jest też sprzeczne z narracją „nowsze wypierają kanoniczną": gdyby tak
było, wykluczenia by wymagały wszystkich trzech, a nie najstarszego.

## 5. Co to znaczy dla S62

Instrukcja rozróżniała dryf (legalny, precedens R15) od gamingiu
(expected jest nieaktualne, wykluczamy nowe, żeby stare wygrywało).

- **Gaming? Nie.** Expected faktycznie implementuje bramkę; wykluczone sesje
  jej nie definiują. Wykluczenie nie służyło utrzymaniu przy życiu
  nieaktualnej odpowiedzi.
- **Dryf udokumentowany? Też nie.** Dryf to „nowe sesje wypierają kanoniczną".
  Tu część wykluczonych sesji zawiera częściowe odpowiedzi, a reguła została
  zastosanej do jednego z trzech identycznych rodzeństw. To nie jest
  opis zjawiska — to ręczne tuningowanie do zielonego wyniku.

Prawidłowa etykieta: **niedokumentowane, nieodtwarzalne dostrojenie**
(undocumented, non-reproducible tuning), nie regresja i nie gaming.

## 6. Konsekwencja: case jest kruchy

Exclusion jest listą na sztywno. Każda nowa sesja, która wspomni bramkę,
znowu wypchnie expected poza okno — i następny agent znów będzie musiał
doklejać ID bez reguły. Case nie testuje retrievalu; testuje, czy lista
wykluczeń jest aktualna.

## 7. `agent_commit.py` — finding zamknięty, brak over-claimu

Plik **istnieje**: `projects/_archive/agentic-research-lab/scripts/agent_commit.py`
(z `unstage()` w linii 58, test `tests/test_agent_commit.py`). Dokumenty roota
atrybuują go poprawnie do ARL — `handoff/state_description/sessions/22_pi…md`
mówi wprost „in ARL `scripts/agent_commit.py`". Wniosek K3 poprzedniej sesji
był więc słuszny. Dwie wzmianki nie nazywają repo (`AGENTS.md`, deep note
`gotchas-that-cost-time…`), ale są one przykładami w zdaniu, nie asercją
istnienia pliku w roocie. **Brak akcji.**

## 8. Next step

Jeden krok: **hartacja case'u `workspace gate`**, bez doklejania kolejnych ID:
zapisać regułę wykluczenia (implementacja vs. referencja) i albo zastosować
ją konsekwentnie do wszystkich rodzeństw, albo porzucić listę na rzecz
innego kryterium. Osobno: wdrożenie Opcji A guardów (decyzja właściciela,
jeszcze niewdrożona).

## Tool calls

| Wartość | Komenda | Surowy output (fragment) |
|---------|---------|--------------------------|
| 1.000 | `python scripts/eval_memory_retrieval.py` | `hit@5=1.000` |
| 0.689 | `python scripts/eval_memory_retrieval.py` | `MRR=0.689 (15/15)` |
| 15/15 | `python scripts/eval_memory_retrieval.py` | `(15/15)` |
| 0.933 | `python scripts/_scratch/audit_prefix_mrr.py` | `hit@5=0.933` |
| 0.622 | `python scripts/_scratch/audit_prefix_mrr.py` | `MRR=0.622 (14/15)` |
| 14/15 | `python scripts/_scratch/audit_prefix_mrr.py` | `(14/15)` |
| 0.067 | `python scripts/_scratch/audit_prefix_mrr.py` | `MRR=0.622` vs `MRR=0.689` |
| 6 | `python scripts/_scratch/audit_workspace_gate_exclusions.py` | `expected ranks (unfiltered): [6, 10, 15]` |
| 9 | `python scripts/_scratch/audit_exclusion_metric_integrity.py` | `eval fetches limit=9 (k 5 + 4 excluded)` |
| 5 | `python scripts/_scratch/audit_exclusion_metric_integrity.py` | `rows removed by exclusion: 5` |
| 4 | `python scripts/_scratch/audit_exclusion_metric_integrity.py` | `rows actually evaluated: 4` |
| 4 | `python scripts/_scratch/audit_exclusion_metric_integrity.py` | `carried by 3 session(s)` → 4 IDs w `exclude_session_ids` |
| 3 | `python scripts/_scratch/audit_exclusion_metric_integrity.py` | `carried by 3 session(s)` |
| 13 | `python scripts/_scratch/audit_excluded_session_content.py` | `chunks containing BOTH … : 13` (01a13bd8) |
| 20 | `python scripts/_scratch/audit_excluded_session_content.py` | `chunks containing BOTH … : 20` (01a13bb8) |
| 43 | `python scripts/_scratch/audit_excluded_session_content.py` | `chunks containing BOTH … : 43` (fe3a511b) |
| 15 | `python scripts/_scratch/audit_excluded_session_content.py` | `chunks containing BOTH … : 15` (01a13271) |
| 16 | `python scripts/_scratch/audit_excluded_session_content.py` | `chunks containing BOTH … : 16` (01a0f9c0-113) |
| 1272 | `python scripts/_scratch/audit_excluded_session_content.py` | `total chunks in session: 1272` |
| 249 | `python scripts/_scratch/audit_excluded_session_content.py` | `total chunks in session: 249` |
| 127 | `python scripts/_scratch/audit_excluded_session_content.py` | `total chunks in session: 127` |
| 203 | `python scripts/_scratch/audit_excluded_session_content.py` | `total chunks in session: 203` |
| 125 | `python scripts/_scratch/audit_excluded_session_content.py` | `total chunks in session: 125` |
| 10580 | `ls -la projects/_archive/agentic-research-lab/scripts/agent_commit.py` | `10580 Oct  5 18:54` |
| 58 | `grep -n "def unstage" …/agent_commit.py` | `58:def unstage(paths: list[str]) -> None:` |
| 33 | `python scripts/check_workspace_integrity.py` | `workspace root holds 33 declared entries` |
| 0 | `python scripts/check_workspace_integrity.py; echo $?` | `EXIT=0` |
| 8 | `git show 66fdb50 --stat` | `8 files changed, 523 insertions(+), 24 deletions(-)` |
| 523 | `git show 66fdb50 --stat` | `523 insertions(+)` |
| 24 | `git show 66fdb50 --stat` | `24 deletions(-)` |

not checked:
- Czy `01a13bd8`, `01a13bb8`, `01a13271` powinny zostać uznane za *pełne*
  odpowiedzi (a nie częściowe) — audyt ustalił, że zawierają opisy, ale nie
  oceniał, czy te opisy są wystarczająco kanoniczne, by wygrać z expected.
  Wymaga to decyzji właściciela o definicji case'u.
- Czy hartowana wersja case'u (usunięcie listy exclusion na rzecz reguły)
  przejdzie — nie wdrażano w tej sesji.
- Wdrożenie Opcji A guardów — decyzja podjęta, nie zaimplementowana.
- Czy `fe3a511b` modyfikowała bramkę w sposób zmieniający jej definicję
  (widać ją w liście `modified`, nie przeczytano diffa).
