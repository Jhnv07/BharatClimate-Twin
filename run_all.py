"""
run_all.py - Execute all BharatClimate Twin pipeline phases in order.

Usage:
    python run_all.py

Runs:
  1. src/features.py   (Phase 2 - Feature Engineering)
  2. src/train.py      (Phase 3 - Model Training)
  3. src/evaluate.py   (Phase 3 - Evaluation Plots)

Does NOT re-run preprocess.py (Phase 1 already done).
"""

import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
ROOT = Path(__file__).resolve().parent

steps = [
    ("Phase 2 - Feature Engineering", [PYTHON, str(ROOT / "src" / "features.py")]),
    ("Phase 3 - Model Training",      [PYTHON, str(ROOT / "src" / "train.py")]),
    ("Phase 3 - Evaluation Plots",    [PYTHON, str(ROOT / "src" / "evaluate.py")]),
]

for label, cmd in steps:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"\n[ERROR] {label} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    print(f"\n[OK] {label} completed successfully.")

print("\n" + "="*60)
print("  All pipeline phases completed!")
print("  Launch the dashboard with:")
print("  streamlit run app.py")
print("="*60)
