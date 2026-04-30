# Updates and Publishing

## Refresh data on an existing chart

```bash
python .claude/skills/blog-charts/scripts/dw_update.py \
    --slug <slug> \
    --csv ./data/refreshed.csv \
    --publish
```

`--publish` triggers a republish so the public embed URL reflects the
new data. Without `--publish`, the draft updates but the public version
stays the same.

The chart ID stays the same across versions; only `publicVersion`
increments. Embed URLs in posts use the versionless redirect
(`https://datawrapper.dwcdn.net/{id}/`) so they always show the latest.

## Change just the metadata

```bash
# Update title only
python .claude/skills/blog-charts/scripts/dw_update.py \
    --slug <slug> --title "New title" --publish

# Update notes (e.g. add a "Last updated" line)
python .claude/skills/blog-charts/scripts/dw_update.py \
    --slug <slug> --notes "Last updated 2026-04-30." --publish

# Add a series label after the fact
python .claude/skills/blog-charts/scripts/dw_update.py \
    --slug <slug> --series-label 'value=New label' --publish
```

## Reset to blog styling defaults

If you used the Datawrapper web UI to experiment and want to start over:

```bash
python .claude/skills/blog-charts/scripts/dw_update.py \
    --slug <slug> --restyle --publish
```

`--restyle` re-applies the full blog style overlay, overwriting any
custom `visualize` settings.

## Publish without changing anything

```bash
python .claude/skills/blog-charts/scripts/dw_publish.py --slug <slug>
```

Useful when you've edited the chart in Datawrapper's web UI directly and
want to push the new version live.

## Re-fetch the embed snippet

`dw_publish.py` prints the responsive iframe to stdout. To re-fetch
without republishing:

```bash
python .claude/skills/blog-charts/scripts/dw_list.py --json | jq -r '."<slug>".embed_iframe'
```

Or look at `~/.cache/blog-charts/registry.json` directly.

## Versioning gotchas

- The `publicUrl` field returned by Datawrapper looks like
  `https://datawrapper.dwcdn.net/oJpU6/2/` (with version). The skill
  strips this to the versionless redirect when building the embed.
- If you ever paste the *versioned* URL into a post by mistake, future
  republishes won't update what readers see. Always use versionless.
- The web UI's "Embed" tab shows the same versionless URL. Either source
  is fine.

## Workflow summary

```
draft  →  dw_create.py  →  dw_export.py (PNG)  →  Read PNG  →  dw_publish.py  →  paste embed in post
                              ↑                                       ↓
                          iterate                              versionless URL
                                                                       ↓
data refresh →  dw_update.py --csv new.csv --publish  →  iframe in post auto-shows new version
```
