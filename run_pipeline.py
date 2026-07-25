"""Run the full analysis pipeline from the project root."""

import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from eda import run_eda
from logging_config import setup_logging
from model import run_full_pipeline

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    logger.info("=== Money vs Happiness ML Pipeline ===")
    run_eda()
    run_full_pipeline()
    logger.info("Done. See results/ and results/plots/")


if __name__ == "__main__":
    main()
