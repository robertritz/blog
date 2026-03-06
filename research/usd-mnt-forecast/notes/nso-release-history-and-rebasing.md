# NSO Release History And Rebasing: Clarification

## Can NSO API give full release-day history retroactively?

Short answer: **not directly**.

What the API provides:

- Table listing endpoints expose a single current `updated` timestamp per table.
- Data responses also include a current `updated` field.

What it does **not** provide:

- A built-in historical log of every past release/revision timestamp for that table.

So you can get the **latest update time now**, but not a full revision timeline back to the past unless you had been recording it.

## How to get vintage-safe release history from now on

- Poll `updated` for the exact table IDs daily (or more frequently around known release windows).
- Append snapshots to a local log.
- Use first-seen timestamps as your release-history proxy for out-of-sample backtests.

## Practical release-frequency inference for this project

Based on the latest `updated` timestamps already logged in `data/derived/nso_release_updates_log.csv`:

- Foreign trade tables were updated on `2026-02-09` and `2026-02-10`.
- CPI tables were updated on `2026-02-13`.
- Industry table was updated on `2026-02-16`.

This supports a practical first-pass assumption that these NSO tables are released on a roughly **monthly** cycle, typically in the **first half of the following month**.

For backtests, a reasonable conservative rule is:

- Monthly NSO indicators: available with a `1-month` lag.
- Quarterly indicators such as BoP: available with at least a `1-2 month` lag after quarter-end unless you have a better release log.

## What "rebasing / reference-year changes" means

Many NSO CPI tables contain a `Reference year` dimension (e.g., `2015=100`, `2020=100`, `2023=100`).

If you mix reference bases without handling, the series can have structural jumps and inconsistent levels.

For modeling, you should either:

1. Pick one base (recommended for first pass), or
2. Chain-link/reconstruct a consistent single-base index.

In this project, the extracted headline CPI file currently uses `2020=100` only.
