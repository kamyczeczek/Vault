---
type: Concept
id: 24_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 25/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

_Looking for more detailed information? Our comprehensive documentation at [claude.ai/code](https://claude.ai/redirect/website.v1.26d5e13f-bc1f-432b-b15a-bdc59c1b87b0/code)_ _covers all the features mentioned in this post and provides additional examples, implementation details, and advanced techniques._

1. Customize your setup
-----------------------

Claude Code is an agentic coding assistant that automatically pulls context into prompts. This context gathering consumes time and tokens, but you can optimize it through environment tuning.

### a. Create `CLAUDE.md` files

`CLAUDE.md` is a special file that Claude automatically pulls into context when starting a conversation. This makes it an ideal place for documenting:

*   Common bash commands
*   Core files and utility functions
*   Code style guidelines
*   Testing instructions
*   Repository etiquette (e.g., branch naming, merge vs. rebase, etc.)
*   Developer environment setup (e.g., pyenv use, which compilers work)
*   Any unexpected behaviors or warnings particular to the project
*   Other information you want Claude to remember

There’s no required format for `CLAUDE.md` files. We recommend keeping them concise and human-readable. For example:

```
# Bash commands
- npm run build: Build the project
- npm run typecheck: Run the typechecker

# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

You can place `CLAUDE.md` files in several locations:

*   **The root of your repo**, or wherever you run `claude` from (the most common usage). Name it `CLAUDE.md` and check it into git so that you can share it across sessions and with your team (recommended), or name it `CLAUDE.local.md` and `.gitignore` it
*   **Any parent of the directory** where you run `claude`. This is most useful for monorepos, where you might run `claude` from `root/foo`, and have `CLAUDE.md` files in both `root/CLAUDE.md` and `root/foo/CLAUDE.md`. Both of these will be pulled into context automatically
*   **Any child of the directory** where you run `claude`. This is the inverse of the above, and in this case, Claude will pull in `CLAUDE.md` files on demand when you work with files in child directories
*   **Your home folder** (`~/.claude/CLAUDE.md`), which applies it to all your _claude_ sessions

When you run the `/init` command, Claude will automatically generate a `CLAUDE.md` for you.

### b. Tune your `CLAUDE.md` files

Your `CLAUDE.md` files become part of Claude’s prompts, so they should be refined like any frequently used prompt. A common mistake is adding extensive content without iterating on its effectiveness. Take time to experiment and determine what produces the best instruction following from the model.
