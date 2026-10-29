---
type: Concept
title: 0001-s49-closeout-and-protocol-discrepancies
status: accepted
date: 2026-10-29
---

# ADR 0001: Zamknięcie linii badawczej S49 ETTh1 H720 oraz audyt rozbieżności metodycznych protokołu

## Kontekst i problem

Linia badawcza S49 (`LONGTERM_ETTH1_H720_DESIGN.md`) została pre-zarejestrowana w celu wyłonienia architektury długoterminowej na horyzoncie 720 h dla zbioru ETTh1 OT, zdolnej pobić historyczny wynik incumbent S-44 (próg G1: raw MAE < 1,9781).

W toku prac zbadano i oceniono trzech kandydatów:
1. `SAB-L` (Signal-Adaptive BigDict Long, L=336): odrzucony po wyczerpaniu 2-iteracyjnego budżetu; mean raw MAE = 4,4611 (przegrana na 12/12 originach).
2. `H2K` (Horizon-Decomposed Drift-Corrected KNN): odrzucony; mean raw MAE = 2,7270 (przegrana z incumbent, niepromowany).
3. `AMR-24/168` (Multi-Scale Envelope + weekly anchor): dokończony, zoptymalizowany na early dev i oceniony na zablokowanym zestawie; mean raw MAE = 3,1480 (std 1,3573). Przegrywa G1 (3,1480 > 1,9781) oraz G2 (DLinear wygrywa na 9/12 originach).

Jednocześnie audyt zgodności protokołu ujawnił istotne rozbieżności metodyczne:
1. **Liczba originów**: Pre-rejestracja w `LONGTERM_ETTH1_H720_DESIGN.md` deklarowała `W=20 locked eval origins` (sliding suite). Rzeczywista ewaluacja zrealizowana w skryptach testowych (`run_h2k_h720_final.py`, `run_amr_h720_final.py`) objęła zestaw **12 originów** (krok co 720 h: od 8640 do 16560).
2. **Liczba seedów**: Pre-rejestracja wymagała oceny na 5 seedach (mean±std) dla modeli z komponentami losowymi. W głównych tabelach wynikowych kandydatów zaraportowano jedynie pojedynczy **seed 42**; 5 seedów wykorzystano wyłącznie w osobnym teście diagnostycznym rankingu G4 dla AMR-24/168 (`results/etth1_h720_amr24168_g4.json`).
3. **Porównywalność progu S44 (1,9781)**: Wynik S-44 pochodzi z 3-modelowego blendu (`NLinear a=1 + a=10 + PatchTST-Delta`) ocenianego na **2161 gęstych originach kroczących** (step=1) na pełnym splicie testowym. W S-44 pojedyncze modele osiągały MAE > 2,89, a na pierwszym oknie W1 sam blend miał MAE 2,1606. W S49 nałożono próg 1,9781 na pojedyncze modele badane na 12 rzadkich originach (step=720). Oceny te nie są bezpośrednio porównywalnymi pomiarami. Nie uprawnia to jednak do niepopartego dowodem wniosku, że pojedynczy model z natury nie mógłby osiągnąć takiego wyniku.
4. **Praktyczna podstawa decyzji**: Na aktualnym zestawie 12 originów BigDictELM L96 osiąga MAE 2,4777, a DLinear 2,5384. Zarówno H2K (2,7270), jak i AMR-24/168 (3,1480) przegrywają ze sprawdzonymi punktami odniesienia, wykazując wysoką wariancję między oknami.

## Decyzja

1. **Zamknięcie linii S49**: Zamykamy linię S49 jako nieudany etap poszukiwania modelu do promocji pod zastosowanym protokołem ewaluacji. Nie przedstawiamy tego jako pełnego, zgodnego z pierwotną pre-rejestracją obalenia wszystkich hipotez, lecz jako rzetelnie udokumentowany brak kandydata spełniającego kryteria awansu.
2. **Status Meta-H**: Opcjonalny czwarty krok (`Meta-H`, selektor per-horizon) **nie zostaje uruchomiony** i zostaje formalnie zamknięty wraz z całą linią S49 po wyczerpaniu 2-iteracyjnego budżetu poszukiwań (kill budget). Przy braku przewagi poszczególnych składowych nad BigDictELM/DLinear budowa selektora nad odrzuconymi modelami nie ma uzasadnienia empirycznego.
3. **Nienaruszalność pre-rejestracji**: Tekst oryginalnej pre-rejestracji w `LONGTERM_ETTH1_H720_DESIGN.md` pozostaje niezmieniony (nie przepisujemy historii wstecz). Ustalenia z wykonania oraz odstępstwa od protokołu zostają utrwalone w datowanym Aneksie Wykonawczym.

## Konsekwencje

- Zapobiega dalszemu strojeniu modeli na zużytym zestawie 12 originów testowych.
- Eliminuje fałszywy obraz stanu badań w repozytorium (AMR-24/168 nie figuruje już jako otwarty kandydat).
- Ewentualne przyszłe badania nad H720 wymagają sformułowania nowej hipotezy, nowych originów deweloperskich oraz zweryfikowania protokołu porównawczego przed uruchomieniem eksperymentu.
