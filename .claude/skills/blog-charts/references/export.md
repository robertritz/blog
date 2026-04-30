# PNG Export

Datawrapper's PNG export endpoint works on **drafts and published charts**.
This is the fast iteration loop — see the chart, fix the chart, see again.

## Basic export

```bash
python .claude/skills/blog-charts/scripts/dw_export.py \
    --slug <slug> --out ./preview.png
```

Default output: ~1600 × 1066 px (zoom=2, retina-sharp for the 680 × 440
embed).

## Flags

| Flag | Default | What it does |
|---|---|---|
| `--out` | required | Output PNG path. Parent dirs are created. |
| `--zoom` | 2 | 1 = mobile/native size; 2 = retina; 3 = oversized for slides. |
| `--plain` | false | Drop title / description / footer — chart body only. |
| `--width` / `--height` | (auto) | Override pixel dimensions. |
| `--border-width` | 20 | Padding around the chart in pixels. |
| `--transparent` | false | Transparent background instead of white. |

## Visual verification loop

After `dw_create.py`, always:

1. Export to a temporary path.
2. Read the PNG file (Claude can do this — the image is shown in
   context).
3. Check: does the title state the finding? Are colors right? Is the
   y-axis honest? Is the source attribution there?
4. Fix with `dw_update.py` if anything's off.
5. Repeat until the chart lands in 5 seconds.

```bash
# Iterate
python .claude/skills/blog-charts/scripts/dw_export.py --slug <slug> --out /tmp/preview.png
# Read /tmp/preview.png and assess
python .claude/skills/blog-charts/scripts/dw_update.py --slug <slug> --title "Better title"
python .claude/skills/blog-charts/scripts/dw_export.py --slug <slug> --out /tmp/preview.png
```

## Plain export for inline use

`--plain` strips the chart frame so you can use the chart body alone in
a context where the surrounding markdown carries the caption.

```bash
python .claude/skills/blog-charts/scripts/dw_export.py \
    --slug <slug> --out ./body.png --plain
```

## Embedding the PNG

For `.md` posts (or anywhere interactive iframes are inconvenient), drop
the PNG into `public/images/<post-slug>/<chart-slug>.png` and reference:

```markdown
![Mongolia's gasoline imports halved in two years](/images/fuel-shortage/gasoline-imports.png)
```

PNGs **do not** auto-refresh when the chart's data updates. Rerun
`dw_export.py` after every `dw_update.py --publish` if the post uses a
PNG embed. (Iframes auto-refresh — see `embeds.md`.)

## Free-tier limits

- PNG export — works.
- PDF export — paid only.
- SVG export — paid only.
