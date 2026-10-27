---
type: Concept
id: 12_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 13/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

the score, so the reward depends only on the agent’s
answer file, not on a second model’s reading of it.
Constructing a library-scale task.A multi-
book task reuses the single-book instruction,
prepends one framing block, and relabels the file
system (Figure 6). The framing block states that the
corpus holds K labeled books, that different ques-
tions concern different books, and that the agent
must identify which book a question asks about
before answering; a corpus-index.md gives a
one-line summary of each member book. Every
question and answer identifier gains the book label
as a prefix, so the verifier keys each gold answer
on the full prefixed identifier and the deterministic
scoring of the single-book case carries over un-
changed.
A.2 Description-generation prompts
The book-to-skill pipeline (Section 3.1) generates
all routing metadata with the two prompts in Fig-
ure 7. The per-chunk prompt runs once per chunk;
the book-level prompt runs once per book over the
resulting chunk descriptions. Both descriptions
are fixed inputs to the two disclosure approaches,
so the same text routes the agent in flat and
hierarchical alike. The choices below fix the
metadata but do not bear on the disclosure question
the paper studies; we record them for reproducibil-
ity.
Two-part per-chunk output.The per-chunk
prompt asks for a one- or two-sentence summary
and a comma-separated list of key elements, the
named characters, locations, organizations, and
topics the chunk introduces. We parse the two
fields from the SUMMARY: and KEY_ELEMENTS:
markers; when a response carries neither marker,
we keep the whole response as the summary and
leave the key-element list empty. The two fields
become adjacent columns of the flat table of
contents and, concatenated, the description
of each hierarchical chapter skill. The key-
element list gives the router exact surface forms,
such as proper names and place names, that a one-
sentence summary tends to paraphrase away.
Book-level summary.The book-level prompt
reads only the chapter summaries, never the book
text, and writes the one- or two-sentence de-
scription that gates discovery. It works from
anonymized names and must not name or infer the
book’s title or author, so a title the agent happens
to recognize cannot shortcut retrieval and inflate a
score.
Determinism.Every call runs at temperature
0 with a fixed seed, so rerunning the pipeline on
the same book reproduces the same metadata. A
per-book manifest records the model, seed, and a
hash of each prompt, letting a later run reuse an
existing skill pack rather than regenerate it.
A.3 Hybrid RAG for agents
Hybrid RAG is our conventional retrieval-indexing
baseline for long-document agent evaluation. We
describe here how it builds the book index, fuses
sparse and dense retrieval, and feeds the retrieved
evidence to the answer model (Figure 8), separat-
ing what it computes while indexing from what it
computes at query time.
Index construction.We split a book into pas-
sages, give each a stable chunk identifier, and build
two retrieval views over the chunk set. A BM25
index forms the sparse view, preserving exact lexi-
cal matches for names, quoted phrases, and local
events; the BGE-M3 embedding model encodes
each chunk into the dense view. We store each in-
dex under a content hash of the source book with a
manifest recording the embedding model, reranker
model, and build metadata, so repeated trials over
the same book load the existing index instead of
rebuilding it.
Hybrid retrieval.At query time, the two re-
trievers run in parallel over the chunk set: BM25
scores rank chunks for the sparse retriever, and em-
bedding similarity to the question ranks them for
the dense retriever. Reciprocal rank fusion (RRF)
merges the two ranked lists, a BGE cross-encoder
reranks the fused candidates, and the top chunks
enter the answer prompt as evidence. We fix the
candidate-retrieval and reranking budgets across
runs.
Agent interface.The agent never sees the full
book. For each question it receives a prompt car-
rying the retrieved evidence chunks and the bench-
mark question, and we instruct it to output exactly
one option letter for multiple choice and only the
final answer text for free-form QA, including Chi-
nese QA. We save the retrieved and reranked chunk
identifiers for every query, so we can inspect the
evidence the agent used without relying on hidden
model state.
Reuse and accounting.Book content, not the
answer model, keys the retrieval index, so the same
index serves repeated trials and different answer
12
