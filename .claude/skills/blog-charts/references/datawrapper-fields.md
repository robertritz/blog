# Datawrapper visualize schema (validated)

Field names and types in this document are taken from `chartTypes.ts` in the
`datawrapper/datawrapper` monorepo and the seed `metadata.visualize` literal in
`JsonCRDT.benchmark.ts`. Where a field is "folk knowledge" — observed in a
public chart's API response or a community example, but not in primary docs —
that is called out explicitly.

The top-level chart object always has the shape
`{ metadata: { data, describe, visualize, annotate, publish } }`. Everything in
this document lives under `metadata.visualize` unless noted.

---

## Range annotations (`metadata.visualize.range-annotations`)

Stored as an **array** of objects. The key is a hyphenated string and must be
accessed bracket-style in JS/TS.

| Field           | Type                                  | Required | Notes                                                                           |
| --------------- | ------------------------------------- | -------- | ------------------------------------------------------------------------------- |
| `id`            | string                                | yes      | Any unique-per-chart id. Datawrapper uses `nanoid(10)`.                         |
| `position`      | object (see below)                    | yes      | The corners of the band. Required even for single-line annotations.             |
| `display`       | `'range'` \| `'line'`                 | yes      | `range` = shaded band, `line` = single rule.                                    |
| `type`          | `'x'` \| `'y'`                        | yes      | Axis the annotation is anchored to. `'x'` for vertical bands on a date x-axis. |
| `color`         | string (CSS color)                    | yes      | Hex like `#cccccc` works.                                                       |
| `opacity`       | number                                | yes      | **0–100, not 0–1** (empirically). The TS types say 0–1 but the renderer treats `0.15` as effectively zero and `15` as ~15% opacity. Use integer values. |
| `strokeWidth`   | `1` \| `2` \| `3`                     | yes      | Only meaningful when `display: 'line'`.                                         |
| `strokeType`    | `'solid'` \| `'dotted'` \| `'dashed'` | yes      | Only meaningful when `display: 'line'`.                                         |
| `showInAllPlots`| boolean                               | no       | Only relevant for split / small-multiple charts.                                |

`position` shape:

```ts
{ x0: number | string, x1: number | string,
  y0: number | string, y1: number | string,
  plot?: AnnotationPlot, group?: string, column?: string }
```

For a date-axis line chart you set `x0` / `x1` to ISO date strings and leave
`y0` / `y1` at the chart range (or `'-Infinity'` / `'Infinity'` — the band
extends to the plot edges either way; observed behavior).

**There is no `text`, `label`, `displayText` or `name` field on a range
annotation.** This is what bit your COVID-19 chart: the band has no caption.
The canonical pattern (per the line-chart Academy article and confirmed in the
TS types) is to add a separate `text-annotations` entry positioned inside the
band.

Worked example — a "COVID-19" shaded band on a line chart:

```json
{
  "metadata": {
    "visualize": {
      "range-annotations": [
        {
          "id": "covid-band",
          "type": "x",
          "display": "range",
          "color": "#cccccc",
          "opacity": 0.15,
          "strokeWidth": 1,
          "strokeType": "solid",
          "position": { "x0": "2020-03-01", "x1": "2021-06-30", "y0": 0, "y1": 0 }
        }
      ],
      "text-annotations": [
        {
          "id": "covid-label",
          "text": "COVID-19",
          "position": { "x": "2020-10-15", "y": "95%" },
          "align": "mc",
          "dx": 0, "dy": 0,
          "size": 12, "italic": true, "bold": false, "underline": false,
          "color": "#666666", "bg": false, "width": 20,
          "showMobile": true, "showDesktop": true, "mobileFallback": true,
          "connectorLine": { "enabled": false, "type": "straight",
            "circle": false, "stroke": 1, "arrowHead": "lines",
            "circleStyle": "solid", "circleRadius": 15,
            "inheritColor": false, "targetPadding": 4 }
        }
      ]
    }
  }
}
```

