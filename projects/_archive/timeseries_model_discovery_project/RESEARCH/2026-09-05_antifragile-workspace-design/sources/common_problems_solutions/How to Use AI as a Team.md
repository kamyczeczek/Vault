---
type: Concept
title: How to Use AI as a Team
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Below is a practical guide based on Tal Raviv’s April 2026 article **“How to use AI as a team.”** I’ve adapted the ideas into an implementation-oriented playbook rather than reproducing the article. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

# Guide: How to Use AI as a Team

## 1. The core problem: shared AI context

Most companies have solved **human-to-human file sharing**, but not **human + AI + team collaboration**.

A typical workflow today looks like this:

> Person A works with Claude → creates a document → copies it to Google Docs → Person B downloads/copies it → puts it into ChatGPT → edits it → creates another version.

This creates three problems:

- **Context fragmentation** — every AI starts with a different understanding of the company.
- **Duplicated work** — people repeatedly explain the same things to their AI.
- **No compounding** — improvements one person makes to their AI workflow aren't automatically available to colleagues.

The goal should instead be:

**Company knowledge → shared AI context → individual AI work → shared output → improved company knowledge**

That creates a feedback loop in which the team's AI capability compounds over time. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 2. What should AI know?

Think about AI context in four levels.

### Level 1 — Company-wide context

Information everyone should be able to use:

- Mission and vision
- Company strategy
- Annual/quarterly OKRs
- Market analysis
- Competitor information
- Key company metrics
- Organization structure
- Planning documents and transcripts

### Level 2 — Department context

For example, a Product/Design workspace could contain:

- Product development process
- Design system
- Roadmap
- Data schema
- Customer personas
- PRD templates
- Ownership information
- Research repositories

### Level 3 — Team context

Information useful to a specific team:

- Previous retrospectives
- Known problems and workarounds
- Dependencies
- Important stakeholders
- Internal processes
- Launch procedures
- Communication channels

### Level 4 — Personal context

Information that should remain private:

- Draft documents
- Personal working notes
- Stakeholder notes
- Feedback
- Personal research
- Your own AI experiments

The important distinction is:

**Not everything should be shared with everyone.**

The AI workspace should preserve the same access boundaries that already exist between humans. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 3. Create an “AI workspace” for every employee

A simple architecture is enough.

```text
Employee AI Workspace/
│
├── AGENTS.md
│
├── Company/
│   ├── Strategy/
│   ├── OKRs/
│   ├── Market/
│   └── Metrics/
│
├── Product/
│   ├── Roadmap/
│   ├── Personas/
│   ├── PRDs/
│   └── Research/
│
├── Team/
│   ├── Retrospectives/
│   ├── Processes/
│   └── Dependencies/
│
└── Personal/
    ├── Drafts/
    ├── Notes/
    └── Research/
```

The exact folder structure isn't particularly important. Organize it in a way that makes sense to humans.

The important property is that **AI can access the same context that the employee can access**. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 4. Use synchronization rather than copies

A particularly practical approach described by Raviv is to use an existing cloud-storage system such as Google Drive.

### Recommended setup

1. Create a company-wide shared folder for AI context.
2. Give the appropriate employees access.
3. Install the desktop sync client.
4. Each employee creates their own AI workspace.
5. Add shortcuts to the shared company/team folders.
6. Make relevant files available locally.
7. Open the workspace with a desktop AI agent.

The critical principle is:

**Don't distribute copies of the same knowledge.**

Use synchronized sources.

If the strategy document changes, everyone—and their AI—should eventually see the same version. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 5. Why local files matter

A desktop AI agent has a major advantage: **the filesystem becomes part of its working context.**

Instead of:

> “Here is this one document. Please analyze it.”

you can give the agent an entire workspace:

> “Here is the company's product context. Understand it and help me work.”

The AI can then traverse multiple files, compare documents, search previous decisions, inspect datasets, and generate new artifacts.

This also makes iteration faster.

For example:

