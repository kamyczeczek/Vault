---
type: Concept
name: retrieval-two-stage
description: Two-stage retrieval over OKF-rag notes: semantic hub first, then source verification with file+line locators.
---

# Retrieval two-stage

1. Stage 1 (hub): run semantic retrieval over `kb/Notes/OKF-rag` to get candidate hubs/slices.
2. Stage 2 (source): for every claim, open the cited source file at the cited lines and verify the passage contains the answer.
3. A hub or slice is never evidence; only a source passage with a valid locator is.
4. Citation format: `sources: [{file, lines}]`.
5. `exact` means the passage lies fully inside the gold range; `related` requires manual verification before citation.
