import os, time
for r, ds, fs in os.walk('C:\\Users\\Mateusz\\Desktop'):
    if 'INBOX' in ds or os.path.basename(r) == 'INBOX':
        inbox_dir = os.path.join(r, 'INBOX') if 'INBOX' in ds else r
        for f in os.listdir(inbox_dir):
            fp = os.path.join(inbox_dir, f)
            print(fp, time.ctime(os.path.getmtime(fp)))
