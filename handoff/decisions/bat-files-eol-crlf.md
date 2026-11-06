---
status: decided
recommendation: extend the eol=crlf fix (already proven on raw_sessions_drive.bat) to raw_sessions.bat, session_brief.bat, session_digest.bat — one commit, renormalize, hook gates apply
decided_at: 2026-11-06
owner: mateusz
---

# bat-files-eol-crlf

Three `.bat` entry files still carry the LF defect that `raw_sessions_drive.bat`
already had fixed: `raw_sessions.bat`, `session_brief.bat`, `session_digest.bat`
store LF in the blob while the Windows worktree needs CRLF — cmd.exe misreads
a LF batch file once it grows past trivial size.

Context: session 4 (flag `raw-sessions-count-ownership-2026-11-06`, commit
`ffd5643`) verified the drive variant now reads `i/lf w/crlf attr/text
eol=crlf` (blob LF, worktree CRLF — the right shape), and kept the remaining
three as an owner decision.

Recommendation: add the `.bat` files to the same `.gitattributes` mechanism as
`raw_sessions_drive.bat`, renormalize, verify `git ls-files --eol` per file,
commit as its own change. Do not hand-edit line endings — the hook and
`git diff --check` are the authorities.

not checked: — (whether the three files are actually invoked on this machine
was not verified; the defect is real per git's eol report, the usage is
assumed from the raw-sessions workflow)
