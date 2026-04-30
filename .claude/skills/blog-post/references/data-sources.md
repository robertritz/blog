# Data Sources

The sources Robert reaches for, in rough order of frequency. Always
check **data.mn** first — it's a curated portal that may already have
the dataset cleaned up.

## data.mn (check first)

Robert's own statistics portal at `~/projects/data/`. Pulls Mongolian
public data into clean CSVs with a registry, version history, and chart
metadata. If a dataset you need is in the data.mn registry, use that
version — saves you the cleaning step.

- Registry: `~/projects/data/tools/registry/`
- Project CLAUDE.md: `~/projects/data/CLAUDE.md`
- Slash command to check: `/data-status` (in the data.mn repo)

If data.mn doesn't have what you need, fall back to the primary source
below.

## NSO — National Statistics Office (1212.mn)

The workhorse. Used in nearly every post.

- **URL**: <https://www.1212.mn/> (also <https://1212.mn>)
- **English mirror of tables**: append `?lang=en` or use the EN toggle
- **NADA microdata catalog**: <http://web.nso.mn/nada/>
- **Format**: tables (web/CSV), microdata (Stata/SPSS), some PDFs

Common categories Robert pulls from:

| Topic | NSO category / table |
|---|---|
| Wages and salaries | `0400-021` series |
| Consumer prices, weekly market prices | `0600-013`, `0600-019` |
| Population and demographics | `0100-t0023`, fertility series |
| Livestock | `1001-029` (animal losses), `1001-109` |
| Trade (exports/imports by commodity) | `1400-006` |
| Household Socioeconomic Survey | NADA catalog 121 |

Practical notes:

- Tables often have a "Region" filter — `Ulaanbaatar` returns NaNs
  on some tables; use `Ulaanbaatar city`. Always sanity-check by
  loading and looking.
- Tables labeled `v1`, `v2` are version revisions. Check release dates.
- Some pages are Mongolian-only. The English toggle doesn't always work
  for the deepest catalog levels.
- The "Statistical book" and weekly price reports live under
  `1212.mn/BookLibrary.aspx?category=...` — non-obvious URL, hidden
  from main navigation.

Cite as: `[National Statistics Office of Mongolia](https://1212.mn)` or
`[NSO](https://www.1212.mn/)`.

## Mongolbank

Exchange rates, money supply, banking-sector data.

- **URL**: <https://www.mongolbank.mn/>
- **Common pages**: official daily exchange rate, monetary statistics,
  banking sector indicators
- **Format**: web tables, some Excel downloads

Used for: USD/MNT, CNY/MNT, M2 money supply, lending rates.

Cite as: `[Mongolbank](https://www.mongolbank.mn/)`.

## MRPAM — Mineral Resources and Petroleum Authority

Fuel reserves, petroleum imports, mining data.

- **URL**: <https://mrpam.gov.mn/>
- **Format**: monthly PDF reports — *requires copy-paste or PDF parsing*

Used in: *Mongolia is running on fumes*. The fuel reserve and import
tables are inside the monthly statistical report PDFs. Robert literally
copy-pasted the numbers in the original post.

Heads up: MRPAM has historically been late with updates and has changed
chart conventions mid-stream (year-over-year vs month-over-month
comparisons). Worth noting in the post if it affects analysis.

Cite as: `[Mineral Resources and Petroleum Authority of Mongolia](https://mrpam.gov.mn/)`
or `MRPAM`.

## World Bank

International comparisons. Mongolia's place in the world.

- **URL**: <https://data.worldbank.org/>
- **API**: <https://api.worldbank.org/v2/>
- **Format**: web (CSV download per indicator), API (JSON/XML)

Used for: fertility rate, GDP, comparative country indicators (Mongolia
vs Kazakhstan vs Russia, etc.).

Indicator codes: e.g. `SP.DYN.TFRT.IN` (fertility rate). Append country
codes via `?locations=MN-KZ-RU-KG`.

Cite as: `[World Bank][n]` with the indicator-specific URL.

## Numbeo

Crowdsourced cost-of-living and price data. Useful when you need a
single number for international comparison and the official sources
don't agree on methodology.

- **URL**: <https://www.numbeo.com/>
- **Format**: web only, no public API on free tier

Used in: *The rent is too darn high* (price-to-income ratio benchmark).
Robert's typical move: cite Numbeo's number, then recalculate with
local data to verify.

Cite as: `[Numbeo](https://www.numbeo.com/)`. Mention methodology in the
post — Numbeo's calculations have non-obvious assumptions.

## shuukh.mn — Supreme Court records

Public criminal case decisions. Used in `research/sentencing-bias/`.

- **URL**: <https://shuukh.mn/>
- **Format**: HTML pages with structured tables + free-text descriptions
- **Access**: scrape (no public API documented)

Cite as: `[shuukh.mn](https://shuukh.mn/)` and link the original case
list page.

## Twitter / X

Used as a *source of prompts* and occasionally as a citation when
responding to a specific tweet. Embed the actual tweet HTML when
responding:

```html
<blockquote class="twitter-tweet"><p lang="en" dir="ltr">...</p>&mdash;
  Username (@handle) <a href="https://twitter.com/...">date</a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
```

In `.mdx` posts this works inline. Robert has a habit of opening posts
with the tweet that prompted them.

## Other Mongolian sources used occasionally

- **Statista** — `https://www.statista.com/` — secondary aggregator,
  sometimes useful for population by age group, market shares.
- **MIK Group** (apartment price index) — referenced in *The rent is too
  darn high* via Twitter.
- **Tenkhleg Zuuch** — UB real-estate data, accessed via Twitter
  contacts.
- **Montsame** — `https://montsame.mn/` — state news agency, used to
  cite government statements.

## When the source is "I made this up from raw data"

Sometimes the analysis combines several sources or is the first time a
ratio has been computed. Cite the *inputs*, not the output:

> "All data in this post comes from Mongolia's [National Statistics Office](https://1212.mn) (1212.mn)."

— *Mongolian meat prices, seven years later*

Or list each source used at the end. Don't claim "Source: Robert Ritz"
unless the data really is original (e.g., the SQAir test).

## Linking style

Prefer **inline footnote-numbered links** for posts with many sources:

```markdown
according to [World Bank data][2]

[1]: https://data.worldbank.org/indicator/SP.DYN.TFRT.IN?locations=MN
[2]: https://data.worldbank.org/indicator/SP.DYN.TFRT.IN?locations=MN-KZ-RU-KG
```

Or **inline parenthetical links** for posts with 1-2 sources:

```markdown
the [Household Socioeconomic Survey](http://web.nso.mn/nada/index.php/catalog/121)
```

Either works. Match the rest of the post.
