# HANDOFF — workspace root

> **GENEROWANE — nie edytuj ręcznie.** `python scripts/build_handoff.py`
> buduje ten plik z `handoff/flags/*.md` + `handoff/deep/*.md`.
> Kontrakt (kto pisze co): `handoff/CONTEXT.md`. Stan maszynowy: `STATE.md`.

Portable state for a cold session entering at the workspace root. Per D12 this
file carries only what is true across projects; the project-local handoff carries
the detail and is linked, never copied. The prose that used to sit here by hand
now has its home in `handoff/flags/` (one flag = one file = one writer) and is
inlined below by the builder.

## How to update

One flag = one file: `handoff/flags/<flag>.md`, frontmatter `flag` / `since` /
`owner` / `agent` / `model` + the entry body. Write **only** the flag you own
(or the one your task retired); never edit another flag's prose — that is what
made the old single-file handoff clobber under two agents. Then rebuild this
view:

```
python scripts/build_handoff.py           # regenerate
python scripts/build_handoff.py --check   # gate form: exit 1 if stale
```

This file is state, not a journal: replace or retire a flag whose claims
stopped holding (delete the file), and compress closed threads into
`handoff/deep/`. Project-local detail is linked, never copied (D11/D12).

## Status

<!-- handoff/flags/pi-subagents-hardening-and-e2e-2026-11-04.md · owner: mateusz · agent: opencode · model: omniroute/agy/gemini-3.8-flash-low -->
`pi-subagents-hardening-and-e2e-2026-11-04` — 2026-11-04: Hardened preflight_agent.py (read-only by default, --clean-stale-locks explicit flag, active git process protection before removing index.lock, git hook configuration check HOOK_ACTIVE/HOOK_INACTIVE). Updated CLAUDE.md to resolve gate caller contradiction and updated .pi/agents definitions for preflight-runner and handoff-closer. Added support in close.py for multiple --include flags. Added unit tests in test_preflight_agent.py (9/9 pass) and created hermetic E2E test in test_handoff_closer_e2e.py verifying dirty tree stray detection and full transaction execution. Subagent handoff-closer live run verified.
not checked: —

<!-- handoff/flags/pi-agents-preflight-and-closer-2026-11-04.md · owner: mateusz · agent: opencode · model: omniroute/agy/gemini-3.8-flash-low -->
`pi-agents-preflight-and-closer-2026-11-04` — 2026-11-04: Added project-level Pi subagents in .pi/agents/ (preflight-runner and handoff-closer) and verified preflight-runner execution; captured raw_sessions_drive.bat default count update.
not checked: handoff-closer subagent full transaction run on a dirty tree.

<!-- handoff/flags/orchestrator-worker-recursion-2026-11-03.md · owner: mateusz · agent: opencode · model: omniroute/gemini/gemini-flash-lite-latest -->
`orchestrator-worker-recursion-2026-11-03` — 2026-11-03: D25 PENDING: recursion E2E did not reach GRANDCHILD-OK-7731; observed 401 provider authentication error via local proxy, not evidence of toolscope or depth cap. tools/orchestrator.md remains a hypothesis.
not checked: provider key rotation and repeat E2E.

<!-- handoff/flags/latest-session-export.md · owner: mateusz · agent: opencode · model: omniroute/gemini/gemini-flash-lite-latest -->
`latest-session-export` — 2026-11-03: Exporter now merges Pi, OpenCode, OMP, and DSH sessions and selects the requested count globally by last activity; Drive wrapper syncs the generated file to G:\My Drive.
not checked: remote Google Drive propagation latency after local copy.

<!-- handoff/flags/fev-full-guard-implemented.md · owner: mateusz · agent: opencode · model: omniroute/gemini-flash-lite-latest -->
`fev-full-guard-implemented` — 2026-11-03: Implemented and tested FEV-full guard / hard stop protocol in benchmark-core (bench.py & test_benchmark_protocol.py), all 42 tests passing successfully.

not checked: none — all protocol tests executed and passed.

<!-- handoff/flags/benchmark-core-phase1b-freeze-2026-11-02.md · owner: mateusz · agent: opencode · model: omniroute/agy/claude-opus-4-6-thinking -->
`benchmark-core-phase1b-freeze-2026-11-02` — 2026-11-02: Phase 1 + 1b of the v2
multi-domain generalization protocol is complete and frozen.

