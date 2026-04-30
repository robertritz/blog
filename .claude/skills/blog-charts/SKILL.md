---
name: blog-charts
description: >
  Publish charts for robertritz.com through the Datawrapper API. Creates,
  updates, styles, publishes, and PNG-exports charts from a CSV. Default
  embed is Datawrapper's responsive interactive iframe (paste into an .mdx
  post); a PNG export drops to disk so Claude can read it back and visually
  verify before publishing. Uses a local slug registry so repeated calls
  update the same chart instead of duplicating it. Applies the blog's
  harmonized style (palette, byline, caption conventions) automatically.
  Triggers on: chart, charts, datawrapper, dw_create, dw_update, dw_publish,
  dw_export, blog-charts, embed chart, line chart, bar chart, column chart,
  scatter, area chart, visualize, publish chart, refresh chart.
---

# Blog Charts (Datawrapper)

Wrapper around the Datawrapper API tuned for robertritz.com. Takes a CSV,
creates or updates a chart, applies the blog's harmonized style, publishes,
and exports a PNG for visual verification.

## When to Use

| Situation | Action |
|---|---|
| New chart for a blog post | `dw_create.py` |
| Refresh a chart's data | `dw_update.py --slug <slug> --csv new.csv --publish` |
| See the chart before publishing | `dw_export.py --slug <slug> --out ./preview.png`, then Read the PNG |
| Publish a draft | `dw_publish.py` (prints the responsive iframe to paste into the post) |
| See all charts | `dw_list.py` (local registry) or `dw_list.py --remote` |
| Delete a chart | `dw_delete.py` |

Old posts that used the matplotlib `chart-maker` skill stay as-is. New
charts default to this skill — interactive embeds work well on mobile and
in dark mode.

## The Gotcha: Slugs Prevent Duplicates

The Datawrapper API has no idempotency. `POST /v3/charts` twice → two
charts with the same title. This skill fixes that with a local slug
registry at `~/.cache/blog-charts/registry.json`.

Every new chart gets a slug — short, kebab-case, namespaced by post:
`<post-slug>--<chart-name>`. For example:

- `fuel-shortage--gasoline-imports`
- `mongolian-meat-prices--annual-trend`
- `usd-mnt-forecast--scenario-grid`

The registry maps each slug to Datawrapper's chart ID. `dw_create.py`
refuses to run if the slug already exists; `dw_update.py` requires one
and operates in-place. See `references/registry.md`.

## The Standard Flow

```bash
# 1. Create (registers slug, uploads data, applies blog style).
python .claude/skills/blog-charts/scripts/dw_create.py \
    --slug fuel-shortage--gasoline-imports \
    --type d3-lines \
    --csv ./data/imports.csv \
    --title "Mongolia's gasoline imports halved in two years" \
    --intro "Monthly volume in tonnes, January 2022 – March 2026." \
    --source-name "National Statistics Office of Mongolia" \
    --source-url "https://www.1212.mn/"

# 2. Preview as PNG. Claude should Read this file and check the chart
#    reads correctly: title, axis labels, data range, colors.
python .claude/skills/blog-charts/scripts/dw_export.py \
    --slug fuel-shortage--gasoline-imports --out /tmp/preview.png

# 3. Publish when it looks right. Prints the responsive iframe snippet.
python .claude/skills/blog-charts/scripts/dw_publish.py \
    --slug fuel-shortage--gasoline-imports

# 4. Paste the printed snippet into the .mdx post.
#    (For a .md post, embed the PNG instead — see references/embeds.md.)

# 5. Later, refresh data with one command.
python .claude/skills/blog-charts/scripts/dw_update.py \
    --slug fuel-shortage--gasoline-imports \
    --csv ./data/imports.csv \
    --publish
```

## Routing — Read the Right Reference

Progressive disclosure. Don't load everything. Load each reference only
when you reach that decision.

| Need | Reference | When to read |
|---|---|---|
| The data-viz philosophy that drives every chart | `references/principles.md` | Always read **before drafting the title** of a new chart |
| Pick the right chart type | `references/chart-types.md` | Before `dw_create.py --type ...` |
| Apply blog style / palette | `references/styling.md` | First use, or when overriding the default palette |
| Write title / intro / source / notes | `references/captions.md` | When drafting `--title`, `--intro`, `--source-name`, `--notes` |
| Embed a published chart in a post | `references/embeds.md` | After `dw_publish.py` |
| Update or refresh a chart | `references/updates-and-publishing.md` | Any chart refresh |
| Export a PNG | `references/export.md` | Any visual verification step |
| Pre-publish checklist | `references/best-practices.md` | Before every `--publish`. Always. |
| Understand / repair the registry | `references/registry.md` | Registry errors |
| Raw API calls | `references/api.md` | Something's not in the CLI |
| Set up the API token | `references/secrets.md` | First time, or "missing token" error |
| Debug | `references/troubleshooting.md` | Any 4xx / 5xx |

## Scripts

All live at `scripts/`. Each is self-contained (`python <name>.py --help`).

| Script | Verb | Key flags |
|---|---|---|
| `dw_create.py` | Create chart, upload CSV, apply style, register slug | `--slug --type --csv --title --intro --source-name --source-url --notes` |
| `dw_update.py` | Push new data or change metadata on existing chart | `--slug --csv --notes --publish --restyle` |
| `dw_publish.py` | Publish / republish, print embed snippet | `--slug` |
| `dw_export.py` | Export PNG (works on drafts) | `--slug --out --zoom --plain` |
| `dw_list.py` | List registered or remote charts | `--remote --sync` |
| `dw_delete.py` | Delete chart + deregister slug | `--slug --force` |
| `dw_get.py` | Show one chart's details | `--slug` |

Every script also accepts `--id <chart_id>` as a fallback when a chart
wasn't made through this tool (or the slug got lost).

## Output Contract

`dw_create.py` prints the chart ID to stdout (captureable) and progress
to stderr. `dw_publish.py` prints the responsive iframe snippet. Registry
entries look like:

```json
{
  "fuel-shortage--gasoline-imports": {
    "id": "dGAQ0",
    "title": "Mongolia's gasoline imports halved in two years",
    "type": "d3-lines",
    "source_csv": "/abs/path/to/imports.csv",
    "public_url": "https://datawrapper.dwcdn.net/dGAQ0/2/",
    "public_version": 2,
    "embed_iframe": "<iframe ...>...</iframe><script>...</script>",
    "published_at": "2026-04-30T06:22:33Z",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

## Free-Tier Constraints

The blog uses Datawrapper's Free plan:

- PNG export works. PDF/SVG require the Custom plan.
- "Created with Datawrapper" stays in the footer. The byline (Robert Ritz)
  and source attribution sit alongside it.
- Custom themes (account-wide) require the paid plan. This skill applies
  blog styling per-chart through `metadata.visualize` — Free-tier compatible.
- No custom logos in the chart footer. Branding is carried by byline,
  source attribution, and the surrounding article.

See `references/styling.md` for what the Free tier can and can't do.

## Companion Skills

- **`roberts-voice`** — invoke when drafting `--title`, `--intro`, and
  `--notes`. Chart captions should sound like the rest of the post.
- **`chart-maker`** (deprecated, matplotlib) — kept for backward
  compatibility with old posts that referenced its templates. New charts
  use this skill.