**Caveat (empirically verified):** the percentage-string syntax (`y: "95%"`)
is **not** honored by the export renderer. Despite the TS type declaring
`y?: number | string`, only finite numeric values in data space render
correctly. Strings like `"95%"`, `"Infinity"`, `"top"` and absurdly large
numbers (`1e15`) all silently fail to render the text annotation. The
skill's `label_for_range` helper takes a `y` parameter and the CLI
computes it from the chart's CSV (max value across all numeric columns).

---

## Text annotations (`metadata.visualize.text-annotations`)

Array of objects. Schema from `TextAnnotationProps` + `id`.

| Field           | Type                                                                          | Required | Notes                                                                       |
| --------------- | ----------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------- |
| `id`            | string                                                                        | yes      | Unique per chart.                                                           |
| `text`          | string                                                                        | yes      | HTML allowed (`<b>`, `<i>`, `<br>`, `<span style="color:red">`).            |
| `position`      | `{ x?, y?, plot?, group?, column?, rowIndex?, rowOffset? }`                   | yes      | Provide `x`/`y` for line/scatter. `column`+`rowIndex` for bar/column.       |
| `align`         | `'tl'\|'tc'\|'tr'\|'ml'\|'mc'\|'mr'\|'bl'\|'bc'\|'br'`                        | yes      | 9-point anchor. `mc` = middle-center, `tl` = top-left, etc.                 |
| `dx`            | number                                                                        | yes      | Horizontal offset in px. Positive = right.                                  |
| `dy`            | number                                                                        | yes      | Vertical offset in px. Positive = down (per Academy: "down or right").      |
| `size`          | number                                                                        | yes      | Font size in px. Default 14.                                                |
| `bold`          | boolean                                                                       | yes      | —                                                                           |
| `italic`        | boolean                                                                       | yes      | —                                                                           |
| `underline`     | boolean                                                                       | yes      | —                                                                           |
| `color`         | string \| `false`                                                             | yes      | `false` inherits from theme; otherwise CSS color.                           |
| `bg`            | boolean                                                                       | yes      | White background pill behind text (the "outline" toggle in the UI).         |
| `width`         | number                                                                        | yes      | Annotation width as a percent (e.g. `20` ≈ 20% of chart width).             |
| `showMobile`    | boolean                                                                       | yes      | Render on mobile.                                                           |
| `showDesktop`   | boolean                                                                       | yes      | Render on desktop.                                                          |
| `mobileFallback`| boolean                                                                       | yes      | If true, hidden mobile annotations get numbered and listed below the chart. |
| `connectorLine` | object (see below)                                                            | yes      | Always present; `enabled: false` disables the line/arrow.                   |
| `showInAllPlots`| boolean                                                                       | no       | For small multiples.                                                        |

`connectorLine`:

```ts
{
  enabled: boolean,
  type: 'straight' | 'curveRight' | 'curveLeft',
  circle: boolean,
  circleStyle: 'solid' | 'dashed',
  circleRadius: number,
  stroke: number,
  arrowHead: 'lines' | 'triangle' | false,
  inheritColor: boolean,
  targetPadding: number
}
```

Multi-line text: use literal `\n` in JSON (Datawrapper renders newlines as
breaks) or `<br>` (HTML).

