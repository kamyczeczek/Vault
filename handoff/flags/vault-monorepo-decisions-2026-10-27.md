---
flag: vault-monorepo-decisions-2026-10-27
since: 2026-10-27
owner: mateusz
agent: opencode
model: opencode/deepseek-v4.1-flash-free
origin: session-close
---

`vault-monorepo-decisions-2026-10-27` — 2026-10-27: D24 zapisuje, co repo zawiera i jak odtworzyć historię.
Stan: `DECISIONS.md` D24 wymienia 4 wyjątki (toolchain, sekrety, książki, pliki >100 MB)
i podaje `git clone --mirror history.bundle` jako jedyny poprawny sposób odtworzenia
12 wchłoniętych repo — zwykły `clone` gubi `refs/remotes/*` (157 commitów w `ecc`).
Next: świeży `git clone` z GitHuba i `check_workspace_integrity.py` w klonie.
not checked: zachowanie klonu — `preflight.py`, hooki i `core.hooksPath` są per-maszyna.
