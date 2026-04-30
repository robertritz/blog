#!/usr/bin/env python3
"""List Datawrapper charts.

    python dw_list.py                 # registered slugs, with their IDs
    python dw_list.py --remote        # every chart on your Datawrapper account
    python dw_list.py --sync          # reconcile registry with remote (removes stale entries)

By default, lists the local slug → chart mapping. The ``--remote`` view is
ground truth — use it when the registry gets out of sync (e.g., a chart
was deleted from Datawrapper's web UI).
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
    p = argparse.ArgumentParser(description="List Datawrapper charts.")
    p.add_argument("--remote", action="store_true", help="Query Datawrapper instead of local registry.")
    p.add_argument("--sync", action="store_true", help="Drop registry entries whose charts no longer exist.")
    p.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")
    p.add_argument("--limit", type=int, default=100, help="Max remote results.")
    args = p.parse_args()

    if args.sync:
        removed = []
        for slug, entry in list(_registry.all_entries().items()):
            try:
                _client.get_chart(entry["id"])
            except KeyError:
                _registry.remove(slug)
                removed.append((slug, entry["id"]))
        print(f"[list] sync: removed {len(removed)} stale entries", file=sys.stderr)
        for slug, cid in removed:
            print(f"  {slug} → {cid} (gone)", file=sys.stderr)

    if args.remote:
        charts = _client.list_charts(limit=args.limit)
        if args.as_json:
            print(json.dumps(charts, indent=2))
            return 0
        print(f"{'ID':8s} {'TYPE':20s} {'PUB':4s} {'TITLE':40s}")
        for c in charts:
            pub = "Y" if c.get("publishedAt") else " "
            print(f"{c['id']:8s} {c.get('type',''):20s} {pub:4s} {c.get('title','')[:40]}")
        return 0

    entries = _registry.all_entries()
    if args.as_json:
        print(json.dumps(entries, indent=2))
        return 0
    if not entries:
        print("(no registry entries — use dw_create.py to add some)")
        print(f"registry file: {_registry.registry_path()}")
        return 0
    print(f"{'SLUG':40s} {'ID':8s} {'TYPE':20s} {'PUB':4s} TITLE")
    for slug, e in sorted(entries.items()):
        pub = "Y" if e.get("published_at") else " "
        print(f"{slug:40s} {e.get('id',''):8s} {e.get('type',''):20s} {pub:4s} {e.get('title','')[:40]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
