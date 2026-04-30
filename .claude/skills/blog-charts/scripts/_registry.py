"""Local registry mapping human slugs to Datawrapper chart IDs.

Why this exists: Datawrapper's API has no native idempotency. A second POST
to /v3/charts with the same title creates a second chart. The fix is a
caller-side slug → chart_id mapping. Each create call takes a ``--slug``
(short, kebab-case, chosen by the writer). The registry stores it.
Subsequent calls with the same slug update the existing chart instead of
creating a duplicate.

For the blog, slugs are conventionally namespaced by post:
``<post-slug>--<chart-name>`` (e.g. ``fuel-shortage--gasoline-imports``)
so charts stay traceable to their posts. The registry doesn't enforce
this — it's a writer convention.

File: ``~/.cache/blog-charts/registry.json``

Schema::

    {
      "version": 1,
      "charts": {
        "<slug>": {
          "id": "oJpU6",
          "title": "...",
          "type": "d3-lines",
          "created_at": "2026-04-30T06:22:03Z",
          "updated_at": "2026-04-30T07:10:00Z",
          "published_at": "...",          # None if never published
          "public_url": "https://datawrapper.dwcdn.net/oJpU6/1/",
          "public_version": 1,
          "embed_iframe": "<iframe ...>...</iframe><script ...>...</script>",
          "source_csv": "/abs/path/to/data.csv",
          "notes": "..."
        },
        ...
      }
    }

The registry is ADVISORY — the chart on Datawrapper is authoritative.
If a registry entry points to a chart_id that 404s, ``sync`` removes it.
"""

from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_ROOT = Path(os.environ.get(
    "BLOG_CHARTS_CACHE",
    str(Path.home() / ".cache" / "blog-charts"),
))
REGISTRY_FILE = REGISTRY_ROOT / "registry.json"
SCHEMA_VERSION = 1

_lock = threading.Lock()
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-_]{0,80}$")


def is_valid_slug(s: str) -> bool:
    return bool(_SLUG_RE.match(s))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load() -> dict:
    if not REGISTRY_FILE.exists():
        return {"version": SCHEMA_VERSION, "charts": {}}
    try:
        data = json.loads(REGISTRY_FILE.read_text())
    except json.JSONDecodeError:
        return {"version": SCHEMA_VERSION, "charts": {}}
    data.setdefault("version", SCHEMA_VERSION)
    data.setdefault("charts", {})
    return data


def _save(data: dict) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True))
    tmp.replace(REGISTRY_FILE)


def get(slug: str) -> dict | None:
    with _lock:
        return _load()["charts"].get(slug)


def get_by_id(chart_id: str) -> tuple[str, dict] | None:
    with _lock:
        for slug, entry in _load()["charts"].items():
            if entry.get("id") == chart_id:
                return slug, entry
    return None


def all_entries() -> dict:
    with _lock:
        return _load()["charts"]


def upsert(slug: str, entry_updates: dict) -> dict:
    """Merge ``entry_updates`` into the entry at ``slug`` and persist."""
    if not is_valid_slug(slug):
        raise ValueError(
            f"invalid slug {slug!r}: use lowercase letters, digits, hyphens, "
            f"underscores (1-81 chars, starting alphanumeric)"
        )
    with _lock:
        data = _load()
        existing = data["charts"].get(slug, {})
        merged = {**existing, **entry_updates}
        if "created_at" not in merged:
            merged["created_at"] = _now()
        merged["updated_at"] = _now()
        data["charts"][slug] = merged
        _save(data)
        return merged


def remove(slug: str) -> bool:
    with _lock:
        data = _load()
        if slug in data["charts"]:
            del data["charts"][slug]
            _save(data)
            return True
    return False


def registry_path() -> Path:
    return REGISTRY_FILE
