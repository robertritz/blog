#!/bin/bash
# Run batch extraction with API key
set -e
cd /home/ritz/projects/research/sentencing-bias

export XAI_API_KEY="$(age -d -i ~/.age/key.txt ~/projects/perspective/.xai-api-key.age)"

echo "Starting batch extraction at $(date)"
echo "API key loaded (length: ${#XAI_API_KEY})"

python3 -u scripts/llm_batch_extraction.py --no-wait

echo "Batch creation complete at $(date)"
