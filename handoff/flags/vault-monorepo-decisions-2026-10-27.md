---
flag: vault-monorepo-decisions-2026-10-27
since: 2026-10-27
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`vault-monorepo-decisions-2026-10-27` — 2026-10-27: D24 zapisuje, co repo zawiera i czego nie.
Stan: `DECISIONS.md` ma wpis D24 (4 wyjątki: toolchain, sekrety, książki, pliki >100 MB;
12 zagnieżdżonych repo jako pliki + `history.bundle`); log audytu domknięty.
Next: `git clone` z GitHuba na czysto i `check_workspace_integrity.py` w klonie.
not checked: zachowanie klonu — `preflight.py`, hooki i `core.hooksPath` są per-maszyna.