Stan:
- **PROTOCOL.md** (304 linie, §0–§15): normatywny dokument v2 zamrożony. Hierarchia
  normatywna (Protokół > Proces > Raport), 3 bramki decyzyjne, populacja N≤8,
  budżet czasu 20 min/metoda, lockbox 42 zadań z limitem 3 użyć, reguły STOP,
  audyt niezależny w §9, rejestr poprawek A1–A4.
- **Manifest zamrożony** (`manifest_sha256 = 34b35abc…b42da`): 20 Dev / 38 kwarantanna /
  42 Lockbox = 100 zadań pełnego zbioru fev-bench. Twarde odcięcie rodzeństwa (15 rodzin
  Dev ∩ Lockbox = ∅, ETT ∉ Lockbox). Lockbox pokrywa 5 z 7 domen (brak cloud, nature).
  247 kolumn targetu × 3 okna = 741 jednostek; 2767 serii, 8301 ewaluacji item × okno.
- **Ledger** (`ledger.jsonl`): Genesis + A1–A4, łańcuch SHA-256 integralny (audit_v2 CLEAN).
- **Moduły bazowe**: `manifest.py` (klasyfikacja rodzin/domen, odcięcie rodzeństwa,
  3 ostatnie okna), `metrics.py` (MASE, clipping [0.01,100], skill score),
  `bootstrap.py` (klaster po 15 rodzinach B=10000, iid, stratyfikowany),
  `ledger.py` (append-only kanoniczny JSON, SHA-256 chain), `guards.py` (Gate 1–3,
  populacja, STOP), `audit_v2.py` (niezależny audyt proceduralny §9).
- **Skan mianowników MASE** (`scan_denominator_anomalies.py`): 20/20 zadań, 0 itemów
  z zerowym błędem sezonowym → brak wykluczeń w manifeście.
- **Testy**: 11 passed (`test_benchmark_v2.py`), czas <4s.
- **Poprawki docs**: CLAUDE.md (9 nowych wpisów w tabelach Where/Route), CONTEXT.md
  (bench.py --fev RESOLVED), MAP.md (10 nowych modułów w mapie).
- Dwie wycofane flagi: `benchmark-core-fev-honest-2026-10-26` (zastąpiona pełną fazą 1b),
  `benchmark-core-full-tests-2026-10-29` (zastąpiona bieżącą fazą).
- Wszystkie punkty z recenzji planu v2 wprowadzone: r=100 dla timeoutów (§6), kontrast
  vs Champion (§4 Bramka 2/3), §9 „ma zakaz", MDE w Fazie 1b (§14), Amendment A2,
  „46 konfiguracji" → 42 zadania (A1).

Weryfikacja:
- `python audit_v2.py` → verdict: CLEAN (0 hard findings), chain intact, partition 100.
- `pytest test_benchmark_v2.py` → 11 passed in 3.13s.
- `python scripts/check_workspace_integrity.py` → OK (36 declared entries, 7 projects).
- `git diff --check` → exit 0.

not checked: mapowanie domen vs papier fev-bench (Appendix E/Tabela 15) — weryfikacja
manualna; pełen suchy przebieg SNaive/NLinear/DLinear na Dewie (Faza 1b checklist §14);
analiza mocy i MDE; budżet ściany Lockboxa; `s44_calib_insample_failed.log` nie został
skopiowany z $env:TEMP do etth1-h720/results/ (plik istnieje, 4520B, nie jest w repozytorium).

Next step: suchy przebieg Seasonal Naive + NLinear + DLinear na 20 zadaniach Dev (3 okna
każde), pomiar czasu i wyznaczenie MDE. To otwiera Fazę 2 (populacja startowa, dashboard).

<!-- handoff/flags/benchmark-core-phase1b-dev-analysis-2026-11-02.md · owner: mateusz · agent: opencode · model: omniroute/gemini/gemini-flash-lite-latest -->
`benchmark-core-phase1b-dev-analysis-2026-11-02` — 2026-11-02: Faza 1b na Dev (suchy przebieg baselines: SeasonalNaive, NLinear, DLinear) zakończona i zweryfikowana.

