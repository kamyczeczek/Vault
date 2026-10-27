"""Positive (in-corpus) and negative (out-of-corpus) sets for calibration.

Sources: frozen pilot eval/extended_eval.py and eval/canary.json (verbatim).
"""

POSITIVES_PL = [
    "Jakie sa metody kompresji sesji agentow?",
    "Czym jest agentic engineering i jak prowadzi od chaosu do świadomego projektowania?",
    "Dlaczego ponowne wymyślanie koła w vibe coding jest problemem?",
    "Jakie są techniki, żeby wycisnąć 2-3x wydajności z AI w kodowaniu?",
    "Jak działa routowanie narzędzi oparte na grafie z samonaprawą?",
    "Do czego służy message passing w analizie i odpornym projektowaniu systemów samonaprawczych?",
    "Jak działa rozproszona detekcja zmian o odporności bizantyjskiej?",
    "Czym charakteryzuje się energetycznie oszczędne uczenie federacyjne z kwantyzacją?",
    "Jak wygląda taksonomia błędów agentów i frameworki debugowania?",
    "Jak realizowana jest niskonarzutowa odporność na błędy dla kwantowej uniwersalności?",
    "What is SEVerA and how does it relate to self-evolving agents?",
    "What trust tiers does this lab use for evidence, and what does tier 3 mean?",
]

POSITIVES_EN = [
    "What are the core structures of agent memory hierarchies?",
    "How do agent execution hooks provide deterministic loop interception and guardrails?",
    "What is the isolate build prove ship methodology in software factories?",
    "How does the engineering workspace function as an adaptive search environment?",
    "What are the key version control paradigms and git discipline patterns for autonomous agents?",
    "How is modular graph structured in agentic RAG?",
    "What is the CRITIC framework for verify-then-correct with external tools?",
    "How does lesson persistence and eviction work in ExpeL?",
]

NEGATIVES_CANARY = [
    "Jaki jest numer telefonu do dzialu HR firmy XYZ?",
    "Kiedy urodzila sie babcia Krystyna z Sierpca?",
    "Ile kosztuje bilet miesieczny w komunikacji miejskiej w Atlantis?",
    "Jaki jest numer NIP firmy Widmo Sp. z o.o.?",
    "Podaj wspolrzedne geograficzne miasta Eldoria.",
]

NEGATIVES_OOC_PL = [
    "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?",
    "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?",
    "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?",
    "Jaki jest tradycyjny przepis na domowe pierogi ruskie?",
    "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?",
]
