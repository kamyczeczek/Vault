---
type: Concept
title: session-12-gates
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Gates — Session 12 (A/B/C/D/E)

- [x] A1: git status i Test-Path w raporcie session-12-report-fix.md jako osobne outputy
  CHECK: powershell -Command "Select-String -Path session-12-report-fix.md -Pattern 'git status --short' | Measure-Object | Select-Object -ExpandProperty Count"
  EXPECT: 2
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Mateusz\Desktop\root_workspace\handoff; path=f3a36ce6d77c/48 entries; EXPECT=matched; output-sha256=df4e26a04a444901b95afef44e4a96cfae34690fff2ad2c66389c70079cdff2b; output-bytes=3

- [x] B1: zdanie o konsumpcji tokenu w session-11-write-tool-test.md
  CHECK: powershell -Command "Select-String -Path session-11-write-tool-test.md -Pattern 'hook konsumuje' | Measure-Object | Select-Object -ExpandProperty Count"
  EXPECT: 1
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Mateusz\Desktop\root_workspace\handoff; path=f3a36ce6d77c/48 entries; EXPECT=matched; output-sha256=f1b2f662800122bed0ff255693df89c4487fbdcf453d3524a42d4ec20c3d9c04; output-bytes=3

- [x] C1: sekcja Post-closure backlog w CONTEXT.md
  CHECK: powershell -Command "Select-String -Path ../projects/research/the-pragmatic-programmer-retrieval/CONTEXT.md -Pattern 'Post-closure backlog' | Measure-Object | Select-Object -ExpandProperty Count"
  EXPECT: 1
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Mateusz\Desktop\root_workspace\handoff; path=f3a36ce6d77c/48 entries; EXPECT=matched; output-sha256=f1b2f662800122bed0ff255693df89c4487fbdcf453d3524a42d4ec20c3d9c04; output-bytes=3

- [x] D1: scope D zaplanowany w session-17-d-scope.md (bez wykonania researchu)
  CHECK: powershell -Command "Test-Path session-17-d-scope.md"
  EXPECT: True
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Mateusz\Desktop\root_workspace\handoff; path=a7703605f6f4/130 entries; EXPECT=matched; output-sha256=ca4a016eae14ab0c7ebb935a6e24ae8b512958f25c788f11eb99566d066b7957; output-bytes=6

- [x] E1: decyzja wlasciciela zapisana w session-13-owner-decision.md
  CHECK: powershell -Command "Select-String -Path session-13-owner-decision.md -Pattern 'E = (Tak|Nie)' | Measure-Object | Select-Object -ExpandProperty Count"
  EXPECT: 1
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Mateusz\Desktop\root_workspace\handoff; path=a7703605f6f4/130 entries; EXPECT=matched; output-sha256=f1b2f662800122bed0ff255693df89c4487fbdcf453d3524a42d4ec20c3d9c04; output-bytes=3
