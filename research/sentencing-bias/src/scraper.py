"""
Scraper for shuukh.mn court decisions.

Usage:
    python scraper.py --pilot 500  # Scrape 500 cases for pilot
    python scraper.py --full        # Scrape all available cases
"""

import re
import json
import random
import time
import requests
from pathlib import Path
from typing import Optional
import argparse
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://shuukh.mn"
API_ENDPOINT = "/site/case_ajax"
CASE_ENDPOINT = "/single_case"

DEFAULT_DATERANGE = "2020/01/01 - 2026/02/04"

HEADERS = {
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (research project - sentencing bias study)",
}

# Polite rate limiting - be respectful to the server
MIN_DELAY = 1.5  # Minimum seconds between requests
MAX_DELAY = 3.0  # Maximum seconds between requests


def polite_sleep():
    """Sleep a random duration to be polite to the server."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)


def get_case_list_page(
    page: int = 1,
    daterange: str = DEFAULT_DATERANGE,
    retries: int = 3,
) -> dict:
    """Fetch one page of case listings from the API.

    Returns dict with keys: case_ids (list[int]), count (int), has_more (bool)
    """
    params = {
        "id": "1",
        "court_cat": "2",
        "bb": "1",
        "page": str(page),
        "daterange": daterange,
        "keyword": "",
        "court": "",
        "index_number": "",
        "number": "",
        "is_active": "",
        "court_order": "1",
        "date_order": "1",
        "result": "",
    }

    for attempt in range(retries):
        try:
            response = requests.get(
                f"{BASE_URL}{API_ENDPOINT}",
                params=params,
                headers=HEADERS,
                timeout=60,
            )
            response.raise_for_status()

            data = response.json()
            count = data.get("count", 0)
            view_html = data.get("view", "")

            # Extract case IDs from the HTML view
            case_ids = [int(m) for m in re.findall(r"/single_case/(\d+)", view_html)]
            # Deduplicate while preserving order
            seen = set()
            unique_ids = []
            for cid in case_ids:
                if cid not in seen:
                    seen.add(cid)
                    unique_ids.append(cid)

            has_more = len(unique_ids) > 0
            return {"case_ids": unique_ids, "count": count, "has_more": has_more}

        except requests.exceptions.Timeout:
            logger.warning(f"Page {page}: timeout (attempt {attempt + 1}/{retries})")
            time.sleep(10 * (attempt + 1))
        except requests.exceptions.RequestException as e:
            logger.warning(f"Page {page}: {e} (attempt {attempt + 1}/{retries})")
            time.sleep(10 * (attempt + 1))

    raise requests.exceptions.ReadTimeout(f"Page {page}: all {retries} attempts timed out")


def enumerate_all_case_ids(
    daterange: str = DEFAULT_DATERANGE,
    max_pages: Optional[int] = None,
    save_path: Optional[Path] = None,
) -> list[int]:
    """Enumerate all case IDs by paginating through the API.

    Resumable: if save_path exists with {"ids": [...], "last_page": N},
    resumes from last_page + 1.

    Args:
        daterange: Date range to query
        max_pages: If set, stop after this many pages (for testing)
        save_path: If set, save IDs to this file as they're collected
    """
    all_ids = []
    seen = set()
    start_page = 1

    # Resume from existing progress
    if save_path and save_path.exists():
        try:
            saved = json.loads(save_path.read_text())
            if isinstance(saved, dict) and "ids" in saved:
                all_ids = saved["ids"]
                seen = set(all_ids)
                start_page = saved.get("last_page", 0) + 1
                logger.info(f"Resuming: {len(all_ids)} IDs from {start_page - 1} pages, starting page {start_page}")
            elif isinstance(saved, list):
                # Legacy format — treat as complete list, re-enumerate from scratch
                all_ids = saved
                seen = set(all_ids)
                logger.info(f"Found legacy format with {len(all_ids)} IDs, re-enumerating from page 1")
                all_ids = []
                seen = set()
                start_page = 1
        except (json.JSONDecodeError, KeyError):
            pass

    # First request to get total count
    result = get_case_list_page(page=1, daterange=daterange)
    total_count = result["count"]
    total_pages = (total_count + 19) // 20  # 20 per page
    logger.info(f"Total cases: {total_count}, estimated pages: {total_pages}")

    # If starting fresh, collect page 1 IDs
    if start_page <= 1:
        for cid in result["case_ids"]:
            if cid not in seen:
                seen.add(cid)
                all_ids.append(cid)
        start_page = 2

    if max_pages and max_pages <= 1:
        return all_ids

    page = start_page
    while page <= total_pages:
        if max_pages and page > max_pages:
            break

        polite_sleep()

        try:
            result = get_case_list_page(page=page, daterange=daterange)
            if not result["has_more"] and not result["case_ids"]:
                break

            for cid in result["case_ids"]:
                if cid not in seen:
                    seen.add(cid)
                    all_ids.append(cid)

            if page % 10 == 0:
                logger.info(f"Page {page}/{total_pages}: {len(all_ids)} IDs collected")
            if page % 25 == 0 and save_path:
                _save_enumeration(save_path, all_ids, page)

        except Exception as e:
            logger.error(f"Page {page} failed: {e}")
            # Save progress before potential crash
            if save_path:
                _save_enumeration(save_path, all_ids, page - 1)
            polite_sleep()  # Extra pause on error

        page += 1

    logger.info(f"Enumeration complete: {len(all_ids)} unique case IDs")

    if save_path:
        _save_enumeration(save_path, all_ids, page - 1)
        logger.info(f"Saved {len(all_ids)} IDs to {save_path}")

    return all_ids


def _save_enumeration(save_path: Path, ids: list[int], last_page: int):
    """Save enumeration progress as resumable JSON."""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(json.dumps({"ids": ids, "last_page": last_page}))


def get_case_detail(case_id: int, retries: int = 3) -> Optional[str]:
    """Fetch individual case HTML with retry logic."""
    url = f"{BASE_URL}{CASE_ENDPOINT}/{case_id}"
    params = {
        "daterange": DEFAULT_DATERANGE,
        "id": "1",
        "court_cat": "2",
        "bb": "1",
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=60)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                # Rate limited - back off significantly
                wait = 30 * (attempt + 1)
                logger.warning(f"Case {case_id}: rate limited, waiting {wait}s")
                time.sleep(wait)
            elif response.status_code >= 500:
                # Server error — worth retrying
                logger.warning(f"Case {case_id}: HTTP {response.status_code} (attempt {attempt + 1}/{retries})")
                time.sleep(10 * (attempt + 1))
            else:
                # Client error (4xx) — not worth retrying
                logger.warning(f"Case {case_id}: HTTP {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            logger.warning(f"Case {case_id}: timeout (attempt {attempt + 1}/{retries})")
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            logger.error(f"Case {case_id}: {e}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))

    return None


def strip_html_to_json(html: str) -> Optional[dict]:
    """Strip full page HTML down to the useful content.

    Returns dict with:
        table_html: metadata table HTML string
        text: plain text from the case content div
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract metadata table
    table = soup.find("table", class_="table")
    table_html = str(table) if table else ""

    # Extract case text from div#source-html (main content area)
    source_div = soup.find("div", id="source-html")
    if source_div:
        text = source_div.get_text()
    else:
        # Fallback: get text from the whole page (some cases have different structure)
        text = soup.get_text()

    if not text.strip():
        return None

    return {"table_html": table_html, "text": text}


