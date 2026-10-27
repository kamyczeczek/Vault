import json
import os

def generate_latex_tables():
    print("=== Generating Publication-Grade LaTeX Tables ===")

    # 1. Rigorous Literature Benchmark
    rigorous_path = "results_rigorous_literature.json"
    if os.path.exists(rigorous_path):
        with open(rigorous_path, "r") as f:
            data = json.load(f)

        latex_lines = [
            r"\begin{table*}[t]",
            r"\centering",
            r"\caption{Rigorous Long-Term Time-Series Forecasting (LTSF) Benchmark Comparison ($L=96$). Lower MSE (top) and MAE (bottom) values are better. Bold indicates best performance.}",
            r"\label{tab:rigorous_ltsf}",
            r"\begin{tabular}{lcccccccc}",
            r"\toprule",
            r"& \multicolumn{2}{c}{$H=96$} & \multicolumn{2}{c}{$H=192$} & \multicolumn{2}{c}{$H=336$} & \multicolumn{2}{c}{$H=720$} \\",
            r"Model & MSE & MAE & MSE & MAE & MSE & MAE & MSE & MAE \\",
            r"\midrule"
        ]

        for dname, horizons in data.items():
            latex_lines.append(r"\multicolumn{9}{l}{\textit{Dataset: " + dname + r"}} \\")
            # Collect models across horizons
            models = set()
            for h_key, m_dict in horizons.items():
                for m_name in m_dict.keys():
                    models.add(m_name)

            for m_name in sorted(models):
                row = [m_name]
                for h_key in ["H_96", "H_192", "H_336", "H_720"]:
                    m_data = horizons.get(h_key, {}).get(m_name, {})
                    mse = m_data.get("mse", 0.0)
                    mae = m_data.get("mae", 0.0)
                    row.append(f"{mse:.3f}")
                    row.append(f"{mae:.3f}")
                latex_lines.append(" & ".join(row) + r" \\")
            latex_lines.append(r"\midrule")

        latex_lines.extend([
            r"\bottom.rule",
            r"\end{tabular}",
            r"\end{table*}"
        ])

        table_txt = "\n".join(latex_lines)
        os.makedirs("results", exist_ok=True)
        with open("results/publication_table.tex", "w") as tf:
            tf.write(table_txt)
        print("Successfully generated results/publication_table.tex")
        print(table_txt[:800] + "\n...")

if __name__ == "__main__":
    generate_latex_tables()
