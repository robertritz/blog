#!/usr/bin/env python3
"""Export a Datawrapper chart as PNG.

    python dw_export.py --slug fuel-shortage--gasoline-imports --out ./preview.png
    python dw_export.py --id oJpU6 --out /tmp/chart.png --zoom 2 --plain

Works on draft AND published charts. This is how Claude visually verifies
a chart before publishing — the resulting PNG is readable by the Read tool
and small enough to inline into the context.

Default zoom is 2 (retina-sharp ~1600 x 1066 px for the 680 x 440 embed).
Use ``--plain`` to drop the title / description / footer and export only
the chart body — useful when the surrounding markdown already carries the
caption.

PDF and SVG exports require Datawrapper's Custom plan; PNG is free.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client
import _registry


def main() -> int:
    p = argparse.ArgumentParser(description="Export a Datawrapper chart as PNG.")
    p.add_argument("--slug", help="Slug from the registry.")
    p.add_argument("--id", dest="chart_id", help="Datawrapper chart ID.")
    p.add_argument("--out", required=True, type=Path, help="Output PNG path.")
    p.add_argument("--zoom", type=int, default=2, help="Export zoom (default 2 = retina).")
    p.add_argument("--plain", action="store_true", help="Chart body only — no title/description/footer.")
    p.add_argument("--width", type=int, help="Override width in px.")
    p.add_argument("--height", type=int, help="Override height in px.")
    p.add_argument("--border-width", type=int, default=20, help="Padding around chart (px).")
    p.add_argument("--transparent", action="store_true", help="Transparent background.")
    args = p.parse_args()

    if args.slug and args.chart_id:
        raise SystemExit("Pass --slug OR --id, not both.")
    chart_id = args.chart_id
    if args.slug:
        entry = _registry.get(args.slug)
        if not entry:
            raise SystemExit(f"No registry entry for slug {args.slug!r}.")
        chart_id = entry["id"]
    if not chart_id:
        raise SystemExit("Pass either --slug or --id.")

    png_bytes = _client.export_png(
        chart_id,
        zoom=args.zoom,
        plain=args.plain,
        border_width=args.border_width,
        width=args.width,
        height=args.height,
        transparent=args.transparent,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(png_bytes)
    print(f"[export] {chart_id}: {len(png_bytes)} bytes → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
