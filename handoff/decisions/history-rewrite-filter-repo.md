---
status: decided
recommendation: do not rewrite — no secret grounds (scan clean), and a size-only rewrite invalidates all 147 public SHAs for ~184MB of legitimate artifacts
decided_at: 2026-11-06
owner: mateusz
---

# history-rewrite-filter-repo

Should `git filter-repo` rewrite history to shrink the repository?

Context: session 2 (flag `archive-provenance-2026-11-06`, commit `9e08e94`)
measured HEAD: `projects/_archive/` holds 3154 tracked files / 255.5 MB
path-sum (244 MB deduped); every large blob is a legitimate archived-project
artifact (three `history.bundle`s, `graph_index.json`, `graph.db`,
`iii.exe.bak`). Session 1 proved no secret motivates a rewrite. The repo on
disk is 6 packs / 193 MiB.

What a rewrite costs: every one of the 147 public commit SHAs changes, which
invalidates commit references in flags, reviews, the `raw-sessions` clone pin
(`3bbf3b0`) and the export mechanism's history assumptions.

Recommendation: do not rewrite on current evidence. Revisit only if clone time
or repo size demonstrably blocks the raw-sessions workflow — as its own plan
with its own commit, per the standing rule that this is never bundled into a
"finish everything" change.

not checked: — (no measurement of clone/push wall-time cost was taken; the
size numbers above are content sums, not transfer times)
