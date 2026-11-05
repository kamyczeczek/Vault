---
type: Concept
source: "https://www.youtube.com/watch?v=-QFHIoCo-Ko"
title: Full Walkthrough Workflow for AI Coding - Matt Pocock
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Full Walkthrough: Workflow for AI Coding — Matt Pocock








**Structured Notes**

## 1. Core Thesis
- AI is a new paradigm, but **software engineering fundamentals still apply**.
- The same practices that make human collaboration effective—clear alignment, small tasks, feedback loops, modular design—also work well with AI.
- The workshop is a practical walkthrough of Matt’s AI coding workflow:
  - Idea → Grill Me → PRD → Kanban/issues → AFK implementation → QA/code review → team review.
- Exercises are in a repo; the demo uses a course-management platform/CMS.
- Key framing: **Do not treat AI as a specs-to-code compiler.** You must keep a handle on the code. Code is your battleground.

---

## 2. Two Fundamental LLM Constraints

### 2.1 Smart Zone vs. Dumb Zone
- Concept from Dex Hardy / Human Layer.
- LLM attention relationships scale roughly quadratically as tokens are added.
- Early in a conversation, the model is in its **smart zone**.
- After ~40% context usage—or roughly **~100K tokens** in Matt’s experience—it enters the **dumb zone**.
  - Even with 1M context windows, coding quality degrades.
  - Large context is better for retrieval (e.g., “find things in five copies of War and Peace”) than for coding.
- Implication: **Size tasks to stay inside the smart zone.**
  - Don’t let the AI bite off more than it can chew.
  - Break large tasks into small chunks.
- Multi-phase plans are essentially loops. Ralph Wiggum pattern:
  - Write a PRD / describe destination.
  - Tell AI: “Make a small change that gets us closer.”
  - Matt prefers more structure than plain Ralph.

### 2.2 LLMs Are Like the Guy from *Memento*
- LLMs continually forget; they reset to base state.
- Every session has stages:
  1. **System prompt** — always in context. Keep it tiny.
  2. **Exploratory phase** — agent explores codebase.
  3. **Implementation phase**
  4. **Testing phase**
- When you clear context, you return to the system prompt.
- **Compacting** squeezes conversation into a history. Matt dislikes it.
  - Prefers clearing context to get a consistent, repeatable baseline.
- Two constraints to remember:
  1. Smart zone / dumb zone.
  2. Memento-like forgetting → manage context deliberately.

### 2.3 Human-in-the-Loop vs. AFK Tasks
- **Human-in-the-loop**: planning, alignment, grilling, crucial decisions.
- **AFK (away from keyboard)**: implementation can often be delegated.
- Mental model: **Day shift (human planning) / Night shift (AI implementation).**
- Planning must be human-in-the-loop. Implementation can be AFK.

---

## 3. End-to-End Workflow Overview
```
Idea
  ↓
Grill Me (alignment)
  ↓
PRD (destination document)
  ↓
Kanban board / Issues (journey document)
  ↓
AFK agent loop (Ralph-style)
  ↓
QA / Code Review
  ↓
More issues / Team review
```
- Two essential documents:
  - **Destination**: PRD — where we’re going.
  - **Journey**: Kanban/issues — how we get there.
- Planning is human-reviewed. Implementation steps back and lets agents work.
- QA feeds new issues back into the Kanban board.

---

## 4. Grill Me Skill (Alignment Phase)

### Purpose
- Prevent misalignment.
- Reach a **shared understanding** with the AI, not just produce a plan.
- Argues against the **specs-to-code movement** / pure vibe coding:
  - If code is wrong, don’t just edit specs and ignore code.
  - You need to understand and shape the code.
- Frederick P. Brooks, *The Design of Design*: the **design concept** is the shared idea among participants.
  - Matt wants a shared design concept with the LLM.

### How It Works
- Start with a clear context.
- Invoke `/grill-me` and pass in the client brief.
- Skill text (paraphrased):
  - “Interview me relentlessly about every aspect of this plan until we reach shared understanding.”
  - “Walk down each branch of the decision tree.”
  - “Resolve dependencies one by one.”
  - “For each question, provide your recommended answer.”
  - “Ask questions one at a time.”
- Subagents:
  - An explore subagent can burn many tokens in an isolated context window.
  - It reports a summary back to the parent/orchestrator agent.
  - This keeps the parent context smaller.

### Example: Sarah Chen Client Brief
- Course platform “Cadence” has poor retention.
- Students sign up, do a few lessons, drop off.
- Request: add gamification.
- Process:
  - Clear context.
  - `/grill-me` with client brief.
  - AI explores codebase.
  - Asks questions: points economy, retroactive points, levels, streaks, UI location.
  - Matt often accepts AI recommendations or adjusts them.
- Grilling can last 40–100 questions.
- Output is conversation history that acts as an asset: the design concept.
- Can also feed meeting transcripts from domain experts into a grilling session.

### Key Q&A on Grill Me
- **Spec Kit / Open Spec / Taskmaster?**
  Own your planning stack. No clear winner. Maintain observability. Inversion of control.
- **Who should use it?**
  Pair/mob programming with AI. Include domain experts, developers, and AI. Crucial decisions need humans.
- **Does AI stop grilling?**
  You can tune skills to pull back or add stop points.
- **Ask User Questions UI?**
  Matt finds it broken in Claude Code and avoids it.

---

## 5. PRD — Destination Document

### Purpose
- Summarize the design concept.
- Document the destination, not the full journey.
- Shape doesn’t matter much; use company template or Matt’s preferred shape.

### Typical Contents
- Problem statement
- Solution
- User stories (e.g., 18 stories)
- Implementation decisions
- Testing decisions
- **Out of scope** — crucial for definition of done
- Proposed modules to modify

### Write a PRD Skill
- Asks for long detailed problem description.
- Can interview relentlessly again.
- Uses a PRD template.
- Can write PRD without grilling, but Matt prefers grill first, then PRD.

### Matt’s Stance on Reviewing PRDs
- He generally does **not** read the PRD closely.
- Reason: LLMs are great at summarization. Alignment already happened in grilling.
- Reading PRD only tests summarization ability.
- Don’t over-optimize the PRD. The real value is alignment and QA.
- Create issues locally or in GitHub.
  - Matt often uses GitHub issues; he closes them when done.
  - Example: course-video-manager repo has 744 closed issues.

### Module Thinking in PRD
- Keep codebase in mind throughout.
- Example: gamification service is a **deep module** with meaningful logic.
- PRD specifies modules to modify:
  - New gamification service
  - Progress service
  - Lesson route
  - Dashboard route
- This module map should stay in your mind during planning and implementation.

---

## 6. Kanban Board / Issues — Journey Document

### From PRD to Independently Grabbable Issues
- Break PRD into issues using:
  - **Vertical slices**
  - **Traceable bullets**
- Skill: “Break a PRD into independently grabbable issues using vertical slices / traceable bullets, written as local markdown files.”

### Horizontal vs. Vertical Slicing
- AI loves to code **horizontally**:
  - Phase 1: all database/schema
  - Phase 2: all API
  - Phase 3: all frontend
- Problem: no integrated feedback until late. AI codes blind.
- Better: **Vertical slices**
  - Thin slices crossing all needed layers.
  - End-to-end functionality visible early.
  - Near-instant feedback.
- **Traceable bullets** analogy:
  - Anti-aircraft gunner uses glowing bullets to see trajectory.
  - Increase feedback on where you’re aiming.
  - From *The Pragmatic Programmer*.

### Example Issues
- Schema + gamification service (AFK, no blockers)
- Streak tracking
- Wire points/streaks into lessons quiz completion (blocked by 1 & 2)
- Retroactive backfill (blocked by 1)
- Final integration (blocked by all)
- First proposed slice was too horizontal.
- Corrected to vertical: “Award points for lesson completion, visible on dashboard.”

### Blocking Relationships → DAG
- Issues have dependencies.
- Kanban board becomes a directed acyclic graph (DAG).
- Enables parallelization:
  - Phase 1: one issue
  - Phase 2: two independent issues in parallel
  - Phase 3: merge/integration
- Sequential plans only allow one agent. Kanban allows multiple agents.

### Documentation Hygiene
- Do not keep old PRDs around forever.
- **Doc rot**: old docs mislead agents when code has changed.
- Matt tends to close/delete PRDs after completion.
- Migrations are different: deterministic running record, probably keep.

---

## 7. AFK Implementation — Ralph Loop

### Simple Once Script
- `once.sh`:
  - Cats all issue markdown files into a variable.
  - Grabs last five commits.
  - Grabs prompt.
  - Runs Claude Code with `--permission-mode acceptEdits`.
- This is not a loop; it’s one run.
- AFK version runs in a Docker sandbox.
- Run once first to observe behavior and tune prompt.

### AFK Prompt Contents
- Local issue files provided at start of context.
- Work on AFK issues only.
- If all AFK tasks complete, output “no more tasks.”
- Pick next task.
- Prioritize:
  1. Critical bug fixes
  2. Development infrastructure
  3. Traceable bullets
  4. Polishing quick wins / refactors
- Explore repo.
- Use TDD to complete task.
- Run feedback loops.

### TDD — Test-Driven Development
- Essential for AI.
- Red → Green → Refactor.
- Write a failing test first.
- Then implement to make it pass.
- Prevents AI from cheating tests by writing implementation first, then tests.
- Adds good tests to codebase.
- Feedback loops are the ceiling for AI coding quality.
  - Without tests/types, AI codes blind.
  - Bad feedback loops → bad AI output.

### Automated Review
- After implementation, get AI to review its own code.
- Important: **clear context before review**.
  - If reviewer runs in same context, it’s in the dumb zone.
  - Reviewer should be in the smart zone.
- Matt uses Sonnet for implementation, Opus for review.
- Automated review catches many bugs before human QA.

### Manual QA
- QA is where you impose taste and opinions.
- Avoid automating everything—otherwise you get slop.
- QA creates more issues for the Kanban board.
- Code review burden increases with AI.
  - Tension between small PRs and long AFK loops.
  - Matt doesn’t have a perfect answer yet.

---

## 8. Codebase Architecture for AI

### Bad Codebases Make Bad Agents
- If codebase is garbage, agent output is garbage.
- Deep understanding of code and TypeScript still matters.

### Deep Modules vs. Shallow Modules
- From John Ousterhout, *A Philosophy of Software Design*.
- **Shallow modules**:
  - Many small files, lots of exports.
  - Tangled dependencies.
  - Hard for AI to navigate.
  - Hard to test—where do you draw boundaries?
  - AI tends to create these if unchecked.
- **Deep modules**:
  - Small, simple interface.
  - Lots of functionality inside.
  - Easy to test with a large test boundary.
  - Caller has simple interface.
- Design the interface; delegate implementation.
- Modules become **gray boxes**:
  - You know shape and behavior.
  - You don’t need to review every internal detail.
  - Retains mental map and sanity.

### Improve Codebase Architecture Skill
- Skill scans codebase for architectural improvement candidates.
- Finds clusters of related modules that can be tested as a unit.
- Example: video editor in browser.
  - Wrapped entire frontend-to-backend flow in one testable module.
  - Used discriminated union between types.
  - Night-and-day improvement for AI changes.
- If you take one thing away: run this skill on your repo.

---

## 9. Parallelization with Sandcastle

- Sandcastle: TypeScript library for running AFK agent loops.
- `run` function:
  - Creates a worktree.
  - Sandboxes in Docker container.
  - Runs prompt inside.
- Parallel flow:
  1. **Planner** looks at backlog and chooses issues to work on in parallel.
  2. Works out phases from blocking relationships.
  3. For each issue: create sandbox, run implementer with issue number, title, branch.
  4. If commits created, review them.
  5. **Merger agent** takes branches and issues, merges them.
  6. Fixes type/test issues from merge.
- Uses Sonnet for implementation, Opus for reviewing.
- Works super well for Matt across most projects.

---

## 10. Push vs. Pull for Coding Standards

- **Push**: instructions always sent to agent.
  - Example: `Claude.md` — “talk like a pirate.”
- **Pull**: agent can retrieve information when needed.
  - Example: skills with description headers.
- Matt’s current approach:
  - **Implementer**: coding standards available via **pull** (skills).
  - **Automated reviewer**: coding standards **pushed** to it.
    - Reviewer gets code + standards to compare.
- Own your planning stack. Don’t over-rely on a framework you don’t understand.

---

## 11. Q&A and Additional Points

### Team Workflow
- The messy real world: parallel ideas, bugs, no full picture.
- Planning phases (idea → PRD) are team activities.
- Use grilling to find questions you can’t answer.
- Loop in team, prototype, research, integrate third-party services.
- PRDs shared for comments/RFCs.
- Once destination clear, move to Kanban implementation.
- QA and code review can happen while agents implement.
- Kanban can accept new blocking issues infinitely.

### Frontend
- AI not good at mature frontend; needs human eyes.
- Can generate 3 prototypes in throwaway route.
- Pick best, feed back into grilling.
- Prototypes are messy and early feedback tools.

### 1M Context Window
- Good for retrieval, less good for coding.
- Smart zone still ~100K for coding.
- Smart zone will grow over time.

### Documentation
- Tend to ditch/close PRDs after completion to avoid doc rot.
- Migrations are different—deterministic record.

### PMs / Non-dev Vibe Coding
- Matt left unanswered, mystery.

### Claude Code
- Matt doesn’t like it much, but it’s currently best among alternatives.
- You can choose any system.
- Ask User Questions UI is broken.

### AI QA
- Yes, use automated review.
- Clear context so reviewer is in smart zone.
- Human QA still needed for taste.

### Old Books
- Matt recommends buying old software engineering books:
  - *The Pragmatic Programmer*
  - *Refactoring*
  - *The Design of Design*
  - *A Philosophy of Software Design*
- Pre-AI writing is a gold mine for prompts and principles.

---

## 12. Final Summary / Key Takeaways

1. **AI is new, but fundamentals matter.**
2. **Manage context**: smart zone vs. dumb zone; clear > compact.
3. **Align via Grill Me**: relentless interview until shared design concept.
4. **Write a PRD**: destination document; don’t over-review or over-optimize.
5. **Break into Kanban/issues**: vertical slices, traceable bullets, blocking relationships.
6. **Implement AFK**: Ralph-style loop, TDD, feedback loops.
7. **Review and QA**: clear context for reviewer; manual QA for taste and new issues.
8. **Design deep modules**: small interfaces, rich internals, easy test boundaries.
9. **Parallelize**: use DAG/Kanban and tools like Sandcastle.
10. **Own your stack**: push/pull standards appropriately.
11. **Avoid slop**: human touch in QA and code review is essential.
12. **Read old software engineering books**: they verbalize what AI needs.

**Final workflow**:
```
Idea → Grill → PRD → Kanban (vertical slices) → AFK agents → QA/Review → more issues → team review
```
- Planning is human-in-the-loop.
- Implementation is AFK.
- QA and code review are where you impose taste.
- Keep the shape of your codebase in mind throughout.





Full Walkthrough: Workflow for AI Coding — Matt Pocock