Stan:
- Przebieg 20/20 zadań Dev (3 okna każde, total 1359.0 s) wykonany w pełni; 19 wspólnych zadań bit-identycznych z Run 1 (`compare_runs.py` OK).
- Czasy dopasowań i budżet: SeasonalNaive (11.1 s, mediana 0.015 ms), NLinear (233.5 s, mediana 10.9 ms, p95 144.2 ms), DLinear (712.2 s, mediana 35.9 ms, p95 478.5 ms). Wszystkie mieszczą się w budżecie 20 min/model.
- Skill score vs SNaive: NLinear +14.88% (dolne CI +3.75%, passes gate), DLinear +12.08% (dolne CI -0.63%).
- Analiza MDE i Bootstrap: Klaster bootstrap (B=10,000, 15 rodzin, alpha=0.05). MDE dla NLinear vs SNaive = 0.1781 (halfwidth 0.1114).
- Weryfikacja mianowników MASE: Zadania z MASE > 3 zweryfikowane — zero itemów z zerowym błędem.

Weryfikacja:
- python scripts/check_workspace_integrity.py → OK.
- git diff --cached --check → exit 0.

not checked: pełny lockbox (skażony A6); optymalizacja hiperparametrów NLinear/DLinear; przebieg testowy (quarantine/test partition).

Next step: Decyzja o przejściu do Fazy 2 (populacja startowa, dashboard) lub dalsze kroki badawcze.

<!-- handoff/flags/benchmark-core-lockbox-a6-disclosure-2026-11-02.md · owner: mateusz · agent: opencode · model: omniroute/agy/claude-opus-4-6-thinking -->
`benchmark-core-lockbox-a6-disclosure-2026-11-02` — 2026-11-02: A6 ujawnia
skażenie Lockboxa (36/42 zadań) i unieważnia możliwość przesegregowania.

Stan:
- **A5 kłamało w punkcie (ii)**: twierdziło, że nie da się ustalić, co policzył
  przerwany legacy przebieg `--fev-full` z 2026-10-30. Da się — log przeżył
  w `%TEMP%/fev-full.log` (959 linii, zapis 00:26–01:50), z nagłówkami
  `-- task N/100` do pozycji 74. Przebieg policzył 73 zadania w całości
  i zadanie 74 częściowo.
- **Skala skażenia**: po `task_id` z `results/manifest.json` (indeks == pozycja−1)
  to **36 z 42 zadań Lockboxa**, 17 z 21 rodzin, wszystkie 5 domen. Skażone
  indeksy: 7–9, 17–30, 35–37, 40–42, 45–49, 56, 62, 63, 65–69.
  Nietknięte: `task_id` 76, 92, 93, 94, 95, 99 (4 rodziny: `ecdc_ili`,
  `fred_md`, `fred_qd`, `gvar`; 2 domeny: econ, healthcare).
- **Przesegregowanie jest niewykonalne** i nie zostało wykonane: `verify_manifest`
  wymaga, by kwarantanna zawierała wyłącznie rodzeństwo rodzin Dev, a Lockbox
  wyłącznie rodziny nie-Dev (plus zakaz ETT). Skażone zadanie Lockboxa nie może
  więc trafić do kwarantanny, a w kwarantannie nie ma czym uzupełnić Lockboxa.
  Próba obejścia tego wymagałaby zmiany niezmiennika, nie danych — dlatego STOP.
- **A6 w ledgerze** (7 wpisów, łańcuch SHA-256 zweryfikowany, manifest
  `34b35abc…b42da` bez zmian) + wiersz A6 w rejestrze §15 `PROTOCOL.md`
  i akapit o zakazie używania Lockboxa do czasu A7.
- Skrypt zapisujący A6 leży w `projects/_archive/benchmark-core-apply-a6.py`,
  bo audyt `isolation.no_lockbox_configs_in_runtime` słusznie zgłosił nazwy
  konfiguracji Lockboxa w kodzie runtime — audyt **nie** został poszerzony.

Weryfikacja:
- `python audit_v2.py` → `verdict: CLEAN (0 hard findings)`, 56 plików runtime.
- `pytest test_benchmark_v2.py` → 18 passed in 2.97s.
- `ledger.verify_integrity(expected_manifest_sha256=…)` → OK, 7 wpisów.
- `git diff --check` → exit 0.

