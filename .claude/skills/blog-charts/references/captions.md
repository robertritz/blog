# Titles, Intros, Sources, and Notes

Four text fields carry the chart's framing. The visualization is only as
clear as the text around it.

| Field | CLI flag | Purpose | Length |
|---|---|---|---|
| Title | `--title` | The finding. | 40-80 chars |
| Intro | `--intro` | Unit, time frame, scope. | 1 sentence, ~120 chars |
| Source name | `--source-name` | Attribution. | Short, e.g. "FRED" |
| Source URL | `--source-url` | Link to underlying data. | Full URL |
| Notes | `--notes` | Footnotes — methodology, caveats. | 1-2 sentences |
| Series label | `--series-label COL=LABEL` | Rename a CSV column in the legend. Repeatable. | Short |
| Series color | `--series-color SERIES=#hex` | Pin a specific color to a series. Repeatable. | — |
| Text annotation | `--annotate-text "X\|Y\|TEXT"` | Callout near a data point. Repeatable. | 4-8 words |
| Range annotation | `--annotate-range "X0\|X1\|TEXT"` | Shaded period (recession bar, policy window). Repeatable. | Short |
| Number format | `--number-format` | Datawrapper format string. | — |
| Unit suffix | `--number-append` | Appended to values (e.g. `%`). | — |
| Unit prefix | `--number-prepend` | Prepended to values (e.g. `$`). | — |

Byline defaults to "Robert Ritz".

## Voice

When drafting these fields, invoke the **`roberts-voice`** skill. Chart
captions should sound like the rest of the post — not a separate
register. Robert's voice is curious, direct, mildly irreverent; data
captions can be drier than body copy but should still feel of-a-piece.

## Titles

Write titles that carry the finding, not the topic.

| Topic-only (weak) | Finding-forward (strong) |
|---|---|
| "Unemployment over time" | "Unemployment is back to pre-pandemic lows" |
| "Mongolian meat prices" | "Mongolian meat prices doubled in five years" |
| "USD/MNT since 2010" | "The tugrik has lost 60% of its value against the dollar since 2010" |
| "Gasoline imports" | "Mongolia's gasoline imports halved in two years" |

Don't over-claim. The title must be defensible against the chart itself.
"X caused Y" but the chart only shows correlation? Rewrite.

### Tense

Past for historical claims ("X rose from A to B"). Present for current
state ("X is at its lowest in a decade"). Future only for forward-looking
projections, with an explicit conditional ("If trade reopens, Y reaches Z").

## Intros

The one-line under the title. Use it to specify units, time frame, and
scope.

Pattern: `<unit>, <time frame>. <optional context>.`

Examples:

- `"Monthly volume in tonnes, January 2022 – March 2026."`
- `"Year-over-year change in CPI, monthly, 2010 – 2026."`
- `"Index, 2020 = 100. Real wages vs. consumer prices."`
- `"Annual average, 1990 – 2026. Mongolia and regional comparators."`

If the chart shows an index, **always say what the base year is**.
If the data is seasonally adjusted, **say so in the intro**, not the notes.

## Source name & URL

`--source-name` renders as "Source: …" in the footer. Examples:

- `--source-name "National Statistics Office of Mongolia"`
- `--source-name "World Bank"`
- For multi-source: `--source-name "World Bank, IMF"`
- For author analysis: `--source-name "Author's calculations"` (cite the
  underlying inputs in `--notes`)

## Notes

Footer notes carry what doesn't fit in the intro:

- Methodology: `"Constructed as ratio of imports to total fuel consumption."`
- Caveats: `"Excludes informal cross-border trade."`
- Last updated (for charts that get refreshed): `"Last updated 2026-04-30."`

Skip notes when there's nothing to say. Empty is fine.

## Series labels

If the CSV column is `value` (the default for many data exports), the
chart legend will literally show "value". Always rename:

```bash
--series-label 'value=Gasoline imports'
```

For multi-series wide CSVs:

```bash
--series-label 'gasoline=Gasoline' \
--series-label 'diesel=Diesel' \
--series-label 'jet_fuel=Jet fuel'
```

## Annotations

**Text annotations** — call out a specific data point. Pipe-separated:

```bash
--annotate-text "2024-03|145000|Peak imports"
--annotate-text "2022-08|72000|Sanctions take effect"
```

Optional 4th and 5th fields override color and size:
`"2024-03|145000|Peak imports|#c53030|13"`.

**Range annotations** — shade a period of time. Useful for recessions,
policy windows, sanctions, conflicts:

```bash
--annotate-range "2022-02-24|2022-12-31|Russia invades Ukraine"
--annotate-range "2008-09|2009-06|"   # plain shaded band, no text
```

For richer annotations (alignment, dx/dy nudges, italic, multi-line),
use the raw API — see `api.md`.

## Series colors

Override the default palette assignment for a specific series:

```bash
--series-color 'Gasoline=#2b5cd6' --series-color 'Diesel=#a8b2c4'
```

Hex `#` is normalized — `2b5cd6` works too. See `styling.md` for the
blog palette.

## Worked example

```bash
python .claude/skills/blog-charts/scripts/dw_create.py \
  --slug fuel-shortage--gasoline-imports \
  --type d3-lines \
  --csv ./data/imports.csv \
  --title "Mongolia's gasoline imports halved in two years" \
  --intro "Monthly volume in tonnes, January 2022 – March 2026." \
  --source-name "National Statistics Office of Mongolia" \
  --source-url "https://www.1212.mn/" \
  --notes "Excludes informal cross-border trade." \
  --series-label 'value=Gasoline imports' \
  --annotate-range '2022-02-24|2022-12-31|Russia invades Ukraine' \
  --annotate-text '2024-03|72000|Refinery shutdown'
```
