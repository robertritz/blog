#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="$ROOT_DIR/tools"
LOG_PREFIX="[tugrik-refresh]"

run() {
  echo "$LOG_PREFIX $*"
  "$@"
}

run bash "$TOOLS_DIR/fetch_mongolbank_basics.sh"
run bash "$TOOLS_DIR/fetch_bop_indicator.sh" 121832 current-account 1104 2000 2026
run bash "$TOOLS_DIR/fetch_bop_indicator.sh" 122137 financial-account 1104 2000 2026
run bash "$TOOLS_DIR/fetch_bop_indicator.sh" 122347 reserve-assets 1104 2000 2026
run bash "$TOOLS_DIR/fetch_bop_indicator.sh" 122364 net-errors-omissions 1104 2000 2026

if [ -f "$TOOLS_DIR/fetch_nso_core.sh" ]; then
  run bash "$TOOLS_DIR/fetch_nso_core.sh"
fi

run python3 "$TOOLS_DIR/extract_nso_core.py"
run python3 "$TOOLS_DIR/fetch_global_factors.py"
run python3 "$TOOLS_DIR/build_feature_panels.py"
run python3 "$TOOLS_DIR/run_forecast_study.py"
run python3 "$TOOLS_DIR/export_tugrik_dashboard.py" --skip-if-unchanged
