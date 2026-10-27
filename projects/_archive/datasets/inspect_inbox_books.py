import os
import pypdf
import zipfile

inbox_dir = 'INBOX'
for f in os.listdir(inbox_dir):
    p = os.path.join(inbox_dir, f)
    print(f"\n==========================================")
    print(f"FILE: {f}")
    print(f"SIZE: {os.path.getsize(p) / 1024 / 1024:.2f} MB")
    if f.endswith('.pdf'):
        try:
            reader = pypdf.PdfReader(p)
            print(f"Type: PDF, Pages: {len(reader.pages)}")
            # Search for table of contents in first 15 pages
            for i in range(min(15, len(reader.pages))):
                txt = reader.pages[i].extract_text() or ""
                if "contents" in txt.lower() or "table of contents" in txt.lower() or "chapter" in txt.lower():
                    print(f"--- Page {i+1} sample ---")
                    lines = [l.strip() for l in txt.splitlines() if l.strip()]
                    print("\n".join(lines[:15]))
                    break
        except Exception as e:
            print("PDF error:", e)
    elif f.endswith('.epub'):
        try:
            z = zipfile.ZipFile(p)
            print(f"Type: EPUB, Entries: {len(z.namelist())}")
            tocs = [n for n in z.namelist() if 'toc' in n.lower() or 'nav' in n.lower()]
            print("TOC candidates:", tocs)
            if tocs:
                content = z.read(tocs[0]).decode('utf-8', errors='ignore')
                print("TOC sample:")
                import re
                titles = re.findall(r'<text>(.*?)</text>', content) or re.findall(r'>([^<]{4,60})<', content)
                for t in titles[:15]:
                    if t.strip():
                        print("  *", t.strip())
        except Exception as e:
            print("EPUB error:", e)
