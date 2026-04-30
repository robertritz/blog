# Blog Styling

Charts on robertritz.com use a small, harmonized palette. The colors are
the same hex values used by the matplotlib `chart-maker` skill, so static
PNGs and interactive Datawrapper embeds read as one design system.

## Palette

| Role | Hex | When to use |
|---|---|---|
| Accent (primary) | `#2b5cd6` | The data point that matters |
| Secondary | `#d4502a` | Comparison, before-after, counterfactual |
| Context | `#a8b2c4` | Background series, "everything else" |
| Supporting amber | `#d4912a` | Third color, sparingly |
| Supporting green | `#2a8f5a` | Fourth color, sparingly |
| Supporting purple | `#7b4ea3` | Fifth color, last resort |

**Rules:**

- One series? Accent (`#2b5cd6`), or context-gray with the focal item in accent.
- Two series? Accent + secondary. Or accent + context if one is background.
- Three+ series? Default to small multiples (`multiple-lines`) instead.
- Highlighting one item in a group? Everything in context-gray, focal item in accent.
- Avoid red-green pairs (color-blindness) — pair warm with cool instead.

## Other defaults

| Element | Value |
|---|---|
| Byline | `Robert Ritz` |
| Plot background | `#fafaf7` (off-white) |
| Gridlines | `#e5e9f0`, horizontal only |
| Embed width × height | 680 × 440 px (matches blog's 720px content column) |
| Footer | Datawrapper attribution stays (Free tier); byline & source sit alongside |

## How styling gets applied

The skill applies styling per-chart through Datawrapper's
`metadata.visualize` and `metadata.publish` properties — Free-tier
compatible, no team theme required. See `_style.py` in `scripts/` for the
implementation.

## Overriding the defaults

For a one-off chart that needs different colors, pass `extra_visualize`
through `_style.style_for(...)` directly, or use Datawrapper's web UI
for fine-tuning after `dw_create.py` runs. The next `dw_update.py
--restyle` will reset to defaults — useful if you experimented and want
to start over.

## Free-tier limits

- "Created with Datawrapper" footer — stays.
- Custom logos in chart footer — not available.
- PDF / SVG export — paid only. PNG works.
- Account-wide custom themes — paid only. We apply per-chart instead.

## Number formatting

Datawrapper's `describe.number-format` accepts patterns like `0.0`,
`0,0`, `0.0%`, `$0.0a`. Common blog choices:

| Data type | `--number-format` | `--number-append` | `--number-prepend` | Example |
|---|---|---|---|---|
| Percent | `0.0` | `%` | — | `3.7%` |
| Dollars (millions+) | `0.0a` | — | `$` | `$1.2B` |
| Plain count with thousands | `0,0` | — | — | `12,340` |
| Index | `0.0` | — | — | `142.3` |
| Mongolian Tugrik | `0,0` | ` ₮` | — | `12,340 ₮` |

`number-divisor` divides input before formatting (use 0.01 to convert
`37` to `0.37` before percent formatting). Be careful — easy to
double-divide.
