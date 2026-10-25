# tools/ — male narzedzia, jedno zadanie, jeden test

Zasada: jeden plik = jedno zadanie = jeden `--selftest`. Bez projektu,
bez runu, bez bramek. Kompozycja (pipeline) dopiero gdy 2–3 dzialaja.

| Tool | Job | Test |
|---|---|---|
| [precedent_index](precedent_index.md) | index precedents → SQLite | `--selftest` |
| [brief](brief.md) | question → 4-section brief ≤8K | `--selftest` |
| [brief_eval](brief_eval.md) | A/B on 5 historical ADRs | `--selftest` |
| [scar](scar.md) | append/query failure modes | `--selftest` |

Kontrakt miedzy narzedziami (jedyny): `precedent.json`
(`id, kind, title, quote, source_path, date`).
`brief.py` czyta ten JSON — nie wie, ze `precedent_index.py` istnieje.

Nie tworzyc: CLAUDE.md, CONTEXT.md, GATES.md, `.ralph/`, wayfindera,
TRANSFER.md. Gdy narzedzie potrzebuje drugiego pliku → folder
`tools/<name>/` (form 1), ale dopiero gdy boli.