(0:07) [music] >> Yeah, we're good. Okay, folks. We're at capacity. Let's kick off. I don't want you waiting here for 25 more minutes before we some arbitrary deadline. So, welcome. My name's Matt, I'm a teacher, and I suppose now I teach AI. Um We have a link up here, if you've not already been to this, which is has the exercises for the um stuff we're going to do today.
(0:41) This is going to be around 2 hours, so we might just sort of kick off 2 hours from now. Is that all right, Mike? Yeah, perfect. Um and the theory behind this talk, or at least the thesis under which I've been operating for the last kind of 6 months or so, is that we all think that AI is a new paradigm, right? AI is obviously changing a lot of things.
(1:03) You guys are obviously interested in this, and that's why you've come to this talk. And I feel that when we talk about AI being a new paradigm, we forget that actually software engineering fundamentals, the stuff that's really crucial to working with humans, also works super well with AI. And this is what my keynote is on tomorrow, really.
(1:27) I'm going to sort of be fleshing that out a lot more. And in this workshop, I'm hopefully going to be able to direct your attention to those things, and uh hopefully show you that I'm right. But we'll see. Um can I get a quick heads-up first? How many of you guys um are coding have ever coded with AI? Raise your hand if you've ever coded with AI. Perfect. Okay.
(1:48) Uh keep your hand raised. Uh let's all uh share those armpits with the world. Um how many of you code every day with AI? Cool. Okay. Uh right, keep your hand raised if you've ever been frustrated with AI. Okay, very good. You can put your hands down. Thank you for that show of obedience. I really appreciate that.
(2:12) And we are also being live-streamed to the Gilgood room as well. I've not uh Did we send someone up to the Gilgood room to just check they're okay? Don't know. But I see you, and there is a way that you can participate, which is we have the um a Q&A. We're going to be doing kind of have a sort of hatred of Q&As cuz they're not very democratic.
(2:31) They're mostly the sort of um most talkative people get to um get to participate and share. And so, we're going to be going through this um Q&A here. So, why do we have to wait till 3:45? The room is packed, the doors are closed. 100% agree. And so, if you want to uh ask a question, we're going to be I would like you to pile into this async, and then we can vote on each other's questions, and hopefully get the best questions surfaced so the for the entire room to enjoy.
(3:00) So, I want to talk about first the kind of weird constraints that LLMs have. And those weird constraints are sort of what we have to base a lot of our work around. Now, there's a guy called Dex Hardy who runs a company called Human Layer, and he came up with this idea, which is that when you're working with LLMs, they have a smart zone and a dumb zone.
(3:27) When you're first kind of like working with an LLM, and it's like you've just started a new conversation, you start from nothing, that's when the LLM is going to do its best work. Because in that situation, the attention relationships are the least strained. Every time you add a token to an LLM, it's kind of like you're adding a team to a football league.
(3:44) You think of the number of matches that get added every time you add a team to a football league, it just goes it scales quadratically. And that's because you have attention relationships going from essentially each token to the other that are positional and the sort of meaning of the individual token. And so, this means that by around sort of 40% or around I would say around 100K is kind of my new marker for this.
(4:07) Cuz it doesn't matter whether you're using 1 million uh context window or 200K, it's always going to be about this. It starts to just get dumber. So, as you continually keep adding stuff to the same context window, it just gets dumber and dumber until it's making kind of stupid decisions. Raise your hand if that feels familiar to you.
(4:30) Yeah, cool. So, this means that we kind of want to size our tasks in a way that sticks within the smart zone. Right? We don't want the AI to bite off more than it can chew. This goes back to old advice like Martin Fowler in refactoring. Uh like uh the pragmatic programmer talks about this. Don't bite off more than you can chew.
(4:49) Keep your tasks small so that you as a developer, a human developer, don't freak out and don't start acting and going into the dumb zone. But how do you tackle big tasks? How do you take a large task like I don't know, cloning a company or something, or just doing something crazy, and how do you break it into small tasks so they all fit into the dumb zone? One way, of course, you could do is I mean, kind of what the AI companies maybe want you to do, or the natural way of doing it is just keep going and going
(5:22) and going, you end up in the dumb zone, charging you tons of tokens per request. You then compact back down. We'll talk about compacting properly in a minute. And you keep going, keep going, compact back down, keep going, keep going, keep going. And I think that's doesn't really work very well because the more sediment I we'll talk about that in a minute.
(5:41) So, the theory here is then, and this is what I was doing for a while, is I would use these kind of um multi-phase plans. Where I would say, "Okay, we have this sort of number four thing here, this large large task. Let's break it down into small sections so that we can then kind of chunk it up and do each little bit of work in the smart zone.
(6:00) " Raise your hand if you've ever used a multi-phase plan before. Yeah, really common practice, right? This is kind of how we've been doing it. Certainly, this is how I was doing it up until December last year, really. And any developer worth their salt will look at this and go, "This is a loop." Right? This is a loop.
(6:19) We've just got phase one, phase two, phase three, phase four. Why don't we just have phase N? Right? Phase N. Where we essentially just say, "Okay, we have, let's say, a plan operating in the background, and then we just loop over the top of it, and we go through until it's complete." And this is where um Raise your hand if you've heard of Ralph Wiggum as a software practice.
(6:44) Okay, cool. Raise your hand if you've not heard of Ralph Wiggum as a software practice, actually. That's more like it. Okay. So, there's this idea called Ralph Wiggum, uh which is kind of um sort of based on this, which is essentially all you need to do is sort of specify the end of the journey, where you just say, "Okay, we create a PRD, a product requirements document, to say, 'Whoa, okay, let's describe where we're going.
(7:05) '" And then we just say to the AI, "Just make a small change. Make a small change that gets us closer and closer to that." And Ralph works okay, but I prefer a little bit more structure. So, that's kind of where we got to in terms of thinking about the smart zone, and that's kind of where I want you to first start thinking about here.
(7:27) Another weird constraint of LLMs is LLMs are kind of like the guy from Memento, right? They just continually forget. They could just keep resetting back to the base state. Let me pull up this diagram. I sort of I I really should use slides, but I just prefer just like randomly scrolling around a uh infinite uh TL draw canvas.
(7:44) Thank you, Steve. Um So, let's say another concept I want you to have is that every session with an LLM kind of goes through the same stages. You have, first of all, the system prompt here. This gray box here is essentially the stuff that's always in your context. You want this to be as small as possible.
(8:04) Cuz if you have a ton of stuff in here, if you have 250K tokens, like I have seen people put in there, then that you're just going to go straight into the dumb zone without even being able to do anything. So, you want this to be tiny. >> [snorts] >> You then go into a kind of exploratory phase.
(8:21) This blue sort of where the coding agent is going out and exploring the code base. Then you go into implementation. And then you go into testing. And sort of making sure that it works, running your feedback loops and things like this. Raise your hand if that feels familiar based on what you've done. Yeah.
(8:36) Sort of the like the the main cornerstones of any session. And when you clear the context, you go right back to the system prompt. Oof, you go right back there. So, you delete everything that's come before. And raise your hand if you've heard of compacting, as well. Yeah, okay. There are some people who've not heard of compacting.
(8:57) So, let's just quickly show what that means. For instance, I've just been having a little chat with my LLM. Uh I want to make sure we sort of, you know, just cover the basics so we're all sort of on the same wavelength here. I've just been having a chat with my LLM. I've been talking about a thing that I want to build.
(9:16) How's the font size? Should I bump it up? Folks in the back? Bump. Bump. Bump. Oh. I'm using Claude Code for this session, but you don't need to use Claude Code. Uh in fact, it's often nice not to use Claude Code. Um so, I've been having a chat with the LLM, just sort of planning out what I'm going to do next.
(9:34) It's asking me a bunch of questions, and I can I highly recommend you do this. There's this tiny little status line here that tells me how many tokens I'm using, the exact number of tokens I'm using. Um I have a article on my website AI Hero if you want to copy this. This is Oh, wow, that is that shakes, doesn't it? Um this is essential information on every coding session cuz you need to know exactly how many tokens you're using so that you know how close you are to the dumb zone.
(10:05) Absolutely essential. And so let's watch it. So I've got two options. I can either clear wrong and go back to nothing or I can compact. And when I compact then it's going to squeeze all of that conversation, which admittedly isn't very much, into a much smaller space. And this in diagram terms kind of looks like this.
(10:27) Where you take all of the information from the session and you essentially create a history out of it, a written record of what happened. And devs love compacting for some reason, but I hate it. I much prefer my AI to behave like uh the guy from Memento because this state is always the same. Always the same every time you do it.
(10:48) You clear and you go back to the beginning. And so if you're able to do that and you're able to optimize for that then you're in a great spot. So that's kind of the two things I want you to think about with LLMs, the two constraints that we're working with. They have a smart zone and a dumb zone and they're like the guy from Memento.
(11:06) So let's take a look at the first exercise. And I'm while I'm doing this, the way I want this to work is I'm going to sort of show you how um I'm going to be sort of walking through it up here and I want you folks to be kind of like tapping away and doing things as well. So that was just a little lecture bit.
(11:21) Let's now actually get and do some coding. For anyone who arrived late or anyone in the Gilgud room uh go to this link up here to see the exercises and clone the repo. You absolutely do not have to, you can just watch me do it if you fancy it. But let's go there myself and let's see what exercises await us. So essentially I've built a um this is from my course.
(11:49) This is a uh a course management platform essentially, a kind of CMS for instructors, for students, and this is what we're going to be building a feature in. So I'm going to take you from essentially the idea for the feature all the way up to building a PRD for the feature, all the way up to implementing the feature.
(12:08) And hopefully you can take inspiration from this process and use it in your own work. So uh let's kick off. So we're going to start by using a a skill which is very close to my heart. It's the grill me skill. And this grill me skill is wonderfully small wonderfully tiny and it helps prevent one of I think the main issues when you're working with an AI, which is misalignments.
(12:37) The uh the sort of silent idea that I'm talking against here, that I'm arguing against, is the specs to code movement. Has anyone heard of the specs to code movement? Raise your hand. It's not really a movement I suppose, it's just sort of people saying specs to code. Um what it is is people say, "Okay, you can write a program or you want to build an app the best way to build that app is to take some specifications so to write some sort of like document and then turn that document into code.
(13:05) " So they just turn it into code. How do you do that? You pass it to AI. If there's something wrong with the resulting code, you don't look at the code, you look back at the specs. You change the specs and you sort of just keep going like this. This is kind of like vibe coding by another name where you're essentially ignoring the code.
(13:25) You don't need to worry about the code. You just sort of keep editing the specs and eventually you just keep going. And I tried this. I really tried it. And it sucks. It doesn't work. Because you need to keep a handle on the code. You need to understand what's in it. You need to shape it because the code is your battleground.
(13:40) And so this is again is where we're going. Let's let's get some exercises. So what I'd like you to do is go to this page, the the grill me skill. And inside the repo here we have a slack message from our pal. Uh where is it? It's in the root of the repo and it's under bur bur bur bur Oh, where is it? Mhm mhm client brief.md.
(14:09) It's a slack message from Sarah Chen. For some reason the Claude always chooses Sarah Chen as the name. I don't know why. Um it's saying that in cadence, our um course platform, our retention numbers are not great. Students sign up to a few lessons then they drop off. I'd love to add some gamification to the platform.
(14:26) And so when you're presented with an idea like this, you need to find some way of turning it into reality. Let's say Sarah Chen is your client, you're on a tight budget, you need to get this done fast. How do you go and do it? Um raise your hand if you would um enter plan mode when you're doing this. Anyone a big user of plan mode? Yep.
(14:45) Um let's actually shout out quickly any other ideas about what you would do with this or any Raise your hand if you what what would be your first port of call? Yep. Ask for more info. Sorry? Ask for more info to verify what is the purpose and where our current standing is. Yes, exactly.
(15:00) Let's imagine that Sarah Chen's gone on holiday, you have no idea, right? Uh she's just posted this thing, you need to action it before you go. Well, my first port of call is I go for this particular skill. I'm going to clear my context. I'm going to uh get rid of you, you don't need to be there. And I'm going to say um I'm going to invoke a skill which is the grill me skill.
(15:25) Let's quickly check. Raise your hands if you don't know what this is. Cool. Oh, sorry sorry. Let me be more specific. Raise your hands if you don't know what I'm doing here when I uh do a forward slash and then type something. Anyone Everyone kind of understand what that is? I'm invoking a skill.
(15:44) I'm invoking the grill me skill. And what I'm going to do is I'm going to say grill me and I'm going to pass in the client brief. So now the LLM really has only a couple of things here. It just has the skill and it has the description of what I want to do. And this is virtually how I start every piece of work with AI.
(16:08) And while it's exploring the code base I'm just going to show you what the grill me skill does. So this is inside the repo so you can check it out. It's extremely short. "Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the decision tree resolving dependencies one by one.
(16:26) For each question provide your recommended answer. Ask the questions one at a time uh blah blah." What this does and what I noticed when I was working with AI, especially in plan mode actually is it would really eagerly try to produce a plan for me. It would say, "Okay, I think I've got enough.
(16:46) I'm just going to poof plan plan." And what I found was that I was really trying to find the words for this, for for what I wanted instead of that. And Frederick P. Brooks in The Design of Design, he has a great quote uh talking about the design concept. When you're working on something new with someone when you're uh all trying to build something together then there's this shared idea that's shared between all participants and that is the design concept.
(17:16) And that's what I realized I needed with Claude. I needed to reach a shared understanding. need an asset, I didn't need a plan, I needed to be on the same wavelength as the AI, as my agent. And this is an extremely effective way of doing it. So hopefully Here we go. Nice. It has done its exploration first of all.
(17:39) It's invoked a sub agent which spent 97 93.7k tokens on Opus. Um and it's asked me the first question. Cool. We can see that even though the sub agent burned a a ton of tokens I haven't actually um uh increased my token usage that much. Raise your hand if you don't know what sub agents are. It's important question.
(18:04) Everyone kind of clear what sub agents are? Okay, I'll give a brief definition. Which is that this this sub agents thing here, this explore sub agent it has essentially gone and called another LLM which has an isolated context window. And then that LLM has reported a summary back.
(18:20) So a sub agent is kind of like a delegation. You're delegating a task to a sub agent. It goes eagerly does all the thing, explores a ton of stuff and then just drip feeds the important stuff back up to the orchestrator agent. To the parent agent. So okay. So hopefully you guys have seen the same thing. It's done an explore.
(18:38) And we now have our first question. Points economy. What actions earn points and how much? Ooh, okay. At this point you can ask it by the way questions to um deepen your understanding of the repo. I obviously know this repo really well cuz I wrote it, but you might not um know what's going on. So let's say my recommendation, keep it simple, two point sources to start.
(19:00) What's so nice about this is that not only does it give us a question that kind of aligns us here, we get a recommendation too. And often what I'll find is the AI's recommendations are really good. And so I'll just say skip video watch events, they're noisy and gameable. I agree. Sarah's asked we'll keep the lessons in the bread and butter.
(19:20) Yeah. Looks good, pal. >> [snorts] >> Now what I usually do is I usually dictate to the AI. I'm usually actually chatting to the AI instead of uh typing here, but uh this is a relatively new laptop and I couldn't get my dictation software working on it um because Windows is crap. Um So, should points be retroactive? There are existing lesson progress records with completion at timestamps.
(19:45) This is a really nasty question, right? Should we actually go back and backfill all of the lesson progress events? This is a kind of question that you need to be aligned on if you're going to fulfill the feature properly. This is not something I considered and Sarah Chen certainly didn't consider. Do I want it to be retroactive? Hmm.
(20:04) Let's actually do a vote inside here. Should we go back and backfill all the records? Raise your hand if you think we should backfill all the records. Raise your hand if you think we shouldn't backfill all the records. There are a lot of fence-sitters in the room. I'm going to say you know, this is the kind of discussion you're sort of having with the AI.
(20:24) You're getting further aligned. Yes, I'm just going to go with his recommendation cuz I'm lazy. Notice too how I'm able to keep in the loop here with AI. I'm not you know, it's it's pinging me these questions pretty quickly. I'm not having to go off and check Twitter or something. Levels.
(20:42) What's the progression curve? Yeah, that looks about right. For instance, yes, okay. So hopefully you should be able to go and um kind of work through this with the AI. >> [clears throat] >> And essentially try to reach an alignment. And this grill me skill, this can last a long time.
(20:58) This can I've had it ask me 40 questions. I've had it ask me 80 questions. I've had some people that asks 100 questions too. Literally you're sat there for an hour chatting to the AI. And what you end up with is essentially this conversation history that works really nicely and works really nicely as an asset of the design concept that you're creating.
(21:19) This can also function like this. You can have a meeting with someone who's a maybe a domain expert. Maybe I have a meeting with Sarah. I feed that meeting transcript into I don't know, Gemini meetings or whatever you guys are using. You take that, you feed it into a grilling session and you grill through the assumptions that you didn't have.
(21:39) So this ends up being a really nice kind of um a really nice way of just taking inputs from the world and then just turning and validating them. So okay. Let's see. I really want to get to the end of this, but I also don't want to just like be sat here talking to the AI in front of you for uh a thousand days.
(21:58) So I'm just going to say yes. Let's see what happens. So I'll tell you what, um while you guys sort of have a little fiddle with this locally, let's start a little Q&A session now. And let's see. How's this going to work? Can we keep the door closed or turn up the microphone? It's quite noisy. Uh let's see.
(22:20) Mike, can we uh door closed. Oh it has been closed. Mark has answered. Beautiful. So what I'd like you to do is there any air con? Yeah, there is some air con, I think. There is some air con. You guys aren't being lit here. I'm being fro I'm being fried alive here. Uh so what I'd like you to do is go on to the Slido, which you can join here.
(22:42) Have a if if you're not taking the exercise, go on to the Slido, have a little fiddle and vote on some good questions. I'm just going to chat to the AI for a second uh until we reach a stopping point. So do streaks earn points? Um streaks are standalone. Let's see what else it comes up with. Where does gamification UI live? Let's have it in the dashboard.
(23:19) I'm just going to scan these and blast through them basically. So how are we doing with our Slido? Okay. Have I tried Spec Kit, Open Spec or Taskmaster instead of the Grill Me skill? Do I find them more verbose or a structured alternative? This is a great question. So there are a ton of different frameworks out there that allow you to um sort of build up this planning process for you.
(23:39) I personally believe you at at this stage, when there's no clear winner, when there's no kind of like one true way and when things are changing all the time, you need to own as much of your planning stack as you possibly can. What I've noticed and a lot of my students is they tend to overuse a certain stack. They get into trouble and they because they don't own the stack and they don't have observability over the whole thing, they just go this isn't working. This sucks.
(24:10) Whereas if um if you have control over the whole thing, then at least you know how to fix it or potentially know how to fix it. So I'm even though I'm sort of giving you uh a stack basically, I believe in inversion of control and you should be in control of the stack. So bur bur bur. Can I press zero, please? Sorry? Sorry, that was a lot of sort of mumbling.
(24:41) Can I Thank you. I'm so sorry. >> [laughter] >> What you didn't want to give Claude good feedback? What is what is wrong with you? Uh okay, cool. Uh many of the questions asked by the Grill Me skill are not necessarily appropriate for a developer, rather a PO. In larger teams, who should use it? Yeah. Um Raise your hand if um you've ever done pair programming.
(25:12) Anyone ever done pair programming? Right. I keep Put your hands down and raise your hand again if you've ever done a pair programming session with an AI. Right. How did it go? Was it good? You enjoy it? I think pair programming sessions with AI is a great idea because you've got a third person in the room who will relentlessly quiz you and ask you questions.
(25:30) It should If you don't know the answer, it should be you, the domain expert and the AI in the same room. If you're have a question about implementation, it should be you, a fellow developer and the AI in the same room, you know. You can be sort of working through these questions in your team.
(25:44) And I think actually we're going to look at implementation in a bit and we're going to see how you can make implementation so much faster. And but I think the really crucial decisions, the ones you need humans for you actually need a lot of humans and it doesn't really matter how many humans are in there.
(26:00) You can actually throw a bunch like a kind of like mob programming with AI essentially. Uh what's my favorite meta prompting tool? I think I kind of answered that. Uh there's no air con. Let's just live with it. Uh how do I use the conversation as an asset after the Grill Me session? Well, we're going to get there.
(26:20) Um okay, so I really want to I want to speed this up sort of artificially. Just what I This is the thing. So someone just said okay, Ralph loop this. But this is crucial because I can't loop over this, right? I can't um I think of there is being two types of tasks in the AI age. Where you have human in the loop tasks, where a human needs to sit there and do it.
(26:49) Which is this. We are the human in the loop, with multiple humans in the loop. And there are AFK tasks. There are tasks where the human can be away from the keyboard and it doesn't matter. Implementation, as we'll see, can be turned into an AFK task. But planning, this alignment phase, has to be human in the loop.
(27:04) Has to be. So I've got to do it, unfortunately. Um I don't know. Uh give me a long list of all your recommendations. I'm running a workshop right now. So I artificially need you to pull more weight. So let's see what it does. Uh let's answer a couple more questions while it's doing its thing. What is my opinion on PMs or other non-dev roles vibe coding task? Hmm.
(27:45) Um I'm going to return to this later, I think. I'm going to leave this unanswered. A bit of mystery. I notice I'm not using the ask user questions UI for Grill Me. Why? Um there's a specific uh UI that you can bring up in Claude Code. I'll answer this just quickly. Uh ask me a question using the ask user question tool.
(28:10) >> [snorts] >> And this UI um is just sort of broken in Claude and I really hate it. You notice I'm using Claude, but I don't like Claude very much. Like you you really are free with this method to choose any um system you like. And this is what the UI looks like. It's very pleasing when you first encounter it, but then you realize it is actually broken in a ton of different ways.
(28:32) All right, what did it come back with? Oh blimey. Oh no. So while this is doing its thing, let me do some teaching in the meantime. The plan here is that we take our Grill Me skill and we need to essentially find some way of turning it into a destination. We need to go down to the uh We essentially need to we're figuring out the shape of this.
(29:01) That's what we're doing. We're figuring out the shape of the tasks during the grilling session. And in order to turn it into a bunch of actionable actions for the AI we essentially need to figure out the destination. We need to know where we're going. We need to know the shape of this entire thing. So I think of there is being two essential documents that we need.
(29:22) We need a document that documents the destination. Oh no. It's so not bright enough. There we go. Still not brighter. There we go. We need something to document the destination. And we need something to document the journey. In other words, we need something a document that's going to figure out what this even looks like in all of its user stories and figure out a definition of done and then we need to figure out what the split looks like.
(29:53) So, that's where we're going to go to next. So, once we finish with the grilling session, yeah, it looks great. Fantastic. I love it. It answered it answered 22 of its own questions. There you go. That's quite representative of what a grilling session looks like. So, at this point now, I have used 25k tokens and all of that or loads of that stuff is gold.
(30:16) I want to keep that around. I've I've got 25k great tokens there. And what I want to do is kind of summarize it in some kind of destination documents. So, this is um the next exercise where we're going to uh we're going to write a product requirements document. And the the product requirements documents or the PRD is essentially that's its function.
(30:44) It's the destination documents. And it's sort of doesn't matter what shape it is. I've got a shape that I prefer and I quite like. But, you can just choose your own shape or whatever your company uses. And all we're really doing is I'm not too worried about that. All we're really doing is summarizing the design concept that we have so far.
(31:10) And the So, let let's try this. So, I'm going to initiate this. I'm going to say zoom all the way to the bottom. All I'm going to do is just say write a PRD. And we can take a look at that skill now. Write a PRD. So, this skill it does a few things. It first asks the user for a long detailed description of the problem.
(31:35) You can use write a PRD without grilling first, but I just like to grill first and then write the PRD afterwards. Then you can um get it to install the repo which we've kind of already done. Then we get it to interview the user relentlessly so we have a kind of grilling session again and then we start um putting together a PRD template.
(31:55) So, this is available in the repo if you want to check it out. And essentially this is what it looks like. We've got some problem statements, the problem the user is facing, the solution to the problem and a set of user stories. And these user stories sort of define what this is. You know, as you you guys have probably seen things like this if you've been a developer at all.
(32:13) Um you know, there are cucumber is a language you can use to write these in or we just sort of um uh write them ourselves essentially. Then we have a list of implementation decisions that were made and list of crucially testing decisions, too. So, I'm going to run this. Okay. And so, it's finished its thing. Ah! Windows, let me close the thing.
(32:37) Thank you. I don't know why I bought a Windows laptop. I think I just I like the challenge. Um >> [clears throat] >> So, the first thing that it's going to give me are a set of proposed modules it wants to modify. Now, there's a deep reason why I'm thinking about this. So, this is at this stage we have an idea, we have sort of specked out the idea, we've reached a sort of understanding of what we're trying to do and then we need to start thinking about the code because at this point we need to this is not specs to code. This is not
(33:15) where we're ignoring the code. We actually keep the code in mind throughout the whole process. And the way I like to do this is I like to just sort of think about a set of proposed modules to modify. We're going to return to this this idea of continually designing your system and keeping your system in mind. So, it's it's saying recommend tests for the gamification service is the only deep module with meaningful logic.
(33:36) These modules look right. Yeah. Looks good. And it's going to hang out a PRD. Now, for ease of setup I've got it so that it creates a set of issues locally. So, it's just going to create essentially a PRD inside this issues directory. But, the way I usually do it and you can check this out yourself is you can go to my um essentially what I consider my work repo which is GitHub um dot com forward slash Matt Pocock forward slash course video manager up here.
(34:15) And in here, this is essentially a app that I create um that I use all the time to record my videos and things like this. I think I've recorded like I pulled out the stats. I think I've recorded like a thousand videos in here or something nuts. Um and you can see here that it's got 744 closed issues. And this is essentially all of the uh PRDs and all of the implementation issues that I've put into here.
(34:37) So, this is how I usually like to do it. >> [clears throat] >> So, that's what I'm doing with the There we go. Yeah, I'm just going to say yes and uh and get that issue out. Let's see. It is inside here. So, we've got the problem statements. People signing up for courses. Uh the solution, the user stories, uh 18 user stories looks nice, some implementation decisions, level thresholds, etc.
(35:03) This is enough information. We've kind of clarified where we're going and what we're doing. So, that's what we do. We essentially have a grilling session and we've created an asset out of it. Now, raise your hand. Should I be reviewing this document? Raise your hand if you think I should be reviewing the documents.
(35:23) Yeah, I don't I don't look at these. The reason I don't look at these is because what am I testing at this point? What am I Like when I read it, what am I testing? What am I What are the failure modes I'm trying to test for? I know that LLMs are great at summarization cuz they are. They're really good at summarization.
(35:41) I have reached the same wavelength as the LLM, right? Using the grill me skill, we have a shared design concept. So, if I have a shared design concept, all I'm doing is I'm just essentially checking the LLM's ability to summarize. So, I don't tend to read these. Let's have Let's have a Q&A cuz I can feel you guys are itching for it.
(36:02) And I think we might have like I don't know, just a 5-minute comfort break just to uh rest my voice and so you can catch up with the exercises for a minute if that's all right. So, let's have a little Q&A sesh. Uh If I don't like Claude Code, which one do I actually like? Um uh Have you ever heard the phrase um uh democracy is the worst way to run a country apart from all the other ways? That's how I feel about Claude Code.
(36:30) Uh we've answered that one. Uh What's your thoughts on developers needing to very deeply understand TypeScript now that fix the TS make no mistakes exist? I don't understand the phrasing of this, but I think I understand meaning, which is that I believe that code is very important and this is kind of going to feed through the whole session and that bad code bases make bad agents.
(36:54) If you have a garbage code base, you're going to get garbage out of the agent that's working in that code base. We'll talk more about that in a bit. And so, I think understanding these tools very deeply, understanding code deeply is going to make you a much much better developer and get more out of AI. Uh and that answers that question, too.
(37:16) Sweet. Uh Get out of there. There you are. Now that we have 1 million tokens available, do we ever actually want to take advantage of that? I've noticed that the dumb zone has become less dumb lately. Okay, great question. This goes back to our kind of initial idea on the dumb zone. Uh I am I recorded my Claude Code course using a 200k context window and on the day that I launched the course they announced the 1 million context window.
(37:53) My take on this is that what Claude Code did is they essentially just did this. Wee! They shipped a lot more dumb zone to you essentially. Now, this is good for tasks where you want to retrieve things from a large context window. If you want to pass five copies of War and Peace or something to it and you want to find out all the things that uh I can't remember a character from War and Peace.
(38:15) Uh Why did I start with that? It's good for retrieval. It's less good for coding. So, I consider that it is about 100k at the moment is the smart zone. The smart zone will get bigger and that will be a really nice improvement. So, folks, we're going to take it like a 5-minute comfort break if that's all right just for my voice and to maybe you can have a little move around or something or grab a drink.
(38:39) I can just notice some sleepy eyes and I want to make sure that we're awake for the next bit if that's all right. So, we'll take 5 minutes and I will see you back here then. All right? So, we have our PRD which I'm not going to read, our kind of destination document. Let's quickly scan for any good questions before we zoom ahead.
(39:02) And Rediscovering the role of software engineering today's world, top three disciplines you recommend. Um Taekwondo is good, I've heard. I've no idea how to answer this question. Um thank you for asking it though. Um Top three disciplines I recommend. I mean Sorry? Plumbing. Plumbing is a good one. Yeah, yeah, yeah.
(39:23) I don't know if that's a discipline. I the plumbers I've hired are not usually very disciplined. Um Right. So, okay. We now have our destination, okay? Um Perfect. So, how do we actually get to our destination? How do we We have a sort of vague PRD? How do we split it so that we don't put things into the dumb zone? In other words, we have our number four, how do we split it into this kind of multi-phase plan? Well, probably what you would do at this point is you would say, "Okay, Claude, give me a multi-phase plan that gets me to this
(39:59) destination, right?" That sort of makes sense. This is what we've been doing before. But I have um a sort of better way of doing it now, which is that I like creating a Kanban board out of this. Raise your hand if you don't know what a Kanban board is. Mm, cool. Okay. A Kanban board is essentially just a set of tickets that you put on the wall that have blocking relationships to each other.
(40:23) So, we're going to see what it kind of looks like here. This is how we've worked um as developers for a long time, really since Agile came around. And what it does, we can see it here, it has proposed that we split this setup into um five different tasks here. We have the first one, which is the schema and the gamification service.
(40:47) Yeah, well, that looks pretty good. This is blocked by nothing. And we can even see here that it's a it's given it a type of AFK, too. You remember I talked about human in the loop and AFK earlier? This is an AFK task. This is something we can just pass off to an agent to do its thing. Streak tracking, okay, that looks good.
(41:04) Uh then wire points and streaks into lessons quiz completion. This is blocked by one and two. Retroactive backfill. This is blocked only by one. And then this one here is blocked by all of the tasks. Cool. Hmm. Now, I consider this you could say, "Why don't we just make this sort of generation of the issues, why don't we just hand that over to the AI? Why do I need to be involved here, right?" Cuz it's given us quite a good selection of tools here.
(41:31) Why do I need to review this and sort of figure out what's next? Now, my take here is that this is really cheap to do, like very quick to do once I've done the PR, and I can immediately see some issues here. There's a really, really important technique when you're kind of figuring out what the shape of this journey should look like.
(41:55) And it sort of comes to this very classic idea, uh which comes from the Pragmatic Programmer called traceable bullets or vertical slices. And traceable bullets really transformed the way I think about actually getting AI to pick its own tasks. Systems have layers, right? There are layers in your system. These might be different deployable units.
(42:20) You might have a database that lives somewhere. You might have an API that lives maybe close to the database but in a separate bit. You might have a front end that lives somewhere totally different like a CDN. Or within these deployable units, you might have different layers within those.
(42:34) In for instance, the code base that we're working in, we have a ton of different services. Service. We have a quiz service, a team service, a user service, coupon service, core service. And these services have dependencies on each other. So, they're kind of like individual layers. Well, what I noticed is that AI loves to code horizontally.
(42:57) So, it loves to code layer by layer. So, in other words, in phase one, it will do all of the database stuff, all of the schema, all of the you know, all the stuff related to that unit. Then it will go into phase two and do all of the API stuff. Then it will add the front end on top of that. Does Can anyone tell me what's wrong with that picture? Why is that not a good thing to do? Raise your hand if you have an answer.
(43:21) Yeah. >> have that whole feedback loop. Exactly. You don't get feedback on your work until you've really started or completed phase three. So, what you really need to do is you you're not until you get to phase three, you're not actually testing that all the layers work together. You haven't got an integrated system that you can test against.
(43:44) And so, instead you need to think about vertical layers. You need to think about thin slices of functionality that cross all of the layers that you need to. And this is a much better way to work, much better way for the AI to work, too, because it means at the end of phase one or during phase one it can get feedback on its entire flow.
(44:04) So, what this means to me is inside the PRD to issues skill up here, I have got break a PRD into independently grabbable issues using vertical slices traceable bullets written as local markdown files. [snorts] We first locate the PRD. Uh again, explore the code base if this is a fresh session.
(44:25) We draft vertical slices. So, we break the PRD into traceable issues. A traceable bullet, by the way, is uh essentially when you're like an anti-aircraft gunner. It's quite a violent idea, actually. Uh and you're looking up in the sky and it's night. If you're just shooting normal bullets, you have no idea what you're firing at, right? You could just be you know, you you see the plane but you don't see where your bullets are going.
(44:48) Traceable bullets is they attach a tiny bit of phosphorescence or phosphor or something to make it glow as it goes. So, this means that every sixth bullet or something you actually see a line in the sky. So, you have feedback on where you're aiming. So, this is what this is the idea here is that we increase our level of feedback and we get near instant feedback on what we're building.
(45:09) Cuz without that the AI is kind of coding blind until it reaches the later phases. We got some vertical slice rules. We quiz the user. And then we create the issue files. So, what I see here is that even though I've I've told it to do vertical slices, it's proposing to create the gamification service first on its own.
(45:32) That's just one slice there. And that to me feels like a horizontal slice. What I want to see in the first vertical slice especially is I want to see the schema changes or some schema changes. I want to see some new service being created and I want a minimal representation of that on the front end.
(45:48) So, I want it to go through the vertical slices, not just the horizontal. Does that make sense? Okay. So, I'm going to give the AI a rollicking. Uh bad boy. No, I'm not. I'm not going to waste tokens just being just naming. Um So, the first slice is too horizontal. I'll just start with that and see if it picks it up.
(46:12) Does that make sense as a concept? And I think having that um what I really like about going back to those old books is that we're really trying to in this day and age like get uh verbalize best software practices in English. And these books, 20-year-old books, have already done that. And it's an absolute gold mine if you want to throw that into prompts.
(46:34) But even with that, it's not going to um not going to do a perfect job each time. So, award points for lesson completion visible on dashboard. Yes, that's a beautiful vertical slice because it's definitely a big chunk of stuff. It's doing a lot of stories there, but we're going to see something visible at the end and the AI will then just be able to add to that.
(46:54) You see why that's preferable to the first one. Cool. Uh looks great. So, we're getting closer now. Anyone following at home as well, you know, not at home but you get the idea. Um will hopefully see the same thing, too, and start developing the same instincts. Let's open up for questions just while I'm still creating these GitHub issues.
(47:16) Uh ba ba ba ba Oh, not GitHub issues. Uh local issues. When will I stop using Windows? Never. What is your Okay, we'll get to that later. How does AI um decide when to stop grilling? Cuz AI can ask incessantly, can we have a smarter way to decide the stop point? Yeah, it does tend to really um those grilling sessions can be super intense.
(47:35) And the thing about these skills is you can tune them if you want to. If you feel like the AI is just absolutely hammering you, hammering you, then you can just tell it to just pull back a little bit or get it to do, you know, stop points and that kind of thing. So, if that's a failure mode that you run into a lot, then you just, you know, change the skill.
(47:55) Uh do I still use uh be extremely concise, sacrifice grammar for the sake of concision? Um there was a tip that I gave folks um 5 months ago, which is that to basically increase the readability of your plans. So, when you're using plan mode, then you can put it in your Claude.md and you can say, "Okay, yeah, approve that.
(48:15) " Let's open up Claude.md. Uh do I have a Claude.md? Maybe I don't. I I really don't use Claude.md very much. I'm just going to put a dummy inside here. Um when No. When talking to me, uh sacrifice grammar for the sake of concision. And this um prompt was uh really useful to me when I was reading the plans because it meant that the plans would come out and they would be very concise, really nice, easy to read, often very concise.
(48:50) But I've since dropped this idea in preference to a grilling session because what I noticed with it just I didn't want to read the plans. I wanted to get on the same wavelength as the LLM. I wanted it to ask aggressive questions to me. And when I stopped reading the plans, I stopped needing them to be concise.
(49:08) So, I think of the plans really in the destination document as uh the end state. And I don't need that end state to be concise. Hopefully that answers your question. Uh What do I think will be the outcome of the Mexican standoff of future roles of PMs and other roles converging? Uh I've no idea. I'm not a pundit. I've no idea.
(49:29) Uh okay. So, we should uh after a couple of approvals, uh end up with a set of issues. Now, these issues that we're creating, they're designed to be independently grabbable, which means that this Kanban board ends up looking kind of like this. Where you have essentially a set of tickets with a whole load of independent relationships.
(49:57) So, this one needs to be done before this one. This one needs to be done before this one. And this one, let's say we got another one over here. This one needs to be done before this one. This means that you can start to parallelize. You can start to get agents working at the same time on these tasks. Because yeah, this one needs to be done first.
(50:18) And then these two can be grabbed at the same time by independent agents. Raise your hand if you've done any kind of parallelization work with agents. Okay, cool. So, this allows you um to turn those plans into to optimally kind of like into a directed acyclic graphs essentially, where you just are able to um essentially have three phases here.
(50:45) Where you have phase one. Uh let me grab move that. Uh above this line here, you do this one. Then phase two, you do the two below it. And then phase three, you do this third one and add it onto that. And when you think about there could be This could This is a relatively simple plan, but you could have many different plans operating all at once.
(51:08) It means that you can do really nice parallelization. And we'll talk more about that in a bit. But that's why I prefer a Kanban board set up like this to a sequential plan. Because a sequential plan can really only be picked up by one agent. So, this Where did it go? Over here. Yeah, this plan here This is really only one loop, right? Only one agent can work on these because we have numbered phases and they're not parallelizable.
(51:38) Does that make sense? Cool. So, we've got our issues. Ah, come on. Stop asking me for I know it's creating them on GitHub. I really don't want that. Oh, no. You fool. Create them in issues instead. No. That's not precise enough. Uh you fool. Create them in local markdown files instead, referencing the local version.
(52:11) Sorry about this. So, once we get to this point, we [clears throat] have a bunch of issues locally that we can start um looping over and implementing. And it's at this point that the human leaves the loop. So, so far Let me pull up a a proper overview of this kind of flow that we're exploring here. So far we have taken an idea.
(52:43) I'll zoom this in a bit for the folks at the back. And we've grilled ourselves about the idea. We can skip over research and prototype, but we turn that into a PRD, into a destination document. We then turn that PRD into a Kanban board. And all of those steps are human reviewed. And now the implementation stage, we step back.
(53:08) And we let an agent um work through that Kanban board or multiple agents work through the Kanban board. Now, what this means is that yeah, we spent a lot of time planning here, but it means that we've queued up a lot of work for the agent. We can think of this as kind of like the day shift and the night shift.
(53:24) This is the day shift for the human, right? Planning everything, getting all the all the stuff ready. And then once we kick it over to the night shift, the AI can just work AFK. But what does that look like? Well, so I'm just going to Oh, yeah. Just allow it. It's perfect. So, this looks like if we head to the next exercise, which is uh in fact, the last exercise here, running your AFK agent.
(53:55) Now, I've called this uh Ralph really cuz it is a it is essentially a Ralph loop. And this prompt here, I want to walk through this really closely. The first thing it's doing here is we're essentially going to run Claude and we're going to basically try to encourage it to work um completely AFK. I'll show you what the sort of script for this looks like in a minute.
(54:19) But you say, "Okay, local issue files from issues are provided at the start of context." The way we do that is if you look inside once.sh here inside the repo, we have uh it's essentially just a bash script, where we grab all of the issues, um [clears throat] which are inside markdown files, and we cat them into a local variable.
(54:40) So, that issues variable contains all of the issues that are in our entire backlog. Then we grab the last five commits. I'll explain why in a minute. And then we grab the prompt and we just run Claude code with permission mode accept edits. And then just essentially just pass it all of the information. This is what the implementer looks like.
(55:04) So, that's what a very very simple version of this sort of loop looks like. And of course, this is not a loop. This is just running it once. The loop is in the AFK version up here, which is uh a fair bit more complicated. And the crucial part here is we're running it in Docker sandbox as well. So, I I don't want you to install Docker on your laptops because we're just going to be like, "You need to download a special image and we're going to tank the conference Wi-Fi if we do that.
(55:29) " So, I'm I am going to demo this to you, but you um won't need to run this yourself, but I'll talk through this in a minute. But essentially, this once loop here, and ba ba ba ba boom. We're just essentially running one version of the thing that we're going to loop again and again and again. So, this is kind of like the human in the loop version. And this is essential.
(55:51) Running this again and again is essential because you're going to see what the agent does and see how it ends up working. And any tuning that you need to add to the prompt, then you can do that. Let's go to the prompt. Um So, local issue files are being passed in. You're going to work on the AFK issues only. That makes sense.
(56:15) If all AFK tasks are complete, output this no more tasks thing. And then the next thing, pick the next task. So, what we're doing here is we're essentially running a backlog or curating a backlog that our AFK agent is going to pick up. That's the purpose of all of these um setups in the beginning. In this uh all the way to this Kanban board here, we're just essentially creating a backlog of tasks for the night shift to pick up.
(56:46) And the night shift, this sort of Ralph prompt here, it's got its own idea about what a good task looks like to next pick up. I'm I did talk about parallelization. I will show you this later, but this is essentially a sequential loop here. We're just going to run one coding agent at a time.
(57:03) This is a good way to just sort of um get your feet wet essentially. So, it's prioritizing critical bug fixes, development infrastructure, then trace bullets, then polishing quick wins and refactors. And then we just have a very simple kind of instruction on how to complete the task. So, we explore the repo. Use TDD to complete the task.
(57:23) I'll get to that later. And we then run some feedback loops. So, let's let's just try this and let's just see what happens. So, good. It's created the issue files. We should be good to go. I'm going to cancel out of this. I'll clear and I'm going to run uh Where is it? Ralph once.sh.
(57:43) And you can feel free if you're following along to do the same thing. So, we can see it's just running Claude inside here with the prompt and with all of the issues that have been passed in. And while it's doing its thing, you probably have some questions about this setup and about the decisions that I've made to essentially delegate all of my coding to AI, right? So, let's let's do a quick Q&A while it's getting its feet under it.
(58:14) Uh okay. Ba ba ba ba ba. I'm going to just remove those. How do you retain negative decisions, things that you decided against, and rationales when persisting the results from the grill me session? Uh great question. There's a very simple answer, which is the in the PRD uh write a PRD section, there is a stuff at the bottom, a section of the things that are out of scope.
(58:40) So, the things we're not going to tackle in this PRD, which is very important for giving a definition of done. Feel free to ping on the Slido if you've got any more questions. Uh what's my front end workflow? Okay, it's a great question. I'm going to I'm going to answer that in a minute, I think. How to deal with agents producing more code that we can review? How to properly parallelize and use multiple agents separate way.
(59:05) Okay, that's That's two questions there. Um Raise your hand if you feel like you're doing more code review now than you used to. Yeah, definitely. Um I don't think there's a way to avoid this. If we delegate all of our coding to agents, you notice that the implementation here is really the only AFK bit.
(59:29) We then also need to QA the work and code review the work, right? And if we are running these loops where it's essentially going to implement four issues in one, it's hard to pair that with the dictum that you should keep pull requests small and self-contained, right? Like small self-contained pull requests means you're needing to do fewer loops or shorter loops or something.
(59:57) Or maybe you do like a big stack of PRs, but that seems horrible as well. That's still just more separated code to review. I don't honestly know what the answer to this yet. I think we just need to be ready to be doing more code review, essentially. Which is not fun. That's not fun thing to say. That's not like I don't know.
(1:00:11) I don't feel good saying that, but I do think it's probably the way things are going. It's a great question. Uh Can we grab a couple of questions from the room as well? Let's not We won't do the mic, but uh raise your hand if you've got a question for me immediately. Yeah. So, the approach is very linear from an idea to uh QA code review.
(1:00:34) Of course, the real world is a lot more messy. So, you have all these ideas that are in parallel and nobody has the full picture. And uh while you're working on something, something else comes in as a bug. Yeah. How do you deal with the messiness? How do you tighten that feedback loop? Great question.
(1:00:52) So, the question was if this all looks great if you're a solo developer, but actually how do you implement this in a team? How do you gather team feedback on this? And my answer to that is that if you have an idea up there and essentially the sort of journey from the idea to the destination is something you need to figure out with the team, right? So, all of this stuff up here, this is kind of like team stuff, you know what I mean? This So, if you have an idea and you do a grilling session on it and you have a question
(1:01:23) that you don't know how to answer, then you need to loop in your team as we described before. Then you might need to go, "Okay, like we just need to build a prototype of this. We need to actually hash this out. We need something that the domain experts can fiddle with." Or okay, we might need to integrate a a third-party library into this.
(1:01:38) We might need to do some research. We might need to actually kind of like um ping this back and forth and find a third-party service that we can get the most out of. We might need to go back with the information that we gathered there to the idea phase. So, all the way up to the sort of PRD in the journey, that's something you need to involve your team with.
(1:01:56) That's something where these assets are going to be shared over and you're going to have requests for comments on them and that that loop is going to just keep grinding and grinding until you figure out where you're going. Once you figure out where you're going, then you can start doing the Kanban board implementation.
(1:02:12) But this is essentially super arguable and the you'll be bouncing back and forth between the phases. Does that make sense? Yeah. Would you not need a PRD for your prototype? Say again, sorry. Would you not want to have a PRD for your prototype? The question was, do you want to go through this whole session just to sort of create a prototype? You don't need a PRD for your prototype as well.
(1:02:31) Let's just quickly talk about prototypes for a second. Um there was a question about how do you make this work for front end? Like how do you cuz front end is like really sensitive to human eyes. You need human eyes looking at the front end all the time to make sure that it looks good. AI doesn't really have any eyes.
(1:02:48) It can look at code, but it front end is multimodal. And so my experiences with trying to plug AI into um let's say agent browser or Playwright MCP to give it You can give it tools to allow it to look through a front end and sort of look at images, but in my experience the um it's not very good at that yet and it can't create a nice front end in a mature code base.
(1:03:15) It can sort of spit one out. But what it can do is you say, "Okay, uh I want some ideas on how uh this front end might look. Give me three prototypes um that I can click between in a throwaway uh throwaway route that I can decide which one looks best." And you take the asset of that prototype and you then feed it back into the grilling session or you get feedback on it, blah blah blah blah blah.
(1:03:39) Answer your question kind of thing? The prototype is just, you know, it's messy. It's supposed to give you feedback earlier on the process. So, that's a great way of working with front end code, great way of looking at software architecture in general. Let's go one more question here. Yes. >> [clears throat] >> In your system, how do you integrate respecting an architecture and design with API contracts and fitting with your larger system? Uh security constraints, all kinds of constraints like that.
(1:04:04) Yeah. There's a lot in that question. The question was, how do you conform with existing architecture? How do you do um how do you make it conform to the code standards like of your code base or Yeah, the architecture design APIs, Yeah. security rules that constrain your design. Yeah. I'm going to answer that in a bit.
(1:04:25) That's okay. So, hopefully we have started to get some stuff cook cooking. Uh it's just pinging on the explore phase here. Hmm, tempted to just start running it AFK. Maybe I will, maybe I won't. Um What it's essentially doing is it's exploring the repo. It's going to then start implementing based on what we wanted.
(1:04:49) Let's actually have one more question just while it's running. Yeah. Why not AI QA everything Yeah. So, the question was, why do you not get AI to QA? AI to QA. I just got uh jargon overload for a second. Um why do you not get AI to uh test its own code? Now, of course, you absolutely can.
(1:05:13) And I think while it's doing while it's cooking here, okay, it's got a clear picture of the code base. It's assessing the issues. It's doing issue 02 as the next task. I'm again going to show you that in a bit, I think. The sort of uh cuz you definitely should do an automated review step as part of implementation.
(1:05:33) So, you have your implementation, you should then, because tokens are pretty cheap and AI is actually really good at reviewing stuff, you should get it to review its own code before you then QA it. I found that that catches a ton of different bugs and the way that works is I will just do a little diagram is if you have, let's say, an implementation that sort of like used up a bunch of tokens in the smart zone, if you get it to sort of try to do its reviewing, it's going to be doing the reviewing in the dumb zone.
(1:06:05) And so, the reviewer will be dumber than the thing that actually implemented it. If we imagine this is the uh let's be consistent. That's the review. That's the implementation. Whereas if you clear the context, then you're essentially going to be able to just review in the smart zone, which is where you want to be.
(1:06:27) Let's see how our implementation is doing. Okay, good. It's generating a migration. That looks pretty nice. We're getting some code spitting out. And while I'm sort of like Aha, here we go. TDD. Let's talk about TDD and then I think we'll have a little another little break. TDD I found is absolutely essential for getting the most out of agents.
(1:06:51) Uh raise your hand if uh you know what TDD is. Cool. Okay. TDD is test-driven development. What it's essentially doing is it's doing a something called red green refactor. And if you look in the code base, you'll be able to find a um a skill which really describes how to do red green refactor and teaches the AI how to do it.
(1:07:13) So, what it's doing is it's writing a failing test first. So, it's saying, "Okay, I've broken down the idea of what I'm doing and I'm just going to write a single test that fails and then I need to make the implementation pass." I have found that first of all, this adds tests to the code base and these this tends to add good tests to the code base.
(1:07:33) And so, we've got this kind of gamification service. It looks like it's using some existing stuff to create a test database. Test fails because the module doesn't exist yet. Okay, we've confirmed red. And then it goes and hopefully runs it and it passes. I found that uh raise your hand if you've ever had AI write bad tests.
(1:07:58) Yeah. It tends to try to cheat at the tests because it's sort of doing it in layers. It will do the entire implementation and then it will do the entire test layer just below it. Uh I'm just going to say yes, you're allowed to use NPX V test. And using this technique, it generally is a lot harder to cheat because it's sort of instrumenting the code before it's then writing the code.
(1:08:22) So, I find that TDD is so so good for places where you can pull it off. In fact, it's so good that I sort of warped my whole uh technique around getting TDD to work better. I can see some dripping eyes. It is so hot in here. You can't imagine how hot it is up here. Let's take another 5-minute comfort break.
(1:08:41) Let's come back at quarter to, I think. Have a nice generous one. And we'll be back in about 6 7 minutes and I'll talk about how uh I think about modules, think about constructing a code base to make this possible. I've just been sort of fiddling with the AI here and we have ended up with some with a commit.
(1:09:02) So, we have something to test. Issue number two is complete. Here's what was done. This is kind of what it looks like when a Ralph loop completes is you end up with a little summary. Um and we have now something we can QA. Because we did the feedback loops because we did the trace bullets because we were uh said, "Okay, give us something reviewable at the end of this." We can immediately go and QA it.
(1:09:24) Now, there's nothing uh less exciting than watching someone else QA something. But, hopefully we can have a little play. Let's just check that it uh works at all. In fact, before I go there, I just want to sort of work through what just happened. Which is we see that it's created some stuff on the dashboard. And it then ran the feedback loops.
(1:09:45) So, it then ran the tests and the types. Now, TDD is obviously really important. And it's really important because these feedback loops are essential to AI, essential to get AI to produce anything reasonable. Because without this, AI is totally coding blind, right? You have to have to um If if your code base doesn't have feedback loops, you're never ever ever going to get decent AI decent output out of AI.
(1:10:15) And often what you'll find is that the quality of your feedback loops influences how good your AI can code, essentially. That is the ceiling. So, if you're getting bad outputs from your AI, you often need to increase the quality of your feedback loops. We'll talk about how to do that in a minute. Now, so it ran NPM run test, NPM run type check.
(1:10:39) It got one type error, and it needed to fix it with a nice bit of TypeScript magic. Very good. Yeah, type of level threshold number. Okay. Uh you see why I stopped teaching TypeScript cuz just AI knows everything now. Um So, and it ran the tests, and it passed, and it's looking good. So, we now end up with 284 tests in this repo.
(1:10:58) Pretty good. I I do find uh front end really hard to test here. We're essentially just testing the service. So, we've created a gamification service, if we look up here. And then we have a test for that service. You can see that the service and the test itself. Now, if I was doing code review here, I would then go to I would first go to review the tests, make sure the tests were testing reasonable things, and then go and kind of review the code itself just to make sure that it's it's not doing anything too crazy, right?
(1:11:32) The essential thing is I need to actually um look at the dashboard. I'm going to log in as a student. Oh, if it'll let me. Maybe it won't let me. Come on, son. There we go. Let's log in as Emma Wilson. Head into courses. Uh let's say I've got an introduction to TypeScript. Continue learning. Uh yes, I completed this lesson.
(1:11:57) And something went wrong. I imagine it's because I don't have Uh SQLite error. I don't have the right table. So, I need a table point events. Point events is a strange table name. I'm not sure quite what it was thinking there. Uh let's suspend. Let's run uh NPM DB migrate. Push, I think. I can't remember which one it was.
(1:12:21) But, you kind of get the idea, right? I I'm not going to subject you to uh watching me do QA because it's so dull. Um but at this point, I would essentially go back in. I would um Let me open the project back up. Uh and I would This This is a crucial moment, um and it's so important to um QA it manually here because QA Oh, dear, oh dear.
(1:12:45) What's going wrong? There we go. QA is how I then um impose my uh opinions back onto the code base, how I impose my taste. What you'll often find is that um there are teams out there who are trying to automate everything, like every part of this process. And they will tend to uh if you try to like automate the sort of creation of the idea, automate uh the QA, automate the research, automate the prototype, you end up with uh apps that I feel just lack taste and are bad.
(1:13:21) Maybe they just don't work, or they they don't even work as intended, or there's just no You need a human touch when you're building this stuff because without that, you just end up with slop. And we are not producing slop here. We're trying to produce high-quality stuff, and so that's what the QA is for. Mhm.
(1:13:39) So, I'm going to do two things in this final section. Which is I'm going to first tell you how to There's probably a question in your mind here, which is let's say I have a code base that I'm working on. And it's a bad code base. It's a code base that's like really complicated, uh that AI just never does good work in, and maybe actually most humans that go into that code base don't do good work.
(1:14:03) How what How do I improve that code base? And the second thing is I'll show you my setup for parallelization. So, let's go with um bad code first. Now, where is it? Where's the diagram? Here it is. In his book, um The Philosophy of Software Design, John Ousterhout talks about the ideal type of module. And let's imagine that you have a code base that looks like this.
(1:14:30) Each of these uh blocks here are individual files. And these files export things from them. You know, they have um things that you pull from the files that you then use in other things. And so, you might have these weird dependencies where this file over here might rely on this file, or might rely on that file, for instance.
(1:14:49) Now, if these files are small and they don't kind of ex- like export many things, then John Ousterhout would call these shallow modules, essentially. Where they're not very um They kind of look like uh this, if I No, actually no. I can't can't make a good diagram of it. They're essentially lots and lots of small chunks.
(1:15:09) Now, this is hard for the AI to navigate cuz it doesn't really understand the dependencies between everything. It can't work out where everything is. You know, it has to sort of manually track through the entire graph and go, "Okay, this relies on this. This one relies on this one. This one relies on this one.
(1:15:22) " And it's then also hard to test this, as well, because where do you draw your test boundaries here? Do you test each module individually? Like just literally draw a test boundary No, don't do that. Around this one? And then maybe another test boundary around the next one, and then the next one? Or should you sort of do big groups of it? Should you say, "Okay, we're going to test all of these related modules together, and just sort of, you know, hope and pray that they work.
(1:15:53) " Now, >> [sighs] >> this means that if I think that bad tests mostly look like that, where the AI essentially tries to sort of wrap every tiny function in its own test boundary, and then just sort of test that those individually work. But, what that does is it means that when, let's say, this module over here calls those two, so it depends on both of these, then this module might miss order the functions, or there might be sort of stuff inside that poor module that's worth testing on its own.
(1:16:27) And if you then wrap this in a test boundary, what do you do? Do you mock the other two modules? How does that work? So, actually figuring out how to um build a code base that is easy to test is essential here. Because if our code base is easy to test, then our code our feedback loops are going to be better, and the AI is going to do better work in our code base.
(1:16:52) Does that make sense? So, what does a good code base looks like look like? Well, not like that. It looks like this. Where you have what John Ousterhout calls deep modules. Modules that have a little interface on there that expose a small, simple interface that have a lot of functionality inside them. Now, what this means is that these are easy to test cuz you just Let's say that there's a dependency between this one and this one.
(1:17:25) My arrow working? Yeah, there we go. Then, what you do is you just wrap a big test boundary around that one module, around this one up here, and you're going to catch a lot of good stuff. Because there's lots of functionality that you're testing, and really the caller, the person calling the module, is going to have a simple interface to work from. So, it's not not too tricky.
(1:17:50) That makes sense? Deep modules versus shallow modules. This is good. This shallow version is bad. And what I find is that unaided um or if you don't uh if you don't watch AI carefully, it's going to produce a code base that looks like this. So, you need to be really, really careful when you're directing it. And that's why, too, is that if we look inside the PRD, uh where is the PRD gone? It's inside the issues.
(1:18:18) It's inside the gamification system. Uh not found. Of course, it's not. Here it is. Then I have uh inside here data model the modules. So, it's specifically saying, "Okay, this gamification service is a new deep module, which we're going to test around. It's going to have this particular interface. And it's going to have um Okay, we're modifying the progress service, too.
(1:18:46) We're modifying the lesson route. We're modifying the dashboard route, etc. So, it's I'm being really specific about the modules that I'm editing, and I'm making sure that I keep that module map in my mind at all times, throughout the planning, and then throughout the implementation. Does that make sense? Very, very useful.
(1:19:03) It's useful for one other reason, too. Not only does it make your app more testable, but you get to do a little mental trick. And I'm going to refill my water while you wait for what that is. Uh let me Let me get a question from you guys. So, raise your hands if you feel like Uh if you feel like you're working harder than ever before with AI.
(1:19:32) Yeah. Uh raise your hands if you feel like you know your code base less well than you used to. Yeah. This is a real thing. Um because we're moving fast, because we're delegating more things, we end up losing a sense of our code base. And if we lose the sense of our code base, we're not going to be able to improve it, and we're essentially delegating the shape of it to AI.
(1:19:59) I [snorts] don't think that's good. But then how do we make it so that we can move fast while still keeping enough space in our brains? I think that this is a way to do it. Because what you're doing here is not only are you thinking about creating big shapes in your code base, big services. What I think you should do is design the interface for these modules, but then delegate the implementation.
(1:20:27) In other words, these modules can become like gray boxes, where you just need to know the shape of them, you need to know what they do, and it's sort of how they behave, but you can delegate the implementation of those modules. I found this is really nice. I don't necessarily need to code review everything inside that module.
(1:20:42) I don't necessarily need to know everything of what it's doing. I just need to know that it behaves a certain way under certain conditions, and that it does its thing. So, it's kind of like okay, I've got a big overview of my code base, and I understand kind of the shapes inside it, understand what the interfaces all do, but I can delegate what's inside.
(1:21:01) I found that has been a really nice way to retain my sense of the code base while preserving my sanity. Make sense? And so, you might ask, how do I take a code base that looks like this and then turn it into a code base that looks like this? How do I deepen the modules? Well, we have Hopefully, it's in here. Pretty sure it is. We have a skill.
(1:21:28) And that skill is called improve code base architecture. Nice and direct. Uh let's run it. What this skill is going to do is it's essentially just going to do it a scan of our code base and looking for what's available here. And feel free to run this yourself if you're um uh running the exercises. And it's exploring the architecture, exploring um essentially how to work within this code base, and it's going to attempt to uh find places to deepen the modules.
(1:22:00) Pretty simple. One really cool um thing that it found here is part of my uh part of my course video manager app is a video editor. A video editor built in the browser, which is really hardcore. Uh it's a decent bit of engineering. And I wanted a way that I could wrap the entire front end all the way to the back end in like a single big module, so that I could test the fact that I press something on the front end and it goes all the way to the back end.
(1:22:26) And so, I found a way essentially by using a kind of discriminated union between the two types here by sort of I was able to use this uh skill to essentially have a huge great big module that just tested from the outside, it was testable from the outside, this video editor infrastructure.
(1:22:44) And it meant that AI could see the entire flow, could act on the entire flow, and test on the entire flow. And honestly, it was just night and day in terms of the uh ability of AI to actually make changes, cuz AI working on a video editor is pretty brutal if you don't give it good tests. So, that is Honestly, I If you take one thing away from today, just try running this skill on your repo and see what happens.
(1:23:09) Let's go to Slido. Let's ask a check a couple of questions as well this is running. So, let's see. Have you tried Claude's auto mode with Claude enable auto mode? That way you can avoid many of the obvious permission checks. We'll talk about permission checks in a second. Do I keep the markdown plans and issues for later reference? Okay.
(1:23:29) This is a great question. So, let's say that you uh have a great idea, you turn it into a PRD, raise and you then implement that PRD, and the PRD is essentially done. Raise your hand if you keep that information in the repo, so you turn it into a markdown file. Raise your hand if you want to keep that around. Cool. Okay.
(1:23:53) And raise your hand if you don't want to keep it around. If you want to get rid of it as soon as possible. Yeah, this is I think an a question that doesn't have a clear answer. What I'm really scared of with any documentation decision is that let's say that we have a PRD for this gamification system, we keep it in the repo.
(1:24:15) We go on, go on, go on. Let's say a month later, we want some edits to the gamification system. And we go in with Claude, and it finds this old PRD and says, yes, I found the original documentation for the PRD system. Well, it turns out that the actual code has changed so much from the original PRD that it's almost unrecognizable.
(1:24:31) The names of things have changed, the um file structure has changed, even the requirements may have changed. We might have actually tested it with users. This is doc rot, where the documentation for something is rotting away in your repo and influencing Claude badly. Or Claude, agents badly. So, I tend to not keep it around.
(1:24:50) I tend to get rid of it. And for me, because my setup uses GitHub issues, I just mark it as closed. It can fetch it if it wants to, but it's got a visual indicator that it's done. So, I tend to prefer ditching these. Thoughts on the BEADS framework from Steve. Uh I've not tested it, but it seems like sort of um another way to manage Kanban boards and issues.
(1:25:13) Seems uh very good, but I've not tried it. Um >> [clears throat] >> Uh let me just quickly check the uh setup here. Let's take a couple of questions from the room. Anybody got any questions at this point about anything that we've covered so far, especially this last bit? Yes. I thought it was interesting your answer about like the markdown files that you delete because they create like doc rot.
(1:25:41) How about migrations? Like with migration files, would you also squash them after that? Like database migrations? Yeah. I don't know. I hope that answers your question. I'm so sorry. No, no. I think database migrations are a different thing because you have a sort of running record of exactly what changed, and it's more deterministic.
(1:26:00) And I think Yeah, it's an interesting analogy. I'm not sure. Let's talk about it afterwards. That's a good way of saying I've no idea. Yeah. Yeah. So, you mentioned that you don't delete the PRD. You mentioned you don't review the PRD once it's done. Sorry, guys. Um I'm just trying to listen to this guy's question.
(1:26:17) Have you considered uh using a deep think like ChatGPT or something to tell it, "Look at this PRD and tell me if it It takes about an hour. Yeah, the question The question here is um should I um in the sort of early planning stage be trying to optimize the plan? This is something I actually see a lot of people doing, and it's a really good um idea.
(1:26:44) So, when you Let's go back to the phases. So, let's say that you have all of these phases here. And you uh you get to the point where you've sort of figured out everything with the LLM, you understand where you're going, you've created this sort of uh journey destination documents here. How do you then uh Like should you then try to optimize and optimize that PRD until it's the perfect PRD you can possibly imagine? I don't think there's a lot of value in that.
(1:27:17) Because I think the journey is really just sort of a hint of where you want to go, and the place that you need to be putting the work is in QA. And you can sort of do that AFK, I suppose, but in my experience, you're not going to get a lot of juice out of it. Like it's the The thing that really matters is getting alignment with the AI, which is you do in the grilling session initially.
(1:27:40) Let's have one more question. Anyone got any more? Yeah. How do you get in in your workflow to get it to code the way you want it to code it so by the time you get to code review, it's at least familiar, it uses the libraries you wanted to use, Yeah. Um we had this question before, actually, which was like uh how do you uh enforce your coding standards on the agents, essentially? How do you get it to code how you want it to code? Now, there's essentially two different ways of doing it.
(1:28:05) Um you've got I don't know. Come on. Push. And you've got pull. What do I mean mean by push and pull? Um Push is where you push instructions to the LLM. So, you say, okay, if you put something in Claude.md, uh talk like a pirate, that instruction is always going to be sent to the agent, right? So, that is a push, actually.
(1:28:32) You're pushing tokens to it. Pull is where you give the agent an opportunity to pull more information. And that's for instance like skills. So, a skill is something that can sit in the repo, and it has a little description header that says, okay, agent, you may pull this when you want to. My thinking, my current thinking about code review and about coding standards looks like this.
(1:28:59) When you have an implementer, What's going on? There we go. Implementer. I'm going to make this less red in a second. Um then you want the coding standards to be available via pull. If it has a question, you want it to be able to sort of answer it. But if you then have an automated reviewer afterwards, then you want it to push.
(1:29:23) You want to push that information to the reviewer. You want to say, "These are our coding standards. Um make sure that this code um follows them." So if you have skills for instance, then you want to push that stuff to the reviewer so the reviewer has both the code that's written and the coding standards to compare to.
(1:29:42) Hopefully that answers your question. I can show you an automated version of this as well actually. Um Yeah, let's do that now just while it's fresh in my mind. I recently um spent uh maybe a week or so uh building this thing called Sandcastle. And Sandcastle is a I was sort of unhappy with the options out there for um running agents AFK.
(1:30:07) And what this does is it's essentially a TypeScript library for running these loops. So you have uh a run function that creates a work tree, um sandboxes it in a Docker container, and then allows you to run a prompt inside that. And in that work tree then, it's just a Git branch and you have that code and you can then merge it later.
(1:30:29) If I open up um there are some really really nice ways of viewing this and it essentially allows you to run these kind of automated loops and allows you to parallelize across multiple different agents really simply. So I'll go into my Sandcastle file, go into main.ts here. And let's just walk through this. So this is kind of like I showed you um a sort of version of the Ralph loop earlier.
(1:30:56) This is where we take it from sequential into parallel. We have here first of all a planner that takes in it's has a plan prompt here that looks at the backlog and chooses a certain number of issues to work on in parallel. Remember I showed you that Kanban board where it had all the blocking relationships? It works out all the phases.
(1:31:16) So this one will say okay, uh let's say we have uh you can ignore all this glue code here. This is essentially just a set of issues, GitHub issues with a title and with a a branch for you to work on. And then for each issue, we create a sandbox and then we run an implementer in that sandbox passing in the issue number, issue title, and the branch.
(1:31:42) This is like the loop that we ran just before. Then if it created some commits, we then review those commits. This is essentially the loop. What do we do with those commits? We pass those into a merger agent. Which takes in a merge prompt, takes in the branches that were created, takes in the issues, and it just merges them in.
(1:32:06) If there are any issues with the merge, you know, with the types and tests and that kind of thing, it solves them. And this has been my uh flow for quite a while now for working on most projects. It works super super well. And uh yeah, I recommend you check out Sandcastle if you want to sort of learn more. And to answer your question properly is that in the reviewer uh I would push the coding standards.
(1:32:30) In the implementer, I would allow it to pull. And I'm actually using uh Sonnet for implementation and Opus for um reviewing cuz I consider reviewing sort of I need I need the smarts then. Any question Actually, let me uh before we do more questions, let's go back here. Okay, where are we at? Okay. We sort of zooming everywhere in this uh talk because I'm kind of having to run things in parallel.
(1:32:56) So let's go back to the improve code base architecture. It has finally finished running and it's found a bunch of architectural improvement candidates. So it's got essentially a cluster of different modules that are all kind of related that could probably be tested as a unit. Got number one, the quiz scoring service.
(1:33:14) There's some reordering logic extraction as well. It has arguments for why they're coupled and it has a dependency category as well. So local substitutable in SQL light within memory test DB. Quiz scoring service just currently has zero tests. This is the biggest gap. So this is what it looks like when we come back of uh improve code base architecture.
(1:33:37) Okay. So we have nominally kind of 17 minutes left. I don't know about you guys, but I'm knackered. >> [laughter] >> Um I want to >> [clears throat] >> Let me let me kind of sum up for you. Cuz I think we're sort of reaching the end of our stamina. I'm going to be available for the full time if you want to um come and ask me questions.
(1:33:58) Um I might do one more check of the slide over, but let's kind of sum up where we've got to. So this is essentially the flow. Where throughout this whole process, we're bearing in mind the shape of our code base. This is not a spec to code compiler. This is not an AI that's sort of just like churning out code.
(1:34:19) We are being very intentional with the kind of modules and the shape of the code base that we want. We are making sure that we are as aligned as possible by using the grilling session, by really hammering out our idea. We're not over indexing into the PRD, we're not trying to read every part of it.
(1:34:35) We're not thinking too much about it even. We're then just turning that into a set of parallelizable issues which can be worked on by agents in parallel. We implement it and we QA and code review the hell out of it and then keep going back to that implementation. One thing I didn't really mention is that in the QA phase what the QA phase is for is creating more issues for that Kanban board.
(1:34:57) So while it's implementing even, you can be QAing the stuff and going back, adding more issues. And the Kanban board just allows you to add blocking issues kind of um sort of infinitely really. And then once that's all done, once you've got code that you're happy with, once you've got work that you're happy with, then you can share it with your team and you can get a full review.
(1:35:15) So this is kind of like once you get here, this is kind of one developer or maybe a couple of developers sort of um managing this and then it's kind of up to you to figure out how to merge it back in. >> [sighs] >> Of course all of this can be customized by you. This is just something that I have found works.
(1:35:32) I'm not trying to like sell you on a kind of approach here. What I recommend if you take one thing away from this session is that you should head back, you should head to Amazon and just buy a ton of those old books because I mean, I just found it so enlightening reading them. Uh you know, pre-AI writing is always like a a really fun to read anyway.
(1:35:54) And I just on every single page I found that there was something useful and something interesting to to read. So thank you so much. Thank you for putting up with the heat. Um hopefully your body temperatures will reset soon. Uh thank you very much. >> [applause] [music]





LIVE: Watch me build a brand-new project from scratch

(0:00) How we doing? This is a very very rare live stream for me. Um, but I have a kind of gap today before sort of figuring out my next course on Monday. And I've been reading a lot about DDD, domain driven design. I've been thinking about kind of retooling my skills. And also I've been thinking about this. I want to do more kind of watch me work long form content and I want a project idea that I can basically use as my playground for this kind of content.
(0:43) Going back to the voyer of the mat. Are you the voyer of the mat, Colin? Hello. Hello, Mark. Um, so what I want from you guys is project ideas because the to-do app could do. I I love a to-do app. Who doesn't love a to-do app customized for your needs? You know, could make it work. There's some good ones here.
(1:07) These are my constraints. I want it to be useful in my everyday work. I want it to have some kind of front end and backend pieces. And I want it to have a decent amount of complexity. I also want it to be ideally something that's useful to the viewers as well. So something AI coding related I think would be cool.
(1:25) Maybe like a coding agent observability platform. Interesting. The Horde is here. Yeah, we're we're vibe coding. Absolutely. That's what we're doing. We're vibe coding. Feel like we need like a definition of vibe coding. You know what I mean? See my uh see me craft my skills. Absolutely. Use Nux.
(1:49) Yeah, I mean I'm not averse to using NX. Give my opinion about Claude. Um or quite a complicated opinion about Claude given I just taught a course on it and e-commerce. Yeah, maybe. Maybe. I don't know. It's not very useful for my people though, for like my squad, for you guys. A complete AI coding company.
(2:11) A live stream chat manager. I mean, I do so I stream so rarely. an app that defines vibe coding. My own simplified open claw. See, I've never This is This is gonna kind of I don't know uh denigrate me in your eyes maybe, but I've never used open claw. I've never tried open claw. Never really felt the need to actually.
(2:36) But some kind of my own platform, something that's useful for you guys would be super cool. Also, I don't want to get in trouble with anthropic, right? You know, [sighs] that's a cheap joke. a codebase skills, rules, adherence, observability. Maybe I think we'd sort of reach that by actually building the thing itself.
(2:54) Everite v2 I wanted to be from scratch. I wanted to be from nothing. Greenfield coding agent skills prompt eval system. Leave it for various tasks. Canon AI coding canon board kind of thing. Interesting. See what actually people said here. What do people actually say? What's this? Using relatively newer third party libraries agents not using library specific skills during implementation.
(3:23) Yeah, maybe editing system. H I don't know. I mean, this is terrible, but I just think my own my own idea is the best is the best idea. I use VS Code as my code editor. GitHub alternative. Maybe maybe it's kind of like you get you in the weeds of git stuff really quickly and I feel like form wizard I don't know I mean these are good like interview level tasks you know you can imagine people like doing these at interview and then being impressive demos bookmarks manager yeah Obsidian vault integration I want it to be pretty
(4:06) complex pretty complicated I don't know. This is the one though. I mean, this is the one I'm feeling because I think this is something that I noticed that teams need all the time is that if you're I'm thinking about like if you're running coding agents in your organization, you want to see how many tokens people are spending.
(4:26) First of all, you want to see if they're having successful sessions or not. You want to see if those sessions are um you know, productive or not. and how many tokens they're using, how much context window using up, how what models people are using, all that stuff. Monor repo. Yeah, probably could be a monor repo if it gets big enough.
(4:53) An oss SDK that can be used independently from the platform. Abs, that's what I'm thinking is that you would have a version of it that was deployed and then a version of it that was local. What am tokens am I expecting to burn here? Uh, I don't know. I'm on um uh Anthropic 20X Max. Yeah, I mean that's what I'm thinking.
(5:11) Ralph needs a dashboard. How do I recommend using my skills along with relatively newer thirdparty libraries? Um, if you're having trouble with those third party libraries, I would create a skill for that third party library and then pull it into like um, basically create documentation for that skill uh, that sort of tells the coding agent how to use it and then you can pull it in during the review phase.
(5:40) This is the kind of stuff that will just be really like this is I think why you guys want to watch me is so that you can pick up because I feel like actually I'm sort of I don't know I feel like I'm just based on the conversations and the questions people ask I'm sort of quite I don't know far ahead is not the right way of framing it I think but I have very clearly very clear opinions about all this stuff.
(6:03) I don't know if they're good opinions but I have very clear and definite opinions. Vel workflows. Isn't it a coding agent observability platform? I don't think so. Yeah, that's what I'm thinking. Like you need somewhere to gather the data for your organization for a coding agent observability platform.
(6:19) I'm sort of talking myself into this now. You needed like a central place for all this data. And [sighs] I feel like you might want that to be a kind of pluggable storage mechanism as well. You know, you might want to store it in your own servers. There's sort of there's a lot of complexity there which I like.
(6:38) I've gone deeper. Um I use Opus most of the time. Yeah. Um yeah, most of the time. I'm really testing um 4.7 now. Yeah, I think maybe maybe I should just do it coding agent observability platform because yeah, I feel that's the missing link in the way I'm teaching as well because I'm I'm not observing my own sessions in the same way.
(7:06) But I should I think a bios I'm not building a bios. Hell no. For a new project, why not build like Cody Kent agent? I'm going to leave Kent's, you know, I I can't just copy Kent all the time. My whole career is basically copying Kent. It's just doing the Kent playbook, but worse than Kent. Haven't moved past agent in the ID.
(7:29) Can barely control that, let alone a swarm of agents yet. I mean, oh, I just want to dive in. You know what I mean? I I I What do we think? I mean, is there a way I can add votes here? Can I add votes? I think I can. Feel like I can. I feel like there's a way of doing it. Oh, yes. Hang on. Start a poll. Uh, should I build a coding agent observability platform? Just did a bit of dictation.
(7:59) I'm just going to say yes or no. Start poll. I never done this before. I have no idea if this is going to be any good. Thanks forever. Oh, sweet. Thank you. I haven't been working on it as much as I should. Um, yeah, we need to do a slideo. I don't know. Can you see that poll? I'm just going to check if actually I can see that poll.
(8:23) Uh, go over here for a sec. Is it is there is there one there? I don't know. Can you guys see a poll? Oh, yes. Okay. Yes. Okay. 78% for Yes. That's pretty good. Hide my Discord DMs. T3 code. Do I have any alter? I suppose all I've given you really is um a one idea. I haven't sort of [sighs] developed it yet. You can see it. Good.
(8:57) Claude's moderator. Woof. I know. when we when we get big enough to need mods, then we'll we'll get there. Um, am I into piano? Yes, I am into piano. I used to be a singing teacher. Weird question. You saw the poll before I saw the video of Really? Interesting. Yeah. I mean, because there's AI observability like for uh AI in applications, right? But then I feel like there's a layer missing which is observability for um your own coding agents.
(9:32) I don't know maybe we should probably validate this, right? Let's actually open up a terminal. Uh and let's just ask Claude about this. So I'm just going to run Claude in my home directory. Yes, I trust this folder. Claude, I've got an idea for an application I want to build. It's an observability platform and it's an observability platform that essentially is personal.
(10:00) So, it's something that you run yourself targeting um claude code or whatever coding agent you're using. I imagine what we're really trying to do is just upload the session to somewhere shared and then we can do um let's have a think. I'm using Whisper Flow by the way as my transcription tool. metrics and analysis and maybe human feedback, rating different sessions to see how they're doing and have this done per user so we can see across our organization what's going on.
(10:44) And I'm going to use um let's use just a standard grill me for this. This is one of my skills. I want you to harden this into a decent idea that I can potentially build. The stack will be TypeScript. Uh, you can't talk to it. I mean, this is just me using Whisper Flow basically. Yeah, this is not me replacing Claude.
(11:06) It's just adding a layer of observ observability on top of it. Grimm is great. Grimm is so good. So, it's loading the skill. It's okay. Here we go. Gez boy, that's a lot of text. Okay, this is a good question though. Who's the primary user? What decision does this tool help them make? There's a big fork here.
(11:26) Individual developer, engineering manager, or team lead, or platform devx at a company? That's good. What's our agent ROI? What prompts, tools, MCPs are worth the spend? Where are we bleeding tokens, costs, and adoption analytics? Ha, these sound compatible, but they're not. They dictate completely different UX.
(11:45) So good. A is a personal timeline with a deep dive in one session. Correct. B is cohort dashboards and comparisons which creates surveillance anxiety. C is aggregate metrics and doesn't care about individuals. Yeah. So I suppose our what's our ideal user here? I have tried caveman. Yeah. Um I mean I haven't tried it properly.
(12:07) Maybe I should try caveman. I do have a caveman skill available that's sort of my version of caveman. Whisper flow is fine for me. You think one individual developer? I mean [snorts] uh let's see a first with C star aggregates as a natural rollup. See B though I think you do want groupings of individual developers.
(12:31) Right. We think one or A. Are we choosing A? Yes. I think you do want a manager to be able to open and review a specific engineer session. I imagine that the way these are going to work in teams is you're going to need to think about or someone on the team is going to be responsible for making the AI better on that team and is going to be the DRRI for that.
(13:00) So you need the ability to dive into someone's session as well as to debug that session with them. There's also the potential for actually doing this live. So if someone's having a problem in their session right now, the engineering manager can view that and see what's going on with it. I really like this idea.
(13:18) I'm really talking myself into it. So I'm going to end the poll. You know, by the way, I'm not really answering the question. I'm sort of it's prompting me to think of things that I'm saying. That's something really important with Grill Me. No, I can't do a poll for each one of these. It's going to take forever. Okay.
(13:37) Consent and visibility model is session sharing opt-in per session always on by or policy or developer control with reduction. Oh, how good are these questions, man? How good are these questions? Coding sessions often contain secrets. Half form thoughts. Yeah. So, PII, personal identifiable information is going to be really important here.
(13:57) Um, manager can watch live without a clear consent model. Will either I get the tool banned by legal security. Absolutely right. or make developers self- censor and route real work elsewhere killing the data quality you need brilliant so always on augandated like corporate endpoint monitoring simple but hostile um per session optin yeah so you share this session I mean h this is bad you don't want per session opt-in because you want stats on what the devs are doing when the DRRi opens someone passction Does the developer get notified?
(14:36) I don't think so. I think that's gross. I don't think so. I think what you've got to realize is that your sessions are public to the organization. I think the developer when they're plugged into the system, it should be kind of tacitly understood that their coding sessions are public within the organization.
(14:58) Having that data is incredibly valuable to companies and so it's important that it's uh visible to all stakeholders. We're grilling on the idea of an observability platform um for agents. That's what we're up to. Um I have sort of tried Pi. I mean I haven't really tried Pi. I need to try more. Where am I going here? I think, oh, my brain's gone.
(15:37) Um, so I think we need to be less concerned about the privacy of the individual developer and more about the importance of the data that we're getting. I also think that there's we need to support on premises data so that the data never leaves the organization, never leaves their servers because I'm not interested in building this into a massive company.
(16:00) I want this to be an open source tool that is uh useful everywhere. Something I noticed people do with these grilling sessions is they just answer like A, B, or C, right? And when we're in the kind of blue sky phase here, when we're really not sure um what's uh how we're supposed to be working, then it's or what we're even building.
(16:27) It's not good to be railroaded that much. Okay, here we go. Q3. How do sessions get into the system? What's the ingestion mechanism? This decides the entire shape of the client, and it's the technical spine. Gh, I love the way it chooses really nice words like this. technical spine here. Um, okay. Yeah.
(16:45) So, this is important, but it's sort of like a um implementation detail tail the JSON. Yeah. So, you got the my initial thought here was hooks. You've got claw code hooks, post tool, use stop session, end hooks. So, or you've got something like this where it creates a bunch of transcripts on disk. Um, you've got a little demon that watches the directory, uploads deltas, um, sort of works with cursor codeex ader. That's a random one.
(17:20) No hook config required. Survives across agent restarts. Yes. Um, so now this is tricky because I don't want to commit to something super early before we understand the trade-offs. Um, so I think I need to get it to do some research here. I'm getting high on Claude's poetry. Absolutely. I mean, wherever good ideas come from, you got to give them credit.
(17:51) I think I want you to do some research here. I want something that's coding agent agnostic that at least works with the top coding agents. I'm going to define the top coding agents as claw code, codeex, pi, open code, and github copilot cli. So if we have hooks there, I want to I want you to go and investigate each of those with different sub aents to ping me back some information on what they support and whether they support open telemetry or whether we would need some kind of proxy over them to grab all of the right
(18:27) information. I think it's inevitable that they will emit uh different schemas and different shapes and we might just need to handle that inside the application. For instance, the shapes that pi emitted changed very very recently in a patch version. So whatever we do, we're going to be kind of on the hook for these systems.
(18:56) There we go. That was a big one. Whisper flow does a really good job of like turning this into transcription or like um whoops of uh making the transcription nicer. And notice that I'm using I specifically call out sub aents because I noticed a um oh not sure which agent you mean. Pi is the agent. I mean ulite.
(19:23) So it's kicking off four in parallel. It's kicking off a claude code guide agent which is nice. That's it kind of built-in agent that understands how to teach claw code. Then it's doing one for OpenAI codeex CLI observability. Open code observability. GitHub Copilot CLI observability. So yeah, there's probably going to be a ton of permission requests here.
(19:44) We're on claw code. We're on 4.7. Yeah, exactly. Colin, you can just add your own JSL files. Yeah, grilling. I mean, grilling sessions are amazing. So, if you got any questions, ask me them now because I'm probably just going to be um answering permissions requests for a few minutes. Can't wait for the day when Claude starts to learn how to code from a Claude code course.
(20:17) Well, I mean, skills are basically that, you know. [sighs] H I mean the lites are often right. That's what makes them uh historically notable. Will you ever return to talk about pure software principles that is not in the rounds of AI topics? I I'm really loving this new era because I get to talk about software principles uh while dressing them up as AI gossip.
(20:49) I'm not on bypass permissions mode because I'm not running inside a sandbox. I could run this inside a sandbox. Um, but I'm just not at the moment. Have I tried auto mode? I don't think I have access to auto mode yet. Do I think it would be beneficial to have Codeex go over my Clawude P plan? No.
(21:17) I think people um over review their plans and I think this is a classic mistake in web development. We got Bristol. What's up? This is like people go over and over the specs that they're going to create when what they need to be doing is getting to code. Um Cloudflare is releasing some amazing features.
(21:42) Am I planning interested to cover them? Don't know maybe can I touch on my AFK implementation method? Yeah, I've really made some big updates to that recently, which is I have my uh wind is blowing outside is a uh repo here called San Castle. And S castle is a coding agent orchestrator. And this is incredible because it allows you to run some agent inside some sandbox.
(22:11) So, it allows you to uh really do amazing things with your setup. It is really cool. Yeah. And um when we actually get to build this then I will be using Sound Castle for it because it's incredible. Uh yeah, don't worry about raw GitHub user content. We got a lot of folks in this stream. Hey, 250 of you. I'm your inspiration. Oh, thank you.
(22:56) [snorts] So, it's done all of its fetching it seems about copilot CLI observability just added an issue requesting Docker SPX as a provider. Haha, interesting. Let's just quickly check that out. MicroVMs. Interesting. What were some challenges when creating Sand Castle? Don't know. Um, usual software development challenges really.
(23:38) sort of figure out the language, figuring out the API, figuring out what we're supposed to do. Yeah, this is it. This is um this is what we're building. Clawed code observability. Um trying to or coding agent observability. Let's see what it says. It's been going for about four minutes now. Use sand castle to automate.
(24:03) The app kind of works, but it's not structured at all. becoming tough to change things. Um, if you end up with an application that's really difficult to change or you um there's a really nice definition of complexity in an application, which is complex apps are hard to change. Uh, simple apps are easy to change.
(24:21) The way you turn a complex app into a simple app is you run this improve codebase architecture skill or at least this will give you opportunities for doing it. This uh explores a codebase like an AI would surface architectural friction, discover opportunities for improving testability, and propose module deepening refactors as GitHub issues.
(24:44) So yeah, it's it's difficult to turn a crap codebase into a good codebase, but this will set you on the right road. Could you please recommend a technology stack for projects so I can create bots, backends, and my SAS projects? TypeScript. Just use TypeScript. Typescript node is brilliant. It's what I've built my entire career on.
(25:06) So, okay, here we go. Here we go. All five agents have a similar shape thankfully. So, so they have a hook surface here. Okay. So, claw code has some sort of hook surface. Um, pi has a hook surface too. Open code has a plug-in system. Copilot CLI has some hooks and every agent gives you an event hook and an append only JSONL on disk.
(25:39) Interesting. Schemas all differ and all evolve. There's no single just use hotel answer. Copilot and PI have no useful hotel at the CLI level. The proxy path is blocked for copilot. Okay, interesting. So, a per agent adapter is unavoidable. Yeah, that's what I thought. Each adapter uses that agent's best surface hooks for live events.
(25:58) Jason Taylor's back stop and normalizes into your internal event schema. Yeah, one local demon loads the right adapter. Uh, does it resolve Q3? Chill out, mate. Chill out. AI is always so aggressive in like trying to create consensus, you know. Yeah. So, I'm I'm not going to answer Q4 yet because we haven't resolved Q3.
(26:22) Go back to Q3 for me. I still haven't decided yet about whether we do a hooksbased system or whether we track the JSONL locally. Happy to catch me live. Happy to be live. 279 of you in the chat. It's huge. This is big for my streams. I mean, I almost never stream. So, yeah. I haven't decided about a hookbased system or whether we track the JSON locally.
(26:58) I guess I mean this is just something that we could experiment with an implementation. It's kind of an implementation detail. It sounds like either option is viable. Need your opinion about models. Miss the edge cases in the product you're making. We always have to write it manually. These can be sold by making a skill or something that gives you edge edge cases.
(27:22) I mean, catching edge cases is hard. Like, it's a hard thing. You have to um accept that you're not going to catch all edge cases when you're planning. So, you have to build in the idea that you're going to QA your application. You're going to make sure that nothing got missed. You know, it's just hard thinking about all the edge cases ahead of time and it's largely impossible.
(27:44) Okay, here we go. Let me lay this out properly now that the research is in. The research shifted my thinking. It's not really a binary choice. Hooks alone are insufficient for most agents. Claude code hook payloads don't include message content, so you still read the JSON. Interesting.
(27:57) Copilot hook payloads are thin. Codex hooks are flaggated and Windows excluded. Ha, I'm on Windows. JSONL alone is efficient and sufficient for some. Right. Right. Right. Right. So what we need to do is change the approach per agent. That makes sense. That make sense? [sighs] Yeah. No, I dig it. So we are trying to investigate um building a coding agent observability platform.
(28:43) That's the plan. Uh, I switched to Windows so that I could expense my graphics card to the business. What's my opinion of people saying that UI front end is the differentiator in the AI era? I don't know. I'm not a pundit. I'm just a teacher. Um, okay. So, at this point, I'm thinking, right, this this context window is now really good, right? We've got a really cool context window.
(29:18) It's full of um interesting information. How do we preserve this going forward? Because I'm I'm not in a directory here. Um we've like invested uh 42 or 45.2K 2K tokens here into researching different coding agents into figuring out some early decisions and I want to save this somewhere and the best place for that is to actually kick off a repo I think.
(29:49) Should have gone with Mac OS and remote Linux Windows system for the GPU. Yeah, that's a good idea. [sighs and gasps] That's a good idea. Uh so I need I want to save this somewhere. I want to save it in a markdown file. But I feel like at this point, you know, we've um sort of figured out the first few bits of the project.
(30:19) Have you used speech to text in Windows 11? Yeah. Uh it's not great. The native one is not great. I don't love it. Uh I use Whisper Flow. Yeah. We got to create a research document. Um, yeah, let's do it. Okay. I love the things that we found here. Um, I want you to create a new repo for this. This new repo is going to live inside reposi.
(30:50) What? What should we call this? Okay. Yeah, let's figure out a name with Opus. What name should I give to this project? I want a just quick placeholder name I can put down to differentiate it from my other projects. Opus is really good at choosing names for stuff. Um, it shows the name Sand Castle, which I really like.
(31:13) I think that's a clever one. Agent scope. Okay, guys. I need your help. This is not good. Agent scope. No, I don't like that. Loop a jeweler's magnifier to inspect sessions or peak. I don't like peak. Peak is sort of, you know, like you're peeking in the peeking in the park. Dirty little peaker. Agents watchtowwer.
(31:42) I barely use, by the way. I suppose it is a a good by the way, but it just feels by the way just feels so underpowered that I just never use it. We're building an agents. Uh, in fact, we can recap, can't we? [laughter] Look at that's actually really good for streams. [snorts] There you go. I don't need to talk now.
(32:01) I could just Wee agent master telescope telescope agent guard peeping Tommy. See cam Harry Potter inflected. Peak. Peak. I kind of want it like metrics based, you know, panopticon. Sauron Barador. Palante. Palante is taken. Mother agent. Vantage. Isn't Vantage a Yeah, Vantage? No. What am I thinking of? This is tough.
(32:59) Give me more ideas. I want them to be kind of metrics based token scope. H. This is an accidental beard. It's not an intentional beard. ACQ. Oh, here we go. Tally H yard stick ledger rubric quant readout Argos agents agent reef [snorts] I mean all of these ideas are taken right surely I don't think I can do fullbeard for me is like a sort of a row of dead hamsters all just sort of gathered along they don't join up you know rubric Quick readout. Quant.
(33:42) God, it's all just rubbish, isn't it? Caliper agent index. Quant yard stick. [sighs] Sort of feels British, you know. I know that. Burning a lot of tokens on it. I know. Yard stick. Yeah, we're looking for a temporary name, right? Let's just call it yard stick. >> [snorts] >> token site agency. Espe um something in Latin.
(34:32) We need a motto. That's what we need. We need a uh what you call it? A coat of arms baseline. Where my token go? Where do token go? Where do token come from? Um, I mean, yard stick seems like it's got a bit of uh metrics. Let's just go with yard stick. Okay, I want to save all of the research that we've done apart from the name stuff in or in fact, you know what? Let's um let's take Claude out of this.
(35:11) Let's actually go back and resume to um just here so that we kill all of that context. Basically, we just sort of clip off that bit of context. So now we're just right at the end of the research phase because that little sort of diversion is not something I sort of want to go back to. So it's almost like we've gone back in time.
(35:33) Now we don't have to keep that in our context. So, we figured out yard stick dilly. [laughter] That's good. Dilly tally. Crow's nest. That's nice. I mean, how many observability companies that Let's just look for the uh Crows Nest observability company. Crows Nest software. There we go. Monitor key business metrics.
(35:58) Uh Yardstick observability company. Yardstick Trust reimagined a technology platform that makes human credibility into something you can continuously see. Yes. Build your dream team with Yardstick's AI powered interview tools. I mean, every one of these people just asked Opus, right? Uh, I cut the context by uh just doing resume basically.
(36:23) So, I went back to a previous conversation. My next call for real engineers is happening. Um, I don't know. I'm going to work it out on Monday, but probably miday, I think. Token autopsy. Let's just go with yard stick. So, we've produced some really good stuff inside this context window, and I want to take it all and put it inside a research document.
(36:48) I want you to create a new repo for me here. Slopwatch. Slopwatch is really good. [laughter] Slopwatch is really good. That's really good. Slopwatch. Slopwatch is a is a winner. Sorry. That has just pipped yard stick to the post. That is incredible. So, it's going to be inside reposi slopwatch. That's genius.
(37:26) Wow. Eddie. So every everyone just go and follow Eddie for that one. Where's Eddie? Eddie There you are, pal. Is my guy Eddie? Go and follow Eddie. A funny funny man. Did Was it Was it you? Yes. Slwatch is great. Perfect. H That's really funny. That just makes it feel more real, doesn't it? Eh, I want you to create a new repo for me here.
(38:04) Put it inside the research directory as a markdown file. I want you to specifically focus on the valuable stuff that we learned here on the differences between the coding agents and the fact that we'll need to take different approaches in recording their data and uploading them somewhere. Cool. There we go. stopwatch.
(38:27) Incredible. So, we've um kind of let's just walk through what we did there, which is over the past how long have we been going? Like 40 minutes. Hey, we've gone from idea to essentially uh a research document. That's sort of where we're at. And this I think is like an early is the way that I treat Greenfield projects is they're essentially until you get to code, until you start sort of putting PRDs down, until you start um working through your ideas properly, seeing your ideas reified into code.
(39:08) You're really just um working with research. That's what you do. It's a research task. Registering gift the slotwatch domain name. It's the danger of doing this stuff. Actually, I remember I was doing a um I was streaming something about TS Reset, I remember, and someone nabbed the nabbed the package name from me.
(39:33) I use Whisper Flow. That is not a Garmin. That is a Pixel Watch. It's got loads of scratches on it. Very annoying. How do I get Claude to focus on System D's scalability to a million users? Uh, well, scalability to a million users is a hard problem. So, once you realize how difficult the problems are that you're asking Claude to do, um, oh, slop cop.
(40:00) Slop cop. That's good. You'll realize that maybe you should just, um, AI is going to do better when you help it. So [snorts] yeah, I think human plus AI is always going to perform AI no matter how good AI gets. Pebble 2. Hey, we had a Pebble 2. Okay, so we got you initialized repos AI slot watch as a git repo and we wrote research coding agent ingestion. Okay.
(40:35) Um so let's cancel out of this. Um going to cancel out of this. So, we're going to code up repos AI slopwatch. Uh, I'll push it to GitHub as well, so we get it. Uh, did I get any update from Anthropic around the terms of use question you've been waiting over a month for? I did not.
(40:51) No, anthropic are still ghosting me on that one. Um, okie dokie. So, we got a read me stopwatch. I like that. Extremely low effort. It's rare you see coding agents put that little effort into a readme. [laughter] that really makes it funny. Uh, okay. Headline finding. I I generally don't read these research documents.
(41:14) The important thing for me is that the um uh conclusions that we came to. I'm going to commit this. I think I'm just going to use um GitHub copilot setup and let's publish. So, slotwatch heading to GitHub public. Exactly. Help the AI help you. Um, okay. So, I didn't want to do do too much on this stream because this is a great idea. I'm really glad I came on stream.
(41:47) Slotwatch is a really really funny name, first of all, and it just crystallizes the the idea and that's awesome. What I want to do is I think set up the repo. I want to set up the repo. And for that, we're going to enter a new grilling session. For long-term agent memory, I'm thinking that I think long-term agent memory is a is sort of a bad idea.
(42:20) You want something that's super observable, that's super concrete, that you can edit immediately, um, and that you can fit into context window. I think so. My current idea for this, which is really only germinating this week, and that I will be testing on this project, is using ADRs, architectural decision records, and using um, a sort of minimal version of DDD domain driven design.
(42:51) So yeah, let's set up the repo because that's going to be boring to watch on a video and we've got nearly 300 of you guys here. We're going to use a fresh context window here and we're going to do another grilling session. I think I'm going to go for a um this is my new version of grill me.
(43:06) It's not got a very good name. It's just called domain model. Um but it's essentially grilling an orbit name. I want to set up this repo to be a Typescript repo. Actually, no, we're not there yet. We can we can't figure out the stack yet because we haven't figured out the shape of the thing that we're building.
(43:35) So what I need to do is I'm going to do some domain modeling here uh with I'm just going to pass in research uh conig agent ingestion. So I'm just going to what I've done is I've taken all of the stuff that was in our previous context window and I've moved it essentially summarized it compacted it into a research document that's going to persist in my system and then we're going to move on from there.
(43:58) It's obviously going to be TypeScript, but the shape of it is up for question. I'd like to talk about the potential architecture for this thing that I'm trying to build. I don't have a strong idea in terms of um what the different deployable units are. And I know that I'll need some kind of front end.
(44:28) I know that I want it to be pluggable so that people can host their own version of this. I'm not really that interested in producing kind of centralized service unless it produces a really good DX for people. I'm not interested in being in handling people's data. I want people to own their own data and own their own storage mechanisms for this.
(44:48) I'm imagining there will be some kind of CLI component to this that you run locally or perhaps a desktop application. I'm really uh totally open to the idea. I mean, this is wide open. We could choose many potential different things here. Maybe a desktop app is like the most sensible idea because we obviously need some kind of persistent API, some some sort of port running locally that's going to capture all of the data.
(45:19) Then we need something to sort of Okay. Well, let's see what it says. Who is the primary user of slopwatch? A solo developer watching their own agents or a team or watching many developers agents? How we sort of had this, didn't we? Yeah, we sort of had this. Business-wise, Matt, have you found more people follow your funnels and become customers today as compared to the TypeScript courses days? Are they more inclined to learn on their own using LMS? Um, my CLCO course was the most successful course I've ever run. So, um,
(46:04) I'm happy in terms of where I am, where I'm positioned in this market. Um, and I feel like there's a lot of good stuff for teachers to do here because people are using these tools wrong. Um, right, we already we already um answered this, right? I'm actually going to you know what I'm going to do? I haven't done this before, but uh I think this is funny.
(46:29) I'm going to run Claude back in my previous uh setup here. I'm going to res resume the conversation that we had here. And then I'm going to say to it, I just got asked this by another Claude code session. How would you answer this based on my answers before in this conversation? So, I'm basically going to get one clawed code to answer another.
(46:56) [laughter] That's funny. This is the reason I have to do this is because I um this conversation was outside of the repo where I'm now working. A peanut gallery. That's a great one. I don't have access to auto mode. Here we go. So, that's good. I'm not going to read it. I'm just going to assume it got it right.
(47:23) I already answered this in another chat. I asked that agent and this is what that agent said. There we go. Bye, Colin. Have a good night. Okay, it's uh it's figured it out. Uh oh, yes. Okay. No, I don't think this is right. No, don't be so eager to create a context MD file. Yeah, I'm experimenting with effort.
(48:11) Um, Claude released XH high mode and it defaulted it created the new default claw code is X high. I can reference another session so the agent can get its context. Um, but that only works if they're in the same directory. We are building a uh coding agent observability tool. Really dreading AI coding until recently and your content helped me get there.
(48:42) Cool. I'm really happy to hear that. Okay. [sighs] Given T-Oorg self-hosted with mandatory on-prem backend live spectate, the next fork is about the capture side. What runs on each developers machine? Whoopsie. Whoa. Hello, Claude. Come on. Update your blooming ghetto UI is terrible. Is terrible. Okie dokie.
(49:14) Is the on machine capture component a longunning background demon or a per process perification process that starts and exits with each agent session? Um, it's a good question. A longunning demon that watches all configured agents continuously maintains FS watches on Jason. Yeah. Right.
(49:37) Because in our research we found that just using hooks was not enough. Um because okay I'm going to explain this deal. In the research we found that hooks was not enough. The cool thing about the hooks model is that you get to totally delegate the process running down to the agent that's downstream and the agent that's downstream just gets to ping network requests off and we don't need to run a separate process.
(50:12) This potentially means that you could have a process running on a remote server that captures the or ingests the information and stores it. What I'm worried about is that people will forget to run this demon somehow and then they although maybe we could start the demon via hooks. How much am I spending for a while? I was on um max 5x which is $90 a month, $100 a month, and now I'm on um 20x, which is $200 a month.
(50:54) Close UI is perfect. 4.7 x should burn tokens approx 4.6 high. That's interesting. 4.7 seems like a junior with a dangerous amount of technical knowledge. guessing at a fix until the build succeeds and assuming that that means the program is correct. I think people overcharacterize LLMs um and anthropomorphize LLMs too much.
(51:18) You know, people say uh that oh yeah, 4.6 feels different to 4.7, that kind of thing. I always think that we can't really get a representative sample. You know, um everything that we do is sort of tainted by our own process and tainted by our own experience with these LMS. So, I think people put too much stock in that.
(51:40) Okay, here we go. So, you're right. I think my recommendation was wrong. Let me refactor the insight you're pointing out. The hook is the trigger that starts a process. So, we don't need a pre-existing always on demon. Yes, that dissolves the people forget to run it problem because the hook configuration is the install.
(51:59) But the pure hook fires curls backend exits isn't enough. The research already established that hooks don't carry full message content and live spectate is a per session capture process spawned by a hook, not a machinewide demon. Yes, that sounds right. Session start hook fires slopwatch capture. Uhhuh. Only for the lifetime of one session.
(52:24) Yes. Cool. From the users perspective, this is demonless. They configure hooks extensions once. Yes, that's good. Yes, that's good. The one thing that gets slightly awkward if you have two claw code sessions running concurrently, you have two different subprocesses. They're cheap and independent. Yes, this is good.
(52:46) This is good. Yeah, I like this. Does this per session sub process spawn by home instinct? Yes, it does. Am I okay for clco codex? There is a shortlived stopwatch process. Yes, that's fine. I really like this. You've done a good job here. Having essentially a sidecar process is a really nice model. I like that phrase, too.
(53:17) Sidecar process. I'm using I'm testing out medium. Yeah, extra high is only for opus. That's right. Demonic plugins. What you talking about? Slobing away. All right. How does a session get attached to a developer's identity and how does the sidecar authenticate to the back end? I So, okay.
(53:55) One thing to notice when you start doing grilling sessions is when language starts to calcify when you start seeing different terms um be used here. So the sidecar is now our terminology for this process that's running inside the claw not running inside but running next to the claw code process.
(54:16) So that's just something to bear in mind and something I like to capture as part of my development process. Have I got the context window always displayed? If you search for uh where is it AI hero claude code status line then you will find it. So this is uh some this is an article you can pass into your LLM to get this beautiful status line down the bottom which is really nice.
(54:41) Look at me in my nice shirt with no beard. Okie dokie. Huh? Huh, this is smart. So, it's asking me um how should we attach a session to a developer's identity? And it's given me some smart ideas here. So, it's going for first of all git config. So, it's zero setup. It just reads the user email at spawn and it's trivially spoofable.
(55:13) Doesn't match the org's identity system. Yeah, that's interesting. Explicit login during npx slopwatch install. Yes. And again we have a kind of install thing calcifying here. Let's see. Yeah. So scikar reads a token from here. Token is minted by the back end when the dev authenticates once. Yeah. Yeah.
(55:45) Yeah. So I guess we're starting to get somewhere. We're starting to see something kind of come out of the mist here because all they need to run locally, they just need to run npx slopwatch install and then somewhere in some other process um there's probably something deployed somewhere that they can do what you call it um oorthth with yeah oorthth device flow against the org's configured IDP with a long live refresh token stored in the OS. as keychain.
(56:22) Yeah. Cool. Cool. The back end becomes an OIDC. Okay. Now, I'm starting to be a little bit freaked out by the language it's using. So, I don't know what an OIDC is. You may do. I don't. So, I'm just going to do a a little zoom out, which is one of my skills. Tell me a bit more about what OIDC is and what an IDP is.
(56:46) I'm a little bit out of my depth here. Zoom out is just a teeny tiny skill kind of like grill me that uh just gets it to kind of like an explain like I'm five. So, what's it going to say? It's taking its time. All right. [clears throat] So, orgs IDP I suppose identity provider. It speaks OIDC.
(57:31) The OIDC protocol links to the slotwatch CLI and the sidecar on dev's machine and the slotwatch. Yeah. Oh, I see. Here we go. So, it's given us all this. Ah, I see. Nice. I only saw the thing at the bottom. So, yeah, IDP is the identity provider, the service that actually stores who works at your company and who authenticates them in a typical org.
(57:59) One IDP is the source of truth for does this person exist? Yes. Cool. Um, GitHub or zero. Yeah, cool. Yeah, I don't know if we want to like I mean this is big. This is a big feature. Don't know if we want to do something simpler than this authentication and this is open ID connect. I see. I've heard of that.
(58:28) So the flow strips jargon. User open slopwatch. Slwatch redirects them to this login. User logs in there. Octa redirects them back to slotwatch carrying a sign token. Yes, that makes sense. Stopwatch verifies the signature against Octus's public key and trust the claim. Cool. Very cool. Yeah, OIDC is built on top of OATH 2.0.
(58:51) Cool. More standardized way. Okay. I've used Oorth a bunch of times. I just didn't know what OIDC did. Got you. Normal OIDC assumes there's a browser. CLI don't have one reliably. Yeah, cool. Here we go. This is what you got to do to login like GitHub or and stuff. Slotwatch login calls the IDP gets a back a short code.
(59:15) CLI prints go to this thing. Enter this code. User does that in their laptop browser. CLI pulls the IDP every few seconds. Done yet? Until the user completes the brow step. Beautiful, beautiful, beautiful. Yeah, there you go. Get all login. Nice. See you. Relying party got you. Okay.
(59:40) So I suppose the question I have is get out of here. Do I need author just to get something up and running locally? Yeah. My question here is that this seems pretty heavy and I wonder if there's a kind of crappier version of orth that I can ship for version one just so we validate the idea early.
(1:00:06) I don't want to have to go through the whole rigarole of doing this or protocol if we can get something working for v1 a little bit simpler. The important part of this is that we validate the idea early. Right? This is a classic software engineering principle. We could spec all of this stuff out, but we actually need to validate whether this is a decent idea.
(1:00:31) We need to see it working. We're we're in the abstract bit right now. H works. I don't know what work I've got some friends who work at work OS, but I don't know what it is. Oh, here we go. Okie dokie. Ah, for God's sake, Claude code. Okay, I can push OIDC to version two. Two genuinely light options, a per user admined token.
(1:01:06) The admin runs the self-hosted back end, opens up a little admin page, clicks add user, types a name and email, gets back a onetime token string, hands that token to the dev over Slack or whatever. Yes. Dev runs slotwatch login and pastes it. Scikar stores it. Sends it as a bearer token on every request.
(1:01:24) The identity is trustworthy. Each token is bound to a user record. Cool. Yeah. So the admin creates the user that has a user record that owns the user and then that just pings down to slot. No IDP integration. Yep. Deprovisioning works because the admin just revokes the token. Yep. Upgrade bath is clean. Yeah.
(1:01:46) Yep. Yep. Yep. Yep. One admin CRUD screen. Perfect. Yeah, that's nice. A day or two. I like that. It gives me a That's like five minutes of work with AI. I love that AI doesn't really understand how long AI takes to code something. Fascinating. Uh yeah, this is the one. This is the one. Option A is great. Is it one of Theo sponsors? Yeah. Yeah.
(1:02:20) Yeah. This this will um stay as a video for sure. Now, it's tricky because I don't want to go too far here because I want to this whole idea of this stream and the reason I came on stream is I want to turn this into a proper video where I actually go through and walk through this stuff. Ha, here we go.
(1:02:50) What does deploy a slotwatch backend look like for the org admin? One binary with everything embedded, a Docker compos bundle or a Kubernet Kubernetes shaped set of services. This is the question that shapes what a back end actually is. One process or several what storage how the front end is stored.
(1:03:09) A single binary battery is included. Woof. So one go or Rust executable. Woof. We might be heading into a Rust build. How about that? Did a major migration last night. It estimated we take four weeks. [laughter] That's funny. [sighs] Um, upgrade swap the binary storage a DB file on disk. Plausible self-hosted Grafana Loki single binary.
(1:03:51) Huh. could be. Yeah, I think I prefer a Postgress backend than an SQLite backend. I don't want to do Kubernetes. I think probably this is tricky, right? You can make single binary TypeScript executables with bun too. This could be a bun build. This could be a bun build. And when um what is it? When P4 is finished, then we can use P4 instead.
(1:04:34) P4 is crazy. Have you seen P4? And it's a terrible name. I don't know why they chose that name. Yeah. So, hybrid [snorts] single binary by default. Mhm. Mhm. Yes, hybrid single binary makes sense. I think pointing to a Postgress database also makes sense. I think that the database needs to outlive the changes to the application and I want it to be on a different deployable unit to wherever the binary is running.
(1:05:31) This I mean this is hardcore, you know. This is this is watch me work, right? That's the theory behind this stream and this is what I'm doing. This is how I work. I'm using 4.7. Yeah, it's doing good so far. I mean, I'm not really noticing a difference. It could be bun. Could be bun. because I mean it would need to be some kind of executable plus an application right but then the application yeah this this is a question I have um how does live spectate work server side has an event from a sidecar reach a manager's browser tab in 100
(1:06:19) milliseconds um the sidecar on Alys's machine post events to the back and a manager watching Alice's session has a browser tab open. Something has to fan those events out from the ingest path to the watching tab. Now, I think it's going overkill here. Let's take a simpler approach here. I want to focus on um I think we can do this with polling, right? I don't think it being as live as possible is really needed.
(1:06:58) Polling every 5 seconds or so or whenever the user focuses back on the tab is probably good enough. This is interesting. Like we are really in blue sky territory here. So it's sort of going into funny implementation details. I'm on medium because I'm just testing it out. Yeah, exactly. TRPC or something. I mean, or yeah, this is interesting.
(1:07:32) We could build like a Rust back end, couldn't we? And proper binary. I've never done a Rust project before. It might be fun. Might be really fun because we definitely need like a element of TypeScript and a front end here, but having an actual, you know, Rust project would be really fun. I don't know.
(1:07:49) Maybe I should just stick to what I know. What does the DRRi review inbox actually contain and what's the sessions life cycle? Okay, so at this point I feel like I'm sort of sick of like talking about the app now because we're in like I'm starting to get a bit of brain burn. What I need to do is actually I think I want to exit out of this and create a new research document based on what we found.
(1:08:16) So I want to compact this session um because we're sort of going all over the place and then I want to start talking about the language because the language how we talk about the application is really important because the AI and I need to be synchronized in terms of the way we talk about it and there has been some really key terminology that's come out of this like the sidecar process like the um admin like the user you know that all that stuff.
(1:08:45) So, I think I want to exit the grilling session here and create another research document in this repo that captures all of the main decisions that we've made. This obviously will be um a partial one. It will it will have unresolved questions that I want to be able to pick up later. Let's do that first. Opus is good at Rust.
(1:09:13) >> Yeah, I'm pressing a key on my keyboard. to trigger whisper flow. The grooming show, the grooming skill is crazy. We we're doing a grilling right now. We're inside a grooming skill. I saw someone uh that said the grill me skill had asked them uh like 200 questions the other day. It's such a game. It's crazy good.
(1:09:32) It's crazy good. I'm just going to have a little sort of brain break and I'm just going to check WhatsApp for a second. My son's with his parents and so uh um Oh, he's having a good time. Oh, sweetie. Done. Yeah. I mean, like there's there's only so much so much deciding you can do, right? Yeah.
(1:10:02) What what what I notice here is that we don't have like um natural um breaks. Coding was kind of like a break from making decisions. It feels like what because when I do this solo, when I'm not streaming, I will tend to have two grilling sessions happening at the same time, you know, one in either terminal.
(1:10:26) And it's just, you know, you're constantly making decisions, making calls. Um, and it's, you know, it's exhausting really. I'm bored of talking now. Get on with it. Yeah. I mean, you sort of need to uh at some point just call it on the deciding because really you can only make meaningful decisions when you're working with an actual asset.
(1:10:51) Um, just working in this kind of abstract space is not good. So, eight resolved decisions. Team or self-hosted or web visibility dest cool. Again, I'm not going to review this research document. I'm just going to trust it because I'm going like I think of um the PRD as like a decision documents basically um or sorry, a destination document.
(1:11:20) The product requirements document kind of describes where we're going. This is not a PRD. This is just like research that I'm doing into the idea that I have. But what I want to do now is sharpen up the language. Two week break to refactor all the slop. I mean, you'll see. I mean, there's not a ton of slop that comes out of here.
(1:11:45) Would it make sense to do different grilling sessions for back end or another for front end and take each side one at a time? No. Absolutely not. uh back end and front end is an artificial decision. The domain, the problem space is the entire thing. Backend and front end are just two um deployable units.
(1:12:04) Um and if they are like we separate them because traditionally we've organized companies around hiring front-end teams and hiring backend teams. That has always been a bad decision because it means that you get too focused on your domain and you don't think about the entire problem space. Um, it's not so much a road map document. I'll show you what I mean.
(1:12:28) Um, I just want to firm up the language. So, I want to firm up the language a little bit and take some of the terms that we've got so far and put them inside a context.md file. Let's do that now. But grill me about each decision. I want to have a lot of control over this. So you'll see what I mean in a second.
(1:12:56) You have to answer all the nuance details about every single thing that might not be of value on initial ideation. It depends. It depends basically because you want a lot of questions from the LLM so that you can tell if you're aligned or not. I mean, I can feel from this grilling session that I have a much clearer idea of what Sloatch is going to be.
(1:13:21) Eddie, what a great name. What a great name. Sloatch. Absolutely killer. Okay. Um, so session. Ha, there we go. Starting with the low most. Okay. So, the point of this the point of this exercise that we're about to go on is that when we firm up the language now or start thinking about language ideas, we can be so much more precise going forward.
(1:13:55) So, the first term it's it's proposing to me is session. A single continuous run of one coding agent from launch to exit attached to one uh developer, one current working directory, one agent version. I love it. Yes. Yes, it captures uh you're capturing data from a session. Yes, I love it. Love it. Love it.
(1:14:14) And it directly maps to a sessions table. Notice how the language, the way we talk about the application is so important here. If session is fuzzy, the whole data model is fudgy. Fuzzy. Um. Yes. Okay. Right. Right. So, there's some edge cases here. Oh, so good. So, resumes Is a resumed session the same session as the original or a new one that points back to the parent? So good.
(1:14:45) Such a good edge case because you're right. A session is like it's it can have you know you can branch right. So yeah again we have forks here. How do you track that in a UI? Right. Dilly tally. Are you actually going to build something or is this pure vibe coding? Yeah, I'm going to build something. This is how I build stuff.
(1:15:17) No, no, this is ubiquitous language. This is ubiquitous language 100%. I think DDD is a fantastic match for uh AI coding 100%. So, clawkins code tasks spawn sub agents that write their own JSONL files. Is each sub aents run a child session or part of the parent? Wow. Here's a little TypeScript wizard. What you saying? Agent version.
(1:15:50) H. Wow. Brilliant. So, [clears throat] all of these are questions that are really hard to answer. Yeah. A fork. The the issue is forks, right? And branching inside the session. Because yeah, are we really going to track that in the UI? Because when we think of a session, we're thinking of like a big list of sessions that attach to the user.
(1:16:15) Feel like I might need to do a diagram here. Gosh, it's this is a hard call. New session with parent ID. Yeah. Because the language we talk use here is so important. The forks one is really tricky and it's really hard for me to work that out. Can you throw some scenarios at me so that we can road test that language more? So this is what DDD does.
(1:17:05) They um domain driven design. The theory behind it is you take a bunch of if you have a sort of disagreement about language um then you take some concrete scenarios and you sort of see which ones are easy to describe with the language that you're using. And that will usually map on to uh whether it's easier to code or not.
(1:17:31) Yeah, loves patterns. Goes so well with DD dependency injection. Yeah, totally. Okay, so scenario A, the explorer. Here we go. Alice is refactoring or module in PI. After 10 turns, she's at a decision point. Rewrite with middleware or refactor in place. She branches. Tries middleware for eight turns. Doesn't like it.
(1:17:53) Branches back to the decision point. Tries in place for 12 turns. Ships it. the middleware branch is abandoned. So is that three sessions or one session with a directed asyclic graph because yeah there's a concept of sessions here and then turns within that session and maybe the turns are sort of branching points right.
(1:18:16) Yeah we are um saving live streams on the channel. The middleware branch costs real tokens and produce real artifacts. files were written then rewound. Does the DRRi inbox show all three? Does Alice's session count this week show plus three or plus one? Brilliant. Okay. Scenario B. Bob is using Pi. 40 turns in, he rewinds two turns to rephrase a prompt.
(1:18:39) Pi treats this as a branch. The old two turns still exist on the By the way, if you don't know what DAG is, directed a cyclic graph. How did Claw get detailed info? We did a research phase earlier where we looked at coding agent ingestion and we looked at basically did a bunch of research went and did some documents and then it has all this stuff in its context.
(1:19:03) You're right. I I am a little bit suspicious about understanding its understanding that it does this but I'm willing to just sort of take it on faith here. Yeah. So I think we need a concept of a turn inside a session. Carol is Dr. Dave is in pi. Carol opens Dave's live spectate view. Dave branches. Now Dave is on branch B.
(1:19:25) Branch A still exists in the tree. Carol's tab is polling. Yeah. Which session is ID? Yes. Yes. Yes. Yes. Yes. Okay. So, let's think about there being sessions and then within sessions there are turns. Since turns maps on to API calls that agents make to the back end or maybe I mean we can argue about terms there might be I don't know there might be some other term there that we use but so a session can contain the directed asyclic graph of all of the branches that were created in the tree.
(1:20:15) Does that make sense? I mean this is 4.7 so I assume its knowledge cutoff is fairly up to date but yeah I I don't know I mean pi's existed for a little while I was actually um at a conference recently I was sat across from Mario the guy who created Pi I didn't realize who he was and I actually um didn't talk to him for the entire time the only time we uh chatted did was um this was at the speaker's dinner for AI engineer London and he said um what is that and pointed to a place of food and is that for everybody or just
(1:21:00) you? Obviously I was being very covetous over the butter chicken. Okay, here we go. Good move. Let me lock in the DAG inside session model and probe to residual fuzziness points. The new shape session is logical turn. One row contains a DAG of turns. Turn is a node in that DAG. Yeah. Yeah. Yeah. Has a parent turn ID.
(1:21:30) Most agents produce a degenerate DAG, a straight line. Only PI produces real branches. Don't know about that. Two things are still fuzzy. Turn terminology. You said turns map onto API calls. That's not right. In standard agent parliament and the gap matters in most agents own docs. A turn means one user message plus the full assistant response. Yes, that makes sense.
(1:21:55) What if called API call a model request? I see. I see. Here we go. A turn versus a model request. Yes. Yes, that makes sense. What about resumes and sub aents? Now that we have the DAG model, the DAG resolves forks but not these. Okay. Context codeex resume context was compacted and reconstructed. Is it the same session just a resume marker turn in the DAG or a new session with a parent session ID? H.
(1:22:41) This is really hard, man. What are your picks? Sub agent should be child sessions with a parent session ID. That's for sure. H yeah, I don't know about compaction because we are building a um a coding agent observability tool and the thing we're working on here is when you finish a session [clears throat] and you or rather you're in a coding agent session and you compact how should that show in the imaginary UI? Uh I imagine memor is not the same artifact stitching session.
(1:23:41) I mean this is this is something that's so hard to answer because we're in such an abstract space. I think we're going to need to figure that out in implementation. So I'll just say that. I'll see what it says. The resume one is really hard for me to figure out while we're still in this abstract mode. I feel like I'm going to need to see a basic version of this working first before I can make any reasonable calls here.
(1:24:06) This is we're building slotwatch. We're building an agent observability platform for either individuals or teams. Genius name. Genius name. Resume stays open until you've seen real data. Yep. Okay, so it's now writing a file to disk which is going to basically be um here we go. Uh let's make this edit context and let's just review it then.
(1:24:37) So this is a file that I'm now using in most of my projects and I don't I don't like this. This really like Okay, let's slightly update the Okay, essentially what it's got here is a glossery which in DDD terms will be a ubiquitous language. So we have a session which is the logical run of one coding agent attached to one developer and one current working directory.
(1:25:09) A session contains a directed asyclic graph of turns. It's not done a good job in formatting this. Actually, you're not using the formatting that's specified in the skill. Can you go back to it? Uh, not skill.mmd, just skill. All the coding agents model things differently. Get to rediscover all their opinions. Yeah.
(1:25:34) How do you manage AI not doing crap code like 500 lines file, bad separation of concerns, junior code sometimes? Um, well, I mean, that's a pretty big question. The answer is that you bake in uh what I'd say is number one, you first um you got to align yourself with the AI, right? You got to make sure that you and the AI are aligned in what you're building.
(1:25:56) Second is you um build in architectural awareness from day one. You get it to specifically tell you all the modules it's going to build uh and you have some control over the modules. And then you uh you add automated review. And then periodically you review the codebase with an AI next to you using my improve your codebase skill which not only improves the architecture of your codebase, makes it easier to change, but makes the feedback loops better for the AI so that it's not producing crap code or code that doesn't work.
(1:26:35) Yeah, a DAG is for branching sessions. Here we go. This is better. So it's actually using the the right format now. So okay, we got a language which is a coding agent. We've then got a session which is one logical run of any coding agent. We've then got a turn one user message plus the full assistant response.
(1:26:54) We've then got a model request, one HTTP call, the agent makes the model provider during a turn. Okay, cool. So these are starting to be sort of entities within our database. I still sort of use Ralph loops. Um, I'm using Sand Castle now. Yep, this V will be available afterwards. Cool. This is good. I'd like to discuss some of the architectural stuff here, such as the sidecar, the binary, if we want to call it that.
(1:27:35) Yeah. Now, when we get to building stuff, I'll show you um my automated review step. You would need an agent observability platform so that you can get insights as to what your agents are doing. So, if you're, you know, how many tokens you're spending, how much context window your AFK agents especially are using.
(1:27:52) This is most and also if you're a team leader, you want to know how your team is using agents and you want to maybe um you might want to compare the sessions using one model or compare the sessions using another model. Yeah, we're grilling about slopwatch. You got vendor locked inside lovable cloud. For some reason, that's a just a strange image in my head.
(1:28:19) Uh, how to migrate from lovable cloud to superbase without losing data? Um, no. I would ask Claude uh using grill me. If they're both post P postgress, you might be fine. Uh, okay. So, grilling the on machine capture thing. The naming is harder than it looks because there are two physical forms. Brilliant. Uh, the naming trap.
(1:28:44) The thing has two forms based on the project. It's either a subprocess or in process code, a TypeScript extension or a JS plugin. Cool. We need one umbrella term for the thing that captures the events on the dev's machine. Yeah. So, yeah, this is cool. So, we've either got a sidec car or an adapter, a collector.
(1:29:15) Yeah, it's a bit too hotel flavored. The capture capture is that right? The capture runs on the developer's machine. Okay. Interesting. So it doesn't the AI doesn't like sidecar as the process. This um if you're tuning in late, this is the process that um essentially runs next to the coding agent, captures the data that the coding agent is putting out and sends it to the um the deployed back end which we also need to name capture.
(1:29:59) Capture surely. Can you use capture like that? Is it not capturer? Listener. Yeah, I suppose listener is good. Listener is probably good. I like listener. Using sand castle. Sweet. We like Matt PCO. That's nice. I don't like capture on its own. Ingestion pipeline that sort of refers to the entire thing.
(1:30:41) This is like a one small part of the um ingesttor I suppose is good. Capturer adapter tap h claw code tap sits on the pipe and siphons off a copy. That's quite nice. Um, capture is a count noun is grammatically iffy. I don't like that agent. That's not doesn't not going to work for us. Capturer. What about listener? Watcher.
(1:31:19) Makes sense. Watcher makes sense. Watcher. Listener. Seer. Oracle. listener collector maybe collector I feel like it said collector didn't it if it my call I'd order them let's have a look listener is already a term of art inside themselves pi's extension API is already this okay so it's it's worried about collision between our terminology and the other terminology.
(1:31:59) Who watches the watcher? H blandness. Yeah, it is too bland, isn't it? Voyer snitch peeper. [laughter] The improcess peeper. You dirty little improcess peeper. feel like because we're uh that would be funny actually just to have I think maybe people should name like they should have funny language to talk about there.
(1:32:38) Uh [sighs and gasps] yeah, I like it too. AI assisted dev is actually really fun for streams. Spy spy. What about peeper? A dirty little one. Taylor. Taylor. Dirty little peeper. Yeah, I'm still thinking that 100k tokens is still the smart zone. Producer is not quite right. Stalker. Two stalkers immediately. Grammatically it works. It's vivid.
(1:33:17) No collision. But here's the honest problem. Uh, [sighs] asking devs. Oh god, it's given me such a serious answer. I'm going to have to go back. Um, I think probably tap. Actually, I'm No, no. I'm just going to say listener. Listener is fine for now. We can fix this later. Like it's We just need to get to good enough here, right? We don't want to just like bike shed about this bloody language all day.
(1:34:06) Yeah, I undid it by um pressing escape twice and went um went back to an earlier turn. I mean, I enjoy my usual coding sessions, too. Um, what's different is that I usually run two of these at the same time, so I just try to burn myself out properly. Yeah, here we go. Number four is the server side binary.
(1:34:42) You called it the binary in your last message. Um, proposed candidates. The server, the back end, the hub, the collector, the collector's pretty good. I like that. Um, I mean, the server, you know, that's it. It's the slotwatch server, the wire. [sighs] Let's get on with the implementation.
(1:35:04) We are so far away from implementation. Believe me, we are so far away. Uh, we need to figure out where we're going first. So, slopwatch. Yeah, I think the server. I think server's great. Observer, the sensor, the wiretapper. Server is great. I'm using Opus. Opus 4.7. Mhm. Mhm. Mhm. Great. Um, I think that is good for now.
(1:35:46) So, we got the coding a. So, let's let's try this out. We're now talking about this imaginary system that we've not created yet. Um, let me try to explain it to you using this language. So, Slopwatch is a self-hosted um on premises observability platform for coding agents. That's good. You take your coding agent and the user runs a listener next to the coding agent.
(1:36:16) That listener reports um information about sessions to the server and the server is a self-hosted process that receives events from the listeners, stores them in Postgress and serves a dashboard and host the admin plane one per organization. That's what we're building. So those are the relationships.
(1:36:38) Uh, I like these example dialogues as well. This session cost $14. Where did it go? Most of it was is on one turn where the agent did 22 tool calls. Each was a model request charged separately. The rest is a sub agent I spawn with a task tool. It's a child session with its own cost. Cool. I love that.
(1:36:54) So, that's feeling pretty good. We've now got a shape here. We've got a local binary and we've got a Hey, Kieran. Um, we've got a backend server. Mhm. Mhm. Um, did we? Yeah, we did some V1 architectural decisions. Okay. Okay. I want to wind up this session because we're nearly heading to the dumb zone. I want you to take a look at the research in V1 architectural decisions and check if there's anything that we need to add from uh this conversation.
(1:37:36) I mean, we are we're getting close to building. We're getting close to something that we can build here. We've got the language is starting to shape up. We're understanding all of the different deployable units. Um the theory, Valera, is that you would um install a plugin. I suppose we need to add that to the docs as well, that would run the listener for you on in a hook.
(1:38:10) Yeah, that's the theory. So, there a couple of absolutely beasty grilling sessions here. And this is very like that's very reminiscent of the way I code. Any advice for graduating computer science students? Um, I don't think so. I never graduated computer science, so you're doing better than I did. I graduated drama degree and a masters in voice and singing.
(1:38:44) Okay, cool. That's looking good. So, let's commit this. Again, I don't read the research files. It's just waste of time. Um, but I do like to read the context.md file. Now, we're getting somewhere. We're getting towards something real. Um, and we're also getting towards um the end of my time. So, thank you for helping me choose a project. This is a really cool idea.
(1:39:12) I think it's got a I mean, it's got a great name. We've got in a basic architecture and we've grilled our way towards something that feels pretty good. All we've done here is we've basically created a two research documents sort of one looking at how different coding agents work in terms of ingestion and the second looking at um sort of creating some architectural decisions and understanding the basic architecture.
(1:39:43) The main one is that we've hammered out some language here and we're now this is kind of like a um domain modeling session really that we've done. Uh I think what I'll do is I'll probably post a recap on this um recapping what we've created and then going from there. I don't want you know Hey Raphael, nice to see you.
(1:40:06) Uh I don't want to We really are just wrapping up. Raphael, sorry. >> [laughter] >> Um, yeah, I uh I want to mostly do this on videos. I don't know how long this project will take. Um, all I want is a project that I can work on that um is something I can make content out of essentially. So, I mean, I've got a few minutes left.
(1:40:43) Has anyone got any questions about my general process in terms of what I've been doing recently and anything like that? I'll probably finish on the hour. So, we've got about seven minutes left. It's only just hit your feed watching Silicon Valley for the 12th time. I've never seen Silicon Valley.
(1:40:57) Never seen it. I need to watch it. I know I do. Everyone tells me I need to watch it. 85k tokens is 9% the daily limit. No, that's um the amount uh I have left in the context or sorry, the amount um the amount of context I've used up. I'm on 1 million hoopus. Did I just use claw to create these empty files? Yeah, we've you go back in the stream.
(1:41:23) We've just been basically grilling um only grilling for the last two hours really or however long I've been on hour 43 which is very you know that's what I do when I code. So, um, these research files are basically just compacted versions of the conversations that I've had. Anyone know how to turn on auto or bypassing claw code desktop? I don't know.
(1:41:48) Since you're using speech to text, I'm surprised you don't clean up the prompts much to reduce token usage. Is it not really worth it? Absolutely not worth it. No, people are way too anal about um about token usage in my opinion, especially input token usage. Input tokens are incredibly cheap, extraordinarily cheap.
(1:42:05) Output tokens are more expensive. I'm using Whisper Flow to dictate. How did 250 people know about the stream? Um, I post it on Twitter, I think. When you show the Sencastle run when we got something to build. We got nothing to build yet. Thank you. Thank you, Rafael. I'm glad you're enjoying using my workflow.
(1:42:33) I appreciate it. What tools am I using to avoid the agents from not listening? Committing with no verify despite me telling it 10 times not to. Um, I don't tend to get those issues. Um, you might need to be more specific. Uh, your focus on terminology is a step I often skip, but you've made me reconsider that it's important to streamline communication.
(1:42:58) It's not only that. It's sort of bringing the language is how you bring a program into life. I now feel like most of this is on rails because we've figured out exactly what we're building and we've given them each term names. Obviously, you can bike shed names to death and we've done a fair bit of that on this stream.
(1:43:15) Um, I probably should have cut some of it short and got a bit more efficient with it and but yeah, but we've landed on something that works, right? Use copilot so you don't have to worry about tokens. Not yet. Can you elaborate on token usage and how to maximize it? How do you mean what? Like use more tokens and just run a load of stuff in parallel.
(1:43:44) Is open code go models able to produce decent code? Not sure. Not checked. How do I make Claude more submissive? Um, I don't know, man. It seems uh a bit of fetish going on there. Maybe when's the next stream? Um, I think probably I will probably not stream the next one. I think I'll probably make it into a proper video because that's what people like.
(1:44:10) Videos tend to do better than streams. It's nice to chat to you guys and nice to sort of, you know, I wouldn't wouldn't have got the name SloWatch if I wasn't on stream. So, thank you for that. How much should you be willing to spend on AI? I mean, it's totally up to you. Oh, sorry. Um, let me go back to gamify element to it with leaderboard of the devs. Totally.
(1:44:38) Totally. We got to figure out the architecture first, but yeah, like having some kind of metrics or maybe the ability to calculate your own metrics. That would be fun. We've got to decide between Rust and TypeScript for the binary too because it could be a genuine Rust binary. Obviously need some kind of front end which would need to be built in, you know, JavaScript, but I've got experience there. Mhm.
(1:45:04) Go on, hit me. We got a few minutes left. Let me uh check Twitter. Eddie Eddie came up with the idea. Slotwatch. Genius idea. So, Chrome me skill is legit. That's right. All right, friends. Let's call it there. I don't know Rust. No. So, I would need to um I'm interested in building something that like I don't really know how it works.
(1:45:35) Like that's that seems fun to me because it's that is a problem that people will have. They'll need to contribute to repos where they don't know the language. Um, I've never written Rust before. I'm really intrigued by it. Uh, and I like the idea. I've wanted to try a Rust project for a while.
(1:45:55) It would be fun, I think. Um, spelt versus React. I use React. You can use Spelt. It doesn't matter too much. Both are extremely mature projects. One more question, then I'll go. Sloatch. What? Good idea. I'm going out for um for Turkish dinner tonight. Swiftom. I've heard Swift is nice, but rustlings. Thanks, Rafael.
(1:46:43) Yeah, it should be fun. Going out with some friends and their kids. Will I demo the new domain model skill? Um, yeah, I can do. I'll do it another video. Have I used PI agent? Um, not yet, but I'm I desperately want to. I keep mean like every morning I wake up and I think maybe today is the last day I'm going to use claw code and um it never is.
(1:47:08) [laughter] I just haven't, you know, I've just got a bit of inertia. I need to move off it. Is this engineering now? Yeah, I think so. Think so. Um, just a ton of grilling, a ton of, um, figuring out what you're trying to build, a ton of alignment, getting all the pieces in a row. And once you've got it in a row, um, you just let it rip.





