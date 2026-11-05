---
type: Concept
id: 253_icm_knowledge_big
title: "ICM_knowledge.md (part 254/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Show human-readable messages to users — never raw errors, stack traces, or technical details

If you catch it, either handle it meaningfully or log it. Never empty catch blocks.

Delete Dead Code

Don't comment out code. Don't leave unused functions, imports, or variables. If it's not being used, delete it. Git has the history if you ever need it back.

Inline Code Documentation

Every source file carries its own documentation. This gives both the developer and Claude immediate context the moment a file is opened — no hunting through separate docs.

File Header — Always Present

Every source file MUST have a header block at the top with three sections: status, issues, and todo. All three sections are always present, even when empty. The empty slots serve as a reminder that documentation can go there — if the sections aren't present, they get forgotten.

#### Template (JS/TS/Vue):

@file DescriptiveFileName

@description What this file is for and what it does (1-3 concise lines)

@status None

@issues None

#### Template (Rust):

//! # DescriptiveModuleName

//! What this module is for and what it does (1-3 concise lines)

//! ## Status

//! ## Issues

//! ## Todo

#### Template (C — header files):

@file descriptive_name.h

@brief What this header defines and its purpose (1-3 concise lines)

@status None

@issues None

#### Template (C — source files):

@file descriptive_name.c

@brief Implementation of [what this file implements]

@status None

@issues None

#### Template (Swift):

/// # DescriptiveFileName

/// What this file is for and what it does (1-3 concise lines)

/// ## Status

/// ## Issues

/// ## Todo

#### When there IS something to document:

@file AvatarUploadService

@description Handles user avatar upload, validation, and storage.

Supports JPEG, PNG, and WebP formats up to 10MB.

@status Avatar upload works but no progress indicator yet

@issues Timeout on large files (>10MB) — needs chunked upload

[ ] Add upload progress bar (blocked on chunked upload)

[ ] Validate image dimensions before upload

#### What each section means:

SectionPurposeExample@statusCurrent state of the code — what works, what's partial"Core CRUD works, batch operations not yet implemented"@issuesKnown bugs, performance problems, fragile areas"Race condition when two users edit simultaneously"@todoIncomplete work left during a session — breadcrumbs"- [ ] Add input validation for email field"

File Header Cleanup Rule

When working in any file, always check the header first. If there are completed TODOs, resolved issues, or outdated status notes — clean them up. Reset sections to "None" when everything is addressed. This prevents documentation rot.

File-Level TODOs Are Breadcrumbs

The @todo section in file headers is NOT the project plan. The real task tracking lives in plan files and .teamide/tasks/. File-level TODOs exist for the "mid-session, had to step away" situation:
