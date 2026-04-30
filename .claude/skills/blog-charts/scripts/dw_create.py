#!/usr/bin/env python3
"""Create a new Datawrapper chart from a CSV file, registered under a slug.

    python dw_create.py --slug fuel-shortage--gasoline-imports --type d3-lines \\
        --csv ./data/imports.csv \\
        --title "Mongolia's gasoline imports halved in two years" \\
        --intro "Monthly volume, January 2022 – March 2026." \\
        --source-name "National Statistics Office of Mongolia" \\
        --source-url "https://www.1212.mn/"

Refuses to run if ``--slug`` is already in the registry. Pass ``--replace``
to delete the existing chart and recreate it under the same slug.

Convention: blog slugs are namespaced ``<post-slug>--<chart-name>`` so charts
stay traceable to their post.

The registry is at ``~/.cache/blog-charts/registry.json``. Use ``dw_list.py``
to see current entries and ``dw_update.py`` to push new data to a slug.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client
import _registry
import _style


def main() -> int:
    p = argparse.ArgumentParser(
        description="Create a new Datawrapper chart from a CSV.",
        epilog="Chart types: d3-lines, d3-area, column-chart, stacked-column-chart, "
        "grouped-column-chart, d3-bars, d3-bars-stacked, d3-scatter-plot, etc. "
        "See references/chart-types.md.",
    )
    p.add_argument("--slug", required=True, help="Short kebab-case identifier (1-81 chars). Convention: <post-slug>--<chart-name>.")
    p.add_argument("--type", dest="chart_type", required=True, help="Datawrapper chart type ID.")
    p.add_argument("--csv", required=True, type=Path, help="Path to CSV data file.")
    p.add_argument("--title", required=True, help="Chart title (the finding, not the topic).")
    p.add_argument("--intro", default="", help="Short description under the title (unit, time frame).")
    p.add_argument("--source-name", default="", help="Data source name (e.g. 'National Statistics Office of Mongolia').")
    p.add_argument("--source-url", default="", help="Data source URL.")
    p.add_argument("--notes", default="", help="Footer notes (methodology, caveats).")
    p.add_argument("--byline", default=_style.BLOG_BYLINE, help="Byline (default: Robert Ritz).")
    p.add_argument(
        "--series-label",
        action="append",
        default=[],
        metavar="COL=LABEL",
        help=(
            "Rename a CSV column in the chart's legend. Repeatable. "
            "Example: --series-label value='Gasoline imports'."
        ),
    )
    p.add_argument("--number-format", help="Datawrapper number format (e.g. '0.0', '0,0').")
    p.add_argument("--number-append", help="Text appended to every number (e.g. '%').")
    p.add_argument("--number-prepend", help="Text prepended to every number (e.g. '$').")
    p.add_argument(
        "--series-color",
        action="append",
        default=[],
        metavar="SERIES=#hex",
        help="Pin a specific color to a series. Repeatable. Example: --series-color 'Gasoline=#2b5cd6'.",
    )
    p.add_argument(
        "--annotate-text",
        action="append",
        default=[],
        metavar="X|Y|TEXT",
        help=(
            "Add a text annotation. Pipe-separated fields. Repeatable. "
            "Example: --annotate-text '2024-03|145000|Peak imports'. "
            "Optional 4th/5th fields: color and size."
        ),
    )
    p.add_argument(
        "--annotate-range",
        action="append",
        default=[],
        metavar="X0|X1|TEXT",
        help=(
            "Add a shaded range annotation (recession bar, policy window). "
            "Repeatable. TEXT can be empty. Example: "
            "--annotate-range '2022-02-24|2022-12-31|Russia invades Ukraine'."
        ),
    )
    p.add_argument("--folder-id", type=int, default=None, help="Datawrapper folder ID.")
    p.add_argument("--replace", action="store_true", help="Delete existing chart and recreate.")
    args = p.parse_args()

    if not _registry.is_valid_slug(args.slug):
        raise SystemExit(
            f"Invalid slug {args.slug!r}. Use lowercase letters, digits, "
            f"hyphens, underscores (1-81 chars)."
        )
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    existing = _registry.get(args.slug)
    if existing:
        if not args.replace:
            raise SystemExit(
                f"slug {args.slug!r} already maps to chart {existing['id']} "
                f"(created {existing.get('created_at', '?')}). "
                f"Use dw_update.py to push new data, or pass --replace to delete & recreate."
            )
        try:
            _client.delete_chart(existing["id"])
            print(f"[create] deleted existing chart {existing['id']}", file=sys.stderr)
        except RuntimeError as e:
            print(f"[create] WARN: delete failed ({e}); continuing", file=sys.stderr)
        _registry.remove(args.slug)

    csv_bytes = args.csv.read_bytes()

    # 1. Create (POST).
    chart = _client.create_chart(args.title, args.chart_type, folder_id=args.folder_id)
    chart_id = chart["id"]
    print(f"[create] {chart_id}: created as {args.chart_type}", file=sys.stderr)

    # 2. Upload CSV (PUT /data).
    _client.upload_data(chart_id, csv_bytes)
    print(f"[create] {chart_id}: uploaded {len(csv_bytes)} bytes of data", file=sys.stderr)

    # 3. Style (PATCH).
    try:
        series_labels = _style.parse_series_labels(args.series_label)
        series_colors = _style.parse_series_colors(args.series_color)
        text_annotations = [_style.parse_text_annotation(a) for a in args.annotate_text]
        range_annotations = [_style.parse_range_annotation(a) for a in args.annotate_range]
    except ValueError as e:
        raise SystemExit(str(e))
    patch = _style.style_for(
        args.chart_type,
        title=args.title,
        intro=args.intro or None,
        source_name=args.source_name or None,
        source_url=args.source_url or None,
        notes=args.notes or None,
        byline=args.byline,
        series_labels=series_labels,
        series_colors=series_colors or None,
        text_annotations=text_annotations or None,
        range_annotations=range_annotations or None,
        number_format=args.number_format,
        number_append=args.number_append,
        number_prepend=args.number_prepend,
    )
    _client.update_metadata(chart_id, patch)
    print(f"[create] {chart_id}: applied blog styling", file=sys.stderr)

    # 4. Register.
    _registry.upsert(
        args.slug,
        {
            "id": chart_id,
            "title": args.title,
            "type": args.chart_type,
            "source_csv": str(args.csv.resolve()),
            "source_name": args.source_name,
            "source_url": args.source_url,
            "intro": args.intro,
            "notes": args.notes,
        },
    )
    edit_url = f"https://app.datawrapper.de/chart/{chart_id}/visualize"
    print(
        f"[create] {chart_id}: registered as slug {args.slug!r}\n"
        f"         edit:    {edit_url}\n"
        f"         preview: https://datawrapper.dwcdn.net/{chart_id}/ (after publish)\n"
        f"         Next: dw_export.py --slug {args.slug} --out ./preview.png "
        f"to visually check before publishing.",
        file=sys.stderr,
    )
    print(chart_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
