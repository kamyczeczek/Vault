import os, time
for root, dirs, files in os.walk('C:\\Users\\Mateusz'):
    if 'INBOX' in dirs:
        inbox = os.path.join(root, 'INBOX')
        for f in os.listdir(inbox):
            fp = os.path.join(inbox, f)
            if os.path.isfile(fp):
                mtime = os.path.getmtime(fp)
                print(f"=== {fp} ({time.ctime(mtime)}) ===")
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                        print(file.read())
                except Exception as e:
                    print('Error:', e)