def scrape_cases(
    case_ids: list[int],
    output_dir: Path,
    progress_path: Optional[Path] = None,
    max_consecutive_failures: int = 10,
) -> dict:
    """Scrape multiple cases with polite rate limiting.

    Saves each case as JSON with stripped content (table_html + text).
    Skips cases that already exist as .json or legacy .html files.
    Writes progress to progress_path every 100 cases.

    If max_consecutive_failures in a row occur (likely network outage),
    pauses with exponential backoff before resuming.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {"success": 0, "failed": 0, "skipped": 0, "ids_failed": []}

    total = len(case_ids)
    consecutive_failures = 0

    for i, case_id in enumerate(case_ids):
        # Skip if already downloaded (check both new JSON and legacy HTML)
        json_path = output_dir / f"{case_id}.json"
        html_path = output_dir / f"{case_id}.html"
        if json_path.exists() or html_path.exists():
            results["skipped"] += 1
            done = results["success"] + results["failed"] + results["skipped"]
            if done % 500 == 0:
                logger.info(f"Skipping: {done}/{total} processed so far")
            continue

        # Consecutive failure backoff — likely network outage
        if consecutive_failures >= max_consecutive_failures:
            if progress_path:
                _save_progress(progress_path, results, total)
            backoff = min(300, 60 * (consecutive_failures // max_consecutive_failures))
            logger.warning(
                f"{consecutive_failures} consecutive failures — "
                f"likely network issue. Pausing {backoff}s..."
            )
            time.sleep(backoff)

        polite_sleep()

        html = get_case_detail(case_id)
        if html:
            case_json = strip_html_to_json(html)
            if case_json:
                json_path.write_text(
                    json.dumps(case_json, ensure_ascii=False),
                    encoding="utf-8",
                )
                results["success"] += 1
                consecutive_failures = 0
            else:
                # HTML fetched but no usable content — real failure, not network
                results["failed"] += 1
                results["ids_failed"].append(case_id)
                consecutive_failures = 0
        else:
            results["failed"] += 1
            results["ids_failed"].append(case_id)
            consecutive_failures += 1

        done = results["success"] + results["failed"] + results["skipped"]
        if done % 25 == 0 or done == total:
            logger.info(
                f"Progress: {done}/{total} "
                f"(success={results['success']}, "
                f"failed={results['failed']}, "
                f"skipped={results['skipped']})"
            )

        # Write progress file every 100 new downloads
        if progress_path and (results["success"] + results["failed"]) % 100 == 0:
            _save_progress(progress_path, results, total)

    # Final progress save
    if progress_path:
        _save_progress(progress_path, results, total)

    return results


def _save_progress(progress_path: Path, results: dict, total: int):
    """Write scraping progress to JSON file."""
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress = {
        "total": total,
        "success": results["success"],
        "failed": results["failed"],
        "skipped": results["skipped"],
        "failed_ids_count": len(results["ids_failed"]),
        "last_failed_ids": results["ids_failed"][-20:],
    }
    progress_path.write_text(json.dumps(progress, indent=2))


def enumerate_sampled_pages(
    n_cases: int = 500,
    seed: int = 42,
    daterange: str = DEFAULT_DATERANGE,
) -> list[int]:
    """Sample case IDs by fetching random pages instead of crawling all pages.

    This is much faster and more polite than enumerating all 4000+ pages.
    """
    rng = random.Random(seed)

    # First, get total count
    result = get_case_list_page(page=1, daterange=daterange)
    total_count = result["count"]
    total_pages = (total_count + 19) // 20
    logger.info(f"Total cases: {total_count}, total pages: {total_pages}")

    # Sample enough random pages to get n_cases unique IDs
    # Each page has ~20 IDs, so sample n_cases/20 * 1.5 pages for margin
    n_pages = min(int(n_cases / 20 * 1.5) + 5, total_pages)
    sampled_pages = sorted(rng.sample(range(1, total_pages + 1), n_pages))
    logger.info(f"Sampling {n_pages} random pages to get {n_cases} case IDs")

    all_ids = []
    seen = set()
    for i, page in enumerate(sampled_pages):
        polite_sleep()

        try:
            result = get_case_list_page(page=page, daterange=daterange)
            for cid in result["case_ids"]:
                if cid not in seen:
                    seen.add(cid)
                    all_ids.append(cid)
        except Exception as e:
            logger.error(f"Page {page} failed: {e}")

        if (i + 1) % 10 == 0:
            logger.info(f"Fetched {i + 1}/{n_pages} pages, {len(all_ids)} IDs collected")

    logger.info(f"Collected {len(all_ids)} unique IDs from {n_pages} pages")

    # Now sample the desired number
    if len(all_ids) > n_cases:
        all_ids = rng.sample(all_ids, n_cases)

    return all_ids


def sample_case_ids(all_ids: list[int], n: int, seed: int = 42) -> list[int]:
    """Random sample of case IDs for pilot."""
    rng = random.Random(seed)
    return rng.sample(all_ids, min(n, len(all_ids)))


def main():
    parser = argparse.ArgumentParser(description="Scrape shuukh.mn court decisions")
    parser.add_argument("--pilot", type=int, help="Number of cases for pilot")
    parser.add_argument("--full", action="store_true", help="Scrape all cases")
    parser.add_argument("--enumerate-only", action="store_true", help="Only enumerate IDs")
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--max-pages", type=int, help="Max pages to enumerate (for testing)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = parser.parse_args()

    ids_path = Path("data/case_ids.json")

    # Load or enumerate case IDs
    if ids_path.exists():
        logger.info(f"Loading existing case IDs from {ids_path}")
        saved = json.loads(ids_path.read_text())
        all_ids = saved["ids"] if isinstance(saved, dict) else saved
    else:
        logger.info("Enumerating case IDs from API...")
        all_ids = enumerate_all_case_ids(
            max_pages=args.max_pages,
            save_path=ids_path,
        )

    logger.info(f"Total case IDs: {len(all_ids)}")

    if args.enumerate_only:
        return

    if args.pilot:
        if all_ids:
            pilot_ids = sample_case_ids(all_ids, args.pilot, seed=args.seed)
        else:
            # Fast path: sample pages randomly instead of enumerating all
            logger.info("Using sampled page enumeration for pilot...")
            pilot_ids = enumerate_sampled_pages(
                n_cases=args.pilot, seed=args.seed,
            )
        output_dir = Path("data/pilot")
        logger.info(f"Scraping {len(pilot_ids)} pilot cases...")

        # Save pilot IDs for reproducibility
        pilot_ids_path = output_dir / "pilot_ids.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        pilot_ids_path.write_text(json.dumps(pilot_ids))

        results = scrape_cases(pilot_ids, output_dir)
        logger.info(f"Pilot scraping complete: {results}")

    elif args.full:
        logger.info(f"Scraping all {len(all_ids)} cases...")
        results = scrape_cases(all_ids, args.output)
        logger.info(f"Full scraping complete: {results}")


if __name__ == "__main__":
    main()
