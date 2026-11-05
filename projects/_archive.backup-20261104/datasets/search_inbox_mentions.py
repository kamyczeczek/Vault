import os
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py') or f.endswith('.md'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                    if 'inbox' in file.read().lower():
                        print(fp)
            except Exception:
                pass
