import os

path = r'C:\Users\Mateusz\Desktop\PROJECTS\agentic-research-lab\INBOX\New Markdown File.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Current start:", content[:200])

if not content.startswith('---'):
    frontmatter = """---
title: "Build Faster by Coding Slower"
source: "Podcast transcript: AI That Works (Dex Horthy & Vaibhav Gupta)"
tags: ["design-first", "rpi", "baml", "testing", "non-deterministic-systems", "workflow"]
---
"""
    content = frontmatter + content
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added frontmatter successfully.")
else:
    print("Frontmatter already present.")
