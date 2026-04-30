# Post Structure

The pattern Robert uses, distilled from his existing posts. Most posts
land in 50-100 lines (~500-1500 words) with 3-7 charts. Don't pad.

## The 5 parts

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HOOK    A personal observation, news item, Twitter      │
│            exchange, or "Mongolians often say X." Grounded │
│            in something real, not a thesis statement.      │
│                                                             │
│ 2. CLAIM   The question or assertion this post tests.      │
│            Stated explicitly. Often a question.            │
│                                                             │
│ 3. DATA    Where the data came from, with a hyperlink.     │
│            Mention the source in the same paragraph        │
│            you introduce it. Don't bury attribution.       │
│                                                             │
│ 4. ANALYSIS  Charts and walkthrough, one finding per       │
│              chart. Methodology shown when it matters,     │
│              hidden when it doesn't. Conversational, not   │
│              academic.                                     │
│                                                             │
│ 5. CLOSE   What does this mean? What's still uncertain?    │
│            Often closes with a deeper question rather      │
│            than a verdict.                                 │
└─────────────────────────────────────────────────────────────┘
```

## Hook — what works

Look at how existing posts open:

> "Just yesterday I learned that there has been a gasoline 'shortage' for a few weeks in Mongolia."
> — *Mongolia is running on fumes*

> "Any parent will tell you that having children is expensive."
> — *Do families with more children make less money?*

> "Since moving to Ulaanbaatar in 2013, I've been to nearly every market in the city."
> — *Which grocery store in Ulaanbaatar is cheapest?*

> "It's hard to think of something more at the core of society than the family dwelling."
> — *The rent is too darn high*

Patterns that recur:

- **Personal observation** — "I noticed", "I learned", "Since moving to UB"
- **Common belief** — "Any parent will tell you", "Mongolians often say"
- **News event** — "Following the Evergrande debt crisis", "On September 14, the government stated…"
- **Twitter prompt** — embed the actual tweet that motivated the post

Anti-pattern: starting with a thesis statement. ("This post will examine the relationship between…") Don't.

## Claim — make it testable

The claim should be a sentence you can *check against data*. Not an
opinion you hold. Examples that work:

- "Do families with more children make less money?" (yes/no with nuance)
- "Is there really a fuel shortage?" (the government said no; the data said yes)
- "Are meat prices outpacing inflation?" (was no, became yes)
- "Is UB really more expensive than NYC?" (Numbeo says so; let's verify)

Good test: if you can imagine a chart that would prove the claim wrong,
the claim is testable.

## Data — name it inline

When you introduce the data source, hyperlink it in the same paragraph:

> "I dug into the 2019 [Household Socioeconomic Survey][3] run by the National Statistics Office to answer this."

Don't dump all source links at the end like a bibliography. Inline,
where the reader needs them. (Footnote-style numbered links at the
bottom of the file are fine — they still render inline.)

The data sources Robert uses, in rough frequency order, are documented
in `data-sources.md`.

## Analysis — one finding per chart

Each chart should answer one small question. Walk through the math when
it matters; skip it when the chart speaks for itself. Look at how
*Mongolia is running on fumes* shows the AI-92 reserves chart, then
explicitly walks through the formula for projecting reserves forward —
because the math is the point. Compare to *Do families with more
children make less money?* which shows the wages-vs-children chart and
moves on — the chart speaks for itself.

Pattern: chart, one or two paragraphs of commentary on what it shows,
move on. Don't repeat in prose what the chart already shows visually.

If you have more than ~7 charts, the post is probably two posts.

## Close — leave a door open

Endings that work:

> "Whether the government's reserve meat program can meaningfully buffer against shocks of this scale is still not clear from the available data."
> — *Mongolian meat prices, seven years later*

> "We don't know yet whether those born in the baby bump (after 2003 or so, mainly Gen Z) will end up better off than their millennial parents."
> — *Do families with more children make less money?*

> "It seems fairly clear from the analysis above that the current shortage of fuel could have been seen as early as July/August this year."
> — *Mongolia is running on fumes*

The pattern: state what you found, name what you couldn't determine,
sometimes connect to a wider question. Don't moralize. Don't predict
with certainty.

## Length and rhythm

| Length (lines) | Examples |
|---|---|
| 25-50 | Quick takes (`a-world-where-ai-has-all-the-answers`, 25 lines) |
| 50-100 | Standard claim test (`mongolia-is-running-on-fumes`, 70) |
| 100-150 | Multi-faceted analysis (`which-grocery-store-in-ulaanbaatar-is-cheapest`, 147) |

Don't write longer than the analysis demands. Short posts published
beat long posts in drafts.

## Headers — optional, sparing

Some posts have `## Section` headers, some don't. Use them when the post
has clear acts (e.g., *Mongolia is running on fumes* uses *Fuel
Reserves*, *Fuel Reserve Projection*, *Hiding Risk*). Skip them when the
post is one continuous argument.

`####` works for tight section breaks within an act:

> #### Reporting Irregularity

## Voice — see `roberts-voice`

The full voice guide lives in the `roberts-voice` skill. The short
version, observed empirically:

- Plain English. Conversational, but not casual to the point of being
  glib.
- Willing to admit uncertainty: "I'm not sure what caused this." "The
  cause isn't clear."
- No moralizing. The data is the point.
- Honest about wrong predictions. Revisit posts say "what I got right
  and what I got wrong" explicitly.
- Avoid the academic register. No "this post will examine", no "in
  conclusion".
