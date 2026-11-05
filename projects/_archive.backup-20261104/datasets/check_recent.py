import os, time
now = time.time()
for root, dirs, files in os.walk('C:\\Users\\Mateusz\\Desktop'):
    if 'ARCHIVE' in root or '.git' in root or 'node_modules' in root or '.pytest_cache' in root or '__pycache__' in root:
        continue
    for f in files:
        fp = os.path.join(root, f)
        try:
            mtime = os.path.getmtime(fp)
            if now - mtime < 7200: # last 2 hours
                print(f"{fp} ({time.ctime(mtime)}) - {os.path.getsize(fp)} bytes")
        except Exception:
            pass
