---
type: Concept
title: trustworthy-agent-tests
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Trustworthy Agent-Generated Tests

Research for D-001: how should an agent create automatic tests that *actually*
confirm built behavior works, rather than tests that merely run green?

Method: `agent-reach` routing (GitHub REST API search + `curl r.jina.ai` for
reading). All cited URLs verified reachable (HTTP 200) on 2026-10-01.

## 1. Why naive generated tests lie

The core failure mode is the **oracle problem**: a test only proves something if
it can detect faults. Defining "the correct output for a given input" is the
_test oracle problem_, considered "a relatively hard problem" tied to
controllability and observability. An agent that writes code and its own tests
is a weak oracle: the same context that produced a bug also produces a test that
codifies the same misunderstanding.

- Primary source: [Test oracle — Wikipedia](https://en.wikipedia.org/wiki/Test_oracle).
  The term comes from Howden; Weyuker's survey of oracle categories.

Concrete sub-failures observed in the mutation-testing literature:

- **The coverage/correctness gap.** Line/branch coverage "measures only which
  code is *executed* by your tests. It does *not* check that your tests are
  actually able to *detect faults*". A suite can "execute all its branches" and
  still miss defects (partially tested code). → from [PIT Mutation
  Testing](https://pitest.org/).
- **Vacuous / no-assertion tests.** "The most extreme examples of the problem
  are tests with no assertions." A generated test that calls a function and
  asserts nothing is green regardless of behavior. → from
  [PIT — weak tests](https://pitest.org/weak_tests).
- **"AI writes your code. AI writes your tests. But who tests the tests?"**
  Copilot/Claude/ChatGPT "generate code faster than humans can review it. They'll
  even write tests that pass. But passing tests aren't the same as *meaningful*
  tests." → from [mbj/mutant](https://github.com/mbj/mutant).
- **Tautological tests.** An assertion derived from the code under test
  (test == implementation) is always true and detects nothing. This is the
  agent analogue of the no-assertion test: the test *encodes* the bug.

Key claim: a green test suite is *necessary but not sufficient*. The agent must
ask, per behavior, "what would this test fail on?" — and ideally prove it can
fail.

## 2. Patterns that make tests trustworthy

### 2a. Acceptance criteria before implementation (executable oracles)
Write the *expected* behavior (oracle) from the spec *before* the code exists,
so the test cannot be reverse-engineered from a buggy implementation. This is
design-by-contract / specification-first testing; oracles are "used before a test
is run with expected results encoded into the test logic." → [Test
oracle](https://en.wikipedia.org/wiki/Test_oracle). For an agent: fix the
oracle from the request/intent, not from the produced code.

### 2b. Mutation checking (does the test actually bite?)
Mutation testing "seed[s] faults into your code, then your tests are run. If
your tests fail then the mutation is killed, if your tests pass then the
mutation lived. The quality of your tests can be gauged from the percentage of
mutations killed." PIT calls mutation testing "the gold standard against which
all other types of coverage are measured." → [PIT](https://pitest.org),
[hcoles/pitest](https://github.com/hcoles/pitest),
[stryker-mutator/stryker-js](https://github.com/stryker-mutator/stryker-js).

Each *alive (surviving) mutation* is a call to action, with exactly two honest
options: "Keep the mutated code" (the test over-specified) or "Add the missing
test" (the test is shallow). → [mbj/mutant](https://github.com/mbj/mutant).
This gives an agent a mechanical, falsifiable signal that a suite is not
tautological: high surviving-mutation rate ⇒ the tests don't actually check the
behavior.

### 2c. Property-based / randomized testing (find the edge cases)
Property-based testing "write tests which should pass for all inputs in
whatever range you describe, and let [the tool] randomly choose which of those
inputs to check — including edge cases you might not have thought of." When a
bug is found, it "reports the simplest possible one" (shrinking). →
[hypothesis.works](https://hypothesis.works). Properties encode *invariants*
(the oracle) rather than one hand-picked example, so they resist the
tautology failure far better than example-based asserts.

### 2d. Independent verification by a separate session/agent
Because the same context that wrote the code is a weak oracle, a *second*
agent (or session) with the oracle handed in — but **without** the
implementation — re-derives expectations and/or runs mutation/fuzz checks.
Independence is what restores the oracle's power. For LLM/agent apps, add
behavioral **red-teaming / evals** on top of unit tests: [promptfoo —
"Test your prompts, agents, and RAGs. Red teaming/pentesting/vulnerability
scanning for AI"](https://github.com/promptfoo/promptfoo).
(Companion open-source tooling: [langfuse](https://github.com/langfuse/langfuse)
for agent tracing/evals.)

### 2e. Evidence logs (make PASS mean VERIFIED)
Record, per test: the command, the input, the *observed* actual vs. the
*independently-stated* expected, and the exit status. A test that logs only
"PASS" without the expected value is unfalsifiable. This mirrors this
workspace's own scar (see `LEARNINGS` / AGENTS tooling hygiene): a gate's
`FAIL:` is evidence; the expected-vs-actual pair is the artifact. Use a
deterministic runner so results are reproducible:
[pytest](https://docs.pytest.org).

## 3. Adoption criteria for this project's pipeline gates

Proposed, concrete, falsifiable gate rules (no pipeline/ code touched here —
these are the criteria gates should encode):

1. **Oracle-first.** No test may be added by an agent without a named expected
   value/invariant derived from the spec *before* the implementation step.
   GATE check: the test file predates, or cites, the intent it verifies.
2. **Anti-vacuity.** A test that has no assertion, or whose assertion is
   `True`/a copy of the code, is rejected. Mutation check on the module; a
   surviving-mutation that removes an observable behavior ⇒ the gate fails.
3. **Independent re-derivation.** At least one acceptance expectation is
   re-derived by a session that was not given the implementation.
4. **Falsifiability evidence.** Every PASS carries the command + actual +
   expected + exit status. "PASS" with no expected value is a `FAIL` of the
   evidence gate.
5. **Behavioral coverage of agents** (prompt/agent/RAG): a red-team/eval pass
   runs alongside unit tests, not in place of them.

## Primary sources (all verified HTTP 200, 2026-10-01)

- https://en.wikipedia.org/wiki/Test_oracle
- https://pitest.org  (+ weak-tests: https://pitest.org/weak_tests)
- https://github.com/hcoles/pitest
- https://github.com/stryker-mutator/stryker-js
- https://github.com/mbj/mutant
- https://hypothesis.works
- https://github.com/promptfoo/promptfoo
- https://docs.pytest.org
