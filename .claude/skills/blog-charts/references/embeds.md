# Embedding Charts in Blog Posts

The blog defaults to **interactive responsive iframes** for new posts.
Datawrapper's embed renders crisply on mobile and supports tooltips, hover
highlights, and dark-mode-aware styling.

## After `dw_publish.py`

The script prints the responsive embed snippet to stdout and saves it in
the registry under `embed_iframe`. It looks like this:

```html
<iframe title="..." aria-label="chart"
        id="datawrapper-chart-XXXXX"
        src="https://datawrapper.dwcdn.net/XXXXX/"
        scrolling="no" frameborder="0"
        style="width: 0; min-width: 100% !important; border: none;"
        height="450"></iframe>
<script type="text/javascript">!function(){...}();</script>
```

The `src` is **versionless** — it always redirects to the latest published
version of the chart. So a `dw_update.py --slug ... --publish` will refresh
what readers see without you having to update any post.

## Pasting into a post

### Option A — `.mdx` post (preferred)

Astro's MDX integration is enabled (`astro.config.mjs`). For interactive
embeds, the post should be `.mdx`, not `.md`. Reasons:

- MDX handles the `<script>` tag correctly (executes the resize listener).
- MDX preserves the iframe attributes verbatim.

Steps:

1. Create the post as `src/content/posts/<slug>.mdx`.
2. Paste the snippet from `dw_publish.py` directly into the body.
3. Run `npm run dev` and verify the chart renders and resizes when you
   change the window width.

### Option B — `.md` post with PNG fallback

Pure markdown can host an `<iframe>`, but the auto-resize `<script>` may
not execute reliably. Two workarounds:

- **Easier**: skip interactivity, embed the PNG. Run
  `dw_export.py --slug <slug> --out public/images/<post-slug>/<chart-slug>.png`
  and reference it as `![](/images/<post-slug>/<chart-slug>.png)`.
- **Harder**: keep the iframe but pin a `height="500"` attribute and
  drop the script. The chart won't auto-resize on window changes but
  will still render. Acceptable for a single chart in a short post.

## Chart spacing in posts

Leave a blank line above and below the embed snippet so Astro's markdown
parser treats it as a block-level element. Inside an `.mdx` JSX
expression won't need this; raw HTML in markdown does.

## Multiple charts on a page

The auto-resize listener script is small and self-deduplicating — copies
of it on a page don't conflict. But for posts with >3 interactive embeds,
consider extracting the script into a shared Astro layout to keep the
markdown source clean.

## Caching the embed snippet

The snippet is stored in the registry at `~/.cache/blog-charts/registry.json`
under `embed_iframe`. Re-fetch with:

```bash
python .claude/skills/blog-charts/scripts/dw_list.py --json | jq '."<slug>".embed_iframe'
```

Or just look at the file directly.

## Static PNG fallback

When you'd rather have a static image — for an `.md` post, for an
emailed newsletter, for archival snapshots — export the PNG:

```bash
python .claude/skills/blog-charts/scripts/dw_export.py \
    --slug <slug> \
    --out public/images/<post-slug>/<chart-slug>.png
```

Convention: PNGs live under `public/images/<post-slug>/`, matching the
existing blog directory pattern. Reference with absolute path:
`![](/images/<post-slug>/<chart-slug>.png)`.

## When the chart updates

If you publish v2 of a chart with `dw_update.py --publish`, every
embedded iframe across all posts updates automatically — they point at
the versionless URL. No post edits required.

PNGs do **not** auto-refresh; rerun `dw_export.py` and overwrite the
file in `public/images/`.
