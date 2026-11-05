---
type: Concept
id: 10_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 11/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William W Cohen, Ruslan Salakhutdi-
nov, and Christopher D Manning. HotpotQA: A dataset for diverse, explainable multi-hop
question answering.arXiv preprint arXiv:1809.09600, 2018.
Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and
Yuan Cao. ReAct: Synergizing reasoning and acting in language models.arXiv preprint
arXiv:2210.03629, 2022.
Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L Griffiths, Yuan Cao, and
Karthik Narasimhan. Tree of thoughts: Deliberate problem solving with large language
models.Advances in Neural Information Processing Systems, 2023.
Andy Zou, Long Phan, Sarah Chen, James Campbell, Phillip Guo, Richard Ren, Alexander
Pan, Xuwang Yin, Mantas Mazeika, Ann-Kathrin Dombrowski, et al. Representation
engineering: A top-down approach to AI transparency.arXiv preprint arXiv:2310.01405,
2023.
A Implementation Details
Models, decoding, infrastructure.Llama-3.1-70B-Instruct (Grattafiori et al., 2024), Llama-
3.1-8B-Instruct, and DeepSeek-R1-Distill-Llama-70B (DeepSeek-AI, 2025) served on 8×H200
GPUs with pipeline parallelism. Decoding settings differ by experiment. The paired-
trajectory experiments (Sections 4 to 7, n=80 ALFWorld and n=30 HotpotQA) and the
early-warning analysis use temperature 0.7, top- p 0.9, max-new-tokens 512, single run
per task. The cross-model behavioral sweep (§7) uses nruns=3 at T=0.7 for reasoning
models and nruns=1 at T=0 for non-reasoning baselines. Deterministic decoding on non-
reasoning baselines keeps variance out of the headline non-reasoning number; reasoning
models are non-deterministic by default so we average over runs instead. The two set-
tings are deliberate, and the non-reasoning Phase 1 condition is the only one with T=0.
We use the ReAct (Yao et al., 2022) two-shot prompt template ( pick_and_place_simple,
pick_heat_then_place_in_recep). Hidden states are extracted at the last-token position;
layer sampling stride 4 for layers 24-56 and stride 8 elsewhere (15 sampled layers for 70B, 9
for 8B).
Compute budget.Wall-clock per experiment on 8 ×H200 (70B-class) unless noted. Paired-
trajectory ALFWorld collection (n=80 tasks ×2 conditions, single-pass replay with hidden-
state caching) takes about 36 H200-hours. HotpotQA cross-domain replay ( n=30 pairs)
takes about 8 H200-hours. R1-Distill-Llama strict-strip recovery ( n=10 pairs ×4 modes:
raw, strict, in-sample, held-out) takes about 22 H200-hours. The Phase 1 cross-model
behavioral sweep (6 conditions ×n= 25 tasks, reasoning nruns=3) takes about 58 H200-hours
total. R1-Distill-Qwen-32B and Qwen3-32B-thinking probe-transfer extensions (2 ×H200
each, n=15-85 paired) take about 14 H200-hours combined. The steering sweep ( n=150
paired observations, α=0.5, nruns=5 pooled) takes about 18 H200-hours. Probe training
and analysis (Ridge or logistic regression on cached hidden states, no GPU) takes about
2 CPU-days. Total reported compute: about 156 H200-hours. Including preliminary and
exploratory runs not in the paper (intervention sweeps that did not enter, extra collection
on archival models, method-development sweeps over layer sampling and calibration), the
full project consumed roughly 3× the reported total, about 450-500 H200-hours on a shared
internal cluster.
Probe training.Logistic regression (binary, boundary, 4-class) with lbfgs solver, C=
1.0, max_iter = 5000, 5-fold stratified cross-validation on L2-normalized features. Ridge
regression with α= 1.0. Operating threshold τ= 0.15 chosen on validation folds to
maximize F1.
Validity controls (full numbers).At L8: real AUROC 1.000, shuffled 0.297 (gap 0.703),
within-step 0.588, step-index R2 0.998. At L32: step-index R2 0.978. Top-10 feature dimen-
sions atL 8 andL 32 are disjoint (IoU=0.0).
11
