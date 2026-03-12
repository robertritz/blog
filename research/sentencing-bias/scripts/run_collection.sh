#!/usr/bin/env bash
# Run full collection pipeline: enumerate → scrape → extract
# Usage: bash scripts/run_collection.sh
# Run in tmux: tmux new-session -d -s sentencing "bash scripts/run_collection.sh"
#
# Resilience: scrape step auto-retries on failure (crash, network, reboot).
# Safe to kill and restart — all steps are resumable.

set -uo pipefail
cd "$(dirname "$0")/.."

MAX_RETRIES=0  # 0 = infinite retries
RETRY_DELAY=120  # seconds between retries

echo "=== Starting full collection pipeline ==="
echo "Time: $(date)"

echo ""
echo "=== Step 1: Enumerate ==="
python3 scripts/collect_all_cases.py --step enumerate
if [ $? -ne 0 ]; then
    echo "ERROR: Enumeration failed. Cannot proceed."
    exit 1
fi

echo ""
echo "=== Step 2: Scrape (with auto-retry) ==="
attempt=0
while true; do
    attempt=$((attempt + 1))
    echo "--- Scrape attempt $attempt ($(date)) ---"
    python3 scripts/collect_all_cases.py --step scrape
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "Scraping completed successfully."
        break
    fi

    echo "Scrape exited with code $exit_code."

    if [ $MAX_RETRIES -gt 0 ] && [ $attempt -ge $MAX_RETRIES ]; then
        echo "Max retries ($MAX_RETRIES) reached. Giving up."
        exit 1
    fi

    echo "Retrying in ${RETRY_DELAY}s... (attempt $attempt)"
    sleep $RETRY_DELAY
done

echo ""
echo "=== Step 3: Extract ==="
python3 scripts/collect_all_cases.py --step extract

echo ""
echo "=== Collection complete ==="
echo "Time: $(date)"
