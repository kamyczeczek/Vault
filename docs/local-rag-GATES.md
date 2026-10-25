# Local RAG — GATES (bramki ukończenia przyszłej budowy)

Ledger dla przyszłej sesji budującej. Ścieżki `local_rag/...` są przykładowe — ustala je ticket R8.

- [ ] G0: Właściciel potwierdził destination mapy
  MANUAL: właściciel przeczytał `docs/wayfinder-local-rag-map.md` i powiedział "destination OK, idziemy" (albo skorygował)
  EVIDENCE: pending

- [ ] G1: Korpus książek jest wczytany i policzony
  CHECK: python local_rag/corpus_stats.py
  EXPECT: "książek: N, chunków: M" gdzie N >= 20 i M >= 1000

- [ ] G2: Embeddingi są zbudowane i zapisane
  CHECK: python local_rag/build_index.py --check
  EXPECT: "index ready: M wektorów, model: <nazwa>"

- [ ] G3: Retrieval odpowiada na 10 pytań właściciela (PL) z top-3 trafieniami
  CHECK: python local_rag/eval.py --questions eval/personal_questions.json
  EXPECT: "trafienia@3 >= 7/10"

- [ ] G4: LLM generuje odpowiedź z cytatem
  CHECK: python local_rag/ask.py "Czym jest SEVerA?"
  EXPECT: odpowiedź zawiera cytat z książki (nie tylko streszczenie)

- [ ] G5: System działa offline (bez wywołań sieciowych)
  MANUAL: uruchom z wyłączonym Wi-Fi, zadaj pytanie, sprawdź że działa
  EVIDENCE: pending

- [ ] G6: Dokumentacja uruchomienia istnieje
  CHECK: python -c "import pathlib; assert pathlib.Path('local_rag/README.md').read_text(encoding='utf-8').lower().find('ollama') >= 0"
  EXPECT: exit 0

- [ ] G7: PageIndex zainstalowany i skonfigurowany lokalnie
  CHECK: pip show pageindex && python -c "from pageindex import PageIndexClient; print('ok')"
  EXPECT: exit 0, "ok"

- [ ] G8: PageIndex indeksuje wybrane książki (te, które nadają się do drzewa)
  CHECK: python local_rag/pageindex_index.py --books-dir <sciezka> --check
  EXPECT: "zaindeksowano N dokumentów, drzewo wygenerowane"

- [ ] G9: PageIndex odpowiada na te same pytania co naive RAG
  CHECK: python local_rag/pageindex_eval.py --questions eval/personal_questions.json
  EXPECT: "odpowiedzi: N/N, z cytatem: M/N"

- [ ] G10: Porównanie obu metod wygenerowane
  CHECK: python local_rag/compare.py --naive-results <plik> --pageindex-results <plik>
  EXPECT: "raport porównawczy: <plik>"

- [ ] G11: Właściciel ocenił obie metody na tych samych pytaniach
  MANUAL: właściciel przeczytał raport porównawczy i wskazał preferencję (albo brak)
  EVIDENCE: pending

- [ ] G12: Obie metody działają offline (bez API, tylko lokalny LLM)
  MANUAL: uruchom z wyłączonym Wi-Fi, zadaj pytanie przez każdą metodę
  EVIDENCE: pending
