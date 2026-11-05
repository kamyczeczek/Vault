---
type: Concept
id: 225_icm_knowledge_big
title: "ICM_knowledge.md (part 226/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

📝 What this is: Part 2 of the rebill automation series — how hitting token limits led to replacing screenshot-based AI with keyboard-driven scripts, cutting API usage by 90% and going 10x faster.

💡 Why it matters: Using AI to watch your screen is expensive and slow — using it to write the automation script once and then running deterministic keystrokes is the actual unlock.

🏷️ Tags: automation, workflow-design, claude-code, browser-automation, optimization

⏱️ 4 min read | 🔓 Free

✍️ David's note: This is the sequel that delivers. Allan hit his token wall and instead of buying more credits, he redesigned the approach — AI writes the script, the script does the work. The "dead man's switch" pattern for protecting live data is something everyone doing browser automation should steal. Constraint-led creativity at its finest.

Mini-Series Part 1: The "Manual Hell" Rebill Project

Following up on my previous post about automating month-end, I want to pull back the curtain on the project that really started it all. It involves a massive company reconstruction, a "manual hell" task, and a midnight breakthrough that tripled my productivity.

The Problem: A Reconstruction Hangover

On January 1, 2026, our company underwent a major reconstruction. Customers were assigned new sales reps, but the final list of who owned which account wasn't finalized until April.

In the meantime, we kept invoicing as usual. The invoices were correct, but the Sales Rep field on the historical records was now wrong. To fix it, we had to go back and update thousands of already invoiced sales orders.

#### The Manual Workflow (or: How to lose your mind):

Search for the Sales Order.

Click Invoice.

Click Rebill.

Change the Sales Rep.

Hit Esc to exit.

Repeat... hundreds (or thousands) of times.

Enter Claude Code & Playwright

I had just started using Claude Code on March 19th after watching @Jake Van Clief ’s videos. Two weeks later, this assignment landed on my desk in the middle of my usual accounting duties.

Since I didn’t have backend API access to D365 F&O, I turned to the Playwright MCP. If I couldn't talk to the database directly, I’d have Claude "drive" the browser just like a human would.

#### The Automation Logic:

Open Chrome to the D365 Sales Order URL.

Open the filters tab.

Add filter information (Customer account, dates for Q1 2026, and identifying which sales orders had the wrong rep).

Execute the "Rebill" click-path automatically.

The "Aha!" Moment at 00:30 AM

It worked, but it was real slow. D365 isn't exactly a speed demon. My boss was happy ("as long as we don't have to do it, I don't care how slow it is"), but I knew we could do better.

Earlier that day, I was running it in one browser and it was taking forever. While the kids were finally asleep that night, I had an idea: Can I run this on more than one tab?
