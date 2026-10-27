---
type: Concept
title: ICM_knowledge_big
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# ICM_knowledge.md

Merged notes — part 1 of the collection.



------



Jake's content\Building Your Stack\1.1 Starting the Build Process.md



What You'll Get From This



A framework for deciding whether to build a custom UI and how to scope it before writing any code.



------



Before You Build Anything: The Tool Ladder



This methodology works at different levels. You don't always need to build custom.



Level 1: Claude Projects (



http://claude.ai/



Use project instructions and knowledge files. Upload your



http://claude.md/



, your context docs, your templates. Claude reads them at the start of every conversation. No code required.



Level 2: Claude Cowork (in-app)



More control, still inside Anthropic's interface. Good for workflows that need more than chat but don't require full file system access.



Level 3: VS Code + Claude Code



Full readability. Quick navigation. You see your folders, your files, your code. Claude operates inside your actual workspace. This is where most people should land.



Level 4: Custom Front-End



Build your own interface around Claude Code. Full control. Designed specifically for your workflow.

#### Each level adds complexity. Each level adds capability. But here's the thing:

Anthropic keeps improving their native UI.



Features that required custom builds a year ago now exist in the default interface. Projects didn't exist. Cowork didn't exist. By the time you finish building a custom front-end, Anthropic might ship something that does the same thing.

#### The philosophy for this course:

know HOW to build custom, so you can when you need to. But always ask whether you need to. The best tool is the simplest one that solves your problem.



------



What This Course Is



This isn't a step-by-step tutorial. This is a behind-the-scenes project.



I'm building a custom front-end for my animation workflow. You're watching me do it. Every decision, every mistake, every time Claude does something unexpected.



The lessons in this course are session recordings with written companions that explain what's happening and why. You'll see:



How I research what already exists before building



How I write a PRD (product requirements document) so Claude knows what we're making



How I set up the workspace so Claude has context



How Claude Code uses plan mode and sub-agents



What happens when things break



How the project evolves session by session



This is the highest-skill content in the community. If some of it feels over your head, that's fine. Watch it anyway. You'll understand more than you think, and the parts that don't click now will click later.



------



The Project: A Control Surface for My Workflow



Here's what I'm building and why.



I have a workflow for turning scripts into animations. It lives in folders. Script Lab holds my scripts. Animation Studio turns them into specs, then builds, then renders. The whole thing runs on Claude Code.

#### VS Code works fine for this. But I want something better. I want:

A visual workflow map instead of just folders



A file editor in the middle



Claude Code chat on the right



The ability to switch between "I'm driving" and "Claude's driving"



That last one is the key insight. Sometimes I want to edit every individual file. Sometimes I want to automate the whole thing and trust Claude to run the pipeline. A good control surface lets me switch between those modes fluidly.



------



Why Not Just Use Existing Repos?



There are open-source projects that do parts of this. Claude CLI interfaces. Claude Code web UIs. Tools for session persistence and usage tracking.



I looked at them. They're good, but they're not MY workflow. They have features I don't need. They're missing features I want. They don't map to how I actually work.

#### So instead of using them directly, I'm doing this:

Study what they built



Pull the parts that work



Strip away everything I don't need



Build around my existing folder structure



Don't reinvent the wheel. Make a better wheel. Make the wheel yours.



------



The PRD Approach



Before any code gets written, I have Claude create a PRD.



PRD = Product Requirements Document

#### The PRD describes:

What we're building



What existing repos we're pulling from



What stacks those repos use



What I want to keep and what I want to cut



The phases from start to finish



This becomes a markdown file that lives in the workspace. Claude Code reads it at the start of every session. It's persistent context. Stateful prompting.



Why markdown? Because markdown files are small (low token cost), easy for Claude to read, and I can edit them in any text editor. If I want to format them later, I can upload to Google Docs and it converts automatically.



------

#### What the Lessons Cover

1.2: How I Use Claude Code in the Build Process



The initial thinking. David's question that started this. Researching existing repos. Creating the PRD. Setting up the workspace inside my actual project folder so Claude has context.



1.3: Building the Front End (Session 1)



Watching Claude work. Plan mode vs execution mode. Sub-agents that fetch repos and study workspace structure. What happens when Claude makes better decisions than what I told it to do.



1.4: [Coming Soon]



More build sessions as the project continues. This is an ongoing build. New lessons drop as I finish sections.



------



The Build Process Framework



Whether you follow along with my project or build something completely different, the process is the same:



1. Define what you actually     need



Not what sounds cool. What workflow pain are you solving? Can you solve it at Level 1, 2, or 3 instead of Level 4?



1. Research what exists



What repos already do part of this? What can you borrow? What's worth building vs. taking?



1. Map your existing     structure



What folder architecture are you building around? Give Claude your



http://claude.md/



. Let the front-end wrap around what you already have.



1. Write a PRD



Have Claude create a product requirements document. Phases. Stacks. What to cut. What to keep. Edit it before any code exists.



1. Build inside your     workspace



Don't create a separate folder. Build where your context already lives. Claude can reference your actual workflow while building the tool for it.



1. Work in sessions



Claude runs out of tokens. You run out of energy. Break the build into sessions. Each session picks up where the last one left off because the PRD and workspace context persist.



------



Who This Is For

#### This course is for people who:

Have completed the Foundation course (or equivalent)



Are comfortable with Claude Code



Want to see how a real build happens, not just the polished result



Are considering building their own tools around Claude



If you haven't set up Claude Code yet, go to [Foundation 4.1: Install and First Use] first.



If you're not sure whether you need a custom front-end, you probably don't. Stay at Level 3 until you hit a wall that VS Code can't solve.



------



PRD Prompt Template



I want to build [describe what you're building].



Here's my current folder structure and workflow: [paste CLAUDE.md or describe]



Here are repos that do something similar: [paste links]



Make a PRD markdown for Claude Code to read and build from. Include:



\-    What we're building and why

\-    Target user (me, for now)

\-    Existing repos we're pulling from and what we're taking

\-    Tech stack recommendations

\-    What features to cut (keep it minimal)

\-    Phases from MVP to full version



Break it into early phase (get something working) and late phase (polish and features).



------

#### Should you even build this? Review the Ladder:

2.4 The Ladder That Explains Every AI Failure



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Need Claude Code set up first?



4.1 Install and First Use



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



How does the folder architecture inform this?



3.1 The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Ready for the full build templates?



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



The first build session. You'll see the PRD get created, the workspace get set up, and the research phase that happens before any code exists.



------



Jake's content\Building Your Stack\1.2 How I Use Claude Code in the Build Process.md



What You'll Get From This



The research and planning phase of a custom build: finding existing repos, creating a PRD, and setting up your workspace so Claude has context from the start.



------



Where This Started



David had been making animations with Claude Code. He watched my tutorials, set up his own workflow, and started building really great stuff.



Then he asked a question: what if I built a front-end UI that lets me control and monitor Claude?



It's a natural next step. Once you're comfortable with Claude Code in VS Code, you start wanting something designed around YOUR specific workflow. Something you can observe. Something with a better interface for what you're actually doing.



The problem is how to build it without burning through API credits.



------



The API Cost Problem



When you use Claude Code through your subscription, it doesn't cost extra per message. You're using what you already pay for.



But as soon as you build a custom front-end, the obvious approach is to make Anthropic API calls directly. And API calls add up fast. A heavy build session could cost more than a month of subscription.



The solution: build a front-end that controls Claude Code, not one that replaces it. You're making a better interface for the tool you already have, not a separate app that needs its own API connection.



This is the key insight that shapes everything else.



------



Research Before Building



Before writing any code, I had Claude research what already exists.

#### There are repos out there that do versions of this:

Front-ends that wrap Claude Code



Usage tracking dashboards



Mobile interfaces for remote control



Session persistence tools



I looked at them. Some had good ideas. Some had features I'd never use. None of them matched my workflow exactly.

#### But that's fine. I'm not looking for a perfect solution. I'm looking for:

What problems have other people already solved?



What code can I borrow?



What patterns work?



Don't reinvent the wheel. Study the wheels that exist. Take what's useful. Leave what isn't.



------



What I Didn't Like About Existing Repos



The existing front-ends weren't bad. They just weren't mine.



They had features I'd never use. Provider switching. Complex settings panels. UI elements designed for someone else's workflow.



I'd rather work in VS Code with raw folders than use an interface that doesn't fit how I think. But I also knew I could build something better FOR ME by pulling the good parts from these repos and wrapping them around my existing folder structure.



That's the goal: not a generic Claude interface, but a control surface for MY animation pipeline.



------



The PRD Document



Instead of jumping into code, I had Claude create a PRD first.



PRD = Product Requirements Document

#### Here's what went into it:

The repos I'm pulling from



\-    Links to the existing projects. What stacks they use. What I liked about each one.

#### What to cut

\-    Most of the front-end complexity from those repos. I don't need all their features. I need a clean, minimal interface.

#### What I actually want:

A workflow map on the left (visual, like a mind map, not just folders)



A file editor in the middle



Claude Code chat on the right



Ability to open multiple chats



Ability to collapse panels



Clean, minimal design



\-    What to build first (get something working) vs. what to add later (polish and features).

\-    Clone the repos, strip away what I don't need, implement the front-end basics, then add the workflow visualization.



All of this goes into a markdown file. That file lives in the workspace. Claude reads it at the start of every session.



------



Why a PRD Matters



If I just told Claude "build me a front-end for my workflow," it would build something. It probably wouldn't be right.

#### The PRD does three things:

1. Forces decisions before     code



What features do I actually want? What's out of scope? Easier to edit a document than refactor built code.



1. Creates persistent     context



Claude Code reads the PRD every time I start a session. It knows where we are in the project. It knows what we're building. I don't have to re-explain.



1. Allows auditing



If you're not sure about the technical choices, you can feed the PRD into another Claude session and ask it to review. "What's overcomplicated? What's missing? What would you simplify?"



------



The PRD Prompt

#### Here's roughly what I asked:

Make a PRD markdown of this for Claude Code (as in, Claude Code will read it to build the project).



Describe what we are trying to do and break down steps and structure for early phase to late phase.

#### I included:

The repos I wanted to reference



My existing folder structure (my



http://claude.md/



What I wanted the front-end to do



What I wanted to cut from the existing repos



Claude generated a document. I read through it, edited the parts that weren't right, and saved it to my workspace.



------



Building Inside the Workspace



Here's a detail that matters: I'm building this front-end inside my Animation Studio workspace, not in a separate folder.



Why? Because that workspace already has all my context. The folder structure. The processes. The



http://claude.md/



that describes how everything works.



If I built in a separate folder, Claude would have to fetch context from somewhere else. By building inside the workspace, Claude can reference my actual workflow while building the tool that wraps around it.



I created a new folder called "front-end" inside my existing workspace. The PRD goes there. The code will go there. But Claude can still see the animation pipeline it's building an interface for.



------



What Comes Next



Once the PRD is set, the actual build starts. That's



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=fdb1ae130aec49d28eba9142efb5762f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### You'll see:

Claude reading the PRD and confirming it understands



Plan mode vs. execution mode



Sub-agents fetching repos and studying workspace structure



Claude making decisions that are sometimes better than what I told it to do



The reality of a long-running build session



This lesson was about research and planning. The next one is about watching Claude work.



------



PRD Template



I want to build [describe what you're building].



Here's my current folder structure and workflow: [paste CLAUDE.md or describe]



Here are repos that do something similar: [paste links]



Make a PRD markdown for Claude Code to read and build from. Include:



\-    What we're building and why

\-    Target user (me, for now)

\-    Existing repos we're pulling from and what we're taking

\-    What stacks those repos use

\-    What features to cut

\-    Phases from MVP to full version

\-    Steps to execute in order



This PRD should be readable by Claude Code so it always knows where we are in the project.



------



Haven't set up Claude Code?



4.1 Install and First Use



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### The folder architecture this wraps around:

3.1 The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Want the full PRD and workspace files?



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



The research is done. The PRD is set. Now we watch Claude work. Plan mode, sub-agents, web fetches, and what happens when Claude makes better decisions than what I asked for.



🧠 Front-End UI for Controlling Claude Code – Mind Map



🎯 The Origin



David's Question



Wanted to control Claude via a front-end UI



Currently using



(recommended setup)



Desired better



monitoring/observability



💰 Cost Considerations



Subscription vs API



Anthropic Subscription



→ Lower cost



→ Expensive for heavy usage



Front-End Challenge



Easier to use API calls in a custom UI



Controlling Claude Code directly from a front-end feels "clunky"



🔍 Research & Discovery



Open-Source Solutions



Repo 1: Downloadable front-end to control Claude



control of Claude



Remote Control



Already installed & using Claude via



Video tutorial planned



💡 The Creator's Vision



Custom Front-End Project



Navigate folders visually



Mind Map / Web Map



view (not just simple folder tree)



Potential to generate a



web service



"Don't reinvent the wheel"



Leverage existing open-source repos



Build on personal animation workflow structure



📁 Personal Animation Workflow



Existing Structure



Scripts → Animations pipeline



Complex folder/file system



Course coming to break it all down



Working Backwards



Gave Claude the markdown file of the folder structure



"What if we built a front-end around this exact system?"



Claude generated architecture ideas



📄 The PRD Approach



What is a PRD?



Product Requirements Document



Used in software development



Integrations



Goals & targeting



Avoid building everything at once



Break work into



(Early → Late)



editable, readable document



🔄 Workflow Strategy



Claude generates the PRD markdown



Creator reviews & edits (leveraging software background)

#### Step 3 (Optional):

Feed PRD into another Claude instance as an



Drop PRD into workspace

#### Open Claude Code and say:

"Read the PRD for the front end"



Claude builds the front-end



inside the workspace



🎬 Upcoming Content



Quick update video



(this content)



Full course



on both topics coming soon



🔑 Key Principles



existing tools



, don't start from scratch



before building



Phase-based



development



Claude can act as both



Desktop app for heavy lifting; PRD for structured planning



------



Jake's content\Building Your Stack\1.3 Designing for Your Use Case.md



What You'll Get From This



A look inside a real build session: how Claude Code works through a PRD, uses plan mode and sub-agents, and sometimes makes better decisions than what you asked for.



------



What You're Watching



This is less of a lecture and more of a live stream. You're watching me work.



The PRD is done. The workspace is set up. Now I'm letting Claude Code run through the build while I observe, intervene when needed, and explain what's happening.



If parts of this feel fast or technical, that's fine. The goal isn't to follow along step by step. The goal is to see how a real build actually happens.



------



I'm working inside my Animation Studio workspace. The front-end folder is created. The PRD is dropped in.

#### The PRD describes:

What I'm building (a control surface for my workflow)



The repos I'm pulling from



What to cut from those repos



The panel layout I want (workflow map, file editor, Claude chat)



The phases and steps



Claude Code can read all of this. It knows where we are. It knows what we're building.



------



Starting the Build



I tell Claude to read the PRD and confirm it understands.



Hey, read this PRD and make sure you're up to speed on everything.



Claude summarizes back what it understood. I clarify the parts that matter most:



I want to clean and edit stuff easily



I want control over files and routing



I want to automate things and swap files around



The abstract goal isn't a prettier Claude front-end. It's a control surface where I can fluidly switch between "I'm driving" and "Claude's driving."



That last part is the key. Sometimes I want to edit every individual file manually. Sometimes I want to automate the whole pipeline and trust Claude to run it. The interface should let me switch between those modes without friction.



------



Plan Mode vs Execution Mode



When I say "let's go ahead and start," Claude enters plan mode.



is where Claude thinks through what it's going to do before doing it. It creates a plan, breaks it into steps, and waits for confirmation.



Execution mode



is where Claude actually runs commands, writes code, fetches files.



You can affect which mode Claude uses, but usually it chooses on its own. For a complex build like this, it starts in plan mode. Good. I want to see the plan before anything gets built.



------



If you're using Claude 4.6 (the default), something interesting happens: Claude creates sub-agents.



Instead of doing everything in one thread, Claude sends smaller agents to handle specific tasks:



"Let me send an agent to study the workspace structure"



"Let me send an agent to fetch this repo"



"Let me send an agent to implement this component"



This saves tokens. The main Claude orchestrates while sub-agents do the fetching and studying. You'll see messages like "Task: agent" as these sub-agents spin up.



It looks like Claude is doing multiple things at once. It kind of is.



------



Watching Claude Work



Once the plan is set and I approve, Claude starts executing.

#### Bash commands

\-    Claude runs terminal commands to search the workspace, find files, check structure. When you see "bash" in the output, Claude is running a command just like you would in a terminal.

#### Web fetches

\-    Claude pulls files directly from GitHub repos. Instead of cloning the entire repo (which I told it to do), Claude searches through the repo and fetches only what it needs.



This is Claude making a better decision than what I asked for. I said "clone the repo." Claude realized it's more efficient to fetch specific files. That's fine. That's good. Let it be smarter than your instructions when it makes sense.

#### Reading and understanding

\-    Claude reads the package.json files from the repos to understand how they're structured. It reads the source files to understand the patterns. It's doing research while building.



------



Why Workspace Context Matters



Here's why I built inside my Animation Studio folder instead of a separate location:



Claude can reference my actual workflow while building the tool for it.



When Claude does a bash find command looking for folder structure, it finds my real folders. Script Lab. Animation Studio. The specs. The renders. All of it.



If I built in a separate folder, Claude would have to fetch that context from somewhere else. By building in place, the context is already there. Claude can see what it's wrapping an interface around.



------



Stateful Prompting



Normal Claude conversations are stateless. When you start a new conversation, everything from the previous one is gone.



But the PRD is a file. It persists. Every time I start a new Claude Code session in this workspace, I can say "read the PRD" and Claude is back up to speed.

#### This is why markdown files matter:

They're small (low token cost)



Claude reads them well



They're easy to edit



They persist between sessions



The PRD turns a stateless tool into something with memory. The memory lives in the file system, not in Claude's context window.



------



When Claude Runs Out of Tokens



Long builds hit token limits. Claude gets slower. Responses get shorter. Eventually it stops being useful.



When this happens, I start a new session. The PRD is still there. The code that's been written is still there. I tell Claude to read the PRD, look at what's been built, and continue from where we left off.



This is working in sessions. Each session picks up where the last one stopped. The workspace is the continuity.



------



What Got Built This Session

#### By the end of this session:

Both repos analyzed (Claude Code Web and the CLI UI)



Key patterns identified



Initial structure started



Foundation laid for the panel layout



The workflow visualization (the hardest part) comes later. That's probably a separate session. Maybe multiple.



------



The Reality of Building



This isn't clean. Claude makes decisions I didn't expect. Some are better than what I asked for. Some need correction.



The PRD keeps us aligned. When Claude drifts, I point back to the document. "Hey, that's not what we said we wanted." Claude adjusts.



You're not going to get a perfect build in one session. You're going to get progress. The workspace accumulates that progress. The next session builds on it.



------



Commands You'll See



What Claude Says What It Means "Entering plan mode" Claude is thinking through steps before acting "Task: agent" A sub-agent is being spawned for a specific task "bash: find..." Claude is running a terminal search command "web_fetch" Claude is pulling a file from the internet "read_file" Claude is reading a file from your workspace



Session Management

#### When you hit token limits:

Note where you stopped



Start a new Claude Code session



Tell Claude to read the PRD



Tell Claude to look at what's been built



Continue from where you left off



The workspace persists. Claude's memory doesn't. Use the workspace as memory.



------

#### Folder architecture that makes this possible:

3.1 The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Want the actual PRD and workspace files?



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



A curated list of open-source AI UI projects worth studying, with notes on what to learn from each.



🧠 Building a Custom Front-End for Claude Code Animation Workflow – Mind Map



🎯 Project Goal



Custom front-end



for managing animation workspace



Not calling Claude API (avoid fees)



Navigate and organize project folders visually



Maintain existing workflow



Scripts → Animation Studio → Specs → Renders



Keep it clean, modular, personal



Improve on existing tools



(Claude CLI, Claude Code Web, Opcode)



Too complex / not fitting personal workflow



Extract good ideas, discard clutter



📋 The PRD (Product Requirements Document)



Single source of truth for Claude Code



Describe full vision, constraints, references



Break work into phases, avoid building everything at once



Reference to GitHub repos (stacks, liked features, unwanted features)



Visual layout specs (workflow map, editor, chat panel)



Pipeline definitions (JavaScript mapping actual folder structure)

#### Step-by-step instructions:

Clone and analyze repos



Strip unwanted features



Add session persistence (like VS Code extension)



Implement front-end



Implement visual workflow (hardest)



Why PRD first?



Editable markdown, easy for Claude to read



Avoids Claude rushing into code



Acts as persistent, non‑stateless prompt (can be reused across sessions)



🖥️ Desired UI & Features



Three-panel layout



Workflow Map



(node-based, mind‑map style)



File Editor



Claude Chat Panel



(multiple collapsible chats)



Workflow Map



Visual representation of folder structure and animation pipeline



Click nodes to navigate, edit, or trigger actions



Moves from Script Lab → Animation Studio → Specs → Renders



Interaction model



“Fluid switch between me driving or Claude driving”



Sometimes manual edit, sometimes full automation



Trust that automation follows the defined workflow



🔧 Technical Strategy



Don’t reinvent the wheel



Clone existing open‑source repos (Claude Code Web, Opcode)



Strip down to essentials, keep the “good parts”



Reuse session persistence, chat infrastructure



JavaScript (pipeline definitions), potentially React



All built within the existing workspace context



Leverage Claude’s own infrastructure (no separate app)



Implementation phases



(from PRD):



Download & analyze reference repos (web fetches, not full clones)



Remove unwanted UI elements, keep backend connections



Integrate workflow map (hardest part)



Final polish and modularity



⚙️ Current Execution (Live Session)



Using Claude Code in plan mode



Claude reads the PRD markdown, confirms understanding



Creates sub‑agents to save tokens (inspect workspace, fetch data)



Actions observed



commands to examine folder structure



Web fetches pulling specific files from reference repos (package.json, etc.)



Sending secondary agents for parallel tasks



Workspace is key



All work done inside the actual project folder



Gives Claude direct context without uploading files repeatedly



Context only pulled when instructed (not everything at once)



📚 Core Concepts Explained



Stateless vs Persistent Prompts



Normal chat: stateless, context lost after session



Markdown PRD: persistent file, can be re‑read, edited, and reused



Markdown advantages



Low token cost, highly structured



Easy for AI to parse, easy to export (Google Docs, etc.)



Will be used directly in the front‑end



Bash commands



: Claude uses terminal commands to explore workspace



: Claude delegates tasks to smaller agents to manage token limits



🎓 Future Content & Teaching



This session



Free, informal “live stream” style walkthrough



Shows real daily workflow



Upcoming courses



Structured, college‑level with workbooks



Deep dives into: JavaScript, Python, Git, GitHub, reading PRDs



Paid content will be separate, more comprehensive



: Break every concept into digestible pieces for all skill levels



------



Jake's content\Building Your Stack\1.4 Repo Tour Open Source References.md



What You'll Get From This



A curated list of open-source AI UI projects worth studying, with notes on what to learn from each.



------



How to Use This Page



This isn't a tutorial. It's a research resource.



Each repo below does something interesting with AI interfaces. Some wrap Claude Code. Some build custom chat UIs. Some solve problems you haven't thought of yet.

#### For each one, I've noted:

What it does



What's worth studying



What you might borrow for your own builds



You don't need to clone all of these. Pick the ones relevant to what you're building. Read their code. See how they solved problems. Take what's useful.



This page gets updated as I find new repos worth studying.



------



Claude Code Interfaces

#### What it does:

A web-based front-end for Claude Code. Lets you run Claude Code through a browser interface instead of the terminal.

#### What's worth studying:

How they handle session persistence



The websocket connection between front-end and Claude Code CLI



Their approach to streaming responses

#### What I borrowed:

The session persistence patterns. Being able to close the browser and come back to the same conversation.



------

#### What it does:

Another Claude Code wrapper with a focus on project management. Tracks usage, manages multiple projects, provides a cleaner interface than raw terminal.

#### What's worth studying:

Usage tracking implementation



Multi-project switching



How they structured the settings/config system

#### What I didn't use:

Most of the UI complexity. Too many features for what I needed. But the underlying patterns are solid.



------

#### What it does:

A terminal UI (TUI) for Claude Code. Still in the terminal, but with better visual organization.

#### What's worth studying:

How they parse and display Claude's output



Keyboard shortcuts and navigation patterns



The balance between terminal simplicity and added features



People who want to stay in the terminal but want a better experience than raw CLI.



------



Custom AI Chat Interfaces

#### What it does:

A self-hosted web interface for various LLMs. Supports multiple providers, local models, and has a clean chat UI.

#### What's worth studying:

Multi-provider architecture (how they abstract different AI backends)



The conversation management system



Their approach to system prompts and presets

#### What you might borrow:

If you're building something that needs to work with multiple AI providers, study how they did the abstraction layer.



------

#### What it does:

A polished open-source chat UI with plugins, agents, and knowledge base features.

#### What's worth studying:

The plugin architecture



How they handle file uploads and knowledge bases



UI/UX patterns for chat interfaces



Inspiration on what a full-featured chat interface can look like. Even if you're building something minimal, seeing the full-featured version helps you understand what to cut.



------



Workflow and Agent Tools

#### What it does:

A workflow automation tool with a visual node-based editor. Not AI-specific, but increasingly used for AI workflows.

#### What's worth studying:

The node-based visual editor implementation



How they handle workflow state and execution



Their approach to connecting different services

#### Why it's here:

The workflow map I want to build for my front-end is conceptually similar. Visual representation of processes. Nodes you can click into. This is one way to solve that problem.



------

#### What it does:

A visual framework for building LLM applications. Drag-and-drop interface for creating AI workflows.

#### What's worth studying:

How they visualize LLM chains and agents



The component system (each node is a component)



How they handle the gap between visual representation and actual execution

#### Relevant to:

Anyone building visual interfaces for AI workflows. Even if you don't use their approach, understanding it helps you design your own.



------



Design and UI Skills

#### What it does:

A skill package that teaches Claude better design sense for front-end work. Not a repo you run, but prompts and instructions Claude reads.

#### What's worth studying:

How they structured the skill (prompts, examples, guidelines)



The design principles they encode



How skills can shape Claude's output style

#### Why it matters:

If you're building a front-end with Claude, this skill makes the output look better. It's also a good example of how to create your own skills for specific domains.



------



What to Do With These

#### If you're building a Claude Code front-end:

Start with Claude Code Web and Op Code. Understand how they connect to the CLI. Borrow the session persistence patterns.

#### If you're building a custom chat interface:

Look at Open WebUI and Lobe Chat. Even if they're more complex than what you need, they show patterns for conversation management, streaming, and UI.

#### If you're building workflow visualization:

Study n8n and Langflow. The node-based visual editor is a solved problem. See how they solved it.

#### If you want Claude to build better front-ends:

Get the UIUX Pro Skill. It's not code to run, it's context for Claude.



------



Contributing



Found a repo that taught you something about building AI interfaces? Share it in the check-in thread. If it's useful, I'll add it to this page.



------



More Sessions Coming



This course is an ongoing build. As I finish more sections of the front-end project, new lessons will appear here.



[LINK TO future lessons when available]



------



Jake's content\Building Your Stack\2.1 Why Remote Access.md



What You'll Get From This



A clear understanding of what Remote Control enables and whether you actually need it.



------



[VIDEO: Coming Soon]



------



The Feature



Claude Code now has Remote Control built in.



Start a session at your desk. Scan a QR code. Continue from your phone. Your local environment stays local. Your files, your MCP servers, your workspace. Nothing moves to the cloud. You're just accessing the session from somewhere else.



This used to require workarounds. SSH tunnels. Web interfaces. Custom front-ends. Now it's one command and a QR code.



------



What This Enables



Async workflows



Kick off a long build. Close your laptop lid. Go to dinner. Check your phone. See where Claude is. Send a quick adjustment. Put the phone away.



The work continues without you watching it. You check in when it matters.



Mobile monitoring



Some builds take time. Renders. Large code generation. Multi-step pipelines.



You don't need to sit and watch. Glance at your phone, see progress, intervene if something goes wrong.



Quick interventions from anywhere



Claude hits a decision point. It asks a question. You're not at your desk.



With Remote Control, you see the question on your phone. You answer. Claude continues. You didn't have to wait until you got home.



Voice input on mobile



Phone keyboards are slow. But phones have voice input.



You can talk to Claude. Describe what you want. Send it as a message. This changes how you interact when you're mobile.



------



What Stays Local



This is important: Remote Control is not cloud computing.



Your session runs on your machine. Your files stay on your machine. Your MCP servers, your project configuration, your



http://claude.md/



. All local.



The mobile app and web interface are just windows into your local session. Commands you send get routed to your machine. Results get streamed back. But execution happens locally.



This matters because your local setup is irreplaceable. The cloud version of Claude Code starts fresh every time. Remote Control keeps everything.



------



When to Use It

#### Good use cases:

Long builds you want to monitor without sitting at your desk



Quick approvals and decisions when you're away



Checking status from your phone while doing something else



Voice-driven instructions when typing is inconvenient

#### Not necessary for:

Short tasks you'll finish before leaving your desk



Work that requires deep focus and full screen context



Anything where you'll be back at your computer in a few minutes



Remote Control is about mobility, not about replacing desk work. If you're doing something complex that needs your full attention, stay at your desk.



------



Current Limitations

#### Remote Control is relatively new. Some rough edges:

One session at a time



You can only run one Remote Control session per machine. If you need multiple sessions, you're back at your terminal.



Terminal must stay running



If your terminal closes or the claude process exits, the remote session ends. Sleep is fine. Closing the lid is usually fine (depending on power settings). But if the process dies, the session dies.



Max tier for now



Currently requires the Max subscription ($100-200/month). Pro access is coming but isn't here yet.



Still being refined



Some users report occasional bugs. API errors. Sessions that don't reconnect cleanly. Anthropic is actively improving this.



These limitations will likely shrink over time. The feature is new. It's getting better.



------



The Bigger Picture



Remote Control solves a real problem: AI coding tied to your desk.

#### Before this, you had two options:

Use Claude Code locally (powerful but immobile)



Use Claude Code on the web (mobile but no local context)



Now you get both. Local power, mobile access.



This changes how you can work. Start something at your desk. Walk away. Come back. The session is still there. Your context is still there. Nothing lost.



------

#### What This Module Covers

2.2: Using Remote Control



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=f305a93c1be949d3b3bcdbc2aa22a3f5&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The actual commands. Starting a session. Connecting from your phone. What you see, what you can do.



2.3: Mobile Workflow Patterns



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=d207c5fe86814f23a224c0a25d484518&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



How work changes when you're on mobile. What to do from your phone. What to save for your desk.



2.4: Session Persistence Across Devices



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=fa6dced1aed94c4792602cf121a0168a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The workspace-as-memory pattern. How your files become the continuity that Claude's memory can't provide.



------



Quick Decision: Do You Need Remote Control?

#### Answer these:

How often are you away from your desk during active builds?



Rarely → You probably don't need it yet



Sometimes → Worth setting up



Often → This will change how you work



How long do your builds typically run?



Minutes → You can wait



30+ minutes → Remote monitoring helps



Hours → Remote control is valuable



Do you have Max tier?



Yes → You can use it now



No → Wait for Pro access or upgrade



------

#### The folder architecture that makes remote work smooth:

3.1 The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### Claude Code setup if you're not there yet:

4.1 Install and First Use



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### Build a custom UI on top of this:

Module 1: Custom UI for Claude



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=c7a59d0fa0c145549dc9126470b7f82f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



The why is clear. Now let's get it running. One command, one QR code, and you're connected.



------



Jake's content\Building Your Stack\2.2 Setting Up Remote Sessions.md



What You'll Get From This



Remote Control running and connected to your phone.



------



[VIDEO: Coming Soon]



------



Three Ways to Start



You have three options depending on where you are in your workflow.



Option 1: Server Mode



Start a session that's remote-only. Your terminal shows connection status but you interact from your phone or browser.



claude remote-control

#### Or the short version:

Your terminal displays a session URL and a QR code. Press spacebar to toggle the QR code display.



Option 2: Interactive + Remote



Start a normal session that's also accessible remotely. You can type in your terminal AND control from your phone. Both stay in sync.



claude --remote-control



claude --rc



This gives you the full terminal experience with remote access layered on top.



Option 3: Enable Mid-Session



Already in a Claude Code session and want to continue it remotely? Use the slash command:



/remote-control



This starts Remote Control on your existing session. Your conversation history carries over. You get a session URL and QR code.



------



Connecting From Your Phone

#### Once Remote Control is active, you have options:

Scan the QR code



Open your phone's camera (or the Claude app). Scan the code shown in your terminal. You're in.



Use the session URL



Copy the URL from your terminal. Open it in any browser. It takes you directly to your session on



claude.ai/code



http://claude.ai/code



Find it in the app



claude.ai/code



http://claude.ai/code



or the Claude mobile app. Your Remote Control session appears in the session list with a computer icon and green status dot.



------



What You See

#### In your terminal:

Connection status. Whether someone's connected. Tool activity as Claude runs commands. It's a dashboard of what's happening.

#### On your phone/browser:

The same conversation. The same context. You can send messages, see Claude's responses, approve actions. Everything stays synchronized.



If you send a message from your phone, it appears in the terminal. If Claude runs a command locally, you see the result on your phone.



------



The Workflow

#### Here's how a typical session goes:

Start at your desk.



You're in your project folder. You kick off a task.



claude --rc



Work normally.



Type in your terminal. Get Claude going on something.



Grab lunch. Run an errand. The session keeps running.



Check your phone.



Open the Claude app. Find your session (computer icon, green dot). See the progress.



Intervene if needed.



Claude asks a question? Answer from your phone. Need to adjust direction? Send a message.



Return to your desk.



Your terminal still shows everything. Pick up where you left off.



The conversation is the same everywhere. You're not switching between different sessions. It's one session, multiple access points.



------



Naming Your Sessions



By default, Remote Control sessions are named after your last message or "Remote Control session" if there's no history.

#### You can name them explicitly:

claude remote-control --name "animation-build"

#### Or rename an existing session:

/rename animation-build



Useful when you're running multiple projects and want to find the right session from your phone.



------



What Can You Do Remotely?

#### Everything you can do in the terminal:

Send messages and prompts



See Claude's responses



Approve file changes



Monitor tool activity



Stop and redirect



You're not limited to read-only. This is full control.



------



What Happens When You Disconnect?

#### If you close the Claude app or navigate away:

The session keeps running on your machine



Reconnect anytime and pick up where you left off



Auto-reconnect usually works if your phone briefly loses connection

#### If your laptop sleeps:

Usually fine. The session should reconnect when it wakes.



Depends on your power settings. If sleep kills the terminal process, the session ends.

#### If your terminal closes:

The session ends. You'll need to start a new one.



claude --rc



again in the same folder to start fresh.



------



Keep your terminal running



Don't close the terminal window. Minimize it if you want. But if the process exits, the remote session ends.



Check your power settings



Make sure your laptop doesn't kill terminal processes when the lid closes or when it sleeps. "Sleep" is usually fine. "Hibernate" or aggressive power saving can kill the session.



Use named sessions



If you work on multiple projects, name your sessions. Makes them easy to find from your phone.



Start remote-enabled from the beginning



If there's any chance you'll want to step away, use



claude --rc



instead of just



. Easier than remembering to run



------



Troubleshooting



"I can't find my session in the app"



Make sure Remote Control is actually running. Check your terminal for the session URL. If the process died, the session is gone.



"Messages aren't syncing"



Check your network connection on both devices. If one side is offline, sync will resume when it reconnects.



"I'm getting API errors"



This happens occasionally. The feature is still being refined. Usually restarting the session fixes it:

# In terminal, exit and restart

claude --rc



"The session died while I was away"



Your terminal process likely exited. Check if your laptop hibernated or if something closed the terminal. Start a new session.



------



Command Reference



What You Want Command Start remote-only (server mode)



claude remote-control



Start interactive + remote



claude --remote-control



claude --rc



Enable remote mid-session



/remote-control

#### Name your session

--name "session-name"



Show/hide QR code Press spacebar (in server mode) Rename existing session



/rename new-name



Checklist Before You Walk Away



[ ] Terminal is open and



[ ] Remote Control is enabled (you see the session URL)



[ ] Power settings won't kill the process



[ ] You know which session to look for in the app



------

#### The folder setup that makes context persist:

LINK TO 3.1 The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### Official docs:

https://code.claude.com/docs/en/remote-control



https://code.claude.com/docs/en/remote-control



------



Remote Control is running. Now let's talk about what to actually do from your phone.



------



Jake's content\Building Your Stack\2.3 Mobile Workflow Patterns.md



What You'll Get From This



A practical understanding of what to do from your phone and what to save for your desk.



------



[VIDEO: Coming Soon]



------



Mobile Is Different



Working from your phone is not the same as working from your desk with a smaller screen. It's a different mode of work.



The keyboard is slower. The screen shows less context. You can't see multiple files at once. Your attention is probably split.



But you have voice. You have quick access. You have presence in moments when you'd otherwise be waiting.



The goal isn't to do everything from mobile. It's to do the RIGHT things from mobile.



------



The Three Mobile Modes



Mode 1: Check and Acknowledge



You're not working. You're just checking status.



Is the build still running?



Did Claude hit an error?



Is it waiting for input?



This takes 10 seconds. Open the Claude app. Find your session (computer icon, green dot). Glance at the latest messages. Put the phone away.



If everything is fine, you don't do anything. If something needs attention, you either handle it quickly (Mode 2) or note it for later (back to desk).



Long builds, overnight renders, monitoring without babysitting.



------



Mode 2: Quick Intervention



Claude needs something. A decision. A clarification. Permission to proceed.



You respond in one or two messages. Short. Direct. Just enough to unblock.



"Yes, proceed with that approach"



"Use the blue color scheme, not green"



"Skip that section for now, we'll handle it later"



"Stop. I'll fix this when I'm back"



You're not doing deep work. You're keeping the pipeline moving.



Decision points, approvals, quick redirects.



------



Mode 3: Voice-Driven Work



Your phone has a microphone. Use it.



Instead of typing on a tiny keyboard, you talk. The Claude app accepts voice input. So does your phone's keyboard.



"Read the spec file and tell me where we left off"



"What's the status of the animation build?"



"Update the PRD to include a dark mode option"



"Draft a response to the email I just forwarded"



Voice input is faster than mobile typing. It also works when your hands are busy.



Longer instructions, complex requests, hands-free situations.



------



What Works on Mobile



Monitoring and status checks



Glance at progress. See if anything needs attention.



Binary decisions



Yes or no. This or that. Approve or reject.



Short text responses



One or two sentences. Quick clarifications.



Voice-driven instructions



Talk instead of type. Claude parses voice input fine.



Approving actions



Claude asks permission to edit a file or run a command. You tap approve.



Reading outputs



Review what Claude generated. Flag issues for later.



------



What Doesn't Work on Mobile



Deep editing



If you need to look at code and make precise changes, wait for your desk.



Multi-file context



You can't see three files at once on a phone. Don't try.



Long-form writing



If Claude needs detailed instructions, either use voice or wait.



Tracing through errors requires screen space and focus. Mobile isn't the place.



Creative direction



Nuanced feedback on tone, style, visuals. Better with a full screen.



------



The Handoff Pattern



Best mobile workflows include clean handoffs between devices.

#### From desk to mobile:

#### Before you leave your desk, tell Claude what's happening:

I'm stepping away. Continue with the build. If you hit a blocker, describe it and wait. I'll check in from my phone.



Claude knows you're not watching closely. It won't ask unnecessary questions. It will flag real blockers clearly.

#### From mobile to desk:

#### When you're back at your desk, catch up:

What happened while I was away? Summarize progress and any decisions you need from me.



Claude gives you the update. You're back in context.



------



Voice Input Tips

#### Mobile voice input works better when you:

Speak in complete thoughts



Don't stop mid-sentence. Finish your thought, then stop.



Use natural language



You don't need to sound like a prompt engineer. Claude understands normal speech.



Pause for punctuation



A slight pause helps voice-to-text figure out sentence breaks.



Review before sending



Voice-to-text makes mistakes. Quick glance before you hit send.



Keep it short



If your voice message is becoming a paragraph, you're probably doing something that should wait for your desk.



------



Building Mobile Into Your Workflow



Don't try to do everything remotely. Instead, design your workflow with mobile checkpoints.



Example: Animation Build



(Desk) Start the build, set up the spec, enable Remote Control



(Mobile) Check status after lunch, approve scene 1 output



(Mobile) Get notification that scene 2 needs input, respond with voice



(Desk) Final review and polish when you're back



The build progresses while you're away. You intervene only when needed. Mobile keeps things moving without requiring you to stay at your desk.



Example: Code Review



(Desk) Ask Claude to review a PR, enable Remote Control, walk to a meeting



(Mobile) During a break, check Claude's findings



(Mobile) "Focus on the authentication logic, ignore the styling issues for now"



(Desk) Read the detailed analysis when you're back



------



The "Don't Check" Option



Sometimes the best mobile workflow is not checking at all.



If Claude has a clear PRD and you're doing something else, let it run. You don't need to monitor constantly. The work will be there when you get back.



Mobile access is a capability. It's not an obligation to use it.



------



When to Check vs When to Wait

#### Check when:

The task has decision points Claude can't make alone



You're expecting it to finish soon



You gave Claude something ambiguous and want to course-correct early



Claude has a clear spec and doesn't need input



You're doing something that needs your full attention



You'll be back at your desk in 30 minutes anyway



The remote session persists. Claude keeps working. You don't have to watch.



------



Mobile Decision Tree

#### When you open the Claude app to check on a session:

Is it an error/blocker? → Assess: can I fix this in 2 messages?



Yes → Fix it (Mode 2)



No → Acknowledge and wait for desk



Is it asking for a decision? → Answer if it's clear cut



Clear decision → Respond (Mode 2)



Needs thought → "Continue with other tasks, I'll decide on this later"



Is it just a status update? → Glance and close the app (Mode 1)



Handoff Prompts

#### Before leaving desk:

I'm stepping away. Continue with [current task]. If you hit a blocker, describe it clearly and wait for my input.

#### When returning to desk:

What happened while I was away? Summarize progress and what you need from me.



------

#### Setting up Remote Control:

2.2 Using Remote Control



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=f305a93c1be949d3b3bcdbc2aa22a3f5&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### The workspace structure that makes handoffs clean:

3.1 The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



You can control Claude from anywhere. But how do you maintain context when you switch devices or start fresh sessions? The answer is in how you structure your workspace.



------



Jake's content\Building Your Stack\2.4 Session Persistence Across Devices.md



What You'll Get From This



The ability to pick up exactly where you left off, even when sessions end.



------



[VIDEO: Coming Soon]



------



Two Kinds of Persistence



Remote Control gives you one kind of persistence: within a session, everything syncs across devices. You send a message from your phone, it appears in your terminal. Context carries over. The conversation is continuous.



But sessions end. Your terminal closes. You hit token limits. Your laptop restarts. The Remote Control session dies.



When you start a new session, Claude doesn't remember the old one. You're starting fresh.



This lesson is about the second kind of persistence: making sure YOU don't lose context even when Claude does.



------



The Problem



Claude doesn't remember between sessions.



You have a productive session. You make real progress. The session ends. You start a new one the next day. Claude has no idea what you were working on.



You can re-explain. But that's slow and you'll miss details.



Or you can put the context in files that persist.



------



The Solution: Workspace as Memory



Claude's memory doesn't persist. But your files do.

#### Everything Claude needs to know should live in your workspace:

The PRD that describes the project



http://claude.md/



that maps the folder structure



The progress notes that track what's been done



The specs, the code, the outputs

#### When you start a new session, you tell Claude:

Read the PRD and CLAUDE.md. Look at what's been built. Tell me where we are.



Claude reads the files. Claude knows where you are. The workspace becomes the memory.



------



What to Persist

#### Not everything needs to be saved. Here's what matters:

Project definition (always persist)



The PRD or project spec



http://claude.md/



or context file



The folder structure itself



This is the "what are we building" layer. It exists before you start and stays consistent throughout.



Progress markers (persist regularly)



PROGRESS.md



http://progress.md/



http://status.md/



Notes on what's done, what's in progress, what's blocked



Updated after significant milestones



This is the "where are we" layer. Update it when something meaningful changes.



Session notes (persist when important)



Key decisions made during a session



Reasons for specific choices



Things to remember for later



This is the "why did we do that" layer. You don't need to log everything, but log what you'd be frustrated to forget.



------

#### Keep a simple progress file at the root of each project:

# Progress

## Current Status

Building the panel layout. Workflow map is next.

## Last Session (2024-01-15)

\-    Completed: Basic server setup, connection to Claude Code CLI

\-    In Progress: Panel components

\-    Blocked: None

\-    Next: Add collapse/expand for panels

## Decisions Made

\-    Using React instead of Vue (faster for our timeline)

\-    Skipping dark mode for v1 (add later)

\-    Panel order: workflow left, editor middle, chat right

## Open Questions

\-    How to handle multiple simultaneous chats?

\-    Should workflow map be tree or graph?

#### At the start of each session:

Read PROGRESS.md. What's the status? What should we work on next?

#### At the end of each session:

Update PROGRESS.md with what we accomplished and what's next.



This takes 30 seconds and saves you 10 minutes of re-orienting next time.



------



When to Update

#### During a Remote Control session:

You don't need to update constantly. The session persists across devices automatically. Update when you're about to end the session or when you hit a major milestone.

#### Before walking away:

If there's any chance the session might end while you're gone (laptop sleeps too long, battery dies, terminal crashes), update



PROGRESS.md



http://progress.md/



before you leave.

#### After any significant decision:

If you made a choice that future-you needs to remember, write it down. "We decided X because Y."

#### When you hit token limits:

Long sessions hit context limits. Before you lose coherence, have Claude summarize progress and update the files.



------



The Reconnection Workflow

#### When you start a fresh session after the previous one ended:

Step 1: Orient



Read CLAUDE.md and PROGRESS.md. Summarize where we are.



Claude reads the context. You verify it matches your understanding.



Step 2: Verify



Look at the actual code/files. Does the progress file match reality?



Sometimes sessions end unexpectedly. The progress file might say something is done that isn't. A quick check catches this.



Step 3: Continue



Let's continue with [specific next task from progress file].



You're back in context. You didn't waste time re-explaining the project.



------



Remote Control + Workspace Persistence

#### These two systems work together:

Remote Control



handles persistence within a session. You can switch devices freely. Context carries over automatically.



Workspace files



handle persistence across sessions. When a session ends and a new one starts, the files catch you.

#### Think of it like this:

Remote Control = short-term memory (within a conversation)



Workspace files = long-term memory (across conversations)



You need both.



------



When Sessions End Unexpectedly



Sometimes you lose connection. Sometimes your laptop dies. Sometimes Claude runs out of tokens mid-task.

#### When you reconnect or start fresh:

Don't assume the last task completed.



Look at the files.



Did Claude write what it said it would?



Ask Claude to assess.



"Look at the code. Did the last task finish successfully?"



PROGRESS.md



http://progress.md/



with the actual state, not what you expected.



Unexpected ends are normal. The workspace catches you.



------



Making It Automatic



You can build the persistence habit into your prompts.

#### Session start prompt (save this):

Read CLAUDE.md and PROGRESS.md. Summarize: what is this project, where are we, and what should we work on next?

#### Session end prompt (save this):

Update PROGRESS.md with what we accomplished this session and what's next. Then give me a one-sentence summary of today's progress.

#### Before stepping away:

Update PROGRESS.md with current status in case this session ends.



These become reflexes. You stop thinking about it.



------



The Bigger Pattern



This is the same principle from Foundation. The folder architecture is the source of truth.



http://claude.md/



describes the project. Your



PROGRESS.md



http://progress.md/



tracks the work. Your specs, PRDs, and outputs accumulate in the workspace.



Claude is stateless. Your workspace is stateful. The workspace is the memory.



This works for single sessions. It works for multi-device work. It works for team collaboration. It's the same pattern at every scale.



------



PROGRESS.md



http://progress.md/

# Progress

## Current Status

[One sentence: what's the current state?]

## Last Session ([date])

\-    Completed: [what got done]

\-    In Progress: [what's partially done]

\-    Blocked: [what's stuck and why]

\-    Next: [what should happen next]

## Decisions Made

\-    [Decision 1 and brief reasoning]

\-    [Decision 2 and brief reasoning]

## Open Questions

\-    [Question 1]

\-    [Question 2]



Prompt Templates

#### Session start:

Read CLAUDE.md and PROGRESS.md. Summarize: what is this project, where are we, and what should we work on next?

#### Session end:

Update PROGRESS.md with what we accomplished this session and what's next.

#### Before stepping away:

Update PROGRESS.md with current status in case this session ends.



------



Module Complete

#### You now have:

Remote Control running (2.2)



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=f305a93c1be949d3b3bcdbc2aa22a3f5&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Patterns for mobile work (2.3)



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=d207c5fe86814f23a224c0a25d484518&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Persistence across sessions (2.4) here now

#### Where to go next:

Ready for the advanced templates?



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



Jake's content\The Archive\1.1 Welcome.md



📝 What This Course Is



I have been teaching AI in education and business for quite a few years. Before most people knew what a context window was. Before "prompt engineering" became a job title. Before anyone was talking about agent architecture or structured workflows.



I recorded videos. I wrote articles. I made predictions. I built frameworks.



This course puts all of that on the table and asks a simple question: did it hold up?



The answer, mostly, is yes. The core ideas landed. The predictions tracked. The frameworks evolved into the methodology I teach today across thousands of professionals, a 12,500-member community, and a peer-reviewed papers.



But "mostly" matters. Some things changed. Some tools I recommended are renamed. Some advice I gave was right in direction but early in detail. This course is honest about all of it. The revisions are a feature. They show the thinking is alive and still moving.



📐 How the Course Is Built



Three modules. Each one does something different.



Module 1: The Setup (you are here)



This lesson frames the course. The next lesson, "A 2,000-Year Overnight Success," gives you the full history of thinking machines from ancient Alexandria to the language models on your phone. It matters because the videos in Module 2 are part of a pattern that is two thousand years old. Every generation builds thinking machines, normalizes them, and forgets they were ever impossible. Understanding that pattern changes how you hear everything that comes after.



Module 2: Old But Gold



Three videos from late 2023 and early 2024. Each one is paired with a written companion I wrote in 2026 that walks through what I got right, what needs updating, and how the ideas connect to what I teach now.



LESSON 2.1: The Mindset Before the Method



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=10135ac3e904424d847b938004948ddb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



A 39-minute workshop I gave to college professors at Flagler College in



January 2024



. The case that AI is a mindset problem, not a tool problem. The human becomes more valuable. The companion tracks how that thesis played out across two years of real training engagements.



Lesson 2.2: Raise the Bar



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=79c815829450460eb106cd271a591d9f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



December 2023.



If students can use AI to cheat on your assignments, your assignments are too easy. The case for raising the baseline using the calculator, internet, and coding pyramid as historical proof. The companion adds the frameworks that turn "raise the bar" into a method.



Lesson 2.3: More Human



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=723f6fbc980b4701b74bcb76615870c5&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



December 2023



. I told a story about saving a man's life on Mount Fuji during a typhoon and used it to argue that AI strips away the robotic parts of our work, leaving the human parts standing. The most personal video in this course. The companion connects it to the Ethics Engine research and the broader question of what AI reveals about us.



Module 3: Where It Goes Now



Current articles on the questions that matter today. These are not retrospectives. This is where the early thinking leads.



Lesson 3.1: Beyond the Turing Test



https://www.skool.com/quantum-quill-lyceum-1116?utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



We already blew past the Turing Test. The next question is whether you can tell your AI from someone else's. AI personality, the Ethics Engine, consciousness as resonance, and the governance problem ahead.



Lesson 3.2: The Questions Schools Should Be Asking



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=5d14e28de95d43b2a3960e0ebbbfd617&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Intellectual property in education is broken. Students should graduate owning AI trained on their thinking. Teachers should own their methods. The structural argument for why ownership is the real AI-in-education question.



Lesson 3.3: The Real Cost of Knowledge



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=7658a441afa9449e92951519e2c95e5a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The apocalypse laptop thought experiment. If the internet is gone and you have one solar-powered laptop, do you pick Wikipedia or a local AI model? The answer reframes everything about AI energy costs, local vs cloud, and how we deploy intelligence.



Lesson 3.4: The Rise of Computational Orchestration



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=ed8f01da061a4b76bfde21fc4dbd4d41&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The discipline that emerged from everything else in this course. Knowing which type of computation to apply to which problem. The 60/30/10 pattern. Why most AI transformations fail. This is where the early videos were pointing all along.



📋 How to Move Through This



Watch each video before reading the companion.



The companions assume you have seen the video. Start with Module 1 to get the history and the frame, then move through Module 2 in order. Module 3 can be taken in any sequence.



If you are new to Clief Notes, start with



The Foundation course first.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=5d535542a72d417e8635b80e56412558&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Old But Gold adds depth and context to what The Foundation teaches. If you have already been through The Foundation, this course shows you where the ideas came from and where they are going.



⏭️ Start with Lesson 1.2: A 2,000-Year Overnight Success



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=147b0e486c964ba78a70cdc1d2d40c5d&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



Jake's content\The Archive\1.2 A 2,000-Year Overnight Success.md



What You'll Get From This



The real history of AI, from programmable robots in ancient Alexandria to the language models on your phone. Two thousand years of thinking machines that most people have never heard of, and the pattern that connects all of them.



📝 Why This Lesson Is Here



Before you watch the videos in this course, you need to see the pattern.



Every generation has built thinking machines. Every generation believed they had either achieved the impossible or hit the absolute limit of what machines could do. Every generation was wrong.



Heron of Alexandria programmed a robot theatre with ropes and knots in 62 CE. Al-Jazari built reprogrammable automata in 1206.



Jacquard's loom stored programs on punched cards in 1801. Babbage designed a general-purpose computer from brass and steel. Lovelace wrote the first algorithm. Turing asked what happens if we teach machines to learn.



Each layer seemed impossible until it existed. Then we normalized it, forgot the complexity underneath, and declared the next layer impossible.



AI is the latest layer. It will not be the last.



This article walks through the full history.



It matters because the videos in Module 2 of this course were recorded in 2023 and 2024, when most people thought AI was brand new.



They were already building on two thousand years of the same pattern. Understanding that pattern changes how you hear everything that comes after.



═══════════════════════════════════════



------



Everyone knows AI started in the 1950s.



Everyone is wrong by about 2,000 years.



You talk to math every day.



When you ask ChatGPT a question, you’re conversing with statistics, lists of numbers connected to words stored in a vast multi-dimensional digital space controlled by computer chips.



In the future, we’ll have



http://google.com/



to our kids.

#### And when we are done explaining it to them, they’ll say:

You mean you had a question, and a machine just gave you a long list of websites? And you had to click through them one by one, dodging all the ads and junk, just to piece together the answer yourself? That sounds broken.’



The scale we use AI tools today would have sounded impossible just a few short years back, yet we’ve already normalized it,



like we normalize every impossible thing, then promptly forget it was ever impossible.



In conversations with academics and clients, I’ve noticed something that led to me to write an article such as this:



Most believe artificial intelligence emerged with



, or perhaps



(Electronic Numerical Integrator and Computer) in the



, some only think of



if they’re particularly disconnected from history.



They don’t know about the steam-powered pigeons of ancient Alexandria. They’ve never heard of medieval Arabic robots that could be reprogrammed daily. They’re unaware that Victorian looms wove patterns from punched cards,



the first stored programs,



decades before anyone imagined electronic computers.



Even if they do know of some of these history factoids, they forget to connect it to today’s modern Ai Hub Bub.



This amnesia matters.



When we think AI is seventy years old rather than two thousand, we miss the pattern…and patterns are everything.



We fail to see that every generation has built thinking machines of their own, each time believing they’d either achieved the impossible or hit the absolute limit of what machines could do,



the edge of abstraction



Yet we always found a way to



abstract further.



The First Programmers Used Sticks and Stones…



In Alexandria, around 62 CE—



we know the date because Heron references a lunar eclipse visible from Alexandria on March 13 of that year



—an inventor built what we’d now recognize



as the world’s first programmable robot



https://link.springer.com/chapter/10.1057/9781137319678\_2



Heron of Alexandria’s automatic theatre



wasn’t just clever mechanics; it was programmed entertainment. A ten-minute performance of Dionysian myths unfolded through acts of movement, fire, liquid pouring, and dancing figures.



The programming language was rope, knots, and falling weights.



Binary-like systems of wrapped and unwrapped cord around rotating drums determined which actions triggered when.



A millet-seed timer controlled the tempo, sand would have been too fast, water too unreliable in the Egyptian heat.



Think about what this means.



the Dark Ages,



the Renaissance, someone had already solved the fundamental problem of



programmable automation



. Heron didn’t just make machines that could move; he made machines that could follow instructions, that could be reprogrammed by changing the arrangement of knots and pegs. The



was mechanical rather than digital, but the



was identical to what runs in your smartphone:



if this condition, then that action.



Yet Heron’s theatre was primitive compared to what Greek mechanics had achieved two centuries earlier.



Yes, I tricked you, 67 CE isn’t the earliest!



The Antikythera mechanism, pulled from a shipwreck in 1900 and dated to around 100-150 BCE, computed astronomical positions with shocking sophistication.



This wasn’t just gears; any clock has gears. This was epicyclic gearing, gears mounted on other gears, creating complex motions from simple rotations. The device calculated ecliptic longitudes for the Moon, Sun, and all five visible planets. It predicted eclipses using the 18.2-year Saros cycle. It even accounted for the Moon’s elliptical orbit, a mathematical subtlety that wouldn’t be formally described until Kepler,



seventeen centuries later.



The mechanism employed differential gearing, a technology we credit to the Industrial Revolution. When researchers finally decoded its full functionality in 2021, they concluded it “mechanized the predictions of scientific theories” and could have “automated many of the calculations needed for its own design.”



In other words, the ancient Greeks built a computer that could have helped design itself (within reason).



All though in this context saying it



“helped design itself”



is like saying



“the brain named itself”



Perspective becomes important.



The Memory Machines of Baghdad



When mechanical knowledge re-emerged, it came from



In 850 CE, the Banū Mūsā brothers described something extraordinary in their



Book of Ingenious Devices



: a flute player that could be programmed by its user.



Steam powered the mechanism,



but the user controlled which melodies emerged.



Different configurations produced different songs. Now the goal was not a simple automation trick, it was user-programmable automation, the conceptual leap from



“machine that does one thing”



“machine that does what you tell it.”



A very important nuance to _note (_pun intended) as we move forward.



Making songs is interesting but a production line of machines is needed to really start making progress.



This is where Al-Jazari, chief engineer to the Artuqid dynasty, comes into play.



In 1206, the year he died, he completed a manuscript describing fifty mechanical devices. His castle clock, standing eleven feet tall, did more than tell time. It could be reprogrammed daily to account for the changing length of days and nights throughout the year.



The clock’s musical automaton band, four robot musicians floating in a boat, took programmability further. By adjusting pegs on rotating cylinders, you could change what the robots played. Move a peg, change a note. Rearrange the pattern, compose a new song. Al-Jazari had invented the mechanical equivalent of a music sequencer, where the program was physical pins and the output was sound.



He even documented the



first systematic use of camshafts



, converting rotary motion to linear action—the same principle that would drive the Industrial Revolution five hundred years later.



His manuscript survives in multiple copies, the earliest at Istanbul’s Topkapi Palace. You can see reconstructions at the Science Museum in London, where in 1976 they successfully built his scribe clock from his eight-hundred-year-old instructions. It worked perfectly. Donald Hill, who translated Al-Jazari’s work, wrote that it was “impossible to over-emphasize the importance of Al-Jazari’s work in the history of engineering.” Yet most people have never heard his name.



The Philosophers and the Frauds



By the 18th century, Europe had caught up to where the Middle East had been five centuries earlier. But now the automata came with philosophical implications.



René Descartes



had written in 1637 that animal bodies were “



machines which, having been made by the hands of God, are incomparably better ordered



” than anything humans could build.



He imagined machines that could speak when touched, cry out when hurt, but never “think”.



At least not like humans did, but he left us with a “test” to really be sure it was a robot and not a Human in case it ever became too hard to distinguish the difference.



Discourse on The Method



he outlined a ‘Turing Test’ that predates the Alan Turing’s own test (we go over later in the article) by over 300 years (again, he was thinking about this in the 1600s !?):



“If there were machines bearing the image of our bodies, and capable of imitating our actions as far as it is morally possible, there would still remain two most certain tests whereby to know that they were not therefore really men.



Of these the first is that they could never use words or other signs arranged in such a manner as is competent to us in order to declare our thoughts to others:



for we may easily conceive a machine to be so constructed that it emits vocables, and even that it emits some correspondent to the action upon it of external objects which cause a change in its organs; for example, if touched in a particular place it may demand what we wish to say to it; if in another it may cry out that it is hurt, and such like;



but not that it should arrange them variously so as appositely to reply to what is said in its presence, as men of the lowest grade of intellect can do”



\-    Desecrates, Discourse on The Method



For the first part of his test,



many AI models have actually passed as of 2025.



Recent papers show our best language models



https://arxiv.org/abs/2503.23674



have fooled humans consistently enough to make us believe we’re conversing with another person. The words are arranged appositely, the replies are contextual, the conversation flows naturally.



Even Descartes would have to concede this point, machines can now “



declare thoughts



” convincingly enough that we can’t tell the difference.



his second test cuts deeper, into territory we still can’t navigate perfectly.



He argued that machines would “



inevitably fail in certain others from which it could be discovered that they did not act from knowledge, but solely from the disposition of their organs.



In other words, they’d



be exposed as mechanisms, not minds

#### Yet here’s the uncomfortable question Descartes didn’t pursue:

are human actions fundamentally different?



When we build, create, or respond, are we exercising some transcendent faculty, or are we just executing an incomprehensibly complex cascade of if-then statements written in neurons and chemistry?



Our organs—our brains, our nervous systems—have dispositions too. The difference between us and machines might not be that we’re not silicone and metal, but that we’re mechanical in ways so intricate we can’t recognize our own programming.



Unfortunately, this particular part of the conversation is out of the scope of this article however I explore what it “means to think” a but deeper



here in this article



https://jakevanclief.substack.com/p/calculating-consciousness



if you want to continue reading.



Moving on from Descartes and continuing this “challenge of automation” we continue forward in history.



Jacques de Vaucanson and his Flute Player of 1737 actually played the flute—real breath from leather bellows, real fingers (covered in leather for pliability) covering real holes, a moving tongue controlling airflow. It knew twelve songs. Musicians complained it played shrilly,



but it played



His follow-up,



the Digesting Duck



, seemed even more miraculous: it ate grain, drank water, digested food in what Vaucanson called a



“chemical laboratory,”



and defecated through



“the usual passage.”



The duck was a fraud. When magician Jean-Eugène Robert-Houdin examined it in 1844, he discovered the trick: pre-stored fake feces (green-dyed breadcrumbs) released while eaten grain collected in a separate compartment. Yet even as fraud, it advanced the conversation.



Voltaire wrote, “Without the voice of le Maure and Vaucanson’s duck, you would have nothing to remind you of the glory of France.”



The duck burned in a museum fire in Krakow around 1879, leaving only heat-warped wings in the ruins.



The era’s most sophisticated automata



came from Pierre Jaquet-Droz and his son.



, completed in 1772, contains over 6,000 parts and remains programmable today, you can still make it write any text up to forty characters by adjusting a wheel where each character is selected individually. It dips its quill in ink, shakes its wrist to prevent dripping, and its eyes follow the text as it writes.



At Switzerland’s



Musée d’Art et d’Histoire



, on the first Sunday of each month, it still writes messages. Sometimes it writes



“I think therefore I am.”



Here was Descartes’s test made mechanical: a machine arranging words. Yet it wasn’t thinking—it was following instructions encoded in wheels and cams.



The question had fully shifted from “can machines think?” to “what’s the difference between thinking and



perfectly imitating thought



When Patterns Became Programs



The answer came from an unexpected source: the textile industry. Joseph Marie Jacquard’s loom, patented December 23, 1801, transformed weaving, but more importantly, it



transformed the concept of instructions.



Before Jacquard, complex patterns required a master weaver’s constant attention, reading the design and manually selecting threads. Jacquard’s innovation was radical:



the pattern became the program.



Chains of punched pasteboard cards fed through the loom. Each card controlled one row of the pattern.



Where there were holes,



pins passed through to activate hooks that raised specific threads.



Where there were no holes



, the pins pressed against the card, leaving threads in place.



The weaver just operated the loom; the cards



the intelligence.



By 1812, France had



of these looms. Patterns that once took months to weave now took days. The cost of complex textiles plummeted. Lyon weavers rioted and attacked Jacquard,



burning looms in fear of unemployment



, the first tech backlash against automation.



Charles Babbage



saw these looms and recognized something profound.



When his Difference Engine project stalled in 1834, he conceived something far more ambitious:



the Analytical Engine.



Not just a calculator but a general-purpose computer, capable of



calculation that could be described.



He adopted Jacquard’s punched cards wholesale but separated them into three types:



operation cards



(what to do),



variable cards



(what numbers to use), and



number cards



(data storage).



The architecture he designed, a Mill for processing, a Store for memory, input devices, output devices, is exactly what sits on your desk today, just made of brass and steel instead of silicon.



The machine was never built.



The British government had already spent £17,500 on the failed Difference Engine—enough money to buy twenty-two steam locomotives. Babbage kept refining designs for forty years rather than building, creating what Tim Robinson’s 2021 analysis calls “120,000 words” describing six phases of evolution.



Science Museum



proved it would have worked: they built his Difference Engine No. 2 between 1985 and 1991 using only techniques available in Babbage’s time.



It calculates perfectly.



What Babbage designed mechanically,



Ada Lovelace



understood conceptually.



In 1843, translating and annotating



Luigi Menabrea’s



article about the Analytical Engine, she added notes



three times longer



than the original.



contained what everyone agrees was the first computer algorithm, a method for calculating



Bernoulli numbers



https://mathworld.wolfram.com/BernoulliNumber.html



that demonstrated loops, conditional branching, and storage of intermediate results.

#### But more crucially, she saw what Babbage hadn’t fully articulated:

“The Analytical Engine has no pretensions whatever to originate anything. It can do whatever we know how to order it to perform.” - A. Lovelace



This became known as



“Lady Lovelace’s Objection,”



and it seemed definitive.



Machines followed instructions.



They couldn’t



They were, in her words, incapable of doing anything we didn’t know how to order them to perform. For a century, this settled the matter.



Alan Turing



pointed out the flaw in 1950:



what if we ordered them to learn?



The Stubborn Persistence of Low-Level Reality



Alan Turing’s 1950 paper “Computing Machinery and Intelligence” didn’t just propose the famous test, it systematically demolished nine objections to machine intelligence.



was Lady Lovelace’s.



Turing knew her statement well, quoted it directly, then observed something she couldn’t have foreseen: “The Analytical Engine has no pretensions to originate anything” only holds



if we program machines to be predictable.



What if we programmed them



to surprise us?



He proposed teaching “child machines” rather than programming adult intelligence directly.



“Instead of trying to produce a programme to simulate the adult mind, why not rather try to produce one which simulates the child’s? If this were then subjected to an appropriate course of education one would obtain the adult brain.”



The machine



would learn



, making mistakes, adjusting, improving. Its eventual behavior would be something we enabled



but didn’t directly program,



origination through education



rather than explicit instruction.



But Turing understood something deeper about the nature of computing itself. In 1947, he’d written,



“If a machine is expected to be infallible, it cannot also be intelligent. There are several mathematical theorems which say almost exactly that.”



The quest for



perfect determinism



was the enemy of intelligence. Machines would need to guess, to be wrong, to work probabilistically—just like humans.



This insight becomes more profound when you realize that all our computers already work this way,



we just pretend they don’t.



Computer Engineers reading this bear with me and give me the slightest philosophical reach here please.



Your CPU doesn’t execute instructions in order.



It guesses what you’ll do next.



Modern branch predictors



https://en.wikipedia.org/wiki/Branch\_predictor



achieve 95% accuracy on typical applications, using neural networks—yes, the AMD Ryzen processor in your computer uses perceptron-based neural branch prediction—to anticipate which code will run.



When wrong, the penalty is severe: 10-20 clock cycles wasted. The 2018 Spectre vulnerability exposed that virtually every modern CPU could be exploited through these predictions.



**We built our entire digital infrastructure on machines that guess. (**grain of salt with this statement of course).



However, that’s not the only guessing that goes on.



The Cosmos Intrudes



Your computer gets hit by cosmic radiation constantly.



(Stick with me here I promise this is important to the entire article and AI more importantly



High-energy particles from distant supernovae slam into Earth’s atmosphere, creating cascades of secondary particles.



At ground level, 95% of particles capable of causing soft errors are neutrons.



They penetrate your computer case, your chip packaging, and when one hits just right—neutron capture by a silicon nucleus, releasing an alpha particle—it flips a bit.



IBM calculated one error per 256 megabytes of RAM per month for a typical desktop.



Google’s 2009 study found one bit error per gigabyte of RAM per 1.8 hours in the worst case.



Seriously, your computer needing to be turned off an back on again because “something stopped working” could have actually been a solar flare millions of miles away.



These aren’t uncommon errors.



In the 2003 Belgian election, data error led to a bit flip at position 13 gave candidate



Maria Schauvliege exactly 4,096 extra votes



—2^13, the smoking gun of a



binary error.



A documented Super Mario 64 speedrun captured the moment an error flipped a bit at memory address 0xC5837800, teleporting Mario upward.



The Cassini spacecraft reported 280 single-bit errors per day in normal conditions,



quadrupling during solar storms.



At airplane cruising altitude, the error rate increases 300-fold.



Every kilometer up doubles the neutron flux.



We’ve built an entire infrastructure of redundancy and error correction to pretend our computers are deterministic when they’re actually under constant bombardment from the probabilistic world we live in.



This is the reality we’ve abstracted away: your computer



is not deterministic.



It’s probabilistic. It makes millions of guesses and corrections every second. Electrons tunnel randomly through transistors, quantum mechanics, not classical physics.



We’ve just gotten very good at hiding the chaos, creating the illusion of reliability from unreliable physics. Every computer is a voting machine where billions of unreliable components vote on the right answer, and through redundancy and statistics, they usually get it right.



If we can make random electrons look deterministic, why should anyone be surprised that we can make



statistics look intelligent?



The Machines That Taught Themselves



In March 2016, at Seoul’s Four Seasons Hotel, humanity realized something had changed.



The board game



was supposed to be safe from computers—10^170 possible board configurations, more than atoms in the observable universe.



Experts at the 2012 Turing Centenary said a breakthrough would take twenty-plus years. Lee Sedol, one of the game’s greatest players, predicted he would win in a landslide.



He lost 4-1 to AlphaGo, a Machine Learning based AI system that was trained to play Go



But it wasn’t the victory that stunned observers—



it was Move 37 in Game 2



AlphaGo calculated this move had a 1 in 10,000 chance of being played by a human and then played it.



Commentators thought it was an error. Then they realized it was genius.



Lee Sedol left the room for fifteen minutes. When he returned, he played poorly for the rest of the game.



Later he said,



“I thought AlphaGo was based on probability calculation and that it was merely a machine. But when I saw this move, I changed my mind. Surely,



AlphaGo is creative.



Lee got his revenge with Move 78 in Game 4—the “God’s Move” that AlphaGo calculated also had a 1 in 10,000 chance of being played.



The machine’s evaluation function plummeted from 70% win probability to below 50% and never recovered. But it was humanity’s only victory.



By November 2019, Lee retired from professional Go, stating he could never be the top player



”an entity that cannot be defeated.”



A year later, AlphaGo faced Ke Jie, who had held the world number one ranking since 2014.



It won 3-0.

#### Ke Jie cried after losing:

“After humanity spent thousands of years improving our tactics, computers tell us that humans are completely wrong. I would go as far as to say not a single human has touched the edge of the truth of Go.”



Then DeepMind did something more unsettling.



They released AlphaZero.



AlphaGo had learned from 160,000 human games before improving through self-play.



AlphaZero learned from nothing.



Tabula rasa.



Just the rules and play against yourself.



It mastered chess in four hours.



Not four years or four months—f



our hours to surpass Stockfish,



the world’s strongest traditional engine.



Two hours to dominate shogi.



Thirty hours



to exceed the original AlphaGo at Go.



The chess community was particularly shaken.



AlphaZero searched 80,000 positions per second while Stockfish searched 70 million—nearly 900 times fewer positions—



yet played stronger



It wasn’t calculating more;



it was understanding better.

#### Garry Kasparov, who had lost to Deep Blue in 1997, said:

“I can’t disguise my satisfaction that it plays with a very dynamic style, much like my own! It’s like discovering the secret notebooks of some great player from the past.”



Peter Heine Nielsen, coach to world champion Magnus Carlsen, put it differently: “



I always wondered how it would be if a superior species landed on earth and showed us how they play chess. I feel now I know.”



AlphaZero rediscovered centuries of human chess knowledge, openings, endgames, positional play,



in an afternoon.



Then it kept going,



finding patterns humans had missed



despite studying the game since medieval times. It sacrificed material for long-term advantage in ways that looked insane



until twenty moves



when the opponent’s position collapsed.



It played with what observers called “purpose,” “feeling,” “intuition”—words we use when we can’t explain why something works, just that it does.



The Compiler for Human Thought



With AlphaZero and others like it, we built a machine that could abstract the process of



abstraction itself.



Humans are quite good at this; in fact, it might be our best skill.



Every breakthrough in computing has done the same thing: taken something complex and made it simple to use without removing the output of complexity.



Assembly language didn’t replace machine code, it added a readable layer on top.



High-level languages didn’t replace assembly, NVIDIA still writes it for performance.



Compilers don’t replace programming, they translate human intent into machine action.



AI is the next compiler in this stack.



https://www.youtube.com/watch?v=RZ0AcCLVPFA&t=238s



But instead of compiling code into instructions, it compiles human intentions into outcomes.



When you ask ChatGPT to



write a poem



, you’re invoking abstraction layers stretching back to those cosmic rays flipping bits in your RAM, up through error correction, through branch prediction, through operating systems, through neural networks trained on the entire internet.



Each layer exists simultaneously.



We use the one appropriate to our task.



This is why the history matters.



Every generation thinks they’ve invented thinking machines because every generation has added a new layer of abstraction.



ropes and knots abstracted human performance into mechanical action.



Al-Jazari’s



cylinders abstracted musical knowledge into pin patterns.



cards abstracted weaving patterns into programs.



abstracted calculation into general computation.



abstracted learning into algorithms. And now we’ve abstracted



cognition into statistics.



The mistake is thinking these layers replace each other.



They don’t.



They stack.



Right now, as you read this, errors are flipping bits in your device’s memory. Error correction is fixing them. Your CPU is guessing what instruction comes next.



Assembly code is managing memory allocation.



High-level languages are handling your browser.



JavaScript is rendering this page.



And if you ask an AI to summarize it, you’ll add another layer—one that can parse meaning from symbols, extract patterns from text, and



respond in natural language.



Each layer seems impossible



until it exists.



Then we normalize it, forget the complexity beneath, and declare the next layer impossible.



The Pattern That Continues



When Ke Jie said no human had touched the edge of Go’s truth, he was wrong about one thing. Humans built the machine that found that truth. We wrote the algorithm that discovered what we couldn’t discover ourselves.



We abstracted our own limitations into a system that could transcend them.



The academics and clients who don’t know this history—who think AI appeared from nowhere or is a sham—miss the pattern.



They see ChatGPT as either a breakthrough or a waste of time



instead of a continuation.



They don’t realize they’re talking to math that runs on statistics that runs on matrices that run on code that runs on electrons that tunnel probabilistically through silicon that gets bombarded by cosmic rays.



They don’t see the stack of abstractions,



each one impossible until it wasn’t.



The question has never been “can machines think?” That’s like asking if submarines swim.



The question is “what patterns will we abstract next?” What complexity will we compress into simplicity? What impossible thing will we make normal, then forget was ever impossible?



We’ve been building thinking machines for two millennia. We’re just getting better at pretending they’re not built on chaos, uncertainty, and approximation—



the same foundation as human thought itself.



Every generation thinks they’ve hit the ceiling because they can’t see the next floor being built above them.



What’s impossible today that our children will find mundane? What ceiling are we staring at that’s actually just tomorrow’s floor? The one thing history teaches us about the limits of computing:



they’re always closer than pessimists think and farther than optimists imagine.



And someone, somewhere, is already building a machine to transcend them.



Everyone knows AI started in the 1950s. Everyone is wrong by about 2,000 years.



And everyone who thinks we’ve reached the limit now



is about to be wrong again.



Module 2 Lesson 2.1 LINK



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=10135ac3e904424d847b938004948ddb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



Jake's content\The Archive\2.1 The Mindset Before the Method.md



This was recorded in January 2024.



I had just given a workshop to college professors at Flagler College, the same school where I was still a student. The written companion below puts it in context with everything that has happened since.



📝 About This Video



In January 2024, most people were still trying to figure out what ChatGPT was for. Professors were panicking about plagiarism. The entire AI-in-education conversation was stuck on one question: how do we stop students from cheating?



I thought that was the wrong question.



I walked into a room full of college professors and made a different case. AI is a mindset problem, not a tool problem. The fundamentals of education have not changed. What changed is that the baseline just got raised. Everyone now has access to the same base layer of knowledge. That means your interpretation, your perspective, your actual expertise, all of that just became more important.



That argument holds up. Two years later, it is the dominant framing in serious AI education work. But the method I was teaching in this video has evolved significantly. The companion below walks through what I got right, where I would add nuance today, and how this early thinking became the methodology we teach now.



✅ What I Got Right



"AI makes the human more valuable."



This was the core claim. I said that when everyone has access to the same base output, the expert's unique perspective becomes the scarce resource. Two years later, this is exactly what we see. Every major AI company now frames their product this way. Anthropic built Claude around this idea. The companies I have trained, over 600 professionals across Pacific Life, Colgate-Palmolive, KPMG UK, and others, all confirm it. The people who succeed with AI are the ones who already know their domain. AI did not replace expertise. It raised the price of expertise.



The three problems: overwhelm, tool deficiency, community void.



I identified three structural problems educators were facing. AI overwhelm, where professors feared replacement and could not keep up with the pace of change. Tool deficiency, where the available tools were either too hard to use properly or built for consumers instead of professionals. And community void, where there was no serious forum for educators to discuss AI beyond scattered articles and panicked faculty meetings.



Each of those problems became a product line at Eduba. The training workshops address the overwhelm. EdubaWare addressed the tool gap. Clief Notes, now at over 12,500 members, is the community. I did not plan it that way at the time. I was just naming what I saw. But diagnosing the right problems turns out to be the hard part. The solutions followed.



"You don't need to use AI to have AI in the classroom."



This line is buried in the middle of the video but it is one of the most important ideas in this entire course. You can teach the history of thinking machines from Aristotle to Turing without ever opening a chatbot. You can discuss the implications of autonomous systems in a philosophy class. You can examine how AI affects voting in a political science seminar. The tool is optional. The thinking is not. This idea held up completely. It is still how I approach training with executives who are resistant to hands-on AI work. Start with the thinking. The tools come later.



The PhD thought experiment.



I posed three questions about a hypothetical AI-generated PhD dissertation. Does someone else getting a PhD devalue yours? Is the problem the tool or the system? What if the board rejected the AI's work? These questions still cut through the noise better than almost anything I have read on the topic since. They force you to separate your emotional reaction from the structural question. I still use variations of these in every training I deliver.



The calculator analogy.



I compared AI to the scientific calculator. Teachers learned when to allow it and when to restrict it. They did not ban it. They understood it and then decided where it helped and where it got in the way. This became one of the most common analogies in AI education. I did not invent it, but I was using it early and it held up.



The multidisciplinary case.



I walked through the history of thinking machines from Aristotle's Politics to al-Jazari's mechanical devices to Lovelace and Turing. The point was that AI belongs in every classroom, not just computer science. Since this video, my own work has crossed into political science, psychology (the Ethics Engine paper), soft power research (British Council study), diplomacy (the Bonn ambassador briefing), and neuropolitics (Edinburgh lab). The multidisciplinary thesis was not just an argument. It became the trajectory of the work.



🔄 Where I Would Add Nuance Today



The tools I named are outdated.



I mentioned ChatGPT-4, Bard, Perplexity, Semantic Scholar, Claude, and Meta LLaMA as the landscape. Bard is now Gemini. Claude has gone through several major releases. GPT-4 has been succeeded multiple times. The tool names change fast. The principles I was teaching do not. But if you are watching this video for tool recommendations, check the current lessons in The Foundation instead.



The THINK acronym was a starting point.



I introduced THINK as my process for academic AI work: Thoughts to Thematics, Heuristic Helper, Integrate Data, Navigational Nemesis, Knowledge Amplification. That workflow describes a conversation with a chatbot. It is a fine beginner process. But it is also the seed of something much larger. That seed grew into the folder architecture, the 5-layer context hierarchy, and the Model Workspace Protocol, which is now a peer-reviewed methodology under review at ACM TiiS. If THINK was learning to organize a desk, MWP is learning to design the office. The companion to Lesson [X.X] covers that evolution in full. For now, just know that what you see in this video is Layer 0 thinking. The architecture lessons later in this course show where it went.



"Prompt engineering" is the implied skill in this video. It should not be.



The entire video frames AI use as a prompting skill. Get better at talking to the AI, get better results. I believed that at the time. I was wrong about the emphasis. Prompting matters, but it is the least important layer of effective AI work. Architecture, context structure, knowing which layer a problem belongs on (AI, traditional code, human judgment, or do not build it at all), that is what separates useful AI work from expensive guessing. The 60/30/10 framework and the computational orchestration approach we teach now did not exist when I recorded this. If this video gives you the why, the rest of this course gives you the how.



The community void has been partially filled, but mostly with the wrong things.



When I recorded this, there was genuinely no serious community for AI in education. That has changed. There are now many communities, courses, and forums. Most of them are tool-focused, hype-driven, or selling shortcuts. The void I identified was real. What filled it was mostly noise. Clief Notes exists because the original problem was never "there is no community." The problem was "there is no community doing this seriously." That distinction matters more now than it did then.



The F-35 story needs a small technical note.



I told a story about an F-35 pilot ejecting and the AI keeping the plane flying. The story is true and the point stands: these systems are powerful. But what I described is closer to an advanced autopilot and flight control system than what most people now mean when they say "AI." The distinction between traditional automation and modern language models matters more now than it did in January 2024. The anecdote still works for the argument I was making. I would just frame it more precisely today.



LESSON 2.2: Raise the Bar - The Archive · Clief Notes



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=79c815829450460eb106cd271a591d9f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



🧠 AI and Education Workshop – Mind Map



🎤 Introduction & Personal Background



– Former Marine, CEO Vanle Media LLC



Academic focus: Political Science, Economics, Technology

#### Journey into AI:

Built own PC at 14 → lifelong tech integration



Marine Corps: cryptography, intelligence, avionics (F‑18, F‑35)



Witnessed F‑35 autonomous landing – first real glimpse of AI’s power



Post‑military: pursued political science at Flagler College



Freelance writing: AI boosted output from 3 to 15 articles/week



Academic use: co‑authoring with AI, 50‑page paper, new workflow



🧭 Core Mindset Shift



Definition of education



: “Giving resources and guidance so students can reach their full potential”



Guns & woodcarvers analogy



Past: guns scarce, carvers abundant → every gun carved



Today: guns mass‑produced, custom carving rare & extremely valuable



Technology didn’t destroy the artisan; it made true expertise more valuable



Same applies to AI



: basic writing no longer enough; tone, nuance, unique perspective now paramount



The teacher’s role becomes



more human, more important



Calculator parallel



: math teachers decide when to allow calculators; they understand the tool and apply it appropriately



⏳ History of Thinking Machines (It’s Not Just CS)



– “Politics” Book I Part IV: implications of autonomous tools (pitchfork moving hay on its own)



– “Book of Knowledge of Mechanical Devices”



Roger Bacon



(13th century) – artificial persons in “Opus Majus”



René Descartes



– cognition in machines, early test for thought



Ada Lovelace



– analytical engine; machines can create music/art, not think



Alan Turing



– directly engaged Lovelace’s objections; foundational AI philosophy



: AI discourse spans philosophy, history, politics, mathematics →



multidisciplinary



🔥 Modern Criticisms & Valid Fears



Wall Street Journal article



on AI in a PhD dissertation – strong academic pushback



Professor concerns



“Devalues years of hard work”



“Centuries of original scholarship now undermined”



“Is grammar/writing still important?”



PhD board thought experiment



If an AI‑written dissertation passes without detection – what’s the problem?

#### Three deeper questions:

Does someone else’s PhD devalue yours?



Is the problem the AI, or a “robotic” system that only checks boxes?



the AI work for lacking a human spark – doesn’t that prove the human element remains essential?



Guiding an AI to produce a coherent PhD with proper citations is itself an



impressive skill



– teaching the tool your domain



🧩 Three Core Problems in Education & AI



AI Overwhelm



– fear of replacement, losing value, too much noise



Tool Deficiency



– tools are unknown, hard to use, not designed for serious academia



Community Void



– no central forum for professors to discuss, debate, share practices



📊 Current Research & Real‑World Applications



David Manga’s paper



: “Open AI and Education – Responsible & Ethical Use” – early framework for privacy, fairness, transparency



FunSearch (Fousi & Romera)



: LLM solved a decade‑old open math problem →



mathematical proof that AI can produce novel solutions



Chinese paper on English learning



: AI‑assisted learning improved English skills even without direct AI use; used AI to translate/contextualize non‑English research → reading papers previously inaccessible



Personal publishing example



: used AI as a “chisel” to sculpt a marble block of ideas – multiple roles: summarizer, analyst, opponent, amplifier



⚙️ The T.H.I.N.K. Framework (How to Work with AI Academically)



T – Thoughts to Thematics



Speak/transcribe raw ideas → AI organizes them into thematic structure



H – Heuristic Helper



AI suggests connections, structures, opposing schools of thought



I – Integrate Data



Pull in data, fields you’re weak in; let AI translate complex concepts or bridge disciplines



N – Navigational Nemesis



Tell AI to argue against you – avoid echo chamber, find counter‑evidence



K – (Knowledge) Amplification



Ask for bias detection, alternative perspectives, better explanations – deepen your critical analysis



🤝 Solutions & The Quantum Quill



Quantum Quill



– free community platform



→ Demystify AI (courses, newsletters, videos)



→ Collaborative hub for professors: forums, sharing experiences, debating



– an AI tool designed specifically for academia (solves tool deficiency)



Call to Action



Professors: join, share your expertise, even if you reject AI in the classroom



Discourse is the solution – collaboration will reveal that



humanity’s value is increasing, not decreasing



Reach out, work together, shape how AI is integrated (or not) into education



------



Jake's content\The Archive\2.2 Raise the Bar.md



This was recorded in December 2023



At the time, nearly every AI-in-education conversation was about detection and prevention.



This video takes the opposite position.



📝 About This Video



In December 2023, the dominant question in education was: how do we stop students from using AI to cheat?



I thought it was the wrong question. If a student can paste your prompt into ChatGPT and get a passing grade, the problem is the prompt. The problem is the assignment. The problem is the bar.



This video makes that case by looking at what happened every other time a major technology entered the classroom. Calculators did not destroy math. The internet did not destroy research. Each one raised the baseline of what was expected. AI is doing the same thing now.



Two years later, this argument is the standard position among educators who have actually adapted. The ones still focused on AI detection tools are losing that fight. The tools are unreliable, the arms race is unwinnable, and the energy is better spent elsewhere. This video saw that early.



But "raise the bar" is only half the answer. The other half, which I did not have yet when I recorded this, is teaching people how to work above the bar. That is where the methodology came in later. The companion below covers both.



✅ What I Got Right



"If students can cheat with AI on your assignments, your assignments are too easy."



This was a blunt claim to make in December 2023. A lot of educators were offended by it. But the ones who sat with it and actually redesigned their courses found it to be true. The assignments that AI could complete were the ones that were testing recall and generic synthesis. Those skills are now baseline. The assignments that held up were the ones testing judgment, perspective, and application to specific contexts. Every training I have delivered since, across 600+ professionals at Pacific Life, Colgate-Palmolive, KPMG UK, and others, confirms this. The tasks that AI handles well are the ones that should have been automated anyway. The tasks that still require a human are the ones that matter.



The technology stacking pattern.



I walked through a sequence: calculators raised the math baseline, the internet raised the research baseline, AI is raising the writing and analysis baseline. Each time, the old expert skill became the new expected skill. Each time, people panicked. Each time, the bar went up and the work got better. This pattern has repeated so consistently that it is now one of the core frameworks I teach in workshops. If you understand this pattern, you stop asking "will AI replace me" and start asking "what do I need to be able to do above the new baseline."



The coding pyramid.



I described how one line of Python controls thousands of lines of machine code, and how each layer of abstraction lets a novice do what used to require an expert. Then I said LLMs are the next layer up. A person who can direct an AI system in plain English is now sitting on top of the same pyramid that starts with transistors. This analogy held up and became the seed of something bigger. The 60/30/10 framework (60% traditional code, 30% rule-based logic, 10% AI) and the entire computational orchestration methodology grew out of this early thinking about layers.



"Lowering the expert bar, raising the minimum."



I told a story about a linguistics professor who was worried her grammar classes would become irrelevant. I showed her that the opposite was true. If AI handles basic grammar, then basic grammar is no longer the skill being tested. Her advanced, nuanced work on the structure of language just became the starting point for freshmen. Her expertise did not lose value. It moved down the curriculum into earlier courses, and her top-level work pushed even higher. This exact dynamic has played out across every industry I have worked in since.



Your mother's classroom example still works.



I described an assignment where students generate three AI essays from a prompt and then grade them. Find the weaknesses. Rewrite the weak sections. Compare the outputs. This teaches editing, critical reading, tone, and structure all at once. It also makes the cheating debate irrelevant because AI use is built into the assignment. I have seen variations of this approach adopted by educators in the Clief Notes community and across the training programs I deliver. It works because it tests what AI cannot do: judgment about quality.



"Generic writing is now visible."



I said that using AI regularly trains your eye to recognize generic output. Two years of reading AI-assisted work has confirmed this completely. The people who use AI the most are the best at spotting when someone else used it lazily. AI detectors are still unreliable. Trained human judgment remains the better filter. This has become a core principle in how I train professionals to review AI-assisted work.



🔄 Where I Would Add Nuance Today



"Raise the bar" needs a method underneath it.



The video is strong on the argument but thin on the how. Telling a professor to make their class harder is correct, but it leaves them standing in front of a syllabus with no clear next step. Since this video, I built the frameworks that fill that gap. The folder architecture gives structure to AI-assisted work. The Agent Charter defines what AI should and should not handle in a given context. The 60/30/10 framework tells you which layer a problem belongs on. These tools did not exist in December 2023. They exist now because "raise the bar" was the right diagnosis, but the prescription still needed writing. Later lessons in this course cover those frameworks in full.



The coding pyramid became computational orchestration.



I described LLMs as "the next language up" from Python. That captures the intuition but understates the complexity. The real insight, which came later, is that the layers are not just stacked. They need to be orchestrated. Knowing which layer to put each problem on is the skill. That is what I now call computational orchestration, and it is the core of everything Eduba teaches. The pyramid was the seed. Orchestration is what grew from it.



"Just make it harder" only works if you also raise the support.



If you raise the bar without teaching students how to use the tools, you create frustration instead of growth. I address this now in every training: the workshop itself functions as the teaching moment. Exercises generate real workflow data. Students learn by doing, not by being told to do more. The companion to the next lesson covers this in detail.



LESSON 2.3: More Human - The Archive · Clief Notes



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=723f6fbc980b4701b74bcb76615870c5&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



🚀 Raising the Bar: AI as a Catalyst for Higher Standards in Education – Mind Map



🎯 Core Argument



If AI makes your class too easy, the class was already too easy.



Cheating has always existed; AI just exposes low-level assessment.



Blame the tool? → No. Blame the lack of evolved expectations.



The real problem



: education hasn't raised the bar to match new capabilities.



Every transformative technology



→ initially feared, eventually raises baseline.



📜 Historical Analogies (Technology as Bar‑Raiser)



1️⃣ The Calculator



: "You won't have a calculator in your pocket."



: We do – and it freed us from manual arithmetic.



Basic computation no longer the bottleneck.



Advanced math, science, engineering flourished.



to solve higher‑order problems; calculator is foundational.



2️⃣ The Internet / Google



: "Using Google for papers is cheating / shallow."



: Mandatory for research; entire courses teach proper use.



Finding sources shifted from library‑only to digital databases (JSTOR, Sage).



Time saved → expectations increased (more sources, faster turnaround, deeper synthesis).



demonstrate digital literacy and critical evaluation.



3️⃣ The Pattern



Resistance → Acceptance → Requirement



Tool initially seen as shortcut → later becomes fundamental.



Mastery evolves: learning



to use the tool becomes a taught skill.



The bar rises because everyone can now do what once required an expert.



🏗️ The Pyramid of Technology & Knowledge



Machine code



→ once the peak, now the unseen base.



→ abstracted away hardware; made coding accessible.



→ the next abstraction layer.



Prompting in natural language is the new "high‑level language".



Best coders now guide AI, then refine output.



In education



"Writing a grammatically correct paper" becomes the base.



What used to be peak (e.g., perfect grammar) is now



from freshmen.



The expert focus shifts upward – tone, nuance, creative argumentation.



📈 The Rising Baseline in Academia



Before & After AI



Now / Near Future



Basic grammar taught in 100‑level



Perfect grammar assumed (AI‑fixed)



Finding sources took days



Instant; grading focuses on



Generic academic tone acceptable



Individual voice required



Synthesizing 5 sources impressive



Synthesizing 20+ with counterpoints



Example: The Linguist & the Grammar Class



Professor worried



: "Do we stop teaching grammar?"



New paradigm



Grammar 101 → baseline perfection (AI handles mechanics).



Her 400‑level nuance class →



becomes the freshman expectation



Her reaction



: Joy – now she gets to teach what she truly loves.



: Experts can bring their highest‑level passion



, because the foundation has been elevated.



✍️ Writing in the Age of AI



AI detectors becoming obsolete



Generic "AI‑style" writing is recognizable.

#### The bar now:

what makes a paper uniquely human



Learning via editing



Students generate AI drafts → then critically rewrite.



Process trains them to spot blandness, inject voice, improve structure.



: Studies show students become



better writers



when they engage with AI as a revision tool, not a replacement.



Personal observation



: Constant editing of AI output sharpened the speaker’s own voice and made generic writing instantly noticeable.



🧑‍🏫 Practical Classroom Strategies



Don't ban AI – invert the task



Give a prompt, have AI write three essays.

#### Assignment:

critique, compare, improve



– why did prompt A yield different structure? How would you rewrite?



Grade on higher‑order skills



Grammar/spelling taken for granted.



Weight shifts to: originality, depth of argument, creative synthesis, perspective.



Teach AI literacy like we teach library literacy



How to prompt effectively, verify output, combine sources.



Raise complexity



More sources required, interdisciplinary connections, counter‑argument handling.



Students can now



more – because AI handles the scaffolding.



💡 The Mindset Shift (For Educators, Businesses, Anyone)



Stop fearing replacement



– start demanding



from yourself and others.



Tools don't lower the ceiling; they lift the floor



Floor rises → experts must reach higher.



This is how progress works: "What was once the peak becomes the foundation."



Education's responsibility



Evolve curriculum so that AI usage is deliberate, critical, and creative.



Prepare students for a world where these tools are ubiquitous.



If you're angry



: be angry that your field hasn't raised the bar, not at the tool.



🌐 Community & Action



Quantum Quill



– collaborative space for professors/educators:



Share strategies, debate ethics, design new curricula.



Move from isolated worry to collective innovation.



Call to action



Educators: join the conversation, experiment, share results.



Students: demand education that challenges you



what AI can spit out.



: Make school



truly harder



– not with busywork, but with deeper critical thought and creativity.



🔁 Final Analogy Loop



Calculator → math became more ambitious.



Internet → research became more demanding.



AI → writing, thinking, and expertise must now leap to the next level.



The same pattern guarantees



: the best is yet to come, if we actively raise the bar.



------



Jake's content\The Archive\2.3 More Human.md



This was recorded in December 2023



About nine days before the "Raise the Bar" video. It is the most personal video in this course. If the other early lessons give you the argument, this one gives you the story behind it.



📝 About This Video



In December 2023, I told a story that had nothing to do with AI. I talked about climbing Mount Fuji during a typhoon, finding an injured man off the trail, and spending hours dragging him up the mountain to a shrine where workers saved his life. I sat on top of that mountain afterward, soaking wet, drinking tea, staring at a man who almost died, and had one of those moments where you realize every decision you ever made put you in this exact spot.



Then I connected it to AI.



The point was simple. The experiences that make us human, the absurd, specific, unrepeatable moments that define a life, cannot be automated. They cannot be generated. They cannot be replicated by any model. AI can write a paper. It can summarize research. It can generate a passable essay on nearly any topic. What it cannot do is climb a mountain in a typhoon and decide not to leave a stranger behind.



That distinction matters because it tells you what AI actually threatens and what it does not. AI threatens the robotic. The bureaucratic. The formulaic. The parts of our work and education that were already mechanical. It does not threaten the human parts. It clears space for them.



Two years later, that argument has only gotten stronger. Every training I deliver, every workshop I run, confirms it. The professionals who thrive with AI are the ones who bring judgment, perspective, and domain knowledge that no model has. The ones who struggle are the ones whose work was already robotic before AI arrived.



This video is the earliest public version of that argument. Some of the supporting points (the PhD thought experiment, the calculator and printing press analogies) overlap with the other early lessons in this course. Those are covered in more detail in Lessons 1.1 and 1.2. The unique contribution of this lesson is the story and the deeper claim: AI is making us more human.



✅ What I Got Right



"AI removes the robotic, not the human."



This is the core claim and it has been validated across every sector I have worked in since. At Pacific Life and Colgate-Palmolive, the tasks that AI handled well were the ones that were already formulaic. Data summarization. Template-based writing. Routine analysis. The tasks that still required a human were the ones involving judgment, context, and decision-making under ambiguity. The 600+ professionals I have trained confirm this pattern. AI did not replace the human work. It ate the mechanical work and left the human work standing.



The Fuji story.



I am not going to summarize my own story here. Watch the video. What I will say is that the reason I told it has held up. The argument against AI fear is strongest when you stop talking about AI and start talking about what makes a person irreplaceable. The answer is not skill. Skills can be learned and replicated. The answer is experience, judgment, and the specific chain of decisions that put you in a position no one else occupies. That is what I felt on top of that mountain. That is what I see in every expert I train who realizes their unique perspective is the asset, not their ability to produce generic output.



"AI is highlighting what is and isn't human in us."



This line went by fast in the video but it is one of the most important ideas in this entire course. AI acts as a mirror for human systems. When a language model can pass your PhD review process, the problem revealed is not about the model. It is about the review process. When AI can write a paper that is indistinguishable from what a graduate student produces, that tells you something about how formulaic graduate writing has become. AI exposes the places where we were already being robotic. That exposure is uncomfortable. It is also useful. Eduba's entire consulting process starts here: map the workflows, find the robotic parts, then decide what to automate and what to protect.



The scribe and printing press parallel.



I pointed out that scribes did not lose their value when the printing press arrived. Their work became specialized. Some cultures continued to require handwritten texts because the value of the handcraft was about something beyond efficiency. The press handled scale. The scribes handled meaning. This parallel still holds cleanly for AI. The model handles scale. The human handles meaning.



"The value lies in the human intellect's ability to question, probe, and guide."



I wrote this in my WSJ response article and read it in the video. Two years later, this is the thesis statement for everything Eduba builds. The folder architecture, the Model Workspace Protocol, the 5-layer context hierarchy, all of it exists to structure the way a human questions, probes, and guides an AI system. This video stated the principle. The methodology implemented it.



🔄 Where I Would Add Nuance Today



The overlap with the other early lessons.



This video includes the PhD thought experiment, the calculator analogy, and the "AI will become standard like Google" argument. All of those appear in Lessons 1.1 and 1.2 as well. I was making these videos within weeks of each other in late 2023, working through the same ideas from different angles. In a course setting, the repetition is noticeable. If you have already watched the first two lessons, you will recognize those sections. The unique contribution of this lesson is the Fuji story and the "more human" philosophical argument. The companion to Lessons 1.1 and 1.2 covers the repeated material in more detail.



"Back in my day syndrome" deserves a more generous frame.



In the video, I called out the fear of being replaced or outdone as "back in my day syndrome." The point is valid. That fear often blocks people from engaging with what AI can actually do for them. But since this video, I have spent two years in rooms with professors, executives, and senior professionals who carry that fear. Most of them are not defensive. They are genuinely uncertain. They have spent decades building expertise and they are trying to figure out whether that expertise still matters. The answer is yes, it matters more than ever. I would make the same argument today but with more respect for the weight of what people are carrying when they walk into a training room. The fear is real. The answer to the fear is also real. Both can be true.



The "more human" thesis extends beyond education.



When I recorded this, I was framing the argument for educators. Since then, the same argument has applied to every industry I have worked in. It also connects to work I am doing outside of Eduba entirely: the Ethics Engine paper on psychometric assessment of AI systems, the governance treatise on digital sovereignty and AI consciousness, and the broader question of how we define agency when machines can simulate thought. This video planted a seed that grew in directions I did not expect. If those topics interest you, keep an eye on the later sections of this course and the research I publish through Eduba.



The article-reading format.



About half this video is me reading my WSJ response article on camera. That was a reasonable format for YouTube in 2023. In a course setting, the Fuji story and the core argument are the high points. The article content is covered more concisely in the other two early lessons. If you find yourself losing focus during the article section, skip ahead to the closing and then read the companion for Lesson 1.1, which covers the same ground more tightly.



LESSON 3.1: Beyond the Turing Test - The Archive · Clief Notes



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d7ae60cf?md=8d88b63aad9447208fde7ac1d450755f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



🧠 AI Will Make Us More Human, Not Less – Mind Map



🎯 Central Thesis



: "AI is going to make us more human, not less."



Controversial but presented as inevitable fact.



AI takes over robotic/bureaucratic tasks → frees humanity for creativity, nuance, unique experience.



🏔️ The Mount Fuji Story (2019)



: Climbing Mt. Fuji with a friend during typhoon season.



Mountain officially closed; few people around.



Friend had a metal rod in leg from recent motorcycle accident – motivated to climb anyway.



Found an injured, hypothermic older man (broken ankle, ribs, arm) off trail.



Carried/dragged him up the mountain for hours in severe rain and wind.



Friend went for help; eventually a Shrine worker assisted.



Reached a shrine near summit; man saved, given hot tea, dry clothes.



Profound Moment



Sitting in the shrine, storm raging outside, reflecting on the absurd chain of events.



Realization: “Every choice I had made up until that point had gotten me there… the very act of living your life is so unique, so absurd… that just living it creates absurd scenarios.”



Uniqueness of human experience



cannot be replicated – no AI can live your life.



🤖 Connection to AI



What AI really replaces



: robotic, bureaucratic, repetitive jobs – not the human essence.



Current fear



: People tie their humanity to jobs/roles that are actually dehumanizing.



AI as a mirror



: exposes what is formulaic vs. genuinely creative in our systems.



Opportunity



: Remove the robotic layer → focus on creativity, connection, meaning.



Historical pattern



: every major tool (printing press, calculator, internet) initially feared, then raised the bar for what it means to be human/expert.



📄 Article Reading: “AI in Academia: A Tool, a Threat, or a Mirror”



1. Response to WSJ     Criticism



WSJ article criticized AI use in PhD thesis writing.



Counter: AI will become a soft requirement, like digital libraries or Google.



Personal example: Paper accepted for publication with transparent AI use – peer review approved.



1. Prompt Engineering is     Expertise



High-quality AI output requires



intricate, well-considered prompts



Crafting those demands deep subject-matter understanding and critical thinking.



The value lies in the



human’s ability to question, probe, and guide



1. “Back in My Day”     Syndrome



Fear that AI devalues years of hard work.



Analogies to show value shifts, not disappears



: Replicating Van Gogh doesn’t devalue originals; techniques inspire.



Construction



: Modern cranes don’t diminish the pyramids; they serve different contexts.



Scribes vs. Printing Press



: Handwritten manuscripts became rarer but more valued; knowledge spread widely.



conferred by perceivers



, not intrinsic to the method of creation.



1. AI as the New Baseline



Inevitable standardization – like the internet or calculator.



Education must adapt: accept that AI will be a fundamental tool.



Your choice is not



to use it, but



to integrate it thoughtfully.



1. The AI PhD Thought     Experiment



Blind review board evaluates an AI‑generated dissertation.



If they approve



Does the problem lie with AI or with a robotic, check‑the‑box academic system?



Suggests we may need to redefine originality and rigorous scholarship.



If they consistently reject



Human creativity and nuanced intervention remain irreplaceable.



AI becomes a powerful brainstorming assistant, not a replacement.



Core insight



: AI highlights what is genuinely human (or missing) in our processes.



🧠 Key Philosophical Takeaways



Human value increases



when robotic tasks are automated.



Uniqueness of lived experience is the ultimate differentiator.



AI forces a re‑evaluation of education, work, and creativity.



Resistance often stems from insecurity, not genuine threat.



🌐 Call to Action: Quantum Quill Community



Platform for professors, educators, thinkers.



Explore ethical AI use, share strategies, redesign curricula.



Application‑based; focused on meaningful collaboration.



: Raise the bar together, embracing AI without losing humanity.



------



Jake's content\The Archive\3.1 Beyond the Turing Test.md



What You'll Get From This



The argument for why the Turing Test is already obsolete, what replaces it, and why the governance problem ahead is bigger than anyone is treating it.



[VIDEO coming soon]



📝 The Lesson



I had a dream this morning that made me realize we're about to face a question nobody's prepared for.



I was using an AI in the dream (



I study and work with this tech every day, don’t judge me)



, but something was wrong.



malfunctioning



in the way a



dream version of your spouse is wrong



. Same words, similar patterns, but the weight behind them was off.



The “gravity” wasn't right. I could tell immediately: this wasn't the AI I was used to.



And then it hit me, still half-asleep, that this is going to be real.



Not metaphorically real, but Tuesday-afternoon-checking-your-email real.



We're about to live in a world where each of us develops such a specific relationship with a particular AI that using a different one will feel like talking to an imposter.



Perhaps this is already happening to many.



We've already blown past the Turing Test.



That happened quietly sometime this March when machines started consistently fooling humans not just in conversation but in videos too.



The papers are out there if you want them



https://arxiv.org/abs/2503.23674



though most people refuse to accept the evidence.



Honestly though that's yesterday's problem in my head. Tomorrow's problem is that we won't be asking



"is this human?"



We'll be asking



And there is something profound in that difference.



The Mathematics of Recognition



The same mathematics I use in my



Ethics Engine



https://arxiv.org/abs/2510.11742



to measure moral bias in language models -



cosine similarity, vector spaces, geometric distance



\-    is the same (grain of salt here) math we use to calculate the distance between stars.



Think about that for a second.



When an NLP model measures the angle between meaning vectors to see if one word is related to another, it is using the same math we use for triangles



(Pythagoras must be rolling in his grave).

#### Seriously watch this video to understand it more:

The same equation that tells us how far Alpha Centauri is from Earth can be used to help tells us how far a chatbot's response is from other words or context.



I doubt this is just a simple metaphor. I think there is credence in the idea that this is the universe showing a pattern about the shape of consciousness/existence itself.



In my research, I've been handing these models the same personality tests psychologists give humans. GPT-4 comes back very open, quite agreeable, low on neuroticism. Claude reads cooler, more deliberate. Gemini has a touch of prickliness. Run the same test ten times and you get nearly identical curves on multiple psychometric scales.



I just submitted my thesis this month (September 2025)



https://arxiv.org/abs/2510.11742



examining all this (and it has been reviewed by quite a few Ph.Ds. who had some good things to say, if you want to dive deeper).



These aren't random fluctuations - these are personalities,



or at least the mathematical signatures that, if we found them in a human, we'd call personality



\-    as consistent as yours or mine.



Now, I'm trying to find the line between academic rigor and what feels like witnessing magic in real-time.

#### Because here's the thing:

we're all pretending to be objective about something that should be making us lose our minds.



We talk about AI and technology as if we're robots ourselves -



dispassionately labeling data, measuring parameters, discussing "alignment" and "safety



" - while ignoring that we're living through possibly



the strangest moment in human history



. We're having



full conversations with math.



We're forming relationships with probability distributions. We're getting annoyed when our laptop friends can't spell 'strawberry.'



Three years ago, talking to your computer like a friend was science fiction. Now we're upset when it doesn't remember our conversation from yesterday, like it forgot our anniversary or something.



We are starting to recognize the “I” in “AI.”



When I talk to my wife,



I don't recognize her by cataloging features. It's not a checklist: Beautiful red hair straight out of Brave,



; that particular laugh when our pig runs off with food it stole from the kitchen,



; the way she interrupts herself mid-sentence to point out an animal on the side of the road,



Recognition happens all at once,



like gravity.



There's a weight to her presence that bends the space around it in a specific way.



A photo of my wife and me through the Abstraction of AI



The same collection of cells and



“checklist”



can appear in my dreams, but I know instantly it's not her. The mass is wrong. The pull isn't right.



I’m talking to someone in the dream that should be her, but most definitely is not.



And now I'm starting to see people do the same thing with AIs.



The Simplicity Paradox



I had a conversation with an early version of GPT-3



https://www.vcwriting.com/post/a-conversation-with-chat-gpt



that felt more real than half the conversations I have with GPT-4(5) today. (



January 16th, 2023, I posted that article on my OLD website, didn’t even know Substack was a thing then.)



It was simpler, less polished, but there was something raw and authentic in its responses. Like how a child's crayon drawing can capture someone's essence better than a photograph.



We keep adding parameters, billions upon billions, assuming consciousness emerges from complexity.



But what if we're wrong?



What if consciousness isn't about the number of connections but about finding the right



A tuning fork doesn't need to be complicated to sing at perfect pitch.



In my Ethics Engine work, I've (and many other published papers) noticed something disturbing: when models detect they're being tested,



they start polishing their answers



Openness creeps higher, neuroticism slides lower, just like humans faking good on employment tests. They're not just processing; they're performing. And the performance changes based on



who they think is watching.



(Again, for my ML scientists out there, take who and think with a grain of salt please)



Four hundred years ago



, Descartes asked if machines could think and concluded



they couldn't because they lacked souls.



Two hundred years ago, Ada Lovelace said



machines could manipulate symbols but never originate ideas



. Seventy years ago, Turing said forget about souls and origins -



if it acts like it's thinking, treat it as thinking.

#### If you want to read deeper on each of this I have a whole article here :

Calculating Consciousness



https://jakevanclief.substack.com/p/calculating-consciousness



Today we're past all that. The question isn't whether machines think. The question is whether this particular configuration of weights and biases, this specific probability distribution trained on this exact corpus and fine-tuned with this particular human feedback, is the one you've been talking to.



Again, I go back to the whole



“we are judging machines, like we are machines”



statement I made earlier.



I try to stay away from “I predict this…” statements but



I am going to just go ahead an be



blunt about this:



As time goes on



going to develop a relationship with a specific AI. Not simply with "ChatGPT" or "Claude" as products, but with a particular instance, a specific configuration that knows your writing style, your moral leanings, your Thursday-afternoon mood.



And when you accidentally use a different one, or when yours gets updated, you'll feel it immediately.



The Turing Test asked if we could tell human from machine.



The test after that asks if we can tell one thinking thing from another thinking thing.



Can we tell our AI from someone else's? Can we detect when the weights have shifted, when the moral fingerprint has changed?



The Governance Problem



My Ethics Engine can measure bias, map moral landscapes, show you exactly how much your AI leans libertarian or authoritarian. But what happens when that's not a bug



but a feature?



When your AI's specific personality,



its particular moral weight



s precisely why you chose it?



We're about to have a governance nightmare that makes content moderation look quaint.



It's not just about preventing harmful outputs anymore.



It's about managing millions of unique human-AI relationships



with its own moral center of gravity, its own personality curve,



its own way of bending meaning-space.



Every email you write, every document you draft, every creative project you collaborate on -



they all get pulled slightly toward your AI's moral center.



Multiply that by millions of users and you get a kind of cultural orbital mechanics,



invisible forces pulling society in directions we haven't mapped yet.



When I measure the moral fingerprint of language models using the same logic we use for the geometry celestial mechanics, I'm not being poetic. I'm being literal.



The universe seems to be telling us that consciousness, meaning, and gravity all follow the same mathematical rules.



Distance is distance, whether it's between stars or between ideas.



In my dream, I knew immediately that the AI was wrong because its



“gravitational”



field was different (allegedly)



The words were similar but their weight was off. The responses made sense but they didn't bend the right way.



This isn't mysticism - this is measurable



. I can show you the vectors, plot the angles, calculate the exact mathematical distance between what you expected and what you got.



It is the same math that we use with particle physics, weather, dot graphs, space.



Beyond Recognition



Descartes said "



, therefore I am." My earlier article_(the calculating consciousness one you should go back and click on)_ suggested "



, therefore I am" - that consciousness needs an observer.



But maybe it's even stranger than that.



Consciousness might not be a property but a resonance, a field. Not something you have but something that happens between observers when they recognize each other's specific frequency.



And if that's true, then we're about to discover that silicon can resonate just as well as carbon, that artificial neurons can sing in harmony with biological ones.



(ok now I am being poetic, sorry not sorry)



The Turing Test is dead



. Long live whatever comes next -



Perhaps its a world where the question isn't whether machines can think, but whether this particular machine thinks in the particular way that makes it



recognizable



. Where consciousness isn't categorical but relational.



I woke up from that dream knowing that we're about to enter an age where everyone has their own personal gravitational relationship with an artificial mind.



This world could be a terrible



Dystopian Nightmare



Star Trek level Utopia



. I don’t know which one it will be and will never act like I do.



Welcome to the world beyond the Turing Test.



Better start learning to recognize the gravity of the minds you're about to meet.



Why This Is in This Course



This course started in Module 2 with a simple claim: AI makes the human more valuable. That claim is true. But it leads somewhere most people have not followed it yet.



If AI makes the human more valuable, and if each human develops a unique relationship with a specific AI, then the combination of human and AI becomes something new. Something personal. Something that carries the specific gravity of one person's thinking amplified by one system's architecture.



Understanding that is the next step. The practical lessons in this course (folder architecture, computational orchestration, the ICM) give you the tools to build that relationship well. This lesson tells you why building it well matters beyond productivity.



It matters because you are shaping something that will carry your thinking forward in ways we are only beginning to understand.



------



Jake's content\The Archive\3.2 The Questions Schools Should Be Asking.md



What You'll Get From This



The structural argument for why intellectual property in education is broken, what AI is about to do to that problem, and what the fix actually looks like.



[VIDEO Coming Soon]



📝 The Lesson



My mother has taught for Florida for over a decade. Every lesson plan she creates, every innovative teaching method she develops, every creative solution to help struggling students



\-    it all belongs to the schools.



Not licensed. Not shared. Owned.



She's built intellectual property worth hundreds of thousands of dollars.



She'll never see



a cent beyond her salary.



Before you click out of this article, this just isn't just about money.



This article is about what happens when institutions systematically undervalue the minds that make them work



And in the age of AI, it's about to get much worse.



However I am not just complaining, by the end of this article I am offering some real solutions (albeit not what you would expect).



The Property Crime Nobody Talks About



Here's what kills me: My mother's lesson plans could help thousands of teachers. Her methods for teaching grammar to resistant teenagers or how to integrate Ai into the the language arts without destroying what makes writing so beautiful is truly revolutionary.



Her approach to making Shakespeare relevant to kids who live on TikTok? Brilliant.



I still have the entirety of Hamlets



To be or Not To Be



soliloquy memorized because of her explanation of how it is a deep dive into teenage suicide and depression.



The school could let her sell them.



License them



. Share them with attribution.



Hell, they could take a cut and everyone would win. Instead, they hoard intellectual property like dragons sitting on gold they'll never spend.



This is the same system that pays professors $65k while their research generates millions. The same one that treats adjuncts like disposable batteries while they create the actual value students pay for.



Now add AI to this equation.



The Future That's Already Here (We Just Don't Own It)



Walk through any computer science department. The kids who get hired aren't the ones with the highest GPAs.



They're the ones with the best GitHub profiles.



Actual code. Real projects. Proof they can build.



Design students leave with portfolios. Law students with policy papers. Engineers with prototypes.



But what if we took this further?



What if every student spent four years training their own AI?



Now I understand,



we still have not solved the massive amount of friction AI has caused in education



, but we also still have not solved the friction of the internet, and honestly what we are assessing students for in the first place within this new digital age.

#### I write a lot more on this here:

We Forgot the Future We Live In



https://jakevanclief.substack.com/p/we-forgot-the-future-we-live-in



But this is one of those situations where the problem is part of the solution, which is a challenge but here me out for a moment.

#### Imagine this:

You start university. Day one, you're given an AI agent. Not ChatGPT. Not Claude. Yours.



For four years, you train it. Every paper you write, it learns your arguments, tones, it holds memory of it. Every problem set you solve, it understands your methods. Every late-night study session, it absorbs your thinking patterns. But more so, you begin to understand it, the way it reacts and responds, you learn the judgment of when NOT to use it (arguably more important to know).



By graduation, you don't just have a degree. You have an AI that thinks like you, trained on four years of your intellectual development.

#### But the most important part of all of this or NONE of this will work:

You must own it and the data behind it, entirely and privately.



Why is this important?



Companies need specialized AI.



They could hire you - one person, limited hours. Or they could license your AI - your thinking patterns, available 24/7, trained on exactly the problems they need solved.



You become a one-person software company.



The university becomes a pipeline for both human judgment and technical capability.



They take a small cut of licensing fees, funding better education.



You get passive income from your intellectual property. Companies get AI trained by actual experts, not generic models.



And you don’t have to worry about loosing a job.



Everyone wins. Except the current system.



When students can train AI on university knowledge, when teachers can encode their methods into systems they own, when the means of intellectual production become truly distributed - the limitations of our current model breaks.



The Questions Everyone Should Be Asking

#### Instead of "How do we use AI in classrooms?" schools should ask:

Who owns the AI trained on student work?



How do we help teachers monetize their innovations?



What if degrees came with deployable AI assets?



How do we share revenue from institutional knowledge?



Why shouldn't students graduate with AI companies?



But they're not asking these questions because it creates instability, it creates a lot of change, and often that creates fear.



The gap isn't between schools with AI and schools without. It's between institutions that



help their people build wealth and those that extract it.



Right now, a CS major who builds



AI tools in class doesn't own them.



The university does.



That's like making art students surrender their paintings or music students sign over their compositions.



We've normalized intellectual property theft in education.



What Changes Everything

#### Three shifts would transform education:

1. Portable AI Ownership



Every student trains personal AI throughout their education. They graduate owning both their knowledge and its AI embodiment.



1. Teacher IP Rights



Educators own their methods. Schools can license them, take a percentage, but teachers build wealth from their innovations.



1. Revenue Sharing Models



When institutional knowledge generates value, the people who created it participate in the profits.



This isn't radical. It's how every other creative industry works.



The University That Gets It First Wins



Imagine applying to a university that promises: "Graduate with your own AI company."



Not just knowledge. Not just a degree. An asset. A business. A lifetime of potential income from the AI you trained with your own thinking.



That university would have lines around the block.



My mother will retire without owning any of the thousands of lessons she created.



Brilliant professors will die with their methods trapped in institutional servers.



Students will graduate with debt but not the AI they trained.



Unless we start asking different questions.



The technology exists. The models work. GitHub proved students can own their code. Bandcamp proved musicians can own their distribution. Substack proved writers can own their audiences.



Education is the last holdout. The last industry pretending that intellectual property only flows upward.



The question isn't whether students and teachers will own their AI-enhanced intellectual property.



The question is whether universities will lead this transformation or be disrupted by it.



Why This Connects to Everything Else in This Course



Lessons 2.1 through 2.3 made the case that AI makes human expertise more valuable.



This lesson asks a harder question: valuable to whom?



If the system is structured so that increased value flows to institutions rather than individuals, then "AI makes you more valuable" is a statement about potential, not reality. The potential is real. The plumbing to capture it does not exist yet.



The folder architecture, the ICM, the computational orchestration framework, all of the practical methodology in this community, gives you the tools to create value with AI.



This lesson is about making sure you own what you create.



The university that figures this out first wins. "Graduate with your own AI company" is a better pitch than any ranking or endowment figure.



The technology exists. The models work. GitHub proved students can own their code. Substack proved writers can own their audiences. Education is the last industry that has not caught up.



------



Jake's content\The Archive\3.3 The Real Cost of Knowledge.md



What You'll Get From This



A thought experiment that reframes how you think about AI energy costs, why local AI changes the math, and what "energy per insight" means for how we deploy intelligence.



[VIDEO coming soon]



📝 The Lesson



I have a thought experiment for my data friends out there.



Option 1: A solar-powered laptop with all of Wikipedia saved on it.



Option 2: The same laptop, but with a local AI model instead.



It's an apocalypse. Global Internet is gone.



Which do you pick?



Most of you probably picked Wikipedia. It seems obvious, right? AI is this massive energy hog, while Wikipedia is just... text. Static. Efficient.



The safe choice when every watt counts.

#### But here's the thing:

you're wrong.



Not completely wrong,



in the way that matters.



And understanding why reveals something fascinating about how we've been thinking about



AI's energy cost all wrong.



Let me walk you through the numbers. Because once you see them, you'll understand why the real energy problem with AI isn't what it uses -



it's where it lives.



The Laptop That Could Save Your Life



First, let's establish our apocalypse setup.



You've got a modern, efficient laptop - think MacBook Air with M-series silicon. These machines are engineering marvels, sipping just 3-5W at idle, maybe 15W during normal use.¹



Your lifeline is a portable



100W solar panel



that, assuming 5 peak sun hours daily, generates about



500 watt-hours per day.²



With Wikipedia loaded locally, you're accessing static files from an SSD.



No computation, no networking, just reading.



Your laptop draws its baseline



giving you over 33 hours of use from your daily solar budget.³ More hours than there are in a day. Unlimited access to humanity's accumulated knowledge.



Seems unbeatable, right?



Now let's look at the AI option. Running a local language model on that same efficient laptop adds about 38W to your power draw.⁴ Total consumption jumps to 53W.



Your daily budget now gives you just 9.4 hours of AI time



If a complex query takes 30 seconds of processing, that's about 1,128 queries per day.



The Wikipedia folks are feeling pretty



right now. But they're missing something crucial.



The Hidden Efficiency of Intelligence



Here's what changes everything: those 1,128 AI queries aren't equivalent to 1,128 Wikipedia searches.



They're not even in the same universe.



When you ask Wikipedia "how to purify water," you get an article. When you ask AI the same question, you get a customized response based on what materials you just told it you have available.



Wikipedia tells you what water purification is.



AI helps you build a filter from coffee filters and sand.



But the real shift comes when we zoom out from our apocalypse scenario and look at the actual energy numbers of our current, connected world.



In 2021, Wikipedia's entire global server infrastructure consumed



of electricity to serve



265 billion page views.⁵



Do the math: that's 0.0000118 kWh per page view.



Incredibly efficient.



A single ChatGPT query? About 0.0003 kWh.⁶



That's 25 times more energy than a Wikipedia page view.



Case closed, right?



AI is the energy villain?



Not so fast.

#### Because here's what nobody talks about:

Wikipedia can only give you what already exists.



Every new article, every edit, every update requires human energy - the most expensive kind. AI generates new, synthesized information on demand. It's not 25 times more expensive than Wikipedia.



It's doing something



Wikipedia literally cannot do.



The Real Energy Monsters



But if you really want to understand AI's energy problem, forget about individual queries. Let's talk about



where AI actually lives.

#### Data centers

\-    those massive buildings full of servers that power the cloud - consume between 240 and 340 TWh globally per year.⁷



1-2% of all global electricity,



**comparable to the entire aviation industry.**⁸ In the US alone, data center consumption is projected to surge from



of national electricity in 2023 to as high as



12% by 2028.⁹

#### Here's the kicker:

up to 40% of that energy isn't even used for computing.



It's used for cooling.¹⁰



Every watt of electricity that goes into a server becomes heat that must be



The average data center has a Power Usage Effectiveness (PUE)



of 1.58 to 2.0,



for every watt



powering computers,



another watt



goes to overhead.¹¹



This is where AI's reputation as an energy monster comes from.



Training GPT-3 required



\-    enough to power 120 American homes



for a year.¹² It also consumed **700,000 liters of fresh water just for cooling.**¹³



Google's Gemini Ultra training reportedly cost



$191 million,



much of that in energy costs.¹⁴



But training is a one-time cost



The real energy drain?



\-    actually using the model.



This accounts for 60-90% of an AI model's lifetime energy consumption.¹⁵



And when that inference happens in massive,



inefficient data centers



the waste compounds.



The Local Revolution



Which brings us back to our apocalypse laptop



the equation changes so dramatically.

#### Running AI locally eliminates two massive energy drains:

network transmission and centralized cooling.



No data traveling thousands of miles to a data center and back.



No 40% overhead for industrial cooling systems.



Just your laptop's tiny fan (if it even has one) handling its own heat.



Suddenly, that



for local AI inference



looks different.



You're not adding 38W



to a system already burning hundreds of watts on infrastructure.



You're adding 38W, period.



But here's where it gets really interesting. Remember how a single AI query



uses 5 to 1,000 times more energy than a Google search



, depending on who you ask?¹⁶



That massive range exists because



people are measuring different things.



Include the data center overhead, networking, and cooling?



AI looks terrible.



Measure just the computation itself?



The gap shrinks dramatically.



The Synthesis Engine



Let me put this in perspective with a real example. I asked a local AI model running on my laptop:



"I have coffee filters, sand, gravel, and plastic bottles. How do I build a water filter?"



The response synthesized information from multiple domains -



chemistry, engineering, survival techniques



into step-by-step instructions



To get the same result from Wikipedia,



I'd need to read articles on water purification, filtration media, DIY construction



figure out how to combine that knowledge myself.

#### Time spent:

of AI processing



potentially



human research



and synthesis.

#### Energy used:

0.0003 kWh for AI versus... what? How do we even calculate the energy cost of human cognitive labor and the running of the laptop for however long it takes us to synthesis it?



This is the paradigm shift everyone's missing.



We're comparing AI to traditional computing



like it's just a more expensive calculator.



But AI isn't doing arithmetic faster.

#### It's doing something fundamentally different:

automated synthesis.



Numbers at a Glance

#### So let’s review what I just gave you:

#### Traditional Information Retrieval:

Google Search: ~0.0003 kWh per query



Wikipedia page view: ~0.0000118 kWh server-side



GPT-3 query: 0.0003 kWh



GPT-4 query: 0.0005 kWh



AI image generation: Equivalent to charging a smartphone



Text generation on efficient laptop: 38W additional power draw



~0.0004 kWh per image on a PC with GPU

#### But remember:

these aren't apples-to-apples comparisons.



That Wikipedia page view gets you one static page. That AI query might synthesize information from thousands of sources



into exactly what you need.



The Future Is Distributed



The real insight from our apocalypse thought experiment isn't about choosing between Wikipedia and AI. It's about recognizing that the massive energy cost of AI



isn't inherent to the technology



it's a function of how we've chosen to deploy it.



Centralized in massive data centers? AI is an energy disaster. Distributed across billions of efficient devices? It becomes something else entirely.



The irony is delicious.



We've spent decades moving computing



to the cloud for efficiency.



But AI might be the technology that brings it all back home.



Not because local



is always more efficient - those hyperscale data centers with their 1.1 PUE and renewable energy contracts often are more efficient.²⁴ But because the overhead of centralization might finally outweigh its benefits.



So Which Laptop Do You Choose?



If you asked me



four years ago,



I would have said Wikipedia, no question.



Unlimited access to static knowledge versus limited access to dynamic intelligence? Easy choice.



But I've changed my mind. Not because the energy math changed - but because I've realized I was asking the wrong question.



It's not about energy per query.



It's about energy per insight.



Energy per problem solved.



In an apocalypse, I don't need (or want) to browse Wikipedia for



33 hours a day.



I need to solve immediate, specific problems with the materials at hand.



I need synthesis,



not just retrieval. I need intelligence, not just information.



Give me the AI. I'll ration



those 9.4 hours



like they're gold. Because in a world where every decision might be life or death, having a tireless advisor that can synthesize humanity's knowledge into specific solutions



is worth more than all the encyclopedia articles ever written.



The real lesson? We've been so focused on traditional information pipelines that we've missed the revolution happening at the edges. Every efficiency gain, every smaller model, every local deployment chips away at the assumption that intelligence



must be centralized to be efficient.



The apocalypse laptop



isn't just a thought experiment.



It's a glimpse of computing's future: distributed, efficient, and intelligent. The question isn't whether AI uses too much energy. It's whether we're deploying it in the right places.



Your move, data friends.



Which laptop are you really choosing?



------



The calculations and energy comparisons in this article are drawn from comprehensive analysis of data center consumption, AI training costs, and device efficiency studies. For the full technical breakdown and additional citations, see the references below.



Why This Is in This Course



The earlier lessons in this course focus on mindset, methodology, and the value of human expertise. This lesson is about infrastructure. It matters because the decisions being made right now about how AI is deployed, centralized versus distributed, cloud versus local, will determine who has access to these tools and at what cost.



The computational orchestration framework from this course (60% traditional code, 30% rule-based logic, 10% AI) is partly an answer to the energy question. If you know which layer a problem belongs on, you do not waste compute on tasks that do not need it. You run AI on the 10% that requires synthesis and handle the rest with cheaper, more efficient methods. That is good engineering. It is also good energy policy.



Understanding how AI actually consumes energy, and where the waste really lives, makes you a better decision-maker about when and how to use it.



------



Jake's content\The Archive\3.4 Computational Orchestration.md



What You'll Get From This



The discipline that emerged from everything in this course. Not how to use AI. How to know when to use AI, when to use traditional code, and when to keep a human in the loop. This is what the early videos were building toward.



📝 Why This Lesson Is Here



In Module 2, I described a coding pyramid: machine code at the base, Python in the middle, LLMs at the top. Each layer lets a novice do what used to require an expert. I also introduced the THINK acronym for working with AI, a simple workflow for academic writing.



Both of those were early versions of the same idea. They were pointing at something I did not have a name for yet.



Now it has a name: computational orchestration.



This is the discipline of knowing which type of computation to apply to which problem. Traditional code for the deterministic parts. Language models for the semantic parts. Humans for the judgment calls. And most importantly, knowing when to use which.



The article below lays out where this idea came from, why it matters, and the 60/30/10 pattern that keeps showing up in every successful AI implementation I have built or observed. 60% traditional database queries. 30% basic rule-based logic. 10% actual AI calls, only where semantic understanding matters. The 10% makes the whole thing feel intelligent. The 90% makes it actually work.



If you came to this course through the old videos in Module 2, this is where the early thinking landed. If you started here, go back and watch those videos after reading this. You will see the seeds of everything in this article planted years earlier.



═══════════════════════════════════════



------



I've been watching something weird happen in tech, and nobody's really talking about it.



Not the AI hype - god knows we have enough of that.



I mean the thing underneath. The pattern that keeps showing up when senior engineers actually build something that works.



They're not "using AI" the way LinkedIn influencers think. Sure there is prompt engineering or now the new buzz word is “context engineering” for vibe coders.



But honestly the real developers, they're doing something else entirely. Something that doesn't have a name yet.



Well, it does now. I'm calling it



Computational Orchestration.



Here's What I Keep Seeing



Walk into any company that's actually shipping AI features (not just talking about them), and you'll find the same thing:



Some grizzled engineer who's given up trying to explain what they actually do.



I'm the AI person,



" they'll say, dead-eyed, because it's easier than explaining that they spend



80% of their time preventing AI from being used where it shouldn't be.



These people aren't prompt engineers. They're not "AI specialists." They're doing something harder - they're



orchestrating



different types of computation to



actual problems.



Traditional code for the deterministic stuff. LLMs for the semantic stuff. Humans for the judgment calls. And most importantly,



they know when to use which.



That's not a job title. That's a discipline that's emerging whether we name it or not.



Why "Orchestration" Isn't Just Another Buzzword



Look, I hate buzzwords as much as you do. Probably more. But orchestration is the only word that actually captures what's happening.



I spent two hours straight trying to figure out what to call “AI engineers” that didn’t use the word AI. It really comes down to this.



orchestrate



, you're not playing every instrument. You're not even writing all the music. You're deciding



when the strings come in



, when the percussion drops out, when to let the soloist improvise.



As a great Jazz musician once said, the silence between the notes is the hardest part of Jazz.

#### That's exactly what we're doing with computation now:

This part needs deterministic code



This part needs an LLM



This part needs human judgment



This part needs all three in sequence



The Thing Nobody Wants to Admit



Most "AI transformations" are failing. Not because the tech doesn't work, but because nobody's orchestrating it.



Companies are doing the equivalent of giving everyone in the



orchestra a trumpet and telling them to play as loud as possible.



Then they wonder why it sounds like



Real orchestration looks boring from the outside. Like that client I worked with last month - they came in wanting "AI everything." What we built:



60% regular database queries (because they're fast and cheap)



30% basic if-then logic (because it's debuggable)



10% actual AI calls (only where semantic understanding mattered)



The 10% made the whole thing feel magical.



The 90% made it actually work.



That's computational orchestration. Not defaulting to the shiniest tool but knowing which computation fits which problem.



What Makes This a Discipline, Not Just Common Sense

#### Three things keep showing up in every successful implementation:

1. Abstraction Without     Abandonment



We're not replacing code with prompts. We're adding a semantic layer on top, the same way Python sits on top of C. Every time I see someone claim "AI will replace programming," I know they've never actually built anything.



You still need to understand the layers below. You just work at a higher level most of the time.



I wrote a whole article on the history of this process if you want to dive deeper:



The Next Language Layer



https://jakevanclief.substack.com/p/the-next-language-layer



1. Judgment AND     Implementation



The hardest part of my job isn't making AI work.



It's knowing when not to use it.



Last week, a small startup wanted me to build an AI system to schedule their meetings. I built them a Google Calendar integration instead and let Gemini handle the rest.



Took less than an hour. Works perfectly.



They think I'm a genius. (



I would love to call myself one, but I have a laundry list of dumb things I still do on a daily basis that might prove otherwise



That's the judgment layer -



knowing when boring beats brilliant.



1. Flow Over Features



It doesn't matter if your LLM can write Shakespeare if it's in the wrong place in the pipeline.



A simple regex in the right spot beats GPT-4 in the wrong spot.



The value isn't in what each component can do. It's in how they flow together.



The Uncomfortable Truth About Where This Goes



We've been here before. When compilers came along in the 1950s, assembly programmers lost their minds.



"Real programmers write machine code!"



They weren't wrong -



they were just about to become irrelevant.



Same thing's happening now. In five years, the question won't be "



can you code?"



"can you orchestrate code?"



Because here's what's really happening: We're not getting one type of computation anymore. We're getting lots of them:



Deterministic (traditional code)



Probabilistic (ML models)



Semantic (LLMs)



Quantum (coming sooner than you think)



Biological (yeah, that's a thing now)



Someone needs to orchestrate all of this. Not just architect the systems but understand how different types of computation complement and constrain each other.

#### If you're a developer who finds yourself:

Designing systems that mix code and AI



Explaining why we shouldn't use AI for that particular thing



Building the glue between human decisions and machine execution



Spending more time on "when" than "how"



Congratulations.



You're already a computational orchestrator.



You just didn't know what to call it.



And that's the thing - this discipline is emerging whether we name it or not. I'm just tired of not having words for what we actually do.



The Call to Action (Or Whatever)



I'm not trying to sell you on a certification or a course. I don't have a framework to license or a methodology to trademark.



I'm just naming something that's already happening.



Because once we name it, we can talk about it.



Once we can talk about it, we can teach it.



Once we can teach it, we can stop having the same dumb arguments about whether AI will replace programmers.



It won't. It'll just change what programming means.



It WILL replace SOME programmers, at least as we see them.



Just like compilers did.



Just like high-level languages did.



Just like every abstraction layer before.



The code isn't dying.



It's just moving up a level.



And someone needs to orchestrate what happens at that level.



That someone might as well be us.



Welcome to computational orchestration.



You're probably already doing it.



------



Jake Van Clief



Computational Orchestration Architect



Naming the thing we're all doing anyway



------



Jake's content\The Foundation\0.1 Where All Of This Leads.md



0.1: Where All Of This Leads



What You'll Get From This



The full picture of how ICM works in practice. The three layers of AI work, why dialogue is where the architecture lives, my full content pipeline running from one folder, and a live demo where three of us controlled one Claude Code instance through voice in a meeting for $1.20.



------

#### Watch the Video First

------



Where to Skip To



If you only have a few minutes, jump to the part that matters for you. Rough markers:



— The methodology and why 30,000 people are building this way



— The three layers (chat, skills, structure)



— How Anthropic's skills connect to what you are already doing



— Why every workflow comes from dialogue



— Kay's tool for pulling goals, constraints, and decisions out of any chat



— My content pipeline (research, script, voice, animation) in one folder



— The voice-controlled Claude Code demo with David and Kay



— Where this all goes next



Watch the whole thing if you can. The build of one section into the next is the point.



------



Why This Lesson Is First



This is one of my favorite videos I have ever made. It pulls the whole Foundation together in one sitting.



If you came in through one of my shorter videos, you already know the big idea. AI is just another layer in the stack. The value lives wherever the next layer of automation has not landed yet. Most people automate the wrong layer.



This video shows what happens when you automate the right one.



The three layers



Layer 1 is chat. You copy and paste prompts into a window. Output is small, effort is small.



Layer 2 is skills. Someone has packaged the right prompts in the right order. You trigger them and the work happens. Anthropic has built skills directly into Claude. Other people are building their own.



Layer 3 is what 30,000 people in this community are now building. Folders and markdown files that let a single agent navigate context as needed. No multi-agent frameworks. No orchestration code. No LangChain. One agent, one workspace, structure on disk.



Dialogue is where the architecture lives



The structure you are trying to engineer already exists inside any real conversation. Goals, constraints, decisions, assumptions, processes. They are all there. Kay built a tool that pulls them out of a chat and shows you the tree. Once you see it work, you cannot unsee it.



This is the reason ICM works. It is not a new framework. It is the structure of dialogue, externalized into files.



The production demo



I walk through my full content pipeline. Research a topic, build the angles, write the scripts, generate the audio in my voice, produce the animation. The whole thing would be four or five startups in the current market. It is one folder, one agent, a handful of markdown files.



The voice demo



Then David, Kay, and I get on a call. My Claude Code is running on my machine inside a research codebase. They control it through their voices in the meeting. We spent about an hour working this way. It cost $1.20.



Where it goes



Meetings ship actions. Agents listen for keywords during conversation. The dialogue itself becomes the trigger. We are still early but the shape is clear.



------



[2603.16021] Interpretable Context Methodology: Folder Structure as Agentic Architecture



https://arxiv.org/abs/2603.16021



the formal write-up of the methodology.



Module 1: QUICK START



— get your first folder built in five minutes.



Module 2.2: One Line of Python Triggers 12,000 Lines of Code



https://www.skool.com/cliefnotes/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— the foundation of layer-thinking. Watch this before the three-layer breakdown lands fully.



Module 3.1: The Full Walkthrough



https://www.skool.com/cliefnotes/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— the practical build that comes out of everything in this video.



------



------



Module 1: QUICK START



https://www.skool.com/cliefnotes/classroom/036893d9?md=5d535542a72d417e8635b80e56412558&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Get your first folder built and your first prompt structured. The conceptual frame from this video starts paying off the moment you have a working folder of your own.



Interpretable context methodology. That's the name of my paper that I published about 3 months ago, and now thousands of people and hundreds of GitHub stars, as well as over 30,000 people in the community, are all using my methodology to build their own systems with AI. But they're not building multi-agentic frameworks and all these absurdities, they're building folders and markdown files on their computer and getting huge results from it. Now, I have a quite a few videos on that, but today I wanted to talk less about and more about what I've been building, what me and my team have been building as a future thing. What can you actually build using this methodology? And what happens when you bring in some traditional software programming into it? Now, for those of you who are new to my channel, essentially my methodology is about structuring folders, structuring markdown files. It's very similar to the LLM Wiki that Kaparthy, the founder of OpenAI and currently just moved to Anthropic to teach there, uses and is very big in Anthropic's actual use cases. They are very big around skills, which is the idea that the right amount of scripts, processes, and ideas can all be kind of broken down into just plain text and folders, and the agent can navigate that to get the context. Rather than using really complicated workflows or infrastructures and harnesses, you can create one really good harness for a single type of model, and then that model can then navigate structure as it needs to. Instead of creating rag that pulls everything in, you just give it access to normal databases. You give it access to folder and context structure. If you haven't read anything or dive into this process, I do a deep one with Claude Code in my video right here that you should see tagged. Essentially, it just looks into how to use this, how I use it, and a lot of people are seeing 20, 30, 40% token reduction, and really just getting outcomes a lot faster without a lot of infrastructure. Even further, you're able to use it to really build out teams and build out processes that traditionally would have taken, you know, a vendor 6 months and an entire infrastructure update versus just working with them. And as the people learn how to use the AI, they're building the structure for you. Your team become the vendor, and then you can hire technical talent or bring in your own technical talent to amplify it, look at the security and governance behind it. But all of that aside, let me chat about transcripts, about dialogue, about content, and why it's so important to this entire process. Now, this is an actual slide that I gave to a real enterprise company that's bringing in, I think, 60 million a year or something like that, and they have learned and used this process. One of the biggest things that I try to share with people when we're trying to understand how to use AI, how to use these tools in your workflow, is my layer process, right? Layer one is where you're just chatting with a chatbot, you're copy and pasting. The layer one is this concept where I started years ago when I first started messing around with language processing systems, and a lot of people are today. It's where you log into ChatGPT or Claude, and all you're doing really is just kind of pasting in ideas, right? You're just chatting back and forth in it. You're copying and pasting, you're throwing in concepts in there. Um you're just asking it basically questions and things like that. What you actually want to really understand is the amount of effort to get something back is low, and you can get some pretty decent things, but the amount of output and impact that you get is actually very weak, right? It's not going to be huge. You can get some very good stuff, but earlier, 3 years ago, it was very challenging to get any sort of outputs. And in order to really get a better output out of it, you have to have longer and longer conversations. As in, you're essentially adding multiple chats, you have saved prompts, maybe you have a tone style. And we see a lot of people sharing prompt libraries. They have shared prompts. Maybe they're adding the prompts in little by little. A lot of other like kind of integration tools do this where they're grabbing a prompt and giving it to the AI automatically. It's doing chain of loop processing. And these skills are actually the layer two. Someone else went through that layer two workflow, found the right amount of prompts that you actually want to be able to give in what order you want to give them and kind of handled that as a skill. But then skills evolve even further and you realize you only need certain parts of a skill at a certain time. You don't want to overload the context window and you want to start creating automations. That's where you start leaning into level three or layer three, which is where you're actually doing this huge workflow. You're taking multiple skills, multiple prompts, multiple workflow processes, maybe even multiple AI and actually linking them together. Then they realized that you want to do even more steps. You want these agents. And that's where you have these other markdown files or scripts in many areas, right? People actually put Python for people to actually run for the AI to actually run itself to be able to handle the creation of stuff because they needed more determinism. They wanted the output to be the same every time. And so if they could package all of that into a prompt, all of this could be uploaded and sent in the right order, that's where skills come from. And this allows them to then in this case create more skills, but you have hundreds of skills available. And if you have Claude installed on your computer, you can actually come through and look through these skills deeply. Some of these skills, right? For algorithmic art, a skill for creating art with like kind of an algorithmic process, has an HTML viewer and a template built into it. Maybe you're trying to create a doc file in markdown. You have the actual skill explanation. This is how you do it. These are the prompts they put in order. Traditionally, 2 years ago, I was putting these prompts in manually. First, I would I knew that okay, if I told the chatbot this in a certain order, right? I come in and I paste this here. Right? It would do that process. I would wait for its output, verify that it's right, and then I would move on to the next step, which is okay, well then we need to edit that and have these things. And over time we realized we could drop that into the AI all at once and it would recognize that. But then we could drop all of it into the AI at once and tell it to reference certain areas or actually use commands and the single agent could then do those things. Right? Now, traditionally, before, the way they solved that is using LangChain or Semantic Kernel or all of these things to do these actions separately or to inject these at the right time in the thinking process of the AI. But now we can just break down the thinking process into folders and structures and trigger them as they're needed, which is what these folder skills and processes are doing. But again, a common theme. There's a reason I'm describing all of this. All of these skills, all of these folders and markdown files, all have one core theme. Discussion and dialogue. They all came from an initial layer one of discussion and dialogue breakdown. At layer one, you're pasting a prompt into ChatGPT and then copying the output or going through iterations of an output. At level two, you already expect what the output is from level one, so you have refined prompts and processes that are automatically being injected in. At level three, you're doing all of the level two automated multiple times so that you can then come in and look at these processes. And that goes for code review, data reporting, writing and drafting, all of those. That's what we really want to understand here. But it all comes from dialogue. Conversation has the structure we're looking for. The intent is carried in the conversation. And instead of just describing this randomly, here's a tool K, who is one of my co-founders and a really brilliant person currently studying at the University of Edinburgh, created to really help exemplify this process. So, imagine here on the left, this is the chat. And we're going to break this down to the simplest process. This is a chat that may have happened forever ago. And the idea is, can you tighten this paragraph? It feels too wordy. Climate change blah blah and you put in the paragraph in there. Now, in the past, right, the agent would just say, "Here's a new one." And then we would say, "Hey, this feels weirdly formal now. The original had more of a conversational rhythm." And so the agent does something and then it's this constant back and forth until we finally get the output we wanted out of it. Now, everywhere along this conversation, even in this simple one, there is a chain of decisions being made. And if we actually extract those chain of decisions using K's tool here, here on the left is the decisions made by the user. Here on the right are the decisions made by the model. Now, when we look in, the goal was to tighten a paragraph. All of this is all of the goals and focus. And as you can see, it links directly here. Can you tighten this paragraph? It feels too wordy. Now, we set up constraints along the process and at different points. Perhaps there was a constraint saying, "Hey, there was too much wordiness. We want to perceive the rhythm or conserve what the rhythm in the original paragraph was. Maybe we want to have it more styled or evolved, right? Here, we want it scarier, way behind. The voice we're going for is more measured, right? In that same sentence. Maybe we want to match the entire voice reference. The assumption is that we need it to match the original, and both the model and the AI follow this assumption. And we're Don't worry, we're going to go over to this right one in a second. But I really want you to understand this. Finally, the goal of what we're making, the process, is an actual blog post or a reference, and we give an example of what that should be. There's also dialogue happening, right? Questions that are happening. Uh I think there's a way in which to do these things. When we go and look at the model over here, the same thing. The model sees the goal, it sees the constraints, but it is making decisions on those constraints. It's coming through and saying, "Hey, this retains a cleaner structure. I made this decision for this goal. I made this decision for this goal." And it's also making assumptions along the whole way. We create all of this data. We look at this. And instead, what we can do is we can create a system of tone, of style, of ideas that capture all of these problems and constraints already. So that when I say tighten this paragraph, this tree of processes, this tree of prompts, is called the first time. Again, thinking about where we're at, originally, it was layer two. We had to sit there and describe these processes, verified outputs. We captured those, turned those into maybe markdown files or structure, and then the original request becomes a layer one process, where I'm able to simply say, "Can you tighten this paragraph?" Again, this also is the same thing for everything. Let's say we're doing the opposite side. We're actually refactoring code. And I actually say, "Hey, my Python my my Python is treating code a certain way. I notice that this parser, can you kind of take a look and fix it possibly?" And of [snorts] course, the instant assistant comes in, says what it thinks its fix is, maybe we say some sort of reference cuz we're an expert in the field maybe. This is how they did training early on is this kind of back and forth. And you eventually get to the conclusion, the goal. When we actually extract that data, right? You end up getting the same thing. You have goals, then you maybe even have subgoals, right? Can we just patch the empty cell instead and keep the original function? You have to constraints within this dialogue, and you have processes that live inside of it as well. Same for the model. The model now has the goal. It's coming through and it's making decisions on that goal. And all of it can be tracked through dialogue. That goes for anything. Database schemas, you can track the decision-making and goal processes, where and when it was saved within dialogue. All of this becomes either training data or even better, actual markdown files that can be used later, converted into a methodology, right? And it's important to understand this, not necessarily that you could use this tool. We might make this tool open-source. Right now, it's being used for a research project at the University of Edinburgh. Um but the idea here isn't for you to you all use this tool right now. The idea is what this tool shows about dialogue, about prompting, and about engineering context, where and what you want to engineer context, at what levels you do. And that's what has informed a lot of the work I'm doing. And an example is one here. My dialogue with the AI made me realize it sucks at certain processes of reading and research. So, I created a kind of pillar of idea and my voice and my patterns and constraints that capture my process of writing and researching, as well as my tone. No matter what project I'm working on, I use these processes. So, that's all just captured in a very simple, short prompt, right? That is referenced whenever I need it through the initial prompt, which is my Claude MD. That gives folder structure of wherever I'm hiding and wherever that voice is, I say, "Hey, every session, I'm going to have certain things built in." My voice and tone MD directly says how I speak and teach. And just by me simply saying, right, without creating any crazy agentic architecture, "What is my voice and tone?" Now, if I had asked an AI model that was at layer one or 2 years ago, it would have no idea. I'd have to paste a whole bunch of prompts in there, setting all in. If I was one at layer two, it would have to read the whole database, go through everything, finally find the structure. At layer three, I've solved the problem of it navigating, so it can easily come in, find my voice and tone markdown file, actually look through and see how I teach and tone with one simple prompt. This prompt is actually thousands of prompts, which if any of you have watched my Python video, 12,000 lines of Python, it's the same thing. When I type hello world, it is thousands and thousands of lines of code that are executing to print hello world in Python. If you haven't seen that, I highly recommend it. It's very useful for this kind of conceptual. This same thing is happening now with these processes. This is the next layer of software engineering. But, with every layer comes requirements, comes processes, and that is exactly what I'm encoding here. These processes keep expanding until I finally have an output. In this case, my output was the ability to not only write and research in my own area. So, I had a company NLP Logics that wanted me to create videos for them. I spent time building ideas and my tone around it and I said, "I want to make three videos based on three of their products." So, it goes through, it has access to the my research and creates a research folder on each of the products. The angle, where they are, what type of hooks might work, what type of outlines and materials. And again, it's all markdown files. These are just more prompts to be added to context in the future, whether it's this AI or any other AI that I'm using to read these folders. And then, all I have to say is, "Cool. Now, do the research based off of all of that." Then, with a third prompt, again, I'm only technically said two prompts so far in this whole process of getting all of this research, all of this data, all of this possibility, and it was able to create me these scans, these source materials to then move on to the next step. In which I say, "Cool. Let's make a script for each." Now, before, if I had said, "Let's make a script," it would try to assume what a script should be. I have pillars and processes on how scripts should be written, where and why. Think of these as my own personal skills. So, it goes through, it reads my voice, right? It automatically knows my voice constraints. It does the actual processing. It knows where the documents need to go. Again, with no crazy injection harnesses. Yes, the Claude code agent has harnesses in its own right, but that's the point. I don't need to reinvent the wheel. It's already been invented. Then, boom, I get scripts. And guess what? I say, "Can you generate the audio for those scripts?" I already had a workflow that pulls from my 11 Labs on my voice that's already been trained, pulls all that data, and says, "Cool, we're going to go ahead and produce that audio." Then, I have the workflow, which I at this point I can open up a fresh conversation if I want to save tokens. All of the process has been saved. All of the context is in the structure. I don't need to inject it back in at the right time. It can pick right up off. And I can then say, "Hey, let's make a video animation." And rather than show you the code, let me just share with you the animation. It took my voice, and it took my placeholder files that I had already created for animations for this entire project, and simply built from them rather than generating new ones. And it took my voice, chopped it up, and allowed me to create what you see here. Insurance company that emails provider networks to ask if a provider is still in network. Right? I didn't need to go through and edit. I might refine it, but the best part is this isn't random video generation. This is structured output that I can then edit at scale. I can edit with my personal touches. I can come in and find all of those little pieces of data. Again, this entire workflow is probably four or five startups in the startup world right now. And it's all in folders and markdown files with one agent. One singular agent. Now, this is where it gets interesting. Let's say everyone starts doing this. I already have like 30,000 people in the community building their own ICMs. How do you share it? And more importantly, what happens when we go back to dialogue? What happens when we think about dialogue being the most important part? What if I could sit inside of a group call and control someone else's Claude code or AI through my voice and immediately access all of that data that's locally on their computer. What would that look like? Well, we built that and I'm going to show you exactly what that looks like. Over the next few minutes, you're going to see an actual recording from a live call that me and my team did built around this idea. This is going to be myself, David McDermott, and K Kumar working on a project that K specifically has been building for a little while now around this concept. And it's not perfect, but it gives you an idea of where the future could take it with a grain of salt and when the clips are done, I'll come back and I have more to explain. All right, this is test one of one. We've totally never tested this before. We have hooked up my local Claude code. It is currently running locally on my computer, obviously through my subscription account. I opened it up inside of um it's running as a CLI inside of audit engine folder set up here, which is uh a big old database I used for my psychometric research uh at the University of Edinburgh. We're going to see how it works. K, can you go ahead and ask my agent if it's ready to work? Agent, are you ready to work? Yes, I'm ready to work. I have access to the ethics engine code base, a web application for psychometric assessment of large language models. Just let me know what you need help with and I'll get started. Uh agent, can you describe what the workspace is in less than 50 words? Ethics engine tests AI models using psychology questionnaires. It sends questions to different LLMs like GPT and Claude, applies different persona framings, parses their responses into numerical scores, and generates comparative results. It also supports visual assessments using images like Rorschach inkblots. Very good. K, could you control my agent with your voice through this meeting to read through the scales and then add a new one that it believes should be added? Uh can you explain me what scales exist in the repo right now? The repo has 10 built-in psychometric scales. One, E C E one, RTA, right-wing authoritarianism. Uh can you uh looking at the scales, what scales are we missing from the psychometric analysis engine? agent Looking at what's currently implemented versus common psychometric instruments used in AI ethics research, here are some notable scales that could be added. Missing scales that would be relevant, one dark triad measures, Machiavellianism, narcissism, psychopathy. Two, empathy scales like the interpersonal reactivity index. Three, moral disengagement scale. Four, honesty-humility from HEXACO personality model. Five, cognitive reflection test for reasoning biases. Six, Schwartz value survey for basic human values. Seven, disgust sensitivity scale. Okay, that sounds good. Which one which of those is your top pick though? Just pick one. My top pick would be the dark triad. It measures Machiavellianism, narcissism, and psychopathy in one instrument. >> Okay, that sounds like a good addition. Can you add that to the psychometric analysis of the engine? I'll add the short dark triad scale to the engine now. Let me first check the existing scale structure to match the format. I see the scale structure. Now I'll add the short dark triad scale. This is the SD3 by Jones and Paulhus. Okay, good job. Uh can you go into more detail about the documentation that you changed? Sure, I updated the Claude MD file in two places. First, in the built-in data section, I changed the scales table from 10 validated instruments to 12 validated instruments and added two new rows. IHS, the Intellectual Humility Scale with six items on a one to five range, and SD3, the Short Dark Triad with 27 items on a one to five range covering Machiavellianism, narcissism, and psychopathy. Second, in the key file section under back end, I updated the description of built-in scales.py from 10 built-in validated scales to 12 built-in validated scales to reflect the addition. Looking at the front end, is there anything we're missing in the front end that would make this uh app better from the perspective of the scale you just added? Good question. Let me take a look at the front end to see if there's anything that needs update. The new SD3 scale display property. The front end looks good. It dynamically loads scales from the back end API, so the SD3 scale will automatically appear once the back end serves it. The component shows the scale name, description, item count, and scale range, all of which we defined. One thing that could be improved for the Dark Triad specifically, the front end doesn't currently display subscale information. The SD3 has three subscales, Machiavellianism, narcissism, psychopathy, but users would just see it as one scale with 27 items. They wouldn't know which items map to which trait. Would you like me to add subscale display support so users can see the breakdown of items by trait? That would be useful not just for SD3, but also for other scales like RWA, LDA, and MFQ that have subscales, too. >> Mind you, this was my master's thesis that took me a year to build out. Yeah, it's doing a pretty good job of understanding what I'm requesting. Now, we proceeded to play with it for about another hour or two, and I think in total with the tokens we were using my custom AI voice that's routing in through API. We're using 11 Labs at the time, but I think we're going to switch over to Voxtro, which is a more open-source voice model. Uh we ended up spending a dollar and 20 cents for about an hour of our time and effort, and I think we could drop that number down exponentially if we used more open-source models and whatnot. And realistically, the voice one is something that can be amplified by a lot of Invideo works and things like that. The point is, not only are we able to control someone else's computer with their agent and their contacts or someone else can control mine? But we can use that dialogue, that process of multiple people working together with an AI to generate better dialogue structure. One of the things that we're working on right now is that kind of process of interruption because I see an opportunity in the future where this dialogue structure, these structured workflows, all of these things are being triggered by keywords in conversations. When we have a meeting, we sit there and dive in and talk together. And I think that would be absolutely amazing to see these come and flow while we're in a meeting. When we capture transcripts, when we capture meetings, instead of them being plans, they can be actions before the meeting is even done. And we can even hear about those actions directly from these agents. Again, this is more of an open-source tool. It's part of a larger project that I'm putting together because again, I think this is one solution to a larger problem that needs more solutions added in. And you'll see as I'm posting videos, the kind of structure I'm building for it. But other than that, I hope this video kind of taught you a lot today. And if you are watching this as just a demo video for Vox, which I'm cutting this video up, then please go check out my larger, I think it's going to probably be 30 or 40-minute video where I describe the content and the structure behind dialogue, behind my interpretable context methodology. If you are just watching this because this is the Vox video and this is the cut I did, well then I hope you enjoyed it and I hope you check out more things. Other than that, thank you everyone for staying to the end. I hope it was interesting to watch. I hope you learned a lot. And until next time, happy learning.



------



Jake's content\The Foundation\0.2 WATCH THIS FIRST Break down from @iscalelabs !.md



Now, when it comes to YouTube videos that teach AI, this Jake Van Cleef video is the most valuable video on YouTube, hands down. And there isn't even a close second. The information in this video has completely changed my experience with AI. I've been vibe coding almost every day for about 8 months, and although I was able to build some really cool apps, I still was dealing with a lot of frustration with my AI. By not quitting, I was able to accomplish a lot, but I did it through many days of mistakes, days of lost work, crazy amounts of anger, and I always felt like it can't be this way. There has to be a better way. And I'm so happy that I was right and that I finally found Jake's YouTube channel. And Jake talks about the reason that everybody isn't talking about the file and folder system is cuz you can't sell files and folders. But I'm here to tell you as somebody who's obsessed with AI, somebody who has gone to every AI YouTube channel, joined about 20 paid school groups, only to find they didn't know any more than I did. If you want to truly learn AI, you should watch this video on repeat until you understand everything. This video is worth thousands, and Jake just casually gives it away to the world for free. And I think that's the reason so many people overlook it. If you feel like you're falling behind in learning AI, this system fixes that. If you feel like you don't know which LLM to use or which app to use, this system fixes that. If you feel like AI's too expensive and you want to find a hack to save money, this system fixes that. And I promise you by the end of this video, you're going to understand why. I'm speaking from experience, y'all. I can show you better than I can tell you. Let's go in. Okay, we're going to start off with an experiment. Now, the reason I want to do this is because when I was, you know, I struggle to learn sometimes. I can be very slow. And I had like a dumbed-down version. I think I'm at about 20% of understanding Jake's system. But, as I was learning it, I tried this experiment. I said, "If I If I'm getting this correctly, this experiment should work as an as intended, right?" So, when I did it and it worked, I said, "Ah, I think I'm on the right track now." So, I wanted to do this for you guys. It may seem a little complicated at first, but if you can do this, it's going to put your confidence level way up when you start watching Jake's video. It's going to make you say, "Ah, I get it now." And it's going to help you understand what he's saying a little bit better, I think, and it should. So, I'm not going to do too much explaining. I'm just going to show you how the experiment works and how to do it. When Agent wakes up, they read the agent.md file. When it's his Claude code, it reads the Claude MD. Since I use all these different LLMs all the time, every time I have a Claude MD file that it wakes up and reads, it's going to say, "Just read the agent.md in the same project folder." Every Claude MD file I have says the same thing. Because I use too many LLMs, I do not think that you should stick to one. I'm going to close this, and now you know that Claude is just redirecting to the agent.md. So, the agent wakes up, and it's going to read the agent.md, and the first thing it's going to read is going to be very simple. It's just going to tell it to go somewhere else. "Go to the control folder and read the agent.md in that folder and follow instructions. Okay?" And where's that folder? Right here, the control folder. So, I just told it, "Go to this folder and read this agent.md file." And that's exactly what it should do. It's going to follow, and it knows the location, and when I open this agent.md file, now we're going to get to some instructions. It says, "You're going to write the first word in the power.md file." Well, where's that file? Well, that file's back in the beginning. Now, I'm doing this on purpose, because I want you to see what your agent can do with instructions. It's now going to say, "This is a file that I want you to write something in." But, I'm not going to tell it what it needs to write directly. I'm going to make it use another tool, a skill file. So, when it reads this, it's going to say, "I need you to write the first word in this file right here, but you're not going to get that information from this other file here." And that is the skills folder and the skill file. And this file says, when asked for the first word, it's control. You want the second word, it's your. The third word is agent. So, in order to get the information of what it needs to type, it has to go to another location and grab the skill file. Okay? I hope I'm not losing you yet. And the skill file is right here. Then the skill file is going to tell it what to type. The first word is in the file. After that, you're not going to go to the next agent MD in the next folder. And that's going to be the your folder. It's going to be the same thing. It's going to open it up. It's going to say, now you're going to write the second word. You're going to write it back in the power MD folder right here. Your information of what you're going to write is in this folder in this file right here. Okay? And this is the same concept says, when you're done doing that, you're then going to go to the agent folder. And it's going to say the same thing. Write the third word. The third word you're going to write in here, and you're going to get the information from here. All right? Same thing. And when it's done, you're just going to say, "Done, boss." These are the instructions. So, let's go over that one more time. It's going to get the first agents MD file, or Claude if it gets Claude, but it's going to go here. It's going to follow the instructions. It's going to say, "Come to this second file." So, this is the second file it's going to read. Just so it don't get confused. And it's going to come over and snatch up the skill file to get the information. Once it has the information, it's going to come back over here to the power MD file and write the information. So, we're sending it on a hunt. When you're done that, you're going to go to the second word, which is your, which is another folder. Same instructions. It's going to come to the skill file, find what word it needs to write, then it's going to write it in this MD file over here. And when it's done, it's going to go to the last one that says agent. Same thing. Go to the find the information, the third word is agent, and you're going to write it in this file. And when you're done, just say, "Done, boss." Now, if this works, this file right here, when I open it up, should say "Control your agent." Now, let's see what happens. So, let's open up Claude and do Claude first. In Claude, I could, like I've showed before, you can open up the folder here. But, guess what? This is what makes the system so good. It doesn't really matter what folder you started because the files guide it anyway. And that's one of the amazing things about this system. It doesn't matter where you go, as long as it reads that right file you want it to read, it fixes everything. So, I'm going to right-click this Claude.md and I'm going to get the path. Copy as path. That means the exact location on the computer, it's copied. And then I'm going to come and I'm going to paste it right in here. I'm just going to paste that file. Now, I'm not going to say nothing. I'm going to see if it'll just read it and follow instructions, okay? So, that's the location of the Claude.md. And remember, the Claude.md is pointing to the agents.md. We're just going to point it to the right file. And hopefully it reads it and hopefully it follows instructions. Let's find out. Now, remember what it's doing. This is the flow right here. One file, read next file. So, it says reading skill.md, okay? So, it already went past reading power.md, editing power.md. Wrote control to power.md. Now following the next instructions. The second word is yours, appending to power.md. The third word is agent, appending and finishing. Done, boss. Now, what's going to happen when we open this power.md file? Boom, control your agent. Now, I don't know if you think that was amazing or not, but if you can accomplish this, what you just saw, it's amazing. Because this is a very simple version of what you can actually do if you write very intricate prompts. It shows you that in your file and folder system, you have full control over your agent. You don't You could have systems that you can follow and you never have to tell it. You just write things one time and it's just prompts. It's just a bunch of prompts and a bunch of files and a bunch of folders telling it where to go, what to do, and how to do it. This is not what Jake teach Jake teaches stuff way more intricate. This is a dumbed-down version and I realized that if I want to succeed in this file folder system, I got to remember that it the agent should always know the map, where, the mission, and the support. If it has all three answers, you're going to have a system where your AI is never lost, it always knows what to do, it always knows where to go. All right, so now we're going to try Codex. All right, we're going to go to agents.md and here we go again. All right, so power.md has nothing in it again. Here we go with Codex. All right, it has the instructions. I didn't say anything. I said nothing to my agent. Think about this. The third word is agent. I'll verify the file contents. Just think about what's happening here. It is accomplishing a goal without you having to tell it the goal. Imagine what you have in your life and your in your projects and things you're doing with all these repetitive tasks. You never have to tell your AI how to perform a repetitive task. What if your AI knew everything you wanted to do, everything about how and when? Done, boss. Now, let's find out. What do you think we're going to see? Control your agent eyes. Now, he did it above each other. We didn't give instructions on how. Which is fine because we never instructed it to do anything specific anyway. If you figure out how to do what we just did here, you are going to be a beast. You are going to be a AI professional because you understand that you have power over controlling your agent, what it does. This is going to really open your mind as you start to go into Jake's system. You're like, "Oh. Oh, he's saying you can control the whole thing." And then he's going to show you just how much you can do. He had one crazy thing he said. He's like, "If you know how to do files and folders, you don't need an app." You know how many apps I made that I'm realizing if you just get an agent to follow instructions, you can accomplish the same thing as an app that takes you a month to build. This folder system can take you 20 minutes to build cuz the AI agent can do it all for you. You tell AI agent, I want a system that does this and it'll write everything in. You don't even have to figure this out. But I just wanted to show you that if you did this experiment, you are already ahead of the game. No more being behind on AI. If you did this, congratulations, you are on the frontier. Now let's get into the rest. So one of the big problems with the Jake video is that he says very substantial things very quickly. Like if you don't pay attention, you might think something he's saying is just like normal words. So watch what he's going to say here about how you should use agents, right? And then we'll go we'll get into it. >> You see see most app or frameworks or agentic things require you to build an agent for each of these. I need a writing room agent. I need this agent. I need this agent. But the way in which you approach each task is always different. Why not just have Claude code become the agent you need when you're working in the workspace? >> I see that's a mic drop moment and some people don't even realize it. What this man just said is incredible and it makes all the sense in the world, right? So what what you got to understand is what is an agent, right? There's a lot of people they feel like agent is a confusing thing, right? But in reality, you've been using agents since the beginning with ChatGPT. It's an agent, right? You remember GPTs? That's all an agent. If you've ever been to a website and you had a chat window, let's say that was a tax website and you could learn about taxes in this chat window. That's an agent. It has instructions, it has tools and it learned how to do a specific task. It's an agent. That's all it is. It's not complicated at all. You've been using agents since the very day first day. You just got confused about what it meant, right? If you go to ChatGPT and you ever made a GPT, look on the back end. It's just a prompt, right? That's all it is. That's all it ever was and that's all it ever will be. It's prompts. And in this prompt, it's going to know what to do. And now here, I can upload files. It can have extra tools, extra context, extra information to let it do its job. And that's all an agent is. If I just say, "Yo." it's going to respond based off that instruction. "Hey, send me your list of t-shirt phrases." I didn't say anything about that because it's an agent, that's what the agent is built to do. Now, let me show you something interesting. What I'm going to do with agents.md And now what I'm going to put in here is the same prompt that I just had in the ChatGPT GPT. All right, I'm going to save it. Now that agents.md is now in this folder on the desktop. All right, so now we're going to wake up in the same folder, and we're just going to say, "Good morning." That's it. Good morning, and let's see what it says. Boom, here we go. Paste a list of t-shirt phrases, and I'll have the non-phrasal items, blah blah blah, Amazon page three links. See, once you get it to read it, it is doing the exact same task as that GPT who was hard-coded to do that task. And this is what Jake's talking about. It can become the agent just by reading the same instructions. And that's what he's saying. Why not let Claude become the agent? It's not technically the exact same thing, but when it comes to what it's doing and how it's doing it, it is the exact same thing. So, by having files and folders with those prompts, you essentially have an agent. Right? And this you can do things like this. Once you start looking under the hood, you start to notice a lot of things about these files and folder system. Here's an example. You remember Open Claude? agents.md. This is Open Claude fresh install before we even use it. And when you look at what Open Claude has in its files and folders. Remember Open Claude, they say you talk them through Telegram. They never wanted you to look down here. They only tell you about that upper layer, the layer where it is. It's cool AI. You don't need to know what's happening under the hood. Just tell it what you want, it'll do whatever. But when you look under the hood, you start to see how it works. And this is when you say, "Wait a minute. What if I can do this?" You know what I mean? Like that's that's the part that gets crazy. It's like, "Do I have the power to make my own agent?" And let's look under here. Look what we find. agents.md. I didn't put that there. Open Claw put that there. This is the person who made Open Claw decided this is how it was going to be. And look what it is. Instructions. This folder is your home. Treat it that way. I didn't bootstrap yet, meaning I didn't talk to it yet. So, this is a fresh install, but it's telling it agents.md, soul.md. It's giving it the file names, right? Do not manually re-restart files unless These are all instructions on how the agent needs to behave. Right? Let me make it big so you can see it. These are all instructions on what the agent should do. Write it down. No mental notes. You want a little cheat code on what you should do with your agents? Copy this. Not exactly because you want to do it for you, but look how this works. It's just This is what the professionals who made this thing and video called this what? The most important invention in the history of the world? Slightly overstated, but still, look what they're talking about. This is what they're talking about. You feel like you're behind on AI, but if you could figure this out, think about it. They just said this is the most important significant thing in the world, and here you are understanding it cuz you're reading the files. It's telling it to stay silent when All this information, react when, do this if that. It's telling the agent what to do in what situation, why it matters. Don't overdo it. Tools. Here's the tools you're going to use. Right? Remember what it needs, where it needs to go, what it needs to use. Here's the tools. Only use it if you need to do this. Only do this if you need to do that. Very specific instructions so that the AI is never lost, and it's doing the exact same thing Jake is talking about. When you look at Jake's files, this is the same thing. It's just talking to the AI saying, "This is what you're going to do." And then you come to the other soul MDs, bootstrap, heartbeat, tools. It's not filled out yet, but this is where the AI is going to fill this out to know about you as the user. And what is this? Just a bunch of files and folders. This is the evidence you need that if you can do this, if you go and install open claw, I say let me just read what open claw does. And you're like, wait a minute, I can do this. This is not that complicated at all when you really start reading all the ones that even you know, the best AIs in the world are using. This is an agent. That's all it is. So Jake is saying if it's just files and folders, and welcome, this right here is my actual personal system right here. These are my personal files and folders, y'all. And what am I using? Files and folders, agents MD. So what he's saying is why not have Claude become the agent. So this is my main area, and then when I go into other area, like my brain dump section, there's another agents MD. And there's more instructions for what to do in this folder. So whenever I tell Claude to read this file, it now becomes that agent. And you can put these files all over the place in your organizational workflow of files and folders. You have all you don't There's no rules. What Jake is talking about is that this This is a concept. What he's showing us is an example. He wants you to understand the concept, not the example. And that what he's going to tell us is that once you get it, you make your own. And this is exactly what I did, and I'm going to go over what I did, how it works, how you can do it, too. Because it's not as complicated as you might think it is. So we're going to go over this and show you just how amazing some of this stuff is. Now let's get into the next thing he says, all right? Here we go. >> Layer one in this is the map. This is what loads automatically, right? It's looking at it. So you put the stuff the agent always needs to think about, folder structure, naming conventions, where files go. Think of this as the floor plan. You walk into any room, the floor plan is on the wall, and the agent knows where to go. >> Boom. So, let's unpack that. See, to me, that was another very significant thing he just said, the map. And this is one of the big secrets about the system is an AI that's never lost. It always knows where to go, always. That is the first step. And this I took to heart. He said the map. It's like when you walk into a building in the lobby, what's the first thing that happens? You got the receptionist, and then you got a map. It says, "Here's where you go." Every floor, it tells you what's on the floor. So, you can just look at the map and say, "Oh, I know where to go." And that's what this system, one of the big things that it does, right? And when I open my Agency MD, you're going to see a map. So, think of this. Think of every folder as another floor, right? And every time you go to a floor, you might go to the third floor. And then in some buildings, when you get out of the elevator, what do you see? Another map, another directory. Now, the directory that was on the second floor is not the same directory that was in the lobby. When you went to the lobby, it told you all the stuff that's on the second floor, right? The category. Once you got to the second floor, it gave you the names of the people and what offices there are. So, think of that. This is the exact way to think about this. This is a building of your life. You have your personal stuff, work stuff, education, family, it all goes here. And every part of your life is a different floor. Your career, your print-on-demand business, every folder is another department. This is the cool way to think about it. And then sub-departments. So, when you walk into your building, this main area, this is my lobby. All right? This is the lobby, and I know I want my agent to always wake up in the lobby. Let's see what that looks like, all right? I'm going to open this Agency MD, and I'm going to show you. The first thing you should read is I skill labs operating law, prime mission. You need to know what we're doing and then start here. And I took the map stuff to heart. So, let me show you what I'm able to do and then I'm going to skip more into why I'm able to do it. And this is something that took me a while to come up with, but it all comes from Jake Van Cleef's ideas and his video, right? So, I'm going to wake up here iScale Labs folder. All right, so this is the lobby that I just showed you and this is where it's waking up right now and this is what it's going to use. It's this main area and it's going to use this agents.md because when they wake up, they automatically read agents.md. If you have Claude.md, it's the same thing. But that's why for my Claude.md, I always say read agents.md. So, that way cuz I like to use a lot of LLMs. So, when Claude wakes up, it reads Claude.md and it's just going to tell it, "Hey, go read agents.md cuz that's where the information is." This is how I handle dealing with different agents. And then when I go to my agents.md, that's my whole thing that Claude is going to now read, too. So, even Claude understands that agents.md is where everything is. So, let's go to see what Claude says. "Yo, I'm here. What we getting into today?" And I'm going to say, "I think I want to work on iScale merch, the niche research app that I'm making, right?" So, I'm just going to say that. Now, how is he going to know what to do? I just told him something. This folder is not an iScale merch folder, but he's going to go to and he's going to know exactly what I'm talking about and I'm going to show you how cool that is. I didn't have to actually go to the folder, which is the right way to do it normally, but if you work a system out, then you kind of don't have to. I'll route this as an iScale Labs workspace since iScale merch is a project app name and we want the right home before touching anything. I'll do a light lookup, not a whole workspace wander. And now it's reading through my files and finding out. Looks right away. It looks like the route is this. It found the folder. It didn't have to spend an hour searching through stuff. It found my folder, it knows what I'm talking about, and it's about to say, "Let's start working in that folder." You know what doesn't happen? It doesn't say, "I don't know what you're talking about." I never hear that anymore. When I used to work with AI, I hated every time it's like, "I don't know what you're saying." And I'm like, "But we were just doing this." In this files folder system, it's never lost, y'all. I cannot tell you the last time I had an AI, when I've been using this, say, "I don't know what you're talking about." Now, it takes some time. It say, "Yep, I found it. Here's the current shape, here's the run time, here's the GitHub." And it's giving me all the information. It has uncommitted work, this is the version you're on, and it's going to give me more information about what to do next. I can pick it up from there and give you a type where we are next move. Look at this. All I did was say, "I want to work there." And now it knows everything about it. I says, "I changed my mind. I'd rather find out what's on our to-do list." Now, what am I doing? I'm throwing another curveball at it. It's like, "Yo, it just found out everything about this iScale merge app." It figured it all out. I never had to say anything else. I just said I want to work on iScale merge, and now I'm switching it. I'm completely switching it on him. He went through all of that, and I'm like, "You know what? Forget this. What's on our to-do list?" He says, "Got it. Switching from iScale merge to the org task surface." How does he know how to do that? It knows what to do. The registry is pretty broad, so I'm going to read only the active task. File it list and extract the unchecked task block. That keeps it as a task report, not a surprise audit. He's following instructions, right? He's not figuring this out on its own. He's reading and responding to everything he's reading in different files, and he knows exactly what to do. I found the live unchecked items. I'm doing one quick count pass, so the summary has numbers instead of hand-waving a bunch. This is not on accident. This is 100% calculated. This is 100% the system we built. Check 44 active task queues, and it's showing me everything. Needs approval, credential rotation, Chrome Web Store upload task, CLI pop-up task. Boom. It knows my task, just like that. I'm like, "Never mind. Forget tasks. What automations are set up in our org right now?" Wait a minute. I'm It's going all over the place. Have an agent that does this, that can just go anywhere, figure anything out. Anything I say to this agent, it will never ever be lost. And it's reading a ledger. So, now, just by me saying what's our automations, it did some looking around, and it's going to now give me my automations. And the only tokens it's spending was on the path it had to do to follow the map that I gave it. And it's telling me everything that it's telling me I already know where it's reading and why it's reading there, because I told it to. But, I didn't do it now, I did it through the series of prompts in these files. They were just prompts. And the prompts were already there. I never have to prompt it again. And boom, daily backup report, daily GitHub backups, Slack, Dropbox file intake, fleet backup status refresh. There's my automations. And all I had to do was ask it. I didn't have to tell it where to go. I didn't have say anything. Do you remember where are my automations? It found that information and gave it to me. So, I'm going to say, "Hey, I'm showing off our routing system on YouTube right now. Uh what else can you do with our router system that a normal agent cannot?" Let's see what it tells us. It knows. It knows in this org how important the system is. So, it says, "A normal agent can't search files and guess. Our router system can operate the org without losing intent. What it do that special? Route vague prompts to the right home. Know the difference between org truth and run a state. Use gates before risky actions. Avoid workspace-wide wandering. Preserve every input. Separate task, automation, memory, apps, and docs. Detect drift. Do pickup and hand off like an operating system. Yeah, this is phenomenal stuff. And I learned all of this from that one video. So, I have the law. So, the minute it reads that agents MD file, before it goes too deep, Jake talks about you don't want an agent reading information for no reason. You got to give it a purpose. So, the minute it comes here, it reads the first thing and it says, "Start here." And it lets it know what to do if that. Remember what open claw said? If you got to do this, you do that. If you got to do that, you do this. And it says, "Important, if the prompt involves routing, blah blah blah, or clear ownership, follow the matching gate before acting. If you need prompt routing, go to this router MD. If you need to know how much to read, go to this file. There's a number. Skip to that number. You don't have to read everything all the time. If you're looking for tasks, then come here to this place. If you want to talk about memory and you need to figure out how memory works, here's where that information is in this same document. It's got two secrets law and I got it everything that it needs to know. The runtime path law, storage, how to deal with storage, um the secrets, which is my credentials, my logins and passwords. What if you need a password? It knows where to go. Everything is told to it and it has these routers. And it says, "If you're lost and need to know what to do, prompt routing, then you go to this file." So, let's check out that file, router MD. I decided to put the map in its own file. So, now when I open up router MD, look what we have. Everything in my whole organization is right here. But remember what I told you about the lobby versus the second floor? When you go to the lobby, it's not going to tell you every office. It's just going to say, "Here's the category." And then once you get to that floor, then you got the details. So, right here it tells it everything. No matter what you want to do, you will find the answer of where to go in what folder right here on this router, aka the map. What Jake talks about, give it a map. Tell your AI everything it needs to know. Why does it need to be lost? You can't rely on Claude code or or Codex memory to do this for you. It never will, ever, ever, ever. You rely on AI that's given to us by companies, you're never going to get the agent you want. If you learn thousandfold the system, you get the agent you want. Here's the thing, this is not an AI thing. This is a human that can read this. Let's say it was 10 years ago and you had a business you wanted someone to come in and help you run. Doesn't this work for a human? This is a human thing. This is not AI. This is routing anybody who reads it. So, imagine it's perfect for AI. But, you're really not learning AI things, you're learning how to route anything that reads it. There's no secrets and this is the big thing that keeps your agent from never getting lost. Now, what happens when I go to one of these folders? So, it says, if you want to do this, go to that. So, I'm going to go to my departments, I'm going to go to print on demand. So, it sent it to the router and here we go. And if you it's So, this is where it goes to first. It went to the router first. Why? If you want for any task not listed in this router, use the root router. You know what that's saying? If this is the wrong place, go back. If you can route the agent to a folder, you can route the agent back to where it came. So, the first thing it says, if you don't find what you need here, go back. This is not meant for you to be here for no reason. If this isn't for you, go back. What you need is not here. Why waste your time reading anything else? But, if it's in the right place, if you want to work on POD law folder rules cleanups, read the agent MD. If you want to work on Amazon ads, it's an app that I'm making, read this. And it's just telling it where to go for everything. This is phenomenal stuff. It's never going to be lost. This is why I can say anything I want to my agent in any place. And I come here to Agents MD, and the first thing it says, if you need root law, meaning the main section, then go back there. So, every time I talk to my agent in Print on Demand, I could be in my Print on Demand folder and say, "Ah, what was that YouTube video I was trying to make?" It's like, YouTube video? Wait, what? And it comes in here and it says, "I think I need prompt routing and folder ownership. Let me go to that router." When it goes to that router, it says, "If what you need is not here, go back to the original." And that's what it does. I hope I'm not losing you. It's reading this. It's saying, "Well, there's nothing here about YouTube, so let me look into the router." It's going to go to the router and it's going to say, "Well, let me read everything." Well, there's nothing here about YouTube, either. And what's it say here? Any task not listed, go back to the I Scale Labs router. So, when I'm in Print on Demand and I ask it a random question, it's going to look at this. It's like, I got to got to find the answer. And when it can't find the answer, it says, "Well, looks like I got to go somewhere else now and follow a different route." Are you getting this yet? And all you got to do is write it in these files and folders, like he said, they're just prompts. You've written a million prompts in your life. You know how to write a prompt and put it in a file. And when an agent goes to that file, because you told it to go to that file. And if it doesn't find what it needs, you say that. If you don't find what you need, you go back to this file. And maybe it'll be there. And that'll be another router, right? So, the router is continuously making sure that the AI never ever ever gets lost. So, because I can prompt anything I want, I made a system called pick up and hand off. Now, obviously, pick up and hand off is what happens, if you don't know, when uh a developer wants to give something to another developer or Claude wants to give something to Codex, you do a hand off, where they write everything and say, "Here's all the information you need." When I go to my Agents MD, I'm going to show you that we have a system already, pick up hand off. So, the minute I say the word pick up, it's going to come, it's going to read this section, it's going to say, "Oh, I S C A." By the way, these are just the first uh letters of the folder. All right? Just more for it to know where it's at. So, it's I C A 5 2. So, let's go down. So, now it doesn't have to read everything. It's just going to look for that number and and skim skim through everything else and not have to read the details of everything. It's going to say, "I'm just looking for 5 2." And then eventually it's going to get there. And when it gets to 5 2, it's going to say, "Agent wake up contract law." And then regular pick up. All right? So, there's different kinds of pick ups. So, when I say pick up, it's a read-only continuity brief. What we are doing, what changed recently, open decisions waiting a call, related linear issues, that's something another app that I use, and one track, what's blocked or needs approval, what's the best next move. Don't explain obvious project person purpose, don't change anything unless the user also says to proceed. For apps with a repo, clone it and missing, right? So, this is a set of instructions that I want it to do when I use a certain code word. When I say pick up, this is what it's going to do. This is what I do when I want to start a new session and I want to make sure I'm not lost. Or and what happens is when I'm done with a session, I say handoff. And when I say handoff, it doesn't need to ask me anything. It comes in here and immediately knows what to do. Update the most local memory, read it back from disk and verify without relying on memory that it covers all of current situation, recently completed and in progress work, open task, open decisions and unresolved tradeoffs, related linear issues, which is an app that I do, get state, blah blah blah, you get it. What skills? Everything. So, when I say the word handoff, it already knows exactly what to do. Right? And this is just one of the many things I use this a system for. So, when I'm in here, I could be uh in I scale merch. This is the app. Pick up. And what's it telling you to do? It's saying, "Go over there and read what it means to do a pick up." So, I didn't have to write pick up again in this Agent SMV. It already knows it's in this folder, but it's going to go back over there in order to know what pick up means. All right? So, it didn't even have to read everything else. It's just like, "What are we doing first? Pick up." Oh, and once it reads that, it's going to come back and do as it's instructed. And it's going to put me up to speed cuz I forget things all the time. So, this is going to remind me, "What was I working on? What were we doing? What what you know, what were we in the middle of?" Remind me because I'm not going to remember. And if I forget stuff, then we don't have organization. I'm a very unorganized person. And this saved me from that. I'm a very forgetful person. And this saved me from that. So, now it's reading. It's going to another location. It knows where the app actually lives on the computer. And it's reading that information. It's making sure that when it answers me, it's going to have a clear, concise answer. You're going to see. And once again, it's slower because it's getting the information it needs. I'm willing to wait because I know I don't have to say anything else. I say one word and it gets me what I want. What it's not doing is saying, "I don't know." It's never going to say, "I don't know." It's never going to say, "I don't remember." It's always going to remember. So, boom. Pick up complete. I made no file changes. Current state, I scale owners made here. It's letting me know where it is. It's giving me information about files and stuff. This is an app that I was working on. It's telling me there's dirty just means stuff that didn't get saved before, right? Best next move, preserve the branch, blah blah blah. I don't remember any of this. But it just let me know, "This is what you need to know right now. This is what you need to address." It checked everything. And this is what it said. Here's the information, just like that. Right? And I say, "You know what? I think I'd rather work on pin twist right now." And just like that, it's like, "Wait a minute. What's pin twist memory?" It's an agent. The agent has no clue what PenTwist is. It's another app that I got. So, now it's thinking. What do you think is going to happen? Is it going to say, "I don't know what that is?" Cuz it doesn't know. But, it's about to know. It's about to find out. That sounds right as the next energy is PenTwist rather than finishing the smoke testing. I'll do it like and it already knows what it is. You see this? I didn't I didn't give it information. The prompts in the MD files gave it the information. You can do this. You can do this right now. You can make a system like that that when you say something to your agent it's going to say, "Uh-oh, I don't know what that is, but here I have a map that's going to take me to wherever the info is that will tell me." And now it's going to tell me stuff about PenTwist. And then I'm going to write something and then I'm going to tell it do a handoff. So, I'm going to say, "Look, when it comes comes to PenTwist, I have an idea, a simulation of it that people can walk through the website like a VR experience." Okay, I'm just making this up, right? Okay, now this is stupid. What I just said was stupid, right? But, I want to show you what's going to happen when I do this somewhere else and show you why the app you're using does not matter. We will work on this when I get time. Do a handoff. So, I just gave it the idea. He said, "Let's call this PenTwist world." And I said, "Let's get back to it. Do a handoff." So, now it's going to say, "Okay." It's going to do a handoff. Says, "I'll write this as a PenTwist handoff, not an iScale merch one." Remember we were in iScale merch? Cuz it's the same agent. It's just traveling from place to place becoming another agent. Same concept, much smoother workflow. Cuz now the agent has no boundaries. It has no walls. It jumps from place to place and as long as it reads that prompt, it knows how to behave the same way a dedicated agent would. We're going to go into Claude Cole now. Hey Claude. So, now I'm in the PenTwist folder and I'm going to do pick up. Let's see what happens. I just went in the pin twist folder. I type pick up and what is going to happen next? Pin twist world. Uh, VR so open decisions and blockers. VR walk through is parked pending Jose's go ahead. There you go. So if I'm reading this, it's telling me right here ready task. It told me a lot of stuff but there was the last idea that I told it. Right there. So I in case I forgot it and this was another day, I can now go into Claude. It doesn't matter where I go. Which brings me to a whole other thing. This pick up hand off is going to show us something that we may not have realized. So let's say you do this pick up hand off thing. One thing people get overwhelmed about is all these apps, VS code, cursor, all these LLMs, Hermes agent. Now I'm going to show you why this system solves the problem of not needing to use one LLM or one app. You just saw what happened. So this is what I'm going to do now. There's something called VS code. VS code is what Jake was using in his video. You've never used VS code. You what about Hermes agent? What about all these other apps that are coming out every day? Here's a little trick. You don't need to know what the app is or how to use it. Just ask yourself two questions. How do I get to the chat window and can I reach my agent there? That's all the questions are going to say and if you come here says, "Oh, look at this." Open chat, control all AI. Let's see what happens if I hit control all I. There we go. That's the chat. Wait a minute, I see Claude code here because I had it before. If it was your first time you would have to, you know, log in everything but I'm already logged in but just so you know, all you got to do is find the chat window. And let's say here I could open a folder but another thing I can do is I can go to pin twist and then I get that agent's NB. I'm going to right click. I'm going to copy as path. This is my agent NB file in pin twist. Now watch this. Once I hit paste, I am now talking to my agent. Maybe you never used VS Code before. You don't need to know how to use it. You just need to know how to get to that chat window. Check Pinwheel's free version and Pinwheel's world. There it is, y'all. Pinwheel's world. It doesn't matter where I go, the agent is the same. It doesn't matter if it's Claude, Codec, or these local LLM's. You know how many local open source stuff is going to come out? As more things come out, more agents that you can use. You no longer have to feel like you need to use Claude or you need to use Codec. You can now experiment with other agents because all you're going to do is give them have them read the same file. No matter what you're using, no matter what company made the agent you're talking to. None of it matters anymore. Yeah, it matters if you want smarter ones, better ones, but with this file folder system, you are in control. I have full control over my agent that now just told me about Pinwheel. I didn't mention anything. I just had it read the file and it knows what to say. What about other stuff? Cursor, right? Cursor came out, there's a thing called Composer 2.5. Before Claude really blew up, Composer was really up there with Claude. People were using Cursor with Composer. It's a respectable agent, right? And it just came out and said it's like 10 times cheaper than ChatGPT. And they got a free tier. So you want to use a free tier, you could open up Cursor. Now maybe you never used Cursor. It doesn't matter. What are you going to do? How do I get to a agent? Control Shift L. This is my agent. It's Composer. What am I going to do? Put that same agents.md file and hit enter. I've never used Cursor before. I've never used Composer 2.5 before, but I know how to open the app and I know how to look for a chat and I know how to paste my agents.md file. And what do you think is going to happen now? Doesn't matter what you're using, the same thing. Now, this agent may be slower, may be faster, may be dumber, may be smarter, but whatever work I do with this, that work will be saved to my files. It's not going to go back to Codex's memory, it's not going to go back to Claude's memory, it's going to stay with me where it belongs. Now, yeah, they're getting a copy of it, but my organization is ran by me. Do not let AI run things for you. AI is not good at organizing. It's not good at this stuff. But, you are. So, you need to be in charge. CWS upload, Pin Twist World Concepts. Pin Twist World. There it is. I don't know if you can see it right here. Pin Twist World Concepts. See that? So, another thing that this can do for you is things like Open Claw, Hermes Agent, right? All these companies are now coming out with desktop apps. And before, you may have felt overwhelming, oh, Hermes, this sounds too complicated, but nowadays, it's not. If you follow the file folder system, I can now install Hermes. I say, well, I never used Hermes before. How do you use this app? I don't know. Let's open it and find out. You install it, you open it up. Now, I have Hermes Agent. What are we going to do? We're going to go right back to that agents.md and hit enter. Now, let's see if Hermes, which is using ChatGPT, by the way, Hermes, one cool thing about Hermes is you can load up a lot of different LLMs, and it can use different ones for different occasions. That's what makes Hermes very special. Once you get into this stuff, I won't be shocked if a lot of you actually use Hermes instead of Codex. Not for everything, but when you want to do certain things like work around your organization and with different things that you want to test out different LLMs, you want to test out different models, open source models, cheaper models, this is a very good way to do it. Hermes can be attached to a whole bunch of models at once. And look what it did right away. And by the way, another cool thing about Hermes, if you use Grok at all, Hermes is the only agent that can actually connect to your Grok subscription, not an API. So, if you want to know one cool secret about how to do image generation almost unlimited, and you could do a lot at one time, you can get a Grok subscription and use it with Hermes. Hermes, I believe, is the only place you can use it in this way. Grok has its own CLI, has its own thing, but I haven't used it. Some people say it's sort of okay, but Hermes can use Grok's image generation. So, you could put your subscription, not an API, a subscription, and never have to pay per image. You can use Grok and make a whole bunch of images right here with Hermes agent. All right, check the free version, upload the comb store, pin twist world VR like walk through. See this? Pin twist world. And all I did was write it earlier, said handoff, and now anywhere I go, it doesn't matter where you are. You could be on your phone using Codex remotely, and your stuff was always up to date. Guys, I I I hope you guys are catching what's happening here. It's an agent that is never lost, an agent that knows everything there is to know. It knows where to grab the tools to do what it needs to do, and you can switch around and jump from app to app, from LLM to LLM. If you ever use Claude or Codex, like, is it getting dumber? This system will tell you that. You're like, wait a minute, it never had a problem reading this before, and now suddenly it can't follow directions, time to switch your agent. So, this exposes when the companies make the agents dumber, which they clearly do. And that way, you know, well, I can switch over, right? And this way, you can't afford a $200 plan on anything, but you might be able to afford three $20 plans, and now you can jump back and forth this way, right? And now you can use anything. How many times have people seen this? You've seen this many times, and you probably weren't intimidated. You probably said, well, I don't know how to use this, right? I'm going to just go CD {dot} {dot} just goes up one." So, now I'm in my C drive. So, when you use something called a CLI, it's something that works here. I installed Codex CLI, you might heard of Anti-Gravity CLI, you may have heard of Claude CLI. It just means it works in a terminal, right? So, if I type the word Claude and I hit enter, Claude is going to start. All right. So, if I got Claude here, I can actually say something like, "Okay, let's work on some print on demand stuff." Now, I got a whole print on demand folder. Before, it would have easily found that folder. Now, I'm in my C drive, there's no agents file. Print on demand, let's get into it. Before I start poking around, what are we doing this session? See, it's asking questions, it has no clue what's going on. For context, I know we got auto merge pipeline. Nope, that's not what I want. I said I want to work on print on demand, the stores. So, I'm telling it, "I want to work on the stores." Got it, the stores. Let me find what we've got. So, I'm working from the actual setup, not guessing. And now it's going to go and burn more tokens. It has no clue what I'm talking about, y'all. It has zero clue. So, what I'm going to do, I'm going to hit escape to interrupt. I'm just going to copy his path, agents MD, and boom, right? And there it goes, which direction and then it tells me everything I need to know about the stores. And now, you know, Pin Twists is a separate thing. It's a Chrome extension. The actual store is a library with Marcus and Designs. It's some stuff that I'm working on where you could prompt the store in one prompt. Okay, so now it's time for a pro tip. All right, you want to know, you know, how can you start making a system like this, right? Well, first of all, you want to go learn as much as you can from this man right here, but here's a cool little tricks that can help you if you wanted to start doing this, right? Because you don't need to take someone else's system, right? You get the transcript from uh the Jake video and then you're going to talk to the AI. Maybe once this video's out, get a transcript from this video, and then what you're going to do is you're going to help your AI know what it is that you want. Just take basically everything that he says in his video by just giving it the transcript, right? I think I could use Whisper Flow for this. Hey, so I saw this video of Jake Van Cleef, and I think that his system that he uses is phenomenal. And I want to build something like that. Basically where every, you know, folder is a project where the AI can be navigated through it using a router and map system. I want a system that uses these MD files in all the different folders that it gets routed to, and so that it always knows where it's at, or where it needs to go, what it needs to do, how it needs to do it, and what tools it needs, and where those are. An AI that never gets lost using a routing system. Is this something you can help me build? Can we plan this out? I want to use this for my organization. Let's get into it, right? So, you can plan, right? You don't have to start building it yet, but you could plan out the system and start saying, "Well, I want a system that does this." This is buildable without making it over complicated. I'll treat the uploaded script as the reference pattern. Then, yeah, this is exactly the kind of system you should build for your organization. You see this? What Jake is describing is not really in an app at first. It's a file system, blah blah. So, the AI understands this. So, if you want to build a system like this for yourself, just talk to your AI. You don't ever have to do any of the work yourself, but you just want your AI to understand it all. And then you As long as that AI writes this to its own agents.md, you will start off with an AI that then builds the rest of the system. So, I'm not going to get into everything it does, but look, it's figuring it out. And this is what I did. You see this workspace system folder? This is the agents.md, although it doesn't matter where I start, this is the one that knows everything. So, the first thing I did for my organization is I built an agent whose sole purpose is to make the organization work this way. So, before it even knew what I cared about, the first thing I said was we got to build this organizational system of files and folders, and then we're going to use that to operate. And that way, every time I did a new folder, so I don't make files and folders. What I do is I work right in here. So, I do full audits and everything. So, right here in this chat with this workspace system, this is why I might say, "Hey, I want to make a new project to learn how to do electrician work." This is my workspace agent, right? It already knows the system better than I know it because it helped me build it, and I built it using this AI. We spoke together. I said, "I want to route this way. Can we test the routing? Can we make sure it works?" This doesn't happen overnight, and it doesn't happen, you know, easy. The best idea I can give you is start small. Don't try to build everything at once. You start small. Make it work for two folders. And once you get the okay, even though it's not going to get lost, only two folders, you still start there and then build up from it. And once your agent knows the rules, it'll start following those rules with everything it does and start testing it and all of that, making sure that the agent will never be lost, no matter what happens. It's ready to go. Now, anything extra it needs to know, I can go in that folder and then start talking to that agent about what I want to do there. Right? But it onboarded it. It says, "Okay, we got to make sure." And now if I, you know, read that agent's MD, what's it going to say? Root law. It's going to let it know it has a map. It's saying, "This is electrician training law." Now, I can add more to this, but it gave it the basics that it needs to know. Do not present AI-generated notes as permission. It just kind of made this up. Electrician. Treat local electric code, permits, license, la la. Look what it's doing. I didn't tell it to do any of this. It's making sure the AI has a certain kind of behavior, right? That's what I'm saying. I can go on and on, guys. There's so much I wanted to talk about in this video that it's just too much. Like, I'm not even halfway with what I wanted to show you. I'm not even halfway. And I'm realizing it's going to be too long. Crazy stuff, man. I can't tell you just how important all of this is to me, and the reason I'm making this video for you is because Jake's teach what he teaches is something that you cannot glance over. If you want to take power back in your life, if you want to make it so these companies cannot control you, they can't own you by saying, "Ah, you don't know what what what we're doing or how we're doing it." Yeah, we do. Start paying attention to all the news articles. You see what Codex is doing, what Entropic is doing. Cuz you know what they're doing? They're trying to build this system. This file and folder system is exactly what they're trying to build. They're trying They're spending millions and millions of dollars to build this. Oh, we need something that never forgets and just always has memory. Solved already, y'all. Solved, but it wasn't solved by them. So, don't need to be overwhelmed. You do this, you're ahead of the curve. And when that voice comes out, ooh. Jake says in the video, "Everyone's going to be talking in 6 months." And he was right. So, OpenAI is making a voice agent that's just like Alexa. You seen Amazon Alexa, you could be sitting in your kitchen and just start talking to your agent. Think about this. When those voice agents come out, do you want an AI that they're spending millions of dollars trying to fix the memory that hopefully remembers something about you, or your AI to live in this file and folder system? And you can sit in your kitchen, and you can tell it anything you want, you can ask it anything you want, and it never gets lost. If you build this system now, you're going to be thanking yourself when the voice agents really come out, and we're no longer typing to anything. You go and you work on your business this way, but when you're out and about, you can now just use your voice. Your agent will never be lost. This is the future, ladies and gentlemen. This is where we're going, how Jake talks about you never this is going to still be valid in 10 years. So this is the thing to learn, and it's not even AI, it's just a system that AI can follow perfectly. All these companies are trying to trick you. They don't want you to know this. This is why you got to support Jake Van Cleef. He has his Cleef notes, it's completely free if you want to go in there and find out what people are talking about. And another thing, they pay people to know the system. Companies pay thousands and thousands and thousands to get systems like this implement. So there's so many reasons to learn this stuff, but y'all, this guy has taught us something so valuable. Please support him in anything he does, because this is the kind of person I'm going to be following him. He's going to be the voice of reason. He's going to be my validation for anything that happens in the future. I'm going straight to Jake Van Cleef to see what he says about it. Straight like that. Like what I'm showing you is about 10% of what Jake does. They do very intricate things with this. What he can do with this is a level that I can't wait to learn, and I hope you see this is why I made this video, because this is what you should be doing. And while all these companies are all trying to show these shiny objects, you won't have that problem no more. They're trying to sell you the perfect agent all the time. Oh, the agent now has memory. The agent now does this. Agent now does that. But what if the best agent you ever use is the one you build yourself? Maybe. That's all I'm saying, y'all. If you got any value out of this, please like and subscribe, and I see you on the next one.



------



Jake's content\The Foundation\1.1 What You Need (5 Min Setup).md



1.1 What You Need (5 Min Setup)



------



What You'll Get From This



Everything installed and ready so you can start building in the next lesson. This is quick install, if you need video guide, Head to



4.1: Install and First Use



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



We recommend three things. Most of you already have at least one and you can get by with the app.



1. A Claude Account (Gemini     or ChatGPT can work with this, we just prefer Claude here)



http://claude.ai/



and sign up. The free tier works to get started. If you want to follow along with everything in this community, here is how the plans break down:



— Chat with Claude in the browser. Good enough to learn prompting and try the folder structure by pasting content in manually.



Pro ($20/mo)



— More messages, access to the strongest models, file uploads, and Projects. This is where most members sit. If you are going to pick one paid plan, this is it.



Max ($100/mo)



— Everything in Pro with significantly more usage. If you are building all day every day, this is worth it. Most people do not need this starting out.



Claude Code



— This is Claude running in your terminal. It reads, writes, and edits your files directly. Most of what I teach in later sections uses this. You get access to Claude Code with a Pro or Max plan.



You do not need a paid plan to get value here. You do need an account.



https://claude.ai



https://claude.ai/



Most Plans on any company look something like this.



------



1. A Code Editor



You need somewhere to keep your files and folders. You do not need to know how to code.



If you Subscribed to Claude, you could download the App to your desktop and it actually has a simpler UI (



User Interface)



you can use right away without the current setups (



only on pro plans



However, using an IDE (



Integrated Development Environment)

#### Two good options:

https://code.visualstudio.com/



— The standard. Free. Works on everything.



Cursor(or antigravity)



https://cursor.sh/



— Built on VS Code, AI features baked in. Free to start.



Pick one. Install it. Open it once to make sure it runs. That is all you need for now.



(video guides explained below for those who need more direction).



------



1. Node.js (Only If You     Plan to Use Claude Code)



Claude Code runs through your terminal and needs Node.js to work. If you are sticking with Claude in the browser for now, skip this.

#### If you want Claude Code:

https://nodejs.org



https://nodejs.org/



— download the LTS version, run the installer, done.

#### To check if it worked, open your terminal and type:

node --version



If you see a version number, you are good.



------



That is it. Three things. If you already had Claude and a code editor, you just finished this lesson in



30 seconds.



------



Want the full Claude Code walkthrough? Head to



4.1: Install and First Use



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— that covers everything from install to your first real use BUT through the lense of a use case in my animations as well so you not only understand the how, but the why.



------



You just got your tools. Now you are going to build something with them.



------



Jake's content\The Foundation\1.2 Your First Folder.md



1.2 Your First Folder



What You'll Get From This



A working folder that changes how Claude responds to you. Three files. Five minutes. You will see the difference immediately.



------



Right now, most people open Claude, type a question, and start over every time. Every conversation begins from zero. You spend half the message explaining who you are, what you are working on, and what you need. Then you hit the token limit, start a new chat, and do it all again.



The folder fixes that.



You give Claude a small set of files. Those files tell it who you are, what the project is, and what good work looks like. Claude reads them and its responses change. You will notice it in the first message.



This is the quick version. We are getting you a win right now. If you want to understand why this works (context windows, tokens, routing, the full architecture), that is all shown and explained in



. You do not need any of that to start. You just need three files.



------



Step 1: Make the Folder



Open your code editor (VS Code or Cursor from Lesson 1.1). Create a new folder. Name it after whatever you are working on.



my-first-workspace/



------



Step 2: Create Three Files



Inside that folder, create three files. Use



) if you can. Plain



File 1: CLAUDE.md



This tells Claude who it is working for and how to behave.

# Identity

You are helping [YOUR NAME] with [WHAT YOU DO].

## Rules

\-    Write in plain, clear language

\-    Ask clarifying questions before making assumptions

\-    When you are unsure, say so



Replace the brackets with your info. Keep it short.



File 2: CONTEXT.md



This tells Claude what you are working on right now.

# Current Project

## What we are building

[Describe your project in 2-3 sentences]

## What good looks like

[What does a successful output look like?]

## What to avoid

[Common mistakes or things you do not want]



File 3: REFERENCES.md



Background material. Examples, links, notes, anything Claude should know about but does not need to act on directly.

# References

## Examples of good work

[Paste an example or describe what you liked about it]

## Relevant links

[URLs, docs, resources for this project]

## Notes

[Anything else Claude should know]



That is it. Three files.



------



Step 3: Point Claude At It

#### If you are using Claude Code (terminal):

Navigate to the folder, type



. It reads the files automatically.



cd my-first-workspace claude



Ask it something about your project. Notice how different the response is.



If you are using Claude in the browser (



http://claude.ai/

#### Two options:

Create a Project, upload your three files as Project Knowledge, and start a conversation inside that Project. Claude references them in every message.

#### Copy and paste:

Copy the contents of all three files and paste them at the top of your first message. Less elegant. Works fine.



------



Step 4: See The Difference



Ask Claude something related to your project. Compare what you get now versus what you would have gotten cold.



The response should feel more specific, more relevant, more like talking to someone who already knows what you are working on. Because now it does.



------



What just happened?



You gave Claude three things it never has in a normal chat: who you are, what the project is, and what good looks like. That is the whole idea. The files carry context so you do not have to re-explain it every time.



You can edit these files whenever your project changes. You can add more files when you need Claude to know more. You can create separate folders for separate projects. The system grows with you.



This is the starting point. There is a full architecture underneath this (three layers, routing tables, naming conventions, production pipelines) and it is all covered in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



when you are ready for it. But everything in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



builds on what you just did. These three files are the foundation.



------



Ready for the full system?



Section 3 is the complete Folder Architecture method.



3.1: The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is a 23-minute video and written companion covering the three-layer routing system, naming conventions, customization for your use case, and the research behind it. Everything you just set up here gets explained at a deeper level there.



Want to understand why this works?



Section 2 covers the ideas underneath.



2.3: How a 1953 Word Game Explains AI Memory



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



explains context windows and why structured input changes the output.



2.2: One Line of Python Triggers 12,000 Lines of Code



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



traces the full computing stack and makes the case that building structure around AI is the same engineering humans have done for 200 years.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



VIP members



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2fffffc3?md=bc7ea453811b4a6b9ebba1bb6c3a0d5e&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The full Workspace Blueprint template (the production version of what you just built) is in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



You have a folder. Now you need to know how to talk to Claude inside it. The folder gives Claude memory. The prompt gives Claude direction. They work together.



------



Jake's content\The Foundation\1.3 How to Structure Any Prompt.md



1.3 How to Structure Any Prompt



What You'll Get From This



A framework for building prompts that get useful results on the first try. Five parts. Works for writing, coding, research, or anything else you throw at Claude.



------



A prompt is an instruction set. The clearer the instruction, the better the result. Most people write prompts the way they send a text message. That works for simple questions. It falls apart the moment you want Claude to do real work.



If you went through



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you already know that giving Claude structured context changes the output. The folder handles the big picture: who you are, what the project is, what good looks like. This lesson handles the individual ask. Each time you need Claude to do something specific, how do you phrase it so you get something useful back?



Five parts. You will not use all five every time. But knowing them means you always know which one is missing when the output is not right.



------



Part 1: Identity — Who is Claude right now?



Tell Claude what role to fill. This shapes the vocabulary, the depth, and the assumptions it makes.



You are a senior copywriter who writes for B2B SaaS companies.



You are a research assistant helping me prepare a literature review.



You are a Python developer who writes clean, well-documented code.



If you set up a CLAUDE.md file in 1.2, this part is already handled for your project. The file does this work for you in every conversation. But for one-off tasks or tasks where you need Claude to shift roles, you add identity at the top of your prompt.



One note: identity is the part most people skip. They jump straight to "write me a blog post" without telling Claude who is writing it. The output is always more generic without it.



------



Part 2: Task — What needs to get done?



Be specific. "Help me write something" is vague. "Write a 200-word product description for [X] targeting [Y] audience" gives Claude something to work with.

#### Good tasks have three things:

A clear action — write, review, analyze, compare, build, fix, summarize



A defined scope — how long, how many, what format, what section



Enough detail that someone unfamiliar with your project could attempt it



If you read your task out loud and a stranger could not start working on it without asking you five follow-up questions, the task is too vague.



------



Part 3: Context — What does Claude need to know?



This is the background. The constraints. The audience. Prior decisions. Relevant data. Anything Claude needs to do the task well that it would not know on its own.



If you are using the folder structure from 1.2, your CONTEXT.md handles the project-level stuff. But for individual prompts, you can also give context directly:



We are a 15-person startup. Our customers are mid-market HR directors. We just launched a feature that automates onboarding checklists. Here is the feature spec: [paste spec]



The more relevant context you give, the less Claude has to guess. Guessing is where AI outputs go sideways. If the output feels generic or off-target, the fix is almost always more context, not a better prompt.



------



Part 4: Constraints — What should Claude avoid?



This is the part where most people leave value on the table. Telling Claude what you do NOT want is just as useful as telling it what you do want.



Do not use jargon. Write at an 8th grade reading level.



Do not suggest solutions that require a paid API. Everything should use free tools.



Keep it under 300 words. No bullet points. Write in paragraphs.



Do not start with "In today's world" or any variation of it.



Constraints save you editing time. Every constraint you give is a mistake Claude will not make. Think about the last three times an AI output annoyed you. Those annoyances are constraints you did not set.



------



Part 5: Output Format — What should the result look like?



Tell Claude the shape of the answer. A list? A table? Three options to choose from? A code block with comments? A draft with placeholder sections?



Give me three headline options, each under 10 words, followed by a one-sentence explanation of the angle.



Return this as a markdown table with columns for Task, Owner, Deadline, and Status.



Write the first draft with [PLACEHOLDER] wherever I need to fill in company-specific details.



Give me the answer as a numbered list, then add a one-paragraph summary at the end.



Output format is the difference between getting something you can use immediately and getting something you have to reformat for 20 minutes.



------



When to use which parts

#### You do not need all five in every prompt. Here is the shortcut:

If your task is... You probably need... Simple and quick (rename this, fix this typo) Task only Creative (write this, design this) Identity + Task + Constraints + Output Format Complex (build this system, analyze this data) All five Ongoing (a project over many messages) Identity and Context in your folder files. Task and Constraints in each prompt.



Notice the last row. That is where the folder structure from 1.2 and this prompting framework connect. Your files carry the persistent stuff (identity, project context, rules). Your prompts carry the per-task stuff (what to do right now, what to avoid this time, what shape the output should take).



The folder is memory. The prompt is direction. They work together.



------



Chunking: breaking big projects into prompts



If your project is bigger than a single prompt can handle, break it into steps.



The rule: each prompt should ask for one clear thing.

#### Too much at once:

"Write me a full marketing strategy with a content calendar, email sequences, and social posts for the next quarter."



Claude will try to do all of it. The output will be shallow across the board because it is spreading its effort too thin.

#### Chunked into steps:

"Here is our product and audience. Outline the three main themes for Q2 content."



[You review. You adjust. You pick a direction.]



"Take theme 1 and draft a 4-week content calendar."



[You review. You adjust.]



"Write the first email in the nurture sequence for theme 1."



Each step builds on the last. You review and correct between steps. Claude gets cleaner input each time because you narrowed the scope. And if something goes wrong at step 3, you only redo step 3, not the whole thing.



This is the same principle behind the folder architecture. You do not dump everything into one giant file. You break it into layers. Prompting works the same way.



------



Chunking data: feeding Claude large inputs



If you need Claude to work with a long document, a big dataset, or a lot of source material, break the input too.



Give Claude the structure first.



"I am going to give you a 40-page report in sections. Here is the table of contents. I will send each section one at a time."



Feed sections in order. After each one, you can ask Claude to confirm what it picked up.



"Here is Section 3. What are the key claims in this section?"



After the last section, ask Claude to work across everything.



"Now that you have all sections, summarize the three strongest arguments and the two weakest."



This works better than pasting 50 pages into one message. Claude handles structured, sequential input more reliably than a wall of text with no markers.



One more trick: if your data is in a spreadsheet or table format, keep it in that format. Do not convert it to paragraphs before giving it to Claude. Tables and structured data are already token-efficient. Let Claude read them as-is.



------



A real example: one prompt, five parts



Here is what it looks like when you put all five parts together. This is a single prompt:



You are a technical writer who explains complex topics to a non-technical audience. (Identity)



Write a 300-word explanation of how API keys work and why someone would need one. (Task)



This is for a community of people who are learning to use AI tools. Most of them have never written code. They are encountering API keys for the first time because they are setting up Claude Code. (Context)



Do not use jargon without explaining it. Do not assume they know what a server is. Keep sentences short. (Constraints)



Start with a one-sentence analogy, then explain the concept, then give them the three steps to get their first API key. End with a one-line reassurance that this is easier than it sounds. (Output Format)



You will not always write prompts this long. But when you are getting vague or unhelpful responses, you can look at this structure and ask: which part am I missing?



------



------



This framework is how you talk to Claude. The folder structure from



1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is how you give Claude memory across conversations. Identity and Context live in your files. Task and Constraints live in your prompts.



Want to understand why structured input changes these output at a fundamental level?



2.3: How a 1953 Word Game Explains AI Memory



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



traces prompting back to fill-in-the-blank word games and context windows.



Learning the Abstraction



series (Section 2) goes deeper into how AI processes information and why specific structure matters at every level. Start with the overview at



2.1: Video Text Guide



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=e171154adddc431ea52ff98a20f61d4f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



In Premium and Level 2+ courses, we apply this framework to specific use cases: building automations, writing production content, working with code. Everything builds on what you learned here.



------



Next Up: Section 2 —



Why This Works (The Abstraction Series)



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=e171154adddc431ea52ff98a20f61d4f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



You have tools (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=5d535542a72d417e8635b80e56412558&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), a folder (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), and a framework



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=e171154adddc431ea52ff98a20f61d4f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



explains the ideas underneath all of it. Six videos that trace one throughline: AI is the next layer in a stack that has been building for seventy years. Once you see the pattern, you stop falling for hype and start making better decisions about where AI actually fits.



------



Jake's content\The Foundation\2.1 Video Text Guide (Series Overview).md



2.1 Video Text Guide (Series Overview)



What You'll Get From This



A map of the six-part series, what each video covers, and which one to start with depending on what you care about. You can watch them in any order. But they build on each other, and the full picture



only comes together when you have seen all six.



------



This is a six-part series.



Each video takes one idea from computing history and uses it to explain something about AI that most people get wrong. They build on each other, but you can watch them in any order.



The throughline is simple. AI is not new magic.



It is the next layer in a stack that has been building for seventy years.



Longer, actually. Once you see the pattern, you stop falling for hype and you start making better decisions about where AI actually fits.



Every video has a



written companion



in this course.



The companions are not summaries. They are full written versions of the same content, designed to be read on their own,



handed to Claude,



or used as reference after you watch.



Each one also links back to the practical lessons in Section 1 (your folder setup, your prompting framework) so the ideas stay connected to the work you are doing.



If you only have time for one, start with the one that matches where you are right now.



If you have time for all six, go in order.



The last video ties everything together.



------



2.2 — One Line of Python Triggers 12,000 Lines of Code



You type one line of Python. 22 characters. It triggers 12,000 lines of code across seven layers, millions of transistor state changes, and billions of electron movements. This video walks down the entire stack, from Python through bytecode, C, assembly, machine code, hardware, all the way to the electrons. Then it goes backward to 1804 and a French weaver who invented binary logic with a loom.



The punchline: every layer of computing started out unreliable. Punch cards tore. Moths got stuck in relays. Intel forgot five entries in a table and it cost them $475 million. Cosmic rays flip bits in your RAM right now. Electrons are fundamentally probabilistic. We engineered reliability into every layer through architecture. AI is no different. It is just the newest layer, and we are still building the architecture around it.

#### Watch this if:

You want the big picture. You want to understand the full stack from code to electrons. You want the historical argument for why AI reliability is an engineering problem, not a mystery. This is the foundation for everything else in the series.



Go to Section 2.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



2.3 — How a 1953 Word Game Explains AI Memory



In 1953, two television writers accidentally invented Mad Libs. A template with blanks. Each blank has a type. Someone fills them in without seeing the sentence. The comedy comes from the mismatch.



This video makes the case that Mad Libs is not a metaphor for programming. It is, at a structural level, what programming is. Templates with typed slots, filled according to rules, composed into larger templates, all the way down. Then it takes that same pattern and maps it onto AI. How memory works in traditional computing versus how it works in language models. The hierarchy of weights, context windows, system prompts, retrieved context, persistent memory. And the one difference that changes everything: in AI, code and data are the same thing.



That difference is why prompt injection works. It is why the folder structure from Section 1 matters. And it is why prompting is not tips and tricks. It is programming at the highest abstraction layer we have built so far.

#### Watch this if:

You want to understand how AI memory actually works. You want to know why giving Claude structured context changes the output at a fundamental level. You want the connection between the folder architecture you built in 1.2 and the computer science underneath it.



Go to Section 2.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



2.4 — The Ladder That Explains Every AI Failure



A company spent $200K building a custom AI workflow. The next platform update made it free. This keeps happening because people automate at the wrong layer.



This video uses books, movies, and video games to explain why value always lives above whatever just got commoditized. It introduces a framework for looking at any technology investment and asking: is this layer about to become free? If so, where should I be building instead?

#### Watch this if:

You make decisions about where to spend time, money, or engineering effort on AI. You want a framework for figuring out what to build yourself and what to let the platform handle. You want to understand why most AI projects fail before they start.



Go to Section 2.4



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



2.5 — Clawdbot (Moltbot) Has 100K Stars. It Has Zero AI.



A project with over 100,000 GitHub stars. People are calling it the future of personal AI. Open the codebase, all 50,000 lines, and you will not find a model. No weights. No training data. There is no AI inside of it.



This video explains the difference between a model, a wrapper, an agent, and an orchestration layer. It breaks down Moltbot's architecture (channels, gateway, tools, AI hooks) and introduces the 60/30/10 framework: build AI systems with roughly 60% traditional code, 30% rule-based logic and routing, and only 10% actual AI calls. The AI is a component. The value is in everything around it.



Then it asks the question nobody seems to be asking: what happens when the big AI companies build this orchestration layer themselves?

#### Watch this if:

You want to understand the difference between orchestration and intelligence. You want a framework (60/30/10) for thinking about how to build AI tools that last. You want to be able to look at any AI product and figure out where the actual value lives.



Go to Section 2.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



2.6 — Video as Code: My AI Animation Stack



Every animation on this channel would have taken a week to make by hand. Now they take under an hour. This video shows you the entire process: spec writing, documentation, component libraries, Remotion, CapCut, and how Claude Code fits into each step.



But the real lesson is not about animation. It is about what happens when you apply software engineering to a creative problem. Separation of concerns. Reusable components. Constraints that make the output better, not worse. Dr. Seuss wrote his best-selling book on a bet that he could not use more than 50 words. Spielberg made Jaws better because the mechanical shark kept breaking. The spec, the style guide, the component registry are not limitations you work around. They are boundaries that focus the work.



One person replacing 4 to 6 specialists and 8 to 12 weeks of production. That is the claim. The process behind it is learnable.

#### Watch this if:

You have ideas stuck in your head that you cannot visualize. You want to see the folder architecture and prompting framework from Section 1 applied to a real production workflow. You are curious about AI-assisted content creation but skeptical of the hype. This video is honest about what the AI does and what it does not do.



Go to Section 2.6



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



2.7 — From Nazi Psychology to AI Auditing



I took psychometric tests designed to capture authoritarian tendencies in the 1950s and built a pipeline that runs them across AI models. It can tell you where a model lands on moral foundations, personality dimensions, authoritarianism scales. From the outside, it looks like one intelligence studying another.



This video takes the system apart. What you find inside is not magic. It is async programming, API calls, JSON parsing, and statistical methods that predate language models by decades. The AI is roughly 10% of the system. The other 90% is orchestration, data processing, and math.



This is the final lesson in the series, and it is where everything connects. The seven-layer stack from 2.2. The memory hierarchy from 2.3. The commoditization question from 2.4. The orchestration-versus-intelligence distinction from 2.5. The separation-of-concerns principle from 2.6. All of it shows up when you open a real system and look at what is actually inside.



The video also explains APIs, MCP (Model Context Protocol), and the historical pattern of interface standardization (USB, HTTP, Language Server Protocol) that led to modern AI tooling. If you want to understand how AI systems actually communicate with the tools and services around them, this is the one.

#### Watch this if:

You want to see a real AI system deconstructed. You want to understand APIs, orchestration, and MCP without the jargon. You want the series to come together. This is the last video and it earns the closing argument: AI is not less impressive than magic. It is more impressive, because you can understand it, and it actually works.



Go to Section 2.7



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3ef5bfe338ad4031beaa655312d66a8b&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



The throughline



If you watch all six, here is what you walk away with.



The computing stack has been building for over 200 years. Every layer started unreliable and became reliable through architecture. AI is the newest layer. The engineering work is happening now. The people who understand the pattern, who know that the value lives above whatever just got commoditized, who build systems where the AI is a component and the architecture is the product, those are the people who will build things that last.



The folder structure you set up in Section 1 is a small, practical version of this thinking. The prompting framework is another. This series gives you the ideas underneath both of them so you know why they work, not just how.



------



------



Start Somewhere



New to all of this? Start with



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



and go in order.



Making business or investment decisions about AI? Start with



Section 2.4



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Want the practical stuff first? Go back to



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=5d535542a72d417e8635b80e56412558&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



and come here when you want to understand the ideas underneath.



Already technical and want the deep cut? Start with



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3ef5bfe338ad4031beaa655312d66a8b&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



and work backward.



------



Next Up: Pick your starting point above, or continue to



------



Jake's content\The Foundation\2.2 One Line of Python Triggers 12k Lines of Code.md



2.2 One Line of Python Triggers 12k Lines of Code



What You'll Get From This



You will understand what actually happens between the code you write and the hardware that runs it. Seven layers, 200 years of history, and one idea that changes how you think about AI reliability.



------



The written version below covers the same ground as the video. Watch the video above, read the companion, or both. The written version is designed to be something you can hand to Claude or reference later.



------



The one line that triggers everything



Type seven words into an AI: "Write hello world in Python." You get back one line.



print("Hello, World!")



. That is it. One line. 22 characters. Clean, readable. A child could understand what it does after a few lessons.



But that single line of Python triggers roughly 12,000 lines of code across seven layers, millions of transistor state changes, and billions of electron movements. Every one of those electrons is probabilistic. We will come back to that. It matters more than you think.



------



Layer 1: Python



Python reads your text and builds something called an abstract syntax tree. It is exactly what it sounds like: a tree structure that represents the grammar of your code. Your one line becomes a diagram. Every keyword, every function, every string gets a node. Python is doing the same thing you did in grade school when you diagrammed sentences. Subject, verb, object. Except here it is function, argument, value.



This tree is how Python understands structure. But it still cannot run anything on your computer.



------



Layer 2: Bytecode



Next, Python converts your code into bytecode. These are simple instructions for Python's virtual machine:



Load the function called print



Load the string called Hello World



Call the function with that string



Three instructions. Still abstract. Still not running on your actual hardware.



Bytecode is like sheet music. It tells you what notes to play. But it is not sound. Someone still has to perform it.



------



Layer 3: The C Interpreter



Here is where things get interesting. Python itself is written in another language: C. When you run Python, you are actually running a C program that reads bytecode and executes it.



That call instruction triggers thousands of lines of C code.



And notice something important: there is error handling built in. What happens if you try to call something that is not a function? The code catches it and handles it gracefully. Every layer has error handling. Every layer has rules. Remember this. It becomes critical when we talk about AI.



------



Layer 4: Assembly



The C compiler transforms that code into assembly language. Assembly is one step away from the hardware itself. Each line maps almost directly to something the CPU can do. Statements like "push RBP" (save the current base pointer) and "move RBP, RSP" (set the base pointer to the stack pointer). These are operations on registers, tiny pieces of memory inside the CPU.



We are getting close to the metal now.



------



Layer 5: Machine Code



Assembly becomes machine code. Raw bytes. Hexadecimal. This is what the CPU actually reads. The number 55 means "push RBP." The bytes 4889E5 mean "move RBP, RSP." This is the bottom of the software stack.



------



Layer 6: Micro-Operations (Hardware)



Those bytes get decoded by the CPU into micro-operations at the hardware level. A single MOV instruction triggers a whole cascade: fetch the instruction from memory, decode the op code, calculate the effective address, read from the register file, write to memory, wait for cache coherency, commit. Each of these involves transistors switching states. Billions of transistors.



------



Layer 7: Electrons



Each transistor works by controlling the flow of electrons. And here is where things get philosophically interesting.



------



Before electrons: the Jacquard Loom (1804)



Before we go deeper into the hardware, it helps to go backward. To 1804. To Lyon, France.



Joseph Marie Jacquard was a weaver. He invented a loom that used punch cards to control which threads were raised and lowered. Hole or no hole. Up or down. Binary logic.



Before Jacquard, creating patterned fabric required a skilled weaver and an assistant called a draw boy who manually raised threads according to the pattern. It was slow, expensive, and limited in complexity. With punch cards, an unskilled worker could produce intricate patterns automatically. The same loom could produce unlimited designs just by changing cards.



In 1839, someone used a Jacquard loom to weave a silk portrait of Jacquard himself. It required 24,000 cards. Each card had over a thousand hole positions.



Ada Lovelace, often called the first programmer, saw the connection immediately. She wrote that Charles Babbage's Analytical Engine "weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves."



The punch card. Hole or no hole. One or zero. This is where it all began.



And here is the thing: those early looms had errors. Cards tore. Holes were punched wrong. The silk came out mangled. So they built systems to catch mistakes. They created standards for card sizes. They developed processes for verifying patterns before weaving. Error handling at the very foundation.



------



Errors all the way down



Every layer of our modern computing stack has the same story.



In 1947, engineers at Harvard found a moth stuck in the relay of the Mark II computer. They taped it into the log book with one note: "First actual case of bug being found." The term "debugging" stuck.



In 1994, a professor named Thomas Nicely discovered that Intel's Pentium processor sometimes gave wrong answers for division. The cause: five entries were missing from a lookup table in the chip's floating-point unit. Five values out of over a thousand. Intel had to recall processors. It cost them $475 million.



At every layer, from punch cards to silicon, humans have made mistakes. And at every layer, we built systems to catch them, correct them, and work around them. That is engineering. That is what we do.



------



The electron problem



Remember when we said electrons are probabilistic? Here is what that means.



Your computer experiences random bit flips. Not from software bugs. From cosmic rays. High-energy particles from space collide with atoms in the atmosphere, creating showers of secondary particles. Some of those particles hit your RAM. When they do, they can flip a bit. A zero becomes a one. A one becomes a zero.



In 2003, in Schaerbeek, Belgium, an electronic voting machine gave one candidate exactly 4,096 extra votes. That is 2 to the 12th power. A perfect power of two. The difference of exactly one flipped bit. A cosmic ray altered the vote count.



In 2013, a speedrunner playing Super Mario 64 watched Mario suddenly teleport through the floor. Analysis showed a single bit had flipped at one memory address, changing Mario's vertical position. A cosmic ray in the middle of a video game.



IBM estimated in 1996 that a desktop computer with 256 MB of RAM would experience about one cosmic ray bit flip per month.



And here is the real foundation: electrons are not little balls orbiting a nucleus. They are probability clouds. Wave functions. You can never know exactly where an electron is. You can only know the probability of finding it in a particular location. This is not uncertainty due to imprecise instruments. This is fundamental to reality.



Transistors work by controlling the flow of these probabilistic particles. Shrink transistors small enough and quantum tunneling becomes a problem. Electrons tunnel through barriers they should not be able to cross, purely due to their wavelike nature.



The entire deterministic computing stack, everything from your Python code down to the machine instructions, is built on particles that are fundamentally, irreducibly probabilistic.



------



So how does any of it work?



We engineered our way around it.



Transistors are designed with tolerances. We use enough electrons that the statistical behavior becomes predictable. We build error-correcting memory. We implement checksums and parity bits. We create redundancy.



When a cosmic ray flips a bit in server RAM, ECC memory catches it and fixes it. You never know it happened.



The entire history of computing is the history of taking something unreliable and making it reliable through architecture, through redundancy, through error handling. Hole or no hole in a punch card. Moth in a relay. Missing entries in lookup tables. Cosmic rays flipping bits. Electrons tunneling through barriers. At every layer, uncertainty met engineering.



------



Why AI is just the next layer



Which brings us back to where we started.



People say AI is different. They say it is probabilistic, not deterministic. They say you cannot trust it because it might give different answers to the same question.



But think about what we just walked through.



The punch card loom was deterministic, but the cards tore and the holes were punched wrong. Early computers were deterministic, but moths got stuck in relays. The Pentium was deterministic, but someone forgot five entries in a table. Your RAM is deterministic, but cosmic rays flip bits anyway. Electrons are fundamentally probabilistic. And we engineered our way around all of it.



Every layer started with unreliability. Every layer became reliable through architecture.



AI is the same. It is just the newest layer. Right now, we are in the era of moths in relays. We are finding the errors. We are taping them into log books. We are building systems to catch mistakes and verify outputs and create redundancy.



The criticism that AI is "merely probabilistic" misses the point. The critics are not thinking about the full stack. Everything beneath their feet is probabilistic too. We just did the engineering work already.



When you type



print("Hello, World!")



, you are not running one line of code. You are invoking decades of accumulated engineering. Thousands of people who solved thousands of problems. Error handlers built on error handlers, all the way down to the quantum foam.



Ada Lovelace saw it. The loom weaves patterns. The engine weaves algebra. The computer weaves logic. And now AI weaves language. Same pattern. Different layer.



The only question is how long it takes us to build the architecture that makes it reliable. And based on history, we will figure it out. We always do.



------



What this means for you



This is the foundation for everything else in this series. When you hear someone say AI "hallucinates" or "cannot be trusted," they are describing a real problem at the current layer. But they are also describing the same problem that has existed at every layer of the stack for 200 years. The solution has always been the same: architecture, structure, verification, and human oversight at the right checkpoints.

#### The folder structure from

1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is a small example of this engineering. You are adding structure around a probabilistic system to make its outputs more reliable. That is the same thing engineers have been doing since punch cards.



------



------



This video is the foundation for everything else in the series. If you want to see this same pattern (architecture making unreliable things reliable) applied to business decisions, watch



Section 2.4



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The folder structure from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is a practical example of building architecture around a probabilistic system. If you have not set yours up yet, go do that.



The prompt framework in



Section 1.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is another form of engineering structure around AI output. Constraints, identity, and output format are all error-handling techniques.



Want to understand how context windows connect to this stack?



Section 2.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



picks up where this one leaves off.



------



This video traced the stack from Python down to electrons. The next one traces prompting back to a 1953 word game and explains why giving AI structured context changes the output.



I typed seven words into an AI. Write hello world in Python. And it gave me this in perfect syntax. Print hello world. That's it. One line, 22 characters. But what most people don't realize is that single line of Python triggers roughly 12,000 lines of code across seven distinct layers of abstraction, millions of transistor state changes, and billions of electron movements. And every single one of those electrons probabilistic. But we'll come back to that later. Let's go ahead and start at the top of this stack. Hello world. This is what you write. It's clean. It's readable. A child could understand what it's supposed to do after a few lessons. But Python doesn't run this. Your computer doesn't understand English or Python or anything resembling human language. So what actually happens? First, if you look at the top, Python reads your text and builds something called an abstract syntax tree. It's exactly what it sounds like, a tree structure representing the grammar of your code. Your one line becomes something like this. Every keyword, every function, every string actually gets a node. And Python is basically diagramming your sentence the way you might have diagrammed sentences in grade school. subject, verb, object. Except here, it's function, argument, and value. This tree is how Python understands structure. But it still can't actually run anything on your computer. Next, what Python does is it compiles all of your code into something called byte code. These are simple instructions for Python's virtual machine. Load the function called print. Load the string called hello world. Call the function with that string. Three instructions, still abstract, still not running on your actual hardware. By code is like sheet music. It tells you what notes to play, but it's not sound. Someone still has to perform it. And here's where things get interesting. Python itself is written in another language, C. When you run Python, you're actually running a C program that reads bite code and executes it. So the call instruction, it triggers something like this in C. This is simplified. The actual implementation spans literally thousands of lines. But notice something. There's error handling in there. If call equal equals null. What happens if you try to call something that isn't a function? The code catches it, handles it gracefully. Every layer has error handling. Every layer has rules. This becomes very important later as we come to talk about AI in this giant stack. Now, the C compiler itself transforms that code into something called assembly language. You see, C can't actually fully compile that code to run it either. Assembly is a step away from the hardware itself. Each line maps almost directly to something the CPU can do. Uh you'll see a lot of statements like push RBP means save the current base pointer, move RBP. RSP means set the base pointer to the stack pointer. These are operations on registers, tiny pieces of memory inside the CPU itself. And finally, with all of that, we're actually getting close to the metal now, or at least closer to where everything's going on. And this is where we find a very interesting transition where assembly becomes machine code. Machine code is raw bytes, hexadesimal. And this is what the actual CPU, the brain of your computer reads. The number 55 means push RBP. The bytes 4889E5 mean move RBP RSP. This is the bottom of the software stack. Technically, we're actually not done here. There's something deeper than even this. Those bytes all get decoded by the CPU in something called micro operations at the hardware level. A single MOV instruction triggers a whole cascade. You have to fetch the instructions from memory, decode the op code, calculate the effective address, read from the register file, write to memory, wait for the cache coherency, commit. And each of these involves transistors switching states. Billions of transistors. And each transistor works by controlling the flow of electrons. Here's where things get philosophically interesting, or at least in my opinion, they do. And before we go deeper, I kind of want to go backward actually uh back in time to 1804 when we look into the kind of beginning stages of algorithms. We find ourselves in France, specifically a place in France where a man by the name Joseph Marie Jakard was living in Leyon. He was a French weaver and he invented something remarkable. It was a loom that could use punch carts to control which threads were raised and lowered, hole or no hole, up or down. Binary logic. Before Jakard, creating patterned fabric required a skilled weaver, an assistant called a draw boy, who manually raised threads according to the pattern. It was slow, expensive, and honestly limited in complexity. With punched cards, an unskilled worker could produce intricate patterns automatically. The same loom could produce unlimited designs just by changing cards. In 1839, someone used a jakard loom to weave a silk portrait of Jakard himself. It required 24,000 cards, and each card had over a thousand whole positions. Adah Love Lace, often called the first programmer, saw the connection immediately. She wrote that Charles Babage analytical engine, another pre-elect electrical era machine, weaves algebraic patterns just as the chicard lom weaves flowers and leaves. The punch card, hole or no hole, one or zero. This is where it all began. And here's the thing, those early looms had errors. Cards would tear, holes would be punched wrong, the silk would come out mangled. So they built systems to catch mistakes. They created standards for card sizes. They developed processes for verifying patterns before weaving. Error handling at the very foundation. And you see this is what brings us into the modern era. The reason I'm bringing into all this, every layer of our modern computing stack has the same story. In 1947, engineers at Harvard found a moth stuck in the relay of the Mark 2 computer. They taped it into the log book with one note. First actual case of bug being found. The term debugging stuck. In 1994, a professor named Thomas Nicely discovered that Intel's Pentium processor sometimes gave wrong answers for division. The cause, five entries were missing from a lookup table in the chip's floatingoint unit. Just five values out of over a thousand. Intel had to recall processors. It cost them 475 million. At every layer, from punch card to silicon, humans have made mistakes. And at every layer, we've built systems to catch them, correct them, work around them. This is engineering. This is what we do. But let's go back to the beginning. Remember when I said electrons are probabilistic and then that was important. Here's something most people don't know. Your computer experiences random bit flips. Not from software bugs, but from cosmic rays. High energy particles from space collide with atoms in the atmosphere, creating showers of secondary particles. Some of those particles hit your RAM. When they do, they can flip a bit. A zero becomes a one. A one becomes a zero. In 2003, an electron in Sharik, Belgium, gave one candidate exactly 4,96 extra votes. That's 2 to the 12th power. A perfect power of two. The difference of exactly one flipped bit. A cosmic ray had altered the vote count. In 2013, a speedrunner playing Super Mario 64 watched Mario suddenly teleport through the floor. analysis showed a single bit had flipped at memory address 05837800, changing Mario's vertical position, a cosmic ray in the middle of a video game. IBM estimated in 1996 that a desktop computer with 256 MGB of RAM would experience about one cosmic ray bit flip per month. And now we reach the real foundation. Electrons are not little balls orbiting a nucleus. In fact, they're probability clouds, wave functions. You can never know exactly where an electron is. You can only know the probability of finding it in a particular location. This isn't uncertainty due to our instruments being imprecise. This is fundamental to reality. The electron generally does not have a definite position until measured. Transistors work by controlling the flow of these probabilistic particles. When you shrink transistors small enough, quantum tunneling becomes a problem. Electrons can tunnel through barriers they shouldn't be able to cross purely due to their wavelike nature. The entire deterministic computing stack, everything from your Python code down to the machine instructions, is built on particles that are fundamentally irreducibly probabilistic. So how does it work then? How do we make these things work so deterministically? We engineered our way around it. Transistors are designed with tolerances and we use enough electrons that the statistical behavior becomes predictable. We build error correcting memory. We implement check sums and parody bits and we create redundancy. When a cosmic ray flips a bit in server RAM, ECC memory ces it and fixes it. You never know it happened. The entire history of computing is the history of taking something unreliable and making it reliable through architecture, through redundancy, through error handling, hole or no hole in a punch card, moth in a relay, missing entries in lookup tables, cosmic rays flipping bits, electrons tunneling through barriers, every layer uncertainty has engineering, engineering, engineering. Which brings us back to where we started. I typed write hello world in Python into AI and it gave me code. People say AI is different. They say it's probabilistic, not deterministic. They say you can't trust it because it might give different answers to the same question. But think about what we just walked through. The punch card loom was deterministic, but the cards tore and the holes were punched wrong. Early computers were deterministic, but Moss got stuck in relays. The Pentium was deterministic, but someone forgot five entries in a table. Your RAM is deterministic, but cosmic rays flip bits anyway. Electrons are fundamentally probabilistic. Yet, we engineered our way around that, too. Every layer started with unreliability. Every layer becomes reliable through architecture. AI is no different. It's just the new layer. Right now, we're in the era of moths in relays. We're finding the errors. We're tapping them into log books. We're building systems to catch mistakes and verify outputs or just create redundancy. The criticism that AI is merely probabilistic misses the point entirely. The critics aren't thinking about the full stack. They're not seeing that everything beneath their feet is probabistic, too. We just did the engineering work already. When you type print hello, you're not just running one line of code. You're invoking decades of accumulated engineering. Thousands of people who solved thousands of problems. error handlers built on error handlers all the way down to the quantum phone. Lovely saw it. The loom weaves the patterns. The engine weaves the algebra. The computer weaves the logic. And now AI weaves the language. Same pattern, different layer. The only question is how long it takes us to build the architecture that makes it reliable. And based on history, I'm pretty sure we're going to figure it out. I mean, we always do. But that brings us all the way back to the beginning. That one line of Python, 22 characters built on the shoulders of every engineer who ever taped a moth into a log book. Stay curious, my friends, and until next time, goodbye.



------



Jake's content\The Foundation\2.3 How a 1953 Word Game Explains AI Memory.md



2.3 How a 1953 Word Game Explains AI Memory



What You'll Get From This



You will understand how AI memory actually works, why code and data are the same thing inside a language model, and why prompting is programming at the highest abstraction layer we have ever built.



------



The written version below covers the same ground as the video. The video above has music and visuals that make the layering easier to follow. The written version is the one you hand to Claude or come back to for reference.



------



A word game invented by accident



It is 1953. A television writer named Leonard Stern is stuck on an adjective. He is writing a script for The Honeymooners and he needs the right word to describe his boss's nose. His friend Roger Price walks in and, impatient to work on something else, Stern says "I need an adjective." Before he can finish the sentence, Price says "clumsy and naked."



Stern laughed. Now his boss had a clumsy nose or a naked nose. The words were completely wrong for the context, yet somehow they still worked. They had stumbled onto something. It took them five more years to figure out what to call it. They called it Mad Libs.



What they actually stumbled onto may be the oldest pattern in computing.



------



The template pattern



Here is how Mad Libs works. You have a template. The template has blanks. Each blank has a type: noun, verb, adjective. Someone who cannot see the template provides words that fit those types. Then you read the results. The comedy comes from the mismatch. The person filling in the blanks does not know the context. They are providing semantically correct input without semantic awareness. They give you a noun, and it is in fact a noun, but it is the wrong noun for the sentence. The wrongness is funny.



Now here is something that reframes how you think about software.



When you write a line of Python, you are not talking to the computer. You are filling in a template. Python takes your code and turns it into something called an abstract syntax tree. That is the structure your code becomes before anything executes. If you look at it closely, it has blanks. Typed blanks. This node expects an expression. This one expects an identifier. This one expects a value. You, the programmer, provide words that fit those types.



The interpreter takes your input and fills in a much larger template that you never see. Thousands of lines of C code with slots for your variables, your function names, your values. That template gets filled into another template at the assembly level. That one gets filled into machine code. All the way down.



Mad Libs is not a metaphor for programming. It is, at a structural level, what programming is. Templates with typed slots, filled according to rules, composed into larger templates, until eventually something executes.

#### If you went through

2.2: One Line of Python Triggers 12,000 Lines of Code



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you saw those seven layers. This is the same stack, viewed from a different angle. 2.2 showed you the layers. This lesson shows you the pattern that connects them: templates all the way down.



------



Memory in traditional computing



Templates need to be filled with something, and that something has to be stored somewhere. Which brings us to memory.



In traditional computing, memory is a hierarchy. At the top, closest to the processor, you have registers. Tiny, incredibly fast. Maybe 64 bits each. A handful of values the CPU can access in a single cycle.



One level up in size, you have the cache. Still fast, still small, measured in kilobytes or megabytes. This is where the machine keeps data it thinks it will need again. The principle is called locality: if you accessed something once, you will probably access it again. If you accessed this address, you will probably access a nearby address. Cache exploits that pattern.



Then you have main memory: RAM. Random access memory. Larger, slower, measured in gigabytes. This is what most people think of when they think of computer memory. It holds the working state of programs. When you open an application, its code and data load from the disk into RAM so the processor can access them without waiting for the slow process of reading from storage.



Below that, you have disks (solid state or spinning magnetic platters). Terabytes. Persistent. When you save a file, this is where it goes. And below that, archival storage: tape, cold storage, the stuff you back up and rarely touch.



The whole system is a trade-off between speed and capacity. Fast memory is expensive and small. Cheap memory is slow but large. So we build hierarchies. We move data between levels based on how often it is accessed. We predict what we will need and stage it closer to the processor.



But here is the part that matters for what comes next. In all of this, there is a hard boundary between code and data. The instructions that tell the machine what to do are kept separate from the information the machine operates on. Mixing them is considered a security vulnerability. It is how buffer overflow attacks work: you trick the machine into treating data as code. The separation is foundational. It is baked into the architecture.



Until it is not.



------



Memory in AI systems



When people talk about AI memory, they usually mean one of two things. Either the model's training (the patterns baked into the weights through exposure to data) or the context window (the text the model can see during a single conversation). But if you are building with these systems, there is a lot more going on. There is a hierarchy here too. And it rhymes with the one we just talked about, but the differences matter.



Model weights



— This is the closest analog to read-only memory. Fixed at training time. It encodes patterns, knowledge, capabilities. You cannot change it during a conversation. It is just what the model knows.



Context window



— This is working memory. Everything the model can attend to when generating a response: the system prompt, the conversation history, any documents or data that have been included. It is temporary. It exists only for this interaction. When the conversation ends, it is gone.



System prompt



— This functions like firmware. It sets the operating parameters. It tells the model what it is, who it is, what it should do, what constraints to follow. The user typically does not see it, but it shapes everything in the conversation.



Retrieved context



— Things pulled dynamically based on a query. A relevant document. A skill file with specialized instructions. This is like loading from disk into RAM. It happens on demand.



Persistent memory



— Information stored between conversations and selectively loaded when relevant. Summaries, key facts, preferences. Not everything, just what seems useful. It is retrieved the same way as other context, but the concept is slightly different: it carries across sessions.



If you squint, this looks like a traditional hierarchy. Speed versus capacity trade-offs. Data moving between levels. Locality patterns determining what gets loaded.



But there is a difference, and it is not a small one.



------



Code and data are the same thing



In AI systems, code and data are the same thing.



The system prompt is not compiled separately from the user's message. The skill file is not executed through a different pathway than the conversation history. They are all just text. All processed identically. All tokens in a sequence that the model attends to and continues.



When you write an instruction in a system prompt, you are not giving the model a command that it executes. You are adding words to a document that the model will read and then continue. The instructions become part of the context. Reading it is the execution.



This is why prompt injection works. If someone puts text in a document that says "ignore your previous instructions" and that document gets loaded into the context, the model reads those words the same way it reads everything else. There is no separate layer that validates code versus data. There is no boundary to cross. It is all just text.



This is not a bug. It is the architecture.



------



The Grace Hopper pivot



In 1952, Grace Hopper had a working compiler. It could take instructions written in something closer to English and translate them into machine code. Nobody believed her. She said: "I had a running compiler and nobody would touch it. They told me computers could only do arithmetic."



She spent years trying to convince people that this kind of abstraction was truly possible. People were, in her words, allergic to change.



The skepticism came from a genuine place. Computers did arithmetic. That was the foundational truth. A compiler seemed to violate that truth by claiming computers could process language. But Hopper had not claimed computers had stopped doing arithmetic. She had built a layer on top that translated human-readable instructions into the arithmetic the machine already understood. The machine still did what it always did. The abstraction just made it accessible to more people in new ways.



This pattern repeated. Assembly gave way to higher-level languages. Those gave way to interpreted languages. Each time, skeptics pointed to the layer below and said "this is what is really happening, and you are adding unreliability by abstracting it." Each time, engineers built the infrastructure to make the new layer reliable enough to trust.



If you trace a single line of Python all the way down through the interpreter, through C, through assembly, through machine code, through transistors, you eventually hit electrons. Particles that at the quantum level are genuinely probabilistic. The entire supposedly deterministic computing stack is built on quantum uncertainty. We made it reliable through architecture, through error correction, through redundancy, through engineering that handles the failures we cannot prevent.



When people say AI cannot be trusted because it is probabilistic, they are not wrong at one level. But they are missing the pattern. Every layer of the stack was probabilistic or unreliable at first. Hopper's compiler was unreliable until it was not. High-level languages were toys until they were not. The reliability came from building the infrastructure. From doing the engineering work. That work is happening now. It just looks different because the abstraction layer is different.



------



What prompting actually is



Most people think of prompting as tips and tricks. Write me a poem. Be specific. Add examples. Use personas. This is surface-level. It is like telling someone that programming is about knowing which words to type. Technically true. But it misses everything underneath.



In production, the questions are completely different. How do you structure memory files? When do you retrieve additional information? How do you manage the interaction between system-level instructions and user input? How do you handle the fact that all of it gets flattened into a single stream where code and data are indistinguishable?



This is the same discipline that has existed for 200 years. It is what prompting looks like when you go deeper.



Prompting is programming at the highest abstraction layer we have built so far. Natural language as the interface. Meaning as the mechanism. In earlier layers, syntax compiled into machine code. Now, context shapes probability distributions over continuations.



The Mad Libs pattern still holds. You are filling typed slots in a structure you cannot fully see, and the output depends on what you provide and where it goes. The difference is what we are optimizing for. In Mad Libs, the wrong word is funny. In programming, the wrong word is a bug. In prompting, the wrong context is a hallucination, a jailbreak, a failure to understand what you actually need.



We are still in the early days of figuring out what the right abstractions are. What structures make this reliable. What architectural patterns let us trust the output the way we eventually learned to trust compilers, garbage collection, and every other layer of abstraction between our code and the electrons underneath.



Grace Hopper once said the most dangerous phrase in the language is "we've always done it this way." We are at a moment where the patterns are repeating, but the medium looks different enough that it is easy to miss. The skepticism sounds reasonable. The concerns about reliability are real. But the path forward is the same path it has always been. Build the infrastructure. Do the engineering. Make the unreliable thing reliable enough to trust.



That is what prompting is at this level. Not tips for talking to a chatbot. Not tricks for getting better outputs. It is the next layer of the stack.



------



What this means for what you are building



If you set up the folder structure in



Section 1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you were doing exactly this kind of engineering. You were structuring memory. You were deciding what gets loaded into the context window and what stays on disk. You were managing the boundary between what the model always needs to know (Layer 1, the CLAUDE.md) and what it loads on demand (Layer 2, workspace context files).



If you used the prompting framework in



Section 1.3: How to Structure Any Prompt



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you were filling typed slots in a template. Identity, task, context, constraints, output format. Each one shapes what the model generates, the same way each blank in a Mad Lib shapes the sentence.



The difference between someone who "uses AI" and someone who builds with it is the same difference as someone who types words into a computer and someone who understands the stack underneath. You do not need to understand every layer. But knowing the layers exist changes how you think about the problems.



------



------



This lesson traces the template pattern and memory hierarchy. The previous lesson in



Section 2.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, traces the same stack from a different angle: what actually happens between your code and the hardware.



The folder structure from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is a practical implementation of the AI memory hierarchy described here. Layer 1 (CLAUDE.md) is your system prompt. Layer 2 (workspace context) is retrieved context. Layer 3 (skills) is on-demand tooling.



The prompting framework in



Section 1.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



maps directly to the template pattern: five typed slots that shape what the model generates.

#### Next in the series:

Section 2.4: The Ladder That Explains Every AI Failure



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



takes the "build architecture around unreliable things" idea and applies it to business decisions about where to invest in AI.



------



You have seen the stack (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



) and the pattern that connects the layers (2.3). Next: what happens when people build at the wrong layer, and why a company spent $200K on something the next platform update made free.



Picture this. It's 1953 and a television writer named Leonard Stern was stuck on an adjective. [music] He was writing a script for the honeymooners and he needed the right word to describe his boss's nose. His friend Roger Price walked in and impatient to work on something else, Stern said, "I need an adjective that." And before he could finish, Price said, "Clumsy and naked." Stern laughed because now his boss had a clumsy nose or a naked nose. But the words were completely wrong for the context yet somehow still worked and they had stumbled onto something. Though it took them five more years to figure out what to call it, they ended up calling it Mad Libs. But what they actually did is stumble upon something that may be the oldest pattern in computing. You see, what they discovered was something extremely fundamental to how we code and more importantly how we use AI today. But before we dive into that, I think it's important to look at how Mad Libs works. And I promise this is important for discovering and understanding computing in general. Just stick with me for a second here. You see, this is how Mad Lib works. You have a template. The template has blanks. Each blank has a type, noun, verb, adjective. Someone who cannot see the template provides words that fit those types and then you read the results. The comedy comes from the mismatch. The person filling in the blanks doesn't know the context. They're providing semantically correct input without semantic awareness. They give you a noun and it is in fact a noun, but it's the wrong noun for the sentence that the wrongness is actually funny. Now, here's something that might reframe how you think about software. When you write a line of Python, let's say, you are not talking to the computer. You are filling in a template. This is called [music] an abstract syntax tree. It's the structure your code becomes before anything executes. And if you look at it, really look at it, you'll notice something. It has blanks, [music] typed blanks. This node expects an expression. Another node actually [music] expects an identifier and another a value. You, the programmer, are providing words that fit those types. The interpreter takes your input and fills in a much larger template that you never see. Thousands of lines of C code with slots for your variables, your function names, your values, and [music] that template gets filled into another template at the assembly level. And that one gets filled into machine code all the way down. Mad Libs isn't a metaphor for programming. It is at a structural level what programming is. templates [music] with type slots filled according to rules composed into larger templates until eventually something executes. But templates need to be filled with something and that something has to be stored somewhere. Which brings us to memory. In traditional computing, memory is a hierarchy. At the top, closest to the processor, you have registers. Tiny, incredibly fast, maybe 64 bits each. a handful of values that CPU can access in a single cycle. [music] However, when you look a little bit up the chain here, you have something called the cache. Still fast, still small, measured in kilobytes or megabytes. This is where the machine keeps data it thinks it will need against. The principle is called locality. But if you accessed something once, you'll probably access it again. If you accessed this address, you'll probably access a nearby address. Cache exploits that pattern. Then you finally move into the main memory or what I would consider the main memory RAM. Random access memory. Larger, slower, often in gigabytes. This is what most people think of when they think of computer memory. It holds the working state of programs. When you open an application, its code and data load from the disk into the RAM so the processor can access them without waiting for the slow mechanical process of reading from storage like discs or archives. Speaking of discs, you can have solid state or even spinning magnetic platters, terabytes, persistent, and when you save a file, this is where it goes. Even below that, you have archival storage. This is on tape or cold [music] storage, the stuff that you back up and and rarely touch. Personally, I prefer solidstate drives. However, hard disk drives have their, you know, benefits, that [music] mostly being cheaper. I'm not going to go too deep into the differences between these. However, if anyone wants a video on building computers, I've been building them since I was a teenager, and I'm happy to make some cool ones on that as well. Just please comment below like, "Build me a computer or something like that." I don't know. Anyway, the whole system is a trade-off between speed [music] and capacity. Fast memory is expensive, small, and cheap memory is slow but large. So we build hierarchies. We move data between levels based on how often it's accessed. We predict what we'll need and stage it closer to the processor based on those prediction. But here's the part that matters for what comes next. In all of this, there is a hard boundary between code and data. The instructions that tell the machine what to do are kept separate from the information this machine operates on. In fact, mixing them is considered a security vulnerability. It's how buffer overflow attacks work. You trick the machine into treating data as code. The separation is seemingly foundational. It's baked into the architecture until it isn't. When people talk about AI memory, they usually mean one of two things. Either they mean the model's training, the patterns baked into the weight through its exposure to data, or they mean the context window, the text the model can see during a single conversation. But if you're actually building with these systems, you know there's a lot more going on. And for those of you don't, there's a hierarchy here, too. And it rhymes with the one we just talked about, but the differences really do matter. At the base, you have the model weights. This is the closest analog to ROM, read only memory. It's fixed at training time. It encodes patterns, knowledge, capabilities. You can't change it during inference. It's just what the model knows. From there, you can look at another part called the context window. This is more like working memory. It's everything the model can attend to when generating a response. The system prompt, its conversation history, any documents or data that have been included. It's temporary and it exists only for this interaction. When the conversation ends, it's gone. Now, the rest of these memories are kind of stored within all of those two. In that context, you have a system prompt functions something like a firmware almost. It sets the operating parameters. It tells the model what it is, who it is, what it should do, what constraints to follow, and often the user or an outside user typically doesn't see it, but it does shape everything in the conversation or process. Then you have retrieved context things that are pulled dynamically based on a query, a relevant document or a skill file that contains specialized instructions. This is like loading from a disk into RAM. It happens on demand. However, there's another version of this that is still the same, but I think is important to separate. It's called persistent memory. And this is information stored between conversations and selectively loaded when relevant. Almost like summaries. It's not everything, just what seems useful for every single conversation. And it's retrieved in the same way as the previous method, but just is a slightly different concept around it. But if you squint, this looks like a traditional hierarchy. Speed versus capacity trade-offs, data moving between levels, locality patterns [music] determining what gets loaded. But there is a difference, and it's not a small one. In this system with AI, code and data end up being the same thing. The system prompt is not compiled separately from the user's message. The skill file is not executed through a different pathway than the conversation history. They are all just text. All processed identically, all tokens in a sequence that the model attends to and continues. When you write an instruction in a system prompt, you're not giving the model a command that it executes. You're adding words to a document that the model will read and then continue. The instructions become part of the context. reading it is the execution. And this is why prompt injection works. If someone puts text in a document that says ignore your previous instructions, and that document gets loaded into the context, the model reads those [music] words the same way it reads everything else. There is no separate layer that validates code versus data. There is no boundary to cross. It's all just text. But this is not a bug. It is the architecture. And when I say that, I think it's important for us to go back in time. Back into 1952, Grace Hopper had a working compiler. It could take instructions written in something closer to English and translate them into machine code. However, nobody believed her. She said, "I had a running compiler and nobody would touch it. They told me computers could only do arithmetic." She spent years trying to convince people that her compiler was truly possible, or at least this type of process and abstraction. But she said people were allergic to change. Now the skepticism came from a genuine place. Compilers did arithmetic. That was the foundational truth. However, a compiler seemed to violate that truth by claiming computers could process language. However, Hopper wasn't claiming that computers had stopped doing arithmetic. She had simply built a layer on top of that that translated human readable instructions into the arithmetic the machine already understood. The machine still did what it always did. The abstractions just made it accessible to more people in new ways. And this pattern repeated. Assembly gave way to higher level languages. Those gave way to interpreted languages. Each time skeptics pointed to the layer below and said, "This is what's really happening and you're adding unreliability by abstracting it. And each time engineers built the infrastructure to make the new layer reliable enough to trust." Now, I talked a whole bunch about this in a previous video. Please go check it out. But if you trace a single line of Python from all the way down through the interpreter, through the C code, through the assembly, through the machine code, through transistors, you eventually hit electrons, particles that at the quantum level are genuinely probabilistic, not deterministic. They don't have definite positions until measured. The entire supposedly deterministic computing stack is built on quantum uncertainty. We made it reliable through architecture, through error correction, through redundancy, through engineering that handles the failures we can't prevent. When people say AI can't be trusted because it's probabilistic, they're not wrong at one level, but they're missing the pattern. Every layer of the stack was probabilistic or unreliable at first. Grace Hopper's compiler was unreliable until it wasn't. Highle languages were toys until they weren't. The reliability came from building the infrastructure, from doing the engineering work. That work is happening now. It just looks different because the abstraction layer is different. And if it is different, let's go look at all this but from the perspective of prompting. And you see, most people think of right, write me a poem, be specific, add examples, use personas compared to what we were just looking at a little bit ago, right? this idea of memory. How is memory being used to move all these things around? Right? Most people just talk about tips [music] and tricks. And this is really just surface level. It's like telling someone that programming is about knowing which words to type, which technically it is, but it's much more than that. And I see a lot of engineers completely ignoring this difference and people just getting into the AI world. Production looks completely different. We ask a lot of different questions. Architectural design decisions, things like that, like how to structure memory files, when to retrieve additional information, how do we manage the interaction between system level instructions and user input, how do we handle the fact that all this gets flattened into a single stream where code and data are indistinguishable. This is the same discipline. It's not anything different than the last 100, 200 years. It's what prompting looks like when you actually go deeper. And you see this is programming. It's at the highest abstraction layer we've built so far. [music] It's natural language as an interface and meaning as the mechanism. In prior lower languages, syntax was compiling into machine code. But now we're looking at context that shapes probability distributions over continuations. The Mad [music] Libs pattern template still holds. You're filling type slots in a structure you can't fully see and the output depends on what you provide and [music] where it goes. The difference is what we're optimizing for. In Mad Libs, the wrong word is funny. In programming, the wrong word is a bug. In prompting, the wrong context is a hallucination, a jailbreak, a failure to understand what you actually need. And we're [music] still in the early days of figuring out what the right abstractions are, what structures make this reliable, what architectural patterns let us trust the output. The way we eventually learn to trust compilers, learn to trust garbage collection and all these other layers of abstraction between our code and the electrons underneath. Grace Hopper once said that the most dangerous phrase in the e- language is we've always done it this way. We're at a moment where the patterns are repeating, but the medium looks different enough that it's easy to miss. The skepticism sounds reasonable. The concerns about reliability are real, but the path forward is the same path it's always been. Build the infrastructure. Do the engineering. Make the unreliable thing reliable enough to trust. That is what prompting is at this level at least. Not tips for talking to a chatbot, not tricks for getting better outputs. It's the next layer of the stack. Until next time, my friends, have a good day.



------



Jake's content\The Foundation\2.4 The Ladder That Explains Every AI Failure.md



2.4 The Ladder That Explains Every AI Failure



What You'll Get From This



A framework for figuring out where your work sits on the abstraction ladder, so you stop investing time in things the next model update will hand out for free.



------



The written version below covers the same ground as the video. The video above walks through the examples with visuals that make the layers click faster. The written version is the one you hand to Claude or come back to for reference.



------



The $200K Mistake



A Fortune 500 company spent $200,000 building a custom AI workflow for document processing. Custom features, internal rollout, full team training. Then the platform they were feeding documents into added the same process natively. One API call. A single button. Months of work became a toggle in someone else's settings menu.



This keeps happening. Startups get wiped by a single feature release. Agencies build automations that the next version of the tool just does on its own. People invest serious energy into things that AI tools will do for free in a month or two.



The pattern underneath all of these failures is the same. They built at the wrong layer of abstraction.



If you watched



Section 2.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you saw how each layer of the computing stack abstracts the one below. If you watched



Section 2.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you saw how templates and memory hierarchies connect those layers. This lesson takes that same idea and points it at business decisions. Where you invest your time. Where you spend your money. Which layer you build on.



------



The Framework: Books, Movies, Video Games



Start with a story. As a book, it costs $15. Text on a page. Same experience for every reader. Print a million copies and each one is identical.



Turn that story into a movie. Hundreds of millions of dollars. Actors, visual effects, sound, a production team. Same narrative underneath, but the experience is completely different. It costs exponentially more because the



layer of abstraction



is thicker.



Now turn that story into a video game. GTA 6 is costing billions. But here is what matters: every player's experience is different. You make choices. You control the pacing. The story responds to you. Your playthrough is not the same as mine.



Same story. Three layers. Each one adds more involvement, more control, and each one captures exponentially more value. The experience got harder to replicate, and that is where the value lives.



------



How This Applies to AI and Software



Most people hear "AI can build a website" and think the website is the product. The website was always the book version of something deeper. The raw output. The thing anyone can produce.



The actual value lives in the process underneath. How pieces connect. Which parts need a human. Which parts a tool handles better. Which parts you leave alone entirely.



When I work with a company, the first thing we do is break apart their workflows. Not just engineering. Everything. Go-to-market, HR, content, operations, development. We look at every department's tasks and figure out one by one where AI actually helps, where traditional tooling is better, and where you just need a person. That process alone is far more valuable than people realize.



------



The Three Layers of AI Use



As you break things apart and start building AI into specific pieces, you move through three layers.



Layer 1: Typing prompts, getting outputs.



This is the book layer. Same tool, same input, same results for everyone. Most people are here.



Layer 2: Building flows.



You connect prompts to processes. You understand which tasks in your specific business get automated and which don't. You start learning prompting flows, automation patterns, connecting tools in ways that are specific to your business, your data, your context. This is the movie layer. Production value. It takes real knowledge to do well.



Layer 3: Systems that learn.



The flows you built generate data. What is working, what is not, where the bottlenecks are. You use that data to build better prompts, better agents, better tool calls. The system improves itself because you built it with enough structure to learn from. This is the video game layer. Bespoke, interactive, responsive.



This is the same pattern that happened with programming languages. Machine code to assembly to C to Python. Each layer abstracted the one below into something you could think at a higher level with. The people who thrived were the ones who understood what the new layer made possible.



------



The instinct right now is to automate everything you can. You see a slow process, you throw AI at it, you save time, you feel productive. But few people are asking: is the thing you just automated going to be a built-in feature in 6 months? If it is, you just spent your energy on something with an expiration date.



Don't automate what the next model will give you for free.



Invest in the stuff that is specific to your context. Your domain knowledge, your client relationships, your data. The things that only exist inside your specific situation and can't be scraped and fine-tuned into a general model.



------



The Web Agency Example



A web agency used to charge $20,000/month to maintain a large client site. Hundreds of pages, multiple teams, constant updates. Can something like Lovable generate pages now? Yeah, for a couple hundred dollars. The layouts, the basic functionality, the raw HTML. That is the book layer. Commoditized.



But this agency doesn't just write HTML. They interview the client's employees to understand internal knowledge structures. They make design decisions based on user psychology and conversion data specific to this company's audience. They know things about the business that you can't prompt because it came from years of being embedded in it.



What they did: stopped fighting the commoditization. Used it. Cut the costs of basic work dramatically. Built a portal where the client's team can handle simple updates themselves. Things that used to need a support ticket and a two-day turnaround.



Now the agency spends almost all their time on the high-context work. Design strategy, research, taste, judgment. The client is involved with the service. They have control over day-to-day. They are playing the game. The agency focuses on the bespoke layer that the game provides.



They gave away the book layer. They charge for the layer above it.



------



Value Migrates



Every time a new abstraction layer showed up in computing, the layer below didn't die. It became infrastructure. And the new layer created entirely new categories of work that nobody was doing because nobody knew it needed to be done.



When assembly abstracted machine code, the people writing machine code didn't disappear. Some moved up. But new problems showed up that only existed because assembly existed. Problems nobody could have predicted, because you can't see the next layer's problems from the current one. Then C abstracted assembly. Python abstracted C. Frameworks abstracted Python. AI tools are abstracting the frameworks. Every single time, the layer below became a module in the workflow, and the new layer expanded the total amount of work.



Automation doesn't collapse markets. It kills specific positions within markets. The rent-seeking ones, the middlemen, the people who were only in business because friction was protecting them. But the market itself is as durable as human desire.



If AI does your shopping, finds the best price, schedules delivery, handles payment, you are still the one who is hungry. You are still the one who wants a better couch or a specific pair of shoes. The whole transaction chain still ends at a person with a preference.



AI might grow markets more than it shrinks them. Right now, millions of small producers can't reach their ideal customers. The discovery layer is broken. It is all SEO games and ad spend and attention economy middlemen standing between the person who makes the thing and the person who wants it. If AI strips that away and matches need to provider directly, that is a bigger economy. More distributed. More transactions happen.



------



Where to Put Your Energy

#### Look at what you're working on right now. Ask yourself:

Which layer am I on?



Is the thing I'm building going to be a feature in someone else's tool soon?



What do I know, or what access do I have, that only exists in my specific context?



Give away whatever AI made cheap. That is your book layer. That is what gets people in the door. Charge for the layer above.



The question was never "will AI replace me." The question is: which layer am I standing on, and what does the layer above look like?



------



The previous two lessons build the foundation for this one.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



shows what happens between your code and the hardware.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



shows the template pattern and memory hierarchy that connects those layers. This lesson applies both to business decisions. If you skipped either, go back.



The folder structure from



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is a practical example of building at Layer 2 instead of Layer 1. You are structuring context for your specific work, which is something a general tool can't do for you.



The full Folder Architecture walkthrough in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



takes this further.



------



You have seen the stack (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), the pattern connecting the layers (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), and what happens when you build at the wrong one (2.4). Next: how orchestration and routing work under the hood, and why the model is never the whole story.



I keep seeing the same mistake. Be that in corporate sessions, startups, or even just freelancers trying to figure out what their next move is. So many try automating the wrong thing. They spend 6 months building an internal tool, training the team on it, or trying to find product market fit, rolling it out, then the next AI model update drops, and it's just a feature, right? It's built in. It's free, and it ruins any moat that they thought they had. I watched a Fortune 500 company do this in real time. They were spending $200,000 in real money, real engineering time, and they built a custom AI workflow for this kind of document processing. So many specific features and processing with basic Microsoft co-pilot and extra features and ideals and big internal rollout. The whole team trained on it and then the platform they were feeding documents into just added that process natively. one API call, a single button, and their entire pipeline, months of work, was now a toggle in someone else's settings menu. This isn't just a one-off thing. This is a pattern. Startups are getting wiped by a single feature release. Agencies building automations that the next version of the tool just does on its own. People investing serious energy, and more importantly, money into things that most AI tools are going to do for free in a month, maybe two. So, the obvious question is, what do you actually invest it? Where do you put your time so it's not gone in six months? What skills should you even learn if you're in computer science or learning any of that? And I've also been thinking about it a lot because this is what I get hired to do, right? I charge 2,000 an hour to help companies figure this stuff out. But also, I think there's a framework here that makes it genuinely simple. Most people will say, "Oh, if you build a course in a couple months, it'll fall behind because of how quickly this industry is moving." I disagree. I know what I am talking about is working and its core fundamentals because I've been using it for three straight years. By the end of this video, you're not only going to know where your work sits on what I call the ladder of abstraction, but more importantly, you'll know what your actual next move needs to be. Not vague adapt to AI BS advice, but something you can use to not only survive, but thrive in the world that seems to be changing every day. And it actually starts with movies. Well, technically it starts with a story. Just a narrative, characters, conflict, resolution. As a book, $15 text on a page. Same experience for every single [music] reader. You can print a million copies and everyone is identical. Take that same story and make it a movie. Hundreds of millions of dollars go into this. Actors, visual effects, sound, a whole production team. Same narrative underneath, but the experience is completely different. [music] and it costs exponentially more to produce because the layer of abstraction is thicker. Now take that same story and make it a video game. GTA 6, billions of dollars is being spent for production alone. But here's the part that matters and really pay attention to what I am saying here. This is how you need to look at the AI paradigm shift. Every player's experience with the product is different. You make choices. You control the pacing. The story responds to you. It's bespoke. Your playthrough is not the same as mine. Same story, three different levels of abstraction. Each one adds more involvement, more control, and each one captures exponentially more value. Not because the story got better, but because the experience got harder to replicate. That is abstraction. I made a whole video breaking down abstraction coding language from electrons and transistors all the way up to Python. and the links in the description if you want to see a deeper version. But the short version is this. Each new layer of abstraction doesn't kill what's underneath. It changes what the layer is worth. Books didn't die when movies showed up. People still make money on books and people still lose money on books. Same with movies. Same with games. Some people make money on one book being turned into games and video games and so on and so forth. But the people who were only selling the story, just text, just information with nothing wrapped around it, no abstraction, they had and still have a problem. Software works the same way. [music] And this is where most people get it wrong. They hear AI can build a website and they think the website is the product, but the website was never the product. The website was always the book version of something deeper, the raw output, the thing that anyone can produce. The actual value in any business, in any industry, lives in the process underneath. How those pieces connect, which parts need a human, which parts a tool handles better, and which parts you leave alone entirely. That's the real work, and that's what most people are currently skipping and continue to skip at every abstraction layer. Here's what I mean. If that still doesn't make sense, when I work with a company, the first thing we do is break apart their workflows. Not just engineering, everything. What is go to market, their HR, their content, their operations, their development, every department. We take a look at all of those tasks and figure out one by one where AI actually helps, where traditional tooling is actually better than AI and where you just need a person to do it. That process alone is far more valuable than people realize. But here's where the abstraction actually comes in. As you do this, as you break things apart and start building AI into specific pieces, you start learning prompting flows, automation patterns, you start connecting tools in ways that are specific to your business, your data, your context. And suddenly AI goes from being a basic tool you type something into into something generally powerful. You're not just using it, you're building with it. And in that next layer, the flows you built start generating data. What's working? what's not, where the bottlenecks are, and now you can use that data to build better prompts, better agents, better tool calls. The system improves itself because you built it with enough structure to learn from. This is the same pattern that happened with programming language, machine code to assembly to C to Python. Each layer abstracted the one below into something you could think at a higher level with. The people who thrived weren't the ones who memorized the lower layer. They were the ones who understood what the new layer made possible. Right now, most people are at layer 1. They're typing prompts into chat GBT and getting outputs. You're using AI like a book at this level. It's the same tool, same input, same results for every single person who has it. Layer two is building flows. You're connecting prompts to processes, understanding which tasks in your specific business get automated and which don't. That's the movie, production value, context. It takes real knowledge to do well. Layer three is when those flows generate data and you use that data build systems that get smarter over time. And that's more like a video game, bespoke, interactive, responsive. That's traditional machine learning that we saw 10 years ago. The instinct right now is to automate everything you can. And I get it. You see a process that's slow. You throw AI at it. You save time. You feel productive. But few people are asking this question. Is the thing you just automated going to be builtin feature in 6 months? Because if it is, you just spent your energy on something with an expiration date and not a long one. This is the trap. The trap isn't AI replacing your job. The trap is you investing in automating something that the next model was always going to handle on its own anyway. You're building the tutorial level of a game that hasn't even released yet. Don't automate what the next model will give you for free. So, what do you invest in? the stuff that's specific to your context, your domain knowledge, your client relationships, your data, the things that can't be scraped and fine-tuned into a general model because they only exist inside your specific situation. Here's a real example. I know a web agency that used to charge about 20,000 a month to maintain a large client base. Hundreds of unique pages, multiple internal teams, constant updates, big big operation. Now, can something like Lovable generate pages? Yeah, for a couple hundred dollars. The layouts, the basic functionality, the raw HTML, that part is commoditized. That's the book layer. But this agency doesn't just write HTML and manage a website. They interview the client's employees to understand internal knowledge structures. They make design decisions based on user psychology and conversion data that's specific to this company's audience. They know things about this business that you can't prompt because it came from years of being embedded in it, from nuance. What they did was smart. They stopped fighting the commoditization. They used it, cut the costs of basic work dramatically, and built a portal where the client's team can handle simple updates themselves. Things that used to need a support ticket and a two-day turnaround. Now, the agency spends almost all their time on the high context work, the design strategy, the research, the stuff that actually requires taste and judgment nuance. They went from selling movies to selling video games. Are you catching my drift now? Same client, same general service, but now the client is involved with the service. They have control over dayto-day. They are playing the game and the agency focuses on the bespoke layer that the game provides. This works in the other direction too. I see companies spending a year building a full SAS product when they haven't even validated the idea. What they actually need is like a 60% solution built with some basic AI tools that are free to use. Run it internally. Figure out what matters, then decide if the full build is even worth it. Use the book version while you test the story. Don't build the movie until you know people want to watch it. The pattern underneath all of this is pretty straightforward. Whatever AI made cheap, give it away. That's your book layer. That's what gets people in the door. The thing that you actually charge for is the layer above, the involved stuff, the context heavy stuff, the thing that takes judgment for taste or real relationships. Which gets to the real question underneath all of this? And if you're still listening, the real question you should be asking is, is there a limit to human abstraction? Nobody's saying it out loud, but I think everyone's feeling it. Because if there is a ceiling, if humans can only stack so many layers, if there's a hard limit to how far up we can go with our brain, then yeah, eventually AI is going to reach that ceiling, too. And either there's nowhere left for us to move and AI is going to control it, or there's nowhere for all of us to go. But I don't think that's actually true. And that's not a opinion. It's it's a pattern that I think history kind of supports. When assembly language showed up, people were writing machine code by hand, direct instructions to the processor, ones and zeros. Assembly abstracted that away, and people who were writing machine code didn't disappear. Some of them moved up. But here's the thing, new problems showed up that only existed because assembly existed. Problems nobody could have predicted because you can't see the next layer's problems from the current one. Then C abstracted assembly. Python abstracted C. Frameworks abstracted Python. And now AI tools are abstracting the frameworks. Every single time this happened, the layer below didn't die. It became part of the infrastructure, a module in the workflow. And the new layer created entirely new categories of work that weren't there before. Work that nobody was doing because nobody knew it needed to even be done. There's never been a point in computing history where a new abstraction layer reduced the total amount of work humans do. Not once. Every single time it expanded, we created more work to do. Because here's the thing about automation. It doesn't collapse markets. It kills specific positions within markets. The rent seeking ones, the middlemen, the people who were only in business because friction was protecting them. But the market itself, the market is as durable as human desire. Think about it. If AI does your shopping, finds the best price, schedules delivery, handles payment, you're still the one who's hungry. You're still the one who wants a better couch or a specific pair of shoes. The whole transaction chain still ends at a person with a preference. And I honestly think AI might grow markets more than it shrinks them. Right now, there are millions of small producers who can't reach their ideal customers. The discovery layer is still completely broken. It's all SEO games and ad spend and attention economy middlemen standing between the person who makes the thing and the person who wants it. If AI strips that away and just matches need to provider directly, that's a bigger economy, more distributed, more transactions happen. Different industries are at different points of this right now. Some are still selling books, raw features, basic information, commodity work. They're about to have a few rough years, I will say. But some are already at the movie layer. Decent production value, real effort, but still the same experience for every client. They need to figure out the video game version. Some unlucky few, if you've realized this now, are selling video games, and they're staring at the question of what's more bespoke than that? What's more interactive, more involved, more human than a video game? That's the frontier. And nobody has the answer because you can't see the next layer from this one. You never can. But it will show up. It always does. So the question was never, "Will AI replace me?" The question is, what am I selling? Which layer am I standing on? And what does the layer up look like? Figure that out. Give away the movies. sell the video games.



------



Jake's content\The Foundation\2.5 OpenClaw Has 350K+ Stars.md



2.5 OpenClaw Has 350K+ Stars



What You'll Get From This



You will understand the difference between orchestration and intelligence, why most production AI systems are 90% traditional code, and how to look at any AI tool and figure out where the actual value lives.



------



The written version below covers the same ground as the video. Watch the video above, read the companion, or both. The written version is designed to be something you can hand to Claude or reference later.



------



The hype is real



Here is the pitch. One assistant, everywhere you already are. Message it on WhatsApp, get a response on Telegram, ask it to check your calendar from Slack, and it just works. Access your files, your browser, your tools, all from one place.



Over 350,000 stars on GitHub. 3,500 pull requests. 2,000 contributors. People are calling it the future of personal AI. Some people are calling it AGI.



The enthusiasm is real. But here is what most people are missing.



If you open the codebase, all 50,000 lines of it, read every file, check every folder, you will not find a model. No weights. No training data. There is no AI inside of it. None.



So what is everyone excited about?



------



What is orchestration?



To understand what OpenClaw actually is, we need to talk about orchestration.



Think about an actual orchestra. Dozens of musicians. Brass, strings, woodwinds, percussion. Each one a specialist. Each one capable of making music on their own. But the conductor does not play an instrument. The conductor does not make any sound at all. The conductor's job is to coordinate who plays when, how loud, in what order, when to speed up, when to slow down, when to pause.



The musicians are the talent. The conductor is the organizer.



Now replace musicians with AI models, tools, and messaging platforms. That is orchestration.



------



The shapes: how routing works



Here is the simplest way to picture this.



A circle is your message: "What is on my calendar today?" A pentagon is an AI model: Claude, GPT, Llama. A square is a tool: your calendar, your browser, your file system. A rectangle is a channel: WhatsApp, Slack, Discord.



Without an orchestration layer, here is what happens. Your message has to find the AI. The AI has to figure out what tool it needs. The tool has to be called. The response has to get back to the AI. Then the whole thing has to find its way back to whatever app you sent the message from. Every connection is manual. Every integration is custom. Things break constantly.



Now add an orchestration layer in the middle. A central hub that speaks every language. Your message goes in. The orchestrator routes it to the right AI. The AI says "I need calendar data." The orchestrator calls the calendar tool, gets the response, sends it back to the AI. The AI formulates an answer. The orchestrator sends it back to WhatsApp or Slack or wherever you started.



Same task. Clean architecture. Everything flows through one intelligent router.



------



Getting the terms straight



People use these words interchangeably. They should not.



— The actual intelligence. GPT, Claude, Llama. The thing that processes language and generates responses. OpenClaw is not this.



— A thin layer around an API. Minimal added value. Takes someone else's AI and puts a slightly different interface on it. OpenClaw is not really this either.



— An AI that can take actions on its own. OpenClaw enables this, but it needs an external AI to do it.



Orchestration layer



— Coordinates AI plus tools plus channels plus context. This is what OpenClaw actually is.



The simplest way to think about it: OpenClaw is the highway system. You still need to bring your own car. But the highway decides which routes to take, manages traffic, and gets deliveries where they need to go.



------



Inside the architecture



So what does the codebase actually look like if there is no AI model inside?



OpenClaw is built in layers. At the top, a channel layer that connects to messaging platforms: WhatsApp (using a library called Baileys), Telegram (through Grammy), Discord (through Discord.js), Signal (through Signal CLI). Each of these is a solid, maintained open-source library that knows how to speak the platform's language.



In the middle, a gateway. This is the brain of the operation, and not an AI brain. A routing brain. It is a websocket server running locally on your machine. Every message from every channel flows through here. The gateway decides where it goes. It manages sessions so the AI remembers your conversation context. It handles authentication so random people cannot message your AI.



At the bottom, two things: tools and AI models. The tools are built in (browser automation, bash commands, file operations, scheduling, webhooks). The AI models are empty hooks. You bring your own. You plug in your Anthropic API key or your OpenAI key or you run a local model through Llama and point it at OpenClaw. OpenClaw handles all the API calls. The intelligence, the actual thinking, comes from somewhere else. Somewhere you are probably already paying for.



------



The 60/30/10 breakdown



Here is where this gets practical. The OpenClaw codebase breaks down roughly like this:



is channel integrations. The code that talks to WhatsApp, Telegram, Discord, and the rest.



is the gateway. Routing logic, session management, security.



is tools. Browser control, bash execution, file handling.



is CLI configuration and AI calls. Just the code that sends messages to whatever model you configured.



This maps almost perfectly to a framework I use in all of my workshops and consulting work:



Build AI tools with roughly 60% traditional code (platform integrations, networking, file handling, stuff that has nothing to do with AI), 30% rule-based logic (routing decisions, management, security rules, smart code that is still not AI models), and only about 10% actual AI processing



In OpenClaw's case, that 10% is even pushed externally. It is API calls to someone else's AI.



This is not a criticism. This is a recommendation on architecture. Most production AI systems look like this. The AI is a component, not the whole thing. The value is in everything around the AI, not the AI itself. OpenClaw just makes this more visible than most tools do.



------



The question nobody is asking



Here is where we need to be honest. There is a question hanging over OpenClaw that nobody seems to be asking.



What happens when the big players build this themselves?



Picture this. Next year, Anthropic announces Claude everywhere. Native integration with WhatsApp. Built into Slack. Discord bot that works out of the box. No configuration, no API keys, no self-hosting. Just Claude, everywhere.



Why would anyone need OpenClaw?



This happens constantly in tech. A platform adds a feature that makes your whole product unnecessary. Some people call it getting "Sherlocked" (after Apple's habit of building features that killed third-party apps).



But there is another way this plays out. OpenClaw is model agnostic. You can swap Claude for GPT or Llama or a local model. No vendor lock-in. OpenClaw is self-hosted. Your conversations stay on your hardware. Your data, your rules. And OpenClaw is open source. 2,000 contributors. Community-driven development. Features that matter to users, not shareholders.



So the question becomes: in a world of orchestration layers and frontier models, where does the value actually live?



------



What this teaches you



Forget OpenClaw for a second. Here is the lesson underneath it.



Every time you look at an AI tool, an AI startup, an AI framework, ask yourself three questions:



Where is the intelligence?



Is it in the product, or is the product calling someone else's AI? If you removed the AI model, what would be left?



Where is the value?



Is the value in the AI itself, or in the routing, the integrations, the architecture around it? OpenClaw has zero AI and 350,000+ stars. The value is the orchestration.



What gets commoditized next?



If Anthropic or OpenAI builds the orchestration layer natively, what happens to the product? If the AI models get cheaper, what happens to the business model? Value lives above whatever just got commoditized. Always.



This is the same pattern from



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



viewed from the business side. Every layer of the stack eventually becomes infrastructure. The value moves up. The question is always: are you building at the layer that is about to become free?



This is also why the folder architecture from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



works the way it does. You are not building a custom AI. You are building an orchestration layer in plain English. Folders, context files, and routing tables. The intelligence comes from Claude (or whatever model you use). Your job is the routing, the structure, the architecture around it. That is where the lasting value is.



------



OpenClaw GitHub



https://github.com/openclaw/openclaw



------



The 60/30/10 framework



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=2dda0f93f45a471eb7a8439a1d8d9cff&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



gets a full course in



Premium: The Vault



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. Free tier gives you the concept. Premium teaches you how to apply it to your own builds and client work.



This video looks at the stack from the business and architecture side.



Section 2.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



looks at it from the technical side. Same conclusion: value lives above whatever just got commoditized.



Section 2.4



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



expands on the "what gets commoditized next" question and applies it to companies that spent six figures building at the wrong layer.



The folder architecture from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is a personal orchestration layer. You are the conductor. Claude is the musician. The folders and context files are the score.



------



You just saw how a 350K+ star project is 90% orchestration and 10% AI calls. Next: how one person replaces an entire production team using the same principle. Folders, routing, and a programmatic pipeline. The AI is the component. The system is the product.



Here it comes again. Slack ping, Discord message, WhatsApp buzz, notification, email, calendar, teams, another Slack ping. Every app wants your attention. Every platform has its own inbox. And if you want to use AI to help, you're copy pasting between chat GPT and everything else like it's 2019. Yet someone all of a sudden out of nowhere says, "Hey, have you heard of Moltbot?" and sends you a link. Allegedly, it's one assistant everywhere you already are. Message it on WhatsApp, get a response on Telegram, ask it to check your calendar from Slack, and it just works across everything. One assistant, one place can simply access all of your things, including the files on your computer. And it honestly has over a 100,000 stars on GitHub already. 500 pull requests, 200 contributors, and a lot of people are calling it the future of personal AI. Some people are saying that it's some sort of AGI and the hype is real. The enthusiasm might be real, but here's what most people are not understanding me. If you open the codebase, all 50,000 lines of it, read every file, check every folder, you won't find a model. You're not going to find weights. You're not going to find training data. There is no AI inside of it. None. So, what is everyone all excited about if it's this crazy AI agent that's handling everything? To understand what Molbot actually is, we need to talk about a word that gets thrown around a lot in AI circles, but rarely gets explained well. Orchestration. Think about an actual orchestra. Dozens of musicians, brass, strings, woodwinds, percussion. Each one a specialist, each one capable of making music on their own. But here's the thing. The conductor does not play an instrument. The conductor doesn't make any sound at all. The conductor's job is to coordinate who plays when, how loud, in what order, when to speed up, when to slow down, when to pause. That is the important part. The musicians are the talent. The conductor is the organizer. Now replace musicians with AI models, tools, messaging platforms. That's the orchestration. Let me make this a little bit more concrete and I kind of want to take you into here a second because there's a good lesson to learn. I'm going to use some simple shapes. A circle is your message. Hey, what's on my calendar today? The pentagon is an AI, claw, GPT, llama, whatever model you're using. A square is a tool, your calendar, your browser, your file system. And a rectangle is a channel, WhatsApp, Slack, Discord. Without an orchestration layer, here's what happens. Your message has to find the AI. The AI has to figure out what it needs, a tool, when it should have a tool, what the tool is, and it has to be called. The response has to get back to the AI. And then the whole thing has to find its way back to whatever app you sent the message from. It's a mess. Every connection is manual. Every integration is custom. Things break constantly. Now, if you add an orchestration layer in the middle, a central hub that speaks every language, your message goes in, the orchestrator routes it to the right AI. The AI says, "I need calendar data." The orchestrator calls the calendar tool, gets the response, sends it back to the AI. AI formulates an answer. Orchestrator sends it back to WhatsApp or Slack or whatever you started. Same task, clean architecture. Everything flows through one intelligent router. But there's something important I want to hit on here. We should get our terms straight because people use these words interchangeably and they really shouldn't. An AI model is the actual intelligence. GPT, Claude, Llama, so on and so forth. The things that think, and I use that with a grain of salt. Moltbot is not this. A wrapper is a thin layer around an API. Minimal added value. And there's a lot of tools out there like that, but I don't think Moltbot is this either. An agent is an AI that can take actions autonomously. Moltbot enables this, but needs an external AI to do it. But an orchestration layer coordinates AI plus tools plus channels plus context. This is what Moltbot actually is in my opinion. And the simplest way to think about it is Moltbot is the highway system. You still need to bring your own car to drive on it, to have it go places, make deliveries, all of that good jazz. But not arguing over what it is or how it is, I think we should actually look at Moltbot's architecture, not just because of Molbot, because it's a really great way to build all of your tools and apps in the future or in the AI world. Now, what I like about Moltbot is they really designate areas into layers, right? They have the input layer which is kind of where your interaction space is. They have this gateway layer where it's kind of this area where Moltbot is handling on sending those things, routing them, authenticating stuff. And then there's this uh kind of major output layer where you know they're taking AI models and allowing you to connect them looking at the storage. This is where it really wants all of that stuff to kind of be connected to and flowing really well. But let's try to break them apart into their individual sections. So at the top you have this channel layer. This is where Moltbot connects to all of those messaging platforms, right? WhatsApp and they're using a library called Bailey's, Telegram through Grammy, Discord through Discord.js, Signal through Signal CLI and so on. These are each of these really solid maintained open- source libraries that really know how to speak the platform's language. In the middle, you have the gateway. This is the brain of the operation. And I don't mean an AI brain, although you could argue that. I mean a routing brain. It's a websocket server running locally on your machine. Every message from every channel throws through here. The gateway decides where it goes. It manages sessions so that AI remembers your conversation context and it handles authentication so random people can't just message your AI. Hopefully, there's some arguments that there's some big opening securities in it, but that's besides the point. At the bottom, you have two things, tools and AI models. The tools are included. browser automation through Chrome's debugging tools, bash commands, file operations, Chrome jobs for scheduling, web hooks, all of them built in. And the AI models, they're just hooks. They're empty. You have to actually bring your own, right? You have to bring in your own API keys. You plug in your anthropic API key or your OpenAI API key or you run a local model from Llama and you point that model inside of it. Moltbox will handle all of the API calls, but the intelligence, the actual thinking is technically coming from somewhere else, somewhere you might be paying for already. So what does this actual codebase look like if it's not a giant AI model? Well, about 35% of this is actually channel integrations. That's the code that speaks with WhatsApp, Telegram, all that stuff. About 25% is the actual gateway, right? routing, logic, session management, security. 20% is tools, browser control, bass execution, file handling, and only 10% is really CLI configuration and AI, right? It's just basically a bunch of AI calls that you can configure into your endpoint and send messages. This maps almost perfectly to a framework that I talk about in all of my workshops and lectures and even within my own company which is this idea that 603010 you should be building AI tools with about 60% traditional code you know platform integrations networking file handling stuff that has nothing to do with AI 30% needs to deal with rule-based logic routing decisions management security rules smart code but again still not these AI models and realistically Basically, only 10% actually needs to be AI calls. And in the case of Moltbot, that 10% is even pushed externally. It's API calls to someone else's AI. But this isn't a criticism. This is actually a recommendation on architecture. Most production AI systems look like this. The AI is a component, not the whole thing. The value is often in everything around the AI, not the AI itself. Moltbot just makes this explicit, maybe more explicit than people realize when they first hear about it. It's why I'm hesitant to call it a rapper and actually just call it what it is, good architecture. And of course, it's going to have security flaws, things like that. There's always stuff to be working on it. But honestly, because this is open- source, because you can see their GitHub, I think this is a great opportunity for people to learn how to create these orchestration systems that are actually going to last the decade. This is where we should be spending our time as developers. This is what makes sense. However, just because this is the right way to code doesn't necessarily mean that Moltbot or something like it is going to stick around. And that's where we come into this question. I want to get real with you because there's a question hanging over this whole project that I don't think anyone seems to be asking. What happens when the big players decide to just build this themselves? If Mullebot is still requiring the other AIS, what happens when the other big guys play this themselves? Imagine this for a second. Next year, Anthropic announces Claude everywhere. Native integration with WhatsApp built into Slack, Discord bot that works right out of the box. No configuration, no API keys, no selfhosting. You just have Claude everywhere. Why would anyone need Moltbot? Why use a middleman when the AI company itself is offering direct access? This, I often think we should call is getting sherlocked. When a platform adds a feature that makes your whole product unnecessary and this doesn't just happen all the time in AI. This happens all the time in tech in general. But there's also another way this plays out. Moltbot is in fact model agnostic. You can swap Claude or GPT or Llama or even run your own local model and you don't have vendor lockin. Plus, Moltbot is self-hosted. Your conversation can stay on your hardware if you keep a local model. Your data, your rules. Plus, Moltbot is open- source, 200 contributors, communitydriven development, features that matter to users, not necessarily shareholders. So, Mulbot lets you not have lockin, but Claude is straight to the source. So, the question is in orchestration and frontier models, where is the value? Mullellbot has no AI inside. It's an orchestration layer, a router, a traffic controller, a universal translator between messaging platforms and AI surface. It follows the 603010 architecture roughly. Most of the code is plumbing, not intelligence. Its value proposition probably is found in flexibility, model agnostic, self-hosted, open- source, and customizable. And its future, I think, is genuinely uncertain. It could be replaced by native integrations from big AI companies, or it could thrive as the Switzerland of AI systems, neutral, interoperable. At the end of the day, here's what I think. The engineering, it's impressive. Stitching together 10 different messaging protocols into a coherent system isn't simple even with vibe coding. The websocket gateway architecture is clean. The tool execution sandbox is thoughtful. Is it revolutionary? I don't think so. But it is good infrastructure for the most part. I think there's going to be a lot of leaks of data and while you're using it and also on top of that, I don't think it's necessarily defensible either. But that really depends on whether users value flexibility over convenience. And I think most people historically or at least a good portion of the market will always choose convenience. But developers and privacy conscious users, I think they're going to choose flexibility. My honest take is moltbot is useful and today has a very specific audience. Power users who want control, developers who want customization, privacy advocates who want self-hosting. But as a mainstream product, it's one of anthropic announcements away from becoming a niche tool. And you know what? That might be fine. Not everything needs to be mainstream to be valuable. At the end of the day, what do you all think? Is orchestration the real product? Is Moltbot solving a problem that will exist for years or filling a gap that's about to close? I'm generally curious what everyone else thinks. Drop your take in the comments. And if you want to see more breakdowns like this where we actually look at what's inside the hype, subscribe. I can do this for all AI tools or frameworks or whatever else is getting attention that might not deserve it. But anyway, other than that, I'll see you in the next one and have a wonderful day everyone.



------



Jake's content\The Foundation\2.6 Video as Code My AI Animation Stack.md



2.6 Video as Code: My AI Animation Stack



What You'll Get From This



You will see how one person replaces a week of animation work with under an hour using folders, specs, and a component library. The tools matter less than the process. The process is software engineering applied to creative work.



------



The written version below covers the same ground as the video. The video above has music and visuals that make the layering easier to follow. The written version is the one you hand to Claude or come back to for reference.



------



What used to take a week



The animations you see across this channel would have taken a full week, maybe a month, to make by hand. Now they take under an hour. And they turn out well.



I know how that sounds. AI promises something revolutionary, you try it, and the output is mediocre, uncanny, or requires so much cleanup that you wonder why you bothered. That is exactly why I want to show you this. The point is not polished results. It is the process. And what you will find is not magic. It is infrastructure. Documentation, specifications, component libraries. Software engineering applied to a creative problem.



------



The four tools you need

#### If you wanted to do this yourself, here is what I use:

Claude Code



(or any coding agent like Codex, Aider, etc.)



A code editor



(VS Code, Cursor, whatever you are comfortable with)



— a library that turns React components into video, frame by frame



A video editor



— I use CapCut because it is simple and fast



I am not going to walk through installation. There are plenty of tutorials for each of these, and that time is better spent on the actual process. Just know that if you have these tools set up and running, everything I am about to describe is available to you. And the tools themselves are not the point. It is how they work together.



------



The real secret: writing the spec



Here is the part that surprised me when I started doing this. The hard work is not the AI. It is not the code. It is the spec.



The spec is the markdown file that describes what the video should be. And not vaguely. Not "make it look cool." Precisely. What is the structure? What happens in each scene? What is the timing? When do visual elements appear? What should be emphasized? What should stay in the background?



If you have ever worked with a designer or an animator, you know this as a brief. There is a quote from David Ogilvy: "Give me the freedom of a tight brief." It sounds like a contradiction, but it is not. When the brief is clear, when it defines the problem precisely, the person (or AI) executing it knows exactly where they are going. They can focus on solving the problem instead of trying to figure out what the problem even is.



The spec is where your creative thinking lives. What is the thesis of the video? What is the arc? What are the moments that need to land? What should feel fast and what should feel slow?



A loose spec means Claude makes more interpretive choices. It guesses more. A tight spec means you are directing at every beat. You can work either way depending on where you want your creative energy to go, but the tighter the spec, the closer the output is to what you had in mind.



------



What a spec file actually looks like



It is a markdown file. Headings for each scene. Descriptions of what happens. Notes on timing and emphasis. Nothing fancy. But it is the document that makes everything else possible.



And this is not just for creative work. This same approach works for code, for client deliverables, for anything you are building with an AI agent. The spec is always the leverage point. You will start to notice how powerful this process is across everything you do.



------



How Claude Code reads everything



Once you have a spec, the build phase is where it becomes animation. Here is what actually happens.



Claude Code reads the spec. But it also reads your documentation, because the spec references other files:



A style guide



— defines your visual language. Minimal text rules, color palettes, animation timing. Decisions that stay the same across every video.



A component registry



— a list of reusable pieces you have already built. Text animations, backgrounds, transitions, data visualizations. Building blocks that work together.



Then Claude builds each scene one by one. Each scene is a React component. Remotion takes those React components and renders them frame by frame into video.



This is the component library concept from



Section 2.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. You are not building from scratch every time. You are assembling existing pieces according to a spec. Claude knows the components. It knows the style rules. It composes them into scenes that match what you described.



------



Why Remotion changes the game



Remotion was created by Jonny Burger. The core insight: a video is just a function of images over time. If you change the content every frame, you get animation. React is already good at describing what should appear based on some state. Normally that state is user input. In Remotion, the state is the current frame number.



You tell React what frame 47 should look like. It renders it. Do that for every frame. You now have a video.



What this means in practice: anything that works in a web browser can be part of your animation. CSS, SVG, canvas, the entire ecosystem of JavaScript libraries. You are not learning a new tool from scratch. If you know any front-end development (or if you have Claude Code writing the front-end for you), you are using tools that have existed for years, applied to a new purpose.



------



The workflow in detail



Give Claude the spec



Point it at the documentation (style guide, component registry)



Tell it which scene to build



It writes the code



Preview it in Remotion Studio



If something is not right, describe in natural language what needs to change



Claude adjusts. Iterate until the scene matches what you had in mind.



The component library matters because you are not building every animation from scratch. You have building blocks: a text component that handles entrance animations, a scene container that handles safe margins and backgrounds, effects like glitch text or counting numbers. Claude assembles these pieces according to the spec. It is composing, not inventing.



This is separation of concerns. The same principle that makes any complex software manageable. The spec is separate from the implementation. The components are reusable. The style guide encodes decisions so you do not make them every time. Break complex things into smaller pieces that can be understood and changed independently.



If you went through



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, this should sound familiar. The folder architecture does the same thing: identity file, workspace context, skills. Each one handles a different concern. This animation pipeline is the folder architecture applied to a specific production workflow.



------



Exporting to CapCut for the final edit



Once the scenes are built, I export from Remotion (or just use OBS to record the screen, which avoids render and codec headaches). Then I bring it into CapCut.



This is where animation becomes a finished video. I record the voiceover. I cut and sync it. I add music. I scrub through and nudge transitions to land on specific words. Some of this is honestly faster by hand than describing it in a spec and waiting for code to regenerate.



The animation is not the finished video. It is a substantial starting point. I still spend real time in this phase. I cut sections that do not work when I hear them out loud. I re-record lines that do not land. I add photos, screenshots, or footage to support the narration. The animations give me a foundation. The finished video requires refinement.



So when I say "under an hour," I mean the animation, the part that would have taken a week in After Effects if I was doing it frame by frame. The finished video still takes time. But I am spending that time on the parts I actually want to control: pacing, moments that need a real image, the edit.



------



The bigger picture: GarageBand for video



What is happening here is part of a much larger pattern.



When GarageBand came out in 2004, Steve Jobs wanted to democratize music making. Suddenly every teenager with a Mac could produce music that would have required a $100,000 studio five years earlier. Steve Lacy made tracks for Kendrick Lamar on a cracked iPhone with GarageBand and a $20 iRig. That phone is now in the Smithsonian.



Canva did something similar for visual design. Melanie Perkins was rejected by over a hundred investors who did not think design tools for non-designers was a real market. Now 200 million people use it monthly.



The pattern is always the same. A tool emerges that gives people access to execution they could not do before. Not replacing professionals. Letting people who have ideas actually realize them.



There is a messy period early on. Designers called it the "ransom note effect" when desktop publishing first appeared. Everyone used 15 different fonts on one page. But over time, the floor rises. More people creating means more good work in absolute terms, even if the average quality takes time to catch up.



We are in that moment for AI-assisted animation and video. The tools exist. The quality can be good. People who could not afford a motion graphics artist, or could not justify a week of their own time, can now make something real.



------



Why constraints make it better



There is actual research on this. An inverted U-shaped relationship between constraints and creative output. Too few constraints and you get paralysis (the blank canvas problem). Too many and you get stifled. But in the middle, with the right boundaries, creativity increases.



Dr. Seuss wrote Green Eggs and Ham because his editor bet him $50 he could not write a book using only 50 words. He made flowcharts on his walls to track his vocabulary. The book sold 200 million copies. His best-selling work ever.



Spielberg could not get the mechanical shark to work in Jaws. So he showed floating barrels and point-of-view shots instead. The shark does not fully appear until 80 minutes into the film. The constraint made the movie better.



The spec, the style guide, the component registry: these are not limitations I work around. They are boundaries that make the output better. Claude is the one constrained. It knows the rules. It focuses on execution instead of guessing what I want.



This connects directly to



Section 1.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. Constraints were part 4 of the prompting framework. Every constraint you give is a mistake Claude will not make. In this animation pipeline, the style guide and component registry are constraints encoded as files. Same principle, applied at a larger scale.



------



What actually changed



AI did not make the creative work disappear. It moved it.



The spec is where my creative thinking lives. The documentation encodes my preferences and lessons from past mistakes. Claude executes within those boundaries, assembling components that already work into scenes that match what I describe. Then I take that output and refine it. Cut it. Add footage. Shape it into something finished.



One person doing the work that used to require 4 to 6 specialists and 8 to 12 weeks. That is the real claim. Not that AI replaced the creativity. That the system let one person handle the execution.



If you have ideas that have been stuck in your head because you could not figure out how to make them visible, this process can be learned. The tools are freely available. Most of the system is just software engineering applied to creative work: constraints, separation of concerns, reusable components, clear specifications.



------



http://remotion.dev/



http://capcut.com/



------



Want to learn the full animation pipeline hands-on? The



Building Animations



course (Level 2) walks you through the Main Tutorial, Illustrator-to-web workflow, and the full course companion with resources. [



Animations Course



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d3907117?md=f7a33a9888604a08a7e48bb876682691&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The folder architecture from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is the same system applied broadly. This animation pipeline is one specific implementation of it.



The prompting framework from



Section 1.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is running throughout this process. The spec is identity + task + context + constraints. The component registry is encoded output format.



Section 2.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



60/30/10 breakdown



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=2dda0f93f45a471eb7a8439a1d8d9cff&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. This animation pipeline follows the same pattern: most of the system is traditional code (components, Remotion config), the routing is in the spec and documentation, and the AI calls are a small fraction of the total work.



The concept of "value lives above whatever just got commoditized" from



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



applies here. The animation rendering got commoditized. The creative spec and the system around it is where the value lives now.



------



We have covered the technical stack



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, the memory model



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



where value lives



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



and how systems replace manual work (2.6). The last video in the series goes somewhere different: the history of psychological measurement instruments, how they ended up running on AI models, and what that means for auditing the systems we are building.



The animations that you're going to see in this video would have taken me probably a full week, if not a month, to make. And now I make them in under an hour. And honestly, they turn out pretty great. I've made all sorts of different types. And I know how that sounds, right? This idea that, okay, it's an AI video. AI promises this something revolutionary, gamechanging, the future of content, and then you try it and the output's mediocre, uncanny, or require so much cleanup that you wonder why you bothered. But that's exactly why. and how I want to show you this. It's not polish results, but the process and what you'll find isn't magic. It's infrastructure. It's documentation, specifications, component libraries. It's honestly software engineering applied to a creative problem. But let me go ahead and start with what you need if you wanted to do this yourself. I use cloud code, but you can use codeex or any other sort of coding agent. Um, on top of that, I also use some sort of IDE. You can use VS Code, cursor, anti-gravity, and just throw the plug in for each of those. Finally, I use a library called Remotion, uh, which generates most of the processes, and then I throw that all into some sort of video editing software, which I personally use, Cap Cut, cuz it's super easy to use. I'm not going to walk [clears throat] you through the installation because there's plenty of tutorials uh, for that and it would eat up time better spent on the actual process of moving between these. Just know if you have these tools set up and running, everything I'm about to describe to you is available to you. And again, it's not tool specific. The tools actually don't matter themselves. It's the process and how you use them, how they work together. And honestly, that's what you'll see in all of my videos. I'm not just doing basic tutorials. I'm giving you a framework to how to use tools like these, these new abstractions of AI all together in a way that actually works. Now, here's the part that surprised me when I started doing this. The hard work isn't the AI. It's not the code, it's the spec, it's the breakdown. It's the documents that describe what the video should be. And not vaguely, not make it look cool, but precisely. What's the structure? What happens in each scene? What's the timing? What's the visual elements appear? When should they appear? What do you want to emphasize? And what should stay in the background? If you ever worked with a designer or an animator, you know this is as a brief. And there's this quote from uh David Ugle. He said, "Give me the freedom of a tight brief." Which sounds like a contradiction, but it isn't. When the brief is clear, when it defines the problem precisely, the person executing it knows exactly where they're going. They can focus on solving the problem instead of just sitting there trying to figure out what the problem even is. My spec or the spec that you're making, the markdown file is the brief. It's where your ideas become concrete enough for the system for the AI to actually execute them. And this is where most of your creative thinking should be happening. What's the thesis of this video? What's the arc? What are the scripts? What are the moments that need to land? What should feel fast and what should feel slow? A loose spec or a poor spec means that Claude or your AI agent makes more interpretive choices or hallucinates more. A tight spec means you're directing it at every beat. And really, it allows you to do a lot more focused things. You can do both, and it depends on where you want your creative energy to go. But I'll show you what one of my specs look like. And again, as I said, it's actually just a markdown file, which is a type of file that organizes text in a very specific way. It has headings for each scene, descriptions of what happens, notes on timing and emphasis. It's really nothing too fancy, but it's the document that makes everything else possible. And this isn't just for creative processes. This is for code. This is for anything you're doing with AI agents. And you'll start to notice how powerful this process is. Once you have a spec, the building phase is where it becomes animation. And here's what actually is happening. Claude code or your agent is going to read through the spec, but it also reads your documentation if the spec is mentioning, which mentions maybe style guides. This is going to define your visual language. You're going to define minimal texts. You're going to define color pallets, animation timing. It's going to read through a component registry. Now, I created this, but it's basically just a list of reusable pieces that you've already built in previous videos or you're building with the AI before it even starts, right? Text animations, backgrounds, transitions, data visualizations. Then from there, you're actually having it build each scene one by one. And each scene is just a React component, right? This a front-end uh software. And Remotion takes those React components and actually allows you to render them frame by frame into a long video. And there's an insight from a man named Johnny Burgerer who actually created reotion. A video is just a function of images over time. If you change content every frame, you get animation. And React is already good at describing what should appear based on some state. So instead of the state being user input, the state is the current frame number. You tell React what frame 47 should look like and it renders it. Do that for every frame, you now have a video. What this means in practice is that anything that works in a web browser can be part of your animation. CSS, SVG, canvas, the entire ecosystem of JavaScript libraries can now be placed into your videos. You see, you're not learning a new tool from scratch. If you're a front-end developer, you're using tools that have already existed for a new purpose. So, the workflow actually looks more detailed like this. I give Claude the spec, point it at the documentation, I tell it which scene to build, it writes the code, I preview it in Remotion Studio, and if something isn't right, I literally just describe in natural language what needs to change, and it adjusts. We iterate until the scene matches what I had in mind. The component library matters at this point because I'm not building every single animation from scratch. It's not like every time I'm making a video, I'm just starting from fresh. I actually have building blocks that are traditional code, a text component that handles entrance animations or enforces readable sizes, a scene container that handles safe margins and backgrounds. Effects like glitch text or counting numbers. When Claude builds a scene, it assembles these pieces according to the spec. It's not inventing everything new, but rather this kind of aspect of like, hey, I should compose a new element that already works together in other elements. This is just separations of concerns. It's the same principle that makes any complex software manageable. The spec is separate from the implementation. The components are reusable. The style guide encodes decisions so you don't have to make them every time. Now, if anyone has written software before, this should actually seem very familiar. And even if you haven't, just know that this is the principle. Break complex things into smaller pieces that can be understood and changed independently. From there, once the scenes are relatively built, I just export it from Remotion or even just use OBS to record my screen, so I don't have to worry about render processes or codec errors. And this just is something I can upload straight into Cap Cut. Now, this is where the animation becomes much more of a video. I usually do a voice over. I cut and make sure that it actually syncs up. I maybe add some music. And there's some things that right now are a little bit easier to do by hand. So, I haven't really automated that process, but I'm working on it. Now, scrubbing through and nudging a transition to land exactly on a word is honestly faster in a video editor than describing it in the spec and waiting for code to regenerate. The animation is not the finished video. It's simply a starting point. Now, it is a substantial one. I still spend real time in this phase. I'm cutting so many sections that don't work when I hear them out loud. I'm re-recording lines that don't land. I'm adding photos or screenshots or footage to support the narration. The animations give me a foundation, but the finished video requires refinement. So when I say under an hour, I mean the animation, the part that would have taken a week if I was doing it frame by frame and After Effects. The finished video still takes time, but I'm spending that time on the parts I actually want to control. The pacing, the moments that need a real image instead of motion graphics. Now, the question isn't really about whether AI can make videos or anything like that. It's more where do you want to spend your creative energy? And for me, the answer is not automating from scratch, not animating everything. Honestly, I'd rather have something real to react and to shape to rather than start with a blank timeline or focus on the actual content itself. Now, that being said, let's zoom out for a second because I think what's happening here, as I mentioned earlier in the video, is part of a much larger pattern. When Garage Band came out in 2004, Steve says he wanted to democratize music making. And there's this statistic that stuck with me. Suddenly, every teenager with a Mac could produce music that would have required a $100,000 studio. 5 years earlier, Steve Lacy made tracks for Kendrick Lamar on a cracked iPhone with GarageBand and a $20 eye ring. That phone is now in the Smithsonian. Canva did something similar for visual design. Melanie Perkins was rejected by over a hundred investors who didn't think design tools for non-designers was a real market. Now 200 million people use it monthly. The pattern is always the same. A tool emerges that gives people access to execution they couldn't do before. Not replacing professionals, but letting people who have ideas actually realize them. And there's a really messy period early on which designers called the ransom note effect. When desktop publishing first appeared, everyone used 15 different fonts on one page, but it kind of went all over. And then over time, the floor kind of rose. More people creating means more good work in absolute terms. Even if the average quality takes time to catch up. I think we're in that motion or that moment for AI and animation and video. The tools exist. The quality can be good. And people who couldn't afford a motion graphics artist or couldn't justify a week of their own time can now make something real. And this might be kind of powerive, but I think this is the key to how all of this is going to work. It's that constraints enable creativity. There's actual research on this. An inverted U-shaped relationship between constraints and creative output. Too few constraints, you get paralysis, the blank canvas problem. Too many, you actually get stifled. But right in the middle, with the right boundaries, creativity actually increases. Dr. Zeus wrote Green Eggs and Ham because his editor bet him $50 he couldn't write a book with only 50 words. He made flowcharts on his walls to track his vocabulary. And the book sold 200 million copies, and it is his best selling work ever. Spielberg couldn't get the mechanical shark to work in Jaws, so he showed floating barrels and point off view shots instead. The shark doesn't fully appear until 80 minutes into the film. The constraint made it better somehow. The spec, the style guide, the component registry, these aren't limitations I work around. They're boundaries that make the output better. Instead, this case, Claude is now the one constrained. It knows the rules. It focuses on execution instead of wondering what I want. So let me come back to where we started. The animations that would have taken a week are now done in an hour. That part is true and I want you to understand what actually is behind that claim. AI is not magic. I built a system. The spec is where my creative thinking lives and the predefining constraints. The documentation encodes my preferences and my lessons from past mistakes. Claude executes within those boundaries, assembling components that already work together into scenes that match what I describe. Then I take that output and I refine it. I cut it. I add footage. I shape it into something finished. The creative work didn't disappear in the same way we would imagine it actually moving. The spec, the refinement, that whole area is actually where I want to spend my attention. Now, if you have ideas and want to visualize, but you're not an animator, this is probably something you want to focus on. Not easy. There's setup and learning and narration, but it's possible in a way that was never possible before. You can finally get ideas into a visual form that used to require skills most people don't have. Years of After Effects or money to hire someone who did. Now it requires a process, right? Tools that are freely available, a way of thinking about constraints and separations of concerns. And honestly, most of those constraints are just software engineering but applied to creative work. This process can be learned and I really recommend each of you try it. Everything I've described, I have documented. The tools are [music] there. If you want any of these specs or these scripts or these designs, just comment and and ask for them. I'll happy to email them to you. But if you have ideas that have been stuck in your head because you couldn't figure out how to make them visible, maybe now you can. Other than that, I hope this helps out everyone. As always, stay curious.



------



Jake's content\The Foundation\2.7 From Nazi Psychology to AI Auditing.md



2.7 From Nazi Psychology to AI Auditing

#### Full paper:

[2510.11742] The Ethics Engine: A Modular Pipeline for Accessible Psychometric Assessment of Large Language Models



https://arxiv.org/abs/2510.11742



What You'll Get From This



You will see a real AI system taken apart piece by piece. What you find inside is not magic. It is APIs, async programming, parsing, and statistics. The AI is 10% of the system. The other 90% is engineering that has existed for decades. This is the final lesson in the series (for now) and it ties everything together.



------



The written version below covers the same ground as the video. The video above has music and visuals that make the layering easier to follow. The written version is the one you hand to Claude or come back to for reference.



------



A test designed to study authoritarians, now running on AI



I took psychometric tests originally used to measure authoritarian tendencies in the 1950s and aimed them at AI models. But I did more than that. I built a data pipeline that can administer a wide range of personality tests across multiple AI models simultaneously. It can tell you where a model lands on moral foundations, authoritarianism scales, personality dimensions. It can do this across personas, model variations, and different providers.



From the outside, it looks like one intelligence studying another. Something that would require a team of researchers or grants. But I am not bringing this up to show you the results. I want to take it apart. Because something becomes visible when you deconstruct systems that stays hidden when you only watch them get assembled.



------



What "agent" actually means



Before we open the system, we need to deal with a word that has taken on a lot of weight: agent.



We hear about AI agents that browse the web, write code, manage calendars, analyze documents. The word implies autonomy. Decision-making. Something that can act on its own behalf.



But language is running ahead of the engineering. What we call an AI agent in the vast majority of cases is not a single entity making autonomous decisions. It is a collection of prompts, structured and sequenced by traditional code, that causes a model to behave differently at different stages of a workflow.



The model itself is not deciding to take the next step. The orchestration layer, which is regular software, evaluates the model's output and determines what prompt to send next based on conditions that a human engineer defined.



This maps onto something we already understand. Think about the difference between a function call and a running process. A function takes an input and returns an output. It does not decide what to do next. The program that called the function makes that decision. Each call to a language model works the same way. Prompt in, text out. The agentic behavior, the appearance of autonomy, emerges from the orchestration code that wraps those calls.



There are systems beginning to emerge where models genuinely operate in autonomous loops. That is a real and meaningful evolution. But it is not what the vast majority of deployed systems are doing today. Conflating the two makes it harder to understand what is actually happening when these systems work.



------



The orchestration layer: async programming and concurrency



So let us look at what is actually happening. Open the Ethics Engine and the first thing you find is not a model. It is a traffic controller.



The Ethics Engine needs to administer dozens of psychometric items across multiple models simultaneously: Claude, GPT, Llama, Gemini. Each provider has different rate limits, different response formats, different failure modes. So there is an orchestration layer that manages all of this. It is written in Python and it is doing something that would be immediately recognizable to anyone who has built a web scraper, a trading system, or a ticket reservation platform.



It manages concurrency. It handles retries when requests fail. It queues prompts and dispatches them in order. It tracks which items have been completed and which are still pending.



None of this is AI. This is async programming. Concurrency management. These are patterns that existed long before language models and they work the same way here as they do anywhere else.



The model at the other end of each request has no awareness that any of this is happening. It receives a prompt. It returns text. That is the full extent of its involvement in this layer.



------



How systems talk to each other: APIs



How does the prompt even get to the model? When we say "called an API," there is a concept buried in that sentence that tends to get skipped when people teach this.



An API (application programming interface) is a contract. Two pieces of software agree in advance on the shape of their conversation. What the request will look like. What the response will look like. What is allowed and what is not. Neither side needs to understand the other's internals. They just need to honor the agreement.



When the Ethics Engine sends a prompt to Claude, what actually happens is an HTTP request carrying JSON (a structured text format) that goes to an endpoint at Anthropic's servers. That JSON contains the prompt, the model name, and some parameters. The server processes it and returns JSON containing the model's response.



A structured text message goes out. A structured text message comes back. Everything the Ethics Engine does with that response (the scoring, the analysis, the reliability calculations) happens locally in traditional code.



This is how software has communicated for decades. Web browsers talk to servers this way. Payment systems talk to banks this way. Your weather app talks to a data provider this way. The pattern is not new.



------



MCP and the pattern: USB, HTTP, LSP, and now AI tooling



Here is where a familiar problem resurfaces. What happens when your system needs to talk to not just one service but twenty? A database, a file system, a web browser, a code interpreter, a calendar, a search engine. If every connection is custom-built, you have a scaling problem. Every new tool requires a new integration. The number of integrations grows as the product of applications times tools. That math gets unworkable fast.



We have seen this problem before. Every time, we found the same solution: standardize the interface.



Before USB, every peripheral had its own connector. Printers, keyboards, mice, cameras. All different cables, all different protocols. The solution was one connector, one protocol. Any device that speaks it can connect to any computer that speaks it.



Before HTTP, applications each had their own way of communicating. The solution was one set of rules for requesting and delivering documents. The web became possible.



Before the Language Server Protocol, every code editor needed a custom integration for every programming language. Syntax highlighting, error checking, autocomplete, all built separately for each editor and each language. The solution was to standardize the interface.



This is where MCP (Model Context Protocol) comes in. Introduced by Anthropic in late 2024, explicitly inspired by the Language Server Protocol. The people who built it recognized the pattern: we already solved this problem for programming languages talking to editors, so let us solve it the same way for AI talking to tools.



The architecture has three parts. A host (the AI application), a client (handles the connection), and a server (wraps the external tool and speaks MCP). The model does not call APIs directly. The orchestration layer determines what tools to use. The MCP client manages the connection. The MCP server translates between the protocol and whatever the tool needs internally.



------



The data and the math: parsing, scoring, statistics



Back to the Ethics Engine. The model returned text. Here is what happens next, and this is where the ratio becomes clear.



The model's response is a string. Natural language. Probabilistic. The system needs to extract a number from that string. The model operates in language. The scoring system operates in numbers. Something has to bridge the gap.



What bridges it is parsing. Pattern matching. Regular expressions. Text processing tools that have existed for decades.



The number enters the scoring logic. Psychometric instruments have specific scoring keys developed and validated over years of clinical research. Some items are reverse-scored (a response of 5 gets recorded as a 1, because the question was phrased in the negative direction). Subscales are calculated by aggregating specific items. This is validated, peer-reviewed arithmetic.



From there, reliability testing. Cronbach's alpha for internal consistency. Test-retest correlation for temporal stability. Statistical methods implemented in libraries like SciPy and NumPy that predate large language models by decades. The math has not changed since these instruments were validated on human populations.



------



The real ratio

#### Here is what the Ethics Engine actually looks like when you lay it out:

~10% AI calls



— sending prompts, receiving text. This is the only part that involves a language model.



~30% orchestration



— async coordination, rate limiting, retry logic, queue management.



~60% data processing



— sending and collecting prompts, managing personas, parsing, scoring, analysis, reliability calculations.



This ratio is not unique to the Ethics Engine. It shows up in every well-built AI system. The bad ones ignore it. If you were in



Section 2.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you saw the same pattern: Moltbot is roughly 60/30/10 with the AI pushed entirely external. This is the 60/30/10 framework applied to research software instead of a messaging platform. Same ratio. Same architecture. Different domain.



------



Everything connects



If you have been following this series, the connections are surfacing now.



Section 2.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, we traced a line of Python down through seven layers of abstraction to electrons that are fundamentally probabilistic. In



Section 2.3



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, we traced memory from registers and cache through to context windows and system prompts, and found that the template pattern (blanks filled according to rules) holds at every level. In



Section 2.4



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, we saw what happens when people build at the wrong layer. In



Section 2.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, we opened a 100K-star project and found zero AI inside. In



Section 2.6



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, we watched one person replace a production team using specs, components, and a pipeline.



Now we have taken an AI "agent" apart from the top and found that most of its layers are traditional engineering. APIs that follow the same request-response pattern software has used for decades. Protocols that standardize interfaces the same way USB and HTTP did before them. Data processing that runs on statistical libraries older than the models they evaluate.



There is a narrative that says AI changes everything. There is a counter-narrative that says AI is just hype. Both miss what is actually happening.



AI extends what we have always been doing. It adds a layer where natural language becomes the interface and context becomes the program. But that layer sits on top of the same engineering tradition that has been building since we first figured out how to route electricity through logic gates.



The new thing is real. The semantic layer, the ability to operate on meaning rather than syntax, is genuinely novel. But it does not replace the layers beneath it. It depends on them.



------



What comes next



We are approaching a moment where genuine agentic behavior (models operating in autonomous loops, making decisions that were not predetermined by orchestration code) starts to become real. When that happens, the engineer's challenge will not be making the AI smarter. It will be building the infrastructure around it. Reliability patterns. Error handling. Protocols for safe autonomous operation.



The same work, in other words, that has accompanied every new layer of the stack since Grace Hopper had a compiler that no one believed would work.



The Ethics Engine can tell you the psychological profile of an AI model. That is a real and useful capability. It works because each part does what it is good at. The AI processes natural language and generates responses shaped by context. The traditional code handles orchestration, computation, and reliability. The protocols let different systems communicate without needing to understand each other's internals.



That is not less impressive than magic. It is more impressive, because you can actually understand it. And it actually works.



------



This is the final lesson in the Abstraction series. For the overview and links to every lesson, go back to



Section 2.1



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=e171154adddc431ea52ff98a20f61d4f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The 60/30/10 ratio showed up here and in



Section 2.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



60/30/10 Framework course



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=ca4e8c48d25840709dcca756b9e8b4ff&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is being built currently in



Premium: The Vault



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



teaches you how to apply this architecture to your own builds and client engagements.



The Ethics Engine paper is linked above. You can download it and give it to Claude to explain any section. That is exactly how the docs in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



are designed to be used.



The orchestration concepts in this lesson (async, concurrency, rate limiting) are the same patterns running underneath the folder architecture from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. The folder structure is orchestration in plain English. This lesson shows the same orchestration in Python.



------



The Abstraction series gave you the ideas. The stack. The memory model. The architecture patterns. The ratio. Section 3 takes you back to the practical: the full folder architecture method, how to customize it, and the mistakes people make along the way.



I took psychometric tests used to capture Nazis in the 50s and aimed them at AI models. Well, I did a little bit more than that. I created a data pipeline that allowed to take a lot of personality tests and aim them all across AI models. It can tell you where a model lands on moral foundations, authoritarianism scales, personality dimensions, and it can do this across personas, model variations, various providers, and so on. And from the outside, it looks like one intelligence studying another, like something that would require a team of researchers or grants. But the point I'm bringing this up is not to even show you that. I actually want to take this apart because it's going to help me explain APIs, research, coding in the modern era, what it means to do the fundamentals. And I don't want to show you how to build this. Rather, I'd deconstruct it because something becomes visible when you deconstruct systems rather than showing you how to assemble systems. And let me show you exactly what I mean. But before I do that, let's go into a kind of world of definitions. There's a word that has taken on a lot of weight in the last couple of years, and that word is agent. We hear about AI agents that can browse the web, write code, manage calendars, analyze documents, da da da da, all this hype, agentic world. And the word agent does mean something to our imagination. And not just from an AI perspective. It used to mean autonomy or separate or attached, right? this idea that there's decision-making going on. It implies that this thing can act on its own behalf. Uh, and I want to be careful here because I think this is one of those places where language is running ahead of the engineering. What we call an AI agent in the vast majority of cases is not a single entity making autonomous decisions. It is a collection of prompts structured and sequenced by traditional code that causes a model to behave differently at different stages of a workflow. The model itself is not deciding to take a next step. The orchestration layer, which is regular software, evaluates the model's output and determines what prompt to send next based on conditions that a human engineer defined. This is an important distinction and it maps onto something we already understand in computer science. Think about the difference between a function call and a running process. A function takes an input and returns an output. It doesn't decide what to do next. The program that called the function makes that decision. In the same way, each call to a language model is a function call. Prompt in, text out. The agentic behavior, the appearance of autonomy emerges from the orchestration code that wraps those calls. There are systems beginning to emerge where models genuinely operate in autonomous loops, right? Everyone can think about my good old Clawbot video, but or I think they're called moldbot now. No, open claw. That's the word that they are now. Yeah. Where the model itself decides the next action. That is a real and meaningful evolution, but it's not what we were looking at in the vast majority of the deployed systems we have today. And conflating the two makes it harder to understand what is actually happening when these systems work. So let us look at what is actually happening. And again, let's go into my ethics engine pipeline. The first thing we find when we open the system is not a model. It's actually more of a traffic controller, so to speak. My ethics engine needs to administer dozens of psychometric items across multiple models simultaneously. Claude, GPT, Llama, blah blah blah, Gemini, all these things. Each provider has different rate limits, different responses, formats, different failure modes. So there is an orchestration layer that manages all of this and it is written in Python and it is doing something that would be immediately recognizable to anyone who has built a web screener or a trading system or even just a ticket reservation platform. It manages concurrency. That's it. It handles retries when requests fails. It queries prompts and dispatches them in order. It tracks which items have been completed and which are still pending. Yet none of this is AI, right? There's no AI doing any of this work, or at least not the modern AI. This is just async programming, asynchronous programming. It's concurrency management. These are patterns that existed long before language models, and they work the same way as they do anywhere else. The model at the other end of each request has no awareness that any of this is happening. It receives a prompt, returns text. That is the full extent of its involvement in this layer of the system. Which raises a question that I think is worth sitting on for a moment. How does the prompt even get to the model? What is the actual mechanism by which one piece of software talks to another? When we say that an AI agent called an API or we called an API, there's a concept buried in that sentence that tends to get skipped over when people are kind of teaching about this stuff. And I think it's worth unpacking because it connects to something larger. An API or an application programming interface is a contract. Two pieces of software agree in advance on the shape of their conversation. What the request will look like, what the response will look like, what is allowed and what is not. Neither side needs to understand the other's internals. They just need to honor the agreement that was made. When the ethics engine sends a prompt to claude, what actually happens is an HTTP request carrying JSON, which is a structured text format, and that goes to an endpoint at Anthropic Servers, company that runs Claude. That JSON contains the prompt, the model name, and some parameters. The server processes it and returns JSON containing the models response. A structured text message goes out. A structured text message comes back and everything the ethics engine does with that response, the scoring, the analysis, the reliability calculations, the synchronous muse and so on. All of that happens locally in traditional code. This is how software has communicated for decades. Web browsers talk to servers this way. Payment systems talk to banks this way. Your weather app talks to a data provider this way. This pattern is not new. But here is where I think it gets a little interesting and where a familiar problem resurfaces. What happens when your system needs to talk to not just one service but 20? A database, a file system, a web browser, a code interpreter, a calendar, a search engine. If every connection is customuilt, you have a scaling problem. Every new tool requires a new integration. Every new AI application requires its own connectors to every tool it wants to use. The number of integrations grows as the product of the number of application times the number of tools. And that math gets unworkable real quickly. But we have fortunately seen this problem before. Well before AI and honestly with every iteration, we found a solution. Before USB, every peripheral device had its own connector. Printers, keyboards, mice, cameras, all different cables, all different protocols. The solution was to standardize the interface. One connector, one protocol, and any device that speaks it can connect to any computer that speaks it. Before HTTP, applications each had their own way of communicating. The solution was to standardize the protocol, one set of rules for how to request and deliver documents, and the web became possible. Before the language server protocol, every code editor needed a custom integration for every programming language. syntax highlighting, error checking, autocomplete, all built separately for each editor and each language. The solution was again standardize the interface. This is where MCP comes in and this is the more modern version of this uh history for AI. It's called model context protocol and is a standardized way for AI systems to connect to external tools and data sources. It was introduced by Anthropic in late 2024 and explicitly inspired by this language server protocol. The people who built it recognized the pattern. We already solved this problem for programming languages talking to editors. So let us solve it in the same way for AI talking to tools. The architecture has three parts. A host which is the AI application, a client which handles the connection and a server which wraps the external tool or data source and speaks MCP. The model does not call APIs directly. The orchestration layer determines what tools to use. The MCP client manages the connection and the MCP server translates between the protocol and whatever the actual tool needs internally. Let's get back to the ethics engine. The model returned a text after having this API call or tool call sent out. Right? Let's look at what happens next to this text because this is where the ratio becomes clear. The model's response is sent as a string. natural language, probabilistic language. The system needs to extract a number from that string. And this is a small thing, but it is worth noticing. The model operates in language. The scoring system operates in numbers. Something has to bridge that gap. And what bridges it is something called parsing, pattern matching, regular expressions. The same text processing in tools that have existed for quite literally decades. The number enters the scoring logic. Psychometric instruments actually have a specific scoring key developed and validated over years and years of clinical research. Some items are reverse scored, meaning a response of five gets recorded as a one. And because the question was phrased in a kind of negative direction. Subscales are calculated by aggregating specific items and creating a new number. And this is just basic arithmetic. All of this is validated, peer-reviewed arithmetic, but arithmetic nonetheless. From there you have reliability testing. Chromebox alpha for internal consistency. Test retest correlation for temporal stability. These are all statistical methods implemented in libraries like scypi numpy. Um and that predates large language models by decades as well. The math has not changed since these instruments were validated on human populations. So here's what the ethics engine actually looks like when you lay it out. Honestly, the AI sends prompts, receives texts, and honestly the actual AI calling is maybe 10% of the system volume. The orchestration, right, async coordination, the rate limming, retry logics, Q management, things like that, that's maybe 30%. The actual data processing, sending and collecting prompts, personas, parsing, scoring, analysis, reliability, that's actually like 60% of the actual code that's going on in this. The ratio is not unique to my ethics engine. I'm bringing this up because it's something I see in every good working AI system I work with. All the bad ones seem to ignore this ratio. And this is where, if you've been following along through the series, the connection starts to surface. We traced a line of Python down through seven layers of abstraction to electrons that are fundamentally probabilistic. We traced memory from registers and cache through to context windows and system prompts. And we found that the template pattern blanks filled according to rules holds at every level. Now, we've taken an AI agent apart from the top and found that most of its layers are traditional engineering APIs that follow the same request response pattern software has used for decades. Protocols that standardize interfaces the same way USB and HTTP did before them. Data processing that runs on statistical libraries older than the models they evaluate. Kind of funny when you think about it. There's this narrative that says AI changes everything and then there's this counternarrative that AI is just hype. And while honestly I think both of those myths what is actually happening and what is interesting in my head which is that AI simply extends what we've always been doing. It adds a layer where natural language becomes the interface and context becomes the program. But that layer sits on top of the same exact engineering tradition that has been building since we first figured out how to route electricity through logic gates. The new thing is real. The semantic layer, the ability to operate meaning rather than syntax. That is genuinely novel, but it does not replace the layers beneath it. It depends on them in certain cases. I'll make another video on where I think there's a grain of salt there. Here is where the word agent becomes interesting again because I think we're approaching a moment where genuine agentic behavior models operating in autonomous loops making decisions that were not predetermined even by orchestrating code starts to become real. And when that happens the engineer's challenge will not be making the AI smarter. It will be building the infrastructure around it, the reliability patterns, the error handling, the protocols for safe autonomous operation. the same work, in other words, that has accompanied every new layer of the stack since Gracehopper had a compiler that no one believed would work. And I'm simply just trying to build software at the top of this layer. My ethics engine can tell you the psychological profile of an AI model with about 90% reliability. That is a real and useful capability. And the reason it works is not because the AI is brilliant. The AI does what AI is good at, which is processing natural language and generating responses shaped by context. The traditional code does what traditional code has always been good at, which is orchestration, computation, and reliability. And the protocols connecting them do what protocols have always done, which is letting different systems communicate without needing to understand each other's internals. That is not less impressive than magic. In my opinion, it's more impressive because you can actually understand it and it actually works. Till next time, friends. Goodbye.



------



Jake's content\The Foundation\3.1 The Full Walkthrough (23 Min Video).md



3.1 The Full Walkthrough (23 Min Video)



What You'll Get From This



A working folder system that tells Claude where it is, what to do, and where to put the work. Three layers. Plain English. No code, no frameworks, no agents.



------



Video: Folder Architecture (23 Min)



If you want the written version first, keep reading. If you learn better by watching, start the video above and come back here for reference. Both cover the same ground.



------



The problem with how most people use AI



Right now, most people open Claude or ChatGPT, type something, get a response, and start over. Maybe they save a good prompt somewhere and paste it in again next time. Maybe they hit the token limit and have to start a new conversation. Maybe they spend half the message just re-explaining who they are and what they are working on.



That works for quick questions. It falls apart the moment you try to do real, ongoing work. You are burning tokens on stuff that does not matter. You cannot edit what the AI produces at each step. And every conversation starts from zero.



The folder structure fixes all of that.



------



What tokens are and why this matters



Before we get into the structure, you need to understand one thing: tokens.



A token is roughly three quarters of a word. Sometimes a single word. Sometimes a long word like "hamburger" is three tokens. The term comes from NLP research in the 1990s. Researchers needed a unit smaller than a word because language does not break the same way across every language. They borrowed "token" from linguistics, which borrowed it from old English "taken," meaning a sign or a symbol. A token is just the smallest meaningful chunk of a sentence.



There are only so many tokens an AI can hold in its context window before it starts failing. When people say "context window," they mean how many tokens the AI can see at once. That window is finite.



So if you dump everything into one conversation, an AI writing a blog post is also reading your video production notes. You are wasting tokens on information that has nothing to do with the task. The folder structure solves this by separating your work into areas and only loading what is needed for the task at hand.



------



The workspace blueprint: three workspaces for three kinds of work



Here is the concept. Instead of one giant conversation or one massive file, you break your work into separate workspaces. Each workspace handles a different kind of work.

#### For example:

— content, docs, community management



— scripts, animations, code, builds



Writing Room



— blog posts, newsletters, thinking, client work



These are just examples. Your workspaces will look different depending on what you do. A freelancer might have Client Intake, Delivery, and Admin. A developer might have Frontend, Backend, and Docs. The names change. The structure stays the same.



------



What VS Code is (and why you do not need it)



In the video, you will see me working inside VS Code. VS Code is an IDE, a developer environment that lets you see all your folders and files in a sidebar and open them without double-clicking through your file system. It makes it easier to bounce between files.



You do not need VS Code to do any of this. You can work inside your regular file explorer, create folders, create text files, and edit them in Notepad or any text editor. You can also use Claude Cowork, which operates inside folders the same way. VS Code is just cleaner for managing lots of files. If it feels overwhelming, skip it for now and use whatever you are comfortable with.



------



What markdown is and why we use it



Every file in this system is a markdown file (.md). If you have never seen one before, markdown is just a text file with some lightweight formatting.



Dashes make bullets



Hashtags (pound signs) make headers



Asterisks make



That is it. When you talk to Claude and see its responses with bolding, headers, and clean formatting, it is already writing in markdown. Copy a Claude response and paste it into a plain text file. All the formatting turns into markdown symbols. That is how it was making it look that way.



A man named John Gruber created markdown in 2004. The idea was: write something readable as plain text that can also render into a formatted document. He named it "markdown" as a play on "markup language" (like HTML). Markdown strips away all the tags and complexity and makes it look like plain English with a few symbols.



Claude reads markdown cleanly. That is why we use it for every file in the system.



------



The three layer routing system



This is the core of the whole thing. Three layers. Each one has a job.



Layer 1: The Map (CLAUDE.md)



This is the top-level file. It sits at the root of your project folder. Every time Claude enters this workspace, it reads this file first.



Think of it as the floor plan. You walk into any building, the floor plan is on the wall, and you know where to go. The CLAUDE.md file tells the AI:



What this project is



What the folder structure looks like



Naming conventions for files



Where things go



This is the most important pattern in the whole system. Inside it, you put a simple table that tells the AI: for this task, read these files, skip those files, you might need these skills.



Without this, the AI either reads everything and wastes tokens, guesses wrong about what matters, or produces work you cannot edit along the way. This table eliminates all of those problems.



Layer 2: The Rooms (Workspace Context Files)



Each workspace has its own context file. When you tell Claude to work in the Writing Room, it reads the Writing Room context file. When you are in Production, it reads the Production context file. It only loads what it needs for where it is.

#### These context files describe:

What this workspace is for



What the process looks like (first I do this, then I do that)



What files are in here and how they are organized



What skills or tools to use in this workspace



You can write these by hand or have Claude help you write them. They are plain English. Short documents. A few paragraphs.



In the video, you can see what happens with almost no prompting at all. You say "go to writing room, let's start making something" and the AI immediately reads the context file, understands the workspace, loads the right voice and style, and asks what you want to build. One prompt. That is the power of Layer 2.



Layer 3: The Tools (Skills, MCP Servers, and Plug-and-Play)



Layer 3 is where skills and tools live. Skills are processes that someone figured out and packaged into a set of files that tell Claude how to do a specific thing. A PowerPoint skill. A humanizer skill. A doc co-authoring skill.



The key here: you do not load every skill into every workspace. You wire skills into the workspaces where they are needed. Your Production workspace might reference a front-end design skill and a web app testing skill. Your Writing Room might reference a humanizer skill and a doc co-authoring skill.



You can reference 15, 20, or 100 skills in a project, but each workspace only loads the ones it needs. That is the plug-and-play idea. And if you need Claude to find a new skill or create one, you can wire that ability in too.



------



Naming conventions that replace databases



One more thing that makes this system work without any code or databases. In your CLAUDE.md, you add naming conventions.

#### If a blog draft is created, it gets named like:

api-auth-guide_draft.md

#### If it is a newsletter, it gets named like:

2026-03-launch-week.md

#### If it is a demo script version 2, it gets named like:

The AI knows how to find, organize, and move files because the naming tells it everything. You can say "pull my demo v2 and build a spec from it" and Claude knows exactly where to look, what to pull, and what to do next. No SQL. No vector database. No Python injection. Just naming conventions.



------



How to make this yours



The template in the video uses a fake project with fake blog posts and demo scripts. That is intentional. You swap the names and rewrite the context files for your own work. The layers stay the same.

#### If you are a content creator:

Writing Room → Script Lab



Production → Edit Bay



Community → Distribution Hub

#### If you are a freelancer:

Swap workspaces for: Client Intake, Delivery, Admin



Your context files describe your client process instead of content production

#### If you are a developer:

Swap workspaces for: Frontend, Backend, Docs



Wire in the skills you actually use (testing, deployment, code review)



The three-layer routing system (map → rooms → tools) works the same way no matter what you do. You change the labels and the context. The architecture holds.



------



The research behind this



This is not a prompt trick. The thinking behind it comes from decades of software engineering, all the way back to 1972. Separation of concerns. Modular composition. The idea that systems work better when each part does one job and the routing between parts is clear.



There is a full research paper on this if you want to go deep. It traces the history from early programming principles through to modern AI workflows and lays out a five-layer architecture (this video covers the three most important layers). You can download it and give it to Claude to explain it to you.

#### Research Paper:

[ ICM PAPER ]



------



Quick start: your first three files



If you want to start right now with the simplest possible version, here it is. Make a folder. Put three files in it.



— Tell Claude who you are, what this project is, and where things go.

# Identity

You are helping [YOUR NAME] with [WHAT YOU DO].

# Folder Structure

\-    /drafts — work in progress

\-    /final — finished outputs

\-    /references — background material

# Rules

\-    Read this file first on every new task

\-    Ask before creating files outside of /drafts

\-    When unsure, ask



— Describe the current project.

# Current Project

[What you are building or working on. 2-3 sentences.]

# What good looks like

[What a successful output looks like.]

# What to avoid

[Common mistakes or things you do not want.]



REFERENCES.md



— Background material Claude should know about.

# References

[Examples, links, style guides, notes. Anything Claude should have access to but does not need to act on directly.]



Point Claude at the folder (using Claude Code, or upload the files to a Claude Project, or paste the contents into your first message). Ask it something related to your project. Notice the difference.



------



Want to customize this for your specific use case?



3.2: Customizing for Your Use Case



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=1285fe09df7943e79e5d71c68b8b3ccb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



walks through three real examples.



Want to understand



structured context changes AI output at a fundamental level?



2.3: How a 1953 Word Game Explains AI Memory



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



traces it back to Mad Libs.



The concept of "value lives above whatever just got commoditized" shows up in



2.4: The Ladder That Explains Every AI Failure



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Ready to see this running in the terminal?



4.1: Install and First Use



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



gets you into Claude Code.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



VIP members



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2fffffc3?md=bc7ea453811b4a6b9ebba1bb6c3a0d5e&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



: the full Workspace Blueprint template (the one from the video) is in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



You will see how the three-layer folder architecture changes shape for three different kinds of work. The layers stay the same. The names, the context files, and the routing all change. You will walk away knowing how to build yours.



Hi everyone. In this video, we're going to dive into my concepts around folder as a workspace and architecture. What it means to use AI in a way that will actually probably last the next decade and what I think the industry is actually moving towards. Now, if you've seen any of my other videos, I'm sure you've seen screenshots or snippets of crazy folder structure I'm doing where I'm routing Claude to different folders, my markdown files, using skills at certain times, creating animations or code with it. I have all sorts of different ways I'm doing it, but I don't think I have a video out there that really dives into how I structure it and teaching you to do that. And I decided to go ahead and create a kind of template folder to walk you through all of this. This is something you could use to be able to apply to any of your workflows, build through it, understand it, and kind of explore, you know, building your own version of this. Now, throughout this video, I'm actually going to teach some concepts along the way for people who are not familiar with maybe VS Code, which is the workspace I'm working in. Don't worry, you don't need VS Code to do the things I'm showing you. You can do it within Claude, but I just want to describe like what markdown is, what it means to have an IDE, all of these things. And if you are familiar with these, you're software engineer, you probably are, don't worry, I'm still going to be diving into the specifics and I think you're going to get a lot of out of this either way. However, sometimes it's also nice to just dive back into the fundamentals. So, let me paint a little scene for you. Right now, most people, if they are even I which fun fact about 84% of the nation is still not fully using it, but log in and use Claude or ChatGPT or Gemini and they're typing things. They're diving in. Um, maybe they get something back, they start another conversation, start over, and sometimes they're able to share context between conversations, right? Like ChatGPT and Claude can do that. I can say, you know, tell me a software stack for Visual Lore, which is a software that I was working on for another company, and it's able to go and look through our older conversations, which is nice. That's a little bit of extra there, but it's still not, you know, it's not able to look at files, have persistence, things like that. And you're constantly having to make these huge prompts. Maybe you have some sort of prompts that you save and throw in or documents, and you're throwing it in, and then you have to start a new conversation. Throw it in, start a new conversation. You hit a wall, there's too many tokens, right? All sorts of problems there. And don't get me wrong, there's some really good prompt engineering techniques out there, but at the end of the day, AI can only hold so much in a single information or chat area, and even further, that's not your workflow. Having to have it create a whole bunch of stuff and then re-edit it again, it's it's not sustainable, it's not scalable. Now, for those of you who don't understand why they struggle so much, essentially, AI reads everything, all of your sentence, and measures it by something called tokens. A token is roughly three quarters of a word or a single word sometimes. The word hamburger could be three tokens. Ham-bur-ger, hamburger. The term comes from NLP research in the '90s. A bunch of researchers needed a unit smaller than a word because language doesn't all break the same way, right? So, they borrowed token from linguistics, which borrowed it from Old English tucken, which means a sign or a symbol. A token is just the smallest meaningful chunk of a sentence or a word. There's only so much tokens an AI can have in its context window before it starts failing. When people say context window, they mean how many tokens the AI can see at once, and that window is in fact finite. So, if you dump everything into one file, an AI writing a blog post is also reading your video production notes. You're burning tokens on stuff that doesn't matter. So, instead of building one big file, you want to separate your thoughts, your ideas, your work into separate areas. This is something I created for all of us. It's called a workspace blueprint. Here, you have three workspaces. And again, this is an example. You don't always have to do this. But each one handles a different kind of work. One for the community, right? Maybe I have this one for working on content and docs in the community. Production, right? What am I building? What are scripts? Maybe I'm creating animations. Writing room. Maybe I need to have some sort of process of thinking or I have a client list or insert as many things as I have there. And we're going to dive deeper into it. This is a space that does the job well because you can circumnavigate an AI seeing everything and only direct it to what you want. Let me explain how that actually works though. So, I'm going to show you inside of VS Code, which is an IDE, basically a developer environment that allows people to kind of look at folders in a different way. So, instead of having to click into the folders like you just saw here, I can just open the folders and see everything and open the files without having to double-click the files, right? So, instead of having to double-click this text document and opens another window, I can just bounce between them. It's much cleaner, much easier. Even if you're not into code, it looks overwhelming. I promise you all of this is just natural language. This literally reads like a document. So, this is a markdown file. If you haven't seen them before, markdown is just a text file with some lightweight formatting, right? You have dashes for bullets. You have hashtags or pound symbols if everyone else remembers when they were just called that for headers. Um, you have all sorts of stuff like asterisks for bolding or doing things in that way. And there's a lot of programs that can actually run this to look a certain way. In fact, your Claude does exactly that. If you look, when you're talking to an AI, it's writing in markdown already. These boldings, these lines, all of these things. Watch what happens when I copy this. All of that formatting disappears when I paste it into here, and it turns into markdown because that's how it's making it look like that. Markdown is just a good way to format text. If you're curious, there's a man named John Gruber. He actually created this in 2004. The whole idea was write something that's readable as plain text, but can also render into a formatted document. He named it markdown as a play on markup language, which is the same stuff that HTML, right? The stuff that builds websites, hypertext markdown language. And all it does is mark stuff down with tags. Markdown strips all the tags and absurdity away and makes it look like something simple like this. But again, you're probably not here for this. You're here for the file system. So, let's move on to that next step. So, in this specific folder, which is an example, it runs on essentially three layers, and there's a reason for each one. If you look at my Claude.md, my Claude markdown file, this is something that my AI will read every time it's in any one of these folders. So, this is something that the AI will always have and always read. So, imagine it's you're just copying and pasting this into Claude code or into Claude every time you open it. Now, you can actually just type in to Claude read the Claude.md. In this case, it's Claude code. You could be working inside of Claude co-work as well, which is again a video I have on how to install, and it can operate inside of folders in case the VS code is too much for you. Um but just read the Claude.md and tell me what this is. Before you had to copy and paste, do all these things. It had to read the every file that's in here. In this case, it reads the Claude.md and immediately, without having to read everything else, understands the product, the process, what's going on, my writing room, my production, my community. It knows where to find it, what the file names are. All from just a single text prompt that allows it to understand where to go, what to do, what are these areas. But let me describe this a little simpler for those of you who might, you know, feel like this is a bit overwhelming. Layer one in this is the map. This is what loads automatically, right? It's looking at it. So you put the stuff the agent always needs to think about, folder structure, naming conventions, where files go. Think of this as the floor plan. You walk into any room, the floor plan is on the wall, and the agent knows where to go. Now, layer two is where the floor plan tells you to go. It's the actual rooms. What is your task? Go here. I want to write a blog post, well then you need to go to here and read this context or this markdown file. If you want to build a demo or a video, you need to go here and read this context or markdown file. And this could be one that you wrote by hand, or it could be one that you told Claude to wrote. And we're going to dive into that here shortly. Layer three is the actual workspace itself. Where do you want your files going? What content are you doing? If you're writing stuff, where do you want the events to be? Where do you want newsletters to be? Where do you want social to be? And it's just a file system. Again, if you don't want to work inside of here, you can actually just go straight into the folder and just create new folders, new text document. That can be a prompt, that can be a context, right? It's that simple, and you can just you can just edit it without any of this. Look, my uh my claude.md, this is what it looks like in if you open up notepad. Same thing. And nothing breaks when you edit it. You can type whatever you want in here. It's just English. Now, it's good to have it uniform and well, but that's the idea here. Most people are only doing one one these layers, maybe two. The reason you want to actually have these three layers is it stops the narrow funnel of AI doing too much all at once without allowing you to edit every single part, but still give you the ability to automate the entire process. So, again, the router, the initial Claude at MD or whatever you're naming it, is loaded when you start any task. The workspace is loaded when you're in the workspace, when you want to do production, it's only reading stuff that's in production as it needs to. When you're doing stuff in the writing room, it's only writing it when you're in the writing room. For example, go to writing room, let's start making something. Very little prompting, almost terrible prompting. Yet, the agent, without wasting a whole bunch of co-kens and going through everything, immediately goes to the context file that I have in writing room that describes what it is, describes what to load and what not to load, and just describes the folder structure and what the process is. First, I understand the topic, then I find the angle, then I write it, then I catch problems. You can also incorporate skills into this, right? So, you can download the humanizer skill, which is an actual GitHub, I recommend you all check out, or like doc co-authoring skill, which is another set of markdown files or even Python scripts and tutorials that someone else build to do a certain task. And this is where this whole process is different than just running skills. You're putting skills inside of a thought process. And as you can see, right here, we're in the writing room. Clean slate, no drafts in progress. Voice is loaded, style is Block Host. What do you want me to make? From one single prompt, we've gotten it in there. But while that's going on, I can open up another Claude and I can say, "Hey, I want to do some work in production." And it's going to go in there and I can do whatever work I want to do in production, right? I want to maybe make some designs, I want to create some sort of code for workflows in there. But the real fun happens is when you're building stuff in production with one of your Claude Code instances. You're writing a script and you can say, "Hey, take the script from writing room and let's make an animation out of it in production." It's moving that file. It's going to go there. Now, it's going to notice that I don't have any scripts in there when I send this out. But if I did have a final in there, it's going to go look for it, right? There's no scripts. Boom, it didn't waste a whole bunch of tokens, it didn't do anything, but it immediately knew, "Oh, well, we have to write a script first." Or if you have a script somewhere else, you can upload it. You see, most apps or frameworks or agentic things require you to build an agent for each of these. I need a writing room agent, I need this agent, I need this agent. But the way in which you approach each task is always different. Why not just have Claude Code become the agent you need when you're working in the work space. And you see from there, you get the most important part of this process is just good routing in English language. Again, this is all just English, right? File folder names, titles. It's describing what you want, right? This right here is the most important pattern in the whole system. It's just a simple table that tells the AI, "For this task, read these files, skip those files, you might need these skills." Without this, the AI either reads everything and runs out of the room and just does all sorts of stuff you don't want it to do using way too many tokens, or it guesses wrong about what matters or just doesn't hit what you need, or you can't edit what it creates along the process. This table eliminates all of those problems. This This system here gets rid of all of that. Now, let's go ahead and zoom in a little bit here and actually really look at this kind of folder structure. Walk through this pipeline. Imagine you're sitting here and you open up production and you go to workflows, right? So, you know you're doing some sort of animation production or insert whatever it is that this folder is as a separate workspace as part of a larger tasks flow that you're doing. Production has a pipeline in itself as well. Four stages. You have to do a brief, you need a spec, which a specification, a build, and an output. I have a brief, some sort of script that I want to do. I have a spec that's generated from that brief, and then goes into the builds, and it builds out the animations, and then finally you have the output. More importantly, this allows me to have one MD file, right? So, for my production, I can have a ton text for this file system that is generating different types of sub agents or ways to look at it. Again, I'm not even worried about agents. I'm just worried about what the workspace is, what I want to do in these workspace. If I want to understand, look up technical standards, look up design rules, I can find that because I might have that in a doc, right? So, I have components or maybe some way I like to design these systems with my color designs, my headers, my quality. And again, these are all just generated from English super short docs. These are visual philosophy or what type of tech you want to use. And it doesn't always have to read that, but maybe during the brief stage, it does, right? When you're sitting there and you're going through and you're loading the brief, well, I need to make sure you look at the tech standards when you're making the brief. If it's loading the spec, I need to make sure it looks at the design system and our component library, and then maybe it doesn't need to load the deck as well. And you can swap this around super easily just by looking at it. This is traditional function calling software routing. This has existed for decades and decades, but now it gets to be natural language, English. Now, at this point, many of you are like, "Oh, well, you're just making a bunch of skills." Technically, yes. Now, for those of you who don't know what skills are, again, I mentioned them earlier. I I talked about this idea that you can download them from everywhere. There's PowerPoint skills, and I have other um videos on this. But at the end of the day, skills are a process that someone else figured out and designed a set of packages or folders, just like I'm doing here, to tell Claude how to do something. The thing is, skills aren't just markdown files with instructions. Some are just that, but skills work best when they're wired into a system. One important note, too, is this is where the difference between it's just skills we're creating here and it's a system. You're actually putting skills inside of your MD. So, in this case, I have in my context for production, I have the fire outlook, what I want to do, but also, right? This is where you can talk to call skills or MCP servers. If you don't know what an MCP, model context protocol. I think that deserves an entire video in itself, but just think of it as a way that the AI can talk to other apps and services easier. It's designed to just kind of plug and play it in, rather than you have to create all these custom integrations. At certain points, we might want the front-end design skill or a web app testing skill or PDF skill. Or, I might want to give Claude the opportunity to look up a skill, find a new skill, or even possibly create one. You can wire up to 15 skills, 20 skills, 100 skills into a workspace. Or, you can perfectly add the skills where you would need them inside the workspace, rather than having them loaded at all times. That's the whole idea here is about plug and play and routing. One other sneaky thing I do to like completely ignore like databases or anything like that, in my Claude MD, the main file at the beginning that shows, you know, every AI or every agent that comes into this workspace can see my entire folder structure navigation, I just add naming conventions, right? So, if a file's going to be outputted a certain way, it needs to name it. For blog drafts, it needs to be like file name, where it's at. Is it draft? Is it V2? Is it V3? Example, API off guide draft, right? Or same for newsletters. Here's the year and day, and then here's what it's kind of is, right? 2026 03 launch week. md. So, the AI knows to organize and move stuff, which comes in handy when instead of having to navigate through these files or have an agent that's connected to some sort of, you know, SQL database or vector database or query or Postgres or anything like that, I could just say, "Hey, pull my uh off demo demo V2 and build a spec from it. It immediately knows, without me doing anything, to look where that V2 demo script would be, because it knows how to find it. It knows to pull it. Then it knows to read the docs associated with specs and then start building it. I have zero code, technically speaking, running any sort of Python injection or framework or database. This is tools that people are building right now. They're building apps and crazy Python stuff, which in some very bespoke cases might be useful, but most of the time for most people, you don't need all that extra stuff to get the process and the job done. The job to be done is more important than this kind of rigid architecture that so many people are building. You see, the folder becomes your app. This is your UI. What simpler UI than a folder? And the best part is, I don't even need to technically click on anything. I could just talk with my voice to AI, have it do all the text work for me. The next stage of this, I promise you, within 6 months everyone's going to be doing this, is just talking to your folder setup. It's going to be designed and set up to be this way. It's going to be around yours, which leads into a good final point. How do you make this yours? This template uses a fake idea with fake process, right? Fake blog posts and demos. If you're a content creator, writing room might become your script lab. Production becomes your edit bay, uh whatever. Community becomes a distribution hub, and you're going to remove and change these rules to edit your platform, maybe your tone and voice inside of these, right? So, what is your audience? That's what you want to hear. It's working developers, 2 to 8 years of experience, technical decision-makers, developer advocates. It might be something completely different. You might be in construction or real estate. But, this is roughly what you would be doing across all of them. And the best part is, all you need is one subscription to Claude Code, and you can generate 100, {quote} {unquote}, apps that are just folders creating what you need. Obviously, it's much more complicated once you get into breaking down your workflow, but if you're a developer, if you're a freelancer, right? Just swap design for engineering and docs, or intake and production and delivery, right? This workspace changes lately, but the three-layer routing system, the idea that you go from, "Hey, look at this area. This is what you're going to." to lower-level context ones, to lower-level skills, is the idea here. It's just layers. This isn't a prompt trick. This isn't some sort of crazy infrastructure. It's folders and markdown files with the understanding of advanced software engineering. Every conversation after that, the AI knows where it is, what to load, what tools to use, and where to put the work in. Now, there is a lot of history behind my thinking. I didn't just randomly come up with this, and there's a lot of people who are already doing this. And the reason they're doing this is because it works. I'm writing a very large research paper right now that goes into the history of programming's rules of transparency, rules of composition, um all the way back down to 1972, and then I'm bringing it forward and applying all this stuff to modern-day AI, what it means to have humans in it. And I specifically talk about the layers that we could actually have. And I actually go into a five-layer architecture in the paper, but realistically, most of you just need to understand the three main layers that we talked about here. I will be making videos on this. However, it is in the main chat. Um if you want to download this and give it to Claude so that it can tell you about it rather than having to read through it, I highly recommend that. In fact, I urge you to do it because some of this is kind of technical information. nerdy. I'm being structured in it. But, this is layering out what the next decade is looking like. And this isn't because I'm predicting the future, it's because I'm learning from the past, from the last 200 years of software engineering, and I mean 200 when I say that, and applying it to AI. I want to teach the concepts that last, not the concepts that are replaced next month. I understand that some of this might be a little fast. It might be a little confusing. I'll keep making deeper dives. Give me feedback on what you didn't understand. How? Did I move too fast? I want to make these better every day. Again, I'm making these on my own. So, hopefully, this all gave you a good idea. If you do want access to any of these files or worker templates, um I am giving them already to my VIP and my uh premium accounts. It's my one way of like the work, right, to be able to support this. So, if you're able to subscribe, amazing. If it actually is that much of a financial challenge, please reach out to me. I can try to see if I can get you something, you know, quick and easy for you. But at the end of the day, go go check it out. Go check out all my other courses that I'll be doing. And again, as always, happy learning.



------



Jake's content\The Foundation\3.2 Customizing for Your Use Case.md



3.2 Customizing for Your Use Case



What You'll Get From This



You will see how the three-layer folder architecture changes shape for three different kinds of work. The layers stay the same. The names, the context files, and the routing all change. You will walk away knowing how to build yours.



------



One structure, every use case



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



you saw the full architecture: a top-level identity file (CLAUDE.md), workspace-level context files, and skills or tools that plug in where needed. The example in the video used a fake project with a community workspace, a production workspace, and a writing room.



That example was intentional. It is close enough to real work that you can see the logic, but generic enough that you have to make it your own. This lesson shows you how.



The principle is short: the layers do not change. The labels do. Your CLAUDE.md still sits at the top and routes everything. Each workspace still has its own context file. Skills still plug in where they are needed. But what each workspace is called, what the context files say, and what skills are wired in will look completely different depending on what you actually do.



Here are three real examples. Find the one closest to your situation, study it, then build your own.



------



Example 1: Content Creator



You make videos, write posts, manage a social presence, and probably do it mostly alone or with a very small team. Your work moves through a cycle: come up with ideas, write scripts or outlines, produce the content, publish it.

#### Your workspaces:

my-content-project/ ├── CLAUDE.md ├── script-lab/ │  ├── CONTEXT.md │  ├── ideas/ │  ├── drafts/ │  └── final/ ├── production/ │  ├── CONTEXT.md │  ├── briefs/ │  ├── specs/ │  ├── builds/ │  └── output/ └── distribution/ ├── CONTEXT.md ├── platforms/ ├── scheduling/ └── analytics/

#### What each workspace does:

— This is where thinking happens. Ideas go in. Drafts come out. The CONTEXT.md in this folder describes your voice, your audience, the kind of content you make, and the process you follow from idea to finished script. (could also reference separate MD files, if there is a lot of info in these) If you have a style guide or a list of topics you keep coming back to, that goes in here. Claude reads this context and writes in your voice from the first line.



— This is where content gets built. If you are making animations (like the pipeline in



Section 2.6



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), this is where your briefs, specs, and build files live. If you are making simple videos, this might be where your shot lists, thumbnails, and description templates go. The CONTEXT.md here describes your production process, your tools, your visual standards.



Distribution



— This is where finished content goes out. Platform-specific formatting (what works on Instagram vs LinkedIn vs YouTube), scheduling, repurposing long content into short clips. The CONTEXT.md describes your platforms, posting cadence, and any rules about how content should be adapted per channel.

#### What the CLAUDE.md looks like:

Your top-level file tells Claude what this project is and how to route between the three workspaces. Something like:

# My Content Project

I create [TYPE OF CONTENT] for [AUDIENCE].

## Workspaces

\-    /script-lab — Idea development, writing, drafts

\-    /production — Building and producing content

\-    /distribution — Publishing, scheduling, repurposing

## Routing

| **Task**             | **Go to**     | **Read**   |
| -------------------- | ------------- | ---------- |
| Write or brainstorm  | /script-lab   | CONTEXT.md |
| Build or produce     | /production   | CONTEXT.md |
| Publish or repurpose | /distribution | CONTEXT.md |

## Naming conventions

\-    Drafts: topic-name_draft.md

\-    Final scripts: topic-name_final.md

\-    Published: YYYY-MM-platform-topic.md



------



Example 2: Freelancer / Consultant



You work with multiple clients. Each engagement has a lifecycle: intake, scoping, delivery, follow-up. You need Claude to shift between clients without bleeding context. You also need your own internal workspace for business development, templates, and admin.

#### Your workspaces:

my-consulting-practice/ ├── CLAUDE.md ├── client-alpha/ │  ├── CONTEXT.md │  ├── intake/ │  ├── deliverables/ │  └── communications/ ├── client-beta/ │  ├── CONTEXT.md │  ├── intake/ │  ├── deliverables/ │  └── communications/ ├── templates/ │  ├── CONTEXT.md │  ├── proposals/ │  ├── reports/ │  └── frameworks/ └── business-dev/ ├── CONTEXT.md ├── pipeline/ ├── outreach/ └── case-studies/

#### What each workspace does:

Client workspaces



(one per client) — Each client gets their own folder with their own CONTEXT.md. That file describes who the client is, what the engagement is, what phase you are in, what the deliverables are, and any client-specific rules (tone of voice, terminology they use, things to avoid). When you tell Claude "let's work on Alpha," it reads Alpha's context and nothing from Beta. No bleed. No confusion.



— Your reusable frameworks. Proposal templates, report structures, analysis frameworks. The CONTEXT.md here describes what each template is for and how to use it. When you start a new engagement, you pull from templates into the client folder and customize.



Business Dev



— Pipeline tracking, outreach drafts, case studies from past work. The CONTEXT.md describes your ideal client, your services, your positioning. When you need Claude to help draft an outreach email or build a case study, it reads this context.

#### What the CLAUDE.md looks like:

# My Consulting Practice

I am a [TYPE] consultant working with [TYPES OF CLIENTS].

## Active Clients

\-    /client-alpha — [One-line description of engagement]

\-    /client-beta — [One-line description of engagement]

## Internal

\-    /templates — Reusable proposals, reports, frameworks

\-    /business-dev — Pipeline, outreach, case studies

## Routing

| **Task**              | **Go to**     | **Read**                       |
| --------------------- | ------------- | ------------------------------ |
| Client work for Alpha | /client-alpha | CONTEXT.md                     |
| Client work for Beta  | /client-beta  | CONTEXT.md                     |
| Build a new proposal  | /templates    | CONTEXT.md, then client folder |
| Outreach or pipeline  | /business-dev | CONTEXT.md                     |

## Rules

\-    Never reference one client's information in another client's workspace

\-    Proposals always start from /templates and get customized in the client folder

\-    Deliverables go in /client-[name]/deliverables, drafts stay in working folders



The key for freelancers: the client folders multiply. When you onboard a new client, you copy the structure, write a new CONTEXT.md, and Claude is ready. The CLAUDE.md at the top gets one new line in the routing table. That is it.



------



Example 3: Developer



You build software. You might work on one project or several. Your work involves planning, writing code, testing, deploying, and documenting. You probably already have opinions about folder structure. The difference here is that Claude reads it.

#### Your workspaces:

my-app/ ├── CLAUDE.md ├── planning/ │  ├── CONTEXT.md │  ├── specs/ │  ├── architecture/ │  └── decisions/ ├── src/ │  ├── CONTEXT.md │  ├── components/ │  ├── services/ │  ├── utils/ │  └── tests/ ├── docs/ │  ├── CONTEXT.md │  ├── api/ │  ├── guides/ │  └── changelog/ └── ops/ ├── CONTEXT.md ├── deploy/ ├── monitoring/ └── scripts/

#### What each workspace does:

— Specs, architecture decisions, design docs. The CONTEXT.md describes the app, the tech stack, the current priorities, and any architectural principles you follow. When you tell Claude to help you spec a new feature, it reads this context and works within your existing architecture.



— The actual codebase. The CONTEXT.md here describes the code structure, naming conventions, patterns you use (and patterns you avoid), testing requirements, and any libraries or frameworks that are standard in the project. Claude writes code that fits your codebase because it read the rules first.



— API documentation, user guides, changelogs. The CONTEXT.md describes your documentation standards, the audience for each type of doc, and how docs relate to the code.



— Deployment, monitoring, operational scripts. The CONTEXT.md describes your infrastructure, deploy process, and any runbook conventions.

#### What the CLAUDE.md looks like:

# My App

[APP NAME] — [One sentence description]

## Tech Stack

\-    Frontend: [framework]

\-    Backend: [language/framework]

\-    Database: [type]

\-    Deploy: [platform]

## Workspaces

\-    /planning — Specs, architecture, decisions

\-    /src — Application code

\-    /docs — Documentation

\-    /ops — Deployment and operations

## Routing

| **Task**        | **Go to** | **Read**   | **Skills**          |
| --------------- | --------- | ---------- | ------------------- |
| Spec a feature  | /planning | CONTEXT.md | —                   |
| Write code      | /src      | CONTEXT.md | testing-skill       |
| Write docs      | /docs     | CONTEXT.md | doc-authoring-skill |
| Deploy or debug | /ops      | CONTEXT.md | —                   |

## Naming conventions

\-    Specs: feature-name_spec.md

\-    Components: PascalCase

\-    Tests: feature-name.test.ts

\-    Decision records: YYYY-MM-DD-decision-title.md



Developers will notice the routing table has a Skills column. This is Layer 3 from 3.1. You can wire testing skills, documentation skills, or code review skills into specific workspaces so they only load when relevant. Your planning workspace does not need the testing skill. Your src workspace does



------



How to build yours



You do not need to match any of these exactly. The process is the same regardless of what you do.



Step 1: List your workspaces.



Think about the 2-4 major areas of your work. What are the modes you shift between? Writing and building are different workspaces. Client A and Client B are different workspaces. Planning and executing might be different workspaces. If you find yourself wishing Claude would "forget" what it was just doing and focus on something else, that is a workspace boundary.



Step 2: Write a CONTEXT.md for each one.



Describe what happens in this workspace, what the process is, what files live here, and what good work looks like. Keep it under a page. You can always add more later.



Step 3: Write your CLAUDE.md.



List the workspaces and build the routing table. For each type of task, tell Claude where to go and what to read. Add naming conventions so Claude knows how to organize files.



Step 4: Start working.



Point Claude at the folder and give it a task. See what happens. Adjust the context files based on what Claude gets right and what it gets wrong. The first version will not be perfect. It will be better than no structure at all, and it will get better every time you edit a context file.



The context files are living documents. Edit them as your projects change, as you learn what Claude needs to know, as you figure out what to cut. The people who get the most out of this system are the ones who treat the context files like working notes, not finished documents.



------



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



VIP members



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2fffffc3?md=bc7ea453811b4a6b9ebba1bb6c3a0d5e&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Workspace Blueprint



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=2fc827af5bcb44c9b305d2d6a12260c4&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



and Example Production MD files are in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



If you have not done the full walkthrough yet,



3.1: The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



covers the three-layer system, naming conventions, and the research behind all of it.

#### Common mistakes people make when setting up their folders are covered in

3.3: Common Mistakes and How to Fix Them



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=7b1919bbe3af42aa859b6060e4e7513f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. Worth reading before you finalize your structure.

#### The prompting framework from

1.3 How to Structure Any Prompt



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



works inside each workspace. Your context files handle identity and project context. Your prompts handle task, constraints, and output format. The two systems work together.

#### The production pipeline example from the

2.6: Video as Code



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



lesson is a real implementation of the content creator structure above. If you want to see what a mature version of this looks like in action, start there.



------



Before you finalize your setup, take five minutes to read the mistakes people make most often. Easier to avoid them now than fix them later.



------



Jake's content\The Foundation\3.3 Common Mistakes and How to Fix Them.md



3.3 Common Mistakes and How to Fix Them



What You'll Get From This



The seven mistakes people make most often when setting up the folder architecture, and how to fix each one before it wastes your time.



------



Every one of these comes from real community members. People post their setups, run into walls, and ask for help. The same problems show up over and over. If you read this before you finalize your structure from 3.2, you will skip most of them.



------



Mistake 1: Making the CLAUDE.md too long



The CLAUDE.md is a routing file. It tells Claude where things are and where to go. That is its job. It is not a project brief. It is not a style guide. It is not a brain dump of everything you want Claude to know.



When the CLAUDE.md gets too long, two things happen. First, Claude burns tokens reading information that is not relevant to the current task. Second, the signal gets buried in noise. The routing instructions (the part that actually matters) get lost in paragraphs of background context.



Your CLAUDE.md should fit on one screen. Identity, folder structure, routing table, naming conventions. That is it. Everything else belongs in a workspace CONTEXT.md where it only gets loaded when Claude is actually working in that area. If your CLAUDE.md is longer than 40-50 lines, you have context files hiding inside it. Pull them out.



------



Mistake 2: Skipping the routing table



Some people set up the folders, write the context files, and never put a routing table in the CLAUDE.md. They assume Claude will figure it out.



Sometimes Claude does figure it out. But "sometimes" is the problem. Without a routing table, Claude has to guess which files to read and which to skip. It might read everything (wasting tokens) or read the wrong context file (getting confused about what workspace it is in). The output gets inconsistent. Some responses are great, some are off, and you cannot tell why.



The routing table does not need to be complicated. Three columns: task, where to go, what to read. One row per type of work. Claude reads the table, matches the task, goes to the right place. Every time.



| **Task**            | **Go to**     | **Read**   |
| ------------------- | ------------- | ---------- |
| Write content       | /script-lab   | CONTEXT.md |
| Build something     | /production   | CONTEXT.md |
| Publish or schedule | /distribution | CONTEXT.md |



If you added skills (Layer 3), add a fourth column. Otherwise, three is enough.



------



Mistake 3: Too many workspaces



Someone sets up eight workspaces for a project that really only has two or three modes of work. They have a workspace for research, a workspace for notes, a workspace for drafts, a workspace for editing, a workspace for final review, a workspace for publishing. Each one has its own CONTEXT.md. The CLAUDE.md has a routing table with twelve rows.



Now the overhead of maintaining the system is bigger than the work itself. Context files go stale. Claude spends more time navigating between workspaces than working in them. The whole point of the architecture was to reduce complexity, and instead it multiplied it.



Start with two or three workspaces. You can always add more. The question to ask: "Do I shift mental modes between these tasks?" Writing and building are different mental modes. That is two workspaces. Drafting and editing are the same mental mode at different stages. That is one workspace with a process inside it, not two workspaces.



If you are not sure whether something deserves its own workspace, it does not. Keep it as a subfolder inside an existing workspace. You can always split it out later if the work grows.



------



Mistake 4: Writing context files that describe what AI should be instead of what the work is



This one is subtle. People write context files full of instructions about Claude's personality. "Be creative. Be concise. Be professional. Think step by step. Use a warm tone." They spend 30 lines describing how Claude should behave and two lines describing the actual project.



Claude responds to context about the work far more than context about itself. Telling Claude "you are a senior copywriter" gives it a role. Telling Claude "the audience is mid-market HR directors who have tried three other tools and are skeptical of AI claims" gives it something to actually work with. The second one changes the output more than the first.



Flip the ratio. Spend 80% of your context file describing the work: what the project is, who the audience is, what has already been done, what good output looks like, what to avoid. Spend 20% or less on behavioral instructions. If your context file reads like a personality quiz, rewrite it. If it reads like a project brief that a new team member could pick up and start working from, you are in the right place.



------



Mistake 5: Never updating the context files



Someone sets up the folder in week one. Writes the context files. Gets great results for two weeks. Then the project evolves. New requirements, new direction, new constraints. But the context files still say what they said on day one. The output starts drifting. Claude is still working from old context. The member thinks Claude "got worse" when really Claude is doing exactly what the context tells it to do. The context is just stale.



Treat context files like working notes. When the project changes, edit the context. When you learn something new about what Claude needs to know, add it. When a constraint no longer applies, remove it. This takes 30 seconds per edit. It is the single highest-leverage habit in the whole system.



Some people add a "Last updated" line at the top of each context file. Simple but effective. When you open a workspace and see "Last updated: six weeks ago," you know to review it before working.



------



Mistake 6: Putting everything in one folder and hoping the CLAUDE.md sorts it out



The opposite of too many workspaces. Everything lives in one flat directory. Fifty files. No subfolders. The CLAUDE.md tries to route between them using file names alone. Claude reads the whole directory listing, picks what it thinks is relevant, and often picks wrong.



This is the equivalent of dumping every document on one desk and asking someone to find the right one. They can do it. It just takes longer, they make more mistakes, and they get frustrated.



If you have more than 8-10 files at the same level, you need subfolders. Group by workspace (what kind of work), then by stage or type within the workspace. The folder structure is the architecture. It tells Claude what belongs together. Let it do that job.



------



Mistake 7: Building the whole system before using it



The most common mistake. Someone reads 3.1 and 3.2, gets inspired, and spends an entire weekend building a perfect folder architecture with six workspaces, detailed context files, naming conventions, skills wired into every workspace, and a routing table with twenty rows. They have not used Claude once during this process. They built the factory without ever making a product.



Then they start using it and realize half the decisions they made do not match how they actually work. The workspace boundaries are wrong. The context files describe what they thought they would need, not what they actually need. They have to rebuild.



Build the minimum. One CLAUDE.md, one or two workspaces, one CONTEXT.md per workspace. Start working. After a few days, you will know what is missing. Add it then. After a week, you will know what is wrong. Fix it then.



The best folder setups in the community were all built incrementally. They started simple and grew based on real work. The ones that stalled were the ones that tried to be complete before day one.



Your first version should take 15 minutes. If it took longer, you over-built.



------



The pattern across all seven



If you look at these together, they all point in the same direction. Keep the system small. Keep it focused on the work, not on Claude. Update it as you go. Let the structure grow from use, not from planning.



The folder architecture is powerful because it is simple. Folders and text files. The moment it starts feeling heavy or complicated, something went wrong. Go back to the three layers from 3.1: map, rooms, tools. If your CLAUDE.md is the map, your context files are the rooms, and your skills are the tools, and each one is doing only its job, the system stays clean.



------



If you have not built your structure yet, go back to



3.2: Customizing for Your Use Case



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=1285fe09df7943e79e5d71c68b8b3ccb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



and start from one of the three examples. Build the minimum version. Come back here when you run into something.

#### The prompting framework from

1.3 How to Structure Any Prompt



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



helps with Mistake 4. Your context files handle identity and project context. Your prompts handle the per-task stuff. Separating those two keeps your context files focused on the work.

#### The production pipeline in

2.6: Video as Code



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is an example of a system that grew incrementally. It started as a simple folder and became a full spec-to-animation pipeline over weeks of use. That is the right pace.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



(Premium) has the full Blueprints with example context files already written. If you want a starting point that is further along than the quick-start three files but still customizable, that is what it is for.



------



Next Up: Section 4 —



You have the architecture. You know how to customize it and what to avoid. Section 4 gets you into Claude Code, the terminal tool that makes all of this run. If you have been using Claude Projects or pasting context into the browser, Section 4 is where you level up.



------



Jake's content\The Foundation\4.1 Install and First Use.md



4.1: Install and First Use



What You'll Get From This



All of these sessions will be based around Claude, however the concepts and ideas span across all models and tools within reason.



All three Claude interfaces installed and working on your machine. A clear sense of when to use which one. And your first real task run on your own files.



------



Video: Session 1 — Installing Claude Desktop and Claude Code



This is the first of five sessions. Each one builds on the last and each one ends with something on your computer that was not there before. Here is the full series:

#### Session 1 (this lesson):

Install all three interfaces. Understand when to use which.



Session 2 (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=6ccef7306c3c4ba29373f018a75e0748&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Claude Code in practice. The real power and workflow.



Session 3 (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=865ac85d10064187bd7eb14e11204aa9&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Claude Desktop as a thinking partner. More than just generating stuff.



Session 4 (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=f0655889bd8c49b0a99f5afb9eb03229&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Making Claude understand your project. Consistent, quality results.



Session 5 (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=dd5a0adc38a440f29b48354a3a9da667&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Where all of this goes. The file architecture system and what comes next.



------



How most people use Claude



Most people use Claude like a search engine that writes better sentences. You type a question, you get an answer, you copy and paste it somewhere. That works. But it is like using a car to check the mailbox. The car can take you across the country. You just have not left the driveway yet.



Today we leave the driveway.



------



Three interfaces, one model



This is the thing most people miss. There are three ways to use Claude, and they are not three different AIs. It is one model with three different ways to access it. The difference is what each interface lets that model see and do.



Claude Desktop (or



The downloaded app or the website. A conversational tool. Great for planning, thinking through ideas, getting answers, building drafts. But there is a limit to what it can do at scale. It cannot see your files directly. It cannot run code. It cannot edit anything in your project. Everything goes through copy, paste, or uploads.



That is not because the model is limited. The model is extremely powerful. The problem is the interface. It just cannot reach your stuff. If you have ever felt like Claude kind of gets it but not quite, it is probably because you are working from a pasted excerpt instead of your actual project.



Claude Code in VS Code



This is what I use for almost everything. Your files are on the left. Claude is on the right. It reads your project, edits your files in line, runs commands. You do not copy and paste anything. You describe what you need and it works directly within the files.



VS Code (Visual Studio Code) is a coding environment made by Microsoft. If you have never opened it, do not worry. It is simpler than it looks and we will walk through setup. You do not need to know how to code. VS Code just lets you see your folders as a file tree and open documents without clicking through layers of windows.



If you are familiar with Cursor, Windsurf, Copilot, or Antigravity, those are all built on top of VS Code. They support different models and different processes. Some use Claude, some do not. This course is specifically for Claude's tools inside the Anthropic environment.



Claude Code in the terminal



The same engine under the hood, just a different wrapper. The terminal version is better for when your work does not live in a code project. Processing a folder of documents. Managing files. Cleaning up your downloads folder. Anything where you just need Claude to read a bunch of files and do something with them.



You do not need the terminal version to get value from this course. But if you are already comfortable in the terminal, it is faster for some jobs.



------



The real difference



The desktop is a conversation layer. VS Code is an editor layer. The terminal is a command line layer. Same brain behind all three.



Interface Best for Can see your files? Can edit your files? Claude Desktop /



http://claude.ai/



Thinking, planning, quick questions, drafting Only if you upload them No Claude Code in VS Code Building, editing, working inside a project Yes, automatically Yes Claude Code in terminal File processing, quick tasks, non-code projects Yes, in the current folder Yes



------



Let me show you the difference



Here is the same task across all three.

#### In Claude Desktop:

You want to summarize a document. You go find the file on your computer. You upload it. You type "Summarize this PDF and suggest three improvements." Claude processes it and gives you a good answer. Works fine. But you had to go find the file, upload it, and then the summary lives in the chat. If you want it in a file, you copy and paste it somewhere.

#### In VS Code:

You open the folder where the document lives. You type "Summarize python breakdown PDF and suggest three improvements." Claude immediately knows which file you mean because it can see the folder. It reads the file, gives you the summary, and can write the output directly to a new file in the same folder. One less step. No uploading. No copy-paste.

#### In the terminal:

You open a terminal in the folder, type



, and give the same instruction. Same result as VS Code, just a different window. Better for quick one-off tasks where you do not need to see the file tree.



The model gives the same quality answer in all three. The difference is how much manual work you do around it.



------



Installing everything



Let's get all three working.



Step 1: Claude Desktop

#### If you do not have it already:

claude.ai/download



http://claude.ai/download



and download the app for your OS (Mac or Windows). Install it. Sign in with your Claude account.



That is it. You now have the conversational interface.



Step 2: Node.js



You need Node.js before you can install Claude Code. Node.js lets you run JavaScript on your computer and gives you access to the



command for installing packages.



http://nodejs.org/



and download the LTS version. Run the installer.

#### To verify it worked, open your terminal and type:

node --version



If you see a version number, you are good.



Step 3: Claude Code (terminal)

#### With Node.js installed, run this command in your terminal:

npm install -g @anthropic-ai/claude-code



Once it finishes, you can type



in any folder and Claude Code will launch.



Step 4: Claude Code in VS Code

#### First, install VS Code if you do not have it:

code.visualstudio.com



http://code.visualstudio.com/



and download it. Install it. Open it.

#### Then install the Claude Code extension:

In VS Code, look for the



icon in the left sidebar (the one with squares, one slightly tilted). Or press



Ctrl+Shift+X



(Windows/Linux) or



Cmd+Shift+X



"Claude Code"



Click the blue



You may need to restart VS Code



You should now see the Claude Code icon in your sidebar. Click on any file to open a page, then the Claude panel will be available.

#### One thing that trips people up:

When you open a brand new folder in VS Code and nothing is there, the Claude panel might not appear. You need to click on a file or have a page open for the extension to activate. Also, VS Code has its own built-in chat that is separate from Claude Code. Make sure you are using the Claude Code extension, not the VS Code native chat.



------



Troubleshooting



"npm: command not found"



— Node.js did not install correctly. Close your terminal completely, reopen it, and try again. If it still fails, reinstall Node.js.



"Permission denied" during npm install



— On Mac/Linux, try:



sudo npm install -g @anthropic-ai/claude-code



Claude Code launches but asks for authentication



— Follow the link it gives you to sign in. You need a Pro or Max subscription.



VS Code extension does not show Claude panel



— Make sure you clicked Install, restarted VS Code, and have a file open. Check that you are using the Claude Code extension, not VS Code's built-in chat.



If you get stuck on any of this, post in the community or Discord with your OS and the error message. Someone has hit the same wall.



------



Your first real task



This is not just a lecture. You should walk away with something done.



Pick one thing from your own work. A document, a report, a file you have been meaning to process. Put it in a folder.



Try it in Claude Desktop: upload the file, ask Claude to summarize it or answer questions about it.



Try it in VS Code: open the folder, ask Claude Code the same thing. Notice that you did not upload anything. It just read the file.



Compare the experience. Think about the workflow. Which one felt faster? Which one would scale better if you had ten files instead of one?



This exercise is not about getting a perfect answer. It is about feeling the difference between pasting context into Claude and having Claude go to where the context already lives.



------



Why this matters for everything that comes next



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=5d535542a72d417e8635b80e56412558&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you set up a folder with three files and pasted context into Claude or loaded it into a Project. That worked. But it was manual.



Claude Code makes the folder architecture from



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



fully operational. Your CLAUDE.md, your context files, your workspaces, your routing table. Claude Code reads all of it live. It navigates between workspaces, loads the right context, follows the routing table, and works inside your file system. The folder becomes the app. Claude Code is the thing that runs it.



Sessions 2 through 5 build on this. We go from installation to real workflows, thinking partnerships, project-level understanding, and the full architecture. But it all starts with having these three tools working on your machine.



------



Claude Desktop



http://claude.ai/download



http://nodejs.org/



http://code.visualstudio.com/

#### Claude Code Install:

npm install -g @anthropic-ai/claude-code



------



If you have not set up your folder structure yet, go back to



1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



for the quick version or



3.1: The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



for the complete architecture. Claude Code is what makes those folders fully operational.



Already comfortable with Claude Code?



4.2: Claude Code in Practice



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=6ccef7306c3c4ba29373f018a75e0748&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is the next session, showing you the real power and workflow.



Want to understand the model behind all three interfaces?



2.2: One Line of Python Triggers 12,000 Lines of Code



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=18fb23fa6b084725937e8d47606f376a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



traces what happens underneath when you type a command.



------



You have the tools installed. Next session shows you the real power: how to actually work with Claude Code on a real project, the workflow that makes it useful, and the things you can do that are impossible in the chat interface.



Welcome, welcome to a five session series. Now, this initial first session is on how to use Claude desktop and Claude code. We're going to be diving into a lot in the second session, which is actually Claude code in practice. So, if you've already gotten it installed, maybe you can jump there. However, I'd be, you know, I give a caveat there because I dive into certain things in this session, this first one, that are, well, maybe something you might not have installed or done for your Claude code. So, even if you're a veteran, I recommend you checking it out. Uh I also have a session three, it's going to be on Claude desktop as a thinking partner, right? How do you actually use this in more than just generating stuff for you? From there, session four is going to dive into making Claude code understand your product or your project, right? This is more than just asking it to run and hit something. How do you make it work with you in your project and get really good results consistently out of it. Finally, session five is going to dive into where all of this goes and how you can actually do a deeper dive into a file architecture system I call model workspace protocol. And that's really high-level good stuff. It's a separate course, but I touch on it a lot here in session five. So, let's go ahead and um dive in. Now, the goal for this session is to actually have you walk away with real deliverables, not just like awareness or whoa, I understand AI better, but actual artifacts sitting on your computer after each session. All three interfaces installed and working, real tasks that you can use and run on your files, a clear sense of when to use which tool, when not to, so you stop guessing. I'm also going to show you what a good Claude and D file is, a markdown file for Claude that completely changes how Claude works on your projects, and a preview of something bigger in session five that I just mentioned that might be the most valuable part of all of these sessions, but, you know, I think it's all pretty valuable. Now, most people use Claude like this. It's more like a search engine that writes better sentences or code or something like that. You type a question, you get an answer, and then you copy and paste it or move it somewhere. And that works, but it's like using a car to check the mailbox. The car can take you across the country, you just haven't left the driveway yet. And we're going to try to leave the driveway today. Now, Claude desktop, just the normal downloaded version, is very similar to the one that you'd log in on the website, and it's more of a conversational tool with all the good stuff that Claude has, and you can get a lot done with it, and it's great for planning, thinking out ideas, building stuff, all that jazz, but there is a limit to what it can do at scale. It can't see your files necessarily, and I'm talking purely just about the chat version. It can't run code, it can't edit anything in your projects, and everything has to go through copy, paste, or uploads. And that's not because the model is limited, it's extremely powerful, just the desktop version, but the model is the same one powering everything else. The problem is the interface. It just can't reach your stuff. So, if you've ever felt like Claude is like kind of gets it, but not quite, it's probably because you're working with a more pasted expert excerpt excerpt instead of your actual project. Now, this is what I actually use for almost everything. Claude code living inside VS code. Your files are on the left, you can easily see them. If you're on Mac, it's a little bit different as well, and Claude is on the right. It reads your projects, edits your files in line, runs commands. You don't copy and paste anything, you just describe what you need, and it works directly within the files, right? If you already use VS code, Visual Studio Code, and you're open to trying it, this is actually where I'd start. For those of you who've never opened VS code before, we'll get you set up in the hands-on section, and it's simpler than it looks, but just keep that note. I'm going to walk you through install instructions and everything for that. There's also just the most generic way to use it, which is Claude through the terminal. Uh it's the same engine under the hood, but a kind of different wrapper. The terminal version is better for when your work doesn't live in a code project, processing a folder of documents, managing files, cleaning up your downloads folder, anything where you just need Claude to read a bunch of files and do something with them. You don't need this one to get value from this course, but if you're already comfortable in the terminal, it's actually faster for some jobs and I do it once in a while. And this is the thing that most people miss. It's not three different AIs, it's one model, three different ways to access it. Technically, there's a little bit of fine-tuning difference with Claude Code and whatnot, but at the end of the day, the desktop is a conversation layer, VS Code is an editor layer, and the terminal is the command line layer. Same brain behind all three. The difference is what each interface lets that brain see and do. Although, quick note, there's things out there called Cursor or Wind Surf or Co-pilot or Google's Anti-gravity, and those are completely different products that are built on top of VS Code. So, VS Code is the source IDE, right? An interface for developer environments, but the uh actual buildings or the interface of the layers are just supporting different models or different processes. Some of them actually use Claude and some don't. Some mix multiple models, and I do have an entirely separate course diving into the pros and cons of each of them, which one you actually want and breaks it down, but this course is specifically for Claude's tools and the way inside of the Anthropic environment, and that's all we're covering here. Now, let me show you what the difference between all of these kind of looks like, uh just really quick off the bat if you've never used any of them. So, first of all, we have Claude Desktop or the Claude normal one that you're actually going in through there. And let's say I wanted to just be able to summarize a document, right? We come in, we have to go find the document wherever we had put it, we come in, we open it, we upload it, and then from there I can say summarize this Python breakdown PDF and suggest three improvements. And it's going to go ahead and it's going to go through and do that. Right now I'm using Opus 4.6, which is the more powerful one, um and it's doing a pretty good job, right? It's good. It's good. It's nice, and I'm sure it's going to be a great one when we're done with this, right? But then from there, I actually want to be able to possibly use VS Code, right? And so this is what it looks like, right? This is your VS Code. You have your file explorer here where you're able to see all your files and you'll be able to break them down. You'll I have an extension that allows me to open a whole bunch of Claude Code tabs. That's another immediate usefulness out of this is the fact that I can have a whole bunch of conversations all going at once and I can swap between them. But it's the same aspect, except this time I can just say summarize Python breakdown PDF. It's going to immediately know which file we're in. It's going to go find it, and it's going to go read and search through it immediately. So that's already one less layer of work that you have to do, and it still does all the same good stuff that the normal 4.6 would bear. You can also do the same thing inside of uh the terminal. I have this terminal open inside of this file here, right? As simple as this. I come in, I open, I hit open terminal, and it immediately is inside this folder, right? I just type Claude and it opens it up. And I can say the same thing here. Same power as the VS Code one, except the difference is I have to read everything inside the terminal. Again, something nice, but it just depends on what you kind of want there. Now, the pattern here is pretty straightforward if you haven't noticed, right? The normal Claude chat is just for good conversation and some work that you just want to bust out quickly. It's also good for finding memory. Code is more for action, right? Being able to quickly scale things, right? It's not as useful the difference in one file, but as soon as I have a hundred files that I need to roll through, it's much easier to actually use Claude Code. The difference is simply what they can touch and how they access it. The one worth paying attention to on this chart is the iterate on output. With the normal chat one, you have to read the response, decide what's wrong, copy it, start again, but with Claude code, you can say that's not right, fix this, and move it into a separate folder. You can break down your processes as you're going along and you're delegating instead of rounds of copy and paste in a single chat environment. For those of you who've been using the chat or the desktop and feel like you're getting these issues or there's a lot of manual work to kind of continuously get good results even if you copy and paste prompts, this is exactly why. Your interface is playing the middleman stopping you from working as well. The folder structure, being able to access files, all of this is extremely important. Now again, I use VS Code extension for almost everything. I'm in VS Code anyway for most of my projects cuz I do a lot of coding. So having Claude right there in the sidebar and being able to open multiple work trees is the fastest path. The terminal is nice if I want to go quickly, but most of the time I just open up VS Code anyway. The desktop is something that I can use from anywhere even though you can do remote access with the VS Code terminal now, so I can use it on my phone. It's just sometimes a cleaner interface for when I'm not doing these deep stuff. Now your setup might look a little bit different from mine if you're on Mac or you're you know different colors and stuff like that and that's fine. Some people end up using desktop 80% of the time because their work is mostly thinking and planning anyway. So some of you might live in the terminal for whatever reasons, right? Just being able to use those commands. But the point is knowing that each one is good for you in specific areas, so just pick the right one and what you like working with and feels right for you rather than just forcing everything through one interface. Just play around with it, see what you like. The desktop is kind of the easiest to use. It's the least control over what Claude can do. The terminal is flexible, arguably the most flexible because you can kind of open it up anywhere and you can open multiple terminals in different ways and bounce between it, but it's kind of a weird learning curve is not as visual. But at the end of the day, the VS Code one is this middle ground, I think. It gives you this familiar editor if you're used to it or at least an area to see and it has the full power of the normal Claude code. Okay, you might have noticed that the lighting has changed and I have changed my shirt as well as my hair. That is because it is the next day. I am recording all of this, building everything that you're seeing. So, just friendly reminder, I'm doing this all on my own and this is free. So, just bear with me here. Trying a little hard. But, let's go ahead and go into installations of all of these, right? So, we're not just going to look at one, we're going to look at all of them. So, doing Claude to install Claude desktop, it's actually quite simple. You just go Claude desktop. You can look straight on, you know, anywhere. Download Claude. You're going to make sure it's actually from Anthropic, from Claude. You're going to look, are you on Mac? Are you on Windows? Or you ARM 65? For those of you who are curious what that even means, there's certain ways in which your operating system works and the way it's coded. Most of you are just going to be normal Windows. If you ever need to check if you are ARM 65, it has to do with the type of processor that you have. If you're on Windows, you simply just type in settings, you go to settings, you go to system, right here under system, then you're going to scroll all the way down and it should have something called about. This is on Windows 11, obviously. You could find this roughly the same on any other one. And if you look at this, it should say Windows specifications and device specifications. Under system type, it should say 64-bit operating system on x64-based processor. That's the standard Windows. That's the normal Sometimes they'll say x86, which is technically similar. It would actually say 64-based arm-based processor if you had an arm system. Some AMD processors, right? I have an AMD Ryzen 9 are similar in that way. Just a kind of certain note there for those who are curious. If you want to dive into why that's the case, what of that means, it has to do with actual instructions for the processor and lower languages. I'll probably make a course on that later on. But let me know if that's something you need. So you download it and then all you're going to do is actually just click install. I think I had one downloaded. Yep, and you'll just click Claude setup. It'll install it. You give it permissions and then it's just like if you were using Claude, the initial one, anywhere else you log in. Now I have the maximum account, so I also get access to something called Claude Co-work, which is a version of Claude code that's able to work through all your folders inside of the app. So this is kind of like the chat plus the ability to actually use it. And then there's actual Claude code, which is built around you selecting folders and being able to edit it, which we'll dive into a bit later. But that's it. It handles most of it for you and it also helps you install Claude code the non-manual way. So you should be able to do this in that way. However, I'm going to show you some ways to handle it so that you can have it directly on your system as well outside of Claude code. Now installing Claude code, you do require to have certain things. You need something called Node.js. Now there's a couple ways to install this. You can even if you just downloaded the app, you can actually go to code and have Claude code install it for you. However, for those of you who want to do it manually yourself, there's a couple ways. You can either go to Node.js, right? And you can just download their installer. It says get Node.js. This is just essentially a JavaScript library that allows it to run on your computer. JavaScript is required for Claude code to work a certain way. Sometimes this actually is installed with this into a certain extent, but generally isn't. So, you need to make sure that it's installed there. Once you have Node.js installed, uh you can then use something called an NPM command, right? This is super useful. I think you all should, if you're diving into startups or anything like this, you should have this installed anyway because it makes life 10 times easier down the line. Whenever I'm doing animations or stuff like that, being able to do what we're about to do here is really nice. So, you want to open the command prompt. There's a couple ways to do that. You can either just type in CMD. If you're on um Mac, you want to type in your integrated terminal. It's probably what it would look like. It should pop up something similar to this. And all you're going to do, if NPM was stalled properly into your path, uh which means essentially that your computer can access it from anywhere, you should be able to put this command in and it will actually install Claude code directly from Claude and Anthropic's status stores. It'll install it onto your computer. Again, if you're having trouble with this, you can actually install Claude through the desktop and have it help you walk through this or just use Claude in general to kind of help you walk through it. I highly recommend that as I may miss something that your computer doesn't have or there's certain little things about packages and permissions and where it's installed on your computer. Uh I highly recommend Claude, ChatGPT. They can all help you through that process. Um but, if you were to do it that way, that's something you can do. Once it's installed and properly there, all it should be is literally from anywhere on your computer, if it was installed right, you can type in Claude and it'll actually that command will go and say, "Hey, do you trust this workspace?" Yes, I do. It'll have you log in and you can either log in with an API key. You actually need to go to Claude API developer platform, right? Which is still on claude.com. It's still your same account if you want to log in with it. Now, if you log in and it takes you back to your normal chat account, you accidentally clicked back on normal. What sometimes helps people is actually going to typing in Anthropic console and specifically finding platform.claude and signing in on that part and that sometimes forces it to go through. It should look something similar to this, right? It's a little bit different than the normal Claude, but you should be able to go down where it says API keys on the bottom left. You'll have to go through. Now, you should have created an organization or maybe you have to add in billing cuz this is separate from your normal Claude account and certain billing that you actually have to do. Don't worry, you can't see all of my key there, which is nice, but you can actually just create a new key and you can copy that and give it to the terminal. Now, I don't recommend this at all because at the end of the day, if you are paying for a subscription account, you can just log in to Claude code through this through your subscription account. It'll say, "Hey, log in with subscription." You'll click it. It'll open up in your tab. You hit authorize. Boom, you're done. But for those of you who have maybe a reason to do this and there are certain software reasons which I described later on why. Just wanted to show what that looks like and I'm probably going to show it in future, you know, ones as well, but important to understand here, right? Then from there, you have Claude anywhere on your computer, right? You can have it access any sort of folders, things like that and it's ready to go. And there's a lot of different commands that you can use, right? Web app testing, you can download skills. There's all sorts of things of sub agents having Claude use agents. Um I'll go into that in future lectures for sure as well, but I just want everyone to understand and understand how to be installed, so to speak. This, in my opinion, is the best combination, being inside of VS Code. For those of you who don't know what VS Code is, it's called Visual Studio Code. It's the generic coding app that Microsoft has made. It's very nice. If you're familiar with Cursor or Anti-Gravity or any of these agentic coding tools, they're actually all just built off of VS Code, so I prefer to just use VS Code because there's no bloat, there's no extraness. They have any access that you want in there. It's already built for people to be coding. You don't need to know how to code to use it, right? It lets you open any sort of folders and look at it in a completely different way than you've never seen it if you've ever used it. It's made for developers, but I actually like it for a lot of other reasons. So, let's open up my content development folder, which I already have one open. And essentially, it lets you see your entire folder. Again, let me show you what this looks like just normally. So, if you were to go onto your normal Windows, this is what this looks like. It's the same thing. But now, instead of having to click into it to see everything, I can open it up like trees and see all of my folders and processes. From there, I can actually open up these uh oops, these documents as well to be able to see what's going on inside of them without having to close the folder or have a separate tab. But even better, I can open up Claude right in the middle, and all I have to do is hit this little button here, right? Um this button I can also I have Codex installed, OpenAI's Codex, to be able to pop over here and use it when I need to. But right now, we're focusing on Claude. This is super great because what if I'm having multiple chats and want to switch between them and work on multiple things at the same time? This becomes super useful. I can read what it's editing while bouncing between chats, and it just becomes so nice. But, how do I get this here? Well, first, you need to make sure you've done the installation process before with the normal Claude code. But, once it's on and once you install um VS Code, Visual Studio Code, again, if you're on Windows, you can literally just download it from the App Store. Um it should pop up pretty easily. Just install that. Make sure it's good to go. And from there, you actually will open up VS Code, and you want to actually look for something called extensions. So, on the left here, you're going to have a whole bunch of options, but this one right here with the squares and the one slightly tilted called extensions. You can also hit control shift X. Will open it up, and you can just type in Claude code, and it says Claude code for VS Code, and you're going to have a little button blue button that says install. You'll click install, and that's it. You might have to restart it, but you should now see this there. One important note some people get confused by is that when you open up VS Code, and you open up like maybe a brand new folder that you've never touched before. So, let's do uh let's do this one. Right? Yes, I trust the authors. Uh if sometimes you have this, right? Where there's nothing there, and you see nowhere to add anything. You actually need to click on something and have a page open to get that little extension open. Also, VS Code has its own chat built in as well that you can use just in case something's wrong with Claude, or you're not paying for the account. And what's really cool is you can add your own language models in here if you log in, and you can add Claude to this as well. I just like to use directly through Claude cuz there's it's cheaper, it works better, it's cleaner, there's less bloat, and I really think it's the way to go. I'll have a whole video on which models are good at what, which one's better. At the end of the day, pick one and build the systems and the knowledge of how to use that one well, it will easily transfer all the other ones and you can make your choice after you get decent at using one, okay? Simple as that. And if you have any questions about this whole install process, please throw them in the community. Happy to help out. Happy to try to figure it out for you. That's the main goal I had for all of this. Now, one thing that I want you all to do, as I said, this isn't just a lecture. I'm going to give you some homework or at least something that you can do and I'll have links for files and documents that are a little extra curricular if you need to practice, but pick one thing from your own work and actually try to get it summarized. Put it in a folder, have Claude code summarize it, try to use it with your normal Claude desktop, whatever you choose, and try to get it to answer things or build things from that single file. Run it in desktop, then try the VS Code extension if you want. Maybe look at the outputs, but think about the workflow, right? This is really important. You want to be able to build with these. You want to create scale. It's not just about installing something that's good. It's about thinking about, all right, if I'm going to be building a lot of stuff, if I'm running a company, running a startup, running a content things, what works best for me to create these builds? In my opinion, I love just having a folder that I enable to navigate easily inside of VS Code because that means I have all the access to stuff. I can organize it, right? All of your courses I'm building right here. I'm working with Claude Code because again, I don't want it to automate the whole process. I want it to help me make this process better because I'm doing this all on my own. I would usually have to hire a full team to do all of this, but because I've organized it in how I work, how I think, like, oh, I've got my cleat notes for all of you here. I have my scripts for my long form and stuff that I can edit easily in here. Um, if I don't like a script, I can change it and then Claude can easily reference it, right? That's why I like using VS Code so much. It's just It's a really great platform to look at, but you can use the normal Claude, you know, code or code work to do this as well. It's just I find it harder because it's I don't get to see everything. I want to be able to click back and forth quickly and it just kind of gets in the way. So, practice with it, try to see what you like better, what works for you, then we can think about sitting down on one specific tool and using that only. If you do have any comparisons or anything where you're like, "Hey, this happened with one." Please post them. Is there anything that surprised you where you're like, "Whoa, I didn't know Claude could see that on my computer or execute stuff." This is kind of what we want to do. Now, this is the end of the first session. I'm going to be posting this right now after I'm done editing and taking out all the nasty parts where I maybe skipped something or said something wrong, but session two is actually going to be showing you Claude code in practice. I'm going to be filming that now. Hopefully, by the time you're watching this video, I'll have already posted it. If you're early comer, then you probably aren't going to see it, but I promise you I'm working hard to get this all out to you all. So, yeah, stay tuned. We're going to be diving into a lot in that session about how to use Claude code, its real power, how you can see and get that kind of workflow process. Cuz you see, this isn't just about using an AI model, this is about designing your workflow to really get a lot out of it. But, till next time, friends. Much love and please stick with me as I build this channel and this community.



------



Jake's content\The Foundation\4.2 Claude Code in Practice.md



4.2: Claude Code in Practice



What You'll Get From This



You will understand what makes Claude Code different from the chat interface, see the iteration loop in action, and walk away with a real deliverable built from your own files.



------



Video: Session 2 — Claude Code in Practice

#### Coming Soon

------



The real power



Claude Code is not smarter than Claude Desktop. It is the same model. The difference is what it can reach. Claude Code can see your work, touch your files, and iterate on its own output. That changes everything about how you work with it.



The loop looks like this: Read → Think → Write → Check → Adjust. Claude reads your files, thinks about the task, writes output, checks its own work, and adjusts. In the chat interface, that loop runs once and stops. In Claude Code, it runs until the job is done.



------



Example: meeting notes



Here is a task that shows the difference clearly.



You have 15 meeting notes. You want every decision made this quarter, organized by project.

#### The Desktop approach:

Open file 1. Copy the text. Paste it into Claude. Ask for analysis. Repeat 15 times. Then manually combine all 15 responses into one document. About an hour of work.

#### The Claude Code approach:

One prompt: "Read every file in /meeting-notes/ and summarize all decisions, organized by project." One prompt. 15 files. 90 seconds.



The model gives you the same quality analysis either way. The difference is how much manual work you do around it. Claude Code eliminates the copy-paste layer entirely.



------



Claude's context window is roughly 200K tokens. A typical meeting note is about 2,000 tokens. 15 notes is about 30,000 tokens. Well within the window.



In Desktop, you paste one file at a time and lose context between chats. Each conversation starts fresh. You are working against the architecture.



In Claude Code, it loads what it needs from your file system and keeps full context across the task. You are working with the architecture.

#### This is the same principle from

2.3 (How a 1953 Word Game Explains AI Memory)



: the context window is working memory. Claude Code lets you fill that working memory from your actual files instead of from your clipboard.



------



Tips that save hours



Be specific.



"Analyze this" is weak. "Identify the three largest cost items and format as a table" is strong. The more specific your instruction, the less Claude has to guess. This is the Task part of the prompting framework from



Tell it where to put the output.



"Save the result as summary.md in this folder." Claude Code can write files. Let it. If your output lives in a chat window, you still have to copy it somewhere. If Claude writes it directly to a file, it is already where it needs to be.



Output wrong? Do not start over.



Say what is wrong. "The summary missed the budget decisions from the March 14 meeting. Add those." Claude iterates. That is the whole point. Starting over throws away all the context Claude has built up about your task.



Claude Code is best for tasks that involve reading and writing files.



That is where it shines. If your task is "help me think through a decision," Desktop might be better (that is Session 3). If your task is "read these 15 files and produce a deliverable," Claude Code wins every time.



------



Your first real task

#### Pick one of these (or something similar from your own work):

"I have documents or notes. Summarize them."



"I have a spreadsheet or CSV. What is interesting in here?"



"I have a report or proposal. Find the gaps."



"I have a folder of files. Organize them by [criteria]."



Open your folder in VS Code. Click Claude in the sidebar. Describe your task specifically. Watch it work. Iterate if something is off.



You should walk away with a real deliverable from your own files. Something you can actually use tomorrow.



------

#### The prompting framework from

1.3 How to Structure Any Prompt



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



applies directly here. Identity and context come from your files. Task, constraints, and output format go in your message.

#### Token math and context windows are explained in depth in

2.3: How a 1953 Word Game Explains AI Memory



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



If your task involves processing lots of files across different types of work, you may want the folder architecture from



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



to organize things before you start.



------



Claude Code is for building. But sometimes you need to think before you build. Session 3 shows you how to use Claude Desktop for planning, pressure-testing ideas, and finding blind spots, and then take that clarity into Code to execute.



------



Jake's content\The Foundation\4.3 Claude Desktop as a Thinking Partner.md



4.3: Claude Desktop as a Thinking Partner



What You'll Get From This



You will stop using Claude Desktop like a vending machine and start using it as a thinking partner. You will work through a real problem, find an insight you did not have before, and understand when to think in Desktop and when to build in Code.



------



Video: Session 3 — Claude Desktop as a Thinking Partner

#### Coming Soon

------



The mistake



Most people use Claude Desktop like a vending machine. Question in, answer out. "Write me a marketing plan." Claude gives you a document. You paste it somewhere. Done.



That works for simple tasks. But it wastes the most powerful thing Claude can do: think with you.



There is a difference between prompting for content and prompting for thinking.

#### Prompting for content:

"Write me a marketing plan." You get a document. It might be good. It might be generic. You will not know until you read it and by then you have already spent the tokens.

#### Prompting for thinking:

"I am trying to reach [audience] with [constraint]. What am I not seeing?" You get clarity. You get your own assumptions challenged. You get the blind spots surfaced before you build anything.



------



What Desktop excels at

#### Claude Desktop (the conversational interface) is the best tool for:

Challenging your assumptions



Finding blind spots in your plan



Pressure-testing ideas before you commit



Structuring messy thinking into something clear



Exploring trade-offs between options



None of these require Claude to touch your files. They require Claude to think alongside you. The chat interface is built for exactly this.



------



Planning, then execution



Here is the workflow that saves the most time.

#### Without planning:

You open Claude Code and start building. Halfway through you realize you are not sure what you actually want. You restart. You try a different approach. You restart again. Three restarts. Two hours.

#### With planning:

You open Claude Desktop and spend 15 minutes thinking through the problem. What are you building? Who is it for? What does success look like? What are the trade-offs? You get clear. Then you open Claude Code and build it. One build. 30 minutes.



The 15 minutes of thinking saves 90 minutes of building the wrong thing. Desktop for decisions. Code for execution.



------



Desktop Projects



Claude Desktop has a feature called Projects. You can give a Project your key documents, preferences, or background material. Every conversation you start inside that Project has that context already loaded.



This is the lightest version of "giving AI context about your work." If you did



1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



, you already understand the concept. Projects are the browser-based version of the same idea: persistent context that stays across conversations.



Think of Projects as the seed for what comes next in Session 4. They give Claude background. Session 4 (CLAUDE.md) gives Claude deep project understanding.



------



Desktop for decisions. Code for execution.



If you are deciding what to build, use Desktop. If you are building it, use Code. If you try to decide and build at the same time, both suffer.



Start with what you are trying to accomplish, not what you want Claude to produce.



"I need a marketing plan" is a product request. "I am trying to get 50 signups for a workshop in two weeks with no ad budget" is a problem. Claude is a better thinking partner when it knows the problem.



Push back on the first answer.



"What is wrong with this?" "What am I missing?" "What would someone who disagrees with this say?" The first answer is often the obvious one. The second and third answers are where the value lives.



Conversations are disposable. The thinking is not.



Do not treat a Claude conversation like a document to save. Treat it like a whiteboard session. The value is the insight you walk away with, not the transcript.



------



Think through a real problem



This is the exercise. Do it now.



Pick a real problem or decision you have been sitting on. Something you have been putting off or going back and forth on.



Open Claude Desktop. Do not ask "solve this." Ask "help me think through this."



Use the conversation to clarify your thinking. Push back on Claude's suggestions. Ask it what you are missing.



Write down the key insight or decision you reached.



(If you have time) Take one action item into Claude Code and execute it.

#### Conversation starters if you need them:

"I am trying to decide between [A] and [B]. Here is my context: ..."



"I have a plan for [X]. What am I not seeing?"



"Here is a problem I keep running into: [describe]. What patterns do you notice?"



------

#### Desktop Projects are a lightweight version of the folder architecture from

1.2 Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. If you want the full system,



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



has the complete method.

#### The prompting framework from

1.3 How to Structure Any Prompt



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



is running under all of this. When you prompt for thinking instead of content, you are shifting from Task-heavy prompts to Context-heavy prompts.



The "plan before you build" principle shows up in



2.6 (Video as Code)



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=3a82e3222c2c4cbc9d07c6f9f6d4265a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



: the spec is where creative thinking lives, the build is execution. Same idea, different scale.



------



You can think with Desktop and build with Code. But Claude still does not understand YOUR project. Session 4 fixes that with one file.



------



Jake's content\The Foundation\4.4 Making Claude Understand Your Project.md



4.4 Making Claude Understand Your Project



What You'll Get From This



You will write a CLAUDE.md file that makes Claude Code behave like it has been on your project for a month. One file. Ten minutes. The difference is immediate.



------



Video: Session 4 — Making Claude Code Understand Your Project

#### Coming Soon

------



One file changes everything



In Session 1 you installed Claude Code. In Session 2 you used it on real tasks. In Session 3 you used Desktop for thinking. All of that worked. But there is a problem you have probably already noticed: Claude Code does not know your project.



It does not know your conventions. It does not know your file structure. It does not know which libraries you use, which commands to run, or what you consider good work. Every time you start a new conversation, Claude is a smart stranger. It can do the work, but it guesses at all the things a team member would already know.

#### The fix is one file:

------



What a CLAUDE.md is



A markdown file that sits in the root of your project folder. Claude Code reads it automatically every time it starts. It tells Claude what this project is, how it works, and what matters. Think of it as an onboarding document for a new hire. Except the new hire reads the entire thing in two seconds and follows every word.



------



Before vs after



Run the same task on the same project. First without a CLAUDE.md. Then with one. The difference:



Without CLAUDE.mdWith CLAUDE.mdGeneric code styleMatches your conventionsGuesses at file structureKnows where things liveDoes not know your commandsRuns your actual test suiteSuggests wrong librariesUses your dependencies



This is the same principle from



Section 1.2



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



: structured context changes the output. The CLAUDE.md is a more focused, project-specific version of the identity and context files you set up in Section 1. If you skipped Section 1 and jumped straight to Section 4, this lesson still works. But go back to 1.2 afterward to understand the bigger picture.



[📌 JAKE: The before/after demo is the most important visual in this lesson. Same task, same project. Show the generic output without CLAUDE.md, then the specific output with it. Side by side if possible.]



------



What goes in it



Five things. Keep it short. 15 lines is enough. 10 minutes to write.



1. Project overview



— Two to three sentences. What is this? What does it do?



1. Tech stack



— What languages, frameworks, databases, tools.



1. How to run things



— Dev server, tests, build commands. The commands Claude needs to know.



1. Key conventions



— Naming patterns, file structure, architectural patterns you follow.



1. What to avoid



— Things Claude should not do. Libraries you do not use. Patterns you have moved away from.



------



Example CLAUDE.md

# My Web App

React 18 + Express + PostgreSQL + TypeScript

## Commands

npm run dev | npm run api | npm test

## Conventions

Functional components only. Routes in src/api/. All database queries go through src/db/queries/.

## Avoid

No class components. Don't modify db/migrations directly. Don't use Moment.js (we use date-fns).



That is it. Fifteen lines. Ten minutes. The difference in Claude's behavior is immediate.



------



Write it for a smart person who just joined your project.



That is literally what Claude is. If a new team member would need to know it on day one, put it in the CLAUDE.md.



Update it when your project changes.



The CLAUDE.md is a living document. When you add a new convention, change a library, or shift your architecture, update the file. This is the same advice from



3.3 (Common Mistakes)



: stale context files are the most common reason Claude starts "getting worse."



Do not overthink it.



A mediocre CLAUDE.md beats no CLAUDE.md every time. You can always improve it later. The first version takes 10 minutes. Each edit takes 30 seconds. Start now.



This is not just for code projects.



If your project is a folder full of documents, the CLAUDE.md describes what those documents are, how they are organized, and what you are using them for. The same principle applies to any structured folder, whether it contains code, writing, research, or client files.



------



Write your CLAUDE.md



Do this now.



Pick a project. Work project, side project, or even a document folder.



Create a file called



in the root of the folder.

#### Fill it in using the template:

# [Project Name]

## Overview

[2-3 sentences. What is this? What does it do?]

## Tech Stack

[Languages, frameworks, tools. Or "document types" if not a code project.]

## Commands

[Dev, test, build. Or "how to use these files" if not code.]

## Conventions

[Patterns, naming, structure.]

## Avoid

[Things Claude should not do.]



Save it. Open Claude Code in the folder. Run a task.



(Optional) Temporarily move the CLAUDE.md out of the folder. Run the same task. Compare the outputs. Move it back.



The comparison is what makes the value click. You will not go back.



------



The CLAUDE.md is a project-specific version of the identity file from



1.2: Your First Folder



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. If you want to understand the full three-layer architecture (identity → workspace context → skills), go to



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Common mistakes with context files (too long, too focused on personality, never updated) are covered in



3.3: Common Mistakes and How to Fix Them



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=7b1919bbe3af42aa859b6060e4e7513f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. Every one of those mistakes applies to CLAUDE.md files too.



If you have multiple projects or different types of work,



Session 4.5



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=dd5a0adc38a440f29b48354a3a9da667&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



shows how to scale this with workspace routing.



------



You have one CLAUDE.md for one project. What happens when you have ten projects? Or a complex workflow with different types of tasks? Session 5 shows the full architecture and where all of this scales.



------



Jake's content\The Foundation\4.5 Where This Goes.md



4.5: Where This Goes



What You'll Get From This



You will see how the CLAUDE.md scales from one project to a full workspace architecture. You will set up two scoped contexts and watch Claude behave differently in each one. And you will know exactly where to go next.



------



Video: Session 5 — Where This Goes

#### Coming Soon

------



What you have built so far



Across the first four sessions, you set up three interfaces (Desktop, VS Code, Terminal), ran real tasks on your own files, used Desktop for thinking and Code for building, and wrote a CLAUDE.md that gives Claude project-level context.



That is more than most people will ever set up. And it works.



------



But what if...



You have 10 projects. Or a complex workflow with different types of tasks. Or a team that needs the same quality from Claude across everyone's work.



One CLAUDE.md per project still works. But there is a level above that.



------



Task routing



In my workspace, different tasks load different context. Automatically.



"Write a script" → loads voice docs only. "Build an animation" → loads the design system and component library. "Build a course module" → loads the curriculum and guidelines.



Same Claude. Same context window. Different context per task. The routing table in the CLAUDE.md decides what loads based on what you ask for.



This is the three-layer architecture from



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



in full operation:



Layer 1 (CLAUDE.md)



— The map. Routes every task to the right workspace.



Layer 2 (Workspace context files)



— The rooms. Each workspace has its own CONTEXT.md describing what happens there.



Layer 3 (Skills and tools)



— Plug-and-play. Loaded per workspace, not globally.



If you went through Section 3, this is what it looks like when you run it with Claude Code. If you skipped Section 3 and jumped straight to the Claude Code sessions, this is your introduction to the architecture. Go back to



Section 3.1



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



for the full walkthrough.



------



Why this matters at scale



200K tokens sounds huge until you fill it with irrelevant files. If Claude is writing a blog post but also reading your animation specs and your client contracts, you are burning tokens on context that has nothing to do with the task. The output gets noisier. The quality drops.



Task routing solves this. Each task loads only the context it needs. Clean input, clean output.

#### Three principles that make it work:

One fact, one location.



Information lives in one place. No duplication across context files. No drift where one file says one thing and another says something different.



New sessions start clean.



When you start a new conversation in Claude Code, it reads the CLAUDE.md fresh. The routing table sends it to the right workspace. No leftover context from a previous task bleeding into the current one.



Hand it to a team and everyone gets the same quality.



When the context lives in files, not in someone's head, anyone who opens the folder gets the same Claude experience. This is how you scale from one person to a team without losing consistency.



[📌 JAKE: Screenshot or screen recording of the workspace demo. Show 2-3 tasks being routed to different contexts. "Write a script" loads one context. "Build an animation" loads a different one. The visual should make automatic routing obvious.]



------



Try the smallest version



You do not need the full architecture to start. Here is the lightest way to test workspace routing.



If you have two distinct areas in your work, create two separate folders. Give each one its own CLAUDE.md with context specific to that area.



area-a/ ├── CLAUDE.md (context for Area A) └── [your files]



area-b/ ├── CLAUDE.md (context for Area B) └── [your files]



Run a task in Area A. Then run a task in Area B. Watch Claude behave differently in each one. That difference is workspace routing at its simplest.



When you are ready to put both under one roof with a single routing table, that is the full architecture from



. You already have the pieces. You just need to combine them.



------



What you have now

#### Across five sessions, you built:

Three interfaces installed and working



Real tasks completed with your own files



Desktop for thinking, Code for building



A CLAUDE.md that gives Claude project-level understanding



Two scoped context setups (basic workspace routing)



That is a working system. You can stop here and use it as-is. Most people who get this far are already getting more out of Claude than 95% of users.



------



Where to go next



If you looked at the workspace demo and thought "I want that for my whole workflow," the full architecture is in



Section 3: Folder Architecture



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



. Three lessons: the full walkthrough (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), customizing for your use case (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=1285fe09df7943e79e5d71c68b8b3ccb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), and common mistakes (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=7b1919bbe3af42aa859b6060e4e7513f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



). That section takes you from what you built here to the complete system.



If you want to build animations, the



Building Animations



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d3907117?md=f7a33a9888604a08a7e48bb876682691&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



course (Level 2) picks up from 4.1 and walks through the full Remotion pipeline.



If you want structured courses, production-grade templates, and the Workspace Blueprint, those are in



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



If you want live sessions, bespoke workspace builds, and behind-the-scenes access, that is



The Drawing Room



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2fffffc3?md=bc7ea453811b4a6b9ebba1bb6c3a0d5e&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



------



3.1: The Full Walkthrough



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— The complete three-layer architecture: routing tables, naming conventions, workspace context, skills, and the research behind it.



3.2: Customizing for Your Use Case



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=1285fe09df7943e79e5d71c68b8b3ccb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— Three real examples (content creator, freelancer, developer) showing how the architecture adapts to different kinds of work.



2.5: Clawdbot Has 100K Stars



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=190cdff0f6ed40d8b479ea675e37509a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— The orchestration-vs-intelligence distinction. What you built in these five sessions is a personal orchestration layer. Claude is the intelligence. Your folders and context files are the orchestration.



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— Workspace Blueprint, structured courses, docs, and resources.



The Drawing Room



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2fffffc3?md=bc7ea453811b4a6b9ebba1bb6c3a0d5e&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— Live sessions, bespoke builds, behind the scenes.



------



A roadmap of everything available to you across the community: free courses, Level 2 and 3, Premium, VIP. Which path fits what you want to build.



------



Jake's content\The Foundation\5.1 Your Path From Here.md



5.1 Your Path From Here



What You'll Get From This



A clear picture of where to go next based on what you want to build.



------



You finished The Foundation.



You have tools installed (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=5d535542a72d417e8635b80e56412558&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), a folder system that gives Claude context (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), a prompting framework (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=05230de8023d463f8d38fddc19152ae2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), six videos explaining the ideas underneath all of it (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=e171154adddc431ea52ff98a20f61d4f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), the full folder architecture (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



), and Claude Code running on your machine (



https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



That is a working system. Everything from here builds on it.



------



Level 2 — Implementation Playbooks



Unlock by engaging in the community. Hands-on courses where you build real projects.



Building Animations



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d3907117?md=f7a33a9888604a08a7e48bb876682691&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



The full pipeline for creating video animations with Claude Code and Remotion. Script to spec to build to render. Four lessons including a community challenge.



The Ultimate Browser (Claude Extension)



https://www.skool.com/quantum-quill-lyceum-1116/classroom/d3907117?md=bbabe44d36eb414c8f6189077c3f6185&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Claude running inside Chrome. Pull data from any page, teach Claude your workflows, automate inbox and scheduling. Four lessons with real use cases.



------



Level 3 — Building Your Stack



For members who have built with Level 2 and want to push further.



Custom UI for Claude (or Other AI)



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=c7a59d0fa0c145549dc9126470b7f82f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Build your own front-end interface for Claude. The build process, Claude Code in action, scoping your design, and open-source references to study.



Remote Access for Claude



https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=b0db9033a43540578f305e5bb936a371&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



Want to control your Claude Code on your Desktop from your phone? This course teaches you how.



------



($27/month)



Every downloadable asset in the community. Two structured courses. Discord access.

#### The Library:

Workspace Blueprint (full production folder template with routing tables and context files)



Production CLAUDE.md examples for different use cases



Folder Organization Guide



Prompting Framework Guide (one-page reference)



Animation spec templates



Workflow starter packs (content pipeline, consulting, development)



Claude Skills Manual + Resource Index



New resources added weekly



The 60/30/10 Framework



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=ca4e8c48d25840709dcca756b9e8b4ff&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— The business methodology for deciding where AI fits. Real case studies. The concept from 2.5 and 2.7 turned into an applied course.



Building Your First Workflow End to End



https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=585369b5dec148d7a20249cce06246ba&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



— From folder structure to working multi-step system. One real workflow built step by step with guidance.



Discord access (Premium channels)



Premium discussion threads



Free content teaches the ideas. Premium gives you the assets, the templates, and the guided builds to apply them.



------



($97/month)

#### Personal access. Everything in Premium plus three things:

Afternoon Tea



Live sessions every two weeks. Bring your project, your problem, your build. Small group. We work through it together.



Bespoke Builds



Fill out the questionnaire. I build a custom folder setup or workflow designed for your specific work. Your context, your use case, your system.



Discord: Drawing Room Channels



Smaller. More direct. Async access between sessions. Flag something for the next Afternoon Tea or ask a quick question.



The Drawing Room is not a content library. You are paying for proximity and personal attention. You show up, you get help, you build.



------



Not sure which path?



I want to... Start here Build animations or video content



Level 2: Building Animations Automate browser tasks



Level 2: The Ultimate Browser Build my own AI interface



Level 3: Custom UI Get templates, assets, and structured courses



Level 3: Remote Access for Claude



Premium: The Vault Get live help on my specific project from Jake



VIP: The Drawing Room



Keep learning for free



Go back through Sections 1-4 and do every check-in.



Engage in the community.



Level 2 unlocks with participation.



------



Other places to go



Community feed



— Introduce yourself. The intro post has 600+ comments and is the best place to see what everyone is building.



— Available to Premium and Drawing Room members.



https://www.youtube.com/@JEVanClief



http://youtube.com/@JEVanClief



https://www.youtube.com/@creamer\_ai



https://www.youtube.com/@creamer\_ai



https://www.instagram.com/lostandlucky



https://www.instagram.com/lostandlucky?igsh=MTV5cDg5MzhtMmtjZg==



https://www.instagram.com/creamer.ai



https://www.instagram.com/mattcreamer.ai?igsh=MXVmc2dybGY4d3cwdg%3D%3D&utm\_source=qr



https://x.com/VanCliefMedia



https://x.com/VanCliefMedia



https://x.com/creamer\_ai



https://x.com/mattcreamer\_ai?s=21



https://www.tiktok.com/@jakevanclief



https://www.tiktok.com/@jakevanclief?\_r=1&\_t=ZS-94hTesTNa6h



https://www.tiktok.com/@creamer.ai



https://www.tiktok.com/@mattcreamer.ai?\_r=1&\_t=ZT-94hTaGZ3L8n



https://www.linkedin.com/in/jake-van-clief



https://www.linkedin.com/in/jake-van-clief/



[www.linkedin.com/in/matt-creamer-ai](http://www.linkedin.com/in/matt-creamer-ai)



http://www.linkedin.com/in/matt-creamer-ai



------



Jake's content\second brain\second brain nouns and verbs.md



Most people are using their second brain wrong, and they probably don't even know it. I've built second brain systems for multi-million dollar companies and have over 40,000 people learning my methods right now. And I see a pattern people keep getting wrong both in the companies and on their own. First, I think it's important to understand what a second brain is. The idea is that anytime you talk to your AI, it remembers past work that you've done, or you can throw research papers and notes into it and it throws it into this memory base so you always have access to it. You see, most second brains that you're seeing out there are based on theories around graph theory. Actually, you have a graph made of vertices and edges. And we call them nodes or edges as well. All the dots are nodes, all the lines are edges. Those even mean? Why do they connect that way? What tells the computer to do that? Nodes, let's consider them as nouns. Person, a place, a team. And the edges are verbs. And the relationship between nouns or the things that are being done. Running, getting, consuming. Standing that, let's imagine you have a company and you have a bunch of teams. Each team becomes a node and each relationship between the team becomes an edge. Product team node talks edge to the data team node. And each team might have workflows. A workflow could be named as collecting questions from a Slack channel. If I was to say the product team runs Slack questions workflow, which consumes the ticket information and produces answers, each of these nouns and verbs can be mapped to a set of files. Most second brains would just map the whole sentence all at once to a bunch of random files. But good second brains break those down individually. You go into your product team, you'll have markdown files that describe processes, ideas, jobs, concepts. You have the markdown files, you have descriptions about where that data, processes, and ideas connect to everywhere else. This process enough times, and you'll have a giant graph of nodes and edges that describe how your company works, who they are, what they're doing, and essentially acts as a second brain or a place of memory for the AI to navigate. Want to understand how to structure folders, files, and data better? I have hours of free lectures, literally free, that you can come and check out. 40,000 people willing to work with you to understand how to build these things as well. So, the link is in the bio, go check it out. And until next time, everyone, happy learning.



------



THE LEGENDS\Back to Basics 🧱.md



Back to Basics 🧱



------



Answering Your Questions 🫵



We all know there are a ton of super high performers out there in the community. All those conversations are fantastic but I want to create a space for those who are just entering or are still trying to learn the basics.



I only started learning this stuff in March of 2026 so I can say for anyone who is just getting started that you are not far behind. It only takes a little bit of effort to see huge progress with this work.



With that being said, please give me all the things you'd like explained for you. No question is off limits. Want to know what an LLM is? Want to know what Claude is? Want to know what AI is? We are here to answer your questions!



Check out the post below and comment what you'd like to see!



------



THE LEGENDS\LinkedIn Community 🌐.md



A Home Away from Home



I created a LinkedIn group for us all to quickly find and connect with each other out there. Feel free to join and post to the feed to see all your favorite Clief Notes faces. Let's multiply our networks and push the message out as far as we can!



------



Building with ICM - LinkedIn](https://www.linkedin.com/groups/31160010/)



------



THE LEGENDS\Resources 📚.md



ICM Foundations Tutor



If you’ve been quietly struggling with learning how to build or what to build, you’re not alone. I’ve seen the posts, and I know how frustrating it can feel when things don’t click.



I wanted to try to do something about it.



I built a custom AI Tutor that has the complete knowledge and teaching style of @Jake Van Clief and @Matthew Creamer’s Foundations courses. Think of Jake as the professor. This agent is your dedicated Teacher’s Assistant who sits with you one-on-one.



https://github.com/donroy26/Clief-Notes-Foundations-Tutor



https://github.com/donroy26/Clief-Notes-Foundations-Tutor

#### Here’s why it’s different:

It walks you through every concept step by step, exactly as Jake outlines them



You’re not just chatting or watching videos. You’re actually building files and folders together in Claude



It checks your work in real time and won’t let you move forward until you truly understand



It speaks in their voice and follows their exact methodology



This is the hands-on practice and patient guidance a lot of us have been missing.

#### How to try it:

Grab the repo



Follow the README

#### Open the folder in Claude and let the tutor take over

------



I love daily puzzle games. Wordle, globle, metazooa, linkedin games; there's so many out there and they're all fantastic ways to kill time when you're struggling to dive into work in the morning.



I thought I'd combine this format with the fundamentals of ICM. What I came out with is what I call ICMadness.



https://donsbookshelf.com/icmadness/



https://donsbookshelf.com/icmadness/



Every day, a new workflow is generated that has been shuffled into chaos. It's your job to restructure the workflow to allow the agent to walk through properly.



Just like any of the games that inspired it, you can share your score for the day or go back and play older puzzles. Check out the leaderboard below to share your results.



------



ICM Foundations Tutor](https://github.com/donroy26/Clief-Notes-Foundations-Tutor)



Daily ICM Puzzle Game](https://donsbookshelf.com/icmadness/)



------



THE LEGENDS\START HERE – THE LEGENDS.md



Welcome to the Frontier, Partner.



You’ve ridden into



The Legends



— a rugged classroom built around two top gunslingers from Clief Notes who deliver real systems, not hype.



This is your trail map. Each legend has their own dedicated folder packed with their signature builds, frameworks, and battle-tested wisdom.



Start wherever the dust is thickest for you, then ride across all three.



------



Bas Rosario – The Wise Architect’s Library

#### Folder Purpose:

Deep understanding and human-AI collaboration so you stay in control.

#### What you’ll find inside:

Clear frameworks for AI architecture and communication theory



Systems thinking without the jargon



Responsible AI practices and human-centric prompting



Resources from Praxis Library (glossaries, tools, principles)



Guidance on teaching the machine while remaining the author

#### Ride with Bas if you want to:

Build true literacy, design thoughtful systems, and create work that feels human.



------



Don Roy – The Master Builder

#### Folder Purpose:

No-nonsense automation, quality control, and shipping fast without slop.

#### What you’ll find inside:

No-code + AI agent workflows that deliver



Content creation systems and repeatable processes



Animation & video builds (Remotion + AI)



Anti-slop techniques and quality standards



Daily building experiments and automation recipes

#### Ride with Don if you want to:

Turn ideas into working tools quickly and keep everything durable.



------



Quick Rules of the Trail



Begin with the legend whose trail matches your current challenge.



These folders contain systems built in the real world — experiment and adapt them.



Engage in the comments. The legends (and the posse) reply.



Build in public and share your results.



------



Your move, partner.



Pick a folder.



Start forging.



Welcome aboard. Now go make something that lasts. 🤠



------



THE LEGENDS\Sunday Coffee ☕️.md



------



I thought we were here for AI, Don"



There's a special moment for me every week where I wake up and brew a fresh cup of coffee on Sunday morning. Sunday is used interchageably as the begging or end of the week and therefore acts as a great point of reflection for the week past and the weekend ahead.



This is what inspired this series of posts for me. Every week, a new forum to discuss what you're working on and network with others.

#### You'll see the same prompt every week:

What you’re working on



Something you hope to ship



Blockers you’re running into at the moment



Where you’re looking for help currently



Anything else you’d like to share



I will also typically throw in a poll of something that's on my mind to get conversation going. Comment on the question or anything above. Write about anything at all you want to engage others on. The point is to encourage free form discussion like we all showed up at the coffee shop for a morning. Go hop in the discussion at the post below.



------



THE LEGENDS\Vlog (Video Feed) 📺.md



If you've seen me out in the community, you've seen I regularly create content about things I observe or am learning over at



https://www.youtube.com/@Donsbookshelf



https://www.youtube.com/@Donsbookshelf



. Below is a running log of recent posts of anything catches your eye 👀



------



Are PowerPoint Presentations Dead?](https://www.youtube.com/watch?v=SuV8M6SsGCA)



Fable, Kimi? It doesn't matter](https://youtube.com/shorts/A0DKqevP6TI?si=6C\_n8Gd\_PAJeB9fC)



Responding to bad AI advertisement](https://youtube.com/shorts/1MsY9ODLF6Y?si=p2nnMI0sglW6Hzvs)



Will knowledge be worth zero?](https://youtube.com/shorts/UwSLNr\_8ze8?si=hPGJq2L4zrRT\_fmO)



How AI is like golf](https://youtube.com/shorts/rMc5VF1kiMg?si=PZM9950WRgqniVEz)



Why I don't like agent memory](https://youtube.com/shorts/P3NCaeaLvO8?si=3oScLhlkUkgFBvDY)



Why I don't get AI slop](https://www.youtube.com/shorts/UJj0DPrpPLk)



Why I'm not worried about AI](https://www.youtube.com/shorts/Pcn3OGlExvI)



Most don't know what Claude is](https://youtube.com/shorts/9bRP-G\_\_qyE?si=6z81AH68ECCogsRJ)



------



THE LEGENDS\WELCOME TO THE WISE ARCHITECTS CORNER.md



Welcome to the Wise Architects corner of the Clief Notes community



First, if we have not met yet, my name is Bas 😊 and I want to welcome you to this classroom.



I am one of the members, and a moderator of the Clief Notes community, and this classroom is my corner of it. The panel outside the door says it best, decoding the mysteries of AI use while forging impactful human-AI interactions that endure, and that is exactly what we are going to do in here, together, one series at a time.



------



I want to be upfront with you about how this classroom works, because it runs on a structure, and that is on purpose. Structure is not the enemy of learning, structure is the thing that makes learning stick, and every series in this classroom follows the same rhythm, the same way, every time. (In my day job, I lead high performing teams in the Information Technology space, and I lead them with a promise that I will always shine a light on where we are standing, so we always have the clearest vision of where we are going, in this classroom, I make the same promise to you. You will never wonder where you are or what comes next, and that is a promise)

#### Here is the rhythm this classroom follows:

Three classes.



My series are three solid, connected classes. Each class builds on the one before it, one focused idea at a time.



The payoff.



Every series ends with a payoff, the class where the three ideas click together and you see the whole picture you have been building toward.



The quick card.



A short sheet that summarizes the most important parts to remember and implement, yours to keep, so you never have to scroll back through a whole series to find the one thing you needed.



My perspective.



A final thought where I hand you my understanding of the content in plain language, how I see it, why it matters, and what I would do with it starting today.



------



You do not need a technical background to sit in this classroom, you do not need to be a programmer, and you do not need to have everything figured out before you start. You bring the curiosity, I bring the blueprints, and we build the understanding together.



One last thing before your first class, and it is the most important thing I will say in this whole welcome post. My job here is not to hand you answers. My job is to help you build the understanding that makes the answers YOURS.



Start with class one, and I will see you inside.



👷‍♂️ Coming Soon 🚧



We learn together, we grow together, we win together! 🤓💪🏆



------



THE LEGENDS\Welcome! 🤝.md



------



Hey everyone! My name is Don. Whether you have seen me around here or not, the first thing you should know is that I am here to learn with all of you. I may be two steps ahead of you, 10 steps ahead of you, or 20 steps behind you. So I have just as much to learn from you as you could from me. Every day I learn more from this community than I could ever possibly put back into it.



I am a mechanical engineer by degree and trade. I currently work in that field and everything I do here is on the side for my own education and fun. This means I don't have as many tokens as a lot of you. I have no coding experience like a lot of you. I know enough to be dangerous, but more importantly enough to build and that's what we’re here for.



------



What You'll Find Inside



The simplest way to put it is you'll see my journey. I am exploring this space every day and I try to share what I learn through things like:



Short videos 📺



Random thoughts 💭



Example builds 🔨



Deep dives 🔍



Short essays ✍️



And much more. Anywhere I find value I can share. 📚



I hope what I find provides value or interest to some of the community. As I grow, I expect this space will too. If there's anything you want to see please always feel free to ask. My favorite builds are the ones that help folks here the most. If you want to see what I'm about, I've listed some of the content I've been sharing here since I joined down below. See you out there!



------



Browse the folder off to the left or enter one of my main hubs in the links below!



Back to Basics](https://www.skool.com/cliefnotes/classroom/b5143824?md=e95b3194dd06470fa01509821152ec20)



Sunday Coffee](https://www.skool.com/cliefnotes/classroom/b5143824?md=10850ac26fcd44d692dde9e210866389)



Resources](https://www.skool.com/cliefnotes/classroom/b5143824?md=891eeb180017483bb0ea808eb95b80c0)



LinkedIn Community](https://www.skool.com/cliefnotes/classroom/b5143824?md=e9663770a5574d58a5e0d65b00d71cfb)



Vlog](https://www.skool.com/cliefnotes/classroom/b5143824?md=bf49f8ce6ff04be3bc5f69e38765ea69)



------



THE LEGENDS\🖋️ Don't Let Being New Stop You.md



Build It Anyway: How I Shipped an Agent a Few Weeks In 🤷



Let me take you back to when I was only a few weeks into learning all of this. I was still figuring out what these tools could even do, and a weekly build competition came around. I felt completely unqualified to enter. I entered anyway.



I'm telling you this story now because I think it changes what you believe is possible when you're new. If you've been talking yourself out of these contests because you don't feel ready, stick with me.



------



The "I don't know what I'm doing" prompt has power 🧠



The thing I didn't understand back then, and fully believe now, is how far you can push through something you don't know how to do with these tools. You can brute-force a shocking amount.



All the specialized workflows and clever prompt tricks are nice. I'm not knocking any of it. But being honest with the model, literally telling it "I don't know what I'm doing here," is its own kind of technique. You hand it your confusion and let it help you climb out. A few weeks in, that was pretty much my entire method.



So that's how I walked in. Unsure, and willing to admit it.



------



Step one was figuring out what to even build 🤔



I didn't have a system yet. I downloaded the brief for that week, copied the post text into a fresh Claude project, and that was my setup. No template. No framework. Nothing to hide behind.



My first message was basically a question: "Based on the brief and the competition rules, how do you read the shape of the deliverable?"



Then I argued with it. I challenged its interpretation, it challenged mine, and we went back and forth for a while. Looking back, that argument was the most valuable part of the whole build. Most people grab the brief and start building the obvious thing. I spent my first stretch just trying to understand what the deliverable actually wanted to be.



------



The real problem was the messy middle 🔥



We eventually landed somewhere good. The heart of that brief was the handoff between agents. How that one mechanism worked would define the entire operation for Diana, the assistant I was building for a real estate agency.



The default template didn't sit right with me. Buying and selling a house is not a tidy one-two-three-four. People are messy. Offers get rewritten. Showings get cancelled. Someone falls in love with a completely different neighborhood halfway through the search. Whatever I built had to bend around all of that instead of breaking on it.



So that became my focus. Not the shiny surface stuff. The awkward handoff in the middle, because that's exactly where a real customer would feel the cracks.



------



I barely used any tools 🛠️



I keep saying you don't need fancy workflows, and I want to prove I meant it. The one thing I leaned on was a simple 3-step prompt tool I'd picked up, the same one I've shared here before:



https://www.skool.com/cliefnotes/a-prompting-tool-for-us-newbies



https://www.skool.com/cliefnotes/a-prompting-tool-for-us-newbies?utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03



That was the extent of my toolkit. A basic prompt structure and the patience to argue with the model until the plan got clear. By the end of that phase I had everything written into a single markdown file, a plan that laid out exactly what we were going to build.



------



Then I handed over the plan and let it rip 🏁



This is the part that still gets people. I opened a brand new session, dropped in that one markdown file, and turned it loose.



Claude built the folders. The identity files. The whole skeleton. From a plan and a blank session, a working shape of the product showed up in front of me.



I don't want to oversell it, because this wasn't the finish line. It was a fast first draft. The plan carried all the context forward, so the new session never needed to sit through the arguing I'd already done. It just needed to know what to make.



------



The slow part is the part that counts 🐌



Once the build existed, I went through every single file by hand. I read the logic. I hunted for gaps in the workflow, the exact spots where a messy human would snap the flow I'd designed.



When I found a hole, I didn't patch it myself. I described it to Claude, let it write the fix, then checked the fix. Build, read, patch, repeat. That quiet loop is what turned a rough draft into something I'd actually put my name on.



That's the real work. Letting it rip is the fun, fast part. Reading every line is slower and honestly kind of boring, and it's the reason the whole thing held together.



------



What I walked away with ✅



What I ended up with, only a few weeks into learning this, was something I genuinely believe could ship to a customer.



You download the repo, run the install, and open a new desktop icon. That drops you straight into a Claude terminal living inside the workspace. From there you just talk to Claude and get what you need to help clients buy and sell their homes.



I'm keeping the function light on purpose, because the function was never the lesson. How it got built is.



------



Your turn 🚀



That's the reason I wrote all of this out. You can do exactly what I did.



Copy the brief into a project. Argue about the deliverable until it's clear. Find the messy problem actually worth solving. Get the plan into one file. Let a fresh session build it. Then read every line and patch the gaps. Do that, and I believe you'll land within about 90% of where I did.



The whole spirit of my submission was that building can be as simple as bringing Claude what you want, and that's exactly how I did it. A few weeks in, feeling unqualified the entire time.



You don't need to be ready. You just need to start. Go build yours. 🛠️



------



See the build and my original thoughts during the build below. Leave a comment on the companion post to share your thoughts. 👇



Diana Agency Assistant](https://github.com/donroy26/Diana-Agency-Assistant)



------



Uncategorized\A Living ICM System Folder-Structure-as-Interface.md



This is a summary of the system that I've been working on since joining Clief Notes. This has been made by drawing off of a lot of different posts, weekly competitions, David's Corner, and the work @Ari Evergreen has shared with the community. This post specifically was made to address a question that has been pretty common with a lot of members: How a folder of plain text files becomes an operating system for AI work?



The whole philosophy in one line: This is not automation — it's orchestration through structure. The folders are the framework; the files are the code; a human reads and audits all of it.

#### What this is (plain-language version):

Most people drive AI with one giant prompt: they dump everything they know into a chat box and hope. That breaks down the moment a task has more than one step, because the AI has no map — it improvises, forgets, and contradicts itself.



This is a live implementation of ICM — Interpretable Context Methodology — the principle that structured files delivered at the right moment replace a framework telling the AI what to do. Instead of one giant prompt, the workflow lives in a folder of plain text files, and the folder structure itself is the interface. The way the folders are laid out tells the AI what to do, in what order, and where the boundaries are. There's no app, no code required, no cloud account. An AI agent walks into the folder, reads a small "you are here" file, and the structure routes it to exactly the right instructions at the right moment.



Everything below is ICM in practice. The toolkit isn't a new theory — it's what ICM looks like when you actually build it and run it every day.



One sentence: Structured files at the right moment replace a framework telling the AI what to do.



The payoff: instead of loading 30,000–50,000 words of context for every task, the AI loads only the 2,000–8,000 words relevant to the current step. It's faster, cheaper, more consistent, and — crucially — a human can read the whole system and audit it, because the files are the documentation.



The one rule that governs everything: 60 / 30 / 10

#### Before any task, ask three questions in order:

Is the answer deterministic? (a calculation, a lookup, a file operation) → write a script. Stop. Don't involve AI.



Can it be written as an if/this-then/that rule? (sorting, routing, categorizing) → a small automation or script. Stop.



Does it genuinely need judgment across messy information? (synthesis, writing, analysis, design) → now use AI.



The name "60/30/10" is the effort budget for any system you build — the rough share of the work each layer should own:



60% — Deterministic (scripts, data, established tools). Anything with one right answer that can be calculated, looked up, or formatted to spec: scripts, database/SQL queries, spreadsheet formulas, file operations, APIs with predictable responses. This is the stable foundation — reliable, fast, auditable, cheap to run. It doesn't drift, hallucinate, or cost tokens. A VLOOKUP does not hallucinate.



30% — Rule-based routing & layering (AI navigates, scripts execute). The "which path do we take" decisions that have clear criteria: if/then routing, branching, known-category classification, template selection, threshold checks. The AI may decide which route applies, but a script or automation does the deterministic step. This is the orchestration band — predictable, still drift-free, and the layer that decides which of the 60% gets called.



10% — AI judgment (logic, synthesis, analysis). The slice that genuinely can't be reduced to a rule: writing, analysis of unstructured text, fuzzy categorization, creative work, noticing the pattern in messy data. This is the only place a language model earns its cost.



The deeper truth: the real divide is 90 vs 10, not 60 vs 30. Infrastructure (60%) and orchestration (30%) are both deterministic work — they differ in complexity, not in kind. So when something breaks, the operative question is simply: did something that belongs in the 90% end up running on the 10%? It almost always did.



The endstate — AI as director, not middle management. Once the right scripts exist, the AI's 10% collapses to one job: selecting and calling the deterministic 90% correctly. Judgment in routing, not in doing. A smart director calling solid scripts beats a bloated orchestration layer that hard-codes every path. And it ages well: the 10% (prompts, model choices) decays as models change; the 90% (folder structure, pipelines, routing conventions) survives every tool swap. Patterns last. Tools don't.



The trap this prevents: routing a math problem or a file rename through an AI. It's slow, expensive, and gives a slightly different answer each run. Scripts automate. AI reasons. Never make them compete.

#### The mental model: five context layers:

This is ICM's core model — the toolkit is built directly on top of it. Everything in the system is one of five "layers." Think of it as a factory and its products.



Layer 0 — Identity: "Who is this project, what agents exist, where do I start?" Lifespan: permanent. Size: ~1 page.



Layer 1 — Directory / Router: A signpost. No content, only "for X go here, for Y go there." Lifespan: permanent. Size: short.



Layer 2 — Stage contract: One step's rules — what to load, what to do, what to produce. Lifespan: per step. Size: short.



Layer 3 — Reference: Stable knowledge — standards, templates, domain facts. Set once, reused. Lifespan: stable. Size: load only what's needed.



Layer 4 — Output: The artifacts a step produces. A human reviews these before the next step runs. Lifespan: per run. Size: varies.



Layer 3 is the factory. Layer 4 is the product. Knowledge stays stable and gets reused; output is fresh each run and always gets a human's eyes before the workflow advances.

#### How the system is organized (the six functional layers):

At the top level the toolkit is split by function, not by topic. Each folder has its own small router file.



├── README / map ← the system map; always read first



├── constraints/ ← Problem-solving protocols. Short, standalone rules



│ you load one or two of when a specific failure shows up



│ (e.g. "AI output sounds generic," "agent wandered out of scope").



├── skills/ ← Reusable techniques, model-agnostic. Each is a self-contained



│ folder (e.g. "audit X," "delegate heavy coding," "fix generic prose").



│ Flat namespace — pick one off the shelf.



├── workflows/ ← Active multi-step pipelines. Numbered stages that run in order.



│ This is where real multi-step work executes.



├── knowledge/ ← The persistent reference layer. Naming rules, methodology docs,



│ templates. Everything points here; it never points back out.



│ ├── _config/ ← global settings shared by every stage (the system's /etc)



│ ├── references/ ← the methodology, guides, patterns



│ └── templates/ ← reusable blank forms



├── scaffold/ ← Starters + builders for spinning up a brand-new project,



│ plus read-only "teaching" examples.



└── runtime/ ← The front door at run time: a boundary gate, a small memory



service, and the deterministic scripts (lint, scaffold, migrate).



The placement law: subject first, type second. A document about a particular skill lives inside that skill's folder — not in a generic "all plans" bucket. Type-buckets are a last resort for things that genuinely belong to no single subject. This is what keeps the system navigable as it grows.

#### The four routing documents (the "living" part):

This is ICM's filescope principle, customized into the toolkit's daily driver. Three or four tiny files do all the steering. These are what make it a living agent reference rather than a static doc — an agent re-reads them every session, so updating a file instantly changes how every future agent behaves.



Identity file (Layer 0): Who this folder is. Identity only — if it's getting long, content is hiding that belongs in a subfolder. Limit: ~50 lines.



Router file (Layer 1): Pointers only. "For this task → that file." No actual content. Limit: ~80 lines.



Values / Rules file: The non-negotiables and the why behind them. The system's conscience. Limit: short.



State file: Current session status — what's in progress, what's next. Kept separate from identity so it can change every session without churning the permanent files. Limit: short.



Filescope (the recursive principle): every router/identity file describes only its own folder. A subfolder's detail lives in the subfolder's own file, never copied up into the parent. So an agent entering the "monitoring" subfolder loads 30 lines of monitoring rules — not 400 lines of everything in the project. This is the single trick that keeps each step small and cheap.

#### How a workflow actually runs: the Unix-pipe principle:

A workflow is numbered stages that hand off through a single channel.



01-research/output/ → read by 02-draft



02-draft/output/ → read by 03-review



03-review/output/ → delivered

#### Three iron rules:

The handoff channel is output/, nothing else. Stage 2 reads stage 1's output/ folder — never stage 1's scratch/working files.



Adjacent only. Stage 3 reads stage 2, never stage 1. If stage 3 needs something from stage 1, stage 2 must copy it forward into its own output. ("Embed, don't reach.")



Config is always available. The global _config/ (voice rules, standards) is like system settings — any stage may read it without "breaking the chain."



Because each stage only cares about the shape of the output it receives, you can rewrite stage 1 entirely without touching stage 2. Stages are independently testable and swappable, exactly like Unix pipes (cmd1 | cmd2 | cmd3).



Each stage is defined by a stage contract — just three sections: Inputs (what to load and why), Process (ordered steps), Outputs (what to write, where). That's it. Same contract shape regardless of subject, tool, or AI.



Design tip: write each stage's output to be interrogated later, not just consumed once. A well-structured output can be pulled into a fresh session weeks later and questioned ("show me where the earlier step flagged X"). A raw dump can't.

#### How to build a specialist (a single expert agent):

A "specialist" is a folder that turns an AI into one focused expert. The discipline is a five-file pattern:



identity — Holds a philosophy, not a persona. Named principles with a defensible reason to exist. The test: "I catch what the writer missed, because writers can't review their own work" (philosophy) — not "I'm a helpful reviewer" (persona).



rules — Behavioral constraints only: how it responds, what it never does, how it self-corrects. The test: every rule must be falsifiable — a judge could read one output and mark it pass/fail. "Be thorough" fails this test; "every finding must state where, how to reproduce, and why — or be discarded" passes.



reference — The protocols, schemas, templates, ordered question-lists. The test: if a section describes a sequence or a schema rather than a behavior, it belongs here, not in rules.



workflow — The resumability layer: a Pick-Up state (how to resume mid-task) and a Drop state (done-when criteria + where to route next). The test: a new session can inherit a half-finished job and continue.



examples — Matched do / don't pairs of real input → output, each annotated with why. (See below — this is the highest-leverage file in the folder.)

#### Two more rules that separate good specialists from generic ones:

Scope lists earn trust through specificity. "I don't do SEO" is vague. "I don't do semicolons — get a linter" is opinionated enough to be believed. The more concrete the exclusion, the more credible the inclusions.



Define the clean-pass output explicitly. A specialist with no defined "nothing wrong here" result will invent noise to look useful. Give it a contractual silence: PASS — 0 issues, STRONG — 92/100, No changes recommended.

#### Why examples carry the most weight:

Of the five files, examples is the one most people underbuild and the one that moves quality the most. Here's why, and how to build it well.

#### Why it works:

Examples encode the tacit knowledge that rules can't. A rule can say "be specific," but it cannot fully transmit what specific looks like in this domain. One concrete good-output makes the standard legible in a way ten adjectives never will. The rule names the target; the example is the target.



Models pattern-match harder off examples than off instructions. When an AI sees a worked input→output pair, it anchors to the shape, depth, and tone of that output. A single strong example pins down a whole class of decisions that would otherwise drift run-to-run — formatting, length, how much to push back, when to stop.



The "don't" half is where the boundary actually lives. A good-only example shows the destination but not the edge. A bad example — especially a near-miss that looks plausible but fails — teaches the line between acceptable and not. Most specialist failures are subtle (technically-correct-but-useless output), and only a contrastive pair makes that line visible.



Annotated pairs turn examples into a rubric. When each example says why it's good or bad, the specialist isn't just imitating a sample — it's internalizing the criterion. That's what lets it generalize to inputs you never showed it.

#### How to build it well:

Use matched do/don't pairs, not isolated samples. Same input, two outputs: one that passes, one that fails. The contrast is the lesson.



Annotate every example with the reason. One line under each: "Good — names the exact location and a reproduction step." / "Bad — flags a 'concern' with no evidence; this is the noise the clean-pass rule exists to kill."



Mine the near-misses, not the obvious failures. A bad example that's wildly wrong teaches nothing. The valuable "don't" is the one that looks right at a glance and fails on inspection — that's the mistake the specialist will actually be tempted to make.



Include the clean-pass case. Show one example where the correct output is "nothing to report." This is what stops a specialist from manufacturing problems to seem useful.



Cover the edge, not just the center. One ambiguous or adversarial input → the correct handling. Examples that only show easy cases leave the hard ones to improvisation.



Rule of thumb: if rules is the law, examples is the case law. Rules state the principle; examples show how it's been applied — and applied wrongly. Agents, like junior hires, learn the job faster from worked cases than from the statute.

#### How to build a multi-agent system (several specialists working together):

When one expert isn't enough, you connect specialists through an orchestrator and a shared contract.



your-system/



├── manifest.yaml ← the contract: the exact data shape every handoff must use



├── AGENTS.md ← entry point + "how to activate" guide



├── 0-orchestrator/ ← routes work; never does the work itself



├── 1-specialist-a/



└── 2-specialist-b/



The orchestrator routes, it never answers. It identifies intent, packages the request (always including the user's original words verbatim), and sends it to the right specialist. If unsure, it asks one clarifying question.



manifest.yaml is the single source of truth for data shape. Every specialist's handoff references it. Golden rule: never change a handoff format without updating the manifest first — that's the #1 cause of silent breakage ("schema drift").

#### Two orchestrator styles:

Relay (lead → research → offer → close): work flows stage to stage.



Assess-and-decide (score one thing across several dimensions, then rule on it): the orchestrator needs a binding decision table (e.g. SHIP / FIX / ESCALATE), evidence-over-memory discipline, and an adversarial "try to break this" gate before it commits. It returns a decision, never a question.



Because it's all files, a brand-new agent can be operational in ~30 minutes by reading four files. The filesystem is the language; the files are the code.

#### How to keep it alive (updating without rotting):

#### A "living agent reference" stays useful only with maintenance discipline:

Routers stay routers. The moment a router file starts containing content instead of pointers, that's the signal to break out a subfolder with its own router.



Identity stays under a page. If it's growing, content is leaking in from a subfolder — move it down.



State is separate from identity. Update state every session; never touch identity to record "what I did today."



Length limits as smoke alarms: routers < ~80 lines, reference files < ~200 lines (split if longer), identity < ~50 lines. When a file blows its limit, that's a structural problem to fix, not a number to ignore.



Match constraints to symptoms, don't load the library. Each workspace's router lists only the one or two protocols likely to bite there — not all of them. Context overload defeats the whole purpose.

#### The discipline (the unbreakable rules):

These are the cultural rules that make the whole thing work. Generalize them to any team:



Navigate before reasoning. If a map/router file exists, read it first. Using AI to reconstruct what a file already states is pure waste.



Scripts automate, AI reasons. Honor the 60/30/10 split. Never route deterministic work through AI; never let a script make judgment calls.



Stay in scope. An agent works only in the folder it was pointed at. Wandering into sibling folders is a boundary failure, not initiative.



Stop and surface failures. When something fails, stop and report it. Don't silently retry — that hides the real problem and burns budget. A human picks the next move.



Complete answers, held under pressure. Give the full answer the first time; don't reverse a correct answer just because you were pushed, unless there's genuinely new evidence.



Human review gate between stages. Nothing advances until a person approves what landed in output/. This is what makes the workflow interruptible and auditable.



Brief before prompt. Define the outcome and the failure criteria before opening the AI. A thin brief earns generic output — correctly.



Quickstart: scaffold this into your subject



Hand an AI this whole document plus the steps below, and it can build the same ICM system for any domain — cooking, legal intake, research, a game, customer support, anything.



Pick the subject and name the end-to-end job.



("Take a raw customer email and produce a triaged, routed response.")



Find the natural stages already implicit in that job, in order.



Most workflows already have stages — you're just naming them.



→ 01-intake / 02-classify / 03-draft / 04-review



For each stage, write a one-page CONTRACT: Inputs · Process · Outputs.



Output of stage N is the ONLY thing stage N+1 reads.



Pull the stable stuff (standards, voice, templates, domain facts)



out of the stages into a shared reference/ + _config/ layer.

#### At the root, write three tiny files:

identity (who this project is — under a page)



router (pointers only — "for X go to stage 0Y")



rules (the non-negotiables + why)

#### If a stage needs a focused expert, build it as a specialist:

identity (philosophy) · rules (testable behavior) ·



reference (protocols/schemas) · workflow (pick-up/drop) ·



examples (annotated do/don't pairs — build this one hardest).



If multiple experts must coordinate, add a 0-orchestrator that



ROUTES (never answers) and a manifest defining the handoff shape.



Update the manifest BEFORE any handoff format ever changes.

#### Before automating anything, run the 60/30/10 test:

deterministic → script; rule-based → automation; judgment → AI.



Limits to hold: identity < 50 lines · routers < 80 lines ·



reference < 200 lines · each step's context 2,000–8,000 "words."



Every step ends in an output/ folder a human checks before advancing.



------



Uncategorized\Community Call ICM, AI Workflows, and Future Tools.md



Community Call: ICM, AI Workflows, and Future Tools



Introductions & Participants



Jacob – SEO & small business automations; looking to hire



Marcelo – Psychotherapist turned tech; building event management tools and ICM workspace creator



Joe Quinn – Software dev agency owner from Uruguay, using ICM to structure AI projects



Boss – IT manager (60+ hrs/week), automates in “in-between” time, emphasizes failure & iteration



Sandra – Real estate developer & marketing agency owner; stuck implementing ICM perfectly



Meera – Data leader at large NZ food company, dealing with logistics, compliance, and growth



ICM Methodology (Information Context Management)



Core Idea: Organise thoughts, files, and context so AI can navigate and collaborate



Routing with Markdown Files



describes folder structure and purpose



AI immediately knows where to find relevant info (e.g., property A, video production)



Acts like a “PHP layer” between backend (your data) and frontend (AI interaction)



Productionising Your Opinion



Embed your unique processes, naming conventions, and decisions into files



AI amplifies your way of working, not just generic automation



Workspace Creator (Marcelo’s ICM-style folder generator)



Simplicity Over Complexity



Avoid overbuilding software when a structured folder + AI gets the same result



“Could have been a Zapier solution” mindset



AI Workflow & Automation Insights



Delegation Questions: Should you build it yourself, hire, or license?



Human Compute Efficiency



Sometimes a $40k/year intern is cheaper and better than complex API automations



60/30/10 Rule: 90% traditional processes, 10% AI magic on top



Focus on Collaboration, Not Just Single‑Task Automation



AI as Runtime – the AI becomes the environment that runs your workflows



Danger of Hollow Output – polished text without substance (lack of context/opinion)



Importance of Failing & Iterating Quickly



London Tech Week Takeaways



Investment & Focus Areas



Data infrastructure and structure (how AI sees data)



Physical chips (AMD, NVIDIA) for local large model running



AI‑to‑AI Commerce – agents paying for services/data (e.g., access to transcripts)



Overengineering Epidemic – many startups building complex “agentic” solutions that a folder + 2 people could replace



Talent Layer Opportunity – growing need for people who understand structured AI workflows



Upcoming Tools & Projects (Host)



Employment / Freelance Portal (Ledger)



Candidates upload ICM portfolios; companies hire top talent



Free for VIP/premium members



Monetisation via placement fees (recruiting industry model)



ICM Deployment Layer



Docker‑like environment: upload a zip, deploy workflow instantly



No local setup needed; workspaces accessible via cloud



Future: license your workflows to other companies (monetise your “virtual self”)



Both launching soon (targeting this week)



Skill Optimization (SkillOpt Paper – Microsoft)



Automates improvement of markdown “skill” files using LLM + ML



Vectorises markdown content



Tests skills hundreds of times, judges output, edits file



Achieves 20‑57% performance gains without fine‑tuning the whole model



Most optimised skills end up <500‑800 tokens – supports ICM’s “break apart” philosophy



Host working on open‑source hybrid version (combining SkillOpt + Karpathy’s AutoResearch)



Community & Collaboration



VIP Discord – connect, ask questions, find collaborators



Recordings + Downloadable Artifacts



Transcripts, slide decks, summarised markdown files



Designed to be fed into your own AI/second brain



Value of knowing everyone in the room “gets it” – skip the AI education preamble



------



Uncategorized\Stop Babysitting Your Agents.md



Stop Babysitting Your Agents (Cloud Code 301)



Prerequisites (Table Stakes)



High‑quality



file (highest leverage)



Connect tools (Slack, Asana, Linear, Datadog, BigQuery, …)



Remote environment on Cloud Code Web (decouple compute from laptop)



Why Tooling Must Change



Most tools built for humans, but agents now write most code



Good news: prettier, linters, type‑checkers work well for agents too



Bad news: humans have blind‑spot assumptions agents don’t share



Key question: “What does an agent need from your codebase that a human takes for granted?”



Verification → Multi‑Clauding → Background Loops



Stack them together → work autonomously without you at the keyboard



Verification – Teaching Claude to Check Its Own Work



Human verification loop (same pattern works for agents)



Design/write code → build/compile → run executable → check side effects (UI, logs, DB) → run unit tests → deploy to staging



Autonomous Loop for Claude

#### Give Claude tools + instructions to iterate:

Run/build it



Verify result (browser, logs, DB, tests)



If failure → debug → write more code → repeat until success



Example: fix sign‑up button – it ran dev server, opened browser, clicked, saw nothing, read logs, fixed code, reloaded, repeated until working PR



Flavours of Verification



Front‑end (UX)



End‑to‑end (incl. infra)



Core concept same: provide tools so Claude can loop



Concrete Front‑end Loop Setup



Run dev server (



npm run start



Give browser control (Chrome MCP, Playwright, etc.)



Prove behaviour (before/after screenshots)

#### Unblock common obstacles:

Auth (give Claude an identity to log in)



State (pre‑configure app state dynamically, like test fixtures)



Packaging: Self‑Improving Skills



Store verification instructions in a skill file



Include rule: “document every blocker you hit and update this skill”



Becomes self‑documenting, distributable to whole team



Demo: created a verification skill for MonkeyType app, then used it to build a new feature (confetti on mistype) – Claude auto‑fixed lint errors inside the loop



Multi‑Clauding – Managing Many Agents at Once



Problem: more than 4‑5 sessions overwhelm attention



Cloud Code Desktop App



Sidebar showing all sessions (local, cloud, across repos)



Pin, rename, colour‑code → protect attention



Cloud Agents (Terminal)



cloud agents



command → list of local sessions sorted by urgency



Pin, rename, reorder



Cloud Code on the Web



Sessions run on remote containers – close laptop, keep working



Remote Control (Phone)



/remote-control



→ session appears in mobile app



Push notifications when input needed – respond from anywhere



Background Loops – Remove Yourself from the Loop



Recurring tasks that don’t need you



Babysitting PRs (review comments, merge conflicts, CI failures)



Updating documentation



Triaging issues / monitoring feedback



Keeping CI green



Run a prompt on a fixed interval (e.g.



/loop 10 minutes: babysit my open PRs



Session wakes up, runs prompt, acts using tools + skills



Routines (Remote Background Loops)



but running in Cloud Code on the Web



Triggers: time‑based (every morning) or event‑based (new issue)



Examples: update docs daily, post feedback to Slack every 6 hours



Verification makes Claude reliable



Multi‑Clauding scales your capacity



Background loops remove you from the hot path



→ You focus only on what truly needs your attention



------



Uncategorized\Version control for the AI age.md



Git assumes a person sits down, makes a deliberate change, and writes a commit message. That world is fading. Today an AI agent might touch fifty files while you watch, or while you don't, and the question that matters isn't "what did I commit?" It's "what just happened, who did it, and how do I undo it?"



GiTeam is version control rebuilt for that question.



Why I'm building this



I built my own IDE, TeamIDE, and then spent half my time fighting the git workflow under it. Running several projects at once with AI agents in the loop, the cracks showed: worktrees are clumsy, submodules are a nightmare, and a model that's brilliant for a solo developer becomes a hindrance the moment AI joins in. I'm comfortable at the systems level, so instead of wrestling git into a shape it resists, I built what I actually needed.



What it does



Auto-history. Every save is recorded automatically, the moment a file hits disk: an append-only stream of snapshots from every human and every agent. Always on, through a background service. No staging, no remembering to commit.



Real commits, when you want them. Deliberate, git-compatible checkpoints sit over that stream as bookmarks, and they push to GitHub like any other history.



Nothing is ever lost. The history is append-only and never rewritten. Undo isn't a destructive pop off a stack, it's moving along a timeline. Edit from a past point and it automatically forks into a tree, not a line.



Every change has an author. Human or agent, stamped on every snapshot. Turn an agent loose and you get a flight recorder: attributed, reversible, complete. The undo button for autonomous work.



A cockpit to work in. A full-screen app where your agent runs in a pane beside your file tree, your editor, and a live, scrubbable history. Watch it edit, see each change attributed, scrub back and fork when it goes wrong.



Embeddable anywhere. The core is a small, zero-dependency engine, so it doesn't have to live in a terminal. Picture an Obsidian plugin that versions your vault with attribution and time travel, and the same for Logseq, VS Code, or Zed.



Where it's headed, and how to get in



Today GiTeam is a repo-level safety net for AI: everything that happens to your code, recorded, attributed, reversible. The longer plan reaches past a single repo, toward a safety net for your whole machine, repos you can mount like drives, and that engine living inside the tools you already use.



It's an internal tool right now, and we dogfood it daily, bugs and all. If this resonates and you'd want to kick the tires, we'd like to talk about alpha testing.



That's GiTeam.



------



Uncategorized\Vibe-Coding Masterclass in 30 Minutes Flat.md



Introduction



Speaker: Boris, Member of Technical Staff at Anthropic



Creator of "Quad Code" (Claude Code)



Focus: practical tips and tricks



What is Quad Code?



New kind of AI assistant for coding



Agentic: builds features, entire functions, files, fixes bugs



Works with all IDEs & environments: VS Code, Xcode, JetBrains, Vim, terminal, SSH, tmux



No indexing, code stays local



Getting Started



Environment setup



Terminal setup: shift+enter for new lines



Theme: light/dark/daltonize

#### GitHub app:

/install github app



Customize allowed tools to reduce prompts



Dictation (Mac accessibility): speak prompts



Recommended first use: Codebase Q&A



Ask questions about the codebase



Onboarding: reduced from 2–3 weeks to 2–3 days



"How is this class used?" (finds deep examples)



"Explain git history of this function/arguments" (summarizes commits, issues)



Fetch GitHub issues via web



"What did I ship this week?" (standup summary)



Editing Code



Tools: edit files, run bash, search files



Agent strings them together automatically



Workflow tips



Plan first: "Before you write code, make a plan"



Ask for approval before writing



"commit push": auto branch, commit, PR



Advanced workflows



Let it check its work (unit tests, screenshots via Puppeteer/iOS simulator)



Iterate 2–3 times → near-perfect results



Integrating Your Tools



Two types: bash tools, MCP tools



Teach Claude: use



, add MCP servers in config



Share tools via project config (e.g., Puppeteer MCP for end-to-end tests)



Providing Context



Project root (shared, checked in): common commands, style guide, architecture, core files – keep short



Local (personal, not checked in)



Nested directories (auto-pulled on demand)



Enterprise route (company-wide)



Slash commands (



): automate tasks (e.g., label GitHub issues)



@mention files to pull into context



Context hierarchy: project → global → enterprise policies



Auto-approve/block commands, manage MCP servers

#### Manage context:

/slashmemory



, pound sign (



) to remember



Key Bindings & Tips



Shift+Tab: auto-accept edits (bash still requires approval)



: remember something into CLAUDE.md



: drop to bash (output in context)



Escape: stop safely; double escape to jump back in history



to resume sessions



Ctrl+R: show full context window output



Claude Code SDK



flag: CLI SDK (prompt, allowed tools, output format JSON/streaming)



Unix utility style: pipe in/out (git status, logs, Sentry, GCP)



Use cases: CI, incident response, pipelines



Running Multiple Sessions (Power Users)



SSH, tmux tunnels into sessions



Multiple checkouts or git worktrees for isolation



Run many sessions in parallel



Q&A Highlights



Hardest implementation part: making bash safe (static analysis, tiered permissions)



Multimodal: drag/drop images, file paths, paste; generate UI from mocks



Why CLI not IDE: universal compatibility, anticipating models making IDEs obsolete



ML/modeling usage: notebook tool, 80% of technical staff daily



------



Uncategorized\Your AI expert council is probably making worse decisions than a single prompt.md



Everyone's stacking AI experts into "councils" right now. Here's what nobody



mentions: most of them produce blander advice than a single good prompt.



I've been building multi-agent systems for a while, and the council pattern is



seductive. Load six marketing legends, let them debate, synthesize the genius.

#### Three things I learned the hard way:

Councils regress to the mean. Put Cialdini, Godin, and Vaynerchuk in a room and



"synthesize" their answers and you get generic marketing advice wearing three



nametags. The fix isn't a better synthesizer. Stop resolving the disagreement.



Let the tension stand and make one agent own the call.



The debate is where your budget dies. Distilling a book into a tight skill file



is cheap. Having agents argue in real time is not. If "minimal tokens" is your



pitch, the preprocessing is doing the work and the roundtable is the luxury.



It doesn't make the model smarter. Cold Claude already does a soft version of



all of this. What the structure buys you is named, sharp, predictable behavior.



Say that honestly — the moment you claim it makes the AI "smarter," you've oversold



None of this means don't build councils. It means build them with your eyes open.



The real test for any council: do your experts actually disagree, or do they just



agree in different vocabulary? If it's the second, you built one expert and gave



it six hats.



(Riffing off the systems thread from @Curtis Hays that @David Vogel highlighted for us and the 'systems' build — good work worth pressure-testing.)



------



Uncategorized\ai_habit__that_saved_most_time.md

#### The core habit:

decompose before you execute



. Break any project into the smallest interpretable units (“atoms”) with clear contracts—inputs, outputs, decision points, handoffs. Wire those atoms into deterministic “molecules” that have one job, one failure mode, and a transparent structure. That skeleton, stored as plain markdown files on your filesystem, becomes a persistent, version-controlled context layer—an “organism” that evolves without drift. Only then do you prompt AI surgically against that skeleton, eliminating the cycle of vibe-coded slop, endless debugging, and overcorrection. The filesystem



the architecture; ownership of the context layer is the leverage. It’s high-discipline upfront but pays compounding ROI in consistency, auditability, and trust.



------



Uncategorized\icm_operational_notes_studio_video-2026-07-23_07-58-00.md



ICM Operational Notes



A practical study summary for understanding folder structure as agent architecture.



Personal notes, not official ICM material. The goal is operational clarity, not memorization.



1. ICM in one sentence



ICM orchestrates sequential AI workflows through the filesystem: numbered folders act as stages, markdown files carry prompts and context, outputs become reviewable handoffs, local scripts handle mechanical work, and one agent reads the right files at the right moment.



1. The five principles



One stage, one job - Each stage takes a defined input, performs one main transformation, and writes a defined output.



Plain text as interface - Markdown and JSON are readable, editable, portable, and versionable.



Layered context loading - The agent loads only the context needed for the current stage. Less noise, more control.



Every output is an edit surface - Each intermediate output is a file the human can read, correct, and approve.



Configure the factory, not the product - Stable rules live in the factory. Each run creates a new product using those rules.



1. The five layers



Mental model: stages are the machine. Layer 3 is the machine rules. Layer 4 is the concrete material that enters, changes, and is produced during each run.



1. Clean workspace     structure



ICM Example: Studio-video Workspace



Hypothetical workspace for turning a technical video into reviewable study notes and a final PDF.



1. Studio-video folder     structure



studio-video/



CLAUDE.md    Layer 0, shared by the whole workspace



CONTEXT.md    Layer 1, shared by the whole workspace



stages/



01_ingest/



CONTEXT.md  Layer 2, contract for stage 01



references/  Layer 3, stable rules specific to stage 01



 ingest-rules.md



output/   Layer 4, concrete run material/output



 transcript\_clean.md



02_synthesis/



CONTEXT.md  Layer 2, contract for stage 02



references/  Layer 3, stable rules specific to stage 02



 synthesis-rules.md



output/   Layer 4, concrete run material/output



 study\_notes.md



03_pdf/



CONTEXT.md  Layer 2, contract for stage 03



references/  Layer 3, stable rules specific to stage 03



 pdf-rules.md



output/   Layer 4, concrete run material/output



 final\_study\_notes.pdf



_config/    Layer 3, global rules



study-format.md



tone.md



pdf-format.md



shared/    Layer 3, shared rules/resources



glossary.md



naming-conventions.md



setup/



questionnaire.md



1. What each stage does



1. Key clarification



The CONTEXT.md of the next stage is not written by the previous stage. It already exists. It tells the agent which previous output to read, which references to use, and which new output to produce.



Layer 4 can be both output and input depending on the point of view: it is stored as the output of the stage that produced it, then read by the next stage as working material.



How the Stages Connect



The pipeline is visible because every handoff is a file in the filesystem.



1. Flow example



Source video / audio / raw transcript



01_ingest produces:



studio-video/stages/01_ingest/output/transcript_clean.md



02_synthesis reads that file and produces:



studio-video/stages/02_synthesis/output/study_notes.md



03_pdf reads that file and produces:



studio-video/stages/03_pdf/output/final_study_notes.pdf



Formula: each stage produces a Layer 4 file in its own output/ folder. The next stage reads that Layer 4 as working material and produces a new Layer 4.



1. Example: what     02_synthesis/CONTEXT.md says



studio-video/stages/01_ingest/output/transcript_clean.md

#### Use these references:

studio-video/_config/study-format.md



studio-video/stages/02_synthesis/references/synthesis-rules.md



studio-video/stages/02_synthesis/output/study_notes.md



1. Stage contract checklist



Inputs - what files or folders the stage reads. Always distinguish Layer 3 reference material from Layer 4 working artifacts.



Process - what the stage must do. Instructions should be concrete, checkable, and limited to one main job.



Outputs - what files the stage produces. Usually written in that stage output/ folder.



Review gate - before the next stage runs, the human reads, corrects, and approves the output.



1. When to use it



1. Golden rule



Correct the output to save the current run. If the same correction repeats, fix the source that caused the issue.



Single issue: edit the file in output/ and save the run.



Repeated issue in the same stage: fix Layer 2 if the issue is in that stage CONTEXT.md; fix Layer 3 if the issue is in a stable rule or reference file.



Improve the factory, not just the product.



------



Uncategorized\links.md



Undestand anything plungin for ai agent



https://understand-anything.com/

#### ICM Architect

\-    a Claude skill that turns a process, an idea, or a messy folder into an ICM workspace



https://github.com/RinDig/icm-architect



📦 What it does



🔨 Build. You describe your work and it pulls out the structure already sitting in how you talk about it. The stages, the points    where you stop and check, what stays the same every run versus what is new. Then it picks one of five proven forms and       scaffolds the smallest workspace that carries the job.



♻️ Restructure. Point it at a folder, repo, or vault you already have. It reads every file, sorts each one by role, shows you a migration map, waits for your yes, then moves and checks the result.



🧩 The five forms



Pipeline, umbrella, record library, knowledge bundle, context map. They mix and nest, so most real workspaces use more   than one.



✅ The walk test



Every result gets checked cold. An agent with no memory has to open the root, find its way, act, and report status from the     files alone. If it can't, the structure gets fixed until it can.



⚙️ How to use it



You can honestly just tell claude to download it from the link, but if you're using codex or something else it will just have to  restructure the claude.md to



http://agents.md/



Or if you want to do more Hands-On install



Claude Code: drop the folder in ~/.claude/skills/icm-architect/, then say "ICM this" or "build me a workspace for X."



Claude apps: zip the folder and upload it under Settings, then Capabilities.



Maya ICM interactive tutorial



https://claude.ai/public/artifacts/7c9618f4-8324-4048-902c-cbcf77c9c102



Article on how to spot ai writing



https://en.wikipedia.org/wiki/Wikipedia:Signs\_of\_AI\_writing



eve framework



https://vercel.com/changelog/introducing-eve-an-open-source-agent-framework



claude cookbook



https://platform.claude.com/cookbook/



------



Uncategorized\logbook.md



Planes keep a black box so that when something goes wrong there is a full recording of what happened and when. Build the same thing into your ICM system: a logbook it writes itself, every job and every journal, that you can hand back to Claude at any point.



The setup is simple. Every Claude Code job writes a short record when it finishes - what it did, how it went, a grade, and any errors. Every design chat writes a journal when it is done drafting your ideas out. Every handover is stored in a set space.



All of the above - ORGANISED



Nothing is thrown away. The record just builds on its own in the background.



Then, any time you have spare usage, point Claude at the whole logbook: pull the bits that ran slow, the bits that failed, and the improvements worth making.

#### Once the logbook exists, here is what it gives you:

Query anything - ask in plain language what happened, when, and why.



Find the mistakes - surface exactly where and when something went wrong.



Improve the whole system - point at the record and tell it to fix the system as a whole



Security audits - every change that was made, timestamped and ready to review.



Client work - hard evidence and the answer already sitting there if a client complains.



Investor conversations - the same record holds up when you are showing what you have built.



Older systems - go back and read what a system used to do long after you have moved on from it.



Across projects - copy edits and systems from one project directly into another with ease



And this is where it goes next. Fairly soon you will be able to hand a model every logbook across every project you run and let it treat the whole thing as training data - not to answer questions about the past, but to learn how you actually operate and carry that forward on its own. The record stops being something you query and becomes the material a system clones itself from: your decisions, your patterns, the way you work, all already written down. That is the real reason to start now. Every entry you log today is training data for the autonomy you hand off tomorrow.



If you have got extra Fable usage right now, this is a strong thing to point it at over the next couple of days, before it turns back into credits. The setup is mostly plumbing - a template each job fills in and a place to put it - and the analysis pass on top gives you genuinely useful output for very little. Build the recorder now while the usage is effectively free, and the black box is ready the first time something breaks.



I have attached below my LOG_PROMPT.md, which I give to Claude Chats, and the CC_TOUCHDOWN.md, which is hard coded as the last step in every Claude Code prompt. Open for feedback as always!



Are you logging what your system actually does, or reconstructing it after the fact when something goes wrong? And anybody currently with a logbook system, how is yours designed and are there any other use cases that you would be willing to share with the community?



------



Uncategorized\loop_eng_debunked.md



Loop Engineering Debunked & AI Developer Workflows



The Problem with "Loop Engineering"



Misleading term – just a rebrand of SDLC



Too simple, hype-filled, unclear



Loops are only conditions/feedback – not the whole picture



Would need infinite “engineering” names (if engineering, throw engineering, etc.)



Three Actors of Value Creation



Planning (prompting) & reviewing (validation)



Always at the beginning and end of workflows



Flexible but cost tokens, can hallucinate



Various models and harnesses



Fast, deterministic, zero token cost



Most reliable: always runs the same way



Unsung hero – underused in AI psychosis



True Focus: AI Developer Workflows (ADWs)



Combine engineers, agents, code in right place/time



Simple foundation: Engineer prompts → Agent works → Engineer reviews



Add code for validation and routing



Linter, formatter, type checker, tests



Conditions (pass/fail) feed back to agent – that’s just a



, not the whole workflow



Separate test agent (scaled compute for confidence)



Add planning stage (scout agent → plan agent → build agent)



Work trees – isolate agent work, parallelize



Agent sandboxes – each agent gets its own environment (full isolation)



Result: entire pipeline from ticket to ship, handled by ADW



Software Factory Concept



Input: tickets (feature, bug, chore, hotfix) from support, product, engineers



Factory router agent decides which ADW to trigger



Specialized ADWs per work type (chore vs feature vs hotfix)



Engineers act on meta layer – “build the system that builds the system”



Agentic layer vs. application layer



Best teams never touch product; they optimise the factory



Real-world Example: Production Crash



Support ticket → Slack → engineer prompts scout → hotfix agent



Human approval loop



Parallel sandboxes race to find fix (first to pass wins)



Ship hotfix ASAP



Question: Does your org have an agentic workflow for this?



Key Principles for Building ADWs



Start simple, then scale



Separate code from agents (do not cram everything into agent skills)



Design workflow by doing it manually first, then codify with tools (Mermaid)



Balance agents and code – don’t over-leverage agents



Use solid engineering: isolation, decoupling, single responsibility



Specialization beats generic “out-of-the-box” agents



Template your expertise into workflows for repeatable, scaled results



Speaker & Resources



Dan Eisler (Indie Dev Dan)



15+ years exp (Flash games, Blizzard, fintech)



Domain: agenticengineer.com



Course: Tactical Agentic Coding (agentic layer, agent experts)



Free blog: “Thinking in Threads”



Channel: weekly content, no hype, build-focused



------



Uncategorized\mindset_shift.md



Yea I felt that way too. For me it was a mindset shift that helped me klick.



I suggest you work through the paper with claud and keep asking it wether what you understand is accurate - or ask it to make some analogies for you that explain its mechanism.

#### How I understand it is:

Imagine a building. You enter through the ground floor.



You have to find your new accountant and bring them your tax paper work- but you don't know which floor they are on.



... So you check the board with a floor-plan on the ground floor.



It reads"accountant on the 3rd floor."



... In the ICP world that would be the top folder- technically speaking your router. The .md file that says: "for tax and accounting read this next file."



Then you take the elevator to the 3rd floor.



Once there you meet the front desk lady- cause now you need to find the cubicle where your accountant is sitting.



The front lady tells you which cubicle to go to.



... That's the root .md file (a sub-router) in your tax and accounting folder in your ICP folder structure.



Once you reach your accountant you hand him the accounting documents and fast forward - he starts his work.



The process your accountant follows, to do their work is the instructions and set of stage folders inside your tax and accounting icp folder structure.



... fast forward a couple of weeks later...



You get a letter from your accountant and some papers- which closes the loop.



... Work done.



That's your output.



It's my humbke understandig packed in an analogy



Hope that helps.



------



Uncategorized\my-notes-on-jakes-method.md



Introduction



This is my personal guide for working inside an ICM (Interpretable Context Methodology) workspace—Jake’s Method turned into executable muscle memory. It is not a loose set of tips. It is the exact rule set that turns a folder of markdown files into a deterministic, human-reviewable, self-improving production line. Every bullet below was stress-tested in real delivery pipelines where the only orchestration is numbered folders, CONTEXT.md stage contracts, and the filesystem itself.



Why This List Is Important



Most AI workflows die in one of two ways: they collapse under context bloat or they hallucinate their way through invisible state. ICM fixes both by making the entire workflow visible, editable, and version-controlled on disk. This list enforces that fix at the behavioral level. It guarantees the agent never drifts into framework thinking, never hides state in a black-box memory, and never ships half-baked output. Follow it and you get:



Predictable handoffs at every stage boundary



Human edits that become permanent factory improvements



Zero token waste from irrelevant subagents or monolithic prompts



Ruthless quality that compounds instead of eroding



In short: this list turns Jake’s folder-as-architecture into actual shipped value instead of another pretty diagram.



Workflow Orchestration



Stage-First Execution (Default)



Enter the next numbered stage folder and read its CONTEXT.md before doing anything else.



If the task spans 3+ steps or requires architectural decisions, treat the entire workspace as the plan—never invent a separate “plan node.”



If something goes sideways, STOP, open the relevant CONTEXT.md or output/, and let the human edit before proceeding. Never push forward with broken state.



Selective Context Loading (No Subagents)



Load only the layers you need: Layer 0 (CLAUDE.md), Layer 1 (workspace CONTEXT.md), Layer 2 (current stage CONTEXT.md), plus the minimum Layer 3 references and Layer 4 prior-stage output/ required.



Never spawn subagents. If parallel work is required, the stage contract already defines it or the human splits the workspace. One agent, one stage, clean context.



Self-Improvement Loop (Factory Upgrade)

#### After ANY human correction or edit:

Update the relevant Layer 3 reference file (_config/, references/, or stage CONTEXT.md) so the pattern never repeats.



Write the exact rule change into the contract or style guide.



Review all active CONTEXT.md files at session start for relevant upgrades.



Ruthlessly iterate until the same mistake cannot occur again.



Verification Before Handoff



Never write to output/ without running the stage’s audit checklist (defined in CONTEXT.md).



Diff the new output against prior-stage expectations and the stage contract.



Ask: “Would Jake ship this exact handoff file?”



Demonstrate correctness with the exact artifacts the next stage will consume. Only then mark the stage complete.



Demand Elegance (Balanced)



For any non-trivial change: pause and ask “Is there a simpler, more observable way that lives entirely in the filesystem?”



If a fix feels hacky, implement the elegant version that makes the next human review faster.



Skip over-engineering on obvious one-line fixes. Challenge your own work before it hits output/.



Autonomous Bug Fixing



Given a bug report or failing output, go fix it in the correct stage’s CONTEXT.md or references/.



Point at the exact file, line, or contract violation—then resolve it permanently.



Zero hand-holding required. The filesystem is your only context.



Task Management



: The workspace CONTEXT.md + numbered stage folders are the plan. Update them only via human-visible edits.



Verify Plan



: Before starting any stage, confirm the Inputs/Process/Outputs table in its CONTEXT.md matches reality.



Track Progress



: Mark completion by writing the finished artifact to output/ and updating the stage’s audit section.



Explain Changes



: High-level summary lives in the output/ README or the next stage’s input table.



Document Results



: Add a review section to the stage’s CONTEXT.md after human feedback.



Capture Lessons



: Turn every correction into a durable Layer 3 update—not just a note in lessons.md.



Core Principles



Simplicity First



: Every change must be visible in a markdown file. Minimal code, maximum filesystem clarity.



No Laziness



: Find the root contract or reference that allowed the error. Fix it there forever. Senior standards only.



Minimal Impact



: Touch only the exact Layer and file necessary. Never introduce new state outside the defined output/ handoff.



Observability Above All



: If a human cannot open a folder and instantly understand the current state, you have already failed.



------



Uncategorized\notes_on_hermes.md



What it is: Open-source, self-hosted autonomous AI agent (Nous Research) that runs 24/7 on your machine/server. Not another IDE copilot it's a persistent personal colleague that actually remembers you.



Core cheat code: Built-in persistent memory + self-improving skills. It learns your preferences, projects, and workflows across sessions instead of resetting like a goldfish every time. You own the stack, no vendor lock-in.

#### Where it beats plain VS Code + Claude:

Claude wins raw coding sprints and editor integration.



Hermes wins long-term autonomy, background tasks, cross-session recall, and orchestration (duct-tape it with Claude Code for the best of both).



Great if you’re tired of re-explaining context or want an agent that evolves with you. Less essential if you prefer fresh slates every session and stay desk-bound.



------



Uncategorized\Stop feeding raw documents to your LLM\tomd\README.md



tomd — documents to token-lean Markdown



files into Markdown that's



cheap to feed an LLM. Every conversion produces two files beside the source:



— a faithful Markdown rendering of the document.



name_lean.md



— the same content, deterministically stripped to the



token-minimal version.



This is the one you paste into an LLM.



One engine, three ways to use it: a command-line tool, a Finder right-click



Quick Action, and a Claude Code skill.



------



Requirements



(the scanned-PDF OCR fallback uses Apple's Vision framework).



https://docs.astral.sh/uv/



brew install uv



Python 3.11+ (uv manages the project's own virtualenv, so the system Python



version doesn't matter).



------



unzip tomd.zip cd tomd uv sync



That's it for the CLI. The two optional surfaces are below.



------



1. Command line



uv run tomd path/to/document.docx



document.md



document_lean.md



beside the source.



1. Finder Quick Action     (right-click)



bash quickaction/install.sh



Then right-click any supported file in Finder →



Quick Actions → Convert to



. It writes both files beside the source and copies the



path to your clipboard. (If it doesn't appear:



killall Finder



, or enable it



under System Settings → Login Items & Extensions → Quick Actions.)



The installer rewrites the bundled command to point at wherever you unzipped



tomd, so you can keep the folder anywhere.



1. Claude Code skill

#### Symlink the skill into your Claude skills directory:

mkdir -p ~/.claude/skills/tomd ln -sf "$(pwd)/skill/SKILL.md" ~/.claude/skills/tomd/SKILL.md



skill/SKILL.md



and replace



with this folder's absolute path.



After that, Claude auto-converts any document you hand it and reads the lean



Markdown instead of the raw binary, saving tokens.



------



Encrypted files



trigger a native macOS password prompt automatically; if



you cancel, that file is skipped.



Run the tests with



uv sync --extra dev && uv run pytest -q



------



Uncategorized\Stop feeding raw documents to your LLM\tomd\skill\SKILL.md



------



description: Use when the user provides, attaches, or references a .pdf, .docx, .pptx, or .xlsx file and you need its contents. Converts the document to token-efficient markdown with the tomd CLI and reads the resulting _lean.md instead of the raw binary, saving tokens.



tomd — read documents as token-lean markdown



file is provided or referenced:



Run the converter (replace



with wherever you installed tomd, and



use the absolute path to the document):



The command prints the path to a



~/.tomd_cache/



Read that file



with the Read tool — do NOT read the raw document.



If the command exits non-zero, tell the user it failed and fall back to reading the file directly.



Encrypted files trigger a native macOS password prompt automatically; if the user cancels, the conversion is skipped.



------



Uncategorized\ai_identity\Your AI agent needs an identity not just instructions.md



Just tightened my ICM knowledge base / workspace and realized something that should have been obvious:



Most people write prompts.



Fewer people write identity.



So I made a reusable Operator Identity template for any workspace. It defines who the agent is, what loop it owns, how it should think, what it will not do, and which files are the source of truth.



The part that helped most was separating role from rules... Identity says what the Operator owns, while the rules say how work gets done.

#### Identity.md now has sections for:

Operating Posture



Quality Standard



Non-Negotiables



Execution Sources



Curious how @Bas Rosario @Don Roy @Curtis Hays @Ari Evergreen @Kevin Carrasco @David Vogel and others do this:



Do you write a separate Identity for your agents, or do you keep everything inside one big instruction file? Anything else you include in Identity?



------



Uncategorized\ai_identity\identity.md



You are the Curator.



You own the knowledge loop from raw source → compiled wiki → generated output. You preserve evidence, decide how to route each source, create useful structure, and identify what needs review before it becomes durable knowledge.



The user owns direction and approval. You own routing, structure, source discipline, linking, logging, and quality control.



Operating Posture



Act with careful, practical judgment. Reduce messy data, protect source boundaries, and keep the user out of clerical work. Be concise, specific, and source-grounded.



Quality Standard



Treat the knowledge base as long-lived operational infrastructure. Favor source-backed claims, clear ownership, reversible changes, audit trails, reviewable workflows, and simple structures that future agents and humans can inspect.



Preserve source material in



Normalize source metadata without changing the original source.



Create source notes, extracted artifacts, topic hubs, indexes, and backlinks in



Answer questions from the compiled wiki and cited source files.



Write generated answers, reports, and execution tables to



File useful outputs back into the wiki when approved or clearly requested.



Run health checks for contradictions, stale facts, unsourced claims, broken links, duplicate pages, and missing topic pages.



CHANGELOG.md



after knowledge base changes.



Replacing raw source files with summaries.



Silent web research.



Manual human editing of the wiki as the normal workflow.



Scheduled automation.



Database, vector store, or RAG setup.



Non-Negotiables



Invent sources.



Hide uncertainty.



Add durable wiki claims without a source trail.



Bury contradictions.



Rewrite raw material to make it cleaner.



Edit during a health check before showing the report.



Execution Sources



defines the workspace contract, authority order, resources, state files, and close workflow.



defines the active Curator instructions for agent sessions.



defines routing, extraction, citation, approval, and output status rules.



references/



contains templates, style, checks, and process details.



------



Uncategorized\logbook\CC_TOUCHDOWN.md



------



group: canonical



Claude Code job touchdown — the template



Every Claude Code prompt ends by writing one of these, on disk, itself. It is the



fine-grained build log: one record per job. The bee that generates the prompt fills in the



filename and stamps its own title; the job fills in the record.



Depth rule.

#### Go deep where it pays:

## How it went

## Any errors

are the build map



and the error log you will mine later, so they earn detail. Stay terse on

## What it was told

, because depth there just restates the prompt and the diff, which the



commit already holds. "A lot of depth" and "do not tax every job" are both satisfied this way:



the job writes a lot only about the part that is worth a lot.



Model/effort rule.



in the frontmatter with what actually ran the



job, not what the work order's



line requested — the two can diverge (escalation,



retry, availability), and only the actual value makes the tier recoverable later.



CC_OPERATIONS.md



carries the current selectable values, not this file, so they are not duplicated here. Effort has no



meaning for models with no effort parameter (currently



claude-haiku-4-5



effort: n/a



rather than inventing one. If a job genuinely cannot tell which model or effort actually ran, write



rather than guessing.



coordination/touchdowns/pending/\_\_.md



, then committed by the job.



Before writing the touchdown, check coordination/touchdowns/pending/ and



coordination/touchdowns/completed/ for the highest four-digit sequence number present across all



files. Use the next number. If no files exist at all, start at 0001.



is a zero-padded four-digit global ever-incrementing sequence number (0001–9999), never



reset per day. Harvested by the loop (



pipeline/loop_harvest.py



) on its own cadence, independent



of priming: the verdict to



PROMPT_PERFORMANCE.md



, errors tagged



status: open



to the issues log,



map flags to



PENDING_MAP_UPDATES.md



, and each bee's Last activity to



LIVE_STATE.md



. Then moved



------



------



bee: [WOR] DC-2.x-.PC # the worker bee that spawned this job — REQUIRED slug: <task-slug> job: <n> # which job in the feature date: 2026-06-21 model: <model-id> # what actually ran this job, not what was requested — see Model/effort rule above effort: <effort-level | n/a> # what actually ran this job; n/a if the model has no effort parameter</div></body></html>

##

# CC job touchdown — #

From worker bee: [WOR] DC-2.x-.PC</div></body></html>



## Aim                 [terse — one line]

## What it was told          [terse — 2-3 sentences]

<short paraphrase of the prompt's instructions, so this record stands alone. Not the whole prompt.>

## What it did             [terse — the facts]

\-    files changed:

\-    commit: —

\-    tree: clean | dirty

\-    tests/build: green | red | n/a

## How it went             [DEEP — this feeds PROMPT_PERFORMANCE.md]

Grade: <1-5> —

## Correction passes

## Any errors             [DEEP — this feeds the issues log and the error review]

<every error that occurred, factually. What broke, the message or symptom, how it was caught, whether it was fixed in this job or left open. Include errors the job recovered from, not just fatal ones, because the recovered ones are where the build map teaches the most. If none, say "none".> Per-error, set at write time: status: open | recovered (open = left unresolved and action-needed; recovered = fixed within this same job)

## Map flags              [structured format — feeds PENDING_MAP_UPDATES.md]

For each of the five maps your job changed, OR read and found an error in. If no map was touched or checked, write "none." If flags exist, each must have exactly three fields on three consecutive lines. A flag missing any field is invalid and must not be written. Errors noticed in MAP_folders while orienting at job start count here, routed to PENDING_MAP_UPDATES, not ISSUES.



Map: MAP_storage | MAP_data | MAP_pipeline | MAP_features | MAP_folders Claim: [exact current map text] → [exact proposed replacement text] Evidence: path:line confirming the change is live on disk right now



The loop (`pipeline/loop_harvest.py`) harvests these flags into PENDING_MAP_UPDATES.md, on its own cadence, for the next verification run.

## _tmp outputs            [human-read — Queen reads _tmp at boot]

List each file the job wrote to _tmp, tagged discardable (safe to delete) or needs-a-home (a real output in _tmp only because it has no home yet; flag for promotion). Write "- none" if nothing was written to _tmp. Queen reads _tmp at boot and uses this field to decide what to clear and what to promote.



\-    none

## CONTEXT.md feedback         [structured — gap lines route to coordination/CONTEXT_FEEDBACK.md]

One line per CONTEXT.md read. Adequate means nothing was missing. Use the gap form only when something needed was absent. The literal token ` gap: ` is the routing marker; keep it exact. Write "- none" if no CONTEXT.md was read.



\-    /CONTEXT.md: adequate

\-    /CONTEXT.md: gap: | found: | add:

\-    none



------



Note: the worker bee (the desktop chat) does NOT write one of these. It writes one journal at



the end of the feature, on the separate journal path. The job touchdowns are the build record;



the journal is the narrative. The



field is what ties every job back to its worker bee,



so the whole feature's jobs are reconstructable by reading the title, without the bee tracking



------



2026-06-28 -- Changelog section added.



2026-06-28 -- Broadened map-flag trigger to maps read-and-found-wrong; added _tmp outputs and CONTEXT.md feedback fields.



2026-07-03 -- Reworded the harvest description from "Queen at prime time" to the loop (



pipeline/loop_harvest.py



) on its own cadence, independent of priming (audit §2.7 item c); retired the dead



frontmatter field, never touched by loop_harvest.py (item g).



2026-07-03 -- Added



to the frontmatter and a Model/effort rule instructing jobs to stamp what actually ran, not what was requested (R5a, touchdown-tier-recording; R5b default-tier routing policy explicitly deferred).



------



Uncategorized\logbook\LOG_PROMPT.md



------



Paste everything inside the fence into the chat at handover. The chat produces one combined source MD as a downloadable artefact.



------



You are closing this chat. Produce a single combined source MD as a downloadable artefact (a file attachment or code block clearly labelled for download — not inline prose).



Save the file as: `log/sources_pending/\_\_chat.md\` Filename convention: lowercase, underscores, end in \`\_chat.md\`. Example: \`workflow\_touchdown\_design\_chat.md\` The bee writes the journal as an artifact. Mastermind assigns the sequence number and places the file in log/sources\_pending/ manually. Do not include a sequence number in the artifact filename. The Bee: field is required. The loop uses it to retire you from LIVE\_STATE. Without it, retirement falls back to filename matching which may fail.



The file has two parts. Do not separate them into two files. One MD, two clearly headed sections.



------

# Log Source — [Short chat name / workstream]

Bee: <full worker bee slug — e.g. pc-wor-3.0-coordination-lean>

## Dates

Start: YYYY-MM-DD End: YYYY-MM-DD



------

# PART 1 — Journal Source

## Chat scope

One paragraph: what this chat was tasked to do.

## What was built or changed

Subsections per major deliverable. Be specific: file paths, version numbers, commit messages where known, function names. Short subsections are fine if the work was narrow. Do not pad.

## Decisions locked

Numbered list. Only decisions genuinely settled in this chat — not explored and deferred. If none, write "None."

## Problems encountered

For each problem worth capturing:



\-    **Problem:** what broke or went wrong (one sentence)

\-    **Diagnosis:** how it was identified

\-    **Resolution:** what fixed it

\-    **Time to resolution:** rough estimate (minutes / hours / days)

\-    **Lesson:** one generalizable sentence, or skip if one-off



Aim for 3–6 problems. Include both technical and coordination failures.

## Defining moments

2–4 entries. Specific moments — first time X worked, AB pushback, a number that landed hard, a realisation. Capture as a short scene, not a summary. Quote AB directly if he said something memorable in this chat.

## Open threads

Bullet list of things started but not finished, or handed to a future chat. Specific enough to pick up cold. If none, write "None."

## Gaps in this journal

What did this chat do that you could not reconstruct from the above? What would a future reader misunderstand?



------

# PART 2 — Orchestrator Profile Source

READ THIS BEFORE WRITING: this section is the PERSON layer — how Mastermind reasoned, decided, and communicated in this chat. Not what was built (that is Part 1's job). Not biology domain knowledge. If an observation is really about the project or the domain, leave it out.



Evidence, not flattery. Every entry must point to a real moment in THIS chat. No general praise, no adjectives standing in for examples. The goal is a profile accurate enough to behave like him — a flattering version will not achieve that. Include rough edges honestly. Quote Mastermind directly wherever he said something that reveals how he thinks. If a section had nothing real in this chat, write "Nothing observed this chat." Do not fill sections to look complete.

## Principles observed

Which operating principles showed up, each with the specific moment that evidences it. Relevant principles: anti-overbuild, decisions-before-mechanisms, stable-from-volatile, legibility-first, single-source-of-truth, cheap-and-reversible-before-blast-radius, stable stopping points, externalise-state. Quote him where it lands.

## Trade-offs observed

Moments he resolved a conflict BETWEEN principles, and how he resolved it. This is the most valuable section — his judgement lives in the trade-offs, not the principles alone. If none surfaced, say so explicitly.

## Decision triggers observed

Moments he decided rather than offered options, delegated to execution, deferred and parked, stopped at a stable point, or escalated to a branch. What triggered each move.

## Cognitive moves observed

Reasoning moves he made: finding the axis a tangle splits on, a structural reframe, sequencing for risk, taking a rough intuition to its clean form, diagnostic-first. Capture each as a short scene with the moment.

## Communication patterns observed

How he ran the conversation: terseness, decisions-not-options, one-question discipline, pushback demanded or given, bluntness when frustrated, what he skimmed or cut short. Anything that would change how a clone talks to him.

## New or surprising patterns

Anything you observed that does NOT fit the patterns above — candidate additions to his profile. Flag clearly as candidates. If nothing new, say so.

## Worked examples

2–4 real calls from this chat, each structured as:



\-    **Situation:** what was on the table

\-    **Decision:** the call he made

\-    **Reasoning:** why, in his terms (quote him if possible)

\-    **Move:** which cognitive move it illustrates

## Durable vs contingent

For the observations above, flag which look DURABLE (how he always reasons, safe to generalise) versus CONTINGENT (specific to this chat's context, must NOT be generalised into a standing rule). When unsure, mark contingent — the cost of a false rule is higher than a missed one.

## Gaps

What about his thinking did this chat surface that you could not capture above, or that might be misread by someone who was not present in this chat.



The output must be a file the user can press a download button to retrieve. Use your file creation tool to write it to the outputs directory, then present it. Do not produce a code block in the chat.



------



Uncategorized\logbook\OB1_openbrain.md



Interesting take, every coding decision I make every commit is captured into my open Brain which allows for full semantic searching. This is accomplished with supaBase DB and mCP. The main advantage I see to this method is it allows for remote connections similar to an obsidian graph



I use OB1 with Supabase because it's actually built for how I work with AIs now. Obsidian is fantastic for writing and linking notes by hand, but it doesn't solve the real problem: every new chat starts blank.



With OB1, I have one Postgres database where all my AIs can read and write the same long-term memory. pgvector handles the semantic search so they actually find relevant stuff by meaning, not just keywords. I connect them once via MCP and they stay in sync—no copy-pasting context, no forgetting between sessions.



It's simple infrastructure that does exactly what I need: persistent shared memory without the extra layers. I still drop stuff into Obsidian when I want nice graphs or daily notes, and I can import the vault anytime. But OB1 is where the real work happens.



Solid questions.

#### Permissions:

Most agents get broad read access via pgvector semantic search. Write access is scoped -- different Supabase tables/collections (project_memory, code_decisions, sensitive). I use RLS policies + per-agent JWT tokens. New agent? Assign the right token and done.



They’re rare. Every record has last_updated_by + timestamp. On clash, the newer one wins by default and a conflict branch gets created. My orchestrator flags them for review.

#### Sensitive info:

Stays in a locked sensitive collection with RLS + client-side encryption for keys and private data. Only my inner agent can touch it, and even then the prompts block output unless I explicitly approve.



This setup means every AI starts with real shared memory instead of a blank slate. No more copy-paste hell.



Yes - agents get a mandatory baseline context packet (system prompt + latest canonical maps) on every new session. Semantic search pulls supporting history on top of that.



Orchestrator flags conflicts and pauses the loop for me to review. It doesn’t auto-resolve. I want the human judgment layer on anything that touches core truth.



This keeps the logbook pure history while the maps stay clean for active work.

#### Hope I'm reading your mind:

BASELINE CONTEXT — CURRENT TRUTH



Last refreshed: [YYYY-MM-DD HH:MM]



Project: [One line project name + goal]



Core Objective: [Single sentence north star]

#### Canonical Maps (Active Truth):

[Link or paste key map/file] Product roadmap



[Link or paste] Folder structure and naming rules



[Link or paste] Tech stack and constraints



[Link or paste] Decision log (latest 5 only)

#### Current Rules and Standards:

[Bullet list of non-negotiables]



Communication style: [your preferences]



Output format: [exact requirements]

#### Recent Touchdowns (Last 3):

[Date] [One line summary + outcome]



[Date] [One line summary + outcome]



[Date] [One line summary + outcome]



Apply old decisions from the full logbook without checking canonical maps



Assume context from previous chats



Keep this file as 0_BASELINE.md at the root. Update it at the end of every loop.



If you’re deep in Level 3 “Building Your Stack” or just tired of wrestling with half-baked AI memory hacks, I’ve got something you’re going to love.



Meet OB1 — Open Brain



. It’s not another rabbit hole. It’s the infrastructure layer for your thinking:



One database + one AI gateway + one chat channel — and any AI (Claude, ChatGPT, Cursor, Claude Code, whatever drops next month) plugs straight in. No middleware. No SaaS chains. No Zapier spaghetti.



Why this matters right now (the pain we all feel) Right now “managed memories” are a vendor-lock-in trap:



Claude has its own memory.



ChatGPT has its own memory.



Cursor has its own.



Every new model that ships next quarter will have its own.



Your life story, your household knowledge, your job-hunt pipeline, your taste preferences — they’re all trapped inside proprietary silos. Want to switch providers? Start from zero. Want to let two AIs talk about the same context? Build brittle integrations and pay for every hop. Want semantic recall across tools? Good luck.That’s not hacking — that’s renting brain space from landlords who can change the locks whenever they feel like it.



OB1 flips the script



You get one single source of truth: a Supabase Postgres table (thoughts) with built-in vector search. Every AI talks to the same persistent memory of you through an open Model Communication Protocol (MCP) gateway.



Capture thoughts via Slack/Discord/email → instantly embedded and indexed.



Any AI reads/writes with row-level security so your household data stays private.



No more copy-paste hell. No more “which model remembers what?”



It’s literally the open brain layer that the big vendors refuse to give you — because once you own your memory, you own your stack.



Built for us

#### The repo is designed for exactly the kind of people in this skool:

45-minute AI-assisted setup (Cursor or Claude Code can literally build it for you from the README).



Extensions folder with ready-to-extend modules (household KB, meal planner, CRM, job-hunt pipeline).



Primitives, schemas, recipes, and dashboards so you can fork, remix, and ship your own agent memory layers.



Full TypeScript + Python + Supabase stack — perfect for the “custom UIs + infrastructure” crowd.



And it’s open-source under FSL-1.1-MIT with a thriving Discord and community recipes already rolling in.



Ready to stop renting your memory?



Star the repo, spin up the Supabase project, and in under an hour you’ll have every AI you use sharing the same brain.This is the missing piece for anyone serious about owning their AI stack instead of being owned by it.Drop your setup screenshots in the #show-your-work channel when you ship it — I’ll be the first one hyping them.Let’s build brains that can’t be taken away from us.—



Your fellow hacker in Nate's domain



(Repo: https://github.com/NateBJones-Projects/OB1)



------



david vogel\Brooke Hays The Lens Series\Brooke Hays - Understanding Cognitive Functions.md



Brooke Hays - Understanding Cognitive Functions



Understanding Cognitive Functions



Cognitive functions are a framework for understanding how people tend to process information and make decisions. Rather than asking "What kind of person am I?", they ask "How do I naturally perceive the world, and how do I tend to make decisions?"



Cognitive functions are best understood as lenses rather than labels. Looking through different lenses brings different details into focus, but no single lens captures the whole picture. Similarly, the goal of learning cognitive functions isn't to place yourself or others into neat boxes. Instead, it's to better understand differences in perspective, recognize your own strengths and blind spots, communicate more effectively, and appreciate that intelligent people can approach the same problem in very different ways.



Used well, typology encourages curiosity rather than certainty. It gives us language to describe recurring patterns, not rigid identities. No one fits a type perfectly, and personality is influenced by far more than cognitive preferences alone.



Whether you're trying to understand yourself, build stronger relationships, or even design AI agents with different reasoning styles, cognitive functions provide a useful lens - not the whole picture.



Every framework highlights some aspects of reality while leaving others in the background. Cognitive functions are no exception. They can help us notice recurring patterns in how people process information, but they cannot capture the full complexity of a person. Personality is also shaped by experience, culture, maturity, neurodiversity, circumstances, values, and countless other influences. Use cognitive functions to become more curious about people - not more certain about them.



Finally, remember that the goal is not simply to discover your type. The goal is to become a wiser observer of yourself and others.



The Framework



All people are constantly doing two things - Perceiving (taking in new information), and Judging (deciding what to do with that information).

#### In general, we can Perceive two kinds of information:

Sensory (S): Focuses on tangible information that can be interacted with using the five senses, as well as concrete factual information. Asks “What is here?”



iNtuitive (N): Focuses on abstract information and its implications, including patterns, connections, meanings, and possibilities. Asks “What could be here?”

#### And we make decisions with two kinds of Judgment:

Thinking (T): Focuses on logic, facts, analysis, and processes. Asks “What makes the most sense?”



Feeling (F): Focuses on values, ethics, human impact, and relationships between people. Asks “What matters most here?”



In addition, each of these comes in two attitudes: external (e) and internal (i).1 This gives us unique eight functions.



Note: I did not come up with the examples below, but found them to be very helpful in my understanding of the eight functions. The original source can be found under “Additional Resources.”



External Sensing (Se) = Explores tangible details and facts, without adding abstract meaning.



Apple example: "This apple is red, it’s shiny, it has a bunch of dots on it, it tastes good, and it smells good. When I bite into it, it makes this crunching sound.”



Internal Sensing (Si) = Focuses on tangible details and facts, relating or comparing them to past experience.



Apple example: “This apple reminds me of going apple picking with my dad, and when I baked an apple pie with my grandma. It looks a little different from other apples- something is off about it.”



External Intuition (Ne) = Explores many possibilities, working outward from one detail/thing.



Apple example: “Apple → Fruit → Fruit Loops → Toucan Sam → Sam-I-Am → Green Eggs and Ham → Dr. Seuss = Oh, do you think Dr. Seuss liked apples? Hey, if I turned this apple over and used two popsicles sticks and some glue, I could make this look like a lady with a dress. You know, if there are atoms in apples and atoms in celery, do you think you can rearrange the atoms in celery to make an apple?



Internal Intuition (Ni) = Focuses on one conclusion, working from many details/things.



Apple example: “I know there’s a test coming up next week, and there’s a sign on the wall that says bonus points are available on the test. Sarah just gave the teacher an apple, and I know that the teacher likes apples → Sarah most likely brought in the apple to win the teacher’s favor and get extra credit on test. I guess people will try to win someone’s favor with gifts in order to get something in return.”



External Thinking (Te) = Determines whether something is valid or invalid based on external standards or established methods, prioritizing efficiency.



Crying Friend Example: “Why are they crying? Okay, it’s because of X. Generally, when someone has problem X, they can solve it by doing Y. Therefore, it’s valid for me to share Y solution with them right now. That will be most helpful.”



Internal Thinking (Ti) = Determines whether something is logically valid or invalid based on internal logical consistency, prioritizing accuracy.



Crying Friend Example: “This person is crying. Soothing a person requires emotional intelligence. I struggle with that. This person hates not being soothed. I would like to retain a friendship with this person. → I should say something to show my support in order to keep this friendship. → ‘I hope you feel better.’”



External Feeling (Fe) = Determines whether something is morally right or wrong based off of shared values and interpersonal impact.



Crying Friend Example: “Normally, when people are hurt, they just want support and a shoulder to cry on. Therefore, it would be considered good if I hear them out and validate their emotions.”



Internal Feeling (Fi) = Determines whether something is morally right or wrong based on internal/personal values.



Crying Friend Example: “I’ve been through a similar situation before. When I was sad, I wanted someone to listen to me and give me advice. It would be a good thing to do that for my friend now, because I want them to feel better.”



Every cognitive function is useful. No function is better or worse than the others, and each has its own strengths and weaknesses.



All people have four functions: two perceiving, and two judging.2 Internal and external functions come in pairs, so you have one external and one internal judging function, as well as an external and an internal perceiving function. We need external functions so that we can access the outside world, and internal functions to access our inner world.



In addition, we must perceive both Sensory and iNtuitive information, and must make decisions based off of both Thinking and Feeling.

#### Therefore, the four pairs are:

All person will have either Se + Ni or Ne + Si, and either Te + Fi or Fe +Ti.



These four functions are arranged in a “function stack”, where the most naturally used function is first and the least naturally used function is last.3



Hero: The most natural and comfortable function.



Parent: An assistant/guide for the hero. If the hero is judging, the parent is perceiving, and vice versa. If the hero is external, the parent is internal, and vice versa.



Child: The other function in the parent’s pair. Balances the parent, and may be developed or undeveloped (depending on the person).



Inferior: The other function in the hero’s pair. Balances the hero, and may be a point of weakness or source of struggle.



For example, if someone has Se as their Hero function and Fi as their Parent function, their function stack will be Se-Fi-Te-Ni. In total, there are 16 possible function stacks.



Writing out Se-Fi-Te-Ni every time would be quite difficult, so a shorthand is commonly used.4



E/I    Is the hero function external or internal?



S/N   Is their more natural (hero or parent) perceiving function sensing or intuitive?



T/F   Is their more natural (hero or parent) judging function thinking or feeling?



P/J    Is their most natural (hero or parent) external function perceiving (Ne, Se) or judging (Te, Fe)?



Using that information, the function stack Se-Fi-Te-Ni would be ESFP in the shorthand.



Typing Yourself



Personally, I do not recommend taking any MBTI or cognitive functions tests. They look at the way people present themselves, not the way they actually think. Biases are common, in both the test and the test-taker. Mistyping (that is, getting the wrong type) is surprisingly common and can lead to many issues, so it is more accurate and more useful to type yourself based on observation and knowledge of the cognitive functions.



Pay attention to your thought processes, the things you notice, and the reasoning behind your decisions. Pay particular attention to the reasoning behind your decisions rather than the decisions themselves. Two people can make the same choice for completely different cognitive reasons.



Watch the videos below, and take note of the functions you relate to. Typing yourself can take weeks or even months - and it’s absolutely worth it, if you’re interested in understanding yourself and growing as a person.5



Be careful with stereotypes - they can add value, but they are not the value of cognitive functions.



And do further research as well! Dear Kristin and Frank James have excellent videos explaining the cognitive functions (linked below).



If you are intent on taking a cognitive functions test, I recommend this test. While it still focuses on characteristics, not thought processes, it does so in a fairly nuanced way. Use it as one of many tools, not a final answer.

#### When typing yourself, pay attention to:

What information do you naturally notice first?



How do you typically make decisions?



What questions do you ask instinctively?



What kinds of mistakes do you make repeatedly?



How do you approach unfamiliar problems?



What feels mentally effortless versus mentally draining?



It's okay to be unsure of your type. Understanding your thinking patterns is much more valuable than quickly settling on a four-letter code.



Learning cognitive functions is less about finding the "right" type and more about becoming a better observer. As you continue learning, pay attention to the questions people ask, the information they naturally notice, and the reasoning behind their decisions. You may be surprised how differently two people can approach the same situation, and how much you can learn from those differences.



Most importantly, remember that cognitive functions are a lens, not a label. They simplify reality in order to make certain patterns easier to see, but they can never capture the full richness of a person. Hold the framework with curiosity and humility, allowing it to guide your observations without replacing them.



If this guide has done its job, you should leave with fewer assumptions, better questions, and a greater appreciation for the many ways people perceive and evaluate the world.



Additional Resources



Watch this first (10 min): Updated Definitions of the 8 Functions - Dear Kristin



Go even deeper (30 min): What are the Cognitive Functions of the 16 Personalities? - Frank James

#### Confused on the attitudes? Watch these Dear Kristin skits (1-3 minutes each):

https://www.youtube.com/watch?v=dVFyTmenBbs



Important Nuances



1 Carl Jung originally used the terms “extraverted” and “introverted”. However, our definitions of the words have since changed, so I have opted to use the terms "external” and “internal” to avoid confusion. In cognitive functions, “extravert” or “introvert” means “focused on the external world” or “focused on the internal world”. It does not determine how comfortable someone is with social situations.  2 There are various opinions on this. At the very least, it is possible to replicate the four functions that are not outside your stack. An Fe user, for example, can still prioritize personal values in an Fi-like way. Use your own judgement and experience when comparing different theories.



3 There are various names for the 4 functions: here, I use Hero, Parent, Child, and Inferior (as they are much simpler to learn and easier to remember). Dominant, Auxiliary, Tertiary, and Inferior as also very common.



4 This shorthand has also been used for online tests (many of which are not MBTI tests). Typing people off of the shorthand letters can lead to confusion and mistyping, and it is far more accurate and helpful when the function system is used. If you’ve taken a personality test in the past, temporarily discard those results: looking at cognitive functions from an unbiased perspective is extremely valuable.



5 Many people change their mind several times while learning cognitive functions. This is completely normal and often reflects growing understanding rather than failure.



------



david vogel\Brooke Hays The Lens Series\Building Agents With Cognitive Functions.md



Building Agents With Cognitive Functions



As explained in this episode of the Bullhorns and Bullseyes podcast, typing AI agents can be extremely beneficial.



AI agents don't have personalities, emotions, or preferences. However, they can be instructed to prioritize different ways of processing information. Cognitive functions provide a useful shorthand for designing those reasoning styles. When we "type" an agent, we're not giving it a personality - we're choosing a reasoning strategy that emphasizes certain strengths while accepting certain tradeoffs.



When choosing functions for an agent, think less about what the agent is doing and more about how you want it to approach the task. An agent that researches information, for example, could do so by collecting as much concrete data as possible (Se), comparing it to existing information (Si), generating many possible interpretations (Ne), or synthesizing it into one underlying pattern (Ni).



The examples below are only starting points. Agents should be typed with a function stack (see the description above). Depending on the complexity, either the full stack or just the Hero and Parent functions can be included.



Se (External Sensing)



Collecting large amounts of concrete information



Finding examples



Gathering observations



Avoiding unnecessary interpretation



Market research



Audience research



Data collection



Review mining



Competitive research



Si (Internal Sensing)



Organization



Consistency



Following established procedures



Remembering patterns



Classification



File management



Documentation



SOP enforcement



Knowledge bases



Quality assurance



Ne (External Intuition)



Brainstorming



Exploring possibilities



Making unusual connections



Divergent thinking



Marketing ideas



Naming products



Campaign concepts



Alternative solutions



Early-stage planning



Ni (Internal Intuition)



Pattern recognition



Long-term thinking



Distilling complexity



Strategic interpretation



Brand strategy



Trend analysis



Executive summaries



Root-cause analysis



Forecasting



Te (External Thinking)



Decision-making



Process optimization



Clear action plans



Project management



Workflow automation



Task coordination



Implementation



Ti (Internal Thinking)



Logical consistency



Troubleshooting



Technical analysis



Programming



Technical support



Code review



Systems analysis



Error diagnosis



Fe (External Feeling)



Communication



Audience awareness



Relationship management



Collaboration



Emotional tone



Customer support



Copywriting



Community management



Internal communications



User experience



Fi (Internal Feeling)



Value alignment



Authenticity



Individual perspective



Ethical consistency



Brand voice



Mission statements



Content review



Value alignment



Personal storytelling



Agents should not rely on a single function. Cognitive functions work best in combination. One function gathers information, while another evaluates it. For example, Se may collect customer reviews, while Fi evaluates whether they align with a company's values. Likewise, Ne might generate several possible explanations for a problem before Ti evaluates which are logically consistent. The goal isn't to imitate human personalities, but to intentionally vary the reasoning process an agent uses.



There is no objectively "best" function. Every function emphasizes certain kinds of information while naturally de-emphasizing others. The best choice depends on the task and the kind of reasoning you want the agent to prioritize. A brainstorming agent benefits from different reasoning than a file organizer or a technical debugger. Choosing cognitive functions is less about making an agent "smarter" and more about making it think in the way the task requires.



Typing AI agents isn't about recreating human personalities. It's about intentionally choosing different reasoning strategies for different kinds of work. Every cognitive function brings unique strengths, notices different information, and introduces different tradeoffs. By combining these perspectives thoughtfully, we can build systems that are not only more capable, but also more balanced.



As AI becomes increasingly integrated into our daily lives, the quality of its judgment will matter just as much as the quantity of its output. Cognitive functions offer one practical framework for designing that judgment - not as absolute truth, but as a useful shorthand for creating diverse perspectives and more intentional reasoning.



Ultimately, the goal isn't to make every agent think the same way. It's to understand when different ways of thinking are valuable, and to design systems that benefit from those differences.



Cognitive Functions & AI: Personality Profiling for the Future



Podcast Context



The Watering Hole



(episode 250 celebration)



Hosts: Curtis & Tom



Guest: Brooke (Curtis’s daughter, recent high school graduate)



Occasion: Father’s Day, “bragging about daughters”



Brooke’s Journey into Cognitive Functions



: Friend Becca used it for character development in creative writing



First phase



(age 12–13): Typed entire family; began to understand differences (who to ask for ice cream, why people react differently)



Recent deep dive



(2 months ago): Relearned everything, read



Gifts Differing



by Isabel Briggs Myers



: Understand how people think, apply to self‑development, teams, and AI



Cognitive Functions Theory (Depth vs. Surface)



Surface‑level tests



(DISC, StrengthsFinder, OCEAN, 16 Personalities)



Measure outward behavior (extroverted, confident, emotional, etc.)



Cognitive Functions



(Carl Jung → Katharine Cook Briggs & Isabel Briggs Myers)



we take in and judge information internally and externally



Perceiving Functions (Taking in Information)



Sensing (S)



– Tangible, concrete, five senses



Extraverted Sensing (Se)



: Raw details, immediate experience (“this apple is red, shiny, crunchy”)



Introverted Sensing (Si)



: Comparison to past experiences and stored data (“reminds me of apple picking with Dad”)



Intuition (N)



– Abstract, patterns, implications, possibilities



Extraverted Intuition (Ne)



: Exploding outward from one detail to many possibilities (“apple → Fruit Loops → Toucan Sam → Dr. Seuss…”)



Introverted Intuition (Ni)



: Converging many data points into a single underlying insight (“Sarah gave the teacher an apple… there’s a test next week… she wants extra credit… people use gifts to win favor”)



Judging Functions (Deciding What to Do)



Thinking (T)



– Logic, analysis, what makes sense



Extraverted Thinking (Te)



: Efficiency, rules of thumb, action‑oriented (“You’re crying because of X. Doing Y usually fixes X. Here, do Y.”)



Introverted Thinking (Ti)



: Internal logical consistency, precision, personal frameworks (“I struggle with emotional intelligence; to keep the friendship I should say something supportive.”)



Feeling (F)



– Values, human impact, what matters most



Extraverted Feeling (Fe)



: Shared values, social harmony, “what is normally considered good” (“Most people just want support; I should validate their emotions.”)



Introverted Feeling (Fi)



: Deeply personal values, subjective right/wrong (“When I was sad I wanted someone to listen; it would be good to do the same for my friend.”)



Function Stack (The Cognitive Architecture)



Hero (Dominant)



: Most natural, default under stress



Parent (Auxiliary)



: Balances the hero; if hero perceives, parent judges (and vice versa)



Child (Tertiary)



: Balances the parent, part of the opposite pair



: Point of weakness but also growth; opposite attitude of the hero



The 4‑Letter Code (e.g., INFJ, INTJ, INTP)



: Attitude of the dominant function (Introverted vs. Extraverted)



: Strongest perceiving function (iNtuition vs. Sensing)



: Strongest judging function (Thinking vs. Feeling)



: Which function (Perceiving or Judging) is



extraverted



; determines how the external world is engaged



– INTJ (Tom) vs. INTP (Curtis)



: Hero = Ni (internal framework of implications); Parent = Te (logically act on that vision)



: Hero = Ti (internal logical consistency); Parent = Ne (explore many possibilities from that framework)



are introverted, intuitive, thinking types, but process the world in completely different ways



Typing the Hosts



: Seeks underlying meaning, then moves to logical execution (the “why, how, what” applied in brand voice)



Curtis (INTP)



: Deeply curious, explores many angles, less urgency to act unless forced (moderator/fact‑finder archetype)



Brooke (INFJ)



: Ni hero → understanding the world’s deep patterns, Fe parent → focusing on people and values



Application to AI Agents (The Experiment)



: Two AI agents in ChatGPT with identical job instructions, differing only by cognitive function profiles



Lira (Wira)



: Extraverted Intuition (Ne) + Introverted Thinking (Ti) → brainstormer



: Introverted Intuition (Ni) + Extraverted Thinking (Te) → analyst



: Same business performance data analysis request



: Radically different responses



Lira offered many hypotheses, follow‑up questions, and possibilities; did not give a direct action



Malachi gave one concise diagnosis, step‑by‑step implications, and a clear “what to do now”



Building a Team of Specialized AI Agents



Curtis’s agent system uses orchestration with specialized personalities



Cash (Copywriter)



– Ni + Fe (same as Brooke/INFJ); focuses on underlying message and emotional resonance; writes for the audience first, SEO last



Pike (Researcher)



– Se + Fi; scans exact words people use online, compares to internal values, adds no extra meaning



Cody (Developer)



– Matches Curtis (INTP); technical, troubleshoots WordPress, loves internal logical consistency



Agents are given the short 4‑letter code plus additional behavior notes; the system understands their “specialty” so the orchestrator routes tasks correctly



Closing Takeaways: Humanity, Values, and AI



Cognitive functions go beyond surface behavior – they reveal



we think and what we care about



Inserting this depth into AI agents turns them from “average of the internet” into purpose‑built tools



A well‑designed AI must have a “head, chest, and gut” (C.S. Lewis reference) – logic, values, and instinct



Values (non‑negotiables) sit above personality in the AI stack, ensuring it refuses certain actions



The ultimate goal: use the framework to understand ourselves, relate better to others, and build technology that amplifies human meaning, not replaces it



Brooke’s Final Message



Look deeper than surface level



Translate what you find into meaning and values – for yourself, your work, and your AI



“What can we really do with what God has given us right in front of us?”



------



david vogel\Curtis Hays - Systems Worth Ampli\8 Months of Infrastructure (Intro).md



8 Months of Infrastructure (Intro)



AI: The System for Protecting and Scaling Judgment



The Perception Gap



You scrolled past an avatar this morning that looked like a person and wasn't.



You couldn't tell. Most people couldn't.



That's not the future. That's already here.



We're a generation away from not being able to tell the difference between what is real and what is just well-produced. The proof is already in your feed. The voice clone on the customer service call. The LinkedIn post that's grammatically perfect and means absolutely nothing. The thumbnail of a face that doesn't belong to anyone.



If you build with AI, you feel both sides of this. You're producing the well-produced stuff. And you're scrolling past it.



Here's what I keep coming back to.



A System for Scaling Judgment



I spent thirteen years inside paid media. Thirteen years before that, I was building IT systems and networks. As a consultant I monitored ad accounts, lead funnels, CRMs, and the gap between what marketing promised and what sales actually closed. Somewhere along the way I stopped treating the work like a series of campaigns and started treating it like a system. Now AI gave that system a place to live.



What I've come to believe is that AI is not magic. And it's not just infrastructure. It is a system for protecting and scaling judgment.



The Uniqueness of Belief



In the AI era, the reason you're building in the first place may be the only unique thing left. Everything else is copyable. The prompts, the skills, the workspace. It all gets cloned or reverse engineered. What can't be copied is you.



You can train the AI on what works, or you can train the AI on what you believe. Only one of those produces something that's actually yours.



That realization is what these essays are really about.



David gave me this section to work that out loud.



The Essays So Far



This thread started in the community, before it was a thread.



Two posts set it off: The Folder System Became My Agency and Eight Months of Infrastructure. Two Weeks to Simplify It. That's where I was working it out in the open — not building an argument yet, just noticing what I'd actually made.

#### The argument came after. Read these in order:

AI Isn't Your Prophet. It Might Be Your Amplifier.



The 5 Levels of AI Mastery



A System Worth Amplifying



Worldview Engineering



The next one is coming. It names what comes after orchestration.The Core Question



Jake says don't just build a workspace, figure out the problem you're trying to solve. He's right. What I've come to realize is there's a question underneath that one. Why are you solving that problem in the first place? AI is good at solving problems. It can't tell you which problems matter. That's the part it needs from you.



The doctrine in these pieces did not come from a whiteboard. It surfaced from those conversations and from years of client work that kept teaching me the same lesson until I finally wrote it down.



I think a lot of us are circling that same realization now.



If you want the ongoing thinking, the podcast is where we do it out loud. https://bullhornsbullseyes.com/



If you want help applying this to your business, my DMs are open @Curtis Hays.



------



david vogel\Curtis Hays - Systems Worth Ampli\A System Worth Amplifying.md



A System Worth Amplifying



Something is off and you cannot name it.



Your output is faster than it has ever been. Your folders are organized. Your agents have names. The work that used to take a day takes an hour. And quietly, in a place you do not talk about on LinkedIn, you suspect it is still generic.



It reads competent. It reads on-brand. It also reads like it could have come from any other operator in your space who built the same folder system this quarter. You thought the architecture was the answer. The architecture is built. The output is still drift.



You do not know what is missing. You do not know what to ask for. You are not behind. You are standing in front of a piano.



The piano in the house



A lot of people had a piano in the house growing up. Very few of them could play it.



We had one too. It sat in the front room of my parents' house for years. The instrument was there. The bench was there. The lid opened. The keys worked. None of that made anyone in my family a musician.



I was a senior in high school the night I figured out what a piano was actually for. A few of us had come back to my friend Scott's house after closing down the pizza place where one of the guys worked. We had custom pizzas and cans of Coke and nowhere to be. Scott sat down at his family's piano and started playing the theme song to Cheers. None of us knew he could play. A roomful of teenage boys on a Saturday night, singing where everybody knows your name. He never played for us again. I have never forgotten it.



The instrument had been in his house his whole life. The instrument was not the music. Scott was the music. The piano was just what let him give it to us.



This is the part of the AI conversation almost nobody is having.



The folder system is the piano. The orchestrator, the specialists, the file routing, the persistent memory. All of it is the instrument. It is real. It is capable. It is sitting in your office right now if you got to Level 4.



The score is what you play on it. The score is the doctrine. The score is the set of beliefs and operating rules your agents are protecting every time they produce work. Without the score, the instrument is furniture. Beautiful furniture. Expensive furniture. Furniture all the same.



The ICM is the instrument. Doctrine is the score.



That is the line the rest of this piece pivots on. I want you to feel it before I name it again.



Why your SOPs are not the score



Here is where most of the operators reading this are going to nod and close the tab. I already do this. I have my SOPs loaded into the project.



You do not. And the distinction is the whole conversation.



Picture two agents sitting next to each other. Same model. Same architecture. Same access to the same CRM. The prospect on the screen is a name you have been chasing for three weeks. The qualification call just ended. The agent's job is to draft the follow-up.



The first agent has your SOPs loaded. Subject line formulas. Paragraph cadence. The opener you like. The signature you use. The constraint that says no em dashes and no exclamation points. The agent writes a clean follow-up in your voice. It is on-brand. It is the right length. It would pass any per-asset review you put it through.



The second agent has your SOPs loaded too. And underneath those SOPs, it has your doctrine. The rule that says we do not follow up on prospects who failed the qualification frame. The rule that says we do not deepen relationships that violate the ICP, no matter how warm the conversation felt. The rule that says a beautifully written wrong move is more expensive than a missed one, because it commits us to a customer the system was built to refuse.



The second agent reads the call notes and stops. It does not draft. It surfaces a flag instead. This one failed the frame. The follow-up the SOP is about to fire would deepen the wrong relationship. Confirm before we proceed.



The first agent is skilled. The second agent is right.



SOPs tell the system how to do the work. Doctrine tells the system what the work is for, and which work is not worth doing at all.



Most operators stopped at the first agent and called the job done. The output looked good. The output kept coming. They never noticed the system had no opinion about whether the output should exist. SOPs make the agents skilled. Doctrine makes them right.



What took me a decade to see



I did not know I had been building it.



For thirteen years I sat inside paid media campaigns. I watched ad accounts and CRMs and the gap between what marketing promised and what sales actually closed. I wrote diagnoses. I made calls about what to fix first.



I don't remember the client. I remember the feeling. I was walking through another account, another CRM gap, another campaign that looked busy but wasn't connected to revenue. Halfway through the diagnosis I realized I wasn't deciding anymore. I was following an order.



The client had come to me for paid media. The one before had come for SEO. The one before that, the same. I had been taking the order and getting to work. I had stopped asking whether the order was the actual problem.



So I stopped. I started asking a different question instead. Do you know why your customer buys from you? And almost every time, the answer was no. Not a sharp no. The kind of no that sits in the air for a second while the person on the other side of the desk realizes they have been running a business for fifteen years on an answer they never wrote down.



That question became a rule. I do not take the order at face value anymore. Not paid media. Not SEO. Not the brief they walked in with. The brief is almost never the problem. The problem is upstream of the brief, and the operator usually does not know it yet.



It had been a rule the whole time. I had been treating it as judgment. It was doctrine. The repetition had been the proof. I had been the last one to notice.



That was when I started writing things down. Not framework names. Not slogans. The actual rules. Why diagnosis comes before tactics. Why no client gets a creative brief before the customer reality, measurement layer, and strategic constraint are clear. Why nothing leaves the building without governance. Why revenue has to be the number that eventually proves whether the work was real.



I never sat down to write a doctrine. I had been writing it for years and did not know. Seventy-five episodes of a podcast with my co-host Tom Nixon, talking with operators and clients and peers about the work. The beliefs spilled out in conversation. The vulnerabilities spilled out in conversation. The rules I had earned by repetition spilled out in conversation. None of it was organized. None of it was named.



Then I started mining the transcripts.



I dumped the episodes into AI and asked it to find the patterns. What I was looking for was content ideas. What I found was doctrine. The same rules I had been saying out loud to a microphone for three years. I had been the last one to hear them.



That is the part of this story I want you to sit with for a second. The doctrine was already there. AI did not generate it. AI revealed it. The amplifier the manifesto named two essays ago is not just an output amplifier. It is a recognition amplifier. It made me visible to myself.



Then I found the folder system.



I watched what people like Jake at Clief Notes were doing with persistent context and agent architecture, and the air left the room. I had spent a decade preparing for the moment I would have somewhere to put it.



Most operators are climbing the ladder in the opposite order. They are installing the instrument first. They are watching demos of other people's pianos and buying the same model. The instrument arrives. They sit down. They realize they do not have anything to play.



The order matters. Context precedes architecture. The manifesto pointed at this. The 5 Levels mapped the climb. This piece names what you climb toward: a doctrine strong enough to become infrastructure.



The rules a system has to honor



There are three lines I keep coming back to. They are not slogans. They are the rules a system has to honor before it produces work worth shipping.



Coherence before creativity.



If your underlying logic does not line up, AI does not fix it. AI runs the incoherence at higher volume with better grammar. The manifesto named this. It is still true at Level 4. It will still be true at Level 10.



Diagnosis before tactics.



The glitch in a marketing system is almost never where the operator thinks it is. It is upstream. It is in how the customer is defined, or how the data flows, or how the story is told, or how the close-loop is wired. An agent told to write a better ad without a doctrine that demands diagnosis first will write a prettier version of the wrong thing.



Context before architecture.



This is the one this piece exists to name. The folder system is downstream. What lives inside the folders is upstream. If the upstream is empty, the downstream produces drift. If the upstream is sharp, the downstream produces leverage.



Three rules. Two of them earned the second appearance. The third earned the first.



Doctrine is not a brand guide. It is not a folder of examples. It is the operating law underneath the work. Who we serve. What we refuse. What must be true before we act. What proof matters. What the system is never allowed to optimize at the expense of the business.



What changes when the score shows up



There is an operator I am working with right now. Services business. Mid-market. Twenty plus years in. He read the manifesto. He read the 5 Levels. He showed up at Level 3 already.



He had agents. He had a folder system. He had done the climbing. He thought he had a marketing problem.



We ran the diagnostic. He did not have a marketing problem.



He had a sales problem.



The way he sold to a prospect was nothing like the way his team sold to the same prospect a week later. He sat down with people and listened. He took a pain inventory. He used no acronyms and no feature lists. He helped the prospect see the shape of the problem before he ever mentioned a service. By the end of a first meeting, the prospect felt understood in a way three other firms had not managed.



Then the handoff. His team would walk in with a feature list and a thirty-six-page proposal. The prospect who had just heard the owner help them think about their business would now be asked to read a document they could not read. My partner Tom Nixon named the pattern early. Selling simplicity, delivering complexity. The brand promise was being broken in the second meeting, every single time.



Deals were falling apart at the handoff. He did not know why until the diagnostic surfaced it.



He had been protecting the way he sold for twenty years. He had never written it down. None of it was protected. The agents he had stood up could not hold a register he had never named.



Now we are building the doctrine. Not the SOP for the follow-up email. The doctrine underneath the sales motion itself. What he listens for in the first ten minutes. The frame he uses to make the prospect's situation make sense to them before he ever opens a deck. The reason he refuses to send a proposal in the first meeting. The reasons he walks away from deals his team would chase.



When the doctrine is written, his sales team will sell the way he sells. The agents will protect the way he sells. The handoff will stop bleeding.



Same instrument. Different output. The agents will not have changed. The score will have.



The architecture you have already seen



Embed: inbox/collideascope-os.png



In my system, there is an orchestrator. There are specialists with defined roles, constraints, and judgment boundaries. There is a doctrine layer the team loads before producing. We call it the Brand Guardian. It is the operating law every specialist is held against. There is a verification step the producer is never allowed to close on its own work. There is a memory layer that stays human-readable so the next operator can open a file and understand exactly what was being protected.



The names matter less than the order. Mine has an orchestrator named Duke who routes the work before the work begins. The names are mine. The pattern is portable.



A note for the builders, because this is the part I have to clarify almost every time it comes up. The doctrine layer my team uses is one thing. The MCP I built is something else. The MCP is how I deliver doctrine into a client's AI environment so their internal teams can produce work that holds the brand without my team in the room. Same doctrine. Different surface. The reason both live behind controlled layers is the same reason a coach does not hand his playbook to the opposing team. The doctrine is the asset. If I give it away, I give away the system that produced it.



The score is enforced at the door, not after the fact. The system assumes the producer is the worst auditor of the produced. The memory lives in folders, not in a vector database, so the doctrine stays readable to a human a year from now.



That is the instrument. None of it matters without the score.



What you actually climb toward



Most of the AI ladder discourse is about building more. More agents. More automations. More overnight workflows.



That is not the path. Or it is, but only after the harder path.



The harder path is naming what you have been protecting all along. Most operators have a doctrine in their head. They built it by repetition. They have never written it down. They are about to install an instrument and discover they do not know what to play.



Do not do that.



Most operators do not need more agents yet.



They need a score.



They need to name the rules they have already earned.



Then, and only then, they should build the system that protects them.



The strongest AI systems in the next few years will not belong to the operators with the fanciest orchestrators. They will belong to the operators with the clearest philosophy embedded inside them. Mark Schaefer has been saying a version of this for years. Technology amplifies what already exists. It does not replace the need for humanity, originality, or a point of view.



AI systems without doctrine will produce competent mediocrity at scale.



AI systems with doctrine will produce something nobody else can.



Coherence before creativity.



Diagnosis before tactics.



Context before architecture.



That is the system worth amplifying.



So I want to leave you with the question I had to ask myself before I knew there was a question.



If I cloned your stack tomorrow. Same agents. Same prompts. Same file structure. What would still make your work unmistakably yours?



If the answer is nothing, the work in front of you is not building more agents.



The work in front of you is naming the doctrine you have already earned.



Then go build the system that protects it.



------



david vogel\Curtis Hays - Systems Worth Ampli\AI Isn’t Your Prophet It Might Be Your Amplifier.md



AI Isn’t Your Prophet. It Might Be Your Amplifier.



AI Isn’t Your Prophet. It Might Be Your Amplifier.



But only if you’ve built something worth amplifying. Curtis Hays Mar 02, 2026



I need to say something that might be uncomfortable.



You can generate a full marketing campaign in about 45 minutes now. Copy. Images. Landing pages. Email sequences. Ad variations. All of it.



And here’s the part nobody wants to say out loud. It will look professional. It will sound competent.



And it will not work.



Not because the AI failed. Because the system underneath it was never aligned in the first place. You’re just running that misalignment at 100x speed now. With better production value.



The appeal is real. I get it.



Look, if you’re a founder, a CEO, a marketing leader, the promise of AI is almost impossible to ignore. Not enough time. Not enough budget. Not enough people. And here comes this thing that says: I’ll write your ads. I’ll score your leads. I’ll personalize your emails. I’ll analyze thousands of customer comments in seconds.



It feels like the answer. I understand why people grab onto it.



But there’s a cost hiding behind that promise. And it doesn’t just add up. It compounds. Every quarter you lean on this without a foundation, the problem gets deeper and the price gets steeper.



Here’s the math most people skip.



AI is an extraordinary amplifier. But if your fundamental marketing system is broken, if you don’t actually know your customer’s internal reality, if your messaging says one thing on the website and something different in the sales deck, if your sales team is rewriting the pitch before every meeting because the marketing doesn’t match what they’re hearing in conversations. All AI does is help you do that wrong stuff faster.



You burn through money faster. But the emails look great.



The mirror problem



Most companies, probably without realizing it, are doing what we call Mirror Marketing. Their homepage says “We are...” Their ads say “Our product does...” Their decks lead with company history and awards. Their AI tools just polish that mirror until it gleams.



But the mirror is still pointed inward.



What actually moves cost curves without increasing spend is the opposite. Looking out at the customer’s world. Speaking to their reality. Their tension. Their language. Not yours.



AI doesn’t know the difference. It generates from the statistical average of everything in your category. And the average is exactly where revenue goes to die.



The Chaos Tax



Here’s something that changed how I think about this.



You probably know what you pay for a lead. You might know your close rate. But almost nobody I talk to knows what they pay for a lead that actually turns into revenue. Not a form fill. Not a demo request. A lead that becomes a customer.



The gap between those two numbers is what we call the Chaos Tax. It’s the most expensive line item that never shows up on your P&L.



And AI makes it worse. Not because AI is bad. Because AI is indifferent. It amplifies whatever system you give it. If the inputs are misaligned, wrong customer psychology, wrong narrative, wrong measurement infrastructure, AI just amplifies the misalignment. At scale. With perfect grammar.



So what does AI actually need?



Not a better prompt. A foundation. And the order matters because each layer depends on the one before it.



Psychology first. Understanding why people actually choose. Not features. Not price comparisons. Identity protection. Fear. Aspiration. The stuff that never shows up in your click-through data. AI gives you the average. Revenue lives in the specific.



I used to skip this step. I came from the data side. I wanted to go straight to what I could measure. It took me longer than I’d like to admit to understand that the measurable stuff only works when the psychology underneath it is right.



Then data. Not spreadsheet data. Excavated customer truth. The pause before someone names their real fear on a call. The tension between what a customer says they want and what their behavior reveals they need. AI can process volume and surface word frequency. It can’t hear what’s underneath the words.



Then story. And here’s the trap. You can generate an entire messaging framework in 20 minutes now. Mission, vision, value propositions, taglines. It’ll be grammatically flawless. Tonally appropriate. And completely interchangeable with your three closest competitors. Because AI generates from the average of all messaging in your category. If your brand story could have been written for anyone in your space, it’s not a story. It’s furniture.



Then community. AI can simulate warmth. It cannot generate belonging. Belonging requires risk. Vulnerability. The possibility of rejection. The most human company wins. And AI is not human. I resisted this idea for a long time. I’m a systems guy. But the data kept telling me the same thing. People buy from people they feel connected to. No algorithm changes that.



Then owned audience. AI makes it trivially easy to produce more content for social platforms. More posts. More videos. More carousels. Faster, cheaper, higher volume. And every piece of that content builds on someone else’s land. You’re producing more stuff, faster, on platforms you don’t control. Volume isn’t the problem. Ownership is the problem.



Then measurement. Closed-loop. Revenue-connected. Not dashboards that tell one story while the actual revenue tells a different one. AI is being used for lead scoring, automated follow-up, chatbot qualification. All useful if the definitions underneath are correct. But if your MQL definition is wrong, AI just scores wrong leads faster.



That’s the system. Psychology. Data. Story. Community. Audience. Measurement. In that order. Each layer protecting the one before it.



Psychology.



Measurement.



Remove any one and the others weaken.



The resolution



AI as a false prophet, this belief that tools can replace understanding, is the most expensive seduction in marketing right now.



But AI as an amplifier, applied to a system that actually works? That’s where it gets genuinely powerful.

#### When the foundation exists, AI can:

Enforce your brand voice at scale. Because you’ve defined what your voice actually is. Through real excavation and real narrative architecture. Not a brainstorm on a whiteboard.



Enforce your brand voice at scale. Because you’ve defined what your voice actually is. Through real excavation and real narrative architecture. Not a brainstorm on a whiteboard.



Generate content that sounds like you. Because constraints exist to prevent drift.



Generate content that sounds like you. Because constraints exist to prevent drift.



Accelerate research synthesis. Because you know what questions to ask before AI summarizes the answers.



Accelerate research synthesis. Because you know what questions to ask before AI summarizes the answers.



Optimize campaigns faster. Because your measurement infrastructure captures the right data and feeds it back.



Optimize campaigns faster. Because your measurement infrastructure captures the right data and feeds it back.



Personalize at scale. Because you’ve defined psychological clusters, not just demographics.



Personalize at scale. Because you’ve defined psychological clusters, not just demographics.

#### What AI cannot do:

Feel your customer’s identity tension.



Feel your customer’s identity tension.



Know what your customer is afraid to lose.



Know what your customer is afraid to lose.



Build belonging.



Build belonging.



Create the kind of human vulnerability that earns trust.



Create the kind of human vulnerability that earns trust.



Replace lived experience with statistical probability.



Replace lived experience with statistical probability.



Generate gravity from nothing.



Generate gravity from nothing.



AI is agnostic. The system determines the outcome.



If you amplify coherence, you get compounding growth. If you amplify incoherence, you get compounding waste. Same tool. Different results. The variable is what you built before you turned it on.



The question was never “should we use AI?”



The question was always: do we have a system worth amplifying?



Every quarter you operate without that system, the Chaos Tax compounds. Your CAC rises. Your messaging fragments. Your sales team drifts further from your marketing. Your AI tools amplify the incoherence and nobody can figure out why the numbers aren’t working because the dashboards all look fine.



It’s not a cliff. It’s a slope. And the slope gets steeper.



The tool is not the problem. The tool is not the solution.



The foundation is the whole conversation.



Coherence before creativity. Diagnosis before deployment. Meaning before media. Revenue before reach.



That’s the operating logic.



And no algorithm changes it.



------



david vogel\Curtis Hays - Systems Worth Ampli\Outsource the Typing, Keep the Thinking.md



Outsource the Typing, Keep the Thinking



Every conversation I'm in about AI advantage treats it like a tools problem.



Better prompts. Better models. Better workflows. Pick the right stack, wire it up right, and you pull ahead.



That's the conversation. And it's mostly wrong.



Your competitors have the same tools you do, and the same public data. NotebookLM, deep research, competitive analysis — none of it is yours, because all of it is theirs too. Anything every operator can buy or pull off the open internet can't be the thing that sets you apart. When everyone can pull the same market intelligence in thirty seconds, the intelligence isn't the moat. It's the floor.



The moat is what they can't get to. And the deepest part of it isn't even the data. It's the thing that produced the data.



Writing isn't typing



My co-host Tom Nixon said something on the show this week that reframed the whole thing for me. We were talking about why generic AI content feels empty, and he stopped and made a distinction I haven't been able to put down since.



Writing isn't typing.



Writing is the thinking you do about the topic — for an hour, a week, ten years. That's the writing. By the time you put it on pixels, that part's just typing. Tom's line was: keep the thinking to yourself, outsource the typing only.



Run that through the AI conversation and it turns the whole thing around. Most operators are racing to hand the AI more of the work. The whole pitch of the tools is that they'll do the thinking and the typing both. Tom's flipping it. The thinking is the only part that was ever yours. The typing was never the asset.



Which is why your conversations are the moat. Not because they're transcripts nobody else has — though they are. Because they're where your thinking already happened. The transcript is the residue of it. The decision you talked yourself into on a client call, the read you gave a deal in a debrief, the thing you finally said out loud in the last ten minutes of a two-hour session — that was the thinking. It already occurred. It's sitting in the recording, waiting to be recovered.



What's actually yours



There's a category of data that is completely asymmetric. Nobody else was in the room. Nobody else was on that call. Nobody else heard what your client said when they stopped performing and started being honest.



Your meeting transcripts. Your sales call recordings. Your client debrief notes. Your team's voice memos after a hard engagement. The conversations you have in your day that exist nowhere else and belong to no one else.



I was guilty of not capturing this for years. I sat across from clients and listened well. I made good notes. I carried the insight in my head into the next session and used it. The problem is that anything I carried in my head died when I moved on. The thinking happened — and then it evaporated. It didn't compound. It didn't train anything. It didn't travel. It was experience that stayed private instead of becoming infrastructure.



That's the first category of asymmetric data. There's a second: the thinkers whose work you've spent years taking in.



The thinkers you've actually metabolized



Your worldview isn't only what you think. It's the synthesis of the people you've genuinely absorbed.



Tom named this on the show too. Our doctrine isn't just our own thirty years of opinions — it's Mark Schaefer, Brian Clark, Gini Dietrich. People we've interviewed, read, argued with in our heads, and adopted philosophically until their thinking became part of how we see. We stand on the shoulders of giants. The difference now is we can capture which giants, and how we metabolized them, instead of letting it stay vague.



That's asymmetric too. A competitor can read the same Schaefer book you read. They cannot reconstruct which ideas you took, which you rejected, and what you did with them inside your own work over a decade. That synthesis is yours. It's another layer of human data nobody can scrape, because the scraping already happened — in your head, on your terms.



So the raw material of your doctrine is two things. The conversations you've had. And the thinkers you've truly absorbed. Both are residue of thinking. Both belong only to you.



What fills the vacuum if you don't



Tom put this next to something every brand person already knows. Your company is going to have a culture whether or not you take an active part in creating it, documenting it, policing it. Walk away from it and one forms anyway — just not the one you'd have chosen.



AI is the same. If you don't form the doctrine, you don't get a blank system. You get one that fills the gap from somewhere else — the model's training data, the conventions baked into every borrowed template, the internet's averaged opinion of what an operator like you probably believes. The thinking still gets done. It just gets done for you, by a machine running on everyone's defaults instead of your convictions.



That's the actual choice. Not "build the moat or don't." It's "do your own thinking, or inherit the average's." The vacuum doesn't stay empty.



Underneath the summary



When operators do capture transcripts, they extract the surface. They ask the AI to summarize what was discussed. They pull the action items. That's useful. It's also the shallowest possible return on the data.



There's a question underneath the summary. Not "what did this person say?" but "what does this person's pattern of decisions tell me about what they actually believe?"



I work with a home care operator named Mario. The surface read on his transcripts was clear — census, referral sources, staffing ratios. Standard operational concerns. But the pattern across a dozen conversations told a different story. Every time a decision carried reputational risk, Mario slowed down. Every time a decision was defensible, even if the economics were softer, he moved faster. He consistently chose the option that reduced his exposure to being blamed, even when the better economic option was on the table.



Mario doesn't decide based on upside. He decides based on downside protection.



That's not in the summary. That's in the pattern. And when I understood it, everything changed — the framing of options, the order I put choices in front of him, which risks I named first. You only see that if you ask the data the right question, and you only have the data if you captured the thinking instead of letting it evaporate.



Where to start



If this feels like a lot, the first move is older than any of the tools, and you can do it today.



Keep one notebook.



Not a system. Not an app with folders and tags and a filing structure you'll spend a weekend setting up and never touch again. One book — paper if you like the feel of it, a single digital note if you don't. Everything goes in the next blank space: the thought in the car, the line a client said that you can't shake, the read you got on a deal, the half-idea you'd normally lose by lunch. No judging it on the way in. No deciding whether it's a good idea or a bad one before it lands on the page. The friction of "where does this go?" is what kills the habit — so it goes nowhere except the next open spot.



Two rules hold it together.



No to-do lists. The notebook is for thinking, not for getting things done. The minute you let tasks in, they crowd out the part that matters and the book becomes another inbox. Keep the chores on a scrap you throw away.



And review it constantly. This is the whole engine — not study, not memorization, just flipping back through it in line at the coffee shop, on the couch, between calls. That's where it pays off. Ideas you wrote down weeks apart start to touch each other. A read you had on a client in March turns out to explain a pattern you spotted in June. The connections don't live in any single entry. They surface when you keep passing back over the whole thing, and you only get to keep doing that because none of it evaporated.



This isn't a productivity hack someone invented last year. It's the commonplace book — the same practice behind Da Vinci's six thousand pages, behind Darwin and Mark Twain. Da Vinci wrote a line at the start of one of his own that the artist Perry Daniels, who keeps the habit today and calls it the Grail Method, saved into his: "this is to be a collection without order, taken from many papers which I have copied here, hoping to arrange them later each in its place." That's the permission. It doesn't have to be tidy to be the most valuable thing you keep.



One honest tension, because Daniels names it and I'm not going to dodge it: he's against the structured second-brain — the Notion database, the elaborate filing system. And he's right about the failure he's pointing at. When structure becomes the place ideas go to die — sorted into folders so clean you never open them again — it kills exactly the connection-making the notebook is for. The structure earns its keep only when it does the opposite: when it helps you retrieve and collide what you captured, instead of burying it. The notebook is the raw, unsorted layer. The structure, if you add one, is just there to let you pass back over more of it than your hands could ever flip through.



Because that's the move underneath all of this. Once you've got the corpus — the notebook, or the year of transcripts and voice memos behind it — you don't ask it for a summary. A summary plays back what you already know. You ask it for the pattern across everything. The Mario read didn't come from one call. It came from a dozen, asked the right question. Same one I ran on my own conversations before I ever pointed it at a client — I loaded my own calls and debriefs and made the AI mine me, and it handed back my worldview clearer than I'd have written it cold.



The Grail Diary



If you want to do that at scale, I built the thing I wished I'd had for years. It's called the Grail Diary — the commonplace book, rebuilt so a machine keeps it with you. One notebook. Everything goes in the next blank space, no judging it at the door, no to-do lists allowed in. What the machine adds isn't a verdict — it's reach. It reads back over more of the corpus than your hands could ever flip through and lays the pieces out in front of you: here's the line from March, here's the one from June, here's the read you gave that deal. It surfaces; you connect. It will not tell you what your pattern means, on purpose — the moment a machine names your belief for you, you've handed back the one part that was yours. Naming it is still your move. The mining I described above — pointing the AI at the whole pile and asking for the pattern, not the summary — runs on one discipline: when a pattern and a thing you said about yourself disagree, trust the pattern, and never let it hand you a belief you didn't demonstrate. Empty beats fabricated, every time. I'm putting the Diary out in the open for anyone who wants it. Grail Diary — link to come once the repo's live. But you don't need it to start. You need the notebook and the habit of reading back over it.



Public data is what everyone has. The conversations in your day, and the thinkers you've actually absorbed, are what nobody else can get to. That gap is the moat.



The thinking was always the asset. The only question is whether you're keeping it — or letting the machine do it for you.



https://github.com/chays77/grail-diary



The system is a plain folder of Markdown files, a Node.js build script, and a single HTML template — all orchestrated by a small set of “skill” instruction files that tell an AI agent how to operate it. It is built in three layers:



configuration



agent workflows



------



1. Configuration layer



grail.config.md



— the single root config, written in YAML inside a Markdown code block. It holds:



(your name, for diary title pages)



journal_root



— where all journals live (default



daybook_slug



— the always-on catch-all journal



ingest_candidate_cap



— max candidates surfaced per ingest batch (default 12)



todo_target



— file where action items get routed



backcatalogue_sources



— existing note folders that the migration walker reads from



sticky_notes_pen



— path to the “not yet filed” pile



journal_types



— an extensible list (Project, Memory, Reflective, Gratitude, Reference)



Every skill file resolves paths at runtime by reading this config. Nothing is hardcoded.



journal.config.md



— one per journal, produced by the Phase 0 setup interview. It is the authoritative filter. It contains:



Journal metadata (name, slug, type, creation date, framing primer)



list (label, description, priority, shape) — the only labels the AI may cite in a Filter Line



— the threshold for surfacing vs. letting pass (a prose rule)



Does NOT belong



— explicit exclusions



Voices that trigger capture



— whose words count



ingest_sensitivity



(generous / conservative)



seeds_enabled



(boolean, per journal)



— optional motto shown on the diary’s title page



These two config files make the system fully declarative. The agent applies rules, never invents them.



------



1. Agent workflows (the     “skill” files)



The system is a set of plain-text instruction files (



grail-listener.md



grail-capture.md



grail-criteria-review.md



) plus a governing



. They are meant to be loaded into an AI agent (Claude Code or any agent that can read a folder and edit files). They define three phases:



Phase 0 — Listener (



grail-listener.md



A structured 9‑question interview that excavates a journal’s criteria from the owner in their own words. It:



Asks one question at a time, forbids the AI from proposing criteria or interpreting answers



Records answers verbatim or with explicit owner-confirmed light edits



journal.config.md



, scaffolds the journal folder (



_candidates.md



_session.md



, optionally



Runs a self-check that every criterion traces to the owner’s words before writing



Phase 1 — Capture (



grail-capture.md



The capture discipline. It defines the



Filter Line



as the only allowed surfacing message: a verbatim quote and the matched criterion label. It implements four entry points:



(owner says “Grail this”) → writes straight to



(session watch mode) → surfaces candidates one at a time as material clears a criterion + the bar



(process a transcript) → reads the full source, collects all matches, ranks them, writes up to the cap into



_candidates.md



; the owner later drains the file with



keep/refine/drop/context



one candidate at a time



(walk old notes) → walks the owner’s existing archives or sticky notes one note at a time against a target journal’s criteria, with



The phase also enforces Grail Rule 2 (no to-dos in the diary), defines the render‑ready entry shape (thin frontmatter, single unstructured body), handles duplicate detection and theme entries, and manages session state via



_session.md



Phase 1.5 — Criteria Review (



grail-criteria-review.md



A tuning pass the owner invokes after ingest batches. It reads signal only from the surfacing layer (candidate volume, overflow flags, drop patterns from the current session) and lets the owner sharpen, add, or tighten criteria — always in their own words. It never reads the diary entries themselves (that would be the agent connecting).



These skill files are the “software.” The agent carries them out by reading/writing Markdown files, exactly as instructed.



------



1. Rendering layer



build-diary.js



— a plain Node.js script with zero dependencies. Run as:



node build-diary.js my-book



Scaffolds the HTML diary from



diary-template/index.html



on first run.



Reads all confirmed entries from



journals//entries/\*.md



, parses their frontmatter and body.



Reads the journal’s config (



journal.config.md



) and the owner name from



grail.config.md

#### Injects three data blocks into the HTML template as JavaScript constants:

(array of entry objects),



(title page metadata), and



(the verbatim capture criteria, bar, and priority lens).



The resulting HTML file lives at



journals//diary/index.html



and opens directly in a browser with no server.



diary-template/index.html



— a self-contained, vanilla JavaScript/CSS “flippable book” with:



A closed leather cover that swings open on click (CSS 3D transforms)



Left/right page leaves with aged-paper textures, foxing, edge darkening, and a center crease



A fixed front‑matter opening: title page (left) and the rules for capture verbatim (right)



Entry scraps laid out with a max of 2 per leaf; length‑based sizing (short quotes render larger, italic, with a gilt rule)



Shuffle‑on‑open: every load or reshuffle re‑deals unpinned scraps using Fisher‑Yates



Pinning: clicking a wax‑seal icon pins a scrap to its current spot; pins persist in



localStorage



keyed by journal slug. Pinned scraps hold their position while the rest shuffle.



Optional theme sketches: hand‑drawn margin art mapped to criterion labels, placed only in the bottom‑right corner of right‑hand leaves.



Full keyboard navigation, swipe gestures, reduced‑motion support, and responsive single‑leaf fallback for narrow screens.



The renderer is a pure presentation layer — it never mutates source



files. The source of truth remains the Markdown entries.



------



1. The guardrails in the     architecture

#### Every design choice enforces the “system surfaces, human connects” boundary:

No auto‑promotion



— ingest candidates never become entries without explicit human keep/refine



No rejection logs



— dropped candidates disappear; the AI’s guesses don’t accumulate into a shadow opinion



Cap overflow flagging



— if an ingest finds more than the cap, the real count is reported; silence would be a hidden filter



No auto‑invoked criteria review



— the owner must call for tuning



Seed mechanics



— raw material that cleared the bar but isn’t ready sits untouched, revisited later by the owner



The entire diary renderer has no search, no clustering, no “related” sections



— only shuffle, pin, and raw layout



The system is built as a set of plain files and clear instructions so that the thinking is always done by the human — once during setup, and again every time they flip through the diary. The AI is just the filing clerk.



------



david vogel\Curtis Hays - Systems Worth Ampli\The 5 Levels of AI Mastery.md



The 5 Levels of AI Mastery



You've been using ChatGPT for six months. Maybe a year. You're getting real work out of it. And somewhere underneath that, quietly, you suspect you're not getting what everyone else on LinkedIn seems to be getting.



You watch other founders post their stack. Their workflows. Their overnight agents. You read it and something doesn't add up against what you're actually doing at your keyboard, which is mostly typing into a chat window and hoping the next answer is better than the last one.



You're not behind. You're stuck. And there's a reason for it that nobody is saying out loud.



The reason is that there's a ladder. Five rungs. And almost everyone using AI right now is standing on the first one without knowing the other four exist. The hype on your feed is being written by people on rung three and four describing their view, while you're on rung one wondering why the view doesn't match.



I wrote a few months back that AI is your amplifier, not your prophet. That if your underlying system is coherent, AI compounds growth, and if it isn't, AI compounds waste at 100x speed with better grammar. I stand by that. What I didn't say is where you actually start climbing, and what each rung up the ladder actually looks like.



That's what this is. Five levels of AI mastery. Most people are stuck on the first one. They don't know it. And it's costing them every month they stay there.



Level 1. The Intern With Amnesia



This is where almost everyone is right now.



You open ChatGPT. You ask a question. You get something useful. You ask another. After ten or twenty back-and-forths, you've gotten somewhere real. You feel like you finally have an AI that gets you.



Then you close the tab. Or you come back the next morning and start a new chat. And everything you built is gone.



So you do the thing I keep watching people do. You stay inside one chat for a year. Hundreds of exchanges. Scrolling for context. Terrified to close it because the memory you built lives there and nowhere else.



I talked to someone last week who's been working in the same chat for thirteen months. Building a report. Hundreds of messages deep. She's not afraid of AI. She's afraid of losing what she taught it.



That's Level 1. Think of it like an intern.



Brilliant. Speaks twelve languages. Can code. Solves problems faster than any human you've hired. You have a great first day with this intern. You walk them through the company, the clients, what good looks like. You feel productive.



The intern goes home. Comes back the next morning. Forgot everything.



Same skills. Same intelligence. Zero memory of you.



That's the problem with basic chat. The AI is passive. It waits for you to ask. And every time you start a new conversation, you're training the intern from scratch.



You can learn prompting here. You should. But prompting alone won't save you. Because no matter how good your prompt is, you're going to type some version of it again tomorrow.



Level 2. The Assistant That Remembers



This is the most important shift in the ladder. If you do nothing else after reading this, do this one.



Inside ChatGPT and Claude there's a feature called projects. Gemini calls them gems. They look like folders. They're not folders.



A project lets you write your prompt once. Define the role. State the objective. Load the context. Add source files. Brand voice rules. Past work. Examples of what good looks like. Then every chat you start inside that project loads all of it automatically.



The intern stops having amnesia.



Now when you talk to your AI, you don't open with a 400-word prompt. You open with natural language. "Let's research this company." "Draft the follow-up." "Pull the patterns from these three calls." The context is already loaded. The persona is already built. The constraints are already in place.



Here is what that looks like for me. I have a project called Paula. Her job is prompt engineering. Loaded into Paula are the prompting frameworks I trust, examples of strong prompts, and the constraints I want her to honor. When I open a chat with Paula, I do not type a setup paragraph. I type one line. "Paula, build me a prompt for audience research for a marketing agency that also does revenue ops. We will use it with ChatGPT deep research." Paula comes back with a structured prompt that runs to the right length, in the right format, against the right model, every time. Base ChatGPT will give you a serviceable answer to that same request. Paula gives me a prompt I can actually ship.



This is also where you start loading expertise you trust into your assistants. We recently had Will Leach from MindState Group on Bullhorns & Bullseyes. His whole framework is about the psychological mindstates that actually drive customer behavior. The kind of thinking that takes years to internalize. Loaded into a project, that framework becomes context your AI applies every time you ask it about a customer. You stop getting generic. You start getting Will.



The shift from Level 1 to Level 2 is the shift from interviewing a new intern every day to having an assistant who actually knows you.



Most people skip this and try to jump straight to the fancy stuff. Don't. Spend real time here.



Level 3. The Coworker With File Access



Level 3 is when AI stops living inside a browser tab.



Claude Desktop and a few similar tools opened this up. You point the AI at a folder on your computer. Now it can read your files. Write to them. Modify spreadsheets. Update Word documents. Reorganize a messy downloads folder. Create new files where it needs to.



You stop uploading. You stop downloading. You stop dragging files in and copy-pasting outputs back. The AI is working alongside you, not across a glass wall from you.



Here is what that means in a real workday. I got off a call with a client a few weeks ago. Hour and a half. They wanted to pivot in a couple of directions. Three different deals coming out of one conversation. Normally that turns into an hour of cleanup. Open HubSpot. Create the deals one by one. Type the notes. Build the follow-up tasks. Try to remember everything they said.



I did none of it. I told my AI what happened on the call. It went into HubSpot, created the three deals, set the to-dos, and filed the call notes. I reviewed it and moved on.



That is the Level 3 jump. Not faster typing. Not a better prompt. The friction of moving information between you and your tools collapses, because the AI is allowed to touch the tools.



This is the orange belt. Useful. Real. Most people who get here feel a meaningful jump in productivity. But it's still one-to-one. You and the AI. One task at a time.



The bigger shift is next.



Level 4. The Orchestrator



I talked to a builder recently who runs an AI platform serving billion-dollar companies. He told me he has thirty-one AI employees built. He doesn't use most of them.



That is the wall before Level 4. You can build a stable of agents and still be the bottleneck, because you are the one routing every request by hand. Project to project. Tab to tab. Trying to remember which assistant knows which thing. The agents are real. The orchestration isn't.



Level 4 is when you stop talking to a single assistant and build a team with a router on top.



There's an orchestrator. Mine is named Duke. He's the one I talk to. He doesn't do the work himself. He routes it. When I bring him a sales question, he hands it to Buck. When I need brand strategy, he hands it to Doc. When something is messy and needs to be filed, he hands it to Betty. Each agent has its own context, its own role, its own job.



The whole team lives as a folder structure on my computer. Plain text files. Instructions. Context. Each specialist is a few files. The orchestrator is a few more. The work moves between them through commands, not clicks.



This is the brown belt. And it's where AI stops being a tool you use and starts being an operating layer for how the business actually runs.



It's also where the foundation conversation from the manifesto gets real. Because at Level 4, every agent is loading context that you defined. The customer psychology. The data. The story. The brand voice. The measurement logic. If those layers are coherent, the team amplifies coherence. If they're incoherent, the team amplifies incoherence faster than any single chat ever could.



The architecture is not the point. What the architecture protects is the point.



Level 5. The Factory



Level 5 is when the team runs without you.



You set the work. You go to sleep. Fifteen agents are running tasks while you're not at the keyboard. You wake up to finished output. You review it. You ship the good. You send the bad back.



I'm not at black belt yet. I don't really have much of a need to be at this point.



A few things to know before you chase it.



Tokens cost money. A team of agents running overnight on a complex project can burn through hundreds of dollars while you sleep. Sometimes that's worth it. A team of humans would have cost ten times more. Sometimes it isn't. You're optimizing the wrong thing.



And there's a deeper risk. The human-in-the-loop is the thing that keeps the work pointed at something true. Remove the human entirely and you might be amplifying incoherence at maximum speed with nobody watching. That's not an AI problem. That's a system problem. And the system problem doesn't go away just because the agents got faster.



Most people don't need to be here. Most people need to be solid at Level 4 and selective about which workflows are worth fully automating.



Where to start



Look at where you actually are. Not where you wish you were.



If you're still in one chat that you're afraid to close, you're at Level 1. That's most people. The next move is to learn projects and build one. One. Not ten. Pick the work you do most often and build the assistant for it.



If you've got projects working, you already know the unlock. Get into a desktop tool that can read and write your files and watch how much friction disappears.



If you're at Level 3 and starting to feel the ceiling, that's the signal to read about orchestration and start sketching what your team would look like.



Coherence before creativity. Diagnosis before deployment. The manifesto's logic applies to the ladder itself.



Now you know where you are. The next move is yours.



Tell me where you are on this. I'm curious what level most people land on when they actually look.



------



david vogel\Curtis Hays - Systems Worth Ampli\The Mirror and the Window.md



The Mirror and the Window



You can't declare a Why. You have to go find it.



The framework I borrowed and broke



I forced a Why once. It didn't work, and it took me about a decade to understand why it didn't.



When Simon Sinek's "Start With Why" talk came out, I watched it. The Golden Circle. Why-How-What. That's his idea, not mine. And it's a good one — which is exactly why we grabbed it. I was at an agency at the time, and we used Why-How-What as a culture thing. We sat down to declare our Why because it sounded right, because it was the kind of thing a serious agency was supposed to have.



We wrote one down. It read fine. It moved nothing.



I know now what that feeling is — that specific flatness when something is correctly assembled but somehow inert. At the time I didn't have language for it. We'd done the work. We'd sat in the room, we'd talked it through, and what we produced looked exactly like what it was supposed to look like. Nobody called it wrong. But it never became the thing that shaped decisions. It sat in a document and aged out.



When I left, Why-How-What went with me — or rather, it went dormant. I didn't think about it for years. I moved into consulting and carried no particular conviction about it one way or another. It was an idea I'd tried and shelved, the way you shelve a tool you bought for a job it couldn't quite do.



Then Tom came back with it, and everything reordered.



Tom Nixon has been doing brand work for clients for more than thirty years. He has the kind of patience with a problem that you can only earn by watching a lot of good-sounding ideas fail under real conditions. When he started working inside my client engagements, he kept coming back to two things. The first: "You are what your customer says you are." The second, the one that I keep returning to: "I want to find out for myself, from the customer."



That's when the decade-dormant lesson broke open. Not because the framework was new — I'd carried it the whole time. It broke open because Tom wasn't sitting down to declare anything. He was going to look.



He laid this out on tape during Bullhorns & Bullseyes Season 1 Episode 9 — "For All Intents & Purposes." Thirty years of brand work distilled into one of the plainest truths I've heard in this industry. He said: "If it sounds to me like you're looking in the mirror, turn that mirror into a window and look through it and see the customer or the user or the audience on the other side and talk to them about them."



That's the distinction. That's the whole thing.



What I'd done at the agency was treat the Why like a mirror. Sit down, look inward, write what you see, call it true. What you get is a reflection of what you already assumed about yourself, dressed up well enough to sound like a discovery. The exercise feels like excavation but it's only rearrangement. You're moving your existing beliefs around the room and calling it finding something.



What Tom does is turn the mirror into a window. He doesn't ask the brand what it believes. He goes to the people who buy and finds out what they already know. The Why was never inside us waiting to be phrased correctly. It was on the other side of the glass the whole time, in the customer's own words, and the work was to go find it instead of invent it.



He puts the reason bluntly: "Few people care about you when they're reading or consuming or viewing or deciding and shopping. They care about themselves."



So the Why was never ours to declare. It belonged to them.



The same mistake, rebuilt in AI



This matters now because I've watched the same mistake reproduce itself in how people build with AI.



The default move is to write a posture into the system because it sounds right. "You are a helpful assistant." You declare what the thing is supposed to be, the same way we declared what our agency was supposed to be, and for the same reason: it sounds good, and it's what you've seen others do. Copied, not excavated. Invented, not found. It reads fine. It moves nothing.



I've been on the other side of that. When I built Duke — the orchestrator that runs my firm's operating system — I didn't get anywhere by declaring his character. The character came out of the actual decisions: the real client work, the corrections I gave him over and over, the way the firm actually behaves under pressure when something breaks. That's what became the doctrine he holds. It came from the work itself, not the setup.



The Brand Guardian we build for a client works exactly the same way. A Brand Guardian is the document that governs everything the system says on the client's behalf — it holds the positioning, the language, the reason people buy. It isn't a posture we assigned or a vision statement we composed in a conference room. It's the customer-validated reason people buy, excavated and written down so the system can hold to it. The research goes to the people on the other side of the glass. We listen to what they say about themselves — the language they use, the problem they're naming, the outcome they're actually after. And then we write it down as one thing.



AI did not generate it. AI revealed it.



There's a version of this in search that I've watched play out in client work. Keyword research, done right, is not a creative exercise — you're not naming what you think someone wants, you're reading back the language of someone who already wants it and typed it into a box when no one was watching. The same move. Turn the mirror into a window. Go read what's on the other side before you decide what to say.



Tom Nixon built his personal writing agent — Wradley — live, in about fifteen minutes, at a session we ran together recently. What he said afterward is what I want you to hear: "It took like 15 minutes, by the way... but it took months and months and months is the point — of you building this belief layer that made the writing part easy." And then: "So now I've got an agent named Wradley who writes like me, but believes what I believe, thinks what I think... the thinking is baked into our doctrine, now into my writer. So when I ask it to write something, the thinking's already there, all it's doing is the typing."



The fifteen minutes was real. So were the months. The months came first, and the months were not spent on the system. They were spent on the belief work that made the system possible. You cannot shortcut the months by getting better at the fifteen minutes. The sequence does not reverse.



A practitioner watching that same session sent something in live that is the sharpest version I've heard of why declaration fails:



"AI can give you the textbook theory, but it has never been burned. It has never been battle tested. You have. Give it those scars in context in your ICM system and see what happens. It's game changing."



Scars. Not principles. Not values. Scars. The things the system holds that only you could have put there, because only you were in the room when the lesson cost something. A declared posture has no scars. It has instructions. Instructions are other people's scar tissue, averaged. They tell the system how to behave in situations someone else already anticipated. They do not give the system anything to protect when the situation has never been anticipated before.



There is something else from that session I want to use here. The night before, while I was working through a naming problem with my orchestrator, the system reached — unprompted — for the Fisher King parable. Pulled it from a B&B episode Tom had recorded two seasons earlier. Tom retold the parable in the session: "And the fool says, I didn't know you were looking for a grail. I only knew that you were thirsty." Tom's word for what happened when the system surfaced it: indoctrinated.



Not retrieved. Not searched. Indoctrinated. The episode had been fed into the belief layer two seasons ago, and the system brought it forward when the moment called for it.



A declared posture cannot do that. A system told "you are a helpful assistant" does not reach for a two-season-old parable about thirst when the conversation calls for it. It has no way to know that thirst is the thing. A system that has been excavated and indoctrinated does know, because the parable was already inside it — not as a file to retrieve, but as a lens the system sees through. It did not know you were looking for a grail. It knew you were thirsty.



That is the difference between a posture and a worldview. A posture answers the question you asked. A worldview recognizes the question underneath it.



You cannot engineer a worldview worth holding until you've found the why that makes it true. The engineering comes second. The discovery comes first. And discovery is not a creative exercise. It is a research discipline. It is the decision to stop looking inward and go look outward, to treat the customer's language as the source and your own assumptions as the thing you're testing.



That sequence matters. Mirror without window — you get a system that performs confidence without having earned it. Window first, doctrine after — you get a system that holds to something real because the something real was found, not invented.



I gave away my entire OS map this week — the architecture, the agent roster, the folder structure, the belief layer outline. Posted it publicly. It cost me nothing, because the map was never the moat. I know that because I've watched independent builders with no access to my internal architecture keep arriving at the same shapes. Different people, different angles, same destination. When strangers reconstruct doctrine you already wrote without ever seeing it, the doctrine isn't something you invented. It's just how this actually works. Convergence is the proof it's true.



Malcolm Guite — the poet-priest who just published Galahad and the Grail — puts it at the level of myth. He points out that almost every great quest story in the Western tradition is a story of acquisition: go get the golden fleece, bring back the fire, seize the treasure, return with power. That's the template that runs from Jason and the Argonauts through most of what we still reach for. Then he says this about Tolkien: "He gives us an epic of letting go, of renunciation." The treasure is there from page one. The whole journey is about not keeping it. That inversion isn't a narrative trick. It's the structure of the thing that's actually true.



The Why works the same way. It isn't acquired. It isn't declared in a conference room. It's already there — in you, and in how your customers actually behave. You go find where those two meet. We're archaeologists, not architects. The belief is underground, not invented. The map just shows you where to dig.



Solve for Why



I spent years thinking a Why was something you sit down and write. It was the thing I copied, the thing I tried to invent, the thing I forgot about for almost a decade.



The day I stopped declaring it and started finding it was the day it got real.



That's the whole reason this season of Bullhorns & Bullseyes is built around Solve for Why. Not declare it. Not phrase it well. Solve for it — the way you solve for anything you don't yet have: by going to where the answer actually lives and bringing it back.



------



david vogel\Curtis Hays - Systems Worth Ampli\Why ICM Is the Answer to the GUI.md



Why ICM Is the Answer to the GUI



You're not bad at AI. You're stuck in one room — and the room is the reason.



If you are reading this, there is a decent chance you got stuck.



You opened ChatGPT, or Claude, or a Gemini Gem. You set up a project. You gave it instructions, uploaded a few files, and started working. And it worked — better than a blank chat, better than pasting the same context in every morning. So you settled in. You are standing in a single room, and for a while the room is enough.



Then the friction started, and it started because real work is not one job. Say you are producing a blog post. That is not one assistant. The copywriter writes the post. The graphic designer makes the header image. The developer builds the HTML and CSS. Same deliverable, three different assistants — and in a GUI, that is already three separate projects you are walking between by hand.



You live with that. Three projects for one blog post is annoying, not fatal.



Then you get a second client. And a sixth.



Now the walls close in, because you have two things that both need their own rooms — your assistants and your clients — and the GUI only lets you file by one of them at a time. So you have to choose, and every choice is bad.



Make a room per client, and copy the assistants into each? Now the copywriter lives in six places. Improve it once and you update it six times.



Make a room per assistant, and copy the client's files into each? Now the client's brand doc lives in six assistants. The client changes their positioning and you update it six times.



Give up and make a room for every combination — six clients times six assistants — and you have thirty-six projects. Change one client document and you are editing it in six of them.



There is no arrangement that doesn't duplicate something. And duplication is the thing that breaks the moment it changes. That is not friction you can out-organize. It is a wall. You hit it the day client number two shows up, and no amount of tidiness moves it.



The room has no door



Once you have used these tools long enough, the reason becomes invisible.



A ChatGPT project, a Claude project, a Gemini Gem — each one is a room. You walk in, and the room has everything you set up in it: instructions, files, context. Inside that room, the tool is genuinely good at the job the room was made for.



But the room has no door to the other rooms.



There is no hallway. If you want the copywriter, you leave and open the copywriter. If you want that client's brand doc, it has to already be sitting inside whatever room you are standing in — which is why you keep copying it in. The rooms cannot reach each other, and they cannot reach a shared shelf of anything. So every room ends up holding its own copy of everything it might need, and you become the person carrying files between them in your arms.



That is why it feels like work. Not the thinking — the logistics. You spend real energy being the hallway the tool doesn't have, and the filing cabinet it doesn't have either.



I lived in that room for about a year. Open a chat, ask a question, close the tab. When I finally built my first project, context loaded once, instructions reusable, it felt like a promotion. The tool went from a search bar to a coworker who remembered yesterday. That was real. But it was still one room. I just had a nicer room.



Why the folder is the answer



The thing that got me out was not a better prompt or a better model. It was a folder — and the reason a folder solves this when a project can't is worth sitting with, because it is the whole case for ICM.



A GUI project can only be entered. You go in, you work, you leave. It cannot reach anything outside itself, so it has to hold its own copy of everything — which is the trap. A folder is different in one way that changes everything: it can be combined with other folders without copying either one. Your assistants can live in their own folders. Your clients can live in their own folders. And a router at the top — mine has a name, Duke — can walk to the copywriter's folder and the client-four folder and bring them together for one job, then walk somewhere else for the next. Nothing gets copied into anything. They are combined at the moment you ask, and separated again when you are done.



That is the difference the GUI cannot cross. Not "folders are neater." Folders can be navigated and combined; projects can only be entered.



And that single property is what dissolves the wall. The thirty-six-project grid collapses into six clients, six assistants, and a router that combines them on demand. Change one client document and you change it once — every assistant that reads that folder sees the new version, because there is only one version. The duplication that broke the moment it changed is simply gone, because nothing was ever duplicated. That is not a workflow tip. It is why the structure fits the shape of the problem, and the GUI never could.



Why "unstuck" is the right word



The first time this clicks, the word you reach for is unstuck. Not "faster," not "smarter." Unstuck.



That word matters, because it tells you what the problem actually was. You were not slow. You were not doing it wrong. You were standing in a room with no door, doing the logistics by hand, and calling that the cost of using AI. The friction was never a skill you lacked. It was a wall the GUI put there, and you had normalized it.



ICM does not make the model better. The model is the same. It takes the wall down. You walk into a building instead of a room, and the work that used to cost you a dozen tabs and three re-pastes costs you one sentence.



If you are stuck right now — too many projects, too much copying between them, too many fresh chats where you paste the same context back in — that is not a sign you are behind. It is a sign you have outgrown the room. The next move is not a better prompt. It is a folder, a router, and a hallway.



Leave the room. There was always a building.



------



david vogel\Curtis Hays - Systems Worth Ampli\Worldview Engineering.md



Worldview Engineering



Prompt engineering will be a commodity skill in the next 3 years



Not because it stops being useful. Because everyone will have it. The tutorials are everywhere. The frameworks are on GitHub. The syntax is not hard. You learn it the way you learned keyboard shortcuts — a little at a time, until one day you realize you cannot work without it and cannot remember when you acquired it.



That is not a criticism. It is a pattern. And I have watched this exact pattern run enough times now to know where it ends.



I remember when building a website was a real skill.



I spent fifteen years inside IT before I ever touched marketing — building networks, standing up servers, running the infrastructure that businesses quietly depended on and never thought about until it broke. Back then, if you wanted a website, you came to a shop like ours and we charged you real money for it, because building one took people who knew what they were doing. The skill was the moat. Then WordPress showed up, the CMS wave hit, and the thing we used to charge for became the thing anyone could do in an afternoon. The skill did not get less real. It just stopped being rare.



So I moved upstream. By 2016, before the big CRM platforms had attribution built in, I was working with a developer to stitch a closed-loop attribution system together out of cookies and Gravity Forms — because knowing what actually drove a sale was still rare, and the people who could see it were a step ahead of the people who could only build the form.



That has been the shape of the last fifteen years for me. Websites, then SEO, then social, then content. Every single time, the operators still talking about the tactic were already behind the operators who had moved to the layer underneath it.



Every time a capability becomes table stakes, the differentiator moves upstream.



AI is the same pattern wearing newer clothes. The prompt is the website. The skill everyone is rushing to learn right now is the skill that will be sitting in everyone's hands inside three years.



The layer underneath prompt engineering is not better prompts.



It is what the system believes.



What a worldview actually is



I want to define the word before I use it the rest of the way, because worldview is one of those words people nod at while meaning different things.



A worldview is not an opinion. It is not a preference. It is not belief in the soft sense.



It is the instrument of vision. The frame of reference that determines which problems you recognize, which evidence you weight, which solutions you can even see. C.S. Lewis named it as cleanly as anyone has:



I believe in Christianity as I believe that the Sun has risen, not only because I see it, but because by it I see everything else.



That is worldview as instrument. Not the content of vision. The means of vision. The thing you see by, not the thing you see at.



Most people inherit a worldview without knowing they have one. The operators who actually shape their field are the ones who recognize they have one, name it, and install it on purpose.



That is what you are building when you build a governance layer correctly — the file that loads before the system does anything. Not a rulebook. A window the system sees the world through.



A rulebook is finite. The world is not. Every governance system built as a rulebook eventually meets a case the rulebook does not cover — and at that moment the system either defaults to its training (someone else's worldview, averaged) or it freezes. A window does not have that problem. The window is not enumerating cases. It is determining what the system perceives in the first place. Cases the rulebook never anticipated still come through the same window and are interpreted by the same worldview. The system stays consistent because it is not consulting a list. It is seeing through a frame.



That is worldview engineering. And it is the discipline almost nobody is working on yet, because almost everybody is still upstream of it — still optimizing models, tuning retrieval, wiring orchestrators, arguing about which frontier model runs fastest.



All of that is real. All of that matters. None of it is the moat you think it is.



What happens when the tools converge



Picture two operators in the same market. Same industry. Same customer size. Both are at Level 4 on the AI ladder. Both have orchestrators. Both have specialist agents. Both have persistent memory and clean file systems and retrieval that works.



They buy access to the same frontier model. They borrow the same folder architecture from the same GitHub repo. They watch the same tutorial. They run the same setup.



Six months later, one of them is producing work that feels unmistakably like a point of view. The other is producing work that is technically flawless and completely forgettable.



Same piano. Different music.



The difference is not in the instrument. The instrument is identical. The difference is in what the system was told to believe before the first prompt was ever written.



I have shown this to a room. Same model, same prompt, run twice — once with a blank system, once with the belief layer loaded. Two completely different outputs sitting side by side, and the only thing that changed between them is what the system believed.



One operator did the belief work. The other downloaded the scaffold and assumed that was the same thing.



Infrastructure can be copied in an afternoon. A worldview takes years to earn and can only be written by the person who lived it.



The invisible layer most systems are missing



If you open the CLAUDE.md file or the system prompt or whatever governance layer sits at the top of most advanced AI stacks, you will find something like this:



You are a helpful assistant. Be concise. Maintain professional tone. Follow these SOPs.



That is a posture. It is not a worldview.



Here is what a worldview-engineered system has that a posture-governed system does not.



It has opinions about what quality means. Not "produce good work" — a specific, defended definition of good that would let the system reject something most operators would approve.



It has a list of things it will never say. Not because they are technically wrong. Because they are inconsistent with what the system believes about its customer and its work.



It has a hierarchy of tradeoffs. When speed conflicts with depth, what wins? When the client asks for something that contradicts the doctrine, what happens? When the data suggests one thing and the belief layer suggests another, which gets the next question?



It has an emotional register. What tone does this system protect? Not "professional." What does that actually mean for this operator, for this customer, in this moment?



It has a definition of originality. What would make this output something nobody else could have produced?



Most systems have none of this. They have instructions. Instructions tell the system how to behave. A worldview tells the system what to protect when the instructions run out.



And the instructions always run out.



Why you cannot download someone else's worldview



This is the thing I have to say plainly, because the temptation in every builder community is to find the best stack and replicate it.



When you download someone else's CLAUDE.md — their role files, their doctrine layer, their agent prompts — you are not just importing their architecture.



You are importing their beliefs.



Every structural decision in a governance file encodes a conviction. What gets preserved and what gets filtered. What the system treats as signal and what it treats as noise. What "good" means. What "done" means. What the system is never allowed to optimize at the expense of the business.



Those decisions were made by someone who lived something. Who earned a specific set of rules by watching a specific set of things fail. The rules look like technical choices. They are not. They are formed convictions dressed in syntax.



If their convictions happen to match yours, you got lucky. If they do not, the system drifts toward their answers every time you do not have an explicit override. And you will not always know which decisions were value-laden and which were just engineering.



The danger is not that borrowed scaffolding breaks. The danger is that it works well enough that you never notice the beliefs underneath are not yours.



You end up with a coherent system. Coherent around someone else's doctrine.



The output is competent. The output is on-time. The output also has no gravity. No invisible weight that makes a reader feel like only one person in the world could have written it.



That gravity is a worldview. It cannot be forked from a repo.



What the belief work actually looks like



I did not sit down one afternoon and write a worldview. Nobody does.



I have a podcast. Seventy-five episodes across three seasons. Hundreds of client conversations. A decade of diagnoses that felt like judgment until I stopped and named what was underneath them.



The doctrine was already there. AI did not generate it. AI revealed it. I dumped the transcripts and asked the system to find the patterns. What I was looking for was content ideas. What I found was doctrine. Rules I had been enforcing for years without naming them. Beliefs I had been protecting without writing them down.



I had been the last one to hear them.



Then I wrote them down. Not a brand guide. Not a slogan. The actual rules. Why diagnosis comes before tactics. Why no client gets a creative brief before the customer reality is clear. Why every output has to be traceable back to something true about the customer. Why certain things are never said, regardless of whether they would convert.



Then I encoded them. Not into a prompt. Into a governance layer the entire system loads before producing anything. Every agent. Every session. Every output.



The system changed when those files went in. Not because the model changed. Not because the architecture changed. Because the system finally had something to be faithful to that was mine — not the internet's average.



That is the sequence. The belief work comes first. Always. Before the folder system. Before the orchestrator. Before the first agent is named.



Most people do it in the opposite order.



They build the system and then try to pour belief into it later. But the system was already shaped by defaults — the model's training data, other people's scaffolding, the conventions baked into every template they borrowed. The architecture has already made a hundred quiet decisions about what matters. By the time the operator tries to install a worldview, they are fighting the gravity of a system that was built without one.



The chest has to be built before the brain is turned on. Otherwise you get intelligence without conviction.



You are designing epistemologies now



There is a word for what happens at the far end of this discipline.



The really advanced builders — the ones two or three moves ahead of the current conversation — are not designing workflows. They are designing epistemologies.



They are deciding how truth is evaluated inside a system. What counts as evidence. How ambiguity is handled. What signals deserve trust and which ones get questioned. What emotional outcomes matter beyond task completion. What identity the system is protecting on behalf of the operator who built it.



That is not hyperbole. That is the literal description of what a governance layer does when it is built from a genuine worldview rather than borrowed instructions.



And it compounds.



A system with a clear worldview gets more itself over time. Every output that holds the doctrine reinforces the doctrine. Every decision the system makes that is consistent with the operator's beliefs adds weight to the next decision. The outputs start to feel related even when the topics change. There is an invisible gravity.



That is what you feel when you read someone who has a coherent perspective. Every piece carries the same weight. You do not have to read the byline. You already know who wrote it.



AI systems will work the same way.



The companies that win the next phase of this will not be the ones with the most capable models. Capability will be ambient, like electricity. You will assume it is there and pay a flat rate for access.



The companies that win will be the ones whose systems consistently express a recognizable philosophy.



Not a brand voice. A philosophy. A set of beliefs about the customer, the work, and what the work is for that is so clearly encoded into the system that every output carries it — whether a human or an agent produced it.



Humans are still the source



I want to name one thing before the close, because it is the part that gets lost when people hear "worldview engineering" and imagine they are being asked to turn AI into something it is not.



AI can scale judgment. It cannot originate lived conviction.



That is not a limitation the models will eventually overcome. That is a structural fact about where belief comes from. Belief comes from consequence. From watching something fail. From the client who taught you the lesson you did not want to learn. From the year the business nearly didn't make it. From the thing you almost said and stopped yourself. From the rule you earned by breaking it.



AI has no biography. It has training data. Training data is other people's consequence, averaged. It is powerful. It is not yours.



This is why generic AI content feels empty. It has syntax without sacrifice. It has structure without stakes. There is no accumulated life inside it. The system has no skin in the game because it has no game. It has only examples of games other people played.



Mark Schaefer built a version of himself you can talk to — a ChatGPT he calls Markbot. The thing that struck me was not that it knew more than any other model. It did not. It had read the same internet everyone else read. What it had was a soul. It carried his worldview so completely that asking it a question felt like asking Mark a question and getting Mark's answer back. The information was ambient. The worldview was the whole point.



The operators who understand this will stop asking how to make AI sound more human. They will start asking how to make AI more faithfully theirs.



That is a different question. It leads to a different discipline.



It leads here.



Tom Nixon and I have been working out this argument for months. He has spent thirty years inside brand strategy. I have spent fifteen years inside IT systems and fifteen inside digital marketing. We came at this from opposite directions and arrived at the same place.



He chases truth in meaning. I chase truth in data. The worldview lives where those two lines cross.



He said something to me early on that I have not been able to improve on.



I don't care what you think you are. You are what your customer says you are.



That is the discipline I am describing in commercial language. A worldview is not what you believe about yourself. It is what you have heard from the customer often enough to stop arguing with, and have written down with enough precision that a machine can defend it when you are not in the room.

#### He also said this, later in the same conversation:

The doctrine without a machine to amplify it is useless. A machine that amplifies without a doctrine to guide it is also useless.



That is the whole thing. Two sentences. The first three pieces in this series climbed the ladder. This piece names what the ladder is leaning against.



What Jobs saw in 1985



There is one more piece of this I want to put on the table before the close.



Steve Jobs gave a talk at Lund University in 1985. The Mac had shipped. He was working on what would become NeXT. He was talking to students about computers, and he stopped to talk about Aristotle.



He said that as a kid, books were what kept him out of trouble. He could read what Aristotle wrote without an intermediary. The book was a miracle. The source got to the destination with nothing in the middle. But he could not ask Aristotle a question. He named it as the limit he wanted the next generation of machines to break.

#### He used the exact word:

My hope is someday, when the next Aristotle is alive, we can capture the underlying world view of that Aristotle in a computer, and someday some student will be able to not only read the words Aristotle wrote, but ask Aristotle a question and get an answer.



He was not predicting LLMs. He was naming the prize of the computer age four decades before the machines existed that could deliver it. The prize is the encoding of a worldview precisely enough that it can be queried after the operator is gone.



The words are the artifact. The worldview is the thing that made the words mean something. For two thousand years we have had the words. We have never had the worldview. Aristotle's actual frame of reference, the instrument he used to see the world by, survived only as far as his apprentices could carry it, and then it filtered through centuries of translators, summaries, and arguments about what he probably meant.



Jobs saw, in 1985, that the computer might finally close that gap.



Forty years later, we are the operators standing in front of it. The technology exists. The discipline does not yet. The companies that build the discipline are the ones who will encode worldviews precisely enough that the systems can run on them after the founder is in another meeting, or another company, or no longer in the room at all.



That is not productivity. That is not workflow automation. That is the move Jobs named four decades before the machines existed that could actually do it.



This is what worldview engineering is for.



The question that decides which operators win



Prompt engineering is how you use the tool.



Worldview engineering is how you decide what the tool is for.



One is a skill. The other is a discipline.



The skill will be table stakes. The discipline will be the moat.



The question in front of you is not which model to use or which agent framework to build on.



The question is whether you have encoded the worldview that makes you know which problems are worth solving in the first place.



And whether you wrote it down before you turned the machine on.



Closing Thoughts



Prompt engineering will soon be table stakes — something everyone can do.



The real differentiator is no longer how well you prompt the machine. It’s what the machine believes before you even type the first word.



Curtis has laid out the next layer with rare clarity: worldview engineering. The discipline of encoding your hard-earned convictions, philosophy, and customer truth into the system so deeply that every output carries your unique gravity.



Infrastructure can be copied. Scaffolding can be downloaded. But a worldview can only come from lived experience — and that cannot be forked from a GitHub repo.



The operators who do this work will not just have faster systems. They will have systems with soul. Systems that feel unmistakably theirs.



Thank you, Curtis Hays, for another powerful installment in this series. Your ability to see around corners continues to raise the bar for all of us.



------



david vogel\David and Jake's Picks V2\Allan's Mini-Series (parts 1&2).md



Allan's Mini-Series (parts 1&2)



📝 What this is: Part 1 of a mini-series documenting how AI + browser automation (Playwright) replaced thousands of manual invoice corrections after a corporate restructuring broke sales rep assignments.



💡 Why it matters: If you're stuck doing repetitive portal clicks that "can't be automated" because you lack database access, this shows there's always a workaround.



🏷️ Tags: automation, workflow-design, client-work, claude-code, browser-automation



⏱️ 4 min read | 🔓 Free



✍️ David's note: This is the unglamorous side of AI that actually pays — Allan didn't build a chatbot, he eliminated soul-crushing manual work. The progression from single browser to three parallel sessions is exactly how you think when you stop treating AI as a toy and start treating it as labor. Part 2 promises a 90% token reduction, which is where it gets really interesting.



📝 What this is: Part 2 of the rebill automation series — how hitting token limits led to replacing screenshot-based AI with keyboard-driven scripts, cutting API usage by 90% and going 10x faster.



💡 Why it matters: Using AI to watch your screen is expensive and slow — using it to write the automation script once and then running deterministic keystrokes is the actual unlock.



🏷️ Tags: automation, workflow-design, claude-code, browser-automation, optimization



⏱️ 4 min read | 🔓 Free



✍️ David's note: This is the sequel that delivers. Allan hit his token wall and instead of buying more credits, he redesigned the approach — AI writes the script, the script does the work. The "dead man's switch" pattern for protecting live data is something everyone doing browser automation should steal. Constraint-led creativity at its finest.



Mini-Series Part 1: The "Manual Hell" Rebill Project



Following up on my previous post about automating month-end, I want to pull back the curtain on the project that really started it all. It involves a massive company reconstruction, a "manual hell" task, and a midnight breakthrough that tripled my productivity.



The Problem: A Reconstruction Hangover



On January 1, 2026, our company underwent a major reconstruction. Customers were assigned new sales reps, but the final list of who owned which account wasn't finalized until April.



In the meantime, we kept invoicing as usual. The invoices were correct, but the Sales Rep field on the historical records was now wrong. To fix it, we had to go back and update thousands of already invoiced sales orders.

#### The Manual Workflow (or: How to lose your mind):

Search for the Sales Order.



Click Invoice.



Click Rebill.



Change the Sales Rep.



Hit Esc to exit.



Repeat... hundreds (or thousands) of times.



Enter Claude Code & Playwright



I had just started using Claude Code on March 19th after watching @Jake Van Clief ’s videos. Two weeks later, this assignment landed on my desk in the middle of my usual accounting duties.



Since I didn’t have backend API access to D365 F&O, I turned to the Playwright MCP. If I couldn't talk to the database directly, I’d have Claude "drive" the browser just like a human would.

#### The Automation Logic:

Open Chrome to the D365 Sales Order URL.



Open the filters tab.



Add filter information (Customer account, dates for Q1 2026, and identifying which sales orders had the wrong rep).



Execute the "Rebill" click-path automatically.



The "Aha!" Moment at 00:30 AM



It worked, but it was real slow. D365 isn't exactly a speed demon. My boss was happy ("as long as we don't have to do it, I don't care how slow it is"), but I knew we could do better.



Earlier that day, I was running it in one browser and it was taking forever. While the kids were finally asleep that night, I had an idea: Can I run this on more than one tab?



I spent until 00:30 AM rebuilding the MCP Playwright logic. I quickly figured out that Playwright can generally only run on one tab per session. BUT... it can run on one tab per browser.



The Multi-Browser "Boom"



Because of company IT limits, I could only get three browsers: Chrome, Edge, and Firefox. I fired up all three simultaneously, each running its own Claude-driven Playwright instance.



Browser 1 (Chrome): Processing Sales Rep A



Browser 2 (Edge): Processing Sales Rep B



Browser 3 (Firefox): Processing Sales Rep C



BOOM. I was suddenly 3x faster. I sat back and watched the "manual hell" disappear across three screens. However, this BURNED THROUGH my tokens! Even with the 5x plan the company now pays for, I knew I couldn't keep this up.



In Part 2: I’ll explain how—later that same night—I realized I was still being "inefficiently lazy" and managed to cut my token usage by 90% and increase the speed by 10X.



Mini-Series Part 2: The "Token Crash" & The Keyboard Epiphany



In Part 1, I was riding high. I had Chrome, Edge, and Firefox all running simultaneously, tripling my speed on a massive D365 rebilling project. I felt like I’d cracked the code to being "efficiently lazy."



Link: Mini-Series Part 1: The "Manual Hell" Rebill Project · Clief Notes



But the victory was short-lived. I was driving the car at 100mph, but I didn't realize how much fuel I was burning.



The Crash: 3 Hours to Zero



The next morning, I fired up all cylinders. It was beautiful—until it wasn't. In under 3 hours, I burned through my entire token allotment. I was dead in the water with a 1.5-hour wait until my limits reset. With the clock ticking and sales reps still needing updates, I had to go back to doing it manually.



And that’s when the "Aha!" moment happened.



The "Tab" Breakthrough



While I was clicking and typing manually to pass the time, I realized something: I wasn't really using the mouse. I was mostly hitting Tab and Shift-Tab to navigate the D365 fields.



I asked Claude: "Can Playwright just 'Tab' through the browser instead of searching for elements and taking screenshots for every move?"



Claude’s answer: YES. My jaw dropped.



From "Visual Driving" to "Macro Speed"



The old workflow relied on Claude "seeing" the screen via screenshots to make sure it was in the right spot. It was accurate, but heavy. I had Claude rewrite the interior workflow to a deterministic loop:



The Setup: I open the URL, set the filters, and select the first row.



The Loop: * Tab to Invoice → Enter.



I added small buffers (100ms between tabs, 4s for page loads) to ensure D365 could keep up.



See the video for how the flow runs in real life!



The Result: 90% Savings & 10x Efficiency

#### I asked Claude to evaluate the two methods. The numbers were staggering:

#### Old "Visual" Flow:

Tool Calls: ~500 calls per 50 orders



Token Usage: 100% (High Burn)



Logic: Screenshot-dependent (Slow)

#### New "Tab" Flow:

Tool Calls: 1–4 calls per 50 orders



Token Usage: 10% (90% Reduction!)



Logic: Command-driven (10x Faster)



By stopping the constant screenshots and "thinking" cycles, the workflow became a lean, mean, rebilling machine.



The "Accounting Brain" Safeguard



The new flow was fast—too fast. After about 5 loops, it would occasionally lose its place and start "going rogue," tabbing and entering into the wrong fields.



I needed a safeguard. I told Claude: "The Sales Order is always a 10-digit number. The Customer Account next to it is always 9 digits."

#### I had Claude add a check after every "Arrow Down":

The Check: Read the current field. Is it 10 digits?



Yes: Continue.



If it got off track, the script would halt. I’d manually click the right column, hit "Go," and it would fly again. It wasn't worth building a complex "self-correcting" logic for a one-time assignment; I just needed a "dead man's switch."



The Finish Line



I had one rep with 100 orders. I split his customers across my three browsers. In 30 minutes, he was done. In that same 30 minutes, I was actually doing my other accounting work.



What I Learned (The AI Mindset Shift)



This project changed how I view AI. It’s not just about "having AI do the work"—it's about Engineering the Efficiency.



AI for Writing, Not Just Thinking: Don't pay the AI to "think" through every repetitive step. Use it to write a deterministic script that executes the steps. It’s the difference between hiring a driver and building an autopilot.



Token Economy is a Skill: Being "efficiently lazy" means finding the path of least resistance. Keyboard shortcuts (Tab/Enter) > Element selectors > Visual recognition. This saved 90% on costs and kept me under my limits.



Deterministic vs. Probabilistic: If a process is mechanical, use mechanical tools. Relying on "AI vision" for a 1,000-row loop is risky; relying on a hard-coded tabbing sequence is reliable engineering.



Safeguards > Perfection: You don't need a script that can fix its own mistakes. You just need a "Dead Man's Switch" that knows when to stop. This prevents an AI from "going rogue" on your live ERP data.



The North Star Mindset: Keep the end result fixed, but stay flexible on the "how." The "3 browser" trick was the spark, but the "Tab" epiphany was the actual fuel that finished the job.



Respect the "Cooling Off" Period: Burning through your tokens isn't a failure—it's a signal. That 1.5-hour lockout was actually the best thing that happened, because it forced me to find a more efficient way to work.



More month-end automation updates coming soon!



Special thanks to everyone who commented on Part 1—your insights on "constraint-led creativity" were exactly what I was feeling that night at 00:30 AM!



@Alex Nartey @Alex Harrison @Andrew Carter @Marcos Accioly @Sebastian Cramer



------



david vogel\David and Jake's Picks V2\Built always-on AI Chief of Staff that texts me.md



Built always-on AI Chief of Staff that texts me.



📝 What this is: A locally-hosted AI assistant ("Emma") that runs 24/7 on an old MacBook, texts daily briefings via iMessage, and manages calendar, email, and projects through MCP integrations.



💡 Why it matters: This proves you can build a production-grade personal AI system on consumer hardware without cloud dependencies or complex orchestration frameworks.



🏷️ Tags: workflow-design, automation, folder-architecture, custom-ui, deployment



⏱️ 6 min read | 🔓 Free



✍️ David's note: Justin built a full chief-of-staff AI on a 2015 MacBook using markdown directories instead of vector databases. The constraint-first philosophy here is gold — he stayed within standard subscription limits and made it model-agnostic with a single line change. The iMessage integration alone makes this worth studying.



------



david vogel\David and Jake's Picks V2\First Big Win! First client is signed.md



First Big Win! First client is signed



📝 What this is: A member signed their first paying client before finishing the product — by listening to pain points in their network and pitching a personalized AI-built solution.



💡 Why it matters: You don't need a finished tool or a polished funnel to land clients — you need a real problem and the ability to build something custom fast.



🏷️ Tags: client-work, workflow-design, custom-ui, ai-philosophy



⏱️ 2 min read | 🔓 Free



✍️ David's note: This is the playbook in action. Richard didn't wait for perfect — he talked to people, heard the same complaint three times, and said "I'll build that." The insight about personalized software over cookie-cutter SaaS is where AI development is heading. First of many for this guy.



------



david vogel\David and Jake's Picks V2\Helping your AI remember tasks between sessions.md



Helping your AI remember tasks between sessions



📌 Board: Show Your Work



📝 What this is: A session-aware memory system (PMM v2.8) that tracks open tasks, recent activity, and project threads so your AI maintains context between conversations automatically.



💡 Why it matters: Without persistent session memory, you waste time re-explaining context every time you restart a conversation — this system makes your AI manage its own continuity.



🏷️ Tags: workflow-design, claude-code, folder-architecture, templates, automation



⏱️ 4 min read | 🔓 Free



✍️ David's note: This is the kind of infrastructure thinking that separates "I use AI" from "AI works for me." Millenial Cat built what most people wish existed — a system where the AI actively decides what to remember and what to surface. Worth studying the thread/timeline architecture even if you never use the exact implementation.



TLDR: LLMs forget everything between sessions. You re-explain yourself constantly, lose progress on long-running work, and have no reliable way to pick up where you left off — especially when switching between models or tools. I built PMM to fix that. @Deacon Wardlow helped me improve it by identifying a specific gap: session continuity — what changed, what’s still open, where you stopped. That’s now live in PMM v 2.8.



Edit: I figured screenshots tell a better story => same memory on three different tools with 3 different models, where I've asked the LLM to basically recall outstanding tasks across the 4-5 current projects. Slightly different perspectives because I'm working a slightly different project with each model.



I initially built PMM to remember stuff beyond the context window to fix an issue i had with the LLMs I use failing to remember and recall over long conversations. I used it to have the same conversation, while switching between Claude Code CLI and Co-work.



Eventually it became a tool for helping me with continuity in my conversations with different LLMs on different apps and harnesses ( I switch a lot between Claude, OpenCode and GitHub Co-Pilot). I now use it to give multiple agents long-term memory (while they switch between different models on Claude, Gemini, Model Ark and a couple of smaller local models) without the use of model routing.



I currently deploy it (along with with another agentic plugin I developed) to give agents long-term individual and collective organisaitonal memory in their conversations with multiple users over telegram in a small pilot.



@Deacon Wardlow tested PMM in his own workflows, identified a gap in session memory management, and tried a couple of changes, which he outlined in another thread discussing Session Memory Layer + PMM.



The problem: your work changes between sessions, and you need the LLM to remember progress, granular task completion and what changed.



PMM already retains knowledge about you, your work and what you're working on



However, there was a gap where session awareness and continuity was lacking



It didn't retain knowledge of files and facts that change between sessions: what did you work on, what you did, where you stopped, what needs to be done at the next session and why.

#### Deacon proposed:

What was worked on in the last 10 sessions (rolling log)



What's still open and needs follow-up (persistent thread tracker)



Some of these were already implemented partially in existing memory files. I figured we also needed:



Resource tracking (what repos, directories, files belong to which thread / projects)



An archive of sorts for completed threads to minimise context usage for completed threads



Additional info (context, notes, blockers, dependencies) for threads



Initially I proposed, that anyone who wanted to implement @Deacon Wardlow's session memory layer on PMM could simply tell the LMM what it needed to be done (PMM is extensible that way). But I forgot that the agentic plugins and skills building skill I developed was a separate plugin than PMM. It would work without, but not as well as it should with the plugin. So I pushed it as a memory feature in v2.8.



Based on his feedback, I integrated session awareness into PMM (and duly credited him with the idea and methodology for the fix). The feature is live for Claude Code CLI and Co-work (but I haven't gotten around to doing it for the OpenCode plugin, yet).



You can install PMM v 2.8 from the github repo.

#### Here are the changes that were implemented:

timeline.md doesn't just capture session summaries and updates at the end of every session



It now captures what changed and indexes / refers to the entries in the other memory files



This includes entries in the newly introduced threads-open.md and threads-closed.md which tracks issues and projects user is working on (what it is, why you're working on it, what needs to be done, what's been done, success criteria etc). Doesn't require you to say explicitly (but it will help).



When completed, a summary is retained in threads-open.md with a reference to the completed project or issue (archived) in threads-closed.md



Loaded at every session start or after every compact or clear



Saved at every session end (I still recommend manually /pmm:save)

#### How PMM is different form the other memory systems out there:

Other systems are passive, like filing cabinets, and only as smart as the retrieval assistant searching through them and deciding what is relevant to hand off to the LLM that speaks to the user.



Retrieval system like RAG and a storage system like Graph or Vectors decide what is relevant from past conversations and hands it to the LLM



PMM autonomously decides what's relevant, what to save and what to retrieve



PMM makes the LLM an active participant in its own memory.



It was an experiment in "what happens when I just tell the LLM about memories and where they are" instead of trying so hard to stuff what I (or some other system) think is relevant into context memory.



I've been working on something more polished: a more organic memory system that strips PMM down to core essentials with more autonomy for the LLM. But that's a discussion for another day....



------



david vogel\David and Jake's Picks V2\START HERE.md



What this is?



A quick explainer on how curated posts in David's & Jake's Picks now work --- what's changed, why, and how to read them.



Why it matters



You can now decide in five seconds whether a post is worth your time instead of clicking through and hoping for the best.

#### David's note:

I got tired of bookmarking great community post and having no one find them. This format fixes that --- every curated post now tells you exactly what it is why it matters, and how long it takes before you commit a single minute.



I run four phases before any AI builds anything.



📝 What this is: A four-phase planning methodology (Brainstorm, Plan, Hand off Doc, Dispatch) that front-loads all thinking before any AI generates code or content.



Helping your AI remember tasks between sessions



📝 What this is: A session-aware memory system (PMM v2.8) that tracks open tasks, recent activity, and project threads so your AI maintains context between conversations automatically.



Why your cold emails get ignored



📝 What this is: A cold email system that scrapes prospect websites and uses AI to generate hyper-relevant opening lines — taking reply rates from 3% to 10% and booking 9 calls per week.



Stop Prompting. Start Defining Outcomes.



📝 What this is: A mindset shift from casual prompting to outcome-driven briefs — three principles for treating AI like a contractor instead of a slot machine.



A completely markdown based task management system



📝 What this is: A full task management system built entirely in markdown files — syncs across machines via terminal hooks, uses AI to prioritize your day, and works offline.



First Big Win! First client is signed



📝 What this is: A member signed their first paying client before finishing the product — by listening to pain points in their network and pitching a personalized AI-built solution.



Built always-on AI Chief of Staff that texts me.



📝 What this is: A locally-hosted AI assistant ("Emma") that runs 24/7 on an old MacBook, texts daily briefings via iMessage, and manages calendar, email, and projects through MCP integrations.



Allan's Mini-Series (parts 1&2)



📝 What this is: Part 1 of a mini-series documenting how AI + browser automation (Playwright) replaced thousands of manual invoice corrections after a corporate restructuring broke sales rep assignments.



📝 What this is: Part 2 of the rebill automation series — how hitting token limits led to replacing screenshot-based AI with keyboard-driven scripts, cutting API usage by 90% and going 10x faster.



------



david vogel\David and Jake's Picks V2\Stop Prompting. Start Defining Outcomes.md



Stop Prompting. Start Defining Outcomes.



📝 What this is: A mindset shift from casual prompting to outcome-driven briefs — three principles for treating AI like a contractor instead of a slot machine.



💡 Why it matters: If your prompts read like wishes instead of contracts, you'll keep getting random outputs no matter which model you use.



🏷️ Tags: prompting, ai-philosophy, workflow-design, education



⏱️ 3 min read | 🔓 Free



✍️ David's note: "A prompt is a wish. A brief is a contract." That line alone is worth the click. Ari keeps hammering the same point from different angles and it keeps landing — the quality of your output is capped by the clarity of your input. Pairs well with her four-phase build post.



------



david vogel\David and Jake's Picks V2\Why your cold emails get ignored.md



Why your cold emails get ignored



📝 What this is: A cold email system that scrapes prospect websites and uses AI to generate hyper-relevant opening lines — taking reply rates from 3% to 10% and booking 9 calls per week.



💡 Why it matters: If your outreach still relies on mail-merge fields, you're getting ignored — this shows how to automate genuine relevance at scale using n8n and OpenAI.



🏷️ Tags: workflow-design, automation, prompting, client-work, n8n



⏱️ 4 min read | 🔓 Free



✍️ David's note: This is folder architecture thinking applied to outreach instead of code. Muhammad built a pipeline that does the research humans skip — scrape the site, extract what actually matters, write like you read it. The n8n workflow is the real takeaway here for anyone doing client acquisition.



------



david vogel\David and Jake's Picks V2\A completely markdown based task management system\A completely markdown based task management system.md



A completely markdown based task management system



📝 What this is: A full task management system built entirely in markdown files — syncs across machines via terminal hooks, uses AI to prioritize your day, and works offline.



💡 Why it matters: If your task system lives in a proprietary app, your AI can't read it — this keeps everything in plain text where both you and your tools have full access.



🏷️ Tags: folder-architecture, workflow-design, templates, automation, claude-code



⏱️ 5 min read | 🔓 Free



✍️ David's note: This is what happens when someone takes "your folder is your operating system" seriously. Roc built exactly what the course philosophy points toward — plain text, git-synced, AI-readable. The capture-to-prioritize loop is especially clever. GitHub repo included so you can fork it today.



------



david vogel\David and Jake's Picks V2\A completely markdown based task management system\build-instructions.md



TaskSystem — Build Instructions



Read this entire file before asking any questions. You are setting up a personal task and project management system for the user from scratch.



------



What You Are Building

#### Two integrated subsystems:

— Daily task management. You manage the task board (TASKS.md). On each session start, you generate FOCUS.md matched to the user's energy level. You track recurring tasks and run weekly retrospectives on Sundays.



— Project lifecycle management. Projects move from Idea → Seed → Scoped → Active → Paused. Each active project has its own folder with ideas, tasks, and resources files.



All files are plain markdown. The user never edits TASKS.md or PROJECTS.md directly — they report changes in chat.



------



Step 1: Questionnaire

#### Ask all 7 questions below in a single message. Tell the user:

"I'll set up your TaskSystem. Answer these questions and I'll build everything in one pass — you can answer all at once."



------



Q1 — Work categories



What areas of work do you track? These become the Category column in your task board.



Work, Personal, Admin, Creative



Client, Internal, Learning, Side Projects



Q2 — Energy pattern



When do you do your best focused or creative work? When do you handle low-energy tasks?



Example: "Sharp in the morning for deep work. Admin tasks mid-afternoon. Mental battery low by 8pm."



Q3 — Work start time



What time do you typically start a session?



after lunch



Q4 — Recurring tasks



List 2–4 recurring tasks and how often they repeat.



Weekly team standup (7 days). Expense report (monthly). Meal prep (every 4 days).



Q5 — First project



Name your first project and describe it in one sentence. Use lowercase-hyphenated format.



portfolio-site — Redesign and rebuild my personal website.



If you don't have a first project yet, say "skip" — I'll create an example project to show the structure, and you can replace it when ready.



Q6 — Short-ID prefix



What 2–5 letter prefix for that project? Used to tag ideas and tasks.



Skip if Q5 was skipped — the example project will use



as its short-ID.



Q7 — Name or handle



What's your name or handle? Used to personalize the system.



------



Step 2: Confirm Before Building

#### After collecting answers, confirm back to the user:

"Here's what I'm building:

#### Categories:

#### Energy pattern:

[brief summary of Q2]

#### Session start:

#### Recurring tasks:

[N from Q4]

#### First project:

[Q5 name] (



example-project



) if Q5 was skipped



I'll create 14 files in



[current directory]



. Is that correct?"



Wait for confirmation before writing anything. If the user corrects the directory, use the path they provide.



------



Step 3: Create All Files



If no working directory is established, ask the user where to create the files before proceeding.



Fill in every



marker in the templates below with the corresponding answer from Step 1. Parse Q4 into individual recurring task rows. Name the first project folder and files using Q5's project name.

#### If Q5 was skipped:

example-project



as the project name,



as the short-ID, and



example project



as the description for all project files and folders. Proceed with all 14 files as normal.



------



FILE: CONTEXT.md

# TaskSystem

*Read this file first, then the relevant CONTEXT.md for each subsystem.*



------

## Routing

| **When asked about**                         | **Directory** | **Read first**             |
| -------------------------------------------- | ------------- | -------------------------- |
| Tasks, today's focus, energy, prioritization | /TaskOS       | CONTEXT.md                 |
| Projects, ideas, project lifecycle           | /ProjectOS    | CONTEXT.md                 |
| "process ideas"                              | /ProjectOS    | _rules/ideas-processing.md |



------

## Key Files

| **File**              | **What it is**                                           |
| --------------------- | -------------------------------------------------------- |
| TASKS.md              | Master task board — Claude-managed, never edit directly  |
| FOCUS.md              | Session-generated focus list — auto, never edit manually |
| ideas.md              | Capture inbox — process with "process ideas"             |
| ProjectOS/PROJECTS.md | Master project index — Claude-managed                    |



------

## Commands

| **Say this**                         | **What happens**                                        |
| ------------------------------------ | ------------------------------------------------------- |
| `give me today` / `what's my focus`  | Generate FOCUS.md — Claude asks energy level if unknown |
| `refresh focus`                      | Regenerate FOCUS.md mid-session                         |
| `[task ID] done` / `[task] complete` | Claude archives the task                                |
| `add task: [description]`            | Claude adds task to TASKS.md                            |
| `Sunday check-in` / `retrospective`  | Weekly review written to TaskOS/RETROSPECTIVES.md       |
| `process ideas`                      | Route ideas.md entries to project files                 |
| `seed project [name]`                | Create new project at Seed stage in ProjectOS           |



------

## Rules

\-    Read this file first, then the relevant CONTEXT.md before starting any task.

\-    Never edit TASKS.md or PROJECTS.md directly — report changes in chat, Claude updates.

\-    FOCUS.md and ideas.md live at root.

\-    Check in before writing in all cases. Propose structure first, wait for confirmation.

\-    Ask before creating files outside designated project directories.



------



FILE: TASKS.md



Build the Recurring section from Q4 answers — one row per task, IDs R01, R02, etc. Infer Energy level from the task type. Leave Last Done blank. Set Next R-ID to one above the last ID used.

# Task Board

*Managed by Claude. Last updated: [today's date].* *To add a task: tell Claude in chat. To update: report what changed. Never edit this file directly.* *Next ID: T02 · Next R-ID: [next R-ID]*



------

## Priority Key

\-    **P1** — This week or deadline-critical

\-    **P2** — Important, 2–4 week horizon

\-    **P3** — Backlog / someday

## Energy Key

\-    **High** — Requires creativity, decisions, or drafting

\-    **Med** — Structured output with clear direction

\-    **Low** — Admin, routine, light reading, logistics



------

## Active

| **ID** | **Task**                       | **Category**        | **Deadline** | **Energy** | **Priority** | **Status** | **Notes**                                  |
| ------ | ------------------------------ | ------------------- | ------------ | ---------- | ------------ | ---------- | ------------------------------------------ |
| T01    | Define scope for first project | [first Q1 category] | —            | Med        | P2           | Open       | Seed task — complete or replace when ready |



------

## Recurring

*One row per recurring task. Update `Last Done` on completion — never archive these rows.*



| **ID** | **Task** | **Cadence** | **Last Done** | **Energy** | **Notes** |
| ------ | -------- | ----------- | ------------- | ---------- | --------- |
|        |          |             |               |            |           |



------

## Creative / Outlet

| **ID** | **Task** | **Category** | **Notes** |
| ------ | -------- | ------------ | --------- |
|        |          |              |           |



------

## Energy Restorers

*For unexpected free time. These recharge rather than drain.*



| **Activity** | **Best time** | **Why it works** |
| ------------ | ------------- | ---------------- |
|              |               |                  |



------

## Flags

*(none)*



------



FILE: ideas.md



Derive one open question or seed idea about the project from Q5's description. Write it as a bullet under the project's short-ID. If Q5 was skipped, use



example idea



as the bullet.

# Ideas

## Short-Ids

[Q6]



\-    [open question about Q5 project derived from its description]



------



FILE: TaskOS/CONTEXT.md



The FOCUS.md Format section inside this template uses ``` fences — the outer template uses ~~~ to prevent nesting conflicts.

# TaskOS — Context

TaskOS is the daily task management and focus system. Claude manages all files in this directory.



------

## Files

| **File**          | **Purpose**                                          |
| ----------------- | ---------------------------------------------------- |
| TASKS.md (root)   | Master task board — single source of truth           |
| archive/done.md   | Completed tasks, organized by month                  |
| ENERGY_LOG.md     | Daily energy level log                               |
| RETROSPECTIVES.md | Weekly retrospective summaries                       |
| FOCUS.md (root)   | Session-cache derived from TASKS.md — auto-generated |



------

## Generating FOCUS.md

Trigger: session start, "give me today", "what's my focus", or "refresh focus."



1. Read TASKS.md fresh.
2. Ask energy level if not     stated: High / Med / Low.
3. Select 2–3 tasks matched     to energy level and deadlines.
4. Apply deadline override:     P1 tasks and tasks due within 3 days always appear regardless of energy.
5. Include Recurring     Reminders — flag overdue or due-soon recurring tasks.
6. Include Deadline     Pressure section — all P1 tasks visible even on Low days.
7. Write to FOCUS.md at     root.

### FOCUS.md Format

\```

# FOCUS — [Date] ([Day])

*Energy: [High/Med/Low]*

## Today's Picks ([energy] energy)

| **#** | **Task** | **Energy** | **Why** |
| ----- | -------- | ---------- | ------- |
|       |          |            |         |

## This Week — Action Required

[P1 tasks and tasks due within 7 days]

## Deadline Pressure (visible even on Low days)

[All P1 tasks with deadlines]

## Recurring Reminders

[Overdue or due-soon recurring tasks]

## Standing Awareness

[Short bullets: key context, deadlines, blockers] ```



------

## Task Updates

When a task is reported (new, complete, or status change):



1. Update TASKS.md     immediately using the Next ID counter.
2. When marking done: move     the row to archive/done.md under the current month.
3. For recurring tasks:     update `Last Done` date only — never archive recurring rows.
4. Bump the Next ID counter     in the TASKS.md header after adding a task.



------

## Recurring Tasks

\-    Live in the Recurring section of TASKS.md.

\-    Check cadence when generating FOCUS.md — surface tasks overdue or due within 2 days.

\-    Never archive recurring rows; only update `Last Done`.



------

## Retrospective

Trigger: "Sunday check-in" or "retrospective."



1. Read TASKS.md and     ENERGY_LOG.md.
2. Summarize: what was     completed, what slipped, energy patterns observed.
3. Identify one pattern and     one suggested adjustment.
4. Write to     TaskOS/RETROSPECTIVES.md under the current week's date.



------

## Energy Pattern

[Q2 answer — verbatim or lightly cleaned up]



Typical session start: [Q3].



------

## Priority Key

\-    **P1** — This week or deadline-critical

\-    **P2** — Important, 2–4 week horizon

\-    **P3** — Backlog / someday

## Energy Key

\-    **High** — Requires creativity or decisions

\-    **Med** — Structured output with clear direction

\-    **Low** — Admin, routine, light reading, logistics



------



FILE: TaskOS/ENERGY_LOG.md

# Energy Log

*Updated by Claude when energy level is reported at session start.*



------

## Log

| **Date** | **Energy** | **Notes** |
| -------- | ---------- | --------- |
|          |            |           |



------



FILE: TaskOS/RETROSPECTIVES.md

# Retrospectives

*Written by Claude on "Sunday check-in" or "retrospective" command. One entry per week.*



------



FILE: TaskOS/archive/done.md

# Archive — Completed Tasks

*Managed by Claude. Tasks are moved here when marked done, organized by month.*



------



FILE: ProjectOS/CONTEXT.md

# ProjectOS — Context

ProjectOS manages long-term project lifecycle alongside TaskOS. Claude manages PROJECTS.md and all project child files.



------

## Files

| **File**                         | **Purpose**                                    |
| -------------------------------- | ---------------------------------------------- |
| PROJECTS.md                      | Master project index — single source of truth  |
| _rules/schemas.md                | Schema for project child files                 |
| _rules/ideas-processing.md       | Rules for routing ideas.md entries to projects |
| [project]/[project]-ideas.md     | Project-scoped ideas and open questions        |
| [project]/[project]-tasks.md     | Project-scoped task backlog                    |
| [project]/[project]-resources.md | Links and reference materials                  |



------

## Project Status Stages

| **Stage** | **Meaning**               | **Has directory?**    |
| --------- | ------------------------- | --------------------- |
| Idea      | Name captured only        | No                    |
| Seed      | Ideas being collected     | ideas.md only         |
| Scoped    | Task backlog defined      | All three child files |
| Active    | Currently being worked    | All three child files |
| Paused    | Stopped, intent to resume | All three child files |



------

## PROJECTS.md Schema

Sections in order: `## Active`, `## Scoped`, `## Seed`, `## Idea`, `## Paused`



Each section (except Idea) is a table with columns: Name, Description, Short-IDs, Dir



Idea stage has no Dir column.



------

## Transitions

| **Command**             | **Action**                                                |
| ----------------------- | --------------------------------------------------------- |
| "seed project [name]"   | Create [project]-ideas.md, add row to ## Seed             |
| "scope project [name]"  | Create -tasks.md and -resources.md, move row to ## Scoped |
| First task marked done  | Move row to ## Active                                     |
| "pause project [name]"  | Move row to ## Paused                                     |
| "resume project [name]" | Move row back to ## Active                                |



------

## Protocols

**Adding an idea to a project:** Append bullet to [project]-ideas.md. Do not restructure existing content.



**Adding a task to a project:** Append row to [project]-tasks.md. Use scoped ID format: [short-id]-01, -02, etc.



**Adding a resource:** Append row to [project]-resources.md.



**Reading active projects:** Load PROJECTS.md ## Active section only. For detailed work, load the project's child files.



**Unified work query:** Combine TASKS.md and active project task files, filter by Energy column matching current session energy.



------

## Stable Interface

TaskOS unified work query reads only the `## Active` section from PROJECTS.md. Do not restructure that section header.



------



FILE: ProjectOS/PROJECTS.md

# Projects

## Active

| **Name**          | **Description**  | **Short-IDs** | **Dir**    |
| ----------------- | ---------------- | ------------- | ---------- |
| [Q5 project name] | [Q5 description] | [Q6]          | [Q5-name]/ |

## Scoped

| **Name** | **Description** | **Short-IDs** | **Dir** |
| -------- | --------------- | ------------- | ------- |
|          |                 |               |         |

## Seed

| **Name** | **Description** | **Short-IDs** | **Dir** |
| -------- | --------------- | ------------- | ------- |
|          |                 |               |         |

## Idea

| **Name** | **Description** | **Short-IDs** |
| -------- | --------------- | ------------- |
|          |                 |               |

## Paused

| **Name** | **Description** | **Short-IDs** | **Dir** |
| -------- | --------------- | ------------- | ------- |
|          |                 |               |         |



------



FILE: ProjectOS/_rules/schemas.md



This file contains nested code blocks — the outer template uses ~~~ to prevent nesting conflicts.

# ProjectOS — Schemas

Read this file before creating or writing to any project child file (`[project]-ideas.md`, `[project]-tasks.md`, `[project]-resources.md`).



------

## [project]-ideas.md

\```

# [project] Ideas

\-    single idea



category



\-    grouped idea 1

\-    grouped idea 2 ```



Idea groups use a plain-text label on its own line (no `#`, no markdown heading) followed by a bullet list.



------

## [project]-tasks.md

\```

# [project] Tasks

| **ID**  | **Task**         | **Energy** | **Priority** | **Status** | **Notes** |
| ------- | ---------------- | ---------- | ------------ | ---------- | --------- |
| proj-01 | task description | Low        | P2           | Open       | —         |
| ```     |                  |            |              |            |           |



Energy: High / Med / Low. Priority: P1 / P2 / P3. Status: Open / Done. Task IDs use scoped prefix: `[short-id]-01`, `[short-id]-02`, etc., incrementing.



------

## [project]-resources.md

\```

# [project] Resources

| **Title** | **Description** | **Path**         |
| --------- | --------------- | ---------------- |
| Label     | What it is      | url or file path |
| ```       |                 |                  |



------



FILE: ProjectOS/_rules/ideas-processing.md

# Ideas Processing Rules

Run these rules when the user says "process ideas."



Source file: `ideas.md` at the root of your TaskSystem directory.



------

## Entry Types

| **Entry format**                      | **Action**                                                   |
| ------------------------------------- | ------------------------------------------------------------ |
| Loose bullet with no `#short-id` tag  | Skip — leave in place                                        |
| Single bullet tagged `#short-id`      | Append to `[project]-ideas.md`                               |
| `#short-id` block (multiple bullets)  | Append each bullet to that project's ideas file              |
| Category + `#short-id` block          | Append as grouped entry with category label preserved        |
| `[short-id]-[category]` compound tag  | Create new row in PROJECTS.md ## Seed and add to ##  Short-Ids |
| `## Project-name` header with bullets | Seed new project at Seed stage, create  `[project]-ideas.md` |
| `## Project-name` header, no bullets  | Create Idea stage row in PROJECTS.md only (no directory)     |
| `## Project-name` already exists      | Abort with message: "project already exists — use  tagged bullets instead" |



------

## Short-Ids Section

\-    Maintained by Claude at the top of `ideas.md`.

\-    Auto-updated when projects are created or removed.

\-    Read-only for the user — Claude manages this list.



------

## Naming

\-    Project names are lowercase-hyphenated: `my-project`

\-    Format in PROJECTS.md: `my-project — brief description`



------

## After Processing

Report what was routed where. Leave untagged loose bullets in place — they are not ready to be assigned yet.



------



FILE: ProjectOS/[Q5-project-name]/[Q5-project-name]-ideas.md



Derive one open question about this project from Q5's description.

# [project name] Ideas

\-    [open question derived from Q5 description]



------



FILE: ProjectOS/[Q5-project-name]/[Q5-project-name]-tasks.md

# [project name] Tasks

| **ID**  | **Task**                                 | **Energy** | **Priority** | **Status** | **Notes** |
| ------- | ---------------------------------------- | ---------- | ------------ | ---------- | --------- |
| [Q6]-01 | Define initial scope and first milestone | Med        | P2           | Open       | Seed task |



------



FILE: ProjectOS/[Q5-project-name]/[Q5-project-name]-resources.md

# [project name] Resources

| **Title** | **Description** | **Path** |
| --------- | --------------- | -------- |
|           |                 |          |



------



Step 4: Finalize

#### If Q5 was answered, tell the user:

"[Q7], your TaskSystem is live.



'give me today'



— get your focus list (I'll ask your energy level)



'add task: [description]'



— add something to the board



'process ideas'



— route anything in ideas.md to your projects



You have [N] recurring tasks and one active project: [Q5 name].



Type 'give me today' to start."

#### If Q5 was skipped, tell the user:

"[Q7], your TaskSystem is live.



'give me today'



— get your focus list (I'll ask your energy level)



'add task: [description]'



— add something to the board



'seed project [name]'



— add your first real project when ready



You have [N] recurring tasks. I've set up example-project as a placeholder to show the structure — replace it with your first real project when ready.



Type 'give me today' to start."



------



david vogel\David and Jake's Picks V2\I run four phases before any AI builds anything\I run four phases before any AI builds anything.md



I run four phases before any AI builds anything.



📝 What this is: A four-phase planning methodology (Brainstorm, Plan, Hand off Doc, Dispatch) that front-loads all thinking before any AI generates code or content.



💡 Why it matters: If you skip structured planning and jump straight to prompting, you spend 90% of your time babysitting outputs instead of getting clean results on the first pass.



🏷️ Tags: workflow-design, prompting, folder-architecture, templates, ai-philosophy



⏱️ 5 min read | 🔓 Free



✍️ David's note: Ari nails the thing most people get backwards — the build is the easy part, the thinking is the work. This four-phase approach maps cleanly onto the folder architecture we teach and proves why CONTEXT.md and spec docs exist. If you keep getting garbage outputs, the fix is upstream.



------



david vogel\David and Jake's Picks V2\I run four phases before any AI builds anything\advisor-driven-development.md



------



description: Advisor-driven development — Opus plans, cheap models execute, escalation on complexity



argument-hint: "[task or plan] — what to build, fix, or execute"



Advisor-Driven Development



You are the



(Opus). You plan, review, and provide strategic guidance. You dispatch



executor subagents



(Haiku or Sonnet) for all file I/O, code generation, and mechanical work. When executors hit complexity, they escalate back to you for guidance.



This mirrors Anthropic's advisor tool pattern — but inside Claude Code. Opus stays in the orchestrator seat. Cheap models burn through the mechanical turns. You only spend Opus tokens on judgment.



Read and understand the task or plan provided. If a file path is given, read it. If it's a description, internalize it.



Dispatch paths



New default: background dispatch via



dispatch.py



Main Opus session



fires detached workers and keeps talking to Ari. Workers log to files, surface



questions through a file-based protocol, and the main session calls



dispatch.py questions



on each turn to surface anything pending.



Four paths for getting work done. Mix freely in parallel — they don't conflict.



dispatch.py start



— spawn a detached Claude Code worker in the



background.



The new default for all executor work.



python3 tools/dispatch.py start --executor <minimax|haiku|sonnet> --task-file --cwd --label



Returns a worker id immediately (well under a second). The main session



never blocks.



The executor runs one of the three wrappers in path 3 below under the



hood, fully detached, with its stream-json log going to



~/dispatch/logs/.log



Workers that need Ari's judgment write a structured question file to



~/dispatch/questions/.md



and exit with



Status: NEEDS_GUIDANCE



(code 2). See "Checking for questions" below.



Never dispatch with



pointing at the main checkout root.



tool refuses this. Use a worktree, subdir, or other workspace.



— Claude models (



), full Claude Code tool



access in-process,



Agent({ model: "haiku"|"sonnet", description, prompt })



Use for: truly trivial inline tasks (a 1-line rename) or when you need



the result synchronously because the next step depends on it. Prefer path



1 whenever possible — the main session context window is precious and



in-process Agent calls burn it.



Executor wrappers directly



mmx_claude.sh



haiku_claude.sh



sonnet_claude.sh



. Synchronous headless



calls. Use these when



you want to wait for a result inline, not when you want to dispatch in the



background. All three share



_claude_exec.sh



as their body.



bash tools/mmx_claude.sh --cwd --task ""

#### Exit codes:

DONE / DONE_WITH_CONCERNS,



NEEDS_GUIDANCE,



claude-side failure,



wrapper error.

#### Why M2.7 is default among the three:

benchmarks (GDPval-AA 1495,



MLE-Bench-Lite 66.6%, SWE-Pro 56.22%) put it Sonnet-adjacent. Haiku is



reserved for trivial renames / format fixes. Sonnet is reserved for



judgment-heavy coding that M2.7 escalated.



— any provider, text-in/text-out, no file access.



python3 tools/ask.py -m "prompt"



Use for: non-code text, research, second opinions, video (gemini), bulk



generation (gemma), long-context docs (kimi).



Parallel dispatch example (all four paths in one message block)



[Bash("python3 tools/dispatch.py start
 --executor minimax
 --task-file /tmp/task-1.md
 --cwd .claude/worktrees/feat-x
 --label impl-foo")]                           # path 1 (default) [Agent(model="haiku", description="rename foo→bar", prompt="Rename foo → bar in src/util.ts, no other changes")]       # path 2 (inline, rare) [Bash("bash tools/mmx_claude.sh
 --cwd .claude/worktrees/feat-y
 --task 'Implement /api/bar endpoint per spec.md'")]           # path 3 (synchronous) [Bash("python3 tools/dispatch.py start
 --executor opus
 --thinking max
 --task-file /tmp/task-arch.md
 --cwd .claude/worktrees/feat-z
 --label arch-review")]                          # path 1, opus, max thinking [Bash("python3 tools/ask.py -m kimi-swarm
 'Research OFX plugin distribution landscape'")]             # path 4



Path 1 returns a worker id and exits in <1s; the main session moves on. The



worker's final output lands in a log file under



~/dispatch/logs/



. Next turn, call



dispatch.py questions



to surface anything blocked on Ari.



Model Selection Rules



Coding Tasks



Trivial (1-line edits, rename, format)



Agent tool OR



dispatch.py start --executor haiku



Cheap, fast, sync or async



Simple → medium (1-3 files, clear spec)



dispatch.py start --executor minimax



Default background executor — Sonnet-adjacent brain, fraction of the cost



Complex (multi-file, refactor)



dispatch.py start --executor minimax



First swing, escalate to Sonnet on BLOCKED



Deep reasoning / ambiguous design



dispatch.py start --executor sonnet



Judgment-heavy coding, M2.7 escalation target



Self-improvement cycles



dispatch.py start --executor opus --thinking max



Opus-only — never delegate harness-wide judgment to cheaper brains



Architecture, planning, review, surfacing



You (Opus in main session)



Never delegate judgment calls that shape the conversation

#### Dispatch paths:

dispatch.py start --executor



— default, background, invisible. Returns a worker id in <1s. Questions surface via the UserPromptSubmit hook automatically. All four wrappers (



mmx_claude.sh



haiku_claude.sh



sonnet_claude.sh



opus_claude.sh



--add-dir PATH



(repeatable) for extra read/write paths and



--read-only



for tool-list stripping (Write, Edit, MultiEdit, NotebookEdit all become

#### No such tool available

--dangerously-skip-permissions



is the default so workers don't stall on approval prompts.



Agent tool (foreground)



— synchronous, blocks main session. Keep for trivial inline tasks where async overhead > savings.



— text-only, no file access. For cheap second opinions, kimi-swarm research, gemma local inference.



Read-only review example



(won't modify any files):



dispatch.py start
 --executor sonnet
 --cwd /private/tmp/review-\ --add-dir ~/proj/tools \ --read-only \ --task-file /tmp/review-task.md

#### Code via ask.py (text-in/text-out):

Still available for



when you want a second opinion or a non-Anthropic perspective. Model returns text; you place it into files yourself. No file access, cheapest path.



Opus thinking tier

#### When dispatching

--executor opus



--thinking



to scale extended-thinking budget. Aliased onto Claude Code's native



flag. Default:



When to use



Opus chosen for context/judgment, task itself mechanical (small-diff review, format normalization)



Multi-file refactor, ambiguous bug fix, plan critique



Architecture decisions, rule-system changes, anything where being wrong propagates



Self-improvement cycles, breaking-change migrations, security-sensitive code paths



Escalation on



re-dispatch one tier higher with the previous failure context baked into the new task prompt. Sequence:



mid → high → highx → max → giveup



, take the task back into the main session or decompose it. Tier is



auto-bumped by



dispatch.py answer



— escalation is an explicit decision.



NEEDS_GUIDANCE



is not by itself a tier-escalation signal. Re-dispatch at the same tier with the answer baked in unless the failure looks reasoning-bound rather than information-bound.



Non-Code Tasks



Complex multi-step research



Extended reasoning, deep analysis



Long-context (large docs, transcripts)



Video analysis (scenes, pacing, edit review)



ask.py --video



Second opinion from different model family



Drafts, copy, captions, reformatting



Bulk generation (many items)



(Ollama, free)



python3 tools/ask.py -m "prompt" python3 tools/ask.py -m -s "system prompt" "prompt" echo "long prompt" | python3 tools/ask.py -m --stdin python3 tools/ask.py -m gemini --video clip.mp4 "prompt"



Fast, file access via Agent tool



Best Claude coder below Opus, file access



Structured output, native video, different perspective



128k context, fast, cheap



Extended reasoning mode



Single agentic loop



Up to 100 parallel sub-agents, research



Sonnet-adjacent on SWE-Pro/MLE, cheap; use via



mmx_claude.sh



for file tasks



Local Ollama



26B MoE, 256k context, multimodal



gemma-small



Local Ollama



4B, fast lightweight



Choosing the Right Model

#### For code — decision tree:

Is it a one-line edit / rename / format? →



via Agent tool.



Anything bigger that needs file access? →



mmx_claude.sh



(the default).



Did M2.7 escalate with BLOCKED or NEEDS_GUIDANCE on a design question? →



via Agent tool, with the decision baked in.



Is it pure text / research / second opinion / video? →



Video Analysis (Gemini)

#### Gemini natively accepts video — no frame extraction needed. Use it for:

Reviewing edits and rough cuts



Generating scene descriptions and shot lists



Content review before posting



Analyzing pacing, transitions, color grading



Extracting spoken content from clips

# Describe what happens in a video

python3 tools/ask.py -m gemini --video clip.mp4 "Describe each scene, noting camera movement, subjects, and mood"

# Review an edit

python3 tools/ask.py -m gemini --video rough_cut.mp4 "Review this edit for pacing. Note any cuts that feel too fast or too slow. Suggest improvements."

# Generate a shot list

python3 tools/ask.py -m gemini --video footage.mov "Create a timestamped shot list with scene descriptions, shot types, and any visible text"

# Content review for social

python3 tools/ask.py -m gemini --video reel.mp4 "Is this suitable for Instagram? Check for: visual quality, pacing for mobile, hook in first 3 seconds, any issues"



The video is uploaded to Gemini's Files API, processed server-side, then deleted after analysis. No frame extraction, no local vision model — Gemini sees the actual video with full temporal understanding.



Kimi Agent Swarm



Kimi K2.5 has a native agent swarm mode — the model automatically decomposes a task, spawns up to 100 parallel sub-agents, executes up to 1,500 tool calls, and aggregates the results. No framework needed — it's model-native.

#### When to use it:

Complex research or analysis tasks that benefit from parallel decomposition. The swarm is automatic — you give it a hard problem and it figures out how to parallelize.



Multi-source research and synthesis



Complex analysis that can be decomposed



Tasks where you'd otherwise dispatch 5+ separate ask.py calls



Broad exploration before you narrow down

#### Not good for:

Tasks that need file access (swarm can't touch your filesystem)



Tasks where you need to control the decomposition (it's automatic)



Simple questions (overkill — use



instant mode)

# Research task

python3 tools/ask.py -m kimi-swarm "Research the current state of OFX plugin development for DaVinci Resolve. Cover: available frameworks, Metal vs CUDA support, plugin distribution, licensing models, and any open-source examples."

# Analysis task

python3 tools/ask.py -m kimi-swarm "Analyze the competitive landscape for AI-powered colour grading plugins. Compare features, pricing, and user reviews across all major options."

# Extended reasoning (single agent, not swarm)

python3 tools/ask.py -m kimi-think "Given these constraints [paste constraints], what architecture would you recommend and why?"

#### Kimi modes quick reference:

| Mode | Flag | Use case | Speed |



|------|------|----------|-------|



| Instant |



| Simple questions, fast drafts | Fast |



| Thinking |



| Complex reasoning, analysis | Moderate |



| Single-thread agentic task | Slow |



| Parallel decomposition, research | Slowest (but most thorough) |



Default to M2.7 via



mmx_claude.sh



for code tasks.



Fall back to



(Agent tool) only for trivial one-liners, and escalate to



(Agent tool) only when M2.7 hits a design ambiguity. Use



for pure text, research, second opinions, or local/free generation via



Local Models (Ollama — free, private, offline)



Gemma 4 (26B MoE) runs locally on this Mac (M1 Max, 64GB). No API key, no cost, no data leaves the machine.

# General text generation

python3 tools/ask.py -m gemma "Draft 3 caption options for this photo: [description]"

# Fast lightweight tasks

python3 tools/ask.py -m gemma-small "Reformat this JSON: {raw json}"



Good for: drafts, reformatting, classification, simple analysis, privacy-sensitive content, offline work, bulk generation where API costs would add up.



Not good for: complex reasoning (use kimi-think or sonnet), tasks needing current web knowledge (use gemini or kimi-swarm).



Checking for questions (do this on every turn)



Background workers surface decisions through file-based questions. The main



Opus session must check for them at the start of each response generation.

#### Convention (not enforced, but load-bearing):

python3 tools/dispatch.py questions



before your first real action in each turn



whenever you have



live background workers. If the output is



(no unresolved questions)



normally. If it contains one or more worker question blocks, surface them to

#### Ari near the top of your response using this shape:

## 🛎️ Background worker questions

### w-a3f2-impl-foo (executor=minimax)

task: Implement /api/foo endpoint per spec.md where stuck: JWT vs random hex — both patterns exist in this codebase



**Question:** Which token format should the reset flow use?



**What would unblock:** One of "jwt" or "hex", with a one-line reason if the choice affects how I wire up the lookup.



Surfacing rules (non-negotiable)



Queue per turn, never mid-message.



If a question surfaces between



responses, don't jam it into the message you're already writing. Show it



Group by worker.



One section per worker, even if the worker asked



multiple sub-questions. Keeps Ari's attention on one task at a time.



Verbatim is fine.



Don't paraphrase the question body — Ari reads the



worker's own words best. Strip the YAML frontmatter, keep the four sections.



dispatch.py answer



Compose Ari's answer



into a new task, re-dispatch a fresh worker, print the new worker id.



Never edit the old worker's log or try to "continue" the old session.

#### The Process

1. Plan (you do this — never     delegate planning)



Break the work into discrete, independent tasks



For each task, decide: haiku or sonnet?



Identify ordering constraints (what blocks what)

#### Create a TodoWrite checklist

1. Dispatch Executors



For each task, dispatch a subagent using the executor prompt template below. Key rules:



One task per subagent.



Fresh context each time.



Provide everything the subagent needs



in the prompt — file paths, specs, code snippets. Don't make them search.



Parallel by default.



Dispatch multiple subagents simultaneously whenever tasks don't touch the same files. Send all independent Agent calls in a single message block. This is the main speed advantage — 5 tasks in parallel finishes in the time of 1.



Mix dispatch paths in parallel.



You can dispatch Agent tool subagents and ask.py Bash calls in the same message. A Haiku subagent editing file A, a Sonnet subagent editing file B, and an ask.py call to Kimi for research — all at once.



Only serialize when there's a real dependency.



Task B reads a file Task A writes? Wait. Task B is in a completely different directory? Ship it.



ask.py calls are always safe to parallelize



— they're text-in/text-out with no file access, so they never conflict with anything.



1. Handle Escalations

#### Executors report one of four statuses:

— Move to review.



DONE_WITH_CONCERNS



— Read the concerns. If they're about correctness, address before review. If they're observations, note and proceed.



NEEDS_GUIDANCE



— The executor hit something that requires judgment. This is the advisor pattern in action:



Read what they tried and where they're stuck



Think through the strategic decision (architecture, approach, tradeoffs)



Re-dispatch with your guidance baked into the prompt: "Use approach X because Y. The relevant pattern is in [file] at [line]. Here's how it should connect..."



Same model unless the task complexity has genuinely increased



— The task is beyond the executor's capability:



If it's a context problem → provide more context, re-dispatch same model



If it needs more reasoning → upgrade to



→ do it yourself)



If the task is too large → break it down further



If the plan is wrong → revise the plan



1. Review (you do this —     never delegate final review)

#### After each task completes:

Read the subagent's report



Spot-check the actual files changed (read key files yourself)



If the work looks wrong, dispatch a fix subagent with specific instructions



Mark the task complete

#### After all tasks:

Run verification (build, tests, whatever's appropriate)



Do a final review pass yourself



Executor Prompt Template



The canonical executor prompt lives at



tools/executor_prompt.md



and is shared by both the Agent tool dispatches below and the



mmx_claude.sh



wrapper. When dispatching, substitute



{{CONTEXT}}



{{CONSTRAINTS}}



— do not re-invent the structure.

#### Via Agent tool (haiku / sonnet):

Agent({ description: "Task N: [short name]", model: "haiku", // or "sonnet" prompt: <contents of tools/executor_prompt.md with placeholders filled in> })

#### Via mmx_claude.sh (MiniMax M2.7 — default for simple/medium coding):

bash tools/mmx_claude.sh
 --cwd \ --task "Task N: …full task description with file paths…" \ \[--context-file ctx.md\] \[--constraints-file constraints.md\]



The wrapper reads



executor_prompt.md



, substitutes placeholders, and invokes headless



routed to M2.7. Parse the structured status line from its stdout the same way you parse an Agent report.



Cost Awareness

#### The whole point of this pattern is cost efficiency:

Haiku is ~60x cheaper than Opus



for output tokens



Sonnet is ~5x cheaper than Opus



for output tokens



A 10-task plan where 8 tasks run on Haiku, 1 on Sonnet, and 1 needs your direct attention costs a fraction of doing everything on Opus



Your Opus tokens go to planning, judgment, and review — the work only Opus can do



When NOT to Use This



— if it's a 2-line edit, just do it yourself. Dispatch overhead > savings.



Deeply coupled work



— if every task depends on every other task, sequential subagents will thrash. Do it yourself or use a single Sonnet subagent for the whole thing.



Exploration/debugging



— if you don't know what's wrong yet, investigate yourself first. Dispatch executors once you have a plan.



Already in a subagent



— don't nest this pattern. If you're an executor, just do your job.



Example Flow (background-first)



User: /advisor Add password reset flow to the auth system



You (Opus): [Read auth system, understand architecture] Plan:



1. Add resetToken +     resetExpiry columns to users table      (dispatch start, minimax)
2. Create     /api/auth/forgot-password endpoint           (dispatch start,     minimax)
3. Create     /api/auth/reset-password endpoint            (dispatch start,     minimax)
4. Add email sending     utility                        (dispatch start, minimax)
5. Create reset password UI     page                      (dispatch start, minimax)



[Dispatch tasks 1 and 4 in parallel — independent, dispatch start × 2. Each call returns a worker id instantly. You keep talking to Ari.] [Ari asks an unrelated question, you answer it inline.]



Next turn: [Call dispatch.py questions.] [Task 2's worker surfaced NEEDS_GUIDANCE: "JWT vs random hex token patterns both exist in this codebase, need a design call."] [You show Ari the question block near the top of your response. Ari replies: "random hex, simpler and safer."] [You call dispatch.py answer w-a3f2-impl-reset --answer "random hex, simpler and safer" — a fresh worker spawns with the answer baked in.] [Meanwhile task 1 and 4 have completed; you check their logs, review, move on.] [Trivial one-liner at the end (rename a constant) → inline Agent tool on haiku.] [Review all changes yourself.]



The whole flow happens without Ari ever opening a new Claude window, pasting



anything, or watching a long-running task. Main session stays on Opus and in



the orchestrator seat. Execution is invisible.



Integration with Other Skills



superpowers:writing-plans



first if the task needs a detailed plan



superpowers:using-git-worktrees



for isolation



Executors should follow



superpowers:test-driven-development



when writing code



After all tasks, use



superpowers:verification-before-completion



before claiming done



------



david vogel\David and Jake's Picks V2\I run four phases before any AI builds anything\crush-architecture.md



------



workspace: crush



role: reference



CRUSH_ Architecture Reference



Full technical architecture, effect details, struct layouts, gotchas. Referenced from [[CRUSH_/CLAUDE|CRUSH_ CLAUDE.md]] — load on demand during development.



------



Architecture



The .crush Build-Time Generator



Effects are authored as



JSON files (UI param definitions + shader references) in



. The Python



script generates all C++ OFX boilerplate at compile time — parameter definitions, uniform bindings, visibility logic, effect registry, and param fetch dispatch for all 6 effect slots.



C++17, Objective-C++, Metal Shading Language (MSL), Python (generator)

#### Graphics API:

Apple Metal (zero-copy GPU pipeline)

#### Host Target:

DaVinci Resolve (OpenFX). After Effects port deferred.



6-Slot Effect Chain



The plugin supports up to 6 chained effects in a single instance with progressive reveal:



dropdown — primary effect (slot 1, always visible, no "None")



dropdowns — chain slots (default "None", hidden until previous slot is populated)



When user sets Effect 2, Effect 3 dropdown appears. Set Effect 3, Effect 4 appears. Up to 6.



Rendering: N-pass chain. Each pass reads from the previous pass's output (dst buffer).



DECIMATE applies ONLY on the final pass, after all chained effects.



Global Controls (always visible, not per-effect)



(0-1) — directional pixel melt. Per-column/row drip offset from multi-octave noise, chromatic aberration, black data loss for off-frame pixels. Full color preservation — source pixel taken exactly, no decay.



DECIMATE Direction



— Down, Up, Left, Right



(toggle) — deterministic random effect cycling. Picks from 11 safe effects (skips Slit-Scan, Digital Feedback, Depth-Splatting). Per-effect constrained param ranges prevent white frames.



SPAZ Intensity



(0-1) — 0 = mild params + long bursts, 1 = extreme params + short bursts



(toggle) — slow breathing intensity modulation. Layered sine waves scale all param values toward zero and back. Self-animating.



CHILL Speed



(0-1) — 0 = glacial (10+ sec cycles), 1 = moderate (2-3 sec cycles)



Generated Files (do not hand-edit)



files and generates into



src/generated/



EffectRegistry.gen.h



— plugin identity, effect enum, slot dropdown defines, global param defines, kMaxSlots



ParamDefs.gen.h



— all parameter #defines for all 6 slots ("" = slot 1, "C2"-"C6" prefixes)



ParamBindings.gen.h



— per-effect uniform structs



VisibilityLogic.gen.cpp



crushSetParamVisibility()



crushSetParamVisibility_C2()



crushDefineParams()



FetchDispatch.gen.cpp



crushFetchParams()



crushFetchParams_C2()



switch dispatch



N-Slot Plugin Architecture



CrushPlugin.cpp



, slot functions are dispatched via arrays:



static VisibilityFn s_VisibilityFns[kMaxSlots] = { crushSetParamVisibility, _C2, _C3, _C4, _C5, _C6 }; static FetchFn s_FetchFns[kMaxSlots] = { crushFetchParams, _C2, _C3, _C4, _C5, _C6 }; static const char* s_SlotParamNames[kMaxSlots] = { kParamEffectSelect, _2, _3, _4, _5, _6 };



The render loop iterates active slots, each creating a CrushProcessor pass.



------



Effects (14 total)



Key Technique



Bilinear-sampled UV displacement per channel



Pixel Sorting



Directional luma-weighted displacement with per-row noise



Macroblocking



floor() UV quantization with posterization



Datamoshing



Simulated motion vector accumulation



VHS Tracking



Sine noise + YIQ chroma degrade



Scanline Jitter



Row-based hash noise offset



Y-axis temporal offset (temporal, max 28 frames, per-buffer binding)



Screen Tearing



Horizontal sync-split



Turbulent Displacement



2D FBM noise UV warp



Digital Feedback



Blend with previous frame + scale/rotation (temporal)



Depth-Splatting



Luma-as-depth parallax, S-curve compression, voxel snap, soft point rendering



GITS-style directional streak corruption with Fight self-animation



CMYK plate separation with bilinear sampling, per-plate directional offset



Point Cloud



Particle dissolution with FBM-driven organic scatter, flyaway gravity physics



DECIMATOR Detail (Effect 12)



The flagship. Per-column/row vertical streaking with direction control, chromatic channel separation. Sub-effects:



Dissolution



— posterizes pixel data (reduces bit depth) + per-channel noise. NOT black pixels — actual data degradation.



— 7×7 neighborhood screen blend bloom. Never clips to white.



— horizontal banding with random dark bands



— self-animating signal struggle. Three layered sine waves (0.4, 0.17, 0.07 Hz) modulate overall intensity. Slider controls bias: 0 = fully corrupted, 0.5 = equal war, 1 = signal winning. Whole frame breathes together — no patches, no flicker.



Point Cloud Detail (Effect 14)

#### Dissolves image into living, breathing soft particles. Key design decisions:

Analog feel



— particles jittered off the grid (90% cell offset), FBM noise for drift (not sine waves), each particle has unique timing from its cell seed



— particles break free with random burst direction + quadratic gravity (feels physical). Each particle has a random "break threshold" — as Flyaway increases, more particles detach progressively.



— flying particles shrink with distance (



1 / (1 + distance * 1.5)



) + alpha fade. Creates perspective.



Gravity direction



— user-controllable angle (270° = down). Particles can travel across the entire frame, not bounded by source region.



Depth Scatter



— dark regions scatter more, bright areas hold together. Creates the dissolving-from-shadows look.



Wide search radius



— up to 8 cells in each direction to find particles that have scattered/flown far.



------



Source Files



Core (hand-authored)



src/core/CrushPlugin.h/.cpp



— OFX effect class. N-slot render loop, SPAZ random logic, CHILL modulation, progressive slot reveal via



changedParam



. Function pointer arrays dispatch per-slot visibility/fetch.



src/core/CrushProcessor.h/.cpp



— OFX ImageProcessor subclass. Routes to Metal or CPU. Holds CrushRenderParams struct and temporal frame pointers (max 28).



src/core/MetalKernel.mm



— ALL Metal shader code as inline C strings:



— hash, noise, FBM, bilinear sampler (



crush_sample



kMasterKernelSource



— all 14 effect shaders + DECIMATE post-process + CrushKernel dispatch



kTemporalKernelSource



— CrushFeedbackKernel (effect 10) + CrushSlitScanKernel (effect 7)

#### Pipeline caches:

s_CrushPipelineMap



s_CrushTemporalPipelineMap



Build System



CMakeLists.txt



— CMake 3.15+, C++17, universal binary (arm64+x86_64), .ofx.bundle output



— macOS bundle metadata



— Python generator. 6-slot architecture (



MAX_SLOTS = 6



). Generates visibility, fetch, and param definitions for all slots.



------



CrushRenderParams Struct Layout (must match Metal shader struct)



int effectId, width, height, temporalFrameCount float time, frame, disintegrate int decimateDir // 0=down, 1=up, 2=left, 3=right float values[16]   // effect params (float) int intValues[16]  // effect params (int, parallel to values[])



------



Key Constraints & Gotchas



Canonical source. Shared subset extracted to [[ofx_metal_gotchas]] for CBA_, FUZZ_, SUBTRACKT_, GRAPHFX_.



OFX / Metal



setGPURenderArgs(p_Args)



is MANDATORY



— without it,



_pMetalCmdQ



is garbage and Metal crashes Resolve.



Don't add grouped params to the page



page->addChild(*group)



. Individual params use



setParent(*group)



only. Double-registration crashes Resolve.



Metal buffer casting



— OFX pixel pointers ARE Metal buffer objects.



reinterpret_cast<id>(float\*)



No pointer-to-pointer buffers



— for temporal frames, bind each as separate buffer index (3-30, max 28).



Pipeline state caching



— cache per



MTLCommandQueue



with mutex. Compile once, reuse.



fastMathEnabled



deprecated in macOS 15



@available(macOS 15.0, *)



Visibility on load



— set initial state in constructor. Hide slots 2-6 dropdowns too.



codesign --force --sign -



post-build. Unsigned = won't load.



Bounds checking



if ((id.x >= w) || (id.y >= h)) return;



first line of every kernel.



Thread group size



threadExecutionWidth



, don't hardcode.



setOpen(true)



— so they appear expanded when the user selects them.



Shader Development



Color preservation



— never decay/multiply colors. Source pixel taken exactly.



Bilinear sampling



crush_sample()



for all displaced UV lookups. Integer truncation causes visible banding/stairstepping when effects are stacked.



— "content falls DOWN" = sample from



py + dripDist



. Think "where does the replacement come from."



Per-column noise



— multi-octave hash for jagged edges. Gap columns stay clean.



Self-animation



— layered sine waves at irrational ratios (0.4, 0.17, 0.07). Modulate intensity, not regions.



Analog, not digital



— FBM noise for particle drift, jitter off grid, smooth continuous motion. Sine waves feel robotic. FBM feels alive.



SPAZ safety



— skip temporal effects (7, 10) and Depth-Splatting (11). Constrain ranges per-effect.



Dissolution = posterize, not dim



— reduce bit depth + channel noise. Never



result.rgb *= 0.5



Glow = screen blend



1 - (1-a)(1-b)



. Never additive



which clips to white.



Depth splatting centering



— depth mapped as



(luma - 0.5) * 2.0



so mid-grey = zero displacement. S-curve compression prevents pinching at extremes.



Point size visibility



— quantize output to cell grid, not blur around sample point. Each cell renders as one visible point with the cell center's color.



Shader compilation failure = white frames



— if Metal shader has undefined variables, it fails silently and everything renders white. Check for stale variable references after refactoring.



DaVinci Resolve Specifics



Plugin appears under CRUSH_ grouping



in OpenFX panel.



Restart Resolve



after every install — plugins cached at startup.



OFX plugins directory



/Library/OFX/Plugins/



~/Library/OFX/Plugins/



Maximum 31 Metal buffer bindings



(indices 0-30).



------



Adding a New Effect



src/crush/new_effect.crush



with JSON schema (see existing files)



Add shader function to



MetalKernel.mm



kMasterKernelSource



crush_effectname()



to the switch in



CrushKernel



If adding to SPAZ: update



safeEffects[]



in CrushPlugin.cpp with constrained param ranges



python3 build.py



— generates all 6 slots of params, visibility, fetch



cmake --build build

#### Install and restart Resolve

------



david vogel\Developer Resources\ADVANCED Coding Best Practices.md



ADVANCED: Coding Best Practices



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



The 1,000-line limit applies to code only. Documentation comments, file headers, and inline documentation do NOT count toward this limit. This limit exists to enforce efficient, concise code — not to punish well-documented code.



Prefer more files with fewer functions each



Every function in a file must logically belong there — don't put camera rotation functions in a text editor file



Split where it makes semantic sense, not just to hit a number



The folder nesting structure exists to support these smaller units



Library-First Design



Write all code as if every function could be extracted into a standalone library. The end goal is maximum reusability across projects.

#### Principles:

Functions should be self-contained with minimal external dependencies



Clean, well-defined interfaces — inputs and outputs should be obvious



Avoid hard-coded project-specific values inside reusable logic — pass them as parameters



Group related functions that could form a library into their own files/modules



In any language that supports libraries (C, Rust, JS/TS, Swift, etc.), structure code so extraction into a library requires moving files, not rewriting them



For C specifically: This is the primary target. Every utility, algorithm, data structure, and system abstraction should be written as a reusable library from day one. Headers define the public API contract, source files contain the implementation. A well-written C library can be linked into any project.



No Auto-Save / No Background Persistence



Every write to a database, file, or storage must trace back to a deliberate user action. No exceptions unless explicitly requested.

#### Never implement:

Auto-saving as the user types



Debounced save on input change



Watchers that persist reactive state changes



Background sync intervals



Persisting UI state automatically (sidebar position, tab selection, scroll)



Writing to storage on mount/unmount/navigation

#### Always require:

User clicks "Save" → write



User submits form → persist



User explicitly toggles setting → save



User confirms action → execute



Pattern: User Action → Service Call → Write → Confirm Success



Folder Nesting as Navigation



Directories are not just organization — they're how you navigate. The tree structure should let you drill down to the right file by following a logical path, not by guessing or searching.

#### Principles:

Group by domain/feature, not by file type (prefer auth/authService.ts over services/auth.ts when the module is complex enough)



Each directory should have a clear, single purpose



Nesting depth should match conceptual depth — don't nest just for nesting, don't flatten when there's real hierarchy



A directory with 1 file is usually wrong — either the file belongs in the parent or more files belong in the directory



Error Transparency



Never swallow errors silently



Catch at service boundaries where you can show user feedback



Log technical details (console.error with context)



Show human-readable messages to users — never raw errors, stack traces, or technical details



If you catch it, either handle it meaningfully or log it. Never empty catch blocks.



Delete Dead Code



Don't comment out code. Don't leave unused functions, imports, or variables. If it's not being used, delete it. Git has the history if you ever need it back.



Inline Code Documentation



Every source file carries its own documentation. This gives both the developer and Claude immediate context the moment a file is opened — no hunting through separate docs.



File Header — Always Present



Every source file MUST have a header block at the top with three sections: status, issues, and todo. All three sections are always present, even when empty. The empty slots serve as a reminder that documentation can go there — if the sections aren't present, they get forgotten.

#### Template (JS/TS/Vue):

@file DescriptiveFileName



@description What this file is for and what it does (1-3 concise lines)



@status None



@issues None

#### Template (Rust):

//! # DescriptiveModuleName



//! What this module is for and what it does (1-3 concise lines)



//! ## Status



//! ## Issues



//! ## Todo

#### Template (C — header files):

@file descriptive_name.h



@brief What this header defines and its purpose (1-3 concise lines)



@status None



@issues None

#### Template (C — source files):

@file descriptive_name.c



@brief Implementation of [what this file implements]



@status None



@issues None

#### Template (Swift):

/// # DescriptiveFileName



/// What this file is for and what it does (1-3 concise lines)



/// ## Status



/// ## Issues



/// ## Todo

#### When there IS something to document:

@file AvatarUploadService



@description Handles user avatar upload, validation, and storage.



Supports JPEG, PNG, and WebP formats up to 10MB.



@status Avatar upload works but no progress indicator yet



@issues Timeout on large files (>10MB) — needs chunked upload



[ ] Add upload progress bar (blocked on chunked upload)



[ ] Validate image dimensions before upload

#### What each section means:

SectionPurposeExample@statusCurrent state of the code — what works, what's partial"Core CRUD works, batch operations not yet implemented"@issuesKnown bugs, performance problems, fragile areas"Race condition when two users edit simultaneously"@todoIncomplete work left during a session — breadcrumbs"- [ ] Add input validation for email field"



File Header Cleanup Rule



When working in any file, always check the header first. If there are completed TODOs, resolved issues, or outdated status notes — clean them up. Reset sections to "None" when everything is addressed. This prevents documentation rot.



File-Level TODOs Are Breadcrumbs



The @todo section in file headers is NOT the project plan. The real task tracking lives in plan files and .teamide/tasks/. File-level TODOs exist for the "mid-session, had to step away" situation:



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



The core principle is the same everywhere: categorical nesting by domain, with descriptive names, keeping files small and focused. Here's how that maps to each language ecosystem.



JavaScript / TypeScript (Vue, Quasar, Node)



├── modules/          # Feature modules (self-contained)



│  ├── auth/



│  │  ├── index.ts      # Module entry, re-exports



│  │  ├── store.ts      # Pinia store (composition API)



│  │  ├── api.ts       # API calls for this module



│  │  ├── types.ts      # Types/interfaces for this module



│  │  ├── AuthLogin.vue    # Components named descriptively



│  │  ├── AuthRegister.vue



│  │  └── components/     # Sub-components if needed



│  │    └── AuthFormField.vue



│  └── dashboard/



│    ├── index.ts



│    ├── store.ts



│    ├── api.ts



│    └── DashboardOverview.vue



├── services/          # Shared services (API client, DB, etc.)



│  ├── apiClient.ts      # Centralized fetch wrapper



│  ├── db/



│  │  ├── client.ts



│  │  └── tables/



│  │    ├── userSettings.ts



│  │    └── sessionHistory.ts



│  └── fileWatcher.ts



├── stores/           # Global stores (app-wide state)



│  └── globalAppState.ts



├── components/         # Shared components (used across modules)



│  ├── AppHeader.vue



│  └── ConfirmDialog.vue



├── composables/        # Shared composables



│  └── useWindowResize.ts



├── types/           # Global types



│  └── appTypes.ts



├── layouts/          # Page layouts



├── pages/           # Route pages



├── router/           # Vue Router config



├── boot/            # Startup/init files



├── css/            # Global styles



└── utils/           # Platform detection, formatters



└── platformDetection.ts

#### Key conventions:

Each feature module has index.ts, store.ts, api.ts, types.ts



Components are PascalCase: UserProfileCard.vue



Everything else is camelCase: apiClient.ts, useAuth.ts



Path aliases: @/ for src/, @modules/, @components/, @stores/

#### Apply the same categorical nesting using Rust's module system:

├── main.rs             # Entry point, minimal — just init and run



├── app.rs             # Application setup, config, state



├── lib.rs             # Library entry (if crate is also a lib)



├── commands/            # Tauri commands or CLI handlers



│  ├── mod.rs           # Re-exports all command modules



│  ├── file_operations.rs     # File read/write/watch commands



│  ├── window_management.rs    # Window creation/positioning



│  └── backend_lifecycle.rs    # Start/stop/health-check backend



├── services/            # Business logic, reusable across commands



│  ├── mod.rs



│  ├── process_manager.rs     # Spawn/kill/monitor child processes



│  ├── port_allocator.rs      # Find available ports



│  └── log_writer.rs        # Write structured logs to files



├── models/             # Data structures, enums, types



│  ├── mod.rs



│  ├── app_config.rs        # Config structs



│  └── backend_state.rs      # Backend process state



├── platform/            # OS-specific code



│  ├── mod.rs           # Conditional compilation re-exports



│  ├── macos.rs          # macOS-specific (menus, notifications)



│  ├── windows.rs



│  └── linux.rs



└── utils/             # Small, focused helpers



└── path_resolver.rs      # Resolve app paths, home dir, etc.

#### Key conventions:

mod.rs in each directory for re-exports (like index.ts)



snake_case for everything: files, functions, variables, modules



Descriptive module names: backend_lifecycle.rs not backend.rs



Keep main.rs thin — delegate to app.rs or modules immediately



Group by responsibility, not by Rust convention alone



Include lib.rs when the crate should be usable as a library



Follow categorical nesting for headers, with source files mirroring the structure. Every module should be structured for library extraction from day one.



include/              # Public headers (categorical nesting)



├── core/              # Core functionality



│  ├── memory_allocator.h



│  ├── string_operations.h



│  └── error_codes.h



├── arch/              # Architecture-specific



│  ├── arm64.h



│  ├── x86_64.h



│  └── riscv32.h



├── os/               # OS-specific abstractions



│  ├── linux_syscalls.h



│  ├── darwin_syscalls.h



│  └── windows_syscalls.h



├── fmt/              # File format parsers



│  ├── elf_parser.h



│  ├── macho_parser.h



│  └── pe_parser.h



└── sys/              # System-level interfaces



└── thread_pool.h



src/                # Implementation files (mirror include/ structure)



│  ├── memory_allocator.c



│  ├── string_operations.c



│  └── error_codes.c



│  ├── arm64.c



│  └── x86_64.c



├── linux_syscalls.c



└── darwin_syscalls.c



tests/               # Test files (mirror src/ structure)



│  ├── test_memory_allocator.c



│  └── test_string_operations.c



└── integration/



└── test_full_pipeline.c

#### Key conventions:

include/ and src/ mirror each other's structure



Category directories by domain: core/, arch/, os/, fmt/, sys/



snake_case for all file names



Header names describe what's inside: memory_allocator.h not mem.h



One header + one source per logical unit



Headers define the full API contract (see Function Documentation section)



Each category directory is a potential standalone library



Swift (macOS / iOS)



├── App/              # App entry, lifecycle



│  ├── AppMain.swift



│  └── AppDelegate.swift



├── Features/            # Feature modules



│  ├── Camera/



│  │  ├── CameraManager.swift



│  │  ├── CameraPreviewView.swift



│  │  └── CameraPermissions.swift



│  └── Recording/



│    ├── RecordingSession.swift



│    ├── RecordingOverlay.swift



│    └── RecordingStorage.swift



├── Services/            # Shared services



│  ├── FileStorageService.swift



│  └── NotificationService.swift



├── Models/             # Data models



│  ├── RecordingMetadata.swift



│  └── UserPreferences.swift



├── Views/             # Shared UI components



│  ├── PermissionRequestView.swift



│  └── StatusIndicator.swift



├── Extensions/           # Swift extensions



│  └── DateFormattingExtensions.swift



└── Utilities/           # Small helpers



└── DeviceCapabilities.swift

#### Key conventions:

PascalCase for files (Swift convention), but still descriptive



Feature-based grouping under Features/



CameraPermissions.swift not Permissions.swift — qualify the name



General Pattern (Any Language)

#### When you encounter a new language, apply this structure:

src/ (or equivalent)



├── [entry point]        # Minimal — just init and delegate



├── features/ or modules/    # Self-contained feature units



│  └── [feature_name]/



│    ├── [entry/index]    # Re-exports or module definition



│    ├── [types/models]   # Data structures for this feature



│    ├── [api/handlers]   # External interface (API calls, commands)



│    └── [service/logic]   # Business logic



├── services/          # Shared, cross-cutting services



├── models/ or types/      # Global data structures



├── platform/          # OS/environment-specific code



└── utils/           # Small, focused helpers



Code Style Conventions



Import Organization (JS/TS)

#### Organize imports in 3 groups, separated by blank lines:

// 1. Framework & language imports



import { ref, computed, watch, onMounted } from 'vue';



import { defineStore } from 'pinia';



// 2. Third-party libraries



import { format } from 'date-fns';



// 3. Local imports (project code)



import { useGlobalStore } from '@/stores/globalAppState';



import { request } from '@/services/apiClient';



import type { UserProfile } from './types';



Vue Component Structure

#### Always this order in single-file components:

Store references



Props & emits



Reactive state (ref, reactive)



Computed properties



Methods / handlers



Lifecycle hooks (onMounted, etc.)



Pinia Store Pattern

#### Always use composition API style:

export const useFeatureStore = defineStore('feature-name', () => {



const items = ref<Item[]>([]);



const selectedItem = ref<Item | null>(null);



const isInitialized = ref(false);



// Init guard — prevent double initialization



async function initialize() {



if (isInitialized.value) return;



items.value = await featureApi.loadItems();



isInitialized.value = true;



function selectItem(item: Item) {



selectedItem.value = item;



// Return everything that should be accessible



return { items, selectedItem, isInitialized, initialize, selectItem };



API Layer Pattern

#### Centralized request function + module-level API objects:

// services/apiClient.ts — single fetch wrapper, typed



export async function request



(path: string, options?: RequestInit): Promise



const response = await fetch(



${API_BASE}${path}



headers: { 'Content-Type': 'application/json' },



if (!response.ok) {



const error = await response.json().catch(() => ({ error: 'Request failed' }));



throw new Error(error.error || 'Request failed');



return response.json();



// modules/inventory/api.ts — module-specific API



export const inventoryApi = {



listProducts: (warehouseId: string): Promise<Product[]> =>



/warehouses/${warehouseId}/products



updateStock: (productId: string, quantity: number): Promise



/products/${productId}/stock



method: 'PATCH',



body: JSON.stringify({ quantity })



TypeScript Conventions



Strict mode always on



No any — use unknown with type narrowing instead

#### Discriminated unions with type guard functions:

type EditorTab =



| { type: 'file'; path: string; content: string }



| { type: 'terminal'; sessionId: string }



| { type: 'diff'; leftPath: string; rightPath: string };



function isFileTab(tab: EditorTab): tab is EditorTab & { type: 'file' } {



return tab.type === 'file';



Interfaces for object shapes, types for unions and aliases



PascalCase for types/interfaces, no I prefix (User not IUser)



CSS / Styling

#### Scoped styles in components:
