---
type: Concept
id: 134_icm_knowledge_big
title: "ICM_knowledge.md (part 135/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

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
