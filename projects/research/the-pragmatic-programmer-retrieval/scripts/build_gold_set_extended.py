"""Build complete 60-question benchmark dataset (eval/gold_set_extended.json).

Phase 2.1 complete dataset:
- 30 hard curated questions (Q1–Q30 from gold_set_hard.json)
- 8 unanswerable questions (OOC rejection / hallucination prevention)
- 7 false-premise questions (premise correction test)
- 15 topic-grounded questions across uncovered topics
Total: 60 questions.
"""
from __future__ import annotations

import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fingerprint import canonical_index_fingerprint

BASE_FILE = "eval/gold_set_hard.json"
OUTPUT_FILE = "eval/gold_set_extended.json"


def build_extended_gold_set(base_path: str = BASE_FILE, output_path: str = OUTPUT_FILE) -> dict:
    with open(base_path, encoding="utf-8") as f:
        hard_data = json.load(f)

    questions = list(hard_data["questions"])

    # 8 Unanswerable questions (out-of-corpus / not in book)
    unanswerable = [
        {
            "id": "u001",
            "header": "Unanswerable (Kubernetes HPA & Ingress)",
            "question": "Jak skonfigurować ingress controller i horizontal pod autoscaler w Kubernetes dla aplikacji mikrousługowej?",
            "reference_answer": "Książka 'The Pragmatic Programmer' nie zawiera informacji na temat konfiguracji Kubernetes, Ingress ani Horizontal Pod Autoscalera (technologie te powstały po pierwotnym wydaniu i nie są tematem książki).",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u002",
            "header": "Unanswerable (React hooks)",
            "question": "Jakie są najlepsze praktyki używania hooków useEffect i useMemo w React 18 do zapobiegania zbędnym re-renderom?",
            "reference_answer": "Książka nie omawia biblioteki React, architektury komponentów UI w React ani hooków takich jak useEffect czy useMemo.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u003",
            "header": "Unanswerable (OAuth 2.0 & JWT)",
            "question": "W jaki sposób zaimplementować bezpieczną autoryzację tokenami JWT z mechanizmem refresh token w protokole OAuth 2.0?",
            "reference_answer": "Książka nie opisuje protokołu OAuth 2.0, struktury tokenów JWT ani mechanizmu refresh tokenów.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u004",
            "header": "Unanswerable (SQLAlchemy & SQL Injection)",
            "question": "Jak zabezpieczyć bazę danych PostgreSQL przed atakami typu SQL Injection przy użyciu parametryzowanych zapytań w SQLAlchemy?",
            "reference_answer": "Książka omawia bezpieczeństwo ogólne (Topic 43: Stay Safe Out There), ale nie zawiera szczegółów technicznych biblioteki SQLAlchemy ani zapytań PostgreSQL.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u005",
            "header": "Unanswerable (Git rebase vs merge)",
            "question": "Jakie są różnice między git merge a git rebase i w jakich sytuacjach interaktywny rebase w Git jest odradzany w zespołach?",
            "reference_answer": "Książka w Topic 19 (Version Control) nakazuje bezwzględne używanie systemów kontroli wersji, ale nie porównuje poleceń git rebase z git merge ani mechaniki interaktywnego rebase.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u006",
            "header": "Unanswerable (Docker multi-stage)",
            "question": "Jak skonfigurować Docker multi-stage build, aby zminimalizować rozmiar obrazu produkcyjnego aplikacji Node.js?",
            "reference_answer": "Książka nie zawiera instrukcji dotyczących kontenerów Docker, plików Dockerfile ani techniki multi-stage build.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u007",
            "header": "Unanswerable (GraphQL & DataLoader)",
            "question": "Jak zaprojektować schemat GraphQL z wykorzystaniem DataLoader, aby rozwiązać problem zapytań N+1 do bazy danych?",
            "reference_answer": "Książka nie omawia technologii GraphQL ani biblioteki DataLoader do batchowania zapytań.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        },
        {
            "id": "u008",
            "header": "Unanswerable (AWS Lambda Serverless)",
            "question": "Jak działają serverless functions w AWS Lambda pod kątem cold startu i limitów pamięci operacyjnej?",
            "reference_answer": "Książka nie porusza zagadnień infrastruktury chmurowej AWS Lambda ani specyfiki problemu cold start w środowiskach serverless.",
            "source_raw": "None (out-of-corpus)",
            "chapter": None,
            "topics": [],
            "type": "unanswerable",
            "difficulty": "unanswerable"
        }
    ]

    # 7 False-premise questions (distinct from q005, q009, q014, q019, q028 in base set)
    false_premise = [
        {
            "id": "fp001",
            "header": "False-Premise (Test Coverage 100%)",
            "question": "Czy według autorów osiągnięcie 100% pokrycia kodu testami jednostkowymi gwarantuje brak ukrytych błędów w systemie produkcyjnym?",
            "reference_answer": "Nie. Autorzy w Topic 41 (Test to Code) wprost stwierdzają, że 100% code coverage to iluzja bezpieczeństwa — metryka ta zlicza jedynie wykonane linie kodu, podczas gdy błędy kryją się w niezbadanych kombinacjach stanów i danych brzegowych.",
            "source_raw": "Rozdział 7, Topic 41 (Test to Code), s. 343-352",
            "chapter": 7,
            "topics": [41],
            "type": "false_premise",
            "difficulty": "false_premise"
        },
        {
            "id": "fp002",
            "header": "False-Premise (Refactoring Sprints)",
            "question": "Czy refaktoryzację według książki należy planować jako osobny, wielotygodniowy sprint techniczny w kalendarzu zespołu raz na kwartał?",
            "reference_answer": "Nie. W Topic 40 (Refactoring) autorzy porównują refaktoryzację do pielęgnacji ogrodu — to nawyk ciągły i codzienny ('refactor early, refactor often'), a nie wielka okresowa akcja.",
            "source_raw": "Rozdział 7, Topic 40 (Refactoring), s. 336-342",
            "chapter": 7,
            "topics": [40],
            "type": "false_premise",
            "difficulty": "false_premise"
        },
        {
            "id": "fp003",
            "header": "False-Premise (Deep Inheritance)",
            "question": "Czy autorzy zalecają stosowanie głębokich hierarchii dziedziczenia klas zamiast kompozycji, aby zmaksymalizować ponowne użycie kodu?",
            "reference_answer": "Nie. W Topic 31 (Inheritance Tax) autorzy przestrzegają przed dziedziczeniem jako groźnym sprzężeniem ('coupling tax') i zalecają alternatywy: interfejsy, delegację ('Has-A trumps Is-A') oraz mixiny.",
            "source_raw": "Rozdział 5, Topic 31 (Inheritance Tax), s. 272-283",
            "chapter": 5,
            "topics": [31],
            "type": "false_premise",
            "difficulty": "false_premise"
        },
        {
            "id": "fp004",
            "header": "False-Premise (Agile Ceremonies)",
            "question": "Czy prawdziwe podejście Agile według autorów polega na bezwzględnym przestrzeganiu ceremonii Scrum, estymacji w story pointach i certyfikacji procesów?",
            "reference_answer": "Nie. W Topic 48 (The Agile Essence) autorzy argumentują, że Agile to krótka pętla sprzężenia zwrotnego (zorientuj się, zrób mały krok, oceń wynik), a formalne metodyki i certyfikacje często wypaczają tę prostą ideę.",
            "source_raw": "Rozdział 8, Topic 48 (The Agile Essence), s. 427-434",
            "chapter": 8,
            "topics": [48],
            "type": "false_premise",
            "difficulty": "false_premise"
        },
        {
            "id": "fp005",
            "header": "False-Premise (Ignoring Lizard Brain)",
            "question": "Czy autorzy radzą ignorować podświadome poczucie oporu przed pisaniem kodu i zmuszać się do natychmiastowego klepania linijek?",
            "reference_answer": "Nie. W Topic 37 (Listen to Your Lizard Brain) autorzy radzą słuchać instynktu — opór przed kodowaniem zazwyczaj oznacza, że podświadomość wykryła ukrytą wadę architektoniczną lub niespójność wymagań.",
            "source_raw": "Rozdział 7, Topic 37 (Listen to Your Lizard Brain), s. 325-330",
            "chapter": 7,
            "topics": [37],
            "type": "false_premise",
            "difficulty": "false_premise"
        },
        {
            "id": "fp006",
            "header": "False-Premise (Exceptions for Flow Control)",
            "question": "Czy autorzy zalecają rzucanie i łapanie wyjątków jako standardowy mechanizm sterowania normalnym przepływem logiki biznesowej?",
            "reference_answer": "Nie. W Topic 24 i 26 autorzy podkreślają, że wyjątki powinny być zarezerwowane wyłącznie dla sytuacji wyjątkowych i nieoczekiwanych błędów, a nie stosowane jako alternatywa dla instrukcji sterujących (if/switch).",
            "source_raw": "Rozdział 4, Topic 24 (Dead Programs Tell No Lies) / Topic 26, s. 220-230",
            "chapter": 4,
            "topics": [24],
            "type": "false_premise",
            "difficulty": "false_premise"
        },
        {
            "id": "fp007",
            "header": "False-Premise (Stone Soup Waiting)",
            "question": "Czy autorzy radzą, aby przed zainicjowaniem jakiejkolwiek innowacji w projekcie zawsze czekać na formalną zgodę kierownictwa i pełny budżet?",
            "reference_answer": "Nie. Metafora 'Stone Soup' (Topic 4) uczy, by być katalizatorem zmian: zamiast prosić o zgodę na wielki projekt, zacznij od małego działającego prototypu i pokaż namacalną wartość, do której inni chętnie dołączą.",
            "source_raw": "Rozdział 1, Topic 4 (Stone Soup and Boiled Frogs), s. 46-49",
            "chapter": 1,
            "topics": [4],
            "type": "false_premise",
            "difficulty": "false_premise"
        }
    ]

    # 15 Topic-grounded questions across uncovered topics
    additional_topics = [
        {
            "id": "q031",
            "header": "Factual (Topic 1: It's Your Life)",
            "question": "Co autorzy mają na myśli pisząc, że masz 'agency' w swojej karierze zawodowej i jak należy reagować na toksyczne środowisko pracy?",
            "reference_answer": "Autorzy podkreślają, że twoja kariera zależy od ciebie. Masz moc decydowania i wprowadzania zmian. Jeśli środowisko jest toksyczne lub firma nie inwestuje w twój rozwój, masz prawo i możliwość zmienić pracę.",
            "source_raw": "Rozdział 1, Topic 1 (It's Your Life), s. 36-37",
            "chapter": 1,
            "topics": [1],
            "type": "factual",
            "difficulty": "łatwa"
        },
        {
            "id": "q032",
            "header": "Procedural (Topic 2: Provide Options)",
            "question": "Jaka jest pragmatyczna zasada reagowania na problem, gdy coś pójdzie nie tak w projekcie: 'Provide options, don't make lame excuses'?",
            "reference_answer": "Zamiast wymówek należy przedstawić opcje rozwiązania problemu. Nie mów 'pies zjadł kod', lecz zbadaj sytuację, powiedz co poszło nie tak i zaproponuj alternatywne drogi wyjścia.",
            "source_raw": "Rozdział 1, Topic 2 (The Cat Ate My Source Code), s. 38-41",
            "chapter": 1,
            "topics": [2],
            "type": "procedural",
            "difficulty": "średnia"
        },
        {
            "id": "q033",
            "header": "Principle (Topic 11: Reversibility)",
            "question": "Dlaczego odwracalność decyzji (Reversibility) jest tak ważna w architekturze oprogramowania i co to oznacza w praktyce?",
            "reference_answer": "Nie ma decyzji wyrytych w kamieniu. Wymagania i środowisko się zmieniają. Architektura musi umożliwiać łatwą zamianę komponentów (np. bazy danych, dostawcy usług) bez przepisywania całego systemu.",
            "source_raw": "Rozdział 2, Topic 11 (Reversibility), s. 104-108",
            "chapter": 2,
            "topics": [11],
            "type": "reasoning",
            "difficulty": "średnia"
        },
        {
            "id": "q034",
            "header": "Design (Topic 14: Domain Languages)",
            "question": "Czym różnią się wewnętrzne DSL od zewnętrznych DSL według autorów i kiedy je stosować?",
            "reference_answer": "Wewnętrzne DSL wykorzystują składnię języka gospodarza (np. Ruby, Elixir, metaprogramowanie). Zewnętrzne DSL mają własny parser i gramatykę. Służą do programowania blisko domeny problemu.",
            "source_raw": "Rozdział 2, Topic 14 (Domain Languages), s. 124-132",
            "chapter": 2,
            "topics": [14],
            "type": "comparison",
            "difficulty": "średnia"
        },
        {
            "id": "q035",
            "header": "Estimation (Topic 15: Estimating)",
            "question": "W jakich jednostkach czasu autorzy zalecają podawać szacunki (estymaty) w zależności od horyzontu czasowego zadania?",
            "reference_answer": "Skala jednostek powinna odzwierciedlać dokładność: 1–15 dni podawaj w dniach; 3–8 tygodni w tygodniach; 8–30 tygodni w miesiącach; powyżej 30 tygodni szacuj ponownie przed podaniem liczby.",
            "source_raw": "Rozdział 2, Topic 15 (Estimating), s. 133-144",
            "chapter": 2,
            "topics": [15],
            "type": "factual",
            "difficulty": "łatwa"
        },
        {
            "id": "q036",
            "header": "Tools (Topic 17: Shell Games)",
            "question": "Dlaczego według autorów każdy pragmatyczny programista powinien biegle posługiwać się powłoką wiersza poleceń (shell)?",
            "reference_answer": "GUI ma ograniczenia i zmusza do pracy w ramach gotowych scenariuszy. Powłoka command line pozwala łączyć narzędzia w potoki, automatyzować powtarzalne zadania i daje pełną kontrolę nad środowiskiem.",
            "source_raw": "Rozdział 3, Topic 17 (Shell Games), s. 152-155",
            "chapter": 3,
            "topics": [17],
            "type": "reasoning",
            "difficulty": "łatwa"
        },
        {
            "id": "q037",
            "header": "Editing (Topic 18: Power Editing)",
            "question": "Co oznacza rada 'Use a Single Editor Well' i dlaczego warto opanować edytor na poziomie odruchów bezwarunkowych?",
            "reference_answer": "Biegłość w jednym zaawansowanym edytorze pozwala przekładać myśli na kod bez zacinania się nad mechaniką edycji. Gdy edytor staje się przedłużeniem dłoni, programista zachowuje flow.",
            "source_raw": "Rozdział 3, Topic 18 (Power Editing), s. 156-160",
            "chapter": 3,
            "topics": [18],
            "type": "factual",
            "difficulty": "łatwa"
        },
        {
            "id": "q038",
            "header": "Tools (Topic 21: Text Manipulation)",
            "question": "Dlaczego autorzy twierdzą, że tekst jest uniwersalnym interfejsem informatyki i dlaczego należy opanować narzędzia manipulacji tekstem?",
            "reference_answer": "Tekst nie ulega przedawnieniu, jest zrozumiały dla człowieka i maszyn oraz stanowi wspólny mianownik łączący narzędzia. Biegłość w obróbce tekstu pozwala automatyzować żmudne czynności.",
            "source_raw": "Rozdział 3, Topic 21 (Text Manipulation), s. 181-184",
            "chapter": 3,
            "topics": [21],
            "type": "reasoning",
            "difficulty": "średnia"
        },
        {
            "id": "q039",
            "header": "Habit (Topic 22: Engineering Daybooks)",
            "question": "Czym jest 'Engineering Daybook' (dziennik inżynierski) i jakie korzyści przynosi jego codzienne prowadzenie?",
            "reference_answer": "To papierowy notatnik, w którym zapisujesz na bieżąco przemyślenia, szkice, pomysły i problemy. Pomaga uwolnić pamięć roboczą, wspiera retrospekcję i nie rozprasza powiadomieniami.",
            "source_raw": "Rozdział 3, Topic 22 (Engineering Daybooks), s. 185-190",
            "chapter": 3,
            "topics": [22],
            "type": "factual",
            "difficulty": "łatwa"
        },
        {
            "id": "q040",
            "header": "Architecture (Topic 32: Configuration)",
            "question": "Gdzie i jak powinny być przechowywane dane konfiguracyjne aplikacji według zaleceń książki?",
            "reference_answer": "Konfiguracja powinna znajdować się poza kodem źródłowym (np. w zmiennych środowiskowych, zewnętrznych serwisach konfiguracyjnych lub plikach konfiguracyjnych), umożliwiając zmianę zachowania bez rekompilacji.",
            "source_raw": "Rozdział 5, Topic 32 (Configuration), s. 284-291",
            "chapter": 5,
            "topics": [32],
            "type": "factual",
            "difficulty": "łatwa"
        },
        {
            "id": "q041",
            "header": "Concurrency (Topic 33: Breaking Temporal Coupling)",
            "question": "Czym jest sprzężenie czasowe (temporal coupling) i jak projektować systemy, które pozwalają na współbieżność zadań?",
            "reference_answer": "Sprzężenie czasowe występuje, gdy kod zakłada sztywny porządek w czasie ('najpierw A, potem natychmiast B'). Należy analizować przepływ pracy (activity diagrams) i oddzielać operacje niezależne, stosując kolejki lub publikację zdarzeń.",
            "source_raw": "Rozdział 6, Topic 33 (Breaking Temporal Coupling), s. 292-298",
            "chapter": 6,
            "topics": [33],
            "type": "reasoning",
            "difficulty": "średnia"
        },
        {
            "id": "q042",
            "header": "Psychology (Topic 37: Lizard Brain)",
            "question": "Co oznacza rada 'Listen to Your Lizard Brain' i jak programista powinien reagować na podświadome poczucie oporu przed pisaniem kodu?",
            "reference_answer": "Instynktowny opór przed kodowaniem często wynika z tego, że podświadomość dostrzegła ukrytą wadę w projekcie. Zamiast zmuszać się do pisania, odejdź od klawiatury, przemyśl problem lub naszkicuj go na papierze.",
            "source_raw": "Rozdział 7, Topic 37 (Listen to Your Lizard Brain), s. 327-333",
            "chapter": 7,
            "topics": [37],
            "type": "reasoning",
            "difficulty": "średnia"
        },
        {
            "id": "q043",
            "header": "Problem Solving (Topic 46: Solving Impossible Puzzles)",
            "question": "Jak autorzy radzą podchodzić do pozornie nierozwiązywalnych problemów programistycznych i algorytmicznych?",
            "reference_answer": "Zidentyfikuj i zakwestionuj pozorne ograniczenia (self-imposed constraints). Często problem wydaje się niemożliwy, bo sami narzuciliśmy sobie nieistniejący warunek brzegowy. Zmień perspektywę lub zdefiniuj problem na nowo.",
            "source_raw": "Rozdział 8, Topic 46 (Solving Impossible Puzzles), s. 418-423",
            "chapter": 8,
            "topics": [46],
            "type": "procedural",
            "difficulty": "średnia"
        },
        {
            "id": "q044",
            "header": "Collaboration (Topic 47: Working Together)",
            "question": "Jakie są zasady efektywnego pair programmingu i dlaczego kodowanie w parze nie oznacza patrzenia koledze przez ramię?",
            "reference_answer": "Pair programming wymaga aktywnego dialogu: jedna osoba pisze kod (kierowca), druga analizuje szerszy kontekst i potencjalne problemy (nawigator). Rolami należy się regularnie zamieniać.",
            "source_raw": "Rozdział 8, Topic 47 (Working Together), s. 424-428",
            "chapter": 8,
            "topics": [47],
            "type": "procedural",
            "difficulty": "średnia"
        },
        {
            "id": "q045",
            "header": "Value (Topic 52: Delight Your Users)",
            "question": "Jaki jest ostateczny cel tworzenia oprogramowania i co oznacza zasada 'Delight Your Users'?",
            "reference_answer": "Celem nie jest tworzenie kodu, lecz rozwiązywanie problemów użytkowników i dostarczanie im wartości przekraczającej ich oczekiwania. Zachwycony użytkownik to miara sukcesu inżyniera.",
            "source_raw": "Rozdział 9, Topic 52 (Delight Your Users), s. 462-464",
            "chapter": 9,
            "topics": [52],
            "type": "factual",
            "difficulty": "łatwa"
        }
    ]

    all_questions = questions + unanswerable + false_premise + additional_topics

    fingerprint = sha256(json.dumps(all_questions, sort_keys=True).encode()).hexdigest()
    book_struct_path = Path(__file__).resolve().parent.parent / "data/book_structure.json"
    index_fingerprint = canonical_index_fingerprint(book_struct_path)

    output = {
        "gold_set_id": "gs_extended_60_v1",
        "book": "The Pragmatic Programmer, 20th Anniversary Edition",
        "questions_count": len(all_questions),
        "fingerprint": f"sha256:{fingerprint}",
        "index_fingerprint": f"sha256:{index_fingerprint}",
        "categories": {
            "hard_curated": len(questions),
            "unanswerable": len(unanswerable),
            "false_premise": len(false_premise),
            "additional_topics": len(additional_topics)
        },
        "questions": all_questions
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wygenerowano rozszerzony gold set: {len(all_questions)} pytań w {output_path}.")
    print(f"Fingerprint: {fingerprint[:16]}...")
    print(f"Rozkład: {output['categories']}")

    return output


if __name__ == "__main__":
    build_extended_gold_set()
