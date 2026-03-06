# NSO Table Shortlist (via `datamn-source-nso`)

This shortlist focuses on series useful for 1-3 month USD/MNT forecasting.

## Recommended Core Tables

1. **Monthly foreign trade (non-cumulative)**
- Table ID: `DT_NSO_1400_003V1.px`
- Subsector: `Economy, environment / Foreign Trade`
- Why: direct monthly `Exports`, `Imports`, `Balance` and `Total turnover`.

2. **Headline CPI inflation (y/y)**
- Table ID: `DT_NSO_0600_010V1.px`
- Subsector: `Economy, environment / Consumer Price Index`
- Why: monthly inflation rate by group; includes `Overall index`.

3. **Headline CPI inflation (m/m)**
- Table ID: `DT_NSO_0600_009V1.px`
- Subsector: `Economy, environment / Consumer Price Index`
- Why: monthly percent change; useful for near-term pressure proxies.

4. **Gross industrial output by subdivision (monthly)**
- Table ID: `DT_NSO_1100_001V2.px`
- Subsector: `Industry, service / Industry`
- Why: includes `Total` and `Mining and quarrying` (activity proxy).

## Optional Supplemental Tables

5. **Industrial production index, 2015=100 (monthly)**
- Table ID: `DT_NSO_1100_016V5.px`
- Why: index version of production dynamics.

6. **Seasonally adjusted industrial production index, 2015=100 (monthly)**
- Table ID: `DT_NSO_1100_015V12.px`
- Why: cleaner short-horizon signal in some specifications.

7. **Terms of trade index (monthly)**
- Table ID: `DT_NSO_1100_015V3_1.px`
- Subsector: `Economy, environment / Foreign Trade`
- Why: strong external-price channel for MNT.

## Commands (using your skill)

All commands below save into this research folder, not into the skill folder.

```bash
python3 /Users/ritz/projects/data/.claude/skills/datamn-source-nso/fetch_data.py \
  --table DT_NSO_1400_003V1.px --lang en \
  --output /Users/ritz/projects/blog/research/usd-mnt-forecast/data/raw/nso

python3 /Users/ritz/projects/data/.claude/skills/datamn-source-nso/fetch_data.py \
  --table DT_NSO_0600_010V1.px --lang en \
  --output /Users/ritz/projects/blog/research/usd-mnt-forecast/data/raw/nso

python3 /Users/ritz/projects/data/.claude/skills/datamn-source-nso/fetch_data.py \
  --table DT_NSO_0600_009V1.px --lang en \
  --output /Users/ritz/projects/blog/research/usd-mnt-forecast/data/raw/nso

python3 /Users/ritz/projects/data/.claude/skills/datamn-source-nso/fetch_data.py \
  --table DT_NSO_1100_001V2.px --lang en \
  --output /Users/ritz/projects/blog/research/usd-mnt-forecast/data/raw/nso
```

## What You Can Collect Manually (Priority)

1. Release schedule and release-day history for the specific NSO tables above.
2. Definitions/metadata notes for rebasing changes (`Reference year` fields in CPI tables).
3. Any methodological break notes (e.g., table version changes from `V1` to `V2`).

These are important for realistic vintage-consistent forecasting backtests.
