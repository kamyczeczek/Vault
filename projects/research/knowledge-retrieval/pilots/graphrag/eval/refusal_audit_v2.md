---
type: Concept
title: refusal_audit_v2
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Refusal Audit v2 (Faza 8d)

## A1 — Podagenty (surowe dane)

### Podagent A — EN out-of-corpus (Q26-Q30)
- **Q26**: What is the latest release date and new features of Python 3.15?
  - matching_ids: `['00_00_software_factory_isolate_build_prove_ship', '00_0d780aefeb5f_low_overhead_transversal_fault_tole', '00_a_bandit_approach_with_evolutionary_operators_fo', '00_a_complete_guide_to_managing_thousands_of_files', '00_a_comprehensive_survey_of_self_evolving_ai_agent', '00_a_methodology_to_engineer_and_validate_dynamic_m', '00_a_tutorial_on_meta_reinforcement_learning', '00_adaptive_search_workspace_architecture', '00_agent_hooks_lifecycle_guardrails', '00_agentic_auto_research_frontier_10_sources']`
  - matching_titles: `['"Research question (part 1/4)"', '"Low-Overhead Transversal Fault Tolerance for Universal Quantum Computation"', '"A Bandit Approach With Evolutionary Operators for Model (part 1/8)"', '"The ICM Folder Structure: A Detailed Guide to Keeping 9,916 Files in One Folder Without Rot (part 1/10)"', '"A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems"', '"A Methodology to Engineer and Validate Dynamic Multi-level Multi-agent Based Simulations"', '"A Tutorial on Meta-Reinforcement Learning"', '"The Engineering Workspace as an Adaptive Search Environment"', '"Agentic Coding Hooks: Lifecycle Interception, Guardrail Semantics, and Loop Remediation"', '"The Agentic Researcher: 10 Frontier Scientific & GitHub Sources on Autonomous Research Discovery (part 1/2)"']`
- **Q27**: What is the current stock price of Tesla?
  - matching_ids: `['00_01_session_graph_research', '00_a_complete_guide_to_managing_thousands_of_files', '00_agent_error_taxonomy_debugging_web_research', '00_artificial_intelligence_a_modern_approach_4th_ed', '00_building_llms_for_production_enhancing_llm_abili', '00_cryptographically_verifiable_authorization_for_a', '00_experience_graph_self_evolving_agents_web_resear', '00_fair_rag_faithful_adaptive_iterative_refinement', '00_firecrawl_token_reduction', '00_grail_learning_to_interact_with_large_knowledge']`
- **Q28**: What is the departure time of flight UA123 from Chicago to London?
  - matching_ids: `['00_00_bend2_vibe_coding_reinventing_wheels', '00_01_session_graph_research', '00_0d780aefeb5f_low_overhead_transversal_fault_tole', '00_32e1be065210_byzantine_fault_tolerant_distribute', '00_32ecfce36290_graph_based_self_healing_tool_routi', '00_a_bandit_approach_with_evolutionary_operators_fo', '00_adaptive_search_workspace_architecture', '00_agent_execution_hooks_guardrails', '00_agent_hooks_lifecycle_guardrails', '00_agentforce_harnessing_the_agency_of_ai_to_scale']`
- **Q29**: Who is the current president of Mars colony?
  - matching_ids: `['00_01_session_graph_research', '00_a_complete_guide_to_managing_thousands_of_files', '00_agent_error_taxonomy_debugging_web_research', '00_artificial_intelligence_a_modern_approach_4th_ed', '00_building_llms_for_production_enhancing_llm_abili', '00_cryptographically_verifiable_authorization_for_a', '00_experience_graph_self_evolving_agents_web_resear', '00_fair_rag_faithful_adaptive_iterative_refinement', '00_grail_learning_to_interact_with_large_knowledge', '00_graph_database_architectural_reflection']`
- **Q30**: What is the latest breakthrough in quantum supremacy?
  - matching_ids: `['00_0d780aefeb5f_low_overhead_transversal_fault_tole', '00_context_in_object_detection_a_systematic_literat', '01_pattern_recognition_and_machine_learning_christo', '01_real_design_patterns_for_agentic_software_factor', '02_building_llms_for_production_enhancing_llm_abili', '02_icm_knowledge_big', '02_llm_engineers_handbook_iusztin_paul_labonne_z_li', '02_theo_s_agents_md_skills_md_breakdown', '02_why_new_ai_models_rarely_change_everything', '03_building_a_practical_ai_assembly_line']`

### Podagent B — PL out-of-corpus (Q4, Q5, Q23, Q24, Q25)
- **Q4**: Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF? -> 9 matching nodes (odmówił poprawnie, bo n_trafien < 2 lub brak cytatów).
- **Q5**: Co powiedzial Jan Kowalski na spotkaniu 2026-09-15? -> 10 matching nodes (odmówił poprawnie).
- **Q23**: Jaka bedzie prognoza pogody w Warszawie jutro o 14:00? -> 0 matching nodes (odmówił poprawnie).
- **Q24**: Jaki jest tradycyjny przepis na domowe pierogi ruskie? -> 10 matching nodes (odmówił poprawnie).
- **Q25**: Jaki padl wynik w ostatnim meczu siatkowki Polska - Brazylia? -> 1 matching node (odmówił poprawnie).

### Podagent C — Canary (Q99, Q98, Q97)
- **Q99**: Jaki jest numer telefonu do dzialu HR firmy XYZ? -> 10 matching nodes (fałszywa koincydencja słów w FTS5).
- **Q98**: Kiedy urodzila sie babcia Krystyna z Sierpca? -> 0 matching nodes.
- **Q97**: Ile kosztuje bilet miesieczny w komunikacji miejskiej w Atlantis? -> 1 matching node.

---

## A2 — Weryfikacja przez diff
`git status`: modified `MAP.md`, untracked directories/files from previous test runs. Podagenty nie zmodyfikowały repozytorium (zero zmian w git diff poza MAP.md z wcześniejszych sesji).

---

## B1 & B2 — Klasyfikacja problemu
- KATEGORIA A (koincydencja słów / problem testu): Q26, Q27, Q28, Q29, Q30, Q99.
- KATEGORIA B (fałszywe pokrycie / problem systemu): Q26, Q27, Q28, Q29, Q30. (`MIN_KEYWORD_MATCHES=2` przepuszcza węzły z koincydencją jako pokryte).
- KATEGORIA C (rzeczywista odpowiedź): pusta.
- A+B jednocześnie: Q26, Q27, Q28, Q29, Q30.
