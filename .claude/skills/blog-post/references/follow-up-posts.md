# Follow-up Posts ("X Years Later")

A distinctive pattern Robert uses: revisiting an old post with fresh
data, being honest about what held and what didn't. The exemplar is
*Mongolian Meat Prices, Seven Years Later*, which revisits a 2019 post
with 2026 data and includes an explicit "What I got right and what I
got wrong" section.

Use the `--follow-up <old-post-slug>` flag with `new_post.py` to scaffold
this structure.

## Why this works

Most data writing is one-shot — publish a finding, move on. The
follow-up is rarer because it requires:

- An old post you can revisit
- The same (or comparable) data refreshed
- Willingness to publish what you got wrong

The third part is the hard one. Most writers retroactively justify their
old work. Robert's revisit posts work because they audit the old
analysis honestly — the meat prices revisit literally lists "what I got
right" and "what I got wrong" as a section.

## The structure

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HOOK    Open with the original prediction or claim.     │
│            "In 2019 I wrote that meat prices would drop.   │
│             They did. Then things got complicated."        │
│                                                             │
│ 2. WHAT'S CHANGED  What's new since the original — events, │
│            data, conditions. Pandemic, dzud, sanctions,    │
│            elections, etc.                                 │
│                                                             │
│ 3. RE-RUN  Walk through the same analysis with fresh data. │
│            Reuse the same chart types where possible — the │
│            visual continuity is the point. Each section    │
│            mirrors a section from the original.            │
│                                                             │
│ 4. AUDIT   Explicit "what I got right and what I got       │
│            wrong" section. Be specific. Bullet points are  │
│            fine. Don't hedge.                              │
│                                                             │
│ 5. NEXT    What new questions does this raise? What's      │
│            still unresolved? Sometimes ends by setting up  │
│            the *next* revisit.                             │
└─────────────────────────────────────────────────────────────┘
```

## What to scaffold from the original

When you start a follow-up:

1. Read the original post end-to-end. Note the claims, predictions, and
   chart structures.
2. Pull the same data sources, refreshed. Try to use the same NSO
   tables, the same column codes — visual continuity matters.
3. Make the same charts (using `blog-charts`) with updated data.
   Keep slugs parallel: if the original had `meat-prices--exports`,
   the follow-up has `meat-prices-2026--exports`.
4. Identify the predictions or claims that can be checked. If the
   original said "X will Y", note whether X actually Y'd.

## The audit section — how to write it

Look at the meat-prices revisit:

> **Right:** My forecast predicted prices would drop after the spring
> 2019 peak. They did. Animal losses remain the strongest predictor of
> price movements. Exports still don't correlate well with prices. Meat
> has continued to get more affordable as a share of income.
>
> **Wrong (or at least different now):** The inflation comparison
> reversed. In 2019, meat prices tracked below CPI. By 2026 they're
> well above it. The 2023/24 dzud was a supply shock large enough to
> break the pattern that had held for a decade.

Notes:

- Specific. Names the prediction, names the result, names the cause.
- Doesn't hedge. "Wrong" is the section header, not "less right than I
  thought."
- Distinguishes "wrong" from "the world changed" — the inflation
  comparison reversed because the underlying reality changed, not
  because the original analysis was flawed. Robert calls that out
  explicitly.

## Linking the original

Always link the original post in the first paragraph:

> "Back in May 2019 I wrote about [Mongolia's meat prices](/posts/mongolian-meat-price-time-series-forecast/), dug into the data on exports, animal losses, and inflation, and even made some forecasts about my predictions on meat prices going forward."

This signals continuity to readers and gets the right SEO crosslink.

## Title patterns that work

| Original | Follow-up |
|---|---|
| Mongolian Meat Prices, A Time Series Forecast (2019) | Mongolian Meat Prices, Seven Years Later (2026) |
| The rent is too darn high (2021) | The rent: still too darn high? (hypothetical) |
| Mongolia is running on fumes (2021) | Mongolia, four years on: did the fuel shortage repeat? (hypothetical) |

Patterns:

- Same noun phrase, with a temporal qualifier ("Seven Years Later",
  "Revisited", "Still…?")
- Question-form follow-ups when the original was a statement; statement-
  form follow-ups when the original was a question

## When NOT to do a follow-up

- The original analysis was wrong in a way that's already obvious. Just
  publish the corrected version as a new post and link to the original
  as "I previously argued X, which was wrong because Y."
- Less than ~2 years has passed and nothing has substantially changed.
  Wait for a real signal before revisiting.
- The data series is broken or methodologically incompatible with the
  original. The follow-up depends on apples-to-apples comparison.

## Scaffolding shortcut

`new_post.py --follow-up <old-slug>` does the following:

1. Reads the old post's frontmatter (title, tags, sources).
2. Pre-fills the new post's frontmatter with the same tags, plus
   `["follow-up"]`.
3. Adds a starter MDX comment block in the body that links to the
   original and stubs out the 5-part follow-up structure.
4. Creates `research/<new-slug>/` with a `prior-post.md` symlink to the
   original (so refresh data scripts can reference the old analysis).