Next: decyzja właściciela o §8 jako A7, jeden z trzech wariantów:
(a) Lockbox = 6 nietkniętych zadań, świadomie bez mocy statystycznej;
(b) 42 zadania zostają jako diagnostyka post-hoc, bez prawa do twierdzenia
konfirmacyjnego; (c) nowe dane spoza fev-bench-100 odbudowują ślepy Lockbox.
Niezależnie od wyboru: zaległy suchy przebieg Fazy 1b na Dev
(SNaive/NLinear/DLinear, 3 okna, czas p95, MDE) — jedyny pomiar, który
odblokowuje Fazę 2.

not checked: mapowanie domen vs papier fev (Appendix E/Tabela 15) — nadal manualne;
czas p95 na `boomlet_1676`; budżet ściany Lockboxa; brak guarda w `bench.py`
przed ponownym `--fev-full` (audyt zgłasza to jako ryzyko proceduralne,
świadomie nietknięte w tym commicie, bo to zmiana zachowania, nie dysclosure).

<!-- handoff/flags/etth1-h720-s44-calibration-2026-10-30.md · owner: mateusz · agent: opencode · model: opencode/deepseek-v4.1-flash-free -->
`etth1-h720-s44-calibration-2026-10-30` — 2026-11-01: The ADR 0001 threshold-comparability
caveat is now a number. The S44 blend (NLinear L336 a=1 + NLinear L336 a=10 +
PatchTST-Delta P24 D32 2L, per-horizon ridge, no intercept, alpha=30000, frozen) scores
4.1255 mean raw MAE on the S49 protocol (12 locked origins, step 720 h, 8640..16560),
5-seed mean 4.1721. BigDictELM L96 2.4777, DLinear 2.5384. Rule fixed before the run:
4.1255 >= 2.4777, so 1.9781 was a protocol artifact (2161 dense step-1 origins), not a
level reachable on 12 sparse step-720 origins.

The blend is also worse than each of its own members (2.61-2.70). Mechanism recorded, not
tuned away: with no intercept the ridge can only express a level multiplier, and the
multiplier learned on a biased-low out-of-sample region (-5.24 bias, member MAE 6.09)
over-corrects at the scored origin (member MAE 2.79) — 1.3249x pushes the level to 25.3
against an actual 21.1. The disjoint second-half sensitivity reproduces the failure
(3.1041), so it is not one unlucky split.

Two corrections were made to an earlier attempt in this session, both before the reported
run. (1) Ridge weights in S44 were fitted on OUT-OF-SAMPLE member forecasts; the earlier
"in-sample ridge" claim was wrong and is removed. (2) The first calibration harness trained
members on s[o-8640:o] and then fed the ridge their forecasts from the last 2880 rows of
that same window — in-sample stacking, which S44 never did. Fixed: members frozen at row
5760 produce the ridge's design matrix over the 2161 out-of-sample tail origins, members
are refit on all 8640 rows for the scored forecast. Recorded as Amendment A1 in
GATES-s44-calibration.md before the run.

Consistency control: the identical S44 frozen test reproduces 1.978126 (rel diff 4.2e-11)
on both data files. Gate evidence for this close: the workspace integrity gate
`check_workspace_integrity.py` exit 0, and `python -m pytest projects/research/etth1-h720
-q` green at 31 passed. S49 stays closed, no model promoted, nothing tuned.

not checked: S44's dense 2161-origin test was not re-scored with seeds 43-46; S44's ridge
was not fitted once and reused (impossible across disjoint origins); alpha was not re-tuned
for the 8640-row window; BigDictELM/DLinear were re-derived, not diffed bit-for-bit against
S49's stored JSON; the two ETTh1 copies were not reconciled (<=3.6e-15, immaterial).

Next step: nothing on this line. Any further H720 work needs a new hypothesis, fresh dev
origins and a protocol registered before the run. The root/config follow-ups from the
CodeGraph G3 FAIL (disable jcodemunch or keep one code-index tool, shorten the CodeGraph
rule in root CLAUDE.md, keep the index for manual queries) remain open and are out of this
project's scope.

