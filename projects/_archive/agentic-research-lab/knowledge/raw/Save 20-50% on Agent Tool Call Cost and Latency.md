---
type: Concept
title: Save 20-50% on Agent Tool Call Cost and Latency
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Save 20-50% on Agent Tool Call Cost and Latency — Structured Notes

## Overview
- Demo showing how **BAML** reduces token usage and cost/latency for agent tool calls.
- Works with **any language**; demo uses **Python**.
- Uses **GPT-4 mini** as the test model.
- BAML is designed to improve tool calling by using models more efficiently.
- All tooling shown is provided by BAML; running `baml init` auto-installs everything.
- Core technique demonstrated: **schema-aligned parsing**.

---

## Problem Being Solved
- Typical LLM tool calls return:
  - Backticks
  - JSON
  - Extra quotation marks
  - Schema-related errors
- Developers often must:
  - Force the model to think about schemas and output orientation
  - Add error correction
  - Retry when the model misunderstands
- This wastes tokens, increases latency, and adds complexity.

---

## Demo Setup
- Quick BAML project created in Python.
- Swap to `gpt-4-mini`.
- A function is transformed into a prompt.
- A test case is written.
- Running the code normally produces backticks and JSON, then simple error correction extracts the right value.

---

## Token-Saving Techniques

### 1. Prefix = Answers
- Tell the model: **“we don’t care”** / use a prefix-style answer.
- Prompt changes to say this instead.
- `ctx.output_format` takes the function return type and schematizes it.
- Model omits quotation marks.
- Tokens: **72 → 64**

### 2. No Quotes Around Strings
- Explicitly instruct: **no quotes around strings**.
- Model returns no quotes at all.
- Values are still extracted correctly.
- Tokens: **64 → 56**
- Total reduction: **72 → 56**
  - Speaker initially says “77% fewer tokens,” then corrects to **~23% fewer tokens**.
  - 56 / 72 = ~77.8% remaining, so ~22.2% fewer.

### 3. Hardcoding the Prompt Further
- Instead of using the compiler, hardcode what the prompt says.
- Change function to return an array, but nothing in the prompt says that.
- `Experience` class will actually return an `Experience`.
- Model runs and produces data, but:
  - Right side gets an array.
  - Array contains experience tokens.
  - It is an empty array because a string cannot be cast to the `Experience` class.
- If the type is `Experience or null`:
  - You get three `null`s.
  - Each string cannot be cast to `Experience`, but can be cast to `null` as a best effort.

### Philosophy Behind This
- Developer no longer has to force the model to think about schemas or orientations.
- Algorithms do this work.
- Happens in **millisecond time** while streaming.
- Gives really good control over exactly what happens.
- Dramatically fewer tokens from two angles:
  1. Cutting absolute tokens.
  2. Avoiding retries when the model misunderstands or makes slight errors.
- Instead of retrying, BAML pulls out as much data as possible with rich information.
  - Example: “items may be dropped”
  - You know exactly which items were dropped.
  - You can decide whether to retry based on constraints.

---

## Robustness / Error Handling
- Switch back to using `output_format`.
- It doesn’t matter if the model outputs:
  - Backticks
  - No quotes
  - Quotes somewhere else
- BAML built a strong algorithm for parsing data from **non-deterministic systems** into the **type system of your choice**.

---

## Cross-Language Usage
- Example in Python:
  ```python
  from baml_client import b
  r = b.extract_resume(...)
  r.experience  # guaranteed to be a list of experiences or none
  ```
- Update to purely a list of experiences and no longer optional:
  - Now it is a list of experiences.
- BAML does bridging across type systems in every language of your choice.
- When coding or agentically coding, everything is **type-system driven**.
- The hard work of getting type-system data is left to the compiler or tooling built to do it robustly.

---

## Key Claims
- Title: **Save 20-50% on agent tool call cost and latency**.
- Demo shows **~23% fewer tokens** in one scenario (72 → 56).
- Works with any language.
- BAML is designed to help you do incredibly good tool calling.
- Technique is called **schema-aligned parsing**.

---

## Takeaways
- Let algorithms handle schema compliance, not the model.
- Use type systems and compilers for robust parsing.
- Partial extraction with metadata enables smarter retry decisions.
- Reduces tokens and latency by avoiding retries and schema negotiation.
- BAML provides cross-language bridging and auto tooling.
- Core idea: parse non-deterministic model output into deterministic typed data as efficiently as possible.