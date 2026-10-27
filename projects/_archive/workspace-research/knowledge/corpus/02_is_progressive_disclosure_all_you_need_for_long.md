---
type: Concept
id: 02_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 3/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

agent splits coordinated across workers (Zhao et al.,
2024; Zhang et al., 2024b). All of these build their
navigation structureat run timeand treat it as tran-
sient, not a persistent artifact, and most evaluate
on long-document reading-comprehension bench-
marks such as QuALITY and NarrativeQA. The
closest neighbor that builds its structure offline is
Corpus2Skill (Sun et al., 2026), which distills an
enterprise corpus into a hierarchical skill directory
the agent navigates top-down. Its generalization
study is telling: navigation beats flat retrieval on
single-domain corpora with a recoverable taxon-
omy but not on open-domain factoid pools, exactly
the regime distinction that favors a single struc-
tured long document. We depart from this run-time
line on every axis: the skill pack is built once from
document structure and reused across queries, the
routing index is persistent and human-inspectable,
and the navigation interface is the file system, not
a bespoke tree API.
2.2 Agent skills
The agent-engineering community has converged
on a complementary pattern, surveyed and formal-
ized around progressive disclosure (Xu and Yan,
2026; Zhou et al., 2026): package a domain or
document as a directory rooted at a SKILL.md
routing file whose when-to-use rules the agent
consults before it reads any content (Anthropic,
2025b,a; Virgilio Jr., 2026; Karaaslan, 2026). Such
skills are hand-curated, induced from agent tra-
jectories (Wang et al., 2026), or, as here, derived
from a document’s own structure. Adopted at scale
on engineering intuition before anyone measured
it, the pattern is promoted as a near-replacement
for retrieval (Willison, 2025; Thoughtworks, 2026)
and, for book-length material, as a way to package
whole books and corpora as on-demand knowledge
bases (Virgilio Jr., 2026; Praison, 2026; PyShine,
2026; Bakal, 2026), with token-savings claims re-
ported under no accuracy control (Pocock, 2026).
Measurement has now begun, and two of its find-
ings bear directly on how we build a skill pack.
First, curated skills help but model-authored ones
do not: SKILLSBENCH(Li et al., 2026) reports
that curated packs lift performance while model-
authored packs add nothing, and Huang (2026)
trace the null to every section of an LLM-written
skill, which argues for fixing a skill’s structure from
the document rather than letting the model author
it wholesale. Second, the routing metadata carries
the weight: auditing 138 000public SKILL.md
files, Zhang et al. (2026) show that valid metadata
is what makes a skill reliably retrievable. Yet all of
this measures skill uplift against a no-skill baseline
on heterogeneous agentic tasks. None tests the pat-
tern against a raw-document baseline on a standard-
ized long-document benchmark, or isolates which
design axis (routing depth, chunk granularity, index
location) carries the effect. We close that gap.
3 Agentic long-context reasoning
Agentic long-context reasoning hands the whole
document to an agent and asks it to answer ques-
tions about it. A book does not fit in a context win-
dow, so the agent must first find the passage that
holds the answer, and practitioners wire that search
three ways without comparing them on equal foot-
ing. The first hands the agent the raw document and
lets it navigate on its own (raw). The second and
third package the document as an Agent Skills (An-
thropic, 2025b) pack and let progressive disclosure
route the agent to the passage, at one of two depths:
a single flat index (flat) or a recursive hierarchy
of per-chunk skills (hierarchical). We build
the two disclosure packs by implementingbook-
to-skill(Virgilio Jr., 2026), a widely adopted open
recipe for turning a long document into a skill pack,
and run all three approaches against the same book.
Both packs share a single chunk set (Section 3.1),
so the disclosure wiring is the only variable (Sec-
tion 3.3).
3.1 The book-to-skill pipeline
We run the following steps once per book, so the
chunk set and the descriptions are fixed inputs to
both disclosure approaches, not variables.
Chunking.We split the book along its own struc-
ture, cutting one chunk at each chapter heading and
following that division whenever the book provides
it. When a book exposes no such headings, we
fall back to fixed-size chunks of about 4000 words,
split at paragraph boundaries. Each chunk becomes
a file under references/, addressable by name.
Description.For each chunk we prompt an
LLM for a short description of what the chunk
covers, paired with the named entities it intro-
duces, and we prompt it once more over those
chunk descriptions for a book-level description
(Appendix A.2). These descriptions are the routing
metadata the agent reads before it opens any chunk,
the one place where Zhang et al. (2026) found meta-
data to be load-bearing for retrievability.
3