```text
AI reads strategy
        ↓
AI analyzes customer research
        ↓
AI drafts PRD
        ↓
Human reviews PRD
        ↓
AI incorporates feedback
        ↓
Final PRD
```

The files themselves become part of the AI's persistent working context. Raviv argues that local agents are currently particularly effective for this because filesystem operations are faster and more flexible than repeatedly retrieving documents through remote integrations. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 6. Add an `AGENTS.md` or `CLAUDE.md`

Your workspace should also contain an instruction file.

For example:

```text
AI WORKSPACE
│
└── AGENTS.md
```

This file should contain **stable instructions**, not constantly changing project information.

Good things to put there:

- How the AI should behave
- Writing style
- Company's terminology
- Decision-making principles
- How to handle uncertainty
- When to ask questions
- How to structure deliverables
- What sources to prioritize
- What the AI should never assume

Bad things to put there:

- Today's project status
- Temporary deadlines
- One-off instructions
- Long documents
- Every piece of company knowledge

A useful rule is to keep the instruction file relatively short—Raviv suggests roughly **200 lines maximum**—because it is applied broadly to AI interactions. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 7. Treat the instruction file as a product

Don't write it once and forget it.

Use this loop:

```text
Use AI
  ↓
AI behaves incorrectly
  ↓
Identify why
  ↓
Improve instructions
  ↓
Use AI again
```

For example:

> “The AI keeps producing excessively long PRDs.”

Instead of repeatedly telling it:

> “Make this shorter.”

change the workspace instructions:

> “PRDs should normally be concise and decision-oriented. Prefer tables and bullets over explanatory prose.”

The next interaction should improve automatically.

This is one of the mechanisms by which **individual AI learning can become organizational AI learning**. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 8. Markdown vs. Google Docs

Use both, but for different purposes.

### Markdown/local files

Best for:

- AI-generated working documents
- Instructions
- Technical context
- Canonical knowledge
- Files AI needs to process frequently

Advantages:

- Fast for agents
- Easy to search
- Easy to modify programmatically
- Works naturally with desktop agents

### Google Docs

Best for:

- Human collaboration
- Comments
- Review
- Editing by non-technical colleagues
- Documents that require simultaneous human editing

A practical pattern is therefore:

**AI workspace → AI work → human collaboration → final shared document**

rather than forcing humans and AI to use exactly the same interface. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 9. The human + AI document workflow

Until the tooling becomes more seamless, use a simple handoff process.

### Step 1 — Work with AI locally

Use your desktop agent to:

- Research
- Analyze
- Draft
- Rewrite
- Compare
- Structure
- Iterate

### Step 2 — Make it human-readable

Once the document reaches a reasonable state, move it into the team's normal collaboration environment.

For example:

```text
Claude / Cursor
       ↓
Draft
       ↓
Review with AI
       ↓
Google Docs / Notion / Confluence
       ↓
Human comments
       ↓
Final document
```

### Step 3 — Bring the document back into AI

The AI should be able to read the shared version again.

This creates a loop rather than a one-way export.

------

# 10. Don't over-engineer the infrastructure

One of the strongest points in the original article is that this problem currently doesn't have an elegant universal solution.

You might be tempted to immediately build:

- Custom RAG infrastructure
- Vector databases
- Complex MCP servers
- A new internal knowledge platform
- A proprietary AI memory system

That may be unnecessary.

If your company already uses Google Drive, Microsoft 365, Dropbox, Notion, or another established system, start there.

The infrastructure should be **boring**.

Your employees already have enough new things to learn with AI.

The goal is not:

> “Let's build an amazing AI infrastructure.”

It is:

> **“Let's make the company's existing knowledge available to everyone's AI.”**

Raviv makes a similar argument against prematurely replacing established cloud-file systems with specialized products. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 11. What about MCP?

MCP can eventually provide a cleaner architecture:

```text
AI agent
   ↓
MCP
   ↓
Google Drive / Notion / Confluence / other systems
```

The advantage is obvious: the AI doesn't need a local copy of everything.

But there is a tradeoff.

Every interaction may require:

```text
AI → remote service
   ↓
search
   ↓
retrieve
   ↓
process
   ↓
return
```

