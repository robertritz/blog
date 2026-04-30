# Chart Types

Pick the chart type to match the question, not the data. Ask "what
comparison is the reader making?"

## Common types and when to use each

| Datawrapper type ID | Name | Best for |
|---|---|---|
| `d3-lines` | Line chart | Time series with 1-5 series. The default for trend stories. |
| `multiple-lines` | Small-multiples line | 6+ series, or series with very different y-ranges. |
| `d3-area` | Area chart | One-series time trend when magnitude (not the rate of change) is the point. Rarely the right call — prefer `d3-lines`. |
| `column-chart` | Vertical columns | A handful of discrete time periods (≤20 columns). Quarterly GDP, annual rates. |
| `stacked-column-chart` | Stacked columns | Composition over time when the total matters. |
| `grouped-column-chart` | Grouped columns | Side-by-side comparison within each period (e.g., two categories per year). |
| `d3-bars` | Horizontal bars | Ranking non-time categories (countries, sectors, items). Long labels fit better horizontally. |
| `d3-bars-stacked` | Stacked bars | Composition within each categorical bar. |
| `d3-bars-split` | Split bars | Diverging comparison (positive vs. negative change). |
| `d3-bars-bullet` | Bullet bars | Performance vs. benchmark / target. |
| `d3-dot-plot` | Dot plot | Ranking with one or two values per category — more honest than bars when zero baseline isn't meaningful. |
| `d3-range-plot` | Range plot | A range per category (min-max, IQR). |
| `d3-arrow-plot` | Arrow plot | Change between two points per category (before → after). |
| `d3-scatter-plot` | Scatter plot | Two continuous variables. Correlation, distribution. |

## Types to avoid, usually

| Type | Reason |
|---|---|
| `d3-pies`, `d3-donuts`, `d3-multiple-pies`, `d3-multiple-donuts` | Pies are bad at comparison. Use a horizontal bar chart instead. |
| `d3-maps-choropleth`, `d3-maps-symbols`, `locator-map` | Maps are for geography, not rank or magnitude. Only use when geography itself is the insight. |
| `tables` | Tables are for precise lookup, not pattern recognition. Pair a chart with a downloadable CSV instead. |

## Decision tree

1. **Does the x-axis represent time?** → Line chart (few series) or column chart (few discrete periods).
2. **Comparing categories?** → Bar chart, horizontal if labels are long.
3. **Comparing composition within categories or time?** → Stacked bar or stacked column.
4. **Relationship between two continuous variables?** → Scatter plot.
5. **Change between two specific points across many categories?** → Arrow plot.
6. **Ranking with honest zero ambiguity?** → Dot plot.

## Style overlays applied automatically

The skill applies blog styling overlays per chart type. These chart types
get specific tuning out of the box:

- `d3-lines`, `multiple-lines`
- `d3-area`
- `column-chart`, `stacked-column-chart`, `grouped-column-chart`
- `d3-bars`, `d3-bars-stacked`, `d3-bars-split`
- `d3-scatter-plot`

For other types the skill still works — you just get Datawrapper's defaults
plus the blog's palette and byline.
