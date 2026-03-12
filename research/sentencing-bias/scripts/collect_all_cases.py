#!/usr/bin/env python3
"""
Orchestrate full data collection for sentencing bias study.

Usage:
    python scripts/collect_all_cases.py --step enumerate
    python scripts/collect_all_cases.py --step scrape [--limit N]
    python scripts/collect_all_cases.py --step extract
    python scripts/collect_all_cases.py --step all
"""

import sys
import json
import logging
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.scraper import enumerate_all_case_ids, scrape_cases
from src.extractor import process_batch

# Paths
DATA_DIR = PROJECT_ROOT / "data"
IDS_PATH = DATA_DIR / "case_ids.json"
RAW_DIR = DATA_DIR / "raw"
PILOT_DIR = DATA_DIR / "pilot"
PROCESSED_DIR = DATA_DIR / "processed"
PROGRESS_PATH = DATA_DIR / "scrape_progress.json"
EXTRACTED_PATH = PROCESSED_DIR / "extracted.json"
LOG_DIR = PROJECT_ROOT / "logs"


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "collection.log"

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    return logging.getLogger(__name__)


def load_case_ids() -> list[int]:
    """Load case IDs from the save file, handling both formats."""
    if not IDS_PATH.exists():
        return []
    saved = json.loads(IDS_PATH.read_text())
    if isinstance(saved, dict):
        return saved.get("ids", [])
    return saved


def step_enumerate(logger):
    """Enumerate all case IDs from shuukh.mn."""
    logger.info("=== STEP: Enumerate case IDs ===")

    existing = load_case_ids()
    if existing:
        logger.info(f"Found existing {len(existing)} IDs in {IDS_PATH}")
        # Check if enumeration was complete by looking at last_page
        if IDS_PATH.exists():
            saved = json.loads(IDS_PATH.read_text())
            if isinstance(saved, dict) and saved.get("last_page"):
                logger.info(f"Last page: {saved['last_page']} — will resume from there")

    ids = enumerate_all_case_ids(save_path=IDS_PATH)
    logger.info(f"Enumeration done: {len(ids)} total case IDs")
    return ids


def step_scrape(logger, limit=None):
    """Scrape case HTML and save as stripped JSON."""
    logger.info("=== STEP: Scrape cases ===")

    ids = load_case_ids()
    if not ids:
        logger.error(f"No case IDs found at {IDS_PATH}. Run --step enumerate first.")
        return

    if limit:
        ids = ids[:limit]
        logger.info(f"Limiting to first {limit} cases")

    logger.info(f"Scraping {len(ids)} cases to {RAW_DIR}")
    results = scrape_cases(ids, RAW_DIR, progress_path=PROGRESS_PATH)
    logger.info(
        f"Scraping done: success={results['success']}, "
        f"failed={results['failed']}, skipped={results['skipped']}"
    )
    if results["ids_failed"]:
        logger.warning(f"Failed IDs ({len(results['ids_failed'])}): {results['ids_failed'][:20]}...")


def step_extract(logger):
    """Run regex extraction on all scraped cases."""
    logger.info("=== STEP: Extract data ===")

    # Extract from raw/ (full dataset)
    raw_count = len(list(RAW_DIR.glob("*.json"))) + len(list(RAW_DIR.glob("*.html")))
    if raw_count > 0:
        logger.info(f"Extracting from {RAW_DIR} ({raw_count} files)")
        results = process_batch(RAW_DIR, EXTRACTED_PATH)
        logger.info(f"Extracted {len(results)} cases to {EXTRACTED_PATH}")

        # Quick coverage summary
        _print_coverage(results, logger)
    else:
        # Fall back to pilot data
        pilot_count = len(list(PILOT_DIR.glob("*.html")))
        if pilot_count > 0:
            logger.info(f"No raw data found, extracting from pilot ({pilot_count} files)")
            results = process_batch(PILOT_DIR, EXTRACTED_PATH)
            logger.info(f"Extracted {len(results)} cases to {EXTRACTED_PATH}")
            _print_coverage(results, logger)
        else:
            logger.error("No data to extract. Run --step scrape first.")


def _print_coverage(results, logger):
    """Print coverage summary for key fields."""
    total = len(results)
    if total == 0:
        return

    fields = ["gender", "age", "education", "sentence_type", "prior_criminal"]
    for field in fields:
        count = sum(1 for r in results if r.get(field) is not None)
        pct = count / total * 100
        logger.info(f"  {field}: {count}/{total} ({pct:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Full data collection for sentencing bias study")
    parser.add_argument(
        "--step",
        choices=["enumerate", "scrape", "extract", "all"],
        required=True,
        help="Which step to run",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of cases to scrape (for testing)",
    )
    args = parser.parse_args()

    logger = setup_logging()
    logger.info(f"Starting collection: step={args.step}, limit={args.limit}")

    try:
        if args.step == "enumerate":
            step_enumerate(logger)
        elif args.step == "scrape":
            step_scrape(logger, limit=args.limit)
        elif args.step == "extract":
            step_extract(logger)
        elif args.step == "all":
            step_enumerate(logger)
            step_scrape(logger, limit=args.limit)
            step_extract(logger)
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Progress has been saved.")
        sys.exit(1)
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