For tasks involving thousands of files or many sequential operations, that can introduce latency and limitations.

So the practical distinction is:

| Approach             | Strength                                  |
| -------------------- | ----------------------------------------- |
| Local filesystem     | Fast, flexible, autonomous                |
| MCP/cloud connectors | Convenient, centralized                   |
| RAG                  | Good for large knowledge retrieval        |
| Git                  | Excellent for technical/high-process work |
| Google Docs/Notion   | Excellent for human collaboration         |

The right answer may eventually be a hybrid architecture.

------

# 12. When Git makes sense

Git is powerful, but it introduces concepts that aren't natural for ordinary knowledge work:

- commits
- branches
- pull requests
- merge conflicts
- version control workflows

It makes sense when:

- Changes are high-stakes
- Technical teams are involved
- Auditability matters
- Documents are closely coupled to code
- The team already understands Git

For a normal business team, a synchronized cloud folder may produce much less friction. Raviv's respondents who preferred Git tended to be small or technically oriented teams. ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

------

# 13. Governance and permissions

This is where the setup needs more discipline.

Think of AI access exactly like employee access.

### Company information

Everyone can read.

### Department information

Only relevant departments.

### Team information

Only team members.

### Personal information

Only the individual.

For example:

```text
Company AI Context
       │
       ├── Product
       │     ├── Product Team A
       │     └── Product Team B
       │
       ├── Marketing
       │
       └── Finance

Personal AI Workspace
       │
       ├── Company → shared
       ├── Product → shared
       └── Personal → private
```

Do not solve AI context sharing by giving everyone access to everything.

**AI should inherit the user's information boundaries.**

------

# 14. A practical company rollout

You don't need to roll this out to 500 employees immediately.

Start with one team.

### Week 1 — Establish the workspace

Create:

```text
AI Context/
├── Company/
├── Department/
└── Team/
```

Add existing documents.

### Week 2 — Establish AI instructions

Create:

```text
AGENTS.md
```

Define:

- terminology
- style
- behavior
- sources
- standards

### Week 3 — Run real work through it

Have the team use AI for actual tasks:

- PRDs
- analysis
- research
- meeting summaries
- planning
- customer research
- competitive analysis

### Week 4 — Capture improvements

Ask:

- What information was missing?
- What did AI misunderstand?
- What instructions were missing?
- Which documents should be canonical?
- What should be shared with the rest of the organization?

Then update the workspace.

------

# 15. The operating model

The mature version looks like this:

```text
                 COMPANY KNOWLEDGE
                        │
                        ▼
              Shared AI Context
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Person A       Person B      Person C
          │             │             │
          ▼             ▼             ▼
         AI             AI            AI
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                 Shared artifacts
                        │
                        ▼
                  Human review
                        │
                        ▼
              Improved knowledge
                        │
                        └──────→ AI Context
```

That last arrow is the important one.

The organization shouldn't merely **use AI**.

It should continuously **improve the context in which its AI operates**.

------

# 16. The key principles

If you reduce the entire approach to ten rules:

1. **Give AI the same context people need to do their jobs.**
2. **Centralize shared knowledge rather than distributing copies.**
3. **Keep private, team, department, and company context separate.**
4. **Prefer existing approved infrastructure over new AI infrastructure.**
5. **Use local files when speed and autonomy matter.**
6. **Use collaborative web documents when humans need to edit together.**
7. **Maintain a short, explicit AI instruction file.**
8. **Continuously improve that instruction file based on failures.**
9. **Don't force every employee onto Git/MCP/RAG just because they're technically interesting.**
10. **Design for compounding knowledge: one person's AI improvement should eventually help everyone.**

The underlying thesis is simple: **the competitive advantage isn't merely having access to the same frontier models. It's giving those models better organizational context and creating a system in which that context gets better over time.** ([Tal Raviv](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com))

**Source:** [Tal Raviv — “How to use AI as a team”](https://www.talraviv.co/p/how-to-use-ai-as-a-team?utm_source=chatgpt.com)