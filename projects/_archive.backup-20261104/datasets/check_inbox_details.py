import os, time

for root, dirs, files in os.walk(r'C:\Users\Mateusz'):
    if os.path.basename(root).lower() == 'inbox':
        for f in files:
            fp = os.path.join(root, f)
            mtime = os.path.getmtime(fp)
            # check if modified today or recently
            print(f"{fp} | {time.ctime(mtime)} | size: {os.path.getsize(fp)}")
