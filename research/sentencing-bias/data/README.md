# Sentencing Bias Dataset

Criminal court of first instance decisions from Mongolia (2020-2026).

## Quick Start

```python
import json

# Load extracted data
with open('processed/extracted.json') as f:
    cases = json.load(f)

print(f"Total cases: {len(cases)}")  # 80,827
```

## Files

| File | Description | Size |
|------|-------------|------|
| `case_ids.json` | All enumerated case IDs | 584 KB |
| `scrape_progress.json` | Collection progress/audit | 1 KB |
| `raw/{id}.json` | Raw scraped content (80,827 files) | 2.9 GB |
| `pilot/{id}.html` | Pilot sample HTML (500 files) | 47 MB |
| `processed/extracted.json` | Extracted structured data | 207 MB |

## Schema: extracted.json

Array of case objects with the following fields:

### Identifiers
| Field | Type | Description |
|-------|------|-------------|
| `case_id` | int | Unique case identifier from shuukh.mn |
| `case_index` | string | Court index number (e.g., "187/2024/0054/Э") |
| `case_number` | string | Case number |

### Case Metadata
| Field | Type | Description |
|-------|------|-------------|
| `court` | string | Court name |
| `judge` | string | Judge name |
| `prosecutor` | string | Prosecutor name |
| `case_date` | string | Decision date (YYYY-MM-DD or raw format) |
| `crime_article` | string | Criminal code article(s) |

### Defendant Demographics
| Field | Type | Description |
|-------|------|-------------|
| `gender` | string | "male" or "female" |
| `age` | int | Age at time of case |
| `birth_date` | string | Birth date (YYYY-MM-DD) |
| `education` | string | Education level (бага, суурь, бүрэн дунд, тусгай дунд, дээд) |
| `education_level` | int | Ordinal: 1=бага, 2=суурь, 3=бүрэн дунд, 4=тусгай дунд, 5=дээд |
| `occupation` | string | Occupation |
| `employed` | bool | Employment status |
| `employment_detail` | string | Employment detail |
| `family_size` | int | Household size |
| `num_children` | int | Number of children |
| `birth_place` | string | Place of birth |
| `residence` | string | Current residence |
| `prior_criminal` | bool | Prior criminal history |
| `prior_criminal_detail` | string | Details of prior history |

### Sentencing
| Field | Type | Description |
|-------|------|-------------|
| `sentence_type` | string | fine, imprisonment, suspended, probation, community_service |
| `sentence_months` | float | Imprisonment duration in months |
| `sentence_fine_mnt` | float | Fine amount in MNT |
| `sentence_fine_units` | int | Fine in legal units (нэгж) |
| `sentence_community_hours` | float | Community service hours |
| `sentence_suspended` | bool | Whether sentence is suspended |
| `sentence_rights_deprived` | string | Rights deprivation details |
| `sentence_raw` | string | Raw sentencing text (first 1000 chars) |

### Data Quality
| Field | Type | Description |
|-------|------|-------------|
| `data_quality_issue` | string | null=valid, "empty_decision"=no text at source, "short_text"=minimal content |

### Extraction Metadata
| Field | Type | Description |
|-------|------|-------------|
| `extraction_method` | string | "regex" or "regex+llm" |
| `extraction_notes` | string | Any extraction issues |

## Schema: raw/{id}.json

```json
{
  "table_html": "<table>...</table>",
  "text": "Full case text..."
}
```

- `table_html`: Metadata table from case page (court, judge, date, article)
- `text`: Plain text extracted from case content div

## Schema: case_ids.json

```json
{
  "ids": [123, 456, ...],
  "last_page": 4063
}
```

## Data Quality

2,859 cases (3.5%) have data quality issues and should be excluded from analysis:

| Issue | Count | Description |
|-------|-------|-------------|
| `empty_decision` | 2,715 | Metadata exists but no decision text at source |
| `short_text` | 144 | Minimal content (<300 chars) |

Filter for analysis: `[r for r in cases if r.get('data_quality_issue') is None]`

## Coverage

Coverage on valid cases (N=77,968, excluding data quality issues):

| Field | Coverage |
|-------|----------|
| court, judge | 100% |
| sentence_type | 70.3% |
| gender | 65.9% |
| education | 62.0% |
| age | 53.2% |
| prior_criminal | 22.3% |

## Date Range

- Query range: 2020-01-01 to 2026-02-04
- Actual case dates: 2020 to early 2026

## Source

- **Website:** https://shuukh.mn
- **Court category:** Criminal Court of First Instance
- **Collection date:** February 2026
- **Access:** Public (no authentication required)

## Reproduction

```bash
# Full collection pipeline
python3 scripts/collect_all_cases.py --step all

# Or individual steps
python3 scripts/collect_all_cases.py --step enumerate
python3 scripts/collect_all_cases.py --step scrape
python3 scripts/collect_all_cases.py --step extract
```

## License

This data is sourced from public court records. Use for research purposes.

## Citation

If you use this dataset, please cite:

```
[Citation to be added after publication]
```

---

*See `../docs/data_collection.md` for detailed collection methodology.*
