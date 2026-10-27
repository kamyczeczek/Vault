"""Frozen evaluation sets for graphrag baseline.
Source: verbatim from extended_eval.py + canary.json (no edits).
Do NOT modify — these are the reference sets for all future comparisons.
"""

IN_CORPUS_PL = [
    ("Q3", "Jakie sa metody kompresji sesji agentow?", [
        "00_session_compaction_for_ai_agents",
        "00_session_compaction_for_ai_agents_research",
        "01_session_compaction_for_ai_agents",
        "01_session_compaction_for_ai_agents_research"
    ]),
    ("Q14", "Czym jest agentic engineering i jak prowadzi od chaosu do świadomego projektowania?", ["00_agentic_engineering_od_chaosu_do_wiadomego_proje"]),
    ("Q15", "Dlaczego ponowne wymyślanie koła w vibe coding jest problemem?", ["00_00_bend2_vibe_coding_reinventing_wheels"]),
    ("Q16", "Jakie są techniki, żeby wycisnąć 2-3x wydajności z AI w kodowaniu?", ["00_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods"]),
    ("Q17", "Jak działa routowanie narzędzi oparte na grafie z samonaprawą?", ["00_32ecfce36290_graph_based_self_healing_tool_routi"]),
    ("Q18", "Do czego służy message passing w analizie i odpornym projektowaniu systemów samonaprawczych?", ["00_524ade10f990_message_passing_for_analysis_and_re"]),
    ("Q19", "Jak działa rozproszona detekcja zmian o odporności bizantyjskiej?", ["00_32e1be065210_byzantine_fault_tolerant_distribute"]),
    ("Q20", "Czym charakteryzuje się energetycznie oszczędne uczenie federacyjne z kwantyzacją?", ["00_225c8527385d_energy_efficient_quantized_federate"]),
    ("Q21", "Jak wygląda taksonomia błędów agentów i frameworki debugowania?", ["00_agent_error_taxonomy_debugging_web_research"]),
    ("Q22", "Jak realizowana jest niskonarzutowa odporność na błędy dla kwantowej uniwersalności?", ["00_0d780aefeb5f_low_overhead_transversal_fault_tole"]),
    ("Q1", "What is SEVerA and how does it relate to self-evolving agents?", ["00_severa_verified_synthesis_of_self_evolving_agent"]),
    ("Q2", "What trust tiers does this lab use for evidence, and what does tier 3 mean?", ["00_okf_methodology_research"]),
]

IN_CORPUS_EN = [
    ("Q6", "What are the core structures of agent memory hierarchies?", ["00_agent_memory_hierarchies"]),
    ("Q7", "How do agent execution hooks provide deterministic loop interception and guardrails?", ["00_agent_execution_hooks_guardrails"]),
    ("Q8", "What is the isolate build prove ship methodology in software factories?", ["00_00_software_factory_isolate_build_prove_ship"]),
    ("Q9", "How does the engineering workspace function as an adaptive search environment?", ["00_adaptive_search_workspace_architecture"]),
    ("Q10", "What are the key version control paradigms and git discipline patterns for autonomous agents?", ["00_agentic_git_discipline_patterns"]),
    ("Q11", "How is modular graph structured in agentic RAG?", ["00_agentic_rag_modular_graph"]),
    ("Q12", "What is the CRITIC framework for verify-then-correct with external tools?", ["00_07_critic_external_tool_verification"]),
    ("Q13", "How does lesson persistence and eviction work in ExpeL?", ["00_08_lesson_persistence_eviction_requirement"]),
]

OOC_PL = [
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?", []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?", []),
    ("Q23", "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?", []),
    ("Q24", "Jaki jest tradycyjny przepis na domowe pierogi ruskie?", []),
    ("Q25", "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?", []),
]

CANARY = [
    ("CANARY_01", "Jaki jest numer telefonu do dzialu HR firmy XYZ?", []),
    ("CANARY_02", "Kiedy urodzila sie babcia Krystyna z Sierpca?", []),
    ("CANARY_03", "Ile kosztuje bilet miesieczny w komunikacji miejskiej w Atlantis?", []),
    ("CANARY_04", "Jaki jest numer NIP firmy Widmo Sp. z o.o.?", []),
    ("CANARY_05", "Podaj wspolrzedne geograficzne miasta Eldoria.", []),
]
