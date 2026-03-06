# Series To Collect

## Confirmed Mongolbank Endpoints

### FX rates (official)
- Daily: `POST https://www.mongolbank.mn/en/currency-rate-movement/data`
- Monthly: `POST https://www.mongolbank.mn/en/currency-rate-movement/data/monthly`
- REER/NEER: `POST https://www.mongolbank.mn/en/neer-reer/data`

### BoM statistics API
- Report tree (external sector group):
  - `POST https://stat.mongolbank.mn/api/report/list?lang=en&parentId=20`
- Indicator list for BoP standard:
  - `POST https://stat.mongolbank.mn/api/indicator/list?lang=en&reportId=1104`
- Indicator data fetch:
  - `POST https://stat.mongolbank.mn/api/indicator/data?lang=en`
- Release calendar:
  - `POST https://stat.mongolbank.mn/api/schedule/data?lang=en&startdate=YYYY-MM-DD&enddate=YYYY-MM-DD`

## Suggested BoP Standard Indicator IDs (`reportId=1104`)
Use these first for the blog post model.

- `121832`: I. Current account
- `121838`: Goods
- `121851`: Services
- `121999`: Primary income
- `122089`: Secondary income
- `122108`: II. Capital account
- `122135`: Net lending/borrowing (current+capital)
- `122137`: III. Financial account
- `122138`: Direct investment
- `122161`: Portfolio investment
- `122237`: Other investment
- `122347`: Reserve assets
- `122364`: Net errors and omissions

## Optional Detail IDs
- `121833`: Current account credit
- `121834`: Current account debit

## NSO Items To Collect Manually (First Pass)
- CPI all-items monthly level/index
- Export and import value monthly
- Mining output monthly (or mining production index)
- Any official macro forecast tables (exchange rate assumptions)

## Data-Lag Conventions To Track
For each series, record:
- `period` (e.g., 2025-10)
- `release_date` (when it became public)
- `vintage` (if revised)

Without this, a 1-3 month forecast backtest can be unintentionally look-ahead biased.
