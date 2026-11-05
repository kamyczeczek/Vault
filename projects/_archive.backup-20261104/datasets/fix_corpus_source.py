import os, yaml

corpus_dir = 'C:\\Users\\Mateusz\\Desktop\\PROJECTS\\agentic-research-lab\\knowledge\\corpus'
for f in os.listdir(corpus_dir):
    if f.endswith('.md'):
        fp = os.path.join(corpus_dir, f)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        if '---' in content:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1])
                    if not isinstance(meta, dict) or 'source' not in meta:
                        print(f"Fixing {f} (missing source)")
                        # add source field based on id or title
                        title = meta.get('title', f) if isinstance(meta, dict) else f
                        new_meta = f"id: {meta.get('id', f[:-3])}\ntitle: \"{title}\"\nsource: \"{f}\"\ntags: {meta.get('tags', ['research'])}\n"
                        new_content = f"----{new_meta}---{parts[2]}"
                        with open(fp, 'w', encoding='utf-8') as outfile:
                            outfile.write(new_content)
                except Exception as e:
                    print(f"Error parsing {f}: {e}")
