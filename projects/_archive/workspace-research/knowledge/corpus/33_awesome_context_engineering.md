---
type: Concept
id: 33_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 34/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

This separation often yields better results than having a single Claude handle everything.

### b. Have multiple checkouts of your repo

Rather than waiting for Claude to complete each step, something many engineers at Anthropic do is:

1.   **Create 3-4 git checkouts** in separate folders
2.   **Open each folder** in separate terminal tabs
3.   **Start Claude in each folder**with different tasks
4.   **Cycle through** to check progress and approve/deny permission requests

### c. Use git worktrees

This approach shines for multiple independent tasks, offering a lighter-weight alternative to multiple checkouts. Git worktrees allow you to check out multiple branches from the same repository into separate directories. Each worktree has its own working directory with isolated files, while sharing the same Git history and reflog.

Using git worktrees enables you to run multiple Claude sessions simultaneously on different parts of your project, each focused on its own independent task. For instance, you might have one Claude refactoring your authentication system while another builds a completely unrelated data visualization component. Since the tasks don't overlap, each Claude can work at full speed without waiting for the other's changes or dealing with merge conflicts:

1.   **Create worktrees**: `git worktree add ../project-feature-a feature-a`
2.   **Launch Claude in each worktree**: `cd ../project-feature-a && claude`
3.   **Create additional worktrees** as needed (repeat steps 1-2 in new terminal tabs)

Some tips:

*   Use consistent naming conventions
*   Maintain one terminal tab per worktree
*   If you’re using iTerm2 on Mac, [set up notifications](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview#notification-setup) for when Claude needs attention
*   Use separate IDE windows for different worktrees
*   Clean up when finished: `git worktree remove ../project-feature-a`

### d. Use headless mode with a custom harness

`claude -p` (headless mode) integrates Claude Code programmatically into larger workflows while leveraging its built-in tools and system prompt. There are two primary patterns for using headless mode:

1. **Fanning out** handles large migrations or analyses (e.g., analyzing sentiment in hundreds of logs or analyzing thousands of CSVs):

1.   Have Claude write a script to generate a task list. For example, generate a list of 2k files that need to be migrated from framework A to framework B.
2.   Loop through tasks, calling Claude programmatically for each and giving it a task and a set of tools it can use. For example: `claude -p “migrate foo.py from React to Vue. When you are done, you MUST return the string OK if you succeeded, or FAIL if the task failed.” --allowedTools Edit Bash(git commit:*)`
3.   Run the script several times and refine your prompt to get the desired outcome.

2. **Pipelining** integrates Claude into existing data/processing pipelines:
