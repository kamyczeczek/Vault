---
type: Concept
id: 69_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 70/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

自然的反应是设计动态动作空间——也许使用类似[RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)的方法按需加载工具。我们在Manus中也尝试过这种方法。但我们的实验表明了一个明确的规则：除非绝对必要，避免在迭代中动态添加或移除工具。主要有两个原因：

1. 在大多数LLM中，工具定义在序列化后位于context的前部，通常在系统prompt之前或之后。因此任何更改都会使所有后续动作和观察的KV-cache失效。

2. 当之前的动作和观察仍然引用当前context中不再定义的工具时，模型会感到困惑。没有[约束解码](https://platform.openai.com/docs/guides/structured-outputs)，这通常导致模式违规或幻觉动作。

为了解决这个问题同时仍然改进动作选择，Manus使用上下文感知的[状态机](https://en.wikipedia.org/wiki/Finite-state-machine)来管理工具可用性。它不是移除工具，而是在解码期间掩码token logits，以根据当前context防止（或强制）选择某些动作。

![Image 2](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/cWxINCvUfrmlbvfV.png)

在实践中，大多数模型提供商和推理框架都支持某种形式的响应预填充，这允许你在不修改工具定义的情况下约束动作空间。通常有三种函数调用模式（我们将使用NousResearch的[Hermes格式](https://github.com/NousResearch/Hermes-Function-Calling)作为示例）：

• **Auto** – 模型可以选择调用函数或不调用。通过仅预填充回复前缀实现：`<|im_start|>assistant`

• **Required** – 模型必须调用函数，但选择不受约束。通过预填充到工具调用token实现：`<|im_start|>assistant<tool_call>`

• **Specified** – 模型必须从特定子集调用函数。通过预填充到函数名开头实现：`<|im_start|>assistant<tool_call>{"name": "browser_`

使用这种方法，我们通过直接掩码token logits来约束动作选择。例如，当用户提供新输入时，Manus必须立即回复而不是采取动作。我们还故意设计了具有一致前缀的动作名称——例如，所有浏览器相关工具都以`browser_`开头，命令行工具以`shell_`开头。这使我们能够轻松强制智能体在给定状态下仅从某组工具中选择，而无需使用有状态的logits处理器。

这些设计有助于确保Manus智能体循环保持稳定——即使在模型驱动的架构下。

### 将文件系统用作Context

现代前沿LLM现在提供128K token或更多的context窗口。但在现实世界的智能体场景中，这通常是不够的，有时甚至是负担。有三个常见的痛点：

1. **观察结果可能很庞大**，特别是当智能体与网页或PDF等非结构化数据交互时。很容易超过context限制。

2. **模型性能往往在超过某个context长度后下降**，即使窗口在技术上支持它。

3. **长输入很昂贵**，即使有前缀缓存。你仍然需要为传输和预填充每个token付费。

为了处理这个问题，许多智能体系统实现context截断或压缩策略。但过于激进的压缩不可避免地导致信息丢失。问题是根本性的：智能体本质上必须基于所有先前状态预测下一个动作——而你无法可靠地预测哪个观察结果可能在十步后变得关键。从逻辑角度来看，任何不可逆的压缩都带有风险。

这就是为什么我们将文件系统视为Manus中的终极context：大小无限、本质上持久，并且可以由智能体本身直接操作。模型学会按需写入和读取文件——将文件系统不仅用作存储，而且用作结构化的外部化内存。

![Image 3](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/sBITCOxGnHNUPHTD.png)

我们的压缩策略总是设计为可恢复的。例如，只要保留URL，网页内容就可以从context中删除；只要路径在沙箱中仍然可用，文档内容就可以省略。这使Manus能够缩短context长度而不会永久丢失信息。

在开发这个功能时，我发现自己在想象状态空间模型（SSM）在智能体设置中有效工作需要什么。与Transformer不同，SSM缺乏完全注意力机制，在长程后向依赖方面存在困难。但如果它们能够掌握基于文件的内存——外部化长期状态而不是在context中保持——那么它们的速度和效率可能会解锁新一类智能体。智能体SSM可能是[神经图灵机](https://arxiv.org/abs/1410.5401)的真正继承者。

### 通过复述操纵注意力

如果你使用过Manus，你可能注意到了一些有趣的事情：在处理复杂任务时，它倾向于创建一个todo.md文件——并在任务进行时逐步更新它，勾选已完成的项目。

这不仅仅是可爱的行为——这是一个操纵注意力的深思熟虑的机制。

![Image 4](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/OYpTzfPZaBeeWFOx.png)

Manus中的典型任务平均需要大约50次工具调用。这是一个长循环——由于Manus依赖LLM进行决策，它容易偏离主题或忘记早期目标，特别是在长context或复杂任务中。

通过不断重写待办事项列表，Manus将其目标复述到context的末尾。这将全局计划推入模型的最近注意力范围，避免"迷失在中间"的问题并减少目标错位。实际上，它使用自然语言来偏向自己对任务目标的关注——而无需特殊的架构更改。

### 保留错误内容

智能体会犯错误。这不是bug——这是现实。语言模型会产生幻觉，环境返回错误，外部工具行为异常，意外的边缘情况总是出现。在多步任务中，失败不是例外；它是循环的一部分。

然而，一个常见的冲动是隐藏这些错误：清理跟踪、重试动作，或重置模型状态并依赖神奇的"[temperature](https://arxiv.org/abs/2405.00492)"。这感觉更安全、更可控。但这是有代价的：擦除失败会移除证据。没有证据，模型无法适应。
