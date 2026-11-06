---
flag: omp-token-profile-20261106
since: 2026-11-06
owner: Mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash
origin: configure Oh My Pi through repo-local files
---

`omp-token-profile-20261106` — 2026-11-06: `.omp/config.yml` przepisany na realny schemat OMP v18.16.0. Usunięto martwe/niepoprawne klucze (`pruneToolDescriptions`, `approvalMode: accept`), dodano kapsle outputu (`artifactSpillThreshold: 20`, `artifactTailBytes: 5`, `artifactHeadBytes: 2.5`, `outputMaxColumns: 512`), jawne lazy tools (`tools.xdev: true`, `xdevDocs: catalog`), read summaries i politykę kompakcji. Weryfikacja: `omp config get` zwraca nowe wartości, `omp config list --scope project` nie ma nieznanych kluczy, `check_workspace_integrity.py` przechodzi. Commit `2aa729f` wypchnięty.
