# Pre-Publish Checklist

Read `principles.md` first. This is the operational checklist that turns
those principles into a publish/no-publish decision. Run it before every
`dw_publish.py`.

## The checklist

- [ ] Title states the finding, not the topic (`captions.md`).
- [ ] Intro specifies the unit and time frame.
- [ ] Source name and URL are populated.
- [ ] No more than 5 series in a line chart (else: small multiples).
- [ ] Y-axis starts at zero **unless** the context justifies a cut baseline.
- [ ] Column / bar chart **always** starts at zero.
- [ ] Primary series in blog accent (`#2b5cd6`); comparison in secondary (`#d4502a`).
- [ ] Time axis reads left-to-right, oldest first.
- [ ] Number formatting is human (`$1.2B`, not `1200000`).
- [ ] Annotations, if any, have padding and don't overlap data.
- [ ] No pie chart, no donut, no 3D, no dual y-axis.
- [ ] PNG-exported and visually checked (read the image).
- [ ] Mobile rendering checked at zoom=1 if there are >5 labels or >3 annotations.

## Zero baseline

### Column and bar charts — always zero.

Bars communicate magnitude by length. Clipping the baseline makes a 2%
increase look like a 30% increase. Datawrapper defaults columns to zero;
don't override unless you have a very good reason and a footer note.

### Line charts — usually, but not always.

Lines communicate change over time. The y-range should be wide enough
to show variation. For narrow-range series (interest rates, unemployment
between 3-10%), a zero baseline wastes vertical space and hides the story.

Rule of thumb:

- Y values 3% to 7% → tight range, hides nothing meaningful.
- Y values 0% to 100% → zero-baseline, the magnitude is the story.
- Indexed series → label the base year in the intro.

## Colors

- One dominant color. Blog accent (`#2b5cd6`) for the main series.
- Second color is comparison or counterfactual — secondary (`#d4502a`).
- Don't use color for decoration. Every color encodes something.
- Red-green together is bad for color-blind readers; pair warm + cool.
- Context-gray (`#a8b2c4`) for baselines and "rest of the field".

## Annotations

Use sparingly — 0-3 per chart. When you use them:

- Place in open space, not on top of data.
- Connect to the data point with a short line/arrow if needed.
- Use neutral color (`#60739f`), not the series color.
- Keep short — 1 line, 4-8 words.

Shaded range annotations are useful for recession bars, policy windows,
shortage periods, election years. Light gray with ~15% opacity so they
read as context, not data.

### Range annotations carry no built-in label

This bit me once: Datawrapper range annotations have **no `text` field**.
A shaded band is purely visual. To label a range, overlay a separate
text-annotation positioned inside the band — see
`references/datawrapper-fields.md` for the schema.

The skill handles this automatically: when you pass
`--annotate-range "X0|X1|TEXT"` with non-empty TEXT, the CLI auto-pairs
the band with a text label anchored at the left edge of the range, near
the top of the plot. Pass an empty TEXT (`X0|X1|`) for a plain band.

### Annotation vs direct line label collision

Line charts default to `labeling: "right"` — series names appear at the
right end of each line. If you place a text annotation near the line
endpoint, the two will overlap.

Two ways to fix:

- `--no-direct-labels` — suppress all auto-placed line labels (sets
  `labeling: "off"`). Use when you're hand-placing labels via text
  annotations or the line is already obvious from the title.
- `--label-margin 25` — keep auto labels but push them further right of
  the endpoint (default is ~5 px). Often enough to clear a nearby
  annotation without losing the labels.

Avoid placing text annotations at exactly the line endpoint when direct
labels are on. Move the annotation inboard (an interior data point) or
disable direct labels.

## Small multiples > busy chart

If a single chart has more than 5 lines, or the lines have very different
scales, split into small multiples (`multiple-lines`). Each panel reads
on its own.

## What to avoid

- **Pie charts and donuts.** Humans are bad at angle and area. Use a
  horizontal bar chart. No exceptions.
- **3D anything.** Perspective distorts comparisons.
- **Dual y-axes.** Readers infer correlation that may not exist. Show
  both series indexed to 100, or split into stacked panels.
- **Stacked lines.** The top line mixes its own value with everything
  below. Use small multiples or `multiple-lines` instead.

## Mobile

Datawrapper renders responsively. The only thing you can break is the
chart by cramming labels. If there are >5 labeled series or >3
annotations, export at zoom=1 to see what mobile readers see.

## When tempted to add a color

Don't. Fewer colors = cleaner chart. Reader attention is expensive. Add
color only when it encodes meaning.
