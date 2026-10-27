files = [
    r"C:\Users\Mateusz\Desktop\PROJECTS\agentic-research-lab\INBOX\New Markdown File.md",
    r"C:\Users\Mateusz\Desktop\ROOT\INBOX\issues.md"
]
for fp in files:
    print("=== " + fp + " ===")
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            print(f.read())
    else:
        print("NOT FOUND")
