#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <indicator_id> [slug] [report_id] [start_year] [end_year]" >&2
  echo "Example: $0 121832 current-account 1104 2000 2026" >&2
  exit 1
fi

INDICATOR_ID="$1"
SLUG_IN="${2:-}"
REPORT_ID="${3:-1104}"
START_YEAR="${4:-2000}"
END_YEAR="${5:-2026}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw/mongolbank"
DERIVED_DIR="$ROOT_DIR/data/derived"
mkdir -p "$RAW_DIR" "$DERIVED_DIR"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

PAYLOAD="$(jq -n \
  --arg report_id "$REPORT_ID" \
  --arg indicator_id "$INDICATOR_ID" \
  --arg start_year "$START_YEAR" \
  --arg end_year "$END_YEAR" \
  '{
    id: $report_id,
    parentId: $indicator_id,
    rCheck: 0,
    cycle_data: {
      interval: "3",
      year_start: $start_year,
      mq_start: "1",
      day_start: "1",
      year_end: $end_year,
      mq_end: "12",
      day_end: "1"
    },
    indicators: [$indicator_id]
  }')"

RESPONSE="$(curl -sS -X POST 'https://stat.mongolbank.mn/api/indicator/data?lang=en' \
  -H 'Origin: https://stat.mongolbank.mn' \
  -H 'Referer: https://stat.mongolbank.mn/' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  --data "$PAYLOAD")"

SUCCESS="$(echo "$RESPONSE" | jq -r '.success // false')"
if [ "$SUCCESS" != "true" ]; then
  echo "Error: API call failed." >&2
  echo "$RESPONSE" | jq -r '.result // .'
  exit 1
fi

NAME="$(echo "$RESPONSE" | jq -r '.result.report[0].NAME_T // ""')"
if [ -z "$NAME" ]; then
  echo "Error: no report data returned for indicator $INDICATOR_ID." >&2
  exit 1
fi

if [ -n "$SLUG_IN" ]; then
  SLUG="$SLUG_IN"
else
  SLUG="$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
  if [ -z "$SLUG" ]; then
    SLUG="indicator-${INDICATOR_ID}"
  fi
fi

BASE="bop_${REPORT_ID}_${INDICATOR_ID}_${SLUG}"
RAW_FILE="$RAW_DIR/${BASE}.json"
CSV_FILE="$DERIVED_DIR/${BASE}.csv"
META_FILE="$DERIVED_DIR/${BASE}_meta.json"

echo "$RESPONSE" > "$RAW_FILE"

echo "$RESPONSE" | jq \
  --arg report_id "$REPORT_ID" \
  --arg indicator_id "$INDICATOR_ID" \
  '.result.report[0] | {
    report_id: $report_id,
    indicator_id: $indicator_id,
    name: .NAME_T,
    parent_id: .PARENT_ID_T,
    level: .LEVEL_T
  }' > "$META_FILE"

# Extract time-series columns (keys like '2025-12#2') into long CSV format.
JQ_TMP="$(mktemp)"
cat > "$JQ_TMP" <<'JQ'
def is_period_key: test("^'[0-9]{4}-[0-9]{2}#[0-9]+'$");
def parse_period_key: capture("^'(?<period>[0-9]{4}-[0-9]{2})#(?<release>[0-9]+)'$");

[
  .result.report[0]
  | to_entries[]
  | select(.key | is_period_key)
  | (.key | parse_period_key) as $k
  | {
      period: $k.period,
      release_flag: ($k.release | tonumber),
      value: .value
    }
]
| sort_by(.period, .release_flag)
| ["period","release_flag","value"], (.[] | [.period, (.release_flag|tostring), (.value|tostring)])
| @csv
JQ

echo "$RESPONSE" | jq -r -f "$JQ_TMP" > "$CSV_FILE"
rm -f "$JQ_TMP"

echo "Saved:"
echo "- $RAW_FILE"
echo "- $META_FILE"
echo "- $CSV_FILE"
