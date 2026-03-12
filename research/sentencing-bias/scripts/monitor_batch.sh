#!/bin/bash
# Monitor batch status until completion
set -e

cd /home/ritz/projects/research/sentencing-bias

export XAI_API_KEY="$(age -d -i ~/.age/key.txt ~/projects/perspective/.xai-api-key.age)"

echo "Starting batch monitor at $(date)"
echo "Will check every 5 minutes..."

while true; do
    echo ""
    echo "=== $(date) ==="
    python3 scripts/llm_batch_extraction.py --status 2>&1
    
    # Check if all pending = 0
    if python3 -c "
import json
p = json.load(open('data/batch_progress.json'))
pending = sum(b.get('num_pending', 1) for b in p['batches'])
exit(0 if pending == 0 else 1)
" 2>/dev/null; then
        echo ""
        echo "=== All batches complete! ==="
        echo "Run: python scripts/llm_batch_extraction.py --resume"
        break
    fi
    
    sleep 300  # 5 minutes
done