`showMobile` / `showDesktop` are independent visibility toggles; `mobileFallback`
is a fallback behavior for hidden-on-mobile annotations (the "Show as key on
mobile" toggle described in the Academy text-annotations article).

---

## Direct line labels (line charts)

The relevant fields, all on `metadata.visualize` (confirmed in the seed
literal):

- **`labeling`**: `'right'` (default — labels at line endpoints) | `'legend'`
  (color key above chart) | `'off'` (no automatic labels). Per Academy: "Annotate
  → Labeling → Line labels: right". `'off'` is folk knowledge and what you want
  if you're hand-placing text annotations near endpoints.
- **`label-margin`**: number, px gap between line endpoint and the label.
  Increase to push direct labels further right and reduce collisions with
  text annotations.
- **`label-colors`**: boolean — when true, direct labels inherit the line color.
- **`line-value-labels`**: boolean — show numeric value next to the direct label.
- **`show-value-labels`**: boolean — show value labels on data points.

**Recommended pattern when text annotations collide with direct labels:**

1. Set `"labeling": "off"` to suppress all direct line labels, OR
2. Keep `"labeling": "right"` and increase `"label-margin"` to e.g. 20–30, and
   place your text annotations with negative `dx` so they sit to the left of
   the endpoint.

There is no per-series toggle for direct labels in `metadata.visualize` (folk
knowledge: `highlighted-series` highlights specific series but does not control
labeling per-series). To label only some series, set `labeling: 'off'` and add
manual `text-annotations` for the lines you want labeled.

---

## Y-axis tick formatting

Confirmed in source: **`describe['number-append']` and `describe['number-prepend']`
are tooltip-only.** The formatter takes a `full` boolean — when `false`
(axis ticks, abbreviated displays) prepend/append are stripped; when `true`
(tooltips, value labels) they are applied. So your ` ₮` only showing in
tooltips is the documented behavior, not a bug.

To put units on tick labels you have two options:

1. **Bake the unit into `y-grid-format`** as a numbro format string. Examples
   (numbro syntax, confirmed by Academy):
   - `'0,0'` → `1,234`
   - `'0.[00]'` → `12.34`
   - `'$0,0'` → `$1,234` (any literal char before the digit token is preserved)
   - `'0,0 ₮'` is not a documented numbro pattern; use a custom format with a
     literal in the prefix slot, or accept that the tugrik symbol can only sit
     in the chart subtitle / intro.

2. **Put the unit in the chart subtitle / intro** (`metadata.describe.intro`) —
   this is the convention Datawrapper's own examples follow and the one their
   blog article on text in viz recommends.

Other y-axis fields (all `metadata.visualize`, all confirmed in seed):

- `y-grid`: `'on'` | `'off'` | `'ticks'`
- `y-grid-format`: numbro format string, default `'auto'`.
- `y-grid-labels`: `'inside'` | `'outside'` | `'off'`
- `y-grid-label-align`: `'left'` | `'right'`
- `y-grid-subdivide`: boolean
- `custom-range-y`: `[string, string]` — manual min/max, empty string = auto.
- `custom-ticks-y`: comma-separated string of values.
- `scale-y`: `'linear'` | `'log'` (folk knowledge for `'log'`).

---

## Other useful fields by chart type

All confirmed in the line-chart seed literal in `JsonCRDT.benchmark.ts` unless
noted as folk knowledge.

### Line charts (`d3-lines`)

- `interpolation`: `'linear'` | `'step-before'` | `'step-after'` | `'curved'`
- `line-widths`: `{ [seriesName]: number }`
- `line-dashes`: `{ [seriesName]: 'solid'|'dashed'|'dotted' }` (folk)
- `line-symbols`: boolean — show dots on points.
- `line-symbols-on`: `'first'` | `'last'` | `'both'` | `'all'`
- `line-symbols-shape`: `'circle'` | `'square'` | `'diamond'`
- `line-symbols-size`: number
- `line-symbols-opacity`: number 0–1
- `highlighted-series`: `string[]` — names of series to emphasize; others fade.
- `highlighted-values`: `(number|string)[]` — highlight specific x values.
- `custom-colors`: `{ [seriesName]: hex }`
- `base-color`: number (theme palette index for non-highlighted lines).
- `date-label-format`: moment-style string, e.g. `'YYYY'`, `'MMM YYYY'`.
- `x-tick-format`: `'auto'` or moment string.
- `tick-position`: `'top'` | `'bottom'`
- `area-opacity`, `area-fill`: for area-line variants.

### Column charts (`column-chart`)

- `base-color`, `custom-colors`, `value-label-format`, `value-label-alignment`
  (`'left'`|`'center'`|`'right'`), `value-label-visibility`
  (`'always'`|`'hover'`|`'never'`), `show-value-labels`,
  `thick` (boolean — wider bars), `sort-bars` (boolean), `reverse-order`.
- `custom-range`: `[min, max]`.
- `block-labels`: boolean — labels above each column.

### Bar charts (`d3-bars`)

- Same `value-label-*` family as columns.
- `compact-group-labels`, `show-group-labels`, `show-category-labels` for
  grouped bars.
- `swap-labels`: boolean.
- `label-alignment`: `'left'`|`'right'`.
- `color-by-column`: boolean (color bars by a category column).
- `group-by-column`: boolean.

### Scatter (`d3-scatter-plot`)

- `shape`: `'fixed'` | `'variable'`
- `size`: `'fixed'` | `'variable'`
- `fixed-symbol`: e.g. `'symbolCircle'`, `'symbolSquare'` (d3-shape names).
- `fixed-size`: number (px).
- `auto-labels`: boolean.
- `outlines`: boolean.
- `color-base`: number (palette index).
- `sticky-tooltips`: boolean.

(Scatter fields above are observed in `datawrapper/snippets`, not in
`chartTypes.ts`. Treat as folk knowledge — names are stable in published
charts but no public schema confirms them.)

---

## Sources

- [`chartTypes.ts` (raw)](https://raw.githubusercontent.com/datawrapper/datawrapper/main/libs/shared/src/chartTypes.ts)
  — primary source for the `RangeAnnotation`, `TextAnnotation`,
  `RangeAnnotationPosition`, `TextAnnotationPosition`, `TextAnnotationAnchor`,
  `TextAnnotationConnectorLine` types. Authoritative.
- [`JsonCRDT.benchmark.ts` (raw)](https://raw.githubusercontent.com/datawrapper/datawrapper/main/libs/shared/src/crdt/JsonCRDT.benchmark.ts)
  — full default `metadata.visualize` literal for a line chart, plus a complete
  example annotation object. Most useful single file in the org.
- [`numberColumnFormatter.ts` (raw)](https://raw.githubusercontent.com/datawrapper/datawrapper/main/libs/shared/src/numberColumnFormatter.ts)
  — confirms `number-append`/`number-prepend` are gated on the `full` flag
  (true for tooltips, false for ticks), explaining why `" ₮"` only renders in
  tooltips.
- [Datawrapper Academy: How to create text annotations](https://www.datawrapper.de/academy/how-to-create-text-annotations)
  — UI-side documentation for align/dx/dy/connectorLine/showMobile semantics
  and HTML formatting in `text`.
- [Datawrapper Academy: Customizing your line chart](https://www.datawrapper.de/academy/customizing-your-line-chart)
  — confirms range annotations have no built-in label, recommends overlaying
  a separate text annotation; documents `labeling` (`right`/`legend`/`off`).
- [Datawrapper Academy: Custom number formats](https://www.datawrapper.de/academy/custom-number-formats-that-you-can-display-in-datawrapper)
  — numbro format token reference for `y-grid-format`, `value-label-format`,
  `tooltip-number-format`.
- [`datawrapper/snippets` repo](https://github.com/datawrapper/snippets) —
  community-style examples; `2020-10-18-trump-tweet-heatmap/create-heatmap.js`
  has a real `metadata.visualize` payload pushed via API.
- [Developer docs: Visualization Properties](https://developer.datawrapper.de/docs/chart-properties)
  — explicitly says "we won't have the capacity to explain every single
  Visualize property" and recommends inspecting real charts via the API. Useful
  context but not an exhaustive schema.

---

## Caveats

- The `chartTypes.ts` types do not include per-chart-type visualize interfaces.
  Per-chart-type fields (line vs column vs scatter) are inferred from the
  benchmark seed and from snippets/example charts, not from a typed schema.
- Datawrapper's official position is that `metadata.visualize` is intentionally
  not fully documented because it changes with chart type and feature flags.
  Treat anything labeled "folk" above as observation, not contract.
- The seed literal is for `d3-lines` specifically; column / bar / scatter
  defaults differ. Best practice when adding a new chart type to the skill: PUT
  a chart with `metadata.visualize: {}`, then GET it back — Datawrapper fills
  in defaults, and the response is the ground-truth schema for that type.
- Numbro is heavily implied as the format library (token shapes match) but
  Datawrapper's docs don't name it. Stick to documented format strings from
  the Academy custom-number-formats page.
- Range-annotation `position.y0`/`position.y1` accept `'-Infinity'`/`'Infinity'`
  as strings in observed payloads, but the type declares `number | string`
  without specifying the magic values — so this is folk knowledge.
