---
type: Concept
id: 28_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 29/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1.   **Ask Claude to write tests based on expected input/output pairs**. Be explicit about the fact that you’re doing test-driven development so that it avoids creating mock implementations, even for functionality that doesn’t exist yet in the codebase.
2.   **Tell Claude to run the tests and confirm they fail**. Explicitly telling it not to write any implementation code at this stage is often helpful.
3.   **Ask Claude to commit the tests**when you’re satisfied with them.
4.   **Ask Claude to write code that passes the tests**, instructing it not to modify the tests. Tell Claude to keep going until all tests pass. It will usually take a few iterations for Claude to write code, run the tests, adjust the code, and run the tests again.
    1.   At this stage, it can help to ask it to verify with independent subagents that the implementation isn’t overfitting to the tests

5.   **Ask Claude to commit the code** once you’re satisfied with the changes.

Claude performs best when it has a clear target to iterate against—a visual mock, a test case, or another kind of output. By providing expected outputs like tests, Claude can make changes, evaluate results, and incrementally improve until it succeeds.

### c. Write code, screenshot result, iterate

Similar to the testing workflow, you can provide Claude with visual targets:

1.   **Give Claude a way to take browser screenshots** (e.g., with the [Puppeteer MCP server](https://github.com/modelcontextprotocol/servers/tree/c19925b8f0f2815ad72b08d2368f0007c86eb8e6/src/puppeteer), an [iOS simulator MCP server](https://github.com/joshuayoes/ios-simulator-mcp), or manually copy / paste screenshots into Claude).
2.   **Give Claude a visual mock** by copying / pasting or drag-dropping an image, or giving Claude the image file path.
3.   **Ask Claude to implement the design** in code, take screenshots of the result, and iterate until its result matches the mock.
4.   **Ask Claude to commit** when you're satisfied.

Like humans, Claude's outputs tend to improve significantly with iteration. While the first version might be good, after 2-3 iterations it will typically look much better. Give Claude the tools to see its outputs for best results.

![Image 2: Safe yolo mode](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F6ea59a36fe82c2b300bceaf3b880a4b4852c552d-1600x1143.png&w=3840&q=75)

### d. Safe YOLO mode

Instead of supervising Claude, you can use `claude --dangerously-skip-permissions` to bypass all permission checks and let Claude work uninterrupted until completion. This works well for workflows like fixing lint errors or generating boilerplate code.
