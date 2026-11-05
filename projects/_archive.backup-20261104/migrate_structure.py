import pathlib
import shutil

root = pathlib.Path('C:/Users/Mateusz/Desktop/PROJECTS/ts-diverse')

# 1. Create root results and plots dirs
results_dir = root / 'results'
plots_dir = root / 'plots'
results_dir.mkdir(exist_ok=True)
plots_dir.mkdir(exist_ok=True)

# 2. Move files from projects/ts-diverse/results to root results
old_results = root / 'projects' / 'ts-diverse' / 'results'
if old_results.exists():
    for f in old_results.glob('*'):
        if f.is_file():
            shutil.copy2(f, results_dir / f.name)
            print(f"Copied {f.name} to {results_dir}")

# 3. Update bench.py
bench_path = root / 'bench.py'
if bench_path.exists():
    content = bench_path.read_text(encoding='utf-8')
    # replace projects/ts-diverse/results with results
    new_content = content.replace('"projects/ts-diverse/results"', '"results"')
    new_content = new_content.replace("'projects/ts-diverse/results'", "'results'")
    if new_content != content:
        bench_path.write_text(new_content, encoding='utf-8')
        print("Updated bench.py")

# 4. Update plot_predictions.py
plot_pred_path = root / 'plot_predictions.py'
if plot_pred_path.exists():
    content = plot_pred_path.read_text(encoding='utf-8')
    new_content = content.replace('output_dir="projects/ts-diverse/plots"', 'output_dir="plots"')
    if new_content != content:
        plot_pred_path.write_text(new_content, encoding='utf-8')
        print("Updated plot_predictions.py")

# 5. Update plot_sunspot.py
plot_sun_path = root / 'plot_sunspot.py'
if plot_sun_path.exists():
    content = plot_sun_path.read_text(encoding='utf-8')
    new_content = content.replace('pathlib.Path("projects/ts-diverse/results")', 'pathlib.Path("results")')
    if new_content != content:
        plot_sun_path.write_text(new_content, encoding='utf-8')
        print("Updated plot_sunspot.py")

# 6. Remove redundant projects directory
projects_dir = root / 'projects'
if projects_dir.exists():
    shutil.rmtree(projects_dir)
    print("Removed redundant projects directory from ts-diverse")

print("Migration complete!")
