# Troubleshooting

## Auth errors

### `Missing DATAWRAPPER_API_TOKEN`

The loader walks up from the skill directory looking for a parent
containing `CLAUDE.md` + `.claude/`. If your `.env` lives elsewhere,
either move it to the blog repo root or export the variable:

```bash
export DATAWRAPPER_API_TOKEN="..."
```

### `Datawrapper API error 401`

Token expired or lacks scopes. Generate a new one at
<https://app.datawrapper.de/account/api-tokens> with: `chart:read`,
`chart:write`, `folder:read`, `folder:write`, `theme:read`, `user:read`.

### `Datawrapper API error 403`

Token missing a scope for the requested operation, or you're trying to
delete a chart owned by another user. Run `dw_get.py --slug <slug>` and
check who owns it.

## Rate limits

### `Datawrapper API error 429`

You burst past 60 req/min. The client throttles to 4 req/sec, but a
parallel run can trip it. Wait a minute.

## Chart errors

### `slug 'X' already maps to chart Y`

`dw_create.py` refuses to clobber an existing slug. Pick a new slug, or
pass `--replace` to delete the existing chart and recreate.

### `No registry entry for slug 'X'`

The slug isn't in your local registry. Check `dw_list.py`. If the chart
exists on Datawrapper, fall back to `--id <chart_id>` or fix the
registry — see `registry.md`.

### `invalid slug 'X'`

Slug constraints: lowercase, alphanumeric start, hyphens/underscores
allowed, 1-81 chars total. No spaces, no uppercase, no special chars.

### Chart looks wrong after `dw_update.py --restyle`

`--restyle` overwrites all `visualize` settings with the blog defaults.
If you'd customized something via the web UI, that's gone. Restore by
re-customizing in the web UI, then `dw_publish.py` to push the new
version.

## Embed errors

### Iframe shows up but doesn't auto-resize

The accompanying `<script>` isn't executing. Most common causes:

- Post is `.md` instead of `.mdx`. Astro's markdown integration may
  strip script tags. Convert to `.mdx`.
- Content Security Policy on the deployed site blocks inline scripts.
  Check the CSP header.
- Multiple iframes on the page with mismatched IDs. The script keys on
  `id="datawrapper-chart-{id}"` — make sure each iframe has a unique
  `id` attribute.

### Iframe loads but chart is blank

- Check the `src` URL in a browser. If it 404s, the chart was unpublished
  or deleted.
- If it loads but shows "Chart not found", the public version was
  withdrawn. Run `dw_publish.py --slug <slug>` to republish.

### Chart updates aren't appearing in published posts

The embed URL must be **versionless** —
`https://datawrapper.dwcdn.net/{id}/` — not the versioned URL with `/2/`
on the end. Re-paste the snippet from the registry's `embed_iframe`
field, which always uses versionless.

## Network errors

### `Network error on POST /v3/charts: timed out`

Connection to Datawrapper failed. The script raises after 60 seconds.
Re-run.

### `Network error: name resolution failure`

DNS failure or you're offline. Re-check connectivity.

## Inspecting state

```bash
# What's in the registry?
python .claude/skills/blog-charts/scripts/dw_list.py

# What's actually on Datawrapper?
python .claude/skills/blog-charts/scripts/dw_list.py --remote

# Reconcile the two
python .claude/skills/blog-charts/scripts/dw_list.py --sync

# Inspect a single chart end-to-end
python .claude/skills/blog-charts/scripts/dw_get.py --slug <slug>
```

## Last-resort

```bash
# Wipe the local registry — charts on Datawrapper survive.
rm ~/.cache/blog-charts/registry.json
```

Then `dw_list.py --remote` to see the canonical state and rebuild the
registry by re-running `dw_publish.py --slug <slug> --id <chart_id>` for
each chart you want back.
