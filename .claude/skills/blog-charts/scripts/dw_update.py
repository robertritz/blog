#!/usr/bin/env python3
"""Update data and/or metadata on an existing Datawrapper chart.

Typical refresh (data only)::

    python dw_update.py --slug fuel-shortage--gasoline-imports --csv ./data/imports.csv --publish

Change title or notes without pushing new data::

    python dw_update.py --slug fuel-shortage--gasoline-imports --notes "Last updated 2026-04-30" --publish

Both identifiers work — ``--slug`` (preferred) or ``--id <chart_id>`` for a
chart that was created outside this tool. When ``--id`` is used, the
registry is left untouched.

The ``--publish`` flag triggers a republish after the update so the public
embed URL reflects the new data. Without it, the draft changes but the
public URL still shows the old version.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client
import _registry
import _style


def _resolve(slug: str | None, chart_id: str | None) -> tuple[str, dict | None]:
    if slug and chart_id:
        raise SystemExit("Pass --slug OR --id, not both.")
    if slug:
        entry = _registry.get(slug)
        if not entry:
            raise SystemExit(f"No registry entry for slug {slug!r}. Use dw_list.py to see slugs.")
        return entry["id"], entry
    if chart_id:
        hit = _registry.get_by_id(chart_id)
        return chart_id, (hit[1] if hit else None)
    raise SystemExit("Pass either --slug or --id.")


def main() -> int:
    p = argparse.ArgumentParser(description="Update data or metadata on an existing chart.")
    p.add_argument("--slug", help="Slug from the registry.")
    p.add_argument("--id", dest="chart_id", help="Datawrapper chart ID (for charts not in the registry).")
    p.add_argument("--csv", type=Path, help="New CSV to push as chart data.")
    p.add_argument("--title", help="Change the chart title.")
    p.add_argument("--intro", help="Change the intro.")
    p.add_argument("--source-name", help="Change source name.")
    p.add_argument("--source-url", help="Change source URL.")
    p.add_argument("--notes", help="Change footer notes.")
    p.add_argument(
        "--series-label",
        action="append",
        default=[],
        metavar="COL=LABEL",
        help="Rename a CSV column in the chart's legend. Repeatable.",
    )
    p.add_argument(
        "--series-color",
        action="append",
        default=[],
        metavar="SERIES=#hex",
        help="Pin a specific color to a series. Repeatable.",
    )
    p.add_argument(
        "--annotate-text",
        action="append",
        default=[],
        metavar="X|Y|TEXT",
        help="Replace text annotations. Pipe-separated. Repeatable. Pass once with no value to clear.",
    )
    p.add_argument(
        "--annotate-range",
        action="append",
        default=[],
        metavar="X0|X1|TEXT",
        help="Replace range annotations. Pipe-separated. Repeatable. TEXT can be empty.",
    )
    p.add_argument("--clear-annotations", action="store_true", help="Remove all annotations.")
    p.add_argument("--number-format", help="Datawrapper number format (e.g. '0.0').")
    p.add_argument("--number-append", help="Text appended to every number (e.g. '%').")
    p.add_argument("--number-prepend", help="Text prepended to every number (e.g. '$').")
    p.add_argument("--publish", action="store_true", help="Republish after update.")
    p.add_argument("--restyle", action="store_true", help="Re-apply blog styling defaults (overwrites visualize settings).")
    args = p.parse_args()

    chart_id, entry = _resolve(args.slug, args.chart_id)
    touched = False

    if args.csv:
        if not args.csv.exists():
            raise SystemExit(f"CSV not found: {args.csv}")
        csv_bytes = args.csv.read_bytes()
        _client.upload_data(chart_id, csv_bytes)
        print(f"[update] {chart_id}: uploaded {len(csv_bytes)} bytes of data", file=sys.stderr)
        touched = True

    try:
        series_labels = _style.parse_series_labels(args.series_label)
        series_colors = _style.parse_series_colors(args.series_color)
        text_annotations = [_style.parse_text_annotation(a) for a in args.annotate_text]
        range_annotations = [_style.parse_range_annotation(a) for a in args.annotate_range]
    except ValueError as e:
        raise SystemExit(str(e))

    metadata_patch_args = {
        "title": args.title,
        "intro": args.intro,
        "source_name": args.source_name,
        "source_url": args.source_url,
        "notes": args.notes,
    }
    has_metadata = (
        any(v is not None for v in metadata_patch_args.values())
        or bool(series_labels)
        or bool(series_colors)
        or bool(text_annotations)
        or bool(range_annotations)
        or args.clear_annotations
        or args.number_format is not None
        or args.number_append is not None
        or args.number_prepend is not None
    )

    if has_metadata or args.restyle:
        chart_type = (entry or {}).get("type")
        if not chart_type:
            fresh = _client.get_chart(chart_id)
            chart_type = fresh.get("type", "d3-lines")

        if args.restyle:
            patch = _style.style_for(
                chart_type,
                title=args.title,
                intro=args.intro,
                source_name=args.source_name,
                source_url=args.source_url,
                notes=args.notes,
                series_labels=series_labels or None,
                series_colors=series_colors or None,
                text_annotations=text_annotations or None,
                range_annotations=range_annotations or None,
                number_format=args.number_format,
                number_append=args.number_append,
                number_prepend=args.number_prepend,
            )
        else:
            describe: dict = {}
            annotate: dict = {}
            visualize: dict = {}
            if args.intro is not None:
                describe["intro"] = args.intro
            if args.source_name is not None:
                describe["source-name"] = args.source_name
            if args.source_url is not None:
                describe["source-url"] = args.source_url
            if args.number_format is not None:
                describe["number-format"] = args.number_format
            if args.number_append is not None:
                describe["number-append"] = args.number_append
            if args.number_prepend is not None:
                describe["number-prepend"] = args.number_prepend
            if args.notes is not None:
                annotate["notes"] = args.notes
            if series_labels:
                visualize["lines"] = {
                    col: {"title": label} for col, label in series_labels.items()
                }
            if series_colors:
                visualize["custom-colors"] = series_colors
            if text_annotations or args.clear_annotations:
                visualize["text-annotations"] = text_annotations
            if range_annotations or args.clear_annotations:
                visualize["range-annotations"] = range_annotations
            metadata: dict = {}
            if describe:
                metadata["describe"] = describe
            if annotate:
                metadata["annotate"] = annotate
            if visualize:
                metadata["visualize"] = visualize
            patch = {}
            if args.title is not None:
                patch["title"] = args.title
            if metadata:
                patch["metadata"] = metadata

        if patch:
            _client.update_metadata(chart_id, patch)
            print(f"[update] {chart_id}: patched metadata", file=sys.stderr)
            touched = True

    if not touched:
        raise SystemExit(
            "Nothing to update. Pass --csv, --title, --intro, --notes, --source-name, "
            "--source-url, or --restyle."
        )

    public_url = None
    version = None
    if args.publish:
        resp = _client.publish(chart_id)
        data = resp.get("data", resp)
        public_url = data.get("publicUrl")
        version = data.get("publicVersion")
        print(f"[update] {chart_id}: published v{version} → {public_url}", file=sys.stderr)

    if args.slug or (entry is not None):
        slug = args.slug
        if slug is None:
            hit = _registry.get_by_id(chart_id)
            slug = hit[0] if hit else None
        if slug is not None:
            updates = {}
            if args.csv:
                updates["source_csv"] = str(args.csv.resolve())
            if args.title is not None:
                updates["title"] = args.title
            if args.intro is not None:
                updates["intro"] = args.intro
            if args.source_name is not None:
                updates["source_name"] = args.source_name
            if args.source_url is not None:
                updates["source_url"] = args.source_url
            if args.notes is not None:
                updates["notes"] = args.notes
            if public_url:
                updates["public_url"] = public_url
                updates["public_version"] = version
            if updates:
                _registry.upsert(slug, updates)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
