---
type: report
title: Eksperyment — ręczne i semantyczne wyszukiwanie w OKF-rag
description: Pierwszy pięciopytaniowy test tego, czy warstwa syntezy i Smart Connections pomagają znaleźć właściwy materiał.
status: draft
tags: [experiment, retrieval, smart-connections, okf]
sources:
  - SYNTHESIS.md
  - SYNTHESIS-kompilacja-i-wyszukiwanie.md
  - DECISION-minimalny-przeplyw-wiedzy.md
generated:
  by: codex
  at: 2026-10-25T00:00:00Z
---

# Cel

Sprawdzić, czy po utworzeniu krótkich syntez łatwiej znaleźć odpowiedź na
pytania dotyczące `Notes/OKF-rag` oraz czy wyszukiwanie semantyczne znajduje
lepszy punkt wejścia niż proste wyszukiwanie słów.

# Metoda

- Zakres Smart Connections: `Notes/OKF-rag`.
- Indeks: 436 notatek i 2331 bloków; 0 starych wektorów; model
  `TaylorAI/bge-micro-v2`.
- Wyszukiwanie semantyczne: pięć pytań w języku naturalnym, `top 5`,
  minimalny score `0.55`.
- Wyszukiwanie tekstowe: `rg` na plikach źródłowych, z wyłączeniem nowych
  syntez, decyzji i indeksu. Liczba wyników jest miarą szumu odkrywania, nie
  równoważnym rankingiem.

# Pytania i wyniki

| # | Pytanie | Najlepszy wynik semantyczny | Score | Pliki znalezione tekstowo |
|---|---|---|---:|---:|
| 1 | Jak wygląda przepływ od materiału do decyzji? | `SYNTHESIS.md` | 0.8179 | 12 |
| 2 | Co jest źródłem prawdy i kto publikuje koncepty? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7679 | 9 |
| 3 | Kiedy koncept wymaga review, provenance i kontroli świeżości? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7935 | 12 |
| 4 | Jakie są ograniczenia ekstrakcji i deduplikacji? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7450 | 9 |
| 5 | Kiedy kompilacja wiki i retrieval są przesadą? | `SYNTHESIS-kompilacja-i-wyszukiwanie.md` | 0.7725 | 6 |

# Obserwacje

## 1. Warstwa syntezy działa jak dobry punkt wejścia

Wszystkie pięć pytań dostało jako najlepszy wynik jedną z nowych notatek
kuratorskich. Wyniki mają score od `0.7450` do `0.8179`, czyli przekraczają
skalibrowany próg realnego dopasowania `0.65`.

To nie dowodzi jeszcze, że Smart Connections znajduje najlepsze źródła. Dowodzi,
że krótkie syntezy są semantycznie rozpoznawalnymi hubami dla pytań, które same
stawiają.

## 2. Wyszukiwanie tekstowe znajduje materiał, ale daje szeroki wachlarz

`rg` znalazł od 6 do 12 plików na pytanie. To jest dobre do zebrania korpusu,
ale bez dodatkowego rankingu nie wskazuje jednego najlepszego dokumentu. Wynik
zależy też od dobranych słów kluczowych.

## 3. Benchmark jest jeszcze częściowo kolisty

Nowe syntezy zostały już zindeksowane i zawierają język pytań testowych. Dlatego
semantic top-1 mierzy przede wszystkim jakość warstwy kuratorskiej, a nie czystą
zdolność znalezienia informacji w dużych importach.

Nie wolno na tej podstawie twierdzić, że Smart Connections jest już lepsze od
wyszukiwania tekstowego dla całego vaultu.

# Wniosek

Warto utrzymywać krótkie syntezy i decyzje jako warstwę nawigacyjną nad surowymi
materiałami. To poprawia odnajdywanie głównych wniosków i daje agentowi stabilny
punkt wejścia. Nie ma jeszcze dowodu, że potrzebny jest pełny pipeline OKF-RAG,
embeddingi lub automatyczna kompilacja całego vaultu.

# Decyzja pośrednia

Na razie używamy następującego podziału:

- wyszukiwanie tekstowe do dokładnego znalezienia nazw, fraz i źródeł;
- Smart Connections do znalezienia konceptu lub syntezy opisującej sens pytania;
- notatki `SYNTHESIS` i `DECISION` jako kuratorowana warstwa wejściowa;
- ręczna weryfikacja źródła przed uznaniem odpowiedzi za fakt.

# Następny test

Zbudować drugą wersję benchmarku z 10–20 pytaniami i oczekiwanym plikiem
źródłowym dla każdego pytania. Wyniki liczyć osobno dla:

1. trafienia w syntezę lub decyzję;
2. trafienia w oryginalny materiał;
3. obecności właściwego pliku w top 5.

Dopiero taki test pozwoli zdecydować, czy warto rozdzielić indeks na warstwę
źródłową i kuratorską albo uruchomić cięższy pipeline.
