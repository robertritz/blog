#!/usr/bin/env python3
"""
Merge LLM extraction results into extracted.json.

Replaces regex extraction with LLM results as the primary source,
keeping regex values as backup columns for comparison/audit.

Usage:
    python scripts/merge_llm_results.py [--dry-run]
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Merge LLM results into extracted.json")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    extracted_path = project_root / "data" / "processed" / "extracted.json"
    results_path = project_root / "data" / "processed" / "llm_extraction_results.json"

    # Load data
    print("Loading extracted.json...")
    with open(extracted_path, "r", encoding="utf-8") as f:
        extracted = json.load(f)
    print(f"  Loaded {len(extracted)} cases")

    print("Loading LLM results...")
    with open(results_path, "r", encoding="utf-8") as f:
        results_data = json.load(f)
    llm_results = results_data.get("results", {})
    print(f"  Loaded {len(llm_results)} LLM results")

    # Fields to merge from LLM
    llm_fields = [
        # v1 fields
        "gender", "age", "education", "employed", "occupation",
        "family_size", "prior_criminal", "sentence_type",
        "sentence_months", "sentence_fine_mnt",
        "extraction_quality", "quality_issues",
        # v2 fields
        "aggravating_factors", "mitigating_factors",
        "victim_relationship", "victim_minor",
        "crime_amount_mnt", "injury_severity", "intoxicated_at_crime",
        "has_lawyer", "plea_agreement", "plea_guilty", "restitution_paid",
        "time_served_days", "sentence_suspended_months",
    ]

    # Track changes
    merged_count = 0
    field_updates = {f: 0 for f in llm_fields}
    field_fills = {f: 0 for f in llm_fields}  # Fills gaps (regex was None)

    # Create backup before modifying
    if not args.dry_run:
        backup_path = extracted_path.with_suffix(".json.backup")
        print(f"\nCreating backup at {backup_path}...")
        shutil.copy(extracted_path, backup_path)

    print("\nMerging LLM results...")

    for case in extracted:
        case_id = case["case_id"]

        # Skip if no LLM result
        if str(case_id) not in llm_results and case_id not in llm_results:
            continue

        llm = llm_results.get(str(case_id)) or llm_results.get(case_id)
        if not llm:
            continue

        merged_count += 1

        # Move current regex values to regex_* columns (first time only)
        if "regex_gender" not in case:
            for field in llm_fields:
                if field in case and field not in ["extraction_quality", "quality_issues"]:
                    case[f"regex_{field}"] = case.get(field)

        # Merge LLM values
        for field in llm_fields:
            llm_value = llm.get(field)

            # Track if we're filling a gap vs updating
            old_value = case.get(field)
            if old_value is None and llm_value is not None:
                field_fills[field] += 1

            if llm_value is not None:
                field_updates[field] += 1
                case[field] = llm_value

        # Update extraction method
        case["extraction_method"] = "llm"
        case["llm_model"] = "grok-4-1-fast"
        case["llm_extracted_at"] = results_data.get("retrieved_at")

    print(f"\nMerged {merged_count} cases with LLM results")

    # Print field statistics
    print("\nField updates (LLM provided value):")
    for field, count in sorted(field_updates.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {field}: {count}")

    print("\nGap fills (regex was None, LLM provided):")
    for field, count in sorted(field_fills.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {field}: {count}")

    # Coverage comparison
    print("\nCoverage comparison:")
    for field in ["gender", "age", "education", "prior_criminal", "sentence_type"]:
        regex_count = sum(1 for c in extracted if c.get(f"regex_{field}") is not None)
        current_count = sum(1 for c in extracted if c.get(field) is not None)
        print(f"  {field}: regex={regex_count} -> merged={current_count} (+{current_count - regex_count})")

    if args.dry_run:
        print("\n[DRY RUN] No files modified.")
    else:
        # Save merged data
        print(f"\nSaving to {extracted_path}...")
        with open(extracted_path, "w", encoding="utf-8") as f:
            json.dump(extracted, f, ensure_ascii=False, indent=2)
        print("Done!")

        print(f"\nBackup saved at: {backup_path}")


if __name__ == "__main__":
    main()
