#!/usr/bin/env python3
"""Publish (or republish) a Datawrapper chart, then save the responsive
embed snippet to the registry.

    python dw_publish.py --slug fuel-shortage--gasoline-imports
    python dw_publish.py --id oJpU6

Republishing is idempotent at the chart-ID level — the chart ID stays,
but ``publicVersion`` increments. The versionless URL
``https://datawrapper.dwcdn.net/{id}/`` always redirects to the latest
version, so links in published posts keep working.

Prints the responsive iframe + script snippet to stdout — paste this into
an ``.mdx`` post for an interactive embed. (For ``.md`` posts, use
``dw_export.py`` and embed the PNG.)  See ``references/embeds.md``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _client
import _registry


def _responsive_embed(chart_id: str, public_url: str | None, title: str) -> str:
    """Build the responsive iframe + auto-resize script snippet.

    Datawrapper's standard embed lives at ``//datawrapper.dwcdn.net/{id}/``
    (versionless — always redirects to latest published). The accompanying
    script listens for postMessages from the iframe and resizes it.
    """
    if public_url:
        # publicUrl looks like https://datawrapper.dwcdn.net/oJpU6/2/.
        # Strip the version segment so the embed always points at the latest.
        src = public_url.rstrip("/").rsplit("/", 1)[0] + "/"
    else:
        src = f"https://datawrapper.dwcdn.net/{chart_id}/"
    safe_title = title.replace('"', "&quot;")
    return (
        f'<iframe title="{safe_title}" aria-label="chart" '
        f'id="datawrapper-chart-{chart_id}" '
        f'src="{src}" scrolling="no" frameborder="0" '
        f'style="width: 0; min-width: 100% !important; border: none;" height="450">'
        f"</iframe>\n"
        f'<script type="text/javascript">'
        f'!function(){{"use strict";window.addEventListener("message",(function(a){{if(void 0!==a.data["datawrapper-height"])'
        f'{{var e=document.querySelectorAll("iframe");for(var t in a.data["datawrapper-height"])'
        f'for(var r,i=0;r=e[i];i++)if(r.contentWindow===a.source)'
        f'{{var d=a.data["datawrapper-height"][t]+"px";r.style.height=d}}}}}}))}}();'
        f'</script>'
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Publish or republish a Datawrapper chart.")
    p.add_argument("--slug", help="Slug from the registry.")
    p.add_argument("--id", dest="chart_id", help="Datawrapper chart ID.")
    args = p.parse_args()

    if args.slug and args.chart_id:
        raise SystemExit("Pass --slug OR --id, not both.")
    slug = args.slug
    chart_id = args.chart_id
    title = ""
    if slug:
        entry = _registry.get(slug)
        if not entry:
            raise SystemExit(f"No registry entry for slug {slug!r}.")
        chart_id = entry["id"]
        title = entry.get("title", "")
    if not chart_id:
        raise SystemExit("Pass either --slug or --id.")

    resp = _client.publish(chart_id)
    data = resp.get("data", resp)
    public_url = data.get("publicUrl")
    version = data.get("publicVersion")
    published_at = data.get("publishedAt")

    if not title:
        try:
            title = _client.get_chart(chart_id).get("title", "")
        except Exception:
            title = "chart"

    embed_iframe = _responsive_embed(chart_id, public_url, title)

    print(f"Published {chart_id} v{version}")
    print(f"URL: {public_url}")
    stable = public_url.rstrip("/").rsplit("/", 1)[0] + "/" if public_url else None
    if stable:
        print(f"Stable URL (latest version): {stable}")
    print()
    print("Responsive embed (paste into an .mdx post):")
    print(embed_iframe)

    if slug or _registry.get_by_id(chart_id):
        target_slug = slug or _registry.get_by_id(chart_id)[0]
        _registry.upsert(
            target_slug,
            {
                "public_url": public_url,
                "public_version": version,
                "published_at": published_at,
                "embed_iframe": embed_iframe,
            },
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
