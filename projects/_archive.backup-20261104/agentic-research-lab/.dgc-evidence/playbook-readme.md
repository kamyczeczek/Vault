# Agent Debugging Playbook

AI agents fail differently from traditional software. A normal stack trace can tell you where code crashed, but not why an agent selected a tool, skipped a guardrail, retried the wrong step, or continued after stale context.

This playbook collects practical debugging patterns for production AI agents:

- Trace every model decision and tool call.
- Preserve run evidence before logs rotate or state changes.
- Use replay to compare expected vs actual behavior.
- Build decision graphs that explain branching paths.
- Capture approval, suspend, resume, and rollback events.

The goal is simple: when an agent behaves incorrectly, you should be able to reconstruct what happened, prove what actually executed, replay the failure path, and ship a regression test.

## Start Here

1. Read the walkthrough: [`walkthroughs/refund-agent-expired-approval-token.md`](walkthroughs/refund-agent-expired-approval-token.md)
2. Use the production checklist: [`checklists/production-agent-debugging-checklist.md`](checklists/production-agent-debugging-checklist.md)
3. Check replay readiness: [`checklists/replay-readiness-checklist.md`](checklists/replay-readiness-checklist.md)
4. Copy the incident template: [`templates/incident-debugging-template.md`](templates/incident-debugging-template.md)

## What's Inside

```text
checklists/
  production-agent-debugging-checklist.md
  failed-tool-call-checklist.md
  replay-readiness-checklist.md
examples/
  open-telemetry-agent-spans.json
  decision-graph.mmd
  replay-fixture.jsonl
templates/
  incident-debugging-template.md
  run-evidence-template.md
walkthroughs/
  refund-agent-expired-approval-token.md
resources/
  glossary.md
  further-reading.md
```

## Core Debugging Questions

When an agent fails, answer these before changing code or rerunning the workflow:

- What was the exact run ID and trace ID?
- Which model, prompt, tool registry, and agent version executed?
- Which context was available to the agent?
- Which tool calls were attempted, with which arguments and results?
- Which approvals, suspends, resumes, retries, and rollbacks occurred?
- What evidence proves the action actually happened?
- Can the failure be replayed without touching production systems?

## Maintainer

Maintained by [Opswald](https://www.opswald.com), an AI agent debugging platform focused on traces, replay, and decision graphs.

This repo is intentionally practical and vendor-light. The patterns should be useful whether you use Opswald, custom OpenTelemetry, LangGraph, OpenAI Agents SDK, Claude Code-style agents, or your own orchestration framework.