# Live: Build a Brand-New Project from Scratch — Structured Notes

## 1. Context and Goals

- Rare live stream before Matt figures out his next course on Monday.
- He has been reading about **DDD (Domain-Driven Design)** and wants to retool his skills.
- Wants to create more **long-form “watch me work” content**.
- Needs a project that can act as a playground for that content.
- Project constraints:
  - Useful in his everyday work.
  - Has frontend and backend pieces.
  - Has a decent amount of complexity.
  - Useful to viewers.
  - Ideally AI-coding related.
- Chat suggests many ideas:
  - Coding agent observability platform.
  - Nx / e-commerce.
  - Live stream chat manager.
  - Simplified OpenClaw.
  - Codebase skills/rules adherence observability.
  - Greenfield coding agent skills prompt eval system.
  - AI coding Kanban board.
  - VS Code alternative.
  - Form wizard, bookmarks manager, Obsidian vault integration.
- Matt settles on a **coding agent observability platform**.
  - Needs a central place to gather data for an organization.
  - Should have pluggable storage.
  - Should support self-hosting / on-prem.
- Poll: 78% vote “Yes” for building a coding agent observability platform.

---

## 2. Initial Idea Validation with Grill Me

- Matt runs Claude in his home directory and invokes the **Grill Me** skill.
- Idea:
  - Personal observability platform for coding agents.
  - Upload sessions somewhere shared.
  - Metrics, analysis, human feedback, session ratings.
  - Per-user data so organizations can see what is going on.
