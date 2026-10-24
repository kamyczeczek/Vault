# Session 7 — R15 forensics

- R15 status before session 6: GREEN at 0d0a585 (session 5). Commit 0d0a585 passed pre-commit with same hook.
- rank fe3a511b now: rank 8 (antigravity::fe3a511b-90c::463, score -14.589) for "FTS5 unicode61".
- top-5 now: 01a14af3 (×2 chunks), ses_eb2d1e180ffe, ses_ebce63c74ffe — new sessions from session 6 ingest.
- Conclusion: R15 broken by session-6 ingest. New sessions displaced fe3a511b from top-5.
- Fix chosen: Option B (explicit exclusion of new sessions), documented as test hygiene (index grew).