import pypdf

# Auffarth pages 152-153
r1 = pypdf.PdfReader('INBOX/MACHINE LEARNING FOR TIME-SERIES WITH PYTHON _ forecast, -- Ben Auffarth -- 1st edition, Erscheinungsort nicht ermittelbar, 2021 -- Packt Publishing - -- isbn13 9781801816106 -- 081bbf327c4c2a10732d9a57a1180fe9 -.pdf')
print("=== AUFFARTH: SUNSPOTS ===")
print(r1.pages[151].extract_text()[:1000])
print("---")
print(r1.pages[152].extract_text()[:1000])

# Bartos / McCleary TOC and Validity chapters
r2 = pypdf.PdfReader('INBOX/Design and analysis of time series experiments -- Bartos, Bradley J_; McCleary, Richard; McDowall, David -- Oxford Scholarship Online, 1, 2017 -- isbn13 9780190661557 -- aee1d4ecc4cd84418bdab2ba52391f92 -- Anna’s.pdf')
print("\n=== BARTOS & MCCLEARY: EXPERIMENT DESIGN ===")
print("Chapter 6 / Statistical Validity:")
print(r2.pages[235].extract_text()[:800])
