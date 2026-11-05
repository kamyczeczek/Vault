---
type: Concept
title: Building a Practical AI Assembly Line
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Building a Practical AI Assembly Line — Structured Notes

## Overview
- Episode of *AI That Works* with Dex (founder of Human Layer) and Vibhav (working on BAML programming language).
- Topic: Using **Storybook** as part of an agentic coding workflow for UI development.
- Core idea: Build UI components in isolation (pure components) so agents can iterate rapidly without running the full app.
- Live demonstration: migrating a codebase to use Storybook components, specifically a data renderer for LLM call results.

---

## The Problem: Front-End Iteration with AI

### Planning Docs Work Better for Backend
- Planning and reviewing markdown docs are great for backend/system design.
- They are **not as effective for frontend** because you can't visualize how things will look from code alone.
- Design discussions, structure outlines, and component names don't tell you if the UI will look good.

### The Feedback Loop is Slow
- Traditional flow: research → design discussion → outline → implementation → finally see UI.
- Assumptions about UI are often wrong and only discovered during implementation.
- To test a UI change, you have to run the whole app, click through states, reproduce data conditions.

### Agentic Loop Problem
- With agents, you often have to run the LLM all the way through to see results.
- Hard to iterate on just the UI; app state must be continuously reloaded.
- Large codebases make agent runs slow because they have to process everything.

### Analogy: Learning Tests
- Previous episodes discussed "learning tests" — small scripts that verify assumptions about code/external systems during planning.
- Storybook is the same idea for UI: verify how things will look and behave before full implementation.
- Find unknowns during planning instead of during implementation.

---

## The Solution: Storybook for UI Components

### What is Storybook?
- A tool for building UI components in isolation.
- Been around 10+ years, since early React.
- Allows you to render a component with different sets of props (stories) without running the full app.
- Open source; collects anonymous analytics by default (can be turned off).

### Why Storybook for Agents?
- Agents are very good at writing React code.
- Figma and other WYSIWYG tools are not as agent-friendly.
- Storybook is just code — agents can edit files on disk.
- Enables a fast hot loop: edit component, see result immediately.
- Can use agent browser or screenshots to let the agent visually verify changes.

### Core Architecture: Pure vs. Wired Components
- **Pure components**: stateless, take props, render UI. No API calls, no state, no side effects.
- **Wired components**: handle state, data fetching, business logic; pass props to pure components.
- Pure components live in a shared UI package (e.g., `packages/ui`).
- Wired components live in apps and are specific to the context (e.g., cloud vs. on-prem).
- Storybook is for pure components; stateful/API components generally should not be in Storybook.

### Example Structure
```
apps/
  app1/
  app2/
packages/
  ui/          # pure components
    Button/
    Card/
    DataTable/
```
- Same pure component imported across multiple apps.
- Wrapper component's only job: business logic → props → pure component.

---

## Agentic Workflow with Storybook

### Bootstrapping Storybook
- Ask agent to bootstrap Storybook in the repo.
- It will install dependencies, create config, and generate a few hello-world stories.
- Then incrementally add components.

### Adding Components
- Identify a component to migrate or create.
- Ask agent: "Take this component and add it to Storybook. Split it into wired vs. pure if needed."
- If already pure, simply add stories.
- Agent creates `.stories.tsx` files that render the component with different prop combinations.

### Iterating on UI
- Open Storybook locally (e.g., port 6009).
- View component in all states.
- Edit props directly in the Storybook UI to test edge cases.
- Give feedback to agent: "I don't like this state, change it."
- Agent edits the component and stories; hot reload shows changes.

### Handling Edge Cases
- When a bug is found in production, paste the bad state into Claude: "Here's a bad state, add it to Storybook, then fix it."
- Storybook becomes a living library of every state the component can be in.
- Example: array rendering, empty arrays, closed arrays, error states, loading states.

### Visual Verification
- Use agent browser or screenshot tools to capture Storybook output.
- Can set up a PNG loop: agent takes screenshot, compares, iterates until it looks right.
- Storybook can render inside a frame (e.g., VS Code pane) to simulate real context.

### PR Review
- Teams can review just the Storybook stories in a PR.
- Pull down the branch, run Storybook, visually inspect components.
- Better than Figma because it's the actual code, no translation step.

---

## Key Benefits

| Benefit                        | Description                                                  |
| ------------------------------ | ------------------------------------------------------------ |
| Faster iteration               | Edit component, see result immediately without running full app |
| Edge case testing              | Easily test all prop combinations, including rare states     |
| Agent-friendly                 | Agents are great at editing React files; Storybook is just code |
| Design system consistency      | Same pure component used across apps                         |
| Designer collaboration         | Designers can review actual React components, not just mockups |
| PR review                      | Visual review of components in isolation                     |
| No full app state reproduction | Don't need to click through app to reproduce a bug           |
| Enables incremental migration  | Can add components one at a time                             |

---

## Examples and Demonstrations

### Button Component
- Simple pure component with props: font, border radius, etc.
- Change props in Storybook UI to see variations.

### Article Reading Page
- Vibe-code a page component, explore via props.
- Test different states: no image, with image, etc.
- Remove "no image" text when no image prop.

### Data Table
- Pure component for displaying tabular data.
- Wired component fetches data from API.
- Stories demonstrate sorting, loading, empty states.

