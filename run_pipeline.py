"""Run the full analysis pipeline from the project root."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from eda import run_eda
from model import run_full_pipeline


def main() -> None:
    print("=== Money vs Happiness ML Pipeline ===\n")
    run_eda()
    print()
    run_full_pipeline()
    print("\nDone. See results/ and results/plots/")


if __name__ == "__main__":
    main()
