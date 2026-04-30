# The Slug Registry

A local JSON file that maps human-readable slugs to Datawrapper chart IDs.
Without it, a second `POST /v3/charts` with the same title creates a
duplicate chart.

## Location

`~/.cache/blog-charts/registry.json` (override with `BLOG_CHARTS_CACHE`
env var if needed).

## Slug naming convention

`<post-slug>--<chart-name>` — keeps charts traceable to their post.

Examples:

- `fuel-shortage--gasoline-imports`
- `mongolian-meat-prices--annual-trend`
- `usd-mnt-forecast--scenario-grid`

Constraints (enforced by `_registry.is_valid_slug`):

- Lowercase letters, digits, hyphens, underscores
- Starts with alphanumeric
- 1-81 chars

## Schema

```json
{
  "version": 1,
  "charts": {
    "<slug>": {
      "id": "oJpU6",
      "title": "...",
      "type": "d3-lines",
      "created_at": "2026-04-30T06:22:03Z",
      "updated_at": "2026-04-30T07:10:00Z",
      "published_at": "...",
      "public_url": "https://datawrapper.dwcdn.net/oJpU6/1/",
      "public_version": 1,
      "embed_iframe": "<iframe ...>...</iframe><script>...</script>",
      "source_csv": "/abs/path/to/data.csv",
      "source_name": "...",
      "source_url": "...",
      "intro": "...",
      "notes": "..."
    }
  }
}
```

## Authority

The registry is **advisory**. The chart on Datawrapper is authoritative.
If a registry entry points to a chart that 404s on Datawrapper, run:

```bash
python .claude/skills/blog-charts/scripts/dw_list.py --sync
```

This walks every entry, hits `GET /v3/charts/{id}`, and removes any
entries whose chart no longer exists.

## Recovery patterns

### "I created a chart in the web UI; how do I register it?"

You can't `dw_create.py` it (the chart already exists). Workaround:
operate by `--id`. Every script accepts `--id <chart_id>` as a fallback.
The registry will pick up the chart on the next `dw_publish.py --slug
<slug>` if you also pass `--slug` to register it for future ops.

Manual approach: edit `~/.cache/blog-charts/registry.json` and add an
entry by hand:

```json
{
  "<slug>": {
    "id": "<chart_id_from_web_ui>",
    "title": "...",
    "type": "d3-lines"
  }
}
```

Then `dw_publish.py --slug <slug>` will fill in the rest.

### "I deleted a chart on Datawrapper; the registry is stale."

```bash
python .claude/skills/blog-charts/scripts/dw_list.py --sync
```

### "I want to start fresh."

```bash
rm ~/.cache/blog-charts/registry.json
```

The charts on Datawrapper survive; only the local mapping is gone. Walk
them again with:

```bash
python .claude/skills/blog-charts/scripts/dw_list.py --remote
```

## Cross-machine note

The registry is local. If you sync the blog repo across machines (Robert
does — Mac at home, Mac at the office), each machine builds its own
registry as you run `dw_create.py` from there. Charts are still on
Datawrapper either way; the registry just speeds up the workflow.

If you need to share registry state between machines, the simplest fix
is to commit `~/.cache/blog-charts/registry.json` somewhere (not in the
blog repo). Or run `dw_list.py --remote --json > registry-snapshot.json`
on one machine and reconstruct on the other.
