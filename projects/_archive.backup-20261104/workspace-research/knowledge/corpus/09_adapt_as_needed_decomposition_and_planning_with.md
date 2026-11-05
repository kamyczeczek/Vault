---
type: Concept
id: 09_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 10/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Limitations
ADAPT relies on the success heuristic generated
by the executor LLM to determine if the model
is capable of performing a complex task. For
decision-making tasks studied in this work, we
find that LLMs can reliably determine task success
based on past action trajectories and textual feed-
back from the environment (see Appendix F). How-
ever, Huang et al. (2023a); Stechly et al. (2023)
discuss the limits of LLM’s ability to self-evaluate
and self-refine. In such situations, future works
may additionally employ external verifiers (Light-
man et al., 2023; Shridhar et al., 2023), theory-of-
mind strategies among multiple LMs (Saha et al.,
2023a), and other calibration and self-evaluation
techniques (Kadavath et al., 2022). These improved
self-evaluation techniques could be useful to extend
our framework to non-decision making tasks such
as question answering.
References
Michael Ahn, Anthony Brohan, Noah Brown, Yevgen
Chebotar, Omar Cortes, Byron David, Chelsea Finn,
Chuyuan Fu, Keerthana Gopalakrishnan, Karol Haus-
man, et al. 2022. Do as i can, not as i say: Ground-
ing language in robotic affordances. arXiv preprint
arXiv:2204.01691.
Jacob Andreas, Marcus Rohrbach, Trevor Darrell, and
Dan Klein. 2016. Neural module networks. In Pro-
ceedings of the IEEE conference on computer vision
and pattern recognition, pages 39–48.
Andrew G Barto and Sridhar Mahadevan. 2003. Re-
cent advances in hierarchical reinforcement learning.
Discrete event dynamic systems, 13(1-2):41–77.
Valts Blukis, Chris Paxton, Dieter Fox, Animesh Garg,
and Yoav Artzi. 2022. A persistent spatial semantic
representation for high-level natural language instruc-
tion execution. In Conference on Robot Learning ,
pages 706–717. PMLR.
Andy Coenen, Luke Davis, Daphne Ippolito, Emily
Reif, and Ann Yuan. 2021. Wordcraft: a human-ai
collaborative editor for story writing. arXiv preprint
arXiv:2107.07430.
Marc-Alexandre Côté, Akos Kádár, Xingdi Yuan, Ben
Kybartas, Tavian Barnes, Emery Fine, James Moore,
Matthew Hausknecht, Layla El Asri, Mahmoud
Adada, et al. 2019. Textworld: A learning environ-
ment for text-based games. In Computer Games:
7th Workshop, CGW 2018, Held in Conjunction with
the 27th International Conference on Artificial In-
telligence, IJCAI 2018, Stockholm, Sweden, July
13, 2018, Revised Selected Papers 7 , pages 41–75.
Springer.
David Dohan, Winnie Xu, Aitor Lewkowycz, Ja-
cob Austin, David Bieber, Raphael Gontijo Lopes,
Yuhuai Wu, Henryk Michalewski, Rif A Saurous,
Jascha Sohl-Dickstein, et al. 2022. Language model
cascades. arXiv preprint arXiv:2207.10342.
Nouha Dziri, Ximing Lu, Melanie Sclar, Xiang Lorraine
Li, Liwei Jian, Bill Yuchen Lin, Peter West, Chandra
Bhagavatula, Ronan Le Bras, Jena D Hwang, et al.
2023. Faith and fate: Limits of transformers on com-
positionality. arXiv preprint arXiv:2305.18654.
Kutluhan Erol, James Hendler, and Dana S Nau. 1994.
Htn planning: Complexity and expressivity. In AAAI,
volume 94, pages 1123–1128.
Linxi Fan, Guanzhi Wang, Yunfan Jiang, Ajay Man-
dlekar, Yuncong Yang, Haoyi Zhu, Andrew Tang,
De-An Huang, Yuke Zhu, and Anima Anandkumar.
2022. Minedojo: Building open-ended embodied
agents with internet-scale knowledge. Advances in
Neural Information Processing Systems, 35:18343–
18362.
Yao Fu, Hao Peng, Litu Ou, Ashish Sabharwal, and
Tushar Khot. 2023. Specializing smaller language
models towards multi-step reasoning. arXiv preprint
arXiv:2301.12726.
Ilche Georgievski and Marco Aiello. 2014. An overview
of hierarchical task network planning. arXiv preprint
arXiv:1403.7426.
Malik Ghallab, Dana Nau, and Paolo Traverso. 2004.
Automated Planning: theory and practice. Elsevier.
Nitish Gupta, Kevin Lin, Dan Roth, Sameer Singh, and
Matt Gardner. 2019. Neural module networks for
reasoning over text. In International Conference on
Learning Representations.
Daniel Höller, Gregor Behnke, Pascal Bercher, Susanne
Biundo, Humbert Fiorino, Damien Pellier, and Ron
Alford. 2020. Hddl: An extension to pddl for ex-
pressing hierarchical planning problems. In Proceed-
ings of the AAAI conference on artificial intelligence,
pages 9883–9891.
Jie Huang and Kevin Chen-Chuan Chang. 2023. To-
wards reasoning in large language models: A survey.
In Findings of the Association for Computational
Linguistics: ACL 2023, pages 1049–1065, Toronto,
Canada. Association for Computational Linguistics.
Jie Huang, Xinyun Chen, Swaroop Mishra,
Huaixiu Steven Zheng, Adams Wei Yu, Xiny-
ing Song, and Denny Zhou. 2023a. Large language
models cannot self-correct reasoning yet. arXiv
preprint arXiv:2310.01798.
Wenlong Huang, Fei Xia, Ted Xiao, Harris Chan, Jacky
Liang, Pete Florence, Andy Zeng, Jonathan Tomp-
son, Igor Mordatch, Yevgen Chebotar, et al. 2023b.
Inner monologue: Embodied reasoning through plan-
ning with language models. In Conference on Robot
Learning, pages 1769–1782. PMLR.
10
