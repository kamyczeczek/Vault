# Vault

Vault is a workspace for reproducible research and the tooling that supports
it. The research projects under `projects/research/` are the products; the
root-level scripts, policies, indexes, and handoff views are supporting
infrastructure.

## Start here

1. Read [`HANDOFF.md`](HANDOFF.md) for the current workspace state.
2. Read [`AGENTS.md`](AGENTS.md) for routing and workspace rules.
3. Choose one project under [`projects/research/`](projects/research/).
4. Run that project's `preflight.py` before changing or running experiments.

The ETTh1 H720 study (`projects/research/etth1-h720`) is closed — the S49 H720
line was rejected. It stays in `projects/research/` for reference; do not start
new work there. Every active project runs the same pattern:

```powershell
cd projects/research/<project>
python preflight.py
python -m pytest -q
```

## Repository map

| Path | Role |
|---|---|
| `projects/research/` | Active research projects |
| `projects/_archive/` | Closed or superseded work |
| `scripts/` | Workspace automation and gates |
| `handoff/` | Source flags for generated state views |
| `HANDOFF.md` | Generated current-state view |
| `docs/` | Human-facing workflow and reference material |

Generated views such as `HANDOFF.md` and `STATE.md` are not edited by hand.
Update their source flags and rebuild them with the documented scripts.
