#!/usr/bin/env python3
"""Delete a Datawrapper chart and (if present) remove it from the registry.

    python dw_delete.py --slug old-chart
    python dw_delete.py --id oJpU6 --force

Deletes on Datawrapper are immediate and not recoverable. This script asks
for confirmation by default; ``--force`` skips the prompt.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client
import _registry


def main() -> int:
    p = argparse.ArgumentParser(description="Delete a Datawrapper chart.")
    p.add_argument("--slug", help="Slug from the registry.")
    p.add_argument("--id", dest="chart_id", help="Datawrapper chart ID.")
    p.add_argument("--force", action="store_true", help="Skip confirmation prompt.")
    args = p.parse_args()

    if args.slug and args.chart_id:
        raise SystemExit("Pass --slug OR --id, not both.")

    slug = args.slug
    chart_id = args.chart_id
    if slug:
        entry = _registry.get(slug)
        if not entry:
            raise SystemExit(f"No registry entry for slug {slug!r}.")
        chart_id = entry["id"]
    elif chart_id:
        hit = _registry.get_by_id(chart_id)
        slug = hit[0] if hit else None
    else:
        raise SystemExit("Pass either --slug or --id.")

    if not args.force:
        try:
            chart = _client.get_chart(chart_id)
            title = chart.get("title", "(untitled)")
        except (KeyError, RuntimeError):
            title = "(not found on Datawrapper)"
        label = f"slug={slug!r}, " if slug else ""
        prompt = f"Delete chart {chart_id} ({label}title={title!r})? [y/N] "
        try:
            ans = input(prompt).strip().lower()
        except EOFError:
            ans = ""
        if ans not in ("y", "yes"):
            print("Aborted.", file=sys.stderr)
            return 1

    try:
        _client.delete_chart(chart_id)
        print(f"[delete] {chart_id}: deleted from Datawrapper")
    except RuntimeError as e:
        print(f"[delete] {chart_id}: {e}", file=sys.stderr)
        return 2

    if slug:
        _registry.remove(slug)
        print(f"[delete] {chart_id}: removed slug {slug!r} from registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
