---
type: Concept
id: 254_icm_knowledge_big
title: "ICM_knowledge.md (part 255/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

You're deep in a function, a priority comes in — drop a TODO so you don't lose your place

You notice something needs doing but it's not the current task — note it so it doesn't get forgotten

If you come back to that file a month later, the TODO catches what fell through the cracks

Cleanup context: When a file-level TODO is completed, remove it from the header. When all TODOs are done, reset to "None". If a TODO turns into a real task, move it to the project plan and remove it from the header.

Function Documentation

Document every public/exported function. Internal helper functions need docs only when the logic isn't obvious from the name and signature.

#### JS/TS pattern:

Calculates the prorated subscription cost for a partial billing period.

Uses daily rate × remaining days, rounded to 2 decimal places.

@param planMonthlyRate - The full monthly rate in dollars

@param startDate - When the subscription started (mid-cycle)

@param billingCycleEnd - End date of the current billing cycle

@returns Prorated cost in dollars (e.g., 14.52)

function calculateProratedSubscriptionCost(

planMonthlyRate: number,

startDate: Date,

billingCycleEnd: Date

): number {

// function body...

#### C header pattern (API contract):

Allocates a block from the thread-local memory pool.

Falls back to system malloc if pool is exhausted.

@param size Bytes to allocate (rounded up to pool alignment)

@return   Pointer to allocated block, or NULL on failure

Thread-safe: yes (per-thread pools, no locks needed)

Reentrant: no (modifies pool state)

void *pool_alloc(size_t size);

#### Rust pattern:

/// Calculates the prorated subscription cost for a partial billing period.

/// Uses daily rate × remaining days, rounded to 2 decimal places.

/// # Arguments

plan_monthly_rate

\-    The full monthly rate in dollars

\-    When the subscription started (mid-cycle)

billing_cycle_end

\-    End date of the current billing cycle

/// # Returns

/// Prorated cost in dollars (e.g., 14.52)

fn calculate_prorated_subscription_cost(

plan_monthly_rate: f64,

start_date: NaiveDate,

billing_cycle_end: NaiveDate,

// function body...

Inline Comments

Use inline comments to explain why, not what. The code shows what it does — comments explain the reasoning that isn't obvious.

// Offset by 1 because the API uses 1-based page indexing

const apiPage = displayPage + 1;

// Must check auth before loading data — the API returns 200 with empty

// results for unauthorized users instead of 401

await verifyAuthStatus();

const results = await loadDashboardData();

#### Don't write comments that just restate the code:

// BAD — restates the code

const total = price * quantity; // multiply price by quantity

// GOOD — explains the business rule

const total = price * quantity; // pre-tax total, tax applied at checkout

Folder Structure Patterns by Language
