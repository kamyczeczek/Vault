---
type: Concept
id: 251_icm_knowledge_big
title: "ICM_knowledge.md (part 252/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Read this file at the start of any coding phase. These are @David Herrera's personal coding conventions that apply to every project, every language, every framework. They override defaults and must be followed unless explicitly told otherwise.

Code is navigated spatially. The folder tree is a mental map — every directory, file, and function name is a landmark. When the structure is clean and names are descriptive, you can find what you need without searching. When it's not, you're lost in your own codebase.

These rules exist to keep code navigable, scannable, and small enough to hold in your head.

@David Herrera's Comment

This is what I use personally. This was made by giving claude 20ish years of my code. its designed to make sure claude writes and organizes code in exactly the way i write and organize code. this makes sure it fits my mental model. one thing i did add was inline documentation and header status/tasks/todos/notes. this along with being very intentional about my naming conventions makes for easy to navigate code blocks. inline docs gives the model context as it goes instead of having to force it to fish for context. allot of your rules belong in the claude.md and not necessarily your coding standards. but thats a bit knitpicky. and allot of these thigns are things you as the lead need to be watching for because most models will still do these things.

Universal Rules

These apply to ALL code in ALL languages. No exceptions.

Descriptive Names — Everything

Every name must tell you what it is at a glance. Files, folders, functions, variables, types, classes, routes, components, database tables, columns — everything.

The test: Would you know what this is from the file tree alone, without opening it?

BadGoodutils.tsdateFormatUtils.tshelpers.tspricingCalculationHelpers.tsdata.tsuserSessionData.tshandler()handleFileUploadComplete()process()processIncomingWebhookPayload()calc()calculateMonthlySubscriptionCost()ItemInventoryLineItemmanage()manageConnectionPool()ServiceNotificationDeliveryServicetmppendingUploadBuffer

Prefer longer, descriptive names over short, ambiguous ones. Abbreviations are acceptable only when universally understood (id, url, http, db, api, auth).

Small Functions — ~100 Lines of Code Max

The ~100-line limit applies to the function body only — the executable logic. Documentation comments above the function do NOT count toward this limit.

If a function body is growing past ~100 lines, look for logical extraction points

Each function should do one thing and do it well

Aim for concise, precise code — fewer lines that do more, not sprawling logic

Use one blank line to separate logical chunks within a function for readability — but no more than one

Don't add unnecessary blank lines just for spacing — simplify the logic instead

Small Files — Under 1,000 Lines of Code
