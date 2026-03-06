#!/usr/bin/env python3
"""Log latest NSO API `updated` timestamps for key tables.

This builds release-history prospectively (from now onward), since NSO API does not
expose a full retroactive release log.
"""

from datetime import datetime, timezone
from pathlib import Path
import csv
import requests
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "nso_release_updates_log.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

BASE = "https://data.1212.mn/api/v1/en/NSO"

# Table map: table_id -> (sector, subsector)
TABLES = {
    "DT_NSO_0600_010V1.px": ("Economy, environment", "Consumer Price Index"),
    "DT_NSO_0600_009V1.px": ("Economy, environment", "Consumer Price Index"),
    "DT_NSO_1400_003V1.px": ("Economy, environment", "Foreign Trade"),
    "DT_NSO_1100_001V2.px": ("Industry, service", "Industry"),
    "DT_NSO_1100_015V3_1.px": ("Economy, environment", "Foreign Trade"),
}


def get_updated(table_id: str, sector: str, subsector: str) -> str:
    url = f"{BASE}/{quote(sector)}/{quote(subsector)}/"
    data = requests.get(url, timeout=30).json()
    for row in data:
        if row.get("id") == table_id:
            return row.get("updated", "")
    return ""


def main() -> None:
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for table_id, (sector, subsector) in TABLES.items():
        updated = get_updated(table_id, sector, subsector)
        rows.append(
            {
                "captured_at_utc": captured_at,
                "table_id": table_id,
                "sector": sector,
                "subsector": subsector,
                "api_updated": updated,
            }
        )

    write_header = not OUT.exists()
    with OUT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "captured_at_utc",
                "table_id",
                "sector",
                "subsector",
                "api_updated",
            ],
        )
        if write_header:
            w.writeheader()
        w.writerows(rows)

    print(f"Logged {len(rows)} table update snapshots to {OUT}")


if __name__ == "__main__":
    main()
