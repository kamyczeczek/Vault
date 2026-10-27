---
type: Concept
id: 17_interpretable_context_methodology_folder_structu
title: "Interpretable Context Methodology: Folder Structure as Agent (part 18/21)"
source: "Interpretable Context Methodology Folder Structure as Agent.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, interpretable-context]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

18•Jake Van Clief, David McDermott
For ICM, the tension is real. Creative content is fuzzier than compiled code. Sometimes the output needs a
human touch that cannot be reduced to a source-level rule. A script might benefit from a turn of phrase that no
amount of voice guide refinement would have produced. Editing the output in that case is the right move. The
practitioner is adding value that the system cannot generate on its own.
But there is a class of output edits that are diagnostic. If the practitioner consistently tightens the opening
paragraph, that is a signal that the stage contract should say “keep the opening under three sentences. ” If the
tone drifts formal every time, that is a signal that the voice guide needs a stronger example of the target register.
These recurring edits are debugging information. They point to fixable source-level problems.
A future version of ICM could support this by tracking output edits across runs. If a practitioner edits the same
kind of thing in the same stage’s output three runs in a row, the system could surface that pattern and suggest a
source-level change: a contract amendment, a reference file update, a new constraint. This would close the loop
between output editing and source improvement, turning one-off fixes into durable system improvements.
The principle matters because it addresses a question about ICM’s long-term trajectory. If workspaces are only
as good as the last human edit of their output, they remain tools. If workspaces improve their own source files
over time, incorporating the patterns they learn from human corrections, they become systems that get better
with use. The debugging and traceability infrastructure described in the previous subsection is a prerequisite for
this: you cannot improve the source if you cannot trace the problem back to it.
7 Conclusion
The principles that made Unix pipelines effective in the 1970s apply to AI agent orchestration in the 2020s.
Programs that do one thing. Output of one becomes input of another. Plain text as universal interface. Human-
readable intermediate state.
ICM applies these principles to a specific problem: structuring context for AI agents across multi-step workflows.
The result is a system where the folder structure replaces the framework. One agent reads different context at
each stage rather than multiple agents coordinating through code. Local scripts handle the mechanical work that
does not need AI. Every intermediate output is a file a human can read and edit.
For practitioners whose AI workflows are sequential, reviewable, and repeatable, this means full pipeline
capability with no framework to learn, no server to maintain, and no developer needed for day-to-day operation.
The workspace is a folder. It can be copied, versioned, shared, and edited with a text editor. The simplest viable
architecture for this class of problem is one that already exists on every computer: the filesystem.
The protocol is open source under the MIT license and includes a workspace-builder for creating new
workspaces across any domain.
References
[1] M. D. McIlroy, E. N. Pinson, and B. A. Tague, “Unix Time-Sharing System: Foreword, ”The Bell System Technical Journal, vol. 57, no. 6,
part 2, pp. 1902–1903, 1978.
[2] D. M. Ritchie and K. Thompson, “The UNIX Time-Sharing System, ”Communications of the ACM, vol. 17, no. 7, pp. 365–375, 1974.
DOI: https://doi.org/10.1145/361011.361061
[3] P. H. Salus,A Quarter Century of Unix. Addison-Wesley, 1994. ISBN: 0-201-54777-5.
[4] E. S. Raymond,The Art of Unix Programming. Addison-Wesley Professional, 2003. ISBN: 0-13-142901-9.
Available: http://www.catb.org/esr/writings/taoup/html/
[5] B. W. Kernighan and R. Pike,The UNIX Programming Environment. Prentice Hall, 1984. ISBN: 0-13-937681-X.
[6] M. Shaw and D. Garlan,Software Architecture: Perspectives on an Emerging Discipline. Prentice Hall, 1996. ISBN: 0-13-182957-2.
[7] S. I. Feldman, “Make — A Program for Maintaining Computer Programs, ”Software: Practice and Experience, vol. 9, no. 4, pp. 255–265,
1979.
DOI: https://doi.org/10.1002/spe.4380090402
[8] E. W. Dijkstra, “On the Role of Scientific Thought, ” Manuscript EWD447, 1974. Reprinted inSelected Writings on Computing: A Personal
Perspective, pp. 60–66. Springer-Verlag, 1982.
