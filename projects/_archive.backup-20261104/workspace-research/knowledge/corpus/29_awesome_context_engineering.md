---
type: Concept
id: 29_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 30/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Letting Claude run arbitrary commands is risky and can result in data loss, system corruption, or even data exfiltration (e.g., via prompt injection attacks). To minimize these risks, use `--dangerously-skip-permissions` in a container without internet access. You can follow this [reference implementation](https://github.com/anthropics/claude-code/tree/main/.devcontainer) using Docker Dev Containers.

### e. Codebase Q&A

When onboarding to a new codebase, use Claude Code for learning and exploration. You can ask Claude the same sorts of questions you would ask another engineer on the project when pair programming. Claude can agentically search the codebase to answer general questions like:

*   How does logging work?
*   How do I make a new API endpoint?
*   What does `async move { ... }` do on line 134 of `foo.rs`?
*   What edge cases does `CustomerOnboardingFlowImpl` handle?
*   Why are we calling `foo()` instead of `bar()` on line 333?
*   What’s the equivalent of line 334 of `baz.py` in Java?

At Anthropic, using Claude Code in this way has become our core onboarding workflow, significantly improving ramp-up time and reducing load on other engineers. No special prompting is required! Simply ask questions, and Claude will explore the code to find answers.

![Image 3: Use Claude to interact with git](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2Fa08ea13c2359aac0eceacebf2e15f81e8e8ec8d2-1600x1278.png&w=3840&q=75)

### f. Use Claude to interact with git

Claude can effectively handle many git operations. Many Anthropic engineers use Claude for 90%+ of our _git_ interactions:

*   **Searching _git_ history** to answer questions like "What changes made it into v1.2.3?", "Who owns this particular feature?", or "Why was this API designed this way?" It helps to explicitly prompt Claude to look through git history to answer queries like these.
*   **Writing commit messages**.Claude will look at your changes and recent history automatically to compose a message taking all the relevant context into account
*   **Handling complex git operations** like reverting files, resolving rebase conflicts, and comparing and grafting patches

### g. Use Claude to interact with GitHub

Claude Code can manage many GitHub interactions:

*   **Creating pull requests**: Claude understands the shorthand "pr" and will generate appropriate commit messages based on the diff and surrounding context.
*   **Implementing one-shot resolutions** for simple code review comments: just tell it to fix comments on your PR (optionally, give it more specific instructions) and push back to the PR branch when it's done.
*   **Fixing failing builds** or linter warnings
*   **Categorizing and triaging open issues** by asking Claude to loop over open GitHub issues

This eliminates the need to remember `gh` command line syntax while automating routine tasks.

### h. Use Claude to work with Jupyter notebooks
