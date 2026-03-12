#!/usr/bin/env python3
"""
LLM Extraction Pilot Script

Tests Grok API extraction on a sample of cases with missing regex fields.
Compares LLM extraction to regex extraction to evaluate coverage gain.

Usage:
    python scripts/llm_pilot.py --sample 50 --model grok-4-1-fast
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from grok_extractor import extract_with_grok, CaseExtraction


@dataclass
class PilotResult:
    """Result for a single case in the pilot."""
    case_id: int
    # Regex results
    regex_gender: Optional[str]
    regex_age: Optional[int]
    regex_education: Optional[str]
    regex_prior_criminal: Optional[bool]
    regex_sentence_type: Optional[str]
    regex_sentence_months: Optional[float]
    regex_sentence_fine_mnt: Optional[float]
    # LLM results
    llm_gender: Optional[str]
    llm_age: Optional[int]
    llm_education: Optional[str]
    llm_prior_criminal: Optional[bool]
    llm_sentence_type: Optional[str]
    llm_sentence_months: Optional[float]
    llm_sentence_fine_mnt: Optional[float]
    llm_employed: Optional[bool]
    llm_occupation: Optional[str]
    llm_family_size: Optional[int]
    # Data quality (from LLM)
    llm_extraction_quality: Optional[str] = None  # complete, partial, unreliable
    llm_quality_issues: Optional[list] = None     # list of issue codes
    # Metadata
    latency_seconds: float = 0.0
    error: Optional[str] = None


def load_extracted_data(extracted_path: Path) -> dict:
    """Load extracted.json and index by case_id."""
    with open(extracted_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {case["case_id"]: case for case in data}


def select_pilot_sample(
    extracted: dict,
    raw_dir: Path,
    sample_size: int,
    seed: int = 42,
) -> list[int]:
    """Select cases for pilot based on criteria.

    Criteria:
    1. Valid (no data_quality_issue)
    2. Missing at least one key field (gender, sentence_type, or prior_criminal)
    3. Has raw JSON file available
    """
    candidates = []

    for case_id, case in extracted.items():
        # Skip cases with data quality issues
        if case.get("data_quality_issue"):
            continue

        # Check for missing key fields
        missing_key_field = (
            case.get("gender") is None or
            case.get("sentence_type") is None or
            case.get("prior_criminal") is None
        )
        if not missing_key_field:
            continue

        # Verify raw file exists
        raw_file = raw_dir / f"{case_id}.json"
        if not raw_file.exists():
            continue

        candidates.append(case_id)

    print(f"Found {len(candidates)} candidate cases with missing fields")

    # Random sample
    random.seed(seed)
    sample = random.sample(candidates, min(sample_size, len(candidates)))

    return sorted(sample)


def run_pilot(
    sample_ids: list[int],
    extracted: dict,
    raw_dir: Path,
    model: str,
) -> list[PilotResult]:
    """Run LLM extraction on pilot sample."""
    results = []
    total = len(sample_ids)

    for i, case_id in enumerate(sample_ids):
        print(f"[{i+1}/{total}] Processing case {case_id}...", end=" ")

        # Load raw case
        raw_file = raw_dir / f"{case_id}.json"
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        text = raw_data.get("text", "")
        regex_data = extracted[case_id]

        # Initialize result with regex data
        result = PilotResult(
            case_id=case_id,
            regex_gender=regex_data.get("gender"),
            regex_age=regex_data.get("age"),
            regex_education=regex_data.get("education"),
            regex_prior_criminal=regex_data.get("prior_criminal"),
            regex_sentence_type=regex_data.get("sentence_type"),
            regex_sentence_months=regex_data.get("sentence_months"),
            regex_sentence_fine_mnt=regex_data.get("sentence_fine_mnt"),
            llm_gender=None,
            llm_age=None,
            llm_education=None,
            llm_prior_criminal=None,
            llm_sentence_type=None,
            llm_sentence_months=None,
            llm_sentence_fine_mnt=None,
            llm_employed=None,
            llm_occupation=None,
            llm_family_size=None,
            latency_seconds=0.0,
        )

        try:
            extraction, latency = extract_with_grok(text, model=model)

            result.llm_gender = extraction.gender
            result.llm_age = extraction.age
            result.llm_education = extraction.education
            result.llm_prior_criminal = extraction.prior_criminal
            result.llm_sentence_type = extraction.sentence_type
            result.llm_sentence_months = extraction.sentence_months
            result.llm_sentence_fine_mnt = extraction.sentence_fine_mnt
            result.llm_employed = extraction.employed
            result.llm_occupation = extraction.occupation
            result.llm_family_size = extraction.family_size
            result.llm_extraction_quality = extraction.extraction_quality.value
            result.llm_quality_issues = extraction.quality_issues
            result.latency_seconds = latency

            quality_flag = f" [{extraction.extraction_quality.value}]" if extraction.extraction_quality.value != "complete" else ""
            print(f"OK ({latency:.1f}s){quality_flag}")

        except Exception as e:
            result.error = str(e)
            print(f"ERROR: {e}")

        results.append(result)

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    return results


def compute_statistics(results: list[PilotResult]) -> dict:
    """Compute coverage and gain statistics."""
    stats = {
        "total_cases": len(results),
        "successful_calls": sum(1 for r in results if r.error is None),
        "failed_calls": sum(1 for r in results if r.error is not None),
        "avg_latency": 0.0,
        "fields": {},
    }

    successful = [r for r in results if r.error is None]
    if successful:
        stats["avg_latency"] = sum(r.latency_seconds for r in successful) / len(successful)

    # Quality stats
    quality_counts = {"complete": 0, "partial": 0, "unreliable": 0}
    issue_counts = {}
    for r in successful:
        if r.llm_extraction_quality:
            quality_counts[r.llm_extraction_quality] = quality_counts.get(r.llm_extraction_quality, 0) + 1
        if r.llm_quality_issues:
            for issue in r.llm_quality_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

    stats["quality"] = {
        "complete": quality_counts.get("complete", 0),
        "partial": quality_counts.get("partial", 0),
        "unreliable": quality_counts.get("unreliable", 0),
        "issues": issue_counts,
    }

    # Calculate per-field stats
    fields = [
        ("gender", "regex_gender", "llm_gender"),
        ("age", "regex_age", "llm_age"),
        ("education", "regex_education", "llm_education"),
        ("prior_criminal", "regex_prior_criminal", "llm_prior_criminal"),
        ("sentence_type", "regex_sentence_type", "llm_sentence_type"),
        ("sentence_months", "regex_sentence_months", "llm_sentence_months"),
        ("sentence_fine_mnt", "regex_sentence_fine_mnt", "llm_sentence_fine_mnt"),
    ]

    for field_name, regex_attr, llm_attr in fields:
        regex_found = sum(1 for r in successful if getattr(r, regex_attr) is not None)
        llm_found = sum(1 for r in successful if getattr(r, llm_attr) is not None)

        # Count cases where regex missed but LLM found
        llm_filled_gap = sum(
            1 for r in successful
            if getattr(r, regex_attr) is None and getattr(r, llm_attr) is not None
        )

        # Count cases where both found (for accuracy comparison)
        both_found = sum(
            1 for r in successful
            if getattr(r, regex_attr) is not None and getattr(r, llm_attr) is not None
        )

        # Count agreement when both found
        agreement = sum(
            1 for r in successful
            if getattr(r, regex_attr) is not None and getattr(r, llm_attr) is not None
            and getattr(r, regex_attr) == getattr(r, llm_attr)
        )

        stats["fields"][field_name] = {
            "regex_found": regex_found,
            "llm_found": llm_found,
            "llm_filled_gap": llm_filled_gap,
            "both_found": both_found,
            "agreement": agreement,
            "agreement_rate": agreement / both_found if both_found > 0 else None,
        }

    return stats


def print_summary(stats: dict):
    """Print a human-readable summary of the pilot results."""
    print("\n" + "=" * 60)
    print("LLM PILOT RESULTS SUMMARY")
    print("=" * 60)

    print(f"\nTotal cases: {stats['total_cases']}")
    print(f"Successful API calls: {stats['successful_calls']}")
    print(f"Failed API calls: {stats['failed_calls']}")
    print(f"Average latency: {stats['avg_latency']:.2f}s")

    # Quality breakdown
    q = stats.get("quality", {})
    print(f"\nData Quality Assessment:")
    print(f"  Complete (usable): {q.get('complete', 0)}")
    print(f"  Partial (some gaps): {q.get('partial', 0)}")
    print(f"  Unreliable (exclude): {q.get('unreliable', 0)}")
    if q.get("issues"):
        print(f"  Issues found:")
        for issue, count in sorted(q["issues"].items(), key=lambda x: -x[1]):
            print(f"    - {issue}: {count}")

    print("\n" + "-" * 60)
    print(f"{'Field':<20} {'Regex':<8} {'LLM':<8} {'Gap Fill':<10} {'Agree %':<10}")
    print("-" * 60)

    for field_name, field_stats in stats["fields"].items():
        agree_pct = (
            f"{field_stats['agreement_rate']*100:.0f}%"
            if field_stats["agreement_rate"] is not None
            else "N/A"
        )
        print(
            f"{field_name:<20} "
            f"{field_stats['regex_found']:<8} "
            f"{field_stats['llm_found']:<8} "
            f"{field_stats['llm_filled_gap']:<10} "
            f"{agree_pct:<10}"
        )

    print("-" * 60)

    # Calculate overall gap-fill rate for key fields
    key_fields = ["gender", "sentence_type", "prior_criminal"]
    total_gaps = sum(
        stats["successful_calls"] - stats["fields"][f]["regex_found"]
        for f in key_fields
    )
    total_filled = sum(stats["fields"][f]["llm_filled_gap"] for f in key_fields)
    gap_fill_rate = total_filled / total_gaps if total_gaps > 0 else 0

    print(f"\nKey fields (gender, sentence_type, prior_criminal):")
    print(f"  Total gaps in sample: {total_gaps}")
    print(f"  Gaps filled by LLM: {total_filled}")
    print(f"  Gap-fill rate: {gap_fill_rate*100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Run LLM extraction pilot")
    parser.add_argument(
        "--sample", type=int, default=50,
        help="Number of cases to sample (default: 50)"
    )
    parser.add_argument(
        "--model", type=str, default="grok-4-1-fast",
        help="Grok model to use (default: grok-4-1-fast)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent.parent
    extracted_path = project_root / "data" / "processed" / "extracted.json"
    raw_dir = project_root / "data" / "raw"
    output_dir = project_root / "data" / "pilot"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check extracted.json exists
    if not extracted_path.exists():
        print(f"Error: {extracted_path} not found")
        sys.exit(1)

    # Load data
    print(f"Loading extracted data from {extracted_path}...")
    extracted = load_extracted_data(extracted_path)
    print(f"Loaded {len(extracted)} cases")

    # Select sample
    print(f"\nSelecting {args.sample} cases for pilot...")
    sample_ids = select_pilot_sample(extracted, raw_dir, args.sample, args.seed)
    print(f"Selected {len(sample_ids)} cases")

    if not sample_ids:
        print("Error: No valid candidates found for pilot")
        sys.exit(1)

    # Run pilot
    print(f"\nRunning LLM extraction with model={args.model}...")
    results = run_pilot(sample_ids, extracted, raw_dir, args.model)

    # Compute statistics
    stats = compute_statistics(results)

    # Save results
    results_path = output_dir / "llm_pilot_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "sample_size": len(sample_ids),
                    "model": args.model,
                    "seed": args.seed,
                },
                "statistics": stats,
                "results": [asdict(r) for r in results],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nResults saved to {results_path}")

    # Print summary
    print_summary(stats)


if __name__ == "__main__":
    main()
