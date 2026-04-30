---
name: chart-maker
description: >
  DEPRECATED. Old matplotlib-based chart skill, kept only so old posts that
  reference its templates still build. For any new chart on robertritz.com,
  use the `blog-charts` skill (Datawrapper-based) instead. Do not trigger
  this skill on chart, charts, visualization, or data viz requests.
---

# Chart Maker (DEPRECATED)

> **Use `blog-charts` for all new charts.** This matplotlib skill is kept
> in place only so older posts that reference its templates and
> `swd.mplstyle` still build. The blog-charts skill (Datawrapper API,
> interactive iframes, slug registry) is the default for new work.

Create publication-quality charts using matplotlib, following *Storytelling With Data* (SWD) by Cole Nussbaumer Knaflic. Charts are visually harmonized with Robert's blog (robertritz.com).

## Iterative Workflow

1. **Write** — Adapt a template (see `templates/`) with the user's data. Load `swd.mplstyle`.
2. **Run** — Execute the script with `python script.py`.
3. **View** — Use the Read tool on the output PNG to see the chart.
4. **Assess** — Run through the self-assessment checklist below.
5. **Refine** — Fix any issues. Maximum 3 iterations, then ship.

Always start from the closest template. Never build from scratch.

## SWD Principles

### 1. Story titles, not label titles
Bad: "Revenue by Quarter"
Good: "Revenue doubled after the pricing change in Q3"

The title tells the reader what to see. The subtitle provides context (units, date range, source).

### 2. Gray first, accent for the story
Most data should be `CONTEXT` gray. Only the data that supports your title's claim gets `ACCENT` blue. This is the single most important SWD principle.

### 3. Eliminate clutter
- No gridlines unless they genuinely help (horizontal bars rarely need them; line charts sometimes do)
- No legend boxes — use direct labels on or near the data
- No borders, background fills, or tick marks
- No axis labels when the title or data labels make them obvious

### 4. Pre-attentive attributes
Use color, weight, and position (not decoration) to guide the eye. Bold the key number. Gray everything else.

### 5. Annotations over legends
Label the data directly. When a line or bar needs explanation, put text next to it, not in a separate legend box.

## Color Reference

```python
# Named constants — use these, not raw hex
ACCENT    = '#2b5cd6'   # Primary blue (blog-harmonized)
SECONDARY = '#d4502a'   # Warm complement (before/after, dual-series)
CONTEXT   = '#a8b2c4'   # Blue-tinted gray (context data)
TEXT_DARK  = '#1f1e1d'   # Titles
TEXT_MID   = '#60739f'   # Labels, annotations
TEXT_LIGHT = '#8895aa'   # Subtitles, footers
GRID       = '#e5e9f0'   # Gridlines (when needed)

# Extended palette (3+ series needing color distinction)
EXTENDED = ['#2b5cd6', '#d4502a', '#d4912a', '#2a8f5a', '#7b4ea3']
```

### Color rules
- **One series?** All bars/lines in `ACCENT`, or all in `CONTEXT` with the key item in `ACCENT`.
- **Two series?** `ACCENT` + `SECONDARY`. Or `ACCENT` + `CONTEXT` if one is background.
- **Highlighting one item in a group?** Everything `CONTEXT`, highlight item `ACCENT`.
- **Never** use more than 5 colors. If you need more, rethink the chart.

## Chart Anatomy

Every chart follows this structure:

```python
# Title — story, not label (bold, TEXT_DARK, 18pt)
fig.text(0.08, 0.95, "Story-driven title here",
         fontsize=18, fontweight='bold', color=TEXT_DARK,
         ha='left', va='top')

# Subtitle — context: units, date range, source (TEXT_MID, 13pt)
fig.text(0.08, 0.91, "Units | Date range | Source",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer — data source attribution (TEXT_LIGHT, 9pt)
fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')
```

Title and subtitle go above the axes (using `fig.text`, not `ax.set_title`), so they span the full figure width.

## Number Formatting

```python
def format_number(n, currency=None, decimals=0):
    """Format numbers with K/M/B suffixes."""
    if currency == 'MNT':
        symbol = '₮'
    elif currency == 'USD':
        symbol = '$'
    else:
        symbol = ''

    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        formatted = f"{n/1_000_000_000:.{decimals}f}B"
    elif abs_n >= 1_000_000:
        formatted = f"{n/1_000_000:.{decimals}f}M"
    elif abs_n >= 10_000:
        formatted = f"{n/1_000:.{decimals}f}K"
    else:
        formatted = f"{n:,.{decimals}f}"

    return f"{symbol}{formatted}" if symbol else formatted
```

## Chart Type Selection

| Data relationship | Chart type | Template |
|---|---|---|
| Compare categories | Horizontal bar | `horizontal_bar.py` |
| Compare over time (few periods) | Column/vertical bar | `column_bar.py` |
| Trend over time | Line chart | `line_chart.py` |
| Before/after or gap | Dumbbell | `dumbbell.py` |
| Correlation | Scatter | `scatter.py` |
| Multi-dimensional patterns | Heatmap | `heatmap.py` |

### Never use
- Pie or donut charts (use horizontal bar instead)
- 3D charts of any kind
- Dual-axis charts (use two panels instead)
- Radar/spider charts
- Word clouds

## Template Reference

Templates live in `.claude/skills/chart-maker/templates/`. Each is a standalone script with realistic sample data. Start from the closest match and adapt.

| Template | When to use | Key features |
|---|---|---|
| `horizontal_bar.py` | Comparing named categories | Sorted by value, direct value labels, gray-first with accent highlight |
| `column_bar.py` | Comparing across time periods or naturally-ordered categories | Vertical bars, optional group comparison |
| `line_chart.py` | Showing trends over time (1–3 series) | Direct end-labels, no legend box |
| `dumbbell.py` | Showing change between two points | Before/after with connecting lines |
| `scatter.py` | Showing correlation between two variables | Optional trend line, labeled outliers |
| `heatmap.py` | Multi-dimensional data grid | Sequential blue colormap, annotated cells |

## Loading the Style

```python
import matplotlib.pyplot as plt
from pathlib import Path

# Load style relative to this skill's location
style_path = Path(__file__).parent / 'swd.mplstyle'
# Or use absolute path:
style_path = Path.home() / 'projects/blog/.claude/skills/chart-maker/swd.mplstyle'
plt.style.use(str(style_path))
```

For scripts not in the skill directory, use the absolute path.

## Self-Assessment Checklist

After viewing each chart PNG, check:

### Must pass
- [ ] Title tells a story (not just a label)
- [ ] Gray-first coloring — most data is `CONTEXT`, accent highlights the story
- [ ] No chart junk: no unnecessary gridlines, borders, tick marks, or legends
- [ ] Text is legible at the output size
- [ ] Data labels are present where the exact value matters

### Should pass
- [ ] Subtitle provides context (units, date range, source)
- [ ] Footer credits data source
- [ ] Numbers use `format_number()` with appropriate suffixes
- [ ] Bars are sorted by value (horizontal bar charts)
- [ ] Lines have direct end-labels (line charts)

### Style pass
- [ ] Colors match the blog palette (no stray colors)
- [ ] Sufficient whitespace — chart doesn't feel cramped
- [ ] Annotation text uses `TEXT_MID` color
- [ ] Title uses `TEXT_DARK` color and is bold