- Stack: TypeScript, but shape is unknown.

### Key Grill Me Questions and Decisions

- **Primary user?**
  - Individual developer?
  - Engineering manager / team lead?
  - Platform DevX at a company?
- Different users imply different UX:
  - A: Personal timeline with deep dive into one session.
  - B: Cohort dashboards/comparisons → surveillance anxiety.
  - C: Aggregate metrics, ignores individuals.
- Matt chooses **A + C as natural rollup**.
  - Manager should be able to open and review a specific engineer’s session.
  - Team needs a **DRRI**-like role responsible for making AI better on that team.
  - Should be able to debug a session with the engineer.
  - Potential for **live spectate** of a session.

### Consent and Visibility

- Coding sessions often contain secrets, half-formed thoughts, PII.
- Options:
  - Always-on mandated, like corporate endpoint monitoring → simple but hostile.
  - Per-session opt-in → kills data quality.
- Matt’s position:
  - Sessions are effectively **public within the organization**.
  - Developers should tacitly understand this when plugged into the system.
  - The data is incredibly valuable to companies.
  - Must support **on-prem / self-hosted** so data never leaves the org.
  - Wants an **open-source tool**, not a massive company.

### Ingestion Mechanism

- Initial question: hooks vs. watching JSONL transcripts?
- Hooks:
  - Claude Code hooks: post-tool-use, stop, session-end.
