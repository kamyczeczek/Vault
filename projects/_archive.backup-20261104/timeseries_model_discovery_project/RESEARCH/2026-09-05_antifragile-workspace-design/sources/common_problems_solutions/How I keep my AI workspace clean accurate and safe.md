---
type: Concept
title: How I keep my AI workspace clean accurate and safe
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

How I keep my AI workspace clean, accurate, and safe (the two rituals that I run every single session)

💡Let me start with the truth of things first, because the truth is the lesson.

================= Token Warning ⚠️==========

Before anyone comes for me 😅

📝 Note: depending on what you are loading, you are accruing token cost. And token cost can balloon if you are not careful.

If any of the files in the initializing phase or handoff phase are large this can become a token intensive practice so when curating this process, BE INTENTIONAL only load what is absolutely needed for the project to start up and for you to get to the fun part, building!

I budget for my own needs, for me this initialization for me is between 5k and 10k, I have made the mistake of making 40k, don't do that!

If you want to understand an estimate of what your character to token ratio is use the site below:

[Tokenizer - OpenAI API](https://platform.openai.com/tokenizer)

Anthropic tokenizer has not been released yet, but Its a few % higher than OpenAI in some cases.

Plain English sentence (115 characters)

- OpenAI GPT-4: 23 tokens
- OpenAI GPT-4o: 23 tokens
- Claude (content only): 23 tokens
- Result: identical

Code and markdown snippet (86 characters)

- OpenAI GPT-4: 24 tokens
- OpenAI GPT-4o: 26 tokens
- Claude (content only): 27 tokens
- Result: Claude a few percent higher

Numbers and punctuation (55 characters)

- OpenAI GPT-4: 25 tokens
- OpenAI GPT-4o: 25 tokens
- Claude (content only): 27 tokens
- Result: Claude about 8 percent higher

One honest footnote: Claude's API adds roughly 7 fixed tokens per message for formatting. On a single short line that looks like a big gap. On a real document it amortizes down to almost nothing.

✅The takeaway:

for the same English text, the tokenizers land within a few percent of each other. The scary "Claude costs way more tokens" headlines do not hold up when you actually measure it. Verified beats confident, every time.

You have been learned and you have been warned!

============ Back to it! 👇=================

I have lost work. An automated cleanup script once deleted dozens of session files we could not get back. The rebuild was awful, painstaking, and a lesson learned.

We came within one command of running a test suite against a live database full of real data.

A contact form sat quietly broken for a full week because a safety shortcut faked success instead of telling us it failed.

None of those were bad luck. Every one of them happened the same way: moving fast, skipping the boring step, trusting that this time it would be fine.

For me, the solution was building two rituals.

1️⃣ My Initialization ritual

2️⃣ My Handoff ritual.

These run every session, no exceptions. Here is exactly what they do, and why they work.

⭐ Ritual 1: Initializing (the pre-flight)

Before any real work happens, we run a start sequence. Think of a pilot's pre-flight checklist. (Shameless reference 😊 I know)

Flight number one and flight number ten thousand get the same checklist, because the day you skip it is the day it's things go wrong.

Here is the shape of it:

=========👍 Initialization Starts================

SESSION START (initializing)

├── 1. Read the handoff first

│-----├── where we left off

│-----├── what is next

│-----└── what is blocked

├── 2. Load only what this project needs

│-----└── less noise, fewer mistakes

├── 3. Load the hard rules, every time

│-----├── no irreversible change without a human check

│-----├── verify before stating anything as fact

│-----├── show the raw output, never a summary

│-----└── protect the data

└── 4. Give a short briefing, then stop

│-----├── where we are

│-----├── what is next

│-----├── blockers

│-----├── open questions

│-----└── proposed first move

By the time work starts, nobody is guessing.

=========👍 Initialization is complete at this point====

=============Session Start - You build =============

Where the magic happens! 🧙🧙‍♂️🧙‍♀️🧝‍♂️🧝🧝‍♀️🎩🪄🔮✨

=============Session Ends - Building Stopped=======

=========👇 Session ends - Handoff Ritual Begins====

📝 Note: the same Token awareness is required at this point as well, giving sharp intentional instruction makes a huge difference and it will save you time and money (Tokens)

⭐ Ritual 2: The handoff (the post-flight log)

When the session ends, we do not just walk away. We close out on purpose.

SESSION END (handoff)

├── 1. Update the handoff

│-----├── what got done

│-----├── what is next

│-----└── what is still blocking

├── 2. Update the health log

│-----├── issues found

│-----└── issues resolved

├── 3. Confirm a clean baseline

│-----├── run the tests

│-----└── run the build

└── 4. Tag the known-good point

│-----└── recommend where next session starts

=========👇 Session ends - Handoff Ritual Ends====

The next session opens to a clean desk instead of a mystery.

💡 What this actually buys me 💡

Three things, and they make things a lot easier to maintain for me.

🧼 Clean.

Every session starts from a known, current state. No drift, no stale notes, no "wait, what were we doing."

🎯 Accurate.

Nothing gets called done without proof. We show the real output, not a confident summary. No guessing dressed up as fact.

🛟 Safe.

Data protection is baked in, and the human is always the gate. Nothing permanent happens without a check first.

💡You can use this today; you do not need my exact setup. You need two bookends, and a handful of plain files that hold the state between them.

1️⃣ Initialization ritual

2️⃣ Handoff ritual.

YOUR WORKSPACE

├── start-ritual---------|→ load context + rules BEFORE any work--- Be mindful of input size

├── end-ritual----------|→ write down state BEFORE you close --- Be mindful of output size

└── the files they read

├-├── handoff.md---------| ← where we left off, what is next

├-├── health-log.md------| ← open issues, what is fixed

├-├── standards.md------| ← the rules you never break

├-└── start-here.md------| ← the ritual itself, written down

Write it down. Make it repeatable. Run it every time, especially when you are tired, because tired is exactly when the boring step gets skipped, and when the work is in danger of re-work.

Note: in this example, the handoff ritual is being run manually at the end of each session. I originally had it fire at right before the compact signal, but by the time it fired, Claude Code is already degraded.

I am now trying to fire the handoff at the statuslines 50% mark, this seems to be the point where degradation starts.

📝 The 7 Ps are real.

💡Proper Prior Planning Prevents Piss Poor Performance.