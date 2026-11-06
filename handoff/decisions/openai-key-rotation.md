---
status: decided
recommendation: rotation not required by evidence — key never entered either repo's history or tree; owner's call, precautionary only
decided_at: 2026-11-06
owner: mateusz
---

# openai-key-rotation

Should the potentially exposed `OPENAI_API_KEY` (the `sk-nry-…` key named in
docs/audit-vault-simplification-2026-11-05.md) be rotated?

Context: session 1 (flag `security-verification-2026-11-06`, commit `0e75431`)
searched the full history of both repos (public: 147 commits; private
`raw-sessions`: 5 commits, clone == remote tip) and the whole 4787-file
working tree. No full key appeared anywhere — only masked placeholders, the
scanner's own pattern text, and `scripts/` copies removed by `e5eaa4c`. The key
lives only in gitignored `.env`-type files (`.gitignore:33-45`).

Recommendation: rotate only as a precaution, not as remediation. The evidence
does not mandate it, and the fact that the key ever sat on disk next to a repo
is the owner's risk call, not a repo-state question.

not checked: — (the audit list of every rotation ever done is the owner's;
this file does not assert one)