- JSONL:
  - Transcripts on disk.
  - Local daemon watches directory, uploads deltas.
  - Works with Cursor, Codex, Aider.
  - No hook config required, survives agent restarts.
- Matt asks Claude to research top coding agents:
  - Claude Code
  - Codex
  - Pi
  - OpenCode
  - GitHub Copilot CLI
- Research via subagents.
- Findings:
  - All have some hook surface.
  - Schemas differ and evolve.
  - No single “just use OpenTelemetry” answer.
  - Copilot and Pi have no useful OTel at CLI level.
  - Proxy path blocked for Copilot.
  - **Per-agent adapter is unavoidable.**
  - Each adapter uses that agent’s best surface:
    - Hooks for live events.
    - JSONL as backstop.
    - Normalize into internal event schema.
  - One local daemon loads the right adapter.
- Further nuance:
  - Hooks alone insufficient for most agents.
  - Claude Code hook payloads don’t include message content → still need JSONL.
  - Copilot hook payloads are thin.
  - Codex hooks are flag-gated and Windows excluded.
  - JSONL alone is efficient and sufficient for some.
  - Therefore approach must change per agent.

---

## 3. Repo, Naming, and Research Document

- Matt wants to save research before context gets too large.
- Naming debate:
  - Agent Scope, Peak, Agent Watchtower, Telescope, Agent Guard, Peeping Tommy, Panopticon, Sauron, Palantir, Vantage, Token Scope, Tally, Yardstick, Ledger, Rubric, Quant, Readout, Argos, Agent Reef.
  - Chat suggests **Slopwatch**.
  - Matt loves it. Slopwatch wins.
