"""Run verify_report.py tests. Each fixture has expected result."""
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

results = []
for case_dir in sorted(FIXTURES.iterdir()):
    if not case_dir.is_dir():
        continue
    expected_file = case_dir / "expected.txt"
    expected = expected_file.read_text().strip() if expected_file.exists() else "0"

    result = subprocess.run(
        [sys.executable, "scripts/verify_report.py",
         "--report", str(case_dir / "report.md"),
         "--transcript", str(case_dir / "transcript.jsonl")],
        capture_output=True, text=True
    )

    ok = str(result.returncode) == expected
    results.append((case_dir.name, result.returncode, expected, ok, result.stdout))

    print(f"[{'PASS' if ok else 'FAIL'}] {case_dir.name}: exit={result.returncode}, expected={expected}")
    print(result.stdout)
    print("-" * 40)

failed = sum(1 for r in results if not r[3])
print(f"{len(results) - failed}/{len(results)} passed")
sys.exit(0 if failed == 0 else 1)
