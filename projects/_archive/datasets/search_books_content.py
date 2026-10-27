import pypdf, zipfile, re

# Check Auffarth for Sunspots / Agent-based / Scenarios
reader = pypdf.PdfReader('INBOX/MACHINE LEARNING FOR TIME-SERIES WITH PYTHON _ forecast, -- Ben Auffarth -- 1st edition, Erscheinungsort nicht ermittelbar, 2021 -- Packt Publishing - -- isbn13 9781801816106 -- 081bbf327c4c2a10732d9a57a1180fe9 -.pdf')
sunspot_pages = []
for idx, page in enumerate(reader.pages):
    txt = page.extract_text() or ""
    if "sunspot" in txt.lower():
        sunspot_pages.append(idx + 1)
print("Auffarth Sunspot mentions pages:", sunspot_pages)

# Check Manu Joseph for Sunspots / Simulation / Scenarios
reader2 = pypdf.PdfReader('INBOX/Modern Time Series Forecasting with Python_ Industry-Ready -- MANU_ TACKES JOSEPH (JEFFREY_) -- EXPERT INSIGHT, 2, 2024 -- Packt Publishing - ebooks -- isbn13 9781835883181 -- 583b01a7b4cff06d74e7668b0dbdc388 -- .pdf')
sunspot_pages2 = []
simulation_pages2 = []
for idx, page in enumerate(reader2.pages):
    txt = page.extract_text() or ""
    if "sunspot" in txt.lower():
        sunspot_pages2.append(idx + 1)
    if "scenario" in txt.lower() or "simulation" in txt.lower():
        simulation_pages2.append(idx + 1)
print("Manu Joseph Sunspot mentions pages:", sunspot_pages2)
print("Manu Joseph Simulation/Scenario pages count:", len(simulation_pages2))