### To-Do Card
- Every state modeled: priority, deleting, toggling, loading.
- Edit props to see behavior in various states.

### Mermaid Renderer
- Iterate on Mermaid diagrams without generating a full document.
- Pure render only; edit data directly in Storybook.

### Conversation Events / Coding Agent Output
- Many different output types: edits, diffs, grep results, etc.
- Each row is a separate stateless pure component.
- Storybook shows every possible output.

### Result Display for LLM Call
- Live migration: asked agent to build a data renderer for LLM call results as a Storybook component.
- Agent created component and stories.
- Demonstrated array rendering issues; agent iterated on pagination idea.
- Showed redaction of API keys in rendered output.

### HTTP Request Array
- Test rendering an array of HTTP requests before building full wiring.
- Decide if UI looks good before investing in implementation.

---

## Tips and Best Practices

### Prompting Agents
- Be specific: "Can you build one of the components, specifically the data renderer as an output for the result of an LLM call into a Storybook system."
- Ask agent to bootstrap Storybook first, then add components incrementally.
- Tell agent to split components into wired vs. pure.
- Ensure agent imports actual shared components, not re-implementing them in Storybook.
- Use plan mode for larger migrations; free-form for smaller tasks.
- Watch for version issues: agent may default to older Storybook version (e.g., Storybook 8); explicitly ask for latest (Storybook 10).

### Component Design
- Keep pure components stateless and props-driven.
- Wrapper components handle state, fetching, business logic.
- Use a shared UI package for pure components.
- Register custom renderers for different types (e.g., system prompt, user prompt, HTTP request).

### Testing and Iteration
- Use Storybook to reproduce bugs: capture the bad state as a story.
- Snapshot testing can be brittle; visual testing is often better.
- Storybook has accessibility plugins (contrast auditing, etc.).
- Can use agent browser for screenshots and automated visual convergence.

### Team Workflow
- Use Storybook for PR review of UI components.
- Designers can review actual components in browser.
- Move design out of Figma earlier; build components directly.
- Mono repo recommended for better agent results.

---

## Limitations and Considerations

### Storybook Limitations
- Not for stateful components that make API calls.
- Interactivity is limited; can simulate but not fully replicate app behavior.
- Snapshot testing only as good as the dataset you create.
- Requires discipline to keep stories organized and up-to-date.

### Agent Limitations
- Agents may hallucinate or use outdated package versions.
- May write component in application instead of shared package.
- Need to explicitly teach pure vs. wired concept; not baked into training set.
- Large codebases slow down agent runs.

### Automation Trade-offs
- More automation → faster system, but harder to debug when broken.
- Need long-term stability for automation to pay off.
- Add as much AI as your QA system can handle in terms of slowdown tolerance.

---

## Broader Implications for AI-Native Development

- New SDLC required for agentic coding: CI/CD, repos, workflows all need to change.
- Component preview tools (Storybook or custom) become essential.
- Front-end engineers' role shifts to wiring data layer; design is already in code.
- Enables more people to contribute to visual/design aspects.
- Iteration speed is undervalued; Storybook dramatically improves it.
- Teams willing to migrate to mono repo get much better agent results.
- Designers starting to use AI to code; some hate Figma now.

---

## Tools and Resources Mentioned

| Tool                      | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| Storybook                 | UI component development and isolation     |
| Figma                     | Design tool (less agent-friendly)          |
| Google Stitch             | Mockup tool                                |
| Stately AI                | Mentioned by chat                          |
| Crispy / RPI              | Agentic coding workflows                   |
| BAML                      | Programming language for LLMs              |
| Agent browser (Vercel)    | Screenshot and visual testing              |
| G Stack                   | Includes browser agent                     |
| Shadcn / Radix UI         | Accessibility-friendly component libraries |
| Playwright / Computer Use | Agent visual verification                  |
| promptfiddle.com          | BAML playground                            |
| Turbo Mono Repo           | Repository structure                       |

---

## Key Quotes

- "You can literally see every single possible thing that [the component] can do."
- "It's like unit testing for visual stuff."
- "You don't have to go spin up the whole web app and click around and create the state that reproduces the bug."
- "Storybook won't help if your designer is Claude." (joke)
- "If you're not willing to migrate to a mono repo, then we are not going to work with you."
- "I think iteration speed is undervalued."
- "Make sure it's actually importing your shared components and not just vibing out a bunch of in Storybook that doesn't actually impact your app."

---

## Summary of the Workflow

1. **Bootstrap Storybook** in the repo (agent installs and configures).
2. **Identify a pure component** or split a wired component into pure + wired.
3. **Add stories** for the pure component covering all prop combinations and edge cases.
4. **Iterate visually** in Storybook: edit props, see results, give feedback to agent.
5. **Reproduce bugs** by adding a story for the bad state, then fix.
6. **Review in PR** by running Storybook and inspecting components.
7. **Migrate incrementally** — one component at a time.

---

## Final Thoughts

- Storybook is a powerful tool for AI-native UI development because it aligns with agents' strengths (editing code) and enables fast visual iteration.
- The pure/wired component architecture is key to making components testable in isolation.
- While not without limitations, the benefits for agentic coding workflows are substantial.
- The broader trend is toward moving design into code earlier, using components as the source of truth, and enabling faster iteration cycles with AI.