<!-- handoff/flags/divide-and-conquer-skill-2026-11-01.md · owner: mateusz · agent: opencode · model: nara/step-5-preview -->
`divide-and-conquer-skill-2026-11-01` — 2026-11-01: The Divide-and-Conquer skill
exists and is routable from every discovery surface. It splits a task into 2+
workstreams with disjoint file sets, each run by its own sub-agent in its own git
worktree on its own branch (`../Vault-wt/<flag>-<slug>`, `dnc/<flag>/<slug>`),
merged only after the user confirms. §0 is a hard gate: disjoint files, per-piece
verification, and an explicit do-not-use list (compute runs, ledgers, handoff
flags, generated views, scripts/hooks/skills edits, dependent pieces).

Wiring: row in `skills/SKILLS.md` (catalog gate R11), line in `skills/INDEX.md`
and in the injected `~/.config/opencode/workspace-skills.md` (kept byte-identical,
verified with `fc`), and a frontmatter description carrying both positive
("Use when") and negative ("Do NOT use") triggers, with no
`disable-model-invocation` flag, so the harness auto-discovers it. The harness
skill list picked the new skill up immediately after the folder was created.

Gate evidence (unlazy ledger G1–G8, all met, raw output in the session
transcript): `verify_catalog.py` exit 0 (32 catalog rows, 32 on-disk folders);
findstr confirmed the name/title frontmatter, both trigger classes in the
description, and the forbidden-write list in the body; the negative control for
`disable-model-invocation` fired on `skills/wayfinder/SKILL.md` and did not fire
on the new skill; both index copies name the skill and match byte-for-byte;
`check_workspace_integrity.py` exit 0.

not checked: the skill has not been exercised on a real multi-workstream task —
the benchmark-core Phase 1 files sitting untracked in the working tree
(manifest.py, metrics.py, bootstrap.py, ledger.py, guards.py and their tests)
are the natural first candidate, but they are another session's uncommitted work
and were left untouched; close.py `--verify-claims` was not used because the
gates were executed directly and their raw output is in the transcript; the
`~/.config/opencode/workspace-skills.md` copy lives outside the repo and is not
git-tracked; the pre-existing "benchmark-core: MAP.md is stale" advisory comes
from that other session's uncommitted files and is theirs to clear.

Next step: once the benchmark-core Phase 1 work is committed, run this skill on
it — one parallel batch of 4 (manifest, metrics, bootstrap, ledger) plus 1
serialized (guards), with conftest.py written by the orchestrator first — and
amend the skill from what that run teaches.

Starsze flagi (251): [handoff/flags/INDEX.md](handoff/flags/INDEX.md)

## where-the-work-landed

type: Concept
title: where-the-work-landed
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Where the work landed

`projects/research/agentic-research-lab/` — a **separate git repo** from this root. Its
T1/ralph work is in `819427c` and `e806d34`. The root's restructure
(gate trim, group move, scar hardening) is committed here as `8da9c18`
(2026-10-02 baseline); the root-architecture pass of the same day
(single-home map, gate docstring, R11, skills catalog) is `0ae22ef`, and the
ARL-side fix tranche (`1d20066`, `f579847`) plus the ingest checkpoints
(`28cfb50`, `6a419fe`) live in the ARL repo. Different workstreams — do not
fold them into one commit.

## gotchas-that-cost-time-worth-60-seconds-to-read-before-worki

type: Concept
title: gotchas-that-cost-time-worth-60-seconds-to-read-before-worki
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Gotchas that cost time (worth 60 seconds to read before working)

- **Polyrepo — verify before concluding anything about tree state.** Run
  `git rev-parse --show-toplevel` in whatever directory you are in. Root and
  each `projects/research/*` are independent repos.
- **Handoff was not a state machine (fixed 2026-10-03).** `.claude/session-handoff.md` in
  `agentic-research-lab` and the old root `HANDOFF.md` were both hand-written, with no
  script rebuilding either — the root one is now derived (`handoff/flags/<flag>.md` +
  `handoff/deep/` -> `scripts/build_handoff.py` -> `HANDOFF.md`, `--check` gates
  staleness; flag file `handoff_flag_per_file_icm`). The ARL project handoff is still
  hand-written. The project handoff had gone stale for two sessions before 2026-10-01,
  and a 2026-10-02 audit of this file found six stale claims at once (a module
  count, two HEAD pointers, the gate check list, a "no run has ever existed"
  line contradicted by a closed run on disk, and an open-vs-done follow-up).
  Audit both by grepping for claims — `findstr /n /c:"<number>" /c:"<sha>"` —
  not by reading one file and assuming the other agrees. A fix found by grep
  must be applied to every file grep can reach.
