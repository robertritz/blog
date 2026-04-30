#!/usr/bin/env python3
"""Show details for a chart: registry entry + live metadata from Datawrapper.

    python dw_get.py --slug fuel-shortage--gasoline-imports
    python dw_get.py --id oJpU6
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client
import _registry


def main() -> int:
    p = argparse.ArgumentParser(description="Show chart details.")
    p.add_argument("--slug", help="Slug from the registry.")
    p.add_argument("--id", dest="chart_id", help="Datawrapper chart ID.")
    p.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON.")
    p.add_argument(
        "--summary",
        action="store_true",
        help="Show a structured snapshot of styling and annotations (palette, ranges, callouts).",
    )
    args = p.parse_args()

    if args.slug and args.chart_id:
        raise SystemExit("Pass --slug OR --id, not both.")
    slug = args.slug
    chart_id = args.chart_id
    entry = None
    if slug:
        entry = _registry.get(slug)
        if not entry:
            raise SystemExit(f"No registry entry for slug {slug!r}.")
        chart_id = entry["id"]
    elif chart_id:
        hit = _registry.get_by_id(chart_id)
        entry = hit[1] if hit else None
        slug = hit[0] if hit else None
    else:
        raise SystemExit("Pass either --slug or --id.")

    try:
        chart = _client.get_chart(chart_id)
    except KeyError:
        print(f"Chart {chart_id} not found on Datawrapper.", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps({"slug": slug, "registry": entry, "chart": chart}, indent=2))
        return 0

    md = chart.get("metadata", {})
    d = md.get("describe", {})
    a = md.get("annotate", {})
    v = md.get("visualize", {})
    print(f"slug:         {slug or '(not registered)'}")
    print(f"id:           {chart.get('id')}")
    print(f"type:         {chart.get('type')}")
    print(f"title:        {chart.get('title')}")
    print(f"intro:        {d.get('intro','')}")
    print(f"byline:       {d.get('byline','')}")
    print(f"source:       {d.get('source-name','')} {d.get('source-url','')}")
    print(f"notes:        {a.get('notes','')}")
    print(f"created:      {chart.get('createdAt')}")
    print(f"last modified:{chart.get('lastModifiedAt')}")
    print(f"published at: {chart.get('publishedAt')}")
    print(f"public URL:   {chart.get('publicUrl')}")
    print(f"editor URL:   https://app.datawrapper.de/chart/{chart.get('id')}/edit")

    if args.summary:
        print()
        print("--- styling snapshot ---")
        print(f"base-color:    {v.get('base-color','(default)')}")
        custom_colors = v.get("custom-colors") or {}
        if custom_colors:
            print("custom-colors:")
            for series, color in custom_colors.items():
                print(f"  {series}: {color}")
        else:
            print("custom-colors: (none — using palette in series order)")
        lines = v.get("lines") or {}
        if lines:
            print("series-labels:")
            for col, cfg in lines.items():
                title = cfg.get("title", col) if isinstance(cfg, dict) else cfg
                print(f"  {col}: {title}")
        y_grid = v.get("y-grid", "(default)")
        x_grid = v.get("x-grid", "(default)")
        print(f"gridlines:     y={y_grid} x={x_grid}")
        custom_range = v.get("custom-range-y")
        if custom_range and any(custom_range):
            print(f"y-range:       {custom_range}")
        n_format = d.get("number-format", "(default)")
        n_pre = d.get("number-prepend", "")
        n_app = d.get("number-append", "")
        print(f"numbers:       format={n_format!r} prepend={n_pre!r} append={n_app!r}")
        text_anns = v.get("text-annotations") or []
        range_anns = v.get("range-annotations") or []
        print(f"annotations:   {len(text_anns)} text, {len(range_anns)} range")
        for i, ann in enumerate(text_anns):
            print(f"  text[{i}]:  x={ann.get('x')!r} y={ann.get('y')!r} text={ann.get('text','')!r}")
        for i, ann in enumerate(range_anns):
            print(f"  range[{i}]: x0={ann.get('x0')!r} x1={ann.get('x1')!r} text={ann.get('text','')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
