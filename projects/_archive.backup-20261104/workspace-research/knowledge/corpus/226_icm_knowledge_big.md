---
type: Concept
id: 226_icm_knowledge_big
title: "ICM_knowledge.md (part 227/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

I spent until 00:30 AM rebuilding the MCP Playwright logic. I quickly figured out that Playwright can generally only run on one tab per session. BUT... it can run on one tab per browser.

The Multi-Browser "Boom"

Because of company IT limits, I could only get three browsers: Chrome, Edge, and Firefox. I fired up all three simultaneously, each running its own Claude-driven Playwright instance.

Browser 1 (Chrome): Processing Sales Rep A

Browser 2 (Edge): Processing Sales Rep B

Browser 3 (Firefox): Processing Sales Rep C

BOOM. I was suddenly 3x faster. I sat back and watched the "manual hell" disappear across three screens. However, this BURNED THROUGH my tokens! Even with the 5x plan the company now pays for, I knew I couldn't keep this up.

In Part 2: I’ll explain how—later that same night—I realized I was still being "inefficiently lazy" and managed to cut my token usage by 90% and increase the speed by 10X.

Mini-Series Part 2: The "Token Crash" & The Keyboard Epiphany

In Part 1, I was riding high. I had Chrome, Edge, and Firefox all running simultaneously, tripling my speed on a massive D365 rebilling project. I felt like I’d cracked the code to being "efficiently lazy."

Link: Mini-Series Part 1: The "Manual Hell" Rebill Project · Clief Notes

But the victory was short-lived. I was driving the car at 100mph, but I didn't realize how much fuel I was burning.

The Crash: 3 Hours to Zero

The next morning, I fired up all cylinders. It was beautiful—until it wasn't. In under 3 hours, I burned through my entire token allotment. I was dead in the water with a 1.5-hour wait until my limits reset. With the clock ticking and sales reps still needing updates, I had to go back to doing it manually.

And that’s when the "Aha!" moment happened.

The "Tab" Breakthrough

While I was clicking and typing manually to pass the time, I realized something: I wasn't really using the mouse. I was mostly hitting Tab and Shift-Tab to navigate the D365 fields.

I asked Claude: "Can Playwright just 'Tab' through the browser instead of searching for elements and taking screenshots for every move?"

Claude’s answer: YES. My jaw dropped.

From "Visual Driving" to "Macro Speed"

The old workflow relied on Claude "seeing" the screen via screenshots to make sure it was in the right spot. It was accurate, but heavy. I had Claude rewrite the interior workflow to a deterministic loop:

The Setup: I open the URL, set the filters, and select the first row.

The Loop: * Tab to Invoice → Enter.

I added small buffers (100ms between tabs, 4s for page loads) to ensure D365 could keep up.

See the video for how the flow runs in real life!

The Result: 90% Savings & 10x Efficiency

#### I asked Claude to evaluate the two methods. The numbers were staggering:

#### Old "Visual" Flow:

Tool Calls: ~500 calls per 50 orders

Token Usage: 100% (High Burn)

Logic: Screenshot-dependent (Slow)

#### New "Tab" Flow:

Tool Calls: 1–4 calls per 50 orders

Token Usage: 10% (90% Reduction!)
