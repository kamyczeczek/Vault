---
type: Concept
id: 03_plain_text_as_interface
title: "Stage 02: Script (part 4/4)"
source: "Plain Text as Interface.md"
tags: [agentic, agents, context-engineering, icm, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

- **Final deliverables** may be binary (e.g., a rendered `.mp4` video or `.pptx` deck). But the *intermediate* artifacts that lead to them are always plain text.
- **Local scripts** may process data in non-text formats (e.g., fetching a PDF as source material). But the extracted, structured content is written back as Markdown for the next stage.
- **Large datasets** may be stored as CSV or JSONL, which are still text-based and diffable.

The principle is: **the communication layer between stages is always plain text. Only the very first input and very last output may be binary.**