- Repo created at: `repos/ai/slopwatch`.
- Research doc created: `research/coding-agent-ingestion`.
- Matt treats greenfield projects as **research tasks** until code/PRD.
- He generally does **not read research documents** closely.
  - Trusts summaries.
  - Reads `context.md` more carefully.
- Repo initialized as Git repo and pushed to GitHub.

---

## 4. Domain Modeling and Ubiquitous Language

- Matt starts a new grilling session called **Domain Model**.
  - Described as a new version of Grill Me.
  - Focused on DDD / ubiquitous language.
- Goal: firm up language before architecture and code.
- Stack is probably TypeScript, but shape is open.
- Requirements:
  - Pluggable, self-hosted.
  - Frontend needed.
  - CLI or desktop app.
  - Local persistent API / port to capture data.
  - Users own their data and storage.
  - Not interested in centralized service unless DX is excellent.

### Capture Component: Daemon vs. Per-Session Process

- Research showed hooks alone are not enough.
- Hooks are useful because they delegate process running to the downstream agent.
  - Agent can ping network requests.
  - No separate always-on process needed.
- But pure hook + curl + backend exit isn’t enough.
  - Hooks don’t carry full message content.
  - Live spectate requires per-session capture.
- Refined model:
  - **Hook is the trigger that starts a process.**
  - No pre-existing always-on daemon.
  - Session start hook fires `slopwatch capture`.
  - Capture process lives only for one session.
  - Demonless from user perspective.
  - User configures hooks/extensions once.
  - Two concurrent sessions = two cheap independent subprocesses.