- **`reflection/loop_state.json` is not a ralph loop.** In
  `agentic-research-lab` it is a list of SHA-256 hashes, read only by
  `pipeline/06_reflect/spawn.py:48`, which uses `MAX_IDENTICAL_EVENTS = 3` to
  damp repeated reflection events. It is untracked since `5fd1d26` and still on
  disk. The `ralph-loop` skill is vendored (`819427c`); the one run that exists
  is closed — see `ralph_run_closed` above.
- **`$?` after a pipe reports the pipe, not Python.** `python gate.py | tail -3;
  echo $?` always prints 0. Capture the exit code before piping, or redirect to
  a file and read it after. `scripts/_scratch/run_and_rc.sh` does this for you.
- **G12 follow-ups are closed in project `## Open work`, not open.** The
  pi_models.py un-ignore (`82b078a`) and the no-artifact-on-failure defect
  (`024f9a5`) are both marked DONE 2026-10-01 in
  `projects/research/agentic-research-lab/CONTEXT.md` `## Open work`, so a
  `CLAUDE.md` → `CONTEXT.md` session sees them as finished.
- **ARL root resolution was one level short after the group move (fixed
  2026-10-02, `1d20066`; scar #7 in ARL `EXPERIENCE.md`).** The failure mode
  is generic: any "look up to the workspace root" path computed from a fixed
  number of `..` hops (`parents[N]`, hard-coded `../..`) silently breaks on
  any reorg — probe `scripts/*.py` for `parents[` after a move. The nested-
  `agentic-research-lab/` dir (a CRLF copy of part of the repo, 3,766 files,
  plus 121 worktree-deleted originals) and the `$null` root debris are the
  same day's tree-shape incidents: run `git status` early, verify a copy is
  byte-identical before deleting anything.

- **`close_session.py` runs `audit_workspace.py` only**, not the 21-gate
  workspace suite. The full suite is what pre-commit runs.
- **ARL `preflight.py` exits 1 on two failed reflection runs** (`bg-smoke3`,
  `smoke-scratch-02`) whose artifacts still fail the gate. That is a standing
  hard block, unrelated to any current work: the 21-gate chain itself is 21/21
  green, and `agent_commit.py` commits fine past it. Run
  `python scripts/quality_check.py` directly when preflight blocks you.

## gate-note-if-you-touch-allowed-root

type: Concept
title: gate-note-if-you-touch-allowed-root
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Gate note (if you touch `ALLOWED_ROOT`)

`scripts/check_workspace_integrity.py` holds `ALLOWED_ROOT`, a whitelist:
any unlisted name at the workspace root is a **FAIL**. This file is listed
there for that reason. Which check is which (hard vs advisory) and the
root-entry procedure: the gate's docstring is the single home; this note
and the other docs link, not restate.

## g12-resolved-2026-10-01-human-decision-closed-same-day

type: Concept
title: g12-resolved-2026-10-01-human-decision-closed-same-day
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# G12 — resolved 2026-10-01 (human decision), closed same day

`reflect.py` is the canonical reflection runner. Speed was the decider: 52 s
single structured call vs `spawn.py`'s 275 s; G11 quality passed for both,
so the wall-clock gap carried no quality signal. Recorded with ABANDON lines
(protocol: recorded, not deleted) in
`projects/research/agentic-research-lab/GATES-T1-phase04-runner.md`.

Follow-ups (both done 2026-10-01):
1. `scripts/pi_models.py` was un-ignored (`.gitignore` entry removed) and
   entered through `agent_commit.py` — commit `82b078a`. Never `git add .`.
2. The carried defect — failed runs wrote no artifact, so a failed run was
   indistinguishable from a never-run one — is fixed in
   `pipeline/06_reflect/reflect.py`: `agent_trace` ledger records
   (`run`/`failure` events with `failure_kind`: `bad_json`, `missing_key`,
   `unexpected_response`, or exception class), plus endpoint resolution moved
   in-run so a missing pi config is a traced failed run, not an import crash.
   Pinned by 4 new tests (`024f9a5`).

## deep-research-kg-icm

type: Concept
title: deep-research-kg-icm
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# HANDOFF — Deep Research: Knowledge Graph Integration + ICM (2026-10-03)

## Status 2026-10-04 (flaga: `deep_research_phase1_done`)

Phase 1 **domknięta** w ARL (`4b363da`): 3 sondy literaturowe + 8 seedów
arXiv, synteza → 12 chunków → rebuild (fingerprint `31989e46d0a5` →
`4880aab33ca4`, 10 373 nodes / 13 457 edges). Ruszyła też Phase 4-runtime:
`85c3318` (dead-route monitor w `route.py`), `5a275b0` (critic gate
w `ask.py`). Next: Phase 2 (ablacja) albo Phase 4-diversity. Szczegóły
we fladze; poniżej oryginalne zlecenie.

---

## Zlecenie
Przeprowadzić głębokie badanie (deep research) na temat: **integracja grafu wiedzy (knowledge graph) z pracą agenta w kontekście Interpretable Context Methodology (ICM)**.

Pytania researchowe:
1. Jak graf wiedzy (FTS5 + SQLite, chunks jako węzły, krawędzie SHARES_TAG/DERIVED_FROM/SCARRED_FROM/PART_OF/SEQUENCE) może być **operacyjnie** używany przez agenta w trakcie kodowania / debugowania / researchu?
2. Jakie są wzorce dopytowania (query patterns), które dają **mierzalną poprawę** jakości decyzji agenta (accuracy, grounding, time-to-fix)?
3. Jak ICM (Interpretable Context Methodology) — podejście "verified corpus → derived graph → reflection → meta-learning" — mapuje się na **praktykę codziennej pracy agenta** (nie tylko batch reflection)?
4. Jakie są **failure modes** obecnej implementacji (stale fingerprints, non-deterministic builds, citation concentration, write-only memory) i jak je mitigować w runtime?

## Kontekst (co już mamy w repo)

### Zaimplementowane i working (commit `5330266` w ARL):
- **Knowledge graph**: `knowledge/graph/build_graph.py` → `graph.db` (10k+ nodes, 12k+ edges, FTS5), fingerprint SHA-256 corpus
- **Query interface**: `knowledge/graph/ask.py` — tag intersection, tag filtering, text search, hybrid
- **Reflection pipeline**: `pipeline/06_reflect/spawn.py` + `route.py` — automated reflection z provenance (fingerprint, plan_version, phase), evidence citations (`Chunk id: \`NN_slug\``)
- **Citation integrity**: `check_reflection.py` — weryfikuje że każdy cytowany chunk istnieje w grafie, fingerprint matches live corpus
- **Determinism gate**: `check_graph_determinism.py` — rebuild z tego samego corpus = identyczny graf (content-hash, nie byte-hash)
- **Evidence grounding**: `check_citation_integrity.py` — citations resolve i support claim
- **Skills**: `poteto-mode-lite` (4 playbooki: investigation/bug-fix/feature/refactor + prove-it-works), `skill_router.py` (3-fazowy: decompose/select/iterate, 19 skill entries), `ralph-loop` (small-session contract)
- **Forge-guardrails**: `.agents/plugins/forge-guardrails/` — PreToolUse/Stop hooks, policy.yaml, venv re-exec, self-cert probe (agent hand-edited state.json → blocked)

### Znane problemy (otwarte, niezasłonięte gate'ami):
1. **Fingerprint staleness**: Additive corpus change → wszystkie prior digests stale. `restamp_provenance.py` re-stamps tylko jeśli cited IDs still resolve. Jeśli nie — trzeba re-run reflection (research decision, nie bookkeeping).
2. **Citation concentration**: `project-entropy.jsonl` ma 100% concentration (top-3 IDs cited in 4/4 rows) — sygnał że reflection czyta wąski fragment grafu.
3. **Dead routes**: `--tag` routes resolving to zero chunks (W-AUDIT-4) — silent failure.
4. **Write-only memory**: `00_icm_implementation_pitfalls_and_failure_modes` mode 2 — "silent promotion decay (write-only memory.md)" — brak eviction mechanismu dla memory.md.
5. **Agent-reach web skill**: goose + omniroute/gemini-flash-lite-latest działa, ale weak model spends budget on tree exploration before using web skill.

## Proponowany plan badań (deep research)

### Faza 1: Literature + Prior Art (1-2 sesje)
- Przegląd literatury: GraphRAG (Microsoft), Knowledge Graphs for Code (CodeGraph, GraphCodeBERT), Agentic RAG, ReAct + KG, MemGPT, HippoRAG, Zep, Letta
- ICM parallels: czym ICM się różni / co dodaje nad standardowym GraphRAG?
- Zapisz notatki do `INBOX/` → `scripts/ingest.py` → graph rebuild

### Faza 2: Eksperymenty operacyjne (2-3 sesje)
- Zdefiniuj **benchmark zadań** dla agenta: (a) bug fix w nieznanym kodzie, (b) feature implementation wymagająca zrozumienia architektury, (c) performance investigation
- Uruchom agenta **z i bez dostępu do grafu** (ablation) — zmierz: grounding rate, hallucination rate, time-to-first-correct-hypothesis, number of file reads
- Użyj `poteto-mode-lite` playbooków jako structured workflow wrapper

### Faza 3: Failure mode deep-dive (1-2 sesje)
- Symuluj/add failure modes: stale fingerprint, dead route, citation concentration, missing eviction
- Zmierz impact na agent quality
- Zaproponuj mitigacje (runtime checks, auto-re-stamp triggers, route health monitoring)

### Faza 4: Syngteza + Implementacja (1 sesja)
- Napisz **design doc** w `docs/research/kg-icm-integration.md`
- Zaimplementuj **jedną konkretną poprawę** (np. runtime fingerprint freshness check w `ask.py`, albo route health monitor, albo citation diversity enforcement w reflection)
- Prove-it-works: test + demo

## Kody dostępu / komendy

```bash
# Wejście do ARL
cd projects/research/agentic-research-lab

# Query graph
python knowledge/graph/ask.py "your question" --tag debugging --limit 10

# Spawn reflection
python pipeline/06_reflect/spawn.py --topic your-topic

# Full quality gate
python scripts/quality_check.py

# Goose run (weak model, requires omniroute credits)
goose run --provider omniroute --model gemini/gemini-flash-lite-latest --instructions ../../../scripts/_scratch/goose_g3_decision_graph_agent_reach_task.txt --output-format json --stats --max-turns 40

# Ralph loop resume
python skills/ralph-loop/scripts/ralph.py --project . resume
```

## Kryteria sukcesu (Definition of Done)

1. **Design doc** `docs/research/kg-icm-integration.md` z: literature survey, failure mode taxonomy, proposed architecture, benchmark results
2. **Implementation** — jedna merged PR z poprawą runtime (gate-passing, test-covered)
3. **Evidence trail** — fresh `INBOX/` sources, ingest logs, graph rebuild, reflection digests z claim-to-source links, implementation diff
4. **G3 verdict** — human review confirming implementation follows from evidence

## Blokery / Ryzyka
- Omniroute credits / gemini-flash-lite-latest availability (budget call)
- Weak model may not execute complex multi-stage research reliably → consider stronger model for research phases, weak only for implementation
- Existing stale reflection artifacts (`vera_expf_*`) — do not count as evidence for this run
- Preflight blocks on 2 hard missing reflection runs (`bg-smoke3`, `smoke-scratch-02`) — unrelated, run `python scripts/quality_check.py` directly

## Next Steps
1. Start Faza 1: `python scripts/expand_literature.py --query "knowledge graph agentic RAG code debugging" --source arxiv --max-results 20`
2. Ingest → graph rebuild → first reflection on "graph integration patterns"
3. Iterate

---

*Wygenerowane 2026-10-03 po commicie ARL `5330266` i roota `ce5aeeb`. Obecny stan: graf gotowy, bramki green, pstack skill zaimplementowany, forge-ab designed, plain-language meter frozen (D-003). Gotowe do startu deep-research.*

## Untyped

* [g12-resolved-2026-10-01-human-decision-closed-same-day](g12-resolved-2026-10-01-human-decision-closed-same-day.md)
* [deep-research-kg-icm](deep-research-kg-icm.md)
* [gotchas-that-cost-time-worth-60-seconds-to-read-before-worki](gotchas-that-cost-time-worth-60-seconds-to-read-before-worki.md)
* [gate-note-if-you-touch-allowed-root](gate-note-if-you-touch-allowed-root.md)
* [where-the-work-landed](where-the-work-landed.md)
