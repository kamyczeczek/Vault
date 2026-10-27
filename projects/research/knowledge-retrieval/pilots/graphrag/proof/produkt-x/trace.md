---
type: Concept
title: trace
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Ślad wykonania — proof: "Kto zarządza firmą, która stworzyła produkt X?"

Generowane przez `graphrag.py ask "Kto zarządza firmą, która stworzyła produkt X?"`

---

## 1. wektorowe_wyszukiwanie_zapytania(STUB:LIKE:seed_kinds)
**Parametry:**
```json
{
  "query": "Kto zarządza firmą, która stworzyła produkt X?",
  "top_k": 3,
  "seed_kinds": ["Produkt"]
}
```
**Wynik:** 1 seed(s): ['01_produkt_x']

---

## 2. przechodzenie_grafu
**Parametry:**
```json
{
  "seed_ids": ["01_produkt_x"],
  "relacje": ["STWORZYŁ", "ZARZĄDZA"],
  "glebokosc": 2
}
```
**Wynik:** 2 triple(s)

---

## 3. pobierz_encje
**Parametry:**
```json
{ "id": "01_produkt_x" }
```
**Wynik:** OK: Produkt X

---

## 4. polacz_z_baza_wiedzy
**Parametry:**
```json
{ "encje": ["01_produkt_x"] }
```
**Wynik:** resolved 1/1

---

## 5. weryfikuj_twierdzenia
**Parametry:**
```json
{ "n_twierdzen": 1, "n_dowodow": 2 }
```
**Wynik:** passed 1, rejected 0

---

## 6. generuj_odpowiedz
**Parametry:**
```json
{ "pytanie": "Kto zarządza firmą, która stworzyła produkt X?" }
```
**Wynik:** OK: 1 claim(s), confidence=wysoka

---

## Podsumowanie dowodów
| Lp. | Triple |
|-----|--------|
| 1 | (01_produkt_x, STWORZYŁ, 02_firma_y) |
| 2 | (02_firma_y, ZARZĄDZA, 03_jan_kowalski) |

**Łącznie narzędzi wywołanych:** 6
**Trójek udowodnionych:** 2
**Twierdzeń zweryfikowanych:** 1 (0 odrzuconych)