- Term used: **sidecar process**.
  - Short-lived `slopwatch` process spawned by hook.

### Identity and Authentication

- How does a session attach to a developer identity?
- Options:
  - Git config → zero setup, trivially spoofable, doesn’t match org identity.
  - Explicit login during `npx slopwatch install`.
  - OAuth device flow against org IDP.
  - Long-lived refresh token stored in OS keychain.
  - Backend becomes OIDC.
- Matt doesn’t know OIDC/IDP.
  - Uses **Zoom Out** skill to get simpler explanation.
  - IDP = Identity Provider.
  - OIDC = OpenID Connect, built on OAuth 2.0.
  - CLI login device flow: CLI gets short code, user goes to browser, enters code, CLI polls until complete.
- Matt wants a simpler v1:
  - **Per-user admin token.**
  - Admin runs self-hosted backend.
  - Admin page: add user, name, email.
  - Gets one-time token string.
  - Hands token to dev over Slack or similar.
  - Dev runs `slopwatch login` and pastes token.
  - Sidecar stores token and sends it as bearer token.
  - Identity is trustworthy; token bound to user record.
  - Deprovisioning = admin revokes token.
  - One admin CRUD screen.
  - Upgrade path to OIDC later is clean.

### Deployment Shape

- Options:
  - One binary with everything embedded.
  - Docker Compose bundle.
  - Kubernetes-shaped services.
- Matt prefers:
  - **Postgres** over SQLite.
  - No Kubernetes.
  - Hybrid: single binary by default + Postgres.
  - Database should outlive app changes.
  - DB should be a different deployable unit.
- Bun can make TypeScript executables.
- Possible Rust backend.
  - Matt has never written Rust.
  - Interested because it would be fun and realistic for contributors who don’t know the language.
- Live spectate:
  - Sidecar posts events to backend.
  - Manager browser tab watches session.
  - Something must fan out events.
  - Matt wants simpler: **polling every ~5 seconds** or on tab focus.
  - Doesn’t need true real-time for v1.
- DRRI review inbox and session lifecycle still unresolved.

### Ubiquitous Language / Glossary

- **Coding agent** — the agent being observed.
- **Session** — one logical run of a coding agent from launch to exit, attached to one developer, one current working directory, one agent version.
  - Maps directly to a `sessions` table.
- Edge cases:
  - Resumes.
  - Forks/branches.
  - Subagents.
  - Agent version.
- DDD approach: use concrete scenarios to road-test language.

#### Scenario A — Alice branches in Pi

- Alice refactors a module in Pi.
- After 10 turns, she reaches a decision point.
- Branches: tries middleware for 8 turns, doesn’t like it.
- Branches back to decision point.
- Tries in-place refactor for 12 turns, ships it.
- Middleware branch abandoned.
- Questions:
  - Is that three sessions or one session with a DAG?
  - Middleware branch cost real tokens and produced real artifacts.
  - Does DRRI inbox show all three?
  - Does Alice’s session count for the week show +3 or +1?

#### Scenario B — Bob rewinds in Pi

- Bob is 40 turns in.
- Rewinds two turns to rephrase a prompt.
- Pi treats this as a branch.
- Old two turns still exist.

#### Scenario C — Carol live spectates Dave

- Dave branches.
- Carol’s tab is polling.
- Which session ID is she watching?

### Resolution: Session as DAG of Turns

- **Session** is logical.
- One row contains a **DAG of turns**.
- **Turn** is a node in that DAG.
- Turn has a `parent_turn_id`.
- Most agents produce a degenerate DAG — a straight line.
- Pi may produce real branches.
- **Turn** = one user message + full assistant response.
- **Model request** = one HTTP call the agent makes to the model provider during a turn.
  - API call is not a turn.
- **Subagent** = child session with parent session ID.
- Compaction/resume unresolved:
  - Need real data before deciding.
  - Resume stays open until real data is available.

### Context.md / Glossary Terms

- Coding agent.
- Session: one logical run of any coding agent.
- Turn: one user message + full assistant response.
- Model request: one HTTP call to model provider during a turn.
- Listener / capture / sidecar:
  - The on-machine capture component.
  - Naming debated: sidecar, capture, capturer, listener, watcher, collector, tap.
  - Matt chooses **listener** for now, can fix later.
  - Runs next to coding agent, captures data, sends to server.
- Server / backend:
  - Self-hosted process.
  - Receives events from listeners.
  - Stores in Postgres.
  - Serves dashboard.
  - Hosts admin plane.
  - One per organization.

### Example Dialogue from Domain Modeling

- “This session cost $14. Where did it go?”
- “Most of it was on one turn where the agent did 22 tool calls.”
- “Each was a model request charged separately.”
- “The rest is a subagent I spawned with a task tool. It’s a child session with its own cost.”

### Final Project Definition from Stream

> Slopwatch is a self-hosted, on-prem observability platform for coding agents.
> The user runs a **listener** next to the coding agent.
> The listener reports information about **sessions** to the **server**.
> The server is a self-hosted process that receives events from listeners, stores them in Postgres, serves a dashboard, and hosts the admin plane — one per organization.
> Install a plugin that runs the listener in a hook.

---

## 5. Process Observations and Principles

- Grilling sessions can last a long time — 40, 80, 100, even 200 questions.
- Constant decision-making is exhausting.
- Matt often runs two grilling sessions at once when working solo.
- You can only make meaningful decisions when working with an actual asset.
- Working purely in the abstract has limits.
- Don’t over-review plans or research documents.
  - The goal is to get to code.
- Language calcifies during grilling.
  - Capture terms as they emerge.
- DDD and ubiquitous language are a strong match for AI coding.
- Frontend/backend split is artificial.
  - The domain/problem space is the entire thing.
  - Don’t do separate grilling sessions for frontend and backend.
- Edge cases are largely impossible to catch in planning.
  - Build in QA.
- Token usage:
  - Input tokens are cheap.
  - Output tokens are more expensive.
  - Don’t be overly anal about input token usage.
  - 100k still feels like the smart zone.
- Complex apps are hard to change; simple apps are easy to change.
  - `improve-codebase-architecture` skill explores codebase, surfaces architectural friction, proposes module-deepening refactors as GitHub issues.
- Sandcastle will be used later for AFK implementation.
- TypeScript is the recommended stack.
- React is fine; Svelte also fine. Matt uses React.

---

## 6. Tools, Stack, and Setup

### Tools Used / Mentioned

- Claude Code.
- Opus 4.7, effort levels: medium, high, xhigh.
- Whisper Flow for dictation.
- Skills:
  - Grill Me.
  - Zoom Out.
  - Domain Model.
  - Improve Codebase Architecture.
- Sandcastle — coding agent orchestrator, sandbox, AFK loops.
- GitHub for repo hosting.

### Likely Stack

- TypeScript.
- React frontend.
- Possibly Rust backend/binary.
- Bun for TypeScript executables.
- Postgres.
- Hybrid single binary + external Postgres.

### Repo Structure So Far

- `repos/ai/slopwatch`
- Research docs:
  - `coding-agent-ingestion`
  - V1 architectural decisions
- `context.md` / glossary for ubiquitous language.

### Next Steps

- Set up repo properly.
- Decide Rust vs TypeScript for binary.
- Build initial version.
- Use Sandcastle for AFK implementation.
- Add automated review.
- QA and iterate.

---

## 7. Q&A / Side Notes

- **Third-party libraries:** create a skill/documentation for the library, pull it in during review.
- **Claude opinion:** complicated; Matt taught a course on it.
- **OpenClaw:** never used it.
- **Long-term agent memory:** bad idea.
  - Want something observable, concrete, editable, fits context.
  - Experimenting with ADRs + minimal DDD.
- **Over-reviewing plans:** common mistake. Get to code.
- **UI/frontend as differentiator:** not a pundit.
- **Scalability to a million users:** hard problem; help AI.
- **Anthropomorphizing LLMs:** people over-characterize them.
  - No representative sample.
- **4.7 xhigh:** burns tokens approx. 4.6 high.
  - 4.7 feels like a junior with dangerous technical knowledge.
  - Guesses at fixes until build succeeds, assumes correctness.
- **Speech-to-text prompt cleanup:** not worth it; input tokens cheap.
- **Agents not listening:** be more specific; may need skills.
- **Terminology focus:** important.
  - Language brings program to life.
  - Once terms are named, much is on rails.
- **Rust:** Matt doesn’t know it but is interested.
  - Could be fun and realistic.
- **Next stream:** probably not; will make proper video instead.
- **Next call for real engineers:** Monday, probably midday.
- **Slopwatch name:** credited to Eddie.
- **Domain name danger:** someone could grab `slopwatch` domain/package name.
- **Migrations:** different from PRDs; deterministic record, probably keep.
- **Input vs output tokens:** input cheap; output more expensive.
- **Model requests vs turns:** important distinction.
- **Subagents:** child sessions with parent session ID.

---

## 8. Summary / Key Takeaways

- The stream went from **idea → Grill Me → research → domain modeling → architecture decisions → repo setup**.
- Project chosen: **Slopwatch** — a self-hosted, on-prem coding agent observability platform.
- Core architecture:
  - **Listener** runs next to coding agent, spawned by hook.
  - **Server** receives events, stores in Postgres, serves dashboard, hosts admin plane.
  - One server per organization.
  - V1 auth: admin-issued per-user tokens.
  - Live spectate via polling, not true real-time.
- Core domain language:
  - Session = logical run.
  - Session contains DAG of turns.
  - Turn = user message + full assistant response.
  - Model request = one HTTP call to model provider.
  - Subagent = child session with parent session ID.
- Process principles:
  - DDD / ubiquitous language is central.
  - Grill relentlessly to align.
  - Don’t over-review plans/research.
  - Get to code and QA.
  - Keep architecture testable and modular.
  - Use Sandcastle for AFK implementation later.
- Next: set up repo, decide Rust vs TypeScript, build, and use the workflow.
