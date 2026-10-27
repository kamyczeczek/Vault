---
type: Concept
id: 32_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 33/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

### h. Pass data into Claude

Several methods exist for providing data to Claude:

*   **Copy and paste** directly into your prompt (most common approach)
*   **Pipe into Claude Code** (e.g., `cat foo.txt | claude`), particularly useful for logs, CSVs, and large data
*   **Tell Claude to pull data** via bash commands, MCP tools, or custom slash commands
*   **Ask Claude to read files** or fetch URLs (works for images too)

Most sessions involve a combination of these approaches. For example, you can pipe in a log file, then tell Claude to use a tool to pull in additional context to debug the logs.

5. Use headless mode to automate your infra
-------------------------------------------

Claude Code includes [headless mode](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview#automate-ci-and-infra-workflows) for non-interactive contexts like CI, pre-commit hooks, build scripts, and automation. Use the `-p` flag with a prompt to enable headless mode, and `--output-format stream-json` for streaming JSON output.

Note that headless mode does not persist between sessions. You have to trigger it each session.

### a. Use Claude for issue triage

Headless mode can power automations triggered by GitHub events, such as when a new issue is created in your repository. For example, the public [Claude Code repository](https://github.com/anthropics/claude-code/blob/main/.github/actions/claude-issue-triage-action/action.yml) uses Claude to inspect new issues as they come in and assign appropriate labels.

### b. Use Claude as a linter

Claude Code can provide [subjective code reviews](https://github.com/anthropics/claude-code/blob/main/.github/actions/claude-code-action/action.yml) beyond what traditional linting tools detect, identifying issues like typos, stale comments, misleading function or variable names, and more.

6. Uplevel with multi-Claude workflows
--------------------------------------

Beyond standalone usage, some of the most powerful applications involve running multiple Claude instances in parallel:

### a. Have one Claude write code; use another Claude to verify

A simple but effective approach is to have one Claude write code while another reviews or tests it. Similar to working with multiple engineers, sometimes having separate context is beneficial:

1.   Use Claude to write code
2.   Run `/clear` or start a second Claude in another terminal
3.   Have the second Claude review the first Claude's work
4.   Start another Claude (or `/clear` again) to read both the code and review feedback
5.   Have this Claude edit the code based on the feedback

You can do something similar with tests: have one Claude write tests, then have another Claude write code to make the tests pass. You can even have your Claude instances communicate with each other by giving them separate working scratchpads and telling them which one to write to and which one to read from.
