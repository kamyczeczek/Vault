---
type: Concept
id: 176_icm_knowledge_big
title: "ICM_knowledge.md (part 177/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

This is the one you paste into an LLM.

One engine, three ways to use it: a command-line tool, a Finder right-click

Quick Action, and a Claude Code skill.

------

Requirements

(the scanned-PDF OCR fallback uses Apple's Vision framework).

https://docs.astral.sh/uv/

brew install uv

Python 3.11+ (uv manages the project's own virtualenv, so the system Python

version doesn't matter).

------

unzip tomd.zip cd tomd uv sync

That's it for the CLI. The two optional surfaces are below.

------

1. Command line

uv run tomd path/to/document.docx

document.md

document_lean.md

beside the source.

1. Finder Quick Action     (right-click)

bash quickaction/install.sh

Then right-click any supported file in Finder →

Quick Actions → Convert to

. It writes both files beside the source and copies the

path to your clipboard. (If it doesn't appear:

killall Finder

, or enable it

under System Settings → Login Items & Extensions → Quick Actions.)

The installer rewrites the bundled command to point at wherever you unzipped

tomd, so you can keep the folder anywhere.

1. Claude Code skill

#### Symlink the skill into your Claude skills directory:

mkdir -p ~/.claude/skills/tomd ln -sf "$(pwd)/skill/SKILL.md" ~/.claude/skills/tomd/SKILL.md

skill/SKILL.md

and replace

with this folder's absolute path.

After that, Claude auto-converts any document you hand it and reads the lean

Markdown instead of the raw binary, saving tokens.

------

Encrypted files

trigger a native macOS password prompt automatically; if

you cancel, that file is skipped.

Run the tests with

uv sync --extra dev && uv run pytest -q

------

Uncategorized\Stop feeding raw documents to your LLM\tomd\skill\SKILL.md

------

description: Use when the user provides, attaches, or references a .pdf, .docx, .pptx, or .xlsx file and you need its contents. Converts the document to token-efficient markdown with the tomd CLI and reads the resulting _lean.md instead of the raw binary, saving tokens.

tomd — read documents as token-lean markdown

file is provided or referenced:

Run the converter (replace

with wherever you installed tomd, and

use the absolute path to the document):

The command prints the path to a

~/.tomd_cache/

Read that file

with the Read tool — do NOT read the raw document.

If the command exits non-zero, tell the user it failed and fall back to reading the file directly.

Encrypted files trigger a native macOS password prompt automatically; if the user cancels, the conversion is skipped.

------

Uncategorized\ai_identity\Your AI agent needs an identity not just instructions.md

Just tightened my ICM knowledge base / workspace and realized something that should have been obvious:

Most people write prompts.

Fewer people write identity.

So I made a reusable Operator Identity template for any workspace. It defines who the agent is, what loop it owns, how it should think, what it will not do, and which files are the source of truth.
