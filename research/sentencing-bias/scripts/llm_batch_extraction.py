#!/usr/bin/env python3
"""
Batch LLM extraction using xAI Batch API.

Runs LLM extraction on all valid cases (77,968) using xAI's native Batch API
for 50% cost savings. Uses structured outputs with Pydantic models.

Usage:
    # Test with 10 cases first (may take up to 24 hours for batch completion)
    python scripts/llm_batch_extraction.py --test

    # Full extraction (all 78K cases in batches of 5000)
    python scripts/llm_batch_extraction.py

    # Resume monitoring existing batches
    python scripts/llm_batch_extraction.py --resume

    # Check status only
    python scripts/llm_batch_extraction.py --status
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from xai_sdk import Client
from xai_sdk.chat import system, user
from grok_extractor import CaseExtraction, SYSTEM_PROMPT


# Configuration
# Note: gRPC has 4MB message limit per add() call, ~40KB per case = max ~100 cases per add()
# We use 1000 cases per batch, but add in chunks of 50 to stay under gRPC limit
BATCH_SIZE = 1000  # Requests per batch
ADD_CHUNK_SIZE = 50  # Requests per add() call (stay under 4MB gRPC limit)
# Note: xAI SDK uses different model names than REST API
# Available: grok-4-1-fast-non-reasoning, grok-4-1-fast-reasoning
MODEL = "grok-4-1-fast-non-reasoning"
POLL_INTERVAL = 300  # 5 minutes between status checks


def get_project_paths() -> dict:
    """Get all relevant project paths."""
    project_root = Path(__file__).parent.parent
    return {
        "project_root": project_root,
        "extracted": project_root / "data" / "processed" / "extracted.json",
        "raw_dir": project_root / "data" / "raw",
        "progress": project_root / "data" / "batch_progress.json",
        "results": project_root / "data" / "processed" / "llm_extraction_results.json",
    }


def load_progress(progress_path: Path) -> dict:
    """Load or initialize batch progress tracking."""
    if progress_path.exists():
        with open(progress_path, "r") as f:
            return json.load(f)
    return {
        "started_at": None,
        "batches": [],  # List of {batch_id, name, case_ids, status, created_at}
        "completed_batch_ids": [],
        "results_retrieved": False,
    }


def save_progress(progress_path: Path, progress: dict):
    """Save batch progress tracking."""
    with open(progress_path, "w") as f:
        json.dump(progress, f, indent=2)


def load_candidates(paths: dict) -> list[dict]:
    """Load all valid cases from extracted.json."""
    with open(paths["extracted"], "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter to valid cases only (no data quality issues)
    valid = [c for c in data if c.get("data_quality_issue") is None]

    # Further filter to cases with raw files
    candidates = []
    for case in valid:
        raw_file = paths["raw_dir"] / f"{case['case_id']}.json"
        if raw_file.exists():
            candidates.append(case)

    return candidates


def create_batches(
    client: Client,
    candidates: list[dict],
    paths: dict,
    batch_size: int,
    test_mode: bool = False,
) -> list[dict]:
    """Create batches of requests using xAI Batch API."""

    if test_mode:
        # Just take first 10 for testing
        candidates = candidates[:10]
        batch_size = 10

    progress = load_progress(paths["progress"])
    progress["started_at"] = progress["started_at"] or datetime.now().isoformat()

    # Check for already-created batches
    existing_case_ids = set()
    for batch_info in progress["batches"]:
        existing_case_ids.update(batch_info.get("case_ids", []))

    # Filter out already-batched cases
    new_candidates = [c for c in candidates if c["case_id"] not in existing_case_ids]

    if not new_candidates:
        print("All cases already have batches created.")
        return progress["batches"]

    print(f"Creating batches for {len(new_candidates)} new cases...")

    batches_created = []

    for i in range(0, len(new_candidates), batch_size):
        chunk = new_candidates[i:i+batch_size]
        batch_num = len(progress["batches"]) + len(batches_created)
        batch_name = f"sentencing_batch_{batch_num:03d}"

        if test_mode:
            batch_name = "sentencing_test_batch"

        print(f"\nCreating batch '{batch_name}' with {len(chunk)} cases...")

        try:
            # Create the batch
            batch = client.batch.create(batch_name=batch_name)

            # Process and add requests in small chunks (stream to avoid memory issues)
            total_added = 0
            case_ids_added = []

            for j in range(0, len(chunk), ADD_CHUNK_SIZE):
                add_chunk = chunk[j:j+ADD_CHUNK_SIZE]
                batch_requests = []

                for case in add_chunk:
                    # Load raw text
                    raw_file = paths["raw_dir"] / f"{case['case_id']}.json"
                    try:
                        with open(raw_file, "r", encoding="utf-8") as f:
                            raw_data = json.load(f)
                    except Exception:
                        continue

                    text = raw_data.get("text", "")
                    if not text:
                        continue

                    # Create chat with structured output
                    chat = client.chat.create(
                        model=MODEL,
                        batch_request_id=str(case["case_id"]),
                        response_format=CaseExtraction,
                    )
                    chat.append(system(SYSTEM_PROMPT))
                    chat.append(user(text))
                    batch_requests.append(chat)
                    case_ids_added.append(case["case_id"])

                # Add this chunk to batch
                if batch_requests:
                    client.batch.add(batch_id=batch.batch_id, batch_requests=batch_requests)
                    total_added += len(batch_requests)
                    # Rate limit: 100 add calls per 30 seconds
                    time.sleep(0.35)

            if total_added > 0:
                batch_info = {
                    "batch_id": batch.batch_id,
                    "name": batch_name,
                    "case_ids": case_ids_added,
                    "num_requests": total_added,
                    "status": "created",
                    "created_at": datetime.now().isoformat(),
                }
                batches_created.append(batch_info)
                print(f"  Created batch {batch.batch_id} with {total_added} requests")

            # Rate limit: 1 batch creation per second
            time.sleep(1.1)

        except Exception as e:
            print(f"  Error creating batch: {e}")
            # Save progress even on error
            progress["batches"].extend(batches_created)
            save_progress(paths["progress"], progress)
            raise

    # Save progress
    progress["batches"].extend(batches_created)
    save_progress(paths["progress"], progress)

    print(f"\nCreated {len(batches_created)} new batches")
    return progress["batches"]


def check_batch_status(client: Client, paths: dict) -> dict:
    """Check status of all batches."""
    progress = load_progress(paths["progress"])

    if not progress["batches"]:
        print("No batches found. Run without --status first.")
        return progress

    print(f"\nBatch Status ({len(progress['batches'])} batches):")
    print("-" * 70)

    total_pending = 0
    total_success = 0
    total_error = 0

    for batch_info in progress["batches"]:
        batch_id = batch_info["batch_id"]
        try:
            batch = client.batch.get(batch_id=batch_id)
            state = batch.state

            batch_info["num_pending"] = state.num_pending
            batch_info["num_success"] = state.num_success
            batch_info["num_error"] = state.num_error
            batch_info["status"] = "completed" if state.num_pending == 0 else "processing"

            total_pending += state.num_pending
            total_success += state.num_success
            total_error += state.num_error

            status_str = "DONE" if state.num_pending == 0 else f"{state.num_pending} pending"
            print(f"  {batch_info['name']}: {status_str} ({state.num_success} ok, {state.num_error} err)")

        except Exception as e:
            print(f"  {batch_info['name']}: ERROR checking status - {e}")

    print("-" * 70)
    print(f"Total: {total_success} succeeded, {total_error} errors, {total_pending} pending")

    save_progress(paths["progress"], progress)
    return progress


def wait_for_completion(client: Client, paths: dict, poll_interval: int = POLL_INTERVAL):
    """Wait for all batches to complete, polling periodically."""
    print("\nWaiting for batch completion...")
    print(f"Polling every {poll_interval} seconds")

    while True:
        progress = check_batch_status(client, paths)

        # Check if all complete
        all_complete = all(
            b.get("status") == "completed"
            for b in progress["batches"]
        )

        if all_complete:
            print("\nAll batches completed!")
            return progress

        # Calculate ETA based on pending count
        total_pending = sum(b.get("num_pending", 0) for b in progress["batches"])
        print(f"\n{total_pending} requests still pending. Waiting {poll_interval}s...")
        time.sleep(poll_interval)


def retrieve_results(client: Client, paths: dict) -> dict:
    """Retrieve results from all completed batches."""
    progress = load_progress(paths["progress"])

    all_results = {}
    all_errors = []

    print("\nRetrieving results...")

    for batch_info in progress["batches"]:
        batch_id = batch_info["batch_id"]

        if batch_id in progress.get("completed_batch_ids", []):
            print(f"  {batch_info['name']}: already retrieved, skipping")
            continue

        print(f"  {batch_info['name']}: retrieving...")

        try:
            pagination_token = None
            batch_results = 0
            batch_errors = 0

            while True:
                # Get page of results
                page = client.batch.list_batch_results(
                    batch_id=batch_id,
                    limit=100,
                    pagination_token=pagination_token,
                )

                # Process succeeded results
                for result in page.succeeded:
                    case_id = int(result.batch_request_id)
                    # Parse the structured response
                    try:
                        content = result.response.content
                        # The response should be JSON matching CaseExtraction
                        if isinstance(content, str):
                            extraction = json.loads(content)
                        else:
                            extraction = content
                        all_results[case_id] = extraction
                        batch_results += 1
                    except Exception as e:
                        all_errors.append({
                            "case_id": case_id,
                            "error": f"Parse error: {e}",
                            "raw_content": str(content)[:500],
                        })
                        batch_errors += 1

                # Process failed results
                for result in page.failed:
                    case_id = int(result.batch_request_id)
                    all_errors.append({
                        "case_id": case_id,
                        "error": result.error_message,
                    })
                    batch_errors += 1

                # Check for more pages
                if hasattr(page, 'pagination_token') and page.pagination_token:
                    pagination_token = page.pagination_token
                else:
                    break

            print(f"    Retrieved {batch_results} results, {batch_errors} errors")
            progress["completed_batch_ids"].append(batch_id)

        except Exception as e:
            print(f"    Error retrieving results: {e}")

    # Save results
    results_data = {
        "retrieved_at": datetime.now().isoformat(),
        "total_results": len(all_results),
        "total_errors": len(all_errors),
        "results": all_results,
        "errors": all_errors,
    }

    with open(paths["results"], "w", encoding="utf-8") as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(all_results)} results to {paths['results']}")
    if all_errors:
        print(f"  {len(all_errors)} errors logged")

    progress["results_retrieved"] = True
    save_progress(paths["progress"], progress)

    return results_data


def print_summary(results_data: dict):
    """Print summary of extraction results."""
    results = results_data.get("results", {})
    errors = results_data.get("errors", [])

    print("\n" + "=" * 60)
    print("LLM BATCH EXTRACTION SUMMARY")
    print("=" * 60)

    print(f"\nTotal results: {len(results)}")
    print(f"Total errors: {len(errors)}")

    if not results:
        return

    # Quality breakdown
    quality_counts = {"complete": 0, "partial": 0, "unreliable": 0, "unknown": 0}
    for r in results.values():
        q = r.get("extraction_quality", "unknown")
        quality_counts[q] = quality_counts.get(q, 0) + 1

    print(f"\nExtraction Quality:")
    for q, count in quality_counts.items():
        if count > 0:
            pct = count / len(results) * 100
            print(f"  {q}: {count} ({pct:.1f}%)")

    # Field coverage
    fields = ["gender", "age", "education", "prior_criminal", "sentence_type",
              "sentence_months", "sentence_fine_mnt", "employed", "occupation", "family_size"]

    print(f"\nField Coverage:")
    for field in fields:
        found = sum(1 for r in results.values() if r.get(field) is not None)
        pct = found / len(results) * 100
        print(f"  {field}: {found}/{len(results)} ({pct:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Batch LLM extraction using xAI Batch API")
    parser.add_argument(
        "--test", action="store_true",
        help="Test mode: process only 10 cases"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume: skip batch creation, just wait and retrieve results"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Check status of existing batches only"
    )
    parser.add_argument(
        "--batch-size", type=int, default=BATCH_SIZE,
        help=f"Requests per batch (default: {BATCH_SIZE})"
    )
    parser.add_argument(
        "--no-wait", action="store_true",
        help="Don't wait for completion (just create batches)"
    )
    args = parser.parse_args()

    # Check API key
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        print("Set it with: export XAI_API_KEY=\"$(age -d -i ~/.age/key.txt ~/projects/perspective/.xai-api-key.age)\"")
        sys.exit(1)

    paths = get_project_paths()
    client = Client(api_key=api_key)

    # Status check only
    if args.status:
        check_batch_status(client, paths)
        return

    # Resume mode: skip creation, wait and retrieve
    if args.resume:
        progress = load_progress(paths["progress"])
        if not progress["batches"]:
            print("No existing batches found. Run without --resume first.")
            return

        wait_for_completion(client, paths)
        results = retrieve_results(client, paths)
        print_summary(results)
        return

    # Load candidates
    print("Loading candidates...")
    candidates = load_candidates(paths)
    print(f"Found {len(candidates)} valid cases with raw files")

    if args.test:
        print("\n*** TEST MODE: Processing only 10 cases ***\n")

    # Create batches
    create_batches(
        client,
        candidates,
        paths,
        args.batch_size,
        test_mode=args.test,
    )

    if args.no_wait:
        print("\nBatches created. Run with --resume to wait for completion.")
        return

    # Wait for completion
    wait_for_completion(client, paths)

    # Retrieve results
    results = retrieve_results(client, paths)
    print_summary(results)

    print("\nDone! Next step: python scripts/merge_llm_results.py")


if __name__ == "__main__":
    main()
