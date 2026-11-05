---
type: Concept
id: 70_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 71/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

![Image 5](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/dBjZlVbKJVhjgQuF.png)

根据我们的经验，改善智能体行为最有效的方法之一看似简单：将错误转向留在context中。当模型看到失败的动作——以及由此产生的观察或堆栈跟踪——它隐式地更新其内部信念。这将其先验从类似动作中转移，减少重复相同错误的机会。实际上，我们认为错误恢复是真正智能体行为最清晰的指标之一。然而，它在大多数学术工作和公共基准测试中仍然代表不足，这些通常关注理想条件下的任务成功。

### 不要被Few-Shot困住

[Few-shot prompting](https://www.promptingguide.ai/techniques/fewshot)是改善LLM输出的常见技术。但在智能体系统中，它可能以微妙的方式适得其反。

语言模型是优秀的模仿者；它们模仿context中的行为模式。如果你的context充满了类似的过去动作-观察对，模型会倾向于遵循该模式，即使它不再是最优的。

这在涉及重复决策或动作的任务中可能很危险。例如，当使用Manus帮助审查20份简历时，智能体经常陷入节奏——重复类似的动作，仅仅因为这是它在context中看到的。这导致漂移、过度泛化，或有时产生幻觉。

![Image 6](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/IIyBBdwwuMDJUnUc.png)

解决方案是增加多样性。Manus在动作和观察中引入少量结构化变化——不同的序列化模板、替代措辞、顺序或格式的轻微噪声。这种受控的随机性有助于打破模式并调整模型的注意力。换句话说，不要让自己陷入few-shot的困境。你的context越统一，你的智能体就越脆弱。

### 结论

Context工程仍然是一门新兴科学——但对于智能体系统来说，它已经是必不可少的。模型可能变得更强、更快、更便宜，但再多的原始能力也无法替代对内存、环境和反馈的需求。你如何塑造context最终定义了你的智能体如何行为：运行多快、恢复多好、扩展多远。

在Manus，我们通过反复重写、死胡同和数百万用户的真实世界测试学到了这些教训。我们在这里分享的内容都不是普遍真理——但这些是对我们有效的模式。如果它们能帮助你避免哪怕一次痛苦的迭代，那么这篇文章就完成了它的使命。

智能体的未来将一次一个context地构建。好好工程化它们。

================================================
FILE: docs/manus/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus.md
================================================
Title: Context Engineering for AI Agents: Lessons from Building Manus

URL Source: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus

Markdown Content:
2025/7/18 --Yichao 'Peak' Ji

At the very beginning of the [Manus](https://manus.im/app) project, my team and I faced a key decision: should we train an end-to-end agentic model using open-source foundations, or build an agent on top of the [in-context learning](https://arxiv.org/abs/2301.00234) abilities of frontier models?

Back in my first decade in NLP, we didn't have the luxury of that choice. In the distant days of [BERT](https://arxiv.org/abs/1810.04805) (yes, it's been seven years), models had to be fine-tuned—and evaluated—before they could transfer to a new task. That process often took weeks per iteration, even though the models were tiny compared to today's LLMs. For fast-moving applications, especially pre–PMF, such slow feedback loops are a deal-breaker. That was a bitter lesson from my last startup, where I trained models from scratch for [open information extraction](https://en.wikipedia.org/wiki/Open_information_extraction) and semantic search. Then came [GPT-3](https://arxiv.org/abs/2005.14165) and [Flan-T5](https://arxiv.org/abs/2210.11416), and my in-house models became irrelevant overnight. Ironically, those same models marked the beginning of in-context learning—and a whole new path forward.
