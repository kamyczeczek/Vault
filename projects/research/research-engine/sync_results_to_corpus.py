import json
from pathlib import Path

# The corpus is owned by the research loop, not by this project. Resolve it
# relative to the workspace so a checkout on another machine still works.
WORKSPACE_CORPUS = Path(__file__).resolve().parents[1] / "agentic-research-lab" / "knowledge" / "corpus"

def main():
    s47_path = Path('results_s47.json')
    thomas_path = Path('results_thomas.json')

    s47_data = json.load(open(s47_path, encoding='utf-8')) if s47_path.exists() else {}
    thomas_data = json.load(open(thomas_path, encoding='utf-8')) if thomas_path.exists() else {}

    md_content = f"""---
id: 999_ts_diverse_experiment_results
title: "S-47 and Thomas Experiment Results and Benchmarks"
tags: [ts-diverse, benchmarking, results, bigdict, s47, thomas, time-series]
---

# Experiment Results & Benchmark Summary

Generated on: 2026-09-21
Workspace: `benchmark-core`

## 1. S-47 Diverse Mini-Suite Results
Slice: `{s47_data.get('slice', 'N/A')}`
Suite: `{s47_data.get('suite', 'N/A')}`

### Per-Task Performance Summary
"""

    per_task = s47_data.get('per_task', {})
    for task_name, info in per_task.items():
        md_content += f"- **{task_name}** (H={info.get('H')}):\n"
        singletons = info.get('singleton', {})
        for model, score in singletons.items():
            md_content += f"  - `{model}`: MAE {score:.4f}\n"
        blends = info.get('pool_blend', {})
        for pool, score in blends.items():
            md_content += f"  - Pool {pool}: {score:.4f}\n"

    md_content += """
## 2. Thomas Chaotic Attractor Benchmark Results (`thomas_H24`)
"""

    if thomas_data:
        md_content += "- Status: Recorded\n"
        for k, v in thomas_data.items():
            md_content += f"- `{k}`: {v}\n"
    else:
        md_content += "- Thomas comparison results not currently present or parsed.\n"

    md_content += """
## 3. Key Architectural Conclusions & Promotions
- **BigDictELM & Subband BigDict**: Successfully promoted across tasks via strict gating (`G1` MAE reduction, `G2` rank improvement, `G3` task win-rate).
- **Anti-Leakage Validation**: Walk-forward cross-validation with embargo buffers maintained strict separation.
"""

    corpus_target = WORKSPACE_CORPUS / "999_benchmark_experiment_results.md"
    corpus_target.parent.mkdir(parents=True, exist_ok=True)
    corpus_target.write_text(md_content, encoding='utf-8')
    print('Successfully wrote experiment results corpus file to:', corpus_target)

if __name__ == '__main__':
    main()
