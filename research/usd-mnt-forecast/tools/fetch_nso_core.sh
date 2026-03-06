#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw/nso"
SKILL_DIR="/Users/ritz/projects/data/.claude/skills/datamn-source-nso"
FETCH_SCRIPT="$SKILL_DIR/fetch_data.py"

mkdir -p "$RAW_DIR"

if [ ! -f "$FETCH_SCRIPT" ]; then
  echo "NSO fetch skill not found at $FETCH_SCRIPT" >&2
  exit 1
fi

TABLES=(
  "DT_NSO_1400_003V1.px"
  "DT_NSO_0600_010V1.px"
  "DT_NSO_0600_009V1.px"
  "DT_NSO_1100_001V2.px"
  "DT_NSO_1100_015V3_1.px"
  "DT_NSO_1100_016V5.px"
  "DT_NSO_1100_015V12.px"
)

for table in "${TABLES[@]}"; do
  echo "Fetching $table"
  python3 "$FETCH_SCRIPT" --table "$table" --lang en --output "$RAW_DIR"
done

echo "NSO core tables refreshed in $RAW_DIR"
