import os
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.venv' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.md', '.json', '.jsonl')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if 'concentration' in content.lower() or 'citation' in content.lower():
                        print(path)
            except Exception as e:
                pass
