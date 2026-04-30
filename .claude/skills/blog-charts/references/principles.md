# Data Visualization Principles

Distilled from *Storytelling with Data* (Cole Nussbaumer Knaflic) and the
practice of The Economist's data team. These are the guiding principles
for every chart on robertritz.com — read this before drafting the title.

## The North Star

A chart should deliver its main message in under five seconds.
Everything else is in service of that message — or it's noise.

## Core Principles

### 1. Start with the question, not the chart

Before opening any tool, write down: who's reading this, what's the one
thing you want them to know, what shift in thinking should it cause? If
you can't say it in a sentence, the chart isn't ready. (Knaflic calls
this "the Big Idea.")

### 2. Match the chart type to the relationship

Trends over time → line. Comparisons across categories → bar. Distributions
→ histogram or dot plot. Part-to-whole → stacked bar (rarely pie).
Correlations → scatter. The chart's geometry should mirror the structure
of the message. See `chart-types.md` for the full decision guide.

### 3. Declutter ruthlessly

Every pixel that isn't carrying meaning is taxing the reader. Remove
chart borders, drop the legend if you can label directly, kill vertical
gridlines, lighten horizontal ones, strip non-data ink. If removing
something doesn't change the message, it shouldn't be there. Datawrapper's
defaults are already strong — don't add ornamentation back.

### 4. Direct the eye with preattentive attributes

Color, weight, and position decide where readers look before they think.
Use one strong accent color for the data point that matters and push
everything else to context-gray. Bold the number that's the headline.
When everything is highlighted, nothing is.

### 5. Title with a stance

The title states the finding ("Mongolian meat prices have doubled in
five years"), not the topic ("Meat price index over time"). The subtitle
handles the dry-but-essential metadata: what's measured, the unit, the
geography, the time window. This is how readers "understand the chart at
a glance." See `captions.md` for examples.

### 6. Label directly, not in a legend

Legends force readers to bounce between key and chart. Put country names
at the end of lines, category names on bars, and call out the value of
the bar that matters. Reserve legends for cases where direct labeling
is genuinely impossible (e.g., five overlapping series with similar
endpoints).

### 7. Annotate the why, not the what

A small text callout that explains the spike ("Russia invades Ukraine")
earns its keep. A label that just restates the y-axis value usually
doesn't. Annotations are where the chart becomes journalism.

### 8. Be honest with axes

Bar charts must start at zero — truncating distorts comparisons of length.
Line charts can start elsewhere if it serves clarity, but make the choice
deliberately and state it in the intro if it's unusual ("Index, 2020 = 100").
Use round, sensible tick values. Avoid dual y-axes — they almost always
mislead readers into inferring spurious correlation.

### 9. Use color sparingly and with purpose

Two or three colors beats a rainbow. Reserve a single accent color for
the data the reader should look at; render everything else in greys.
Maintain a consistent palette across charts in the same post so the
reader builds intuition. The blog's palette is in `styling.md`.

### 10. Cite the source, every time

A small "Source: …" line at the bottom is a credibility signal and a
journalistic obligation. Add a footer note for non-obvious methodology
(e.g., "Excludes seasonally adjusted figures").

### 11. Pre-flight test the chart

Before publishing, export a PNG and read it as if you'd never seen the
data. What lands first? What's confusing? Iterate on the chart, not on
the explanation around it. The skill's `dw_export.py` exists for this
exact step.

## What to Avoid

- Pie charts with more than two slices (humans are bad at angle / area)
- Donut charts, radar charts, word clouds
- 3D, shadows, gradients, drop-shadows
- Dual y-axes (unless plotting the same unit at two scales)
- Truncated y-axes on bar charts
- Rainbow palettes when one accent would do
- Legends when direct labels would work
- Red-green pairings (color-blindness) — use blue-orange or red-grey
- Titles that describe the data instead of stating the finding
- Decorative chart junk (backgrounds, clipart, fills)

## Quick Checklist Before You Publish

- [ ] Title states the finding (not the topic).
- [ ] Subtitle gives the unit and time window.
- [ ] One accent color for the focal data; everything else gray.
- [ ] Source attribution present.
- [ ] Bar chart starts at zero.
- [ ] No more than 5 series in a line chart (else: small multiples).
- [ ] PNG-exported and read back to verify it lands in 5 seconds.

## Source Notes

- Cole Nussbaumer Knaflic, *Storytelling with Data* (2015) — the
  "what to say" framework, decluttering, preattentive attributes.
- The Economist's data team — chart titles that take a stance, off-white
  plot backgrounds (`#fafaf7`-ish), small accent rectangles for branding,
  sparse axes, integer ticks, direct labels over legends.
- Sarah Leo's "Mistakes, we've drawn a few" (2019) categorizes bad
  charts as misleading, confusing, or failing to make a point. Worth
  re-reading when a chart isn't working.
