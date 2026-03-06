#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw/mongolbank"
DERIVED_DIR="$ROOT_DIR/data/derived"

mkdir -p "$RAW_DIR" "$DERIVED_DIR"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

post_mongolbank() {
  local url="$1"
  local referer="$2"
  local out="$3"

  curl -sS -X POST "$url" \
    -H 'Origin: https://www.mongolbank.mn' \
    -H "Referer: ${referer}" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    > "$out"
}

post_stat() {
  local url="$1"
  local out="$2"

  curl -sS -X POST "$url" \
    -H 'Origin: https://stat.mongolbank.mn' \
    -H 'Referer: https://stat.mongolbank.mn/' \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    > "$out"
}

echo "Fetching Mongolbank FX and REER/NEER..."
post_mongolbank 'https://www.mongolbank.mn/en/currency-rate-movement/data' \
  'https://www.mongolbank.mn/en/currency-rate-movement' \
  "$RAW_DIR/fx_daily.json"

post_mongolbank 'https://www.mongolbank.mn/en/currency-rate-movement/data/monthly' \
  'https://www.mongolbank.mn/en/currency-rate-movement/monthly' \
  "$RAW_DIR/fx_monthly.json"

post_mongolbank 'https://www.mongolbank.mn/en/neer-reer/data' \
  'https://www.mongolbank.mn/en/neer-reer' \
  "$RAW_DIR/neer_reer.json"

echo "Fetching BoM statistics metadata..."
post_stat 'https://stat.mongolbank.mn/api/report/list?lang=en&parentId=20' \
  "$RAW_DIR/bop_report_list_parent20.json"

post_stat 'https://stat.mongolbank.mn/api/indicator/list?lang=en&reportId=1104' \
  "$RAW_DIR/bop_indicator_list_1104.json"

post_stat 'https://stat.mongolbank.mn/api/indicator/list?lang=en&reportId=1103' \
  "$RAW_DIR/bop_indicator_list_1103.json"

post_stat 'https://stat.mongolbank.mn/api/indicator/list?lang=en&reportId=1125' \
  "$RAW_DIR/international_reserve_indicator_list_1125.json"

post_stat 'https://stat.mongolbank.mn/api/schedule/data?lang=en&startdate=2024-01-01&enddate=2027-12-31' \
  "$RAW_DIR/release_schedule_2024_2027.json"

echo "Building derived CSV files..."

jq -r '
  ["rate_date","usd_mnt"],
  (.data | sort_by(.RATE_DATE)[]
    | [.RATE_DATE, (.USD | if . == "-" then "" else gsub(","; "") end)])
  | @csv
' "$RAW_DIR/fx_daily.json" > "$DERIVED_DIR/usd_mnt_daily.csv"

jq -r '
  ["period","usd_mnt"],
  (.data | sort_by(.RATE_DATE)[]
    | [.RATE_DATE, (.USD | if . == "-" then "" else gsub(","; "") end)])
  | @csv
' "$RAW_DIR/fx_monthly.json" > "$DERIVED_DIR/usd_mnt_monthly.csv"

jq -r '
  ["period","neer","reer"],
  (.data | sort_by(.RATE_DATE)[]
    | [
        .RATE_DATE,
        (.NEER | if . == "-" then "" else gsub(","; "") end),
        (.REER | if . == "-" then "" else gsub(","; "") end)
      ])
  | @csv
' "$RAW_DIR/neer_reer.json" > "$DERIVED_DIR/neer_reer_monthly.csv"

jq -r '
  ["release_date","series_name","data_period"],
  (.result | sort_by(.DATE, .DATA)[] | [.DATE, .NAME, .DATA])
  | @csv
' "$RAW_DIR/release_schedule_2024_2027.json" > "$DERIVED_DIR/release_schedule_2024_2027.csv"

echo "Done."
echo "Raw:     $RAW_DIR"
echo "Derived: $DERIVED_DIR"
