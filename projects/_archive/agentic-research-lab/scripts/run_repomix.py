import argparse
import subprocess
import sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description="Pack project context into single .txt file using repomix")
    parser.add_argument(
        "-o",
        "--output",
        default="project-context.txt",
        help="Output file path (default: project-context.txt)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    output_path = (project_root / args.output).resolve()

    cmd = [
        "npx",
        "repomix",
        "--style",
        "plain",
        "--output",
        str(output_path),
        "--ignore",
        "knowledge/raw/**,**/*.db,**/*.sqlite,**/*.sqlite3,reflection/digests/**,node_modules/**,.git/**",
    ]

    print(f"Running repomix in {project_root}...")
    try:
        res = subprocess.run(cmd, cwd=str(project_root), shell=True, check=True)
        print(f"Generated context file: {output_path}")
        return res.returncode
    except subprocess.CalledProcessError as err:
        print(f"Repomix failed with code {err.returncode}", file=sys.stderr)
        return err.returncode

if __name__ == "__main__":
    sys.exit(main())
