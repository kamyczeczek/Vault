---
type: Concept
id: 00_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 1/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Repository: yzfly/awesome-context-engineering
Files analyzed: 15

Estimated tokens: 79.8k

Directory structure:
└── yzfly-awesome-context-engineering/
    ├── README.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README_CN.md
    └── docs/
        ├── claudecode/
        │   ├── claude-code-best-practices-zh.md
        │   ├── claude-code-best-practices.md
        │   └── effective-context-engineering-for-ai-agents.md
        ├── dbreunig/
        │   ├── how-contexts-fail-and-how-to-fix-them.md
        │   ├── how-to-fix-your-context.md
        │   ├── 上下文修复的实用指南.md
        │   └── 长上下文的失效原理及解决方案.md
        ├── langchain/
        │   ├── context-engineering-for-agents.md
        │   └── 智能体的Context工程-中文版.md
        └── manus/
            ├── AI智能体的Context工程：构建Manus的经验教训.md
            └── Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus.md

================================================
FILE: README.md
================================================
# Awesome Context Engineering

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![GitHub stars](https://img.shields.io/github/stars/yzfly/awesome-context-engineering.svg?style=social&label=Star)](https://github.com/yzfly/awesome-context-engineering)
[![GitHub forks](https://img.shields.io/github/forks/yzfly/awesome-context-engineering.svg?style=social&label=Fork)](https://github.com/yzfly/awesome-context-engineering)

A curated collection of resources, papers, tools, and best practices for **Context Engineering** in AI agents and Large Language Models (LLMs).

> Context engineering is the art and science of filling the context window with just the right information at each step of an agent's trajectory.

[中文版本](README_CN.md) | [English](README.md)

## 📚 Table of Contents

- [What is Context Engineering?](#what-is-context-engineering)
- [Featured Articles](#featured-articles)
- [Research Papers](#research-papers)
- [Tools & Projects](#tools--projects)
- [Expert Insights](#expert-insights)
- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
- [Contributing](#contributing)
- [Star History](#star-history)

## What is Context Engineering?

Context Engineering is the systematic optimization of information payloads for Large Language Models (LLMs). It encompasses:

- **Context Retrieval & Generation**: Selecting and creating relevant information
- **Context Processing**: Organizing and structuring context for optimal consumption
- **Context Management**: Handling context windows, memory, and state across interactions
- **Context Compression**: Reducing token usage while preserving essential information
- **Context Isolation**: Separating concerns across different context spaces

## 📖 Featured Articles

### Context Rot: How Increasing Input Tokens Impacts LLM Performance
- https://research.trychroma.com/context-rot
