# Data Collection Report

Technical appendix documenting the full data collection process for the sentencing bias study.

## Executive Summary

| Metric | Value |
|--------|-------|
| Total cases enumerated | 80,827 |
| Cases successfully scraped | 80,827 (100%) |
| Cases extracted | 80,827 (100%) |
| Date range queried | 2020-01-01 to 2026-02-04 |
| Collection period | 2026-02-04 to 2026-02-09 |
| Raw data size | 2.9 GB |
| Extracted data size | 207 MB |

## Data Source

- **Source:** shuukh.mn (Supreme Court of Mongolia public database)
- **Endpoint (enumeration):** `GET https://shuukh.mn/site/case_ajax`
- **Endpoint (case detail):** `GET https://shuukh.mn/single_case/{case_id}`
- **Court category:** Criminal Court of First Instance (`court_cat=2`)
- **Authentication:** None required (public data)

## Collection Process

### Phase 1: Enumeration

**Objective:** Discover all available case IDs within the date range.

**Method:** Paginated API requests (20 cases per page)

**Parameters:**
- `daterange`: `2020/01/01 - 2026/02/04`
- `court_cat`: `2` (criminal first instance)
- `bb`: `1`

**Results:**
- Total pages enumerated: 4,063
- Unique case IDs discovered: 80,827
- Duration: ~35 hours (API response time ~40s per page)

**Code:** `src/scraper.py::enumerate_all_case_ids()`

### Phase 2: Scraping

**Objective:** Fetch HTML for each case and extract usable content.

**Method:** Individual HTTP requests with rate limiting (1.5-3.0s between requests)

**Storage format:** JSON files with structure:
```json
{
  "table_html": "<table>...</table>",  // Metadata table (court, judge, date, article)
  "text": "..."                        // Full case text (bio, facts, decision)
}
```

**Rationale for format:** Raw HTML pages averaged 64-165 KB each, but 70% was navigation, scripts, and styling. Stripping to table + text reduced storage from ~8 GB to 2.9 GB while preserving all extractable information.

**Results:**
| Category | Count |
|----------|-------|
| Newly scraped | 77,372 |
| Skipped (from pilot) | 3,455 |
| Initially failed | 4 |
| Retried successfully | 4 |
| **Total on disk** | **80,827** |

**Initially failed cases:**
- Case IDs: 39872, 42362, 47747, 120039
- Failure reason: HTTP 500 errors (server-side, all 3 retry attempts failed)
- Resolution: Retried on 2026-02-09, all 4 succeeded
- Root cause: Likely temporary server issues during original scrape window

**Duration:** ~4.5 days (API response time ~50s per case)

**Code:** `src/scraper.py::scrape_cases()`

### Phase 3: Extraction

**Objective:** Parse structured and semi-structured data from case content.

**Method:** BeautifulSoup for HTML parsing + regex patterns for Mongolian text

**Structured fields (from table_html):**
- `court`, `judge`, `case_date`, `case_number`, `case_index`, `crime_article`, `prosecutor`

**Semi-structured fields (from text via regex):**
- Demographics: `gender`, `age`, `birth_date`, `education`, `occupation`, `employed`, `family_size`, `birth_place`, `residence`, `prior_criminal`
- Sentencing: `sentence_type`, `sentence_months`, `sentence_fine_mnt`, `sentence_fine_units`, `sentence_community_hours`, `sentence_suspended`, `sentence_rights_deprived`

**Results:**
- Total cases extracted: 80,827
- Output file: `data/processed/extracted.json` (207 MB)

**Code:** `src/extractor.py::extract_case()`, `process_batch()`

## Data Quality Audit

Not all scraped cases contain usable decision text. Some cases in the shuukh.mn database have metadata (court, judge, date, crime article) but the actual decision text was never uploaded.

| Category | Count | % | Notes |
|----------|-------|---|-------|
| Valid content | 77,968 | 96.5% | Full decision text available |
| Empty decision | 2,715 | 3.4% | Metadata only, no decision text at source |
| Short text | 144 | 0.2% | Minimal content (<300 chars) |

**Empty decision cases:** These return HTTP 200 with valid metadata table, but `div#source-html` (the decision text container) is empty on the live website. This is a source database issue, not a scraping error. Verified by re-checking sample cases on 2026-02-09.

**Recommendation:** Exclude 2,859 cases with `data_quality_issue` flag from analysis.

## Extraction Coverage

### All cases (N=80,827)

| Field | Count | Coverage |
|-------|-------|----------|
| court | 80,827 | 100.0% |
| judge | 80,827 | 100.0% |
| crime_article | 78,920 | 97.6% |
| sentence_type | 54,826 | 67.8% |
| gender | 51,354 | 63.5% |
| education | 48,371 | 59.8% |
| age | 41,490 | 51.3% |
| prior_criminal | 17,380 | 21.5% |

### Valid cases only (N=77,968)

Excluding cases with `data_quality_issue`:

| Field | Count | Coverage |
|-------|-------|----------|
| court | 77,968 | 100.0% |
| judge | 77,968 | 100.0% |
| sentence_type | 54,828 | 70.3% |
| gender | 51,355 | 65.9% |
| education | 48,372 | 62.0% |
| age | 41,493 | 53.2% |
| prior_criminal | 17,381 | 22.3% |

**Note on coverage rates:** Coverage on valid cases (~66-70% for key fields) is closer to pilot validation rates (~69-71%). Remaining gaps are due to:
1. Non-standard bio section formats
2. Multi-defendant cases where first defendant parsing fails
3. Cases using different Mongolian phrasing patterns

LLM-based extraction for missing fields is planned as a potential Phase 2 enhancement.

## Data Distribution

### Temporal Distribution

| Year | Cases |
|------|-------|
| 2020 | 13,267 |
| 2021 | 12,082 |
| 2022 | 13,277 |
| 2023 | 13,121 |
| 2024 | 14,131 |
| 2025 | 14,682 |
| 2026 | 263 |

### Court Distribution (Top 10)

| Court | Cases |
|-------|-------|
| Баянзүрх дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 8,135 |
| Сонгинохайрхан дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 7,007 |
| Сүхбаатар дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 5,266 |
| Баянгол дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 4,890 |
| Чингэлтэй дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 4,409 |
| Хан-Уул дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 4,030 |
| 2025 - Баянзүрх, Сүхбаатар, Чингэлтэй дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 2,954 |
| Дархан-Уул аймаг дахь сум дундын анхан шатны шүүх | 2,950 |
| Төв аймаг дахь сум дундын анхан шатны шүүх | 2,950 |
| 2025 - Баянгол, Хан-Уул, Сонгинохайрхан дүүргийн Эрүүгийн хэргийн анхан шатны шүүх | 2,749 |

Total unique courts: 49

### Sentence Type Distribution

| Type | Cases |
|------|-------|
| fine | 42,339 |
| imprisonment | 6,209 |
| community_service | 5,165 |
| suspended | 1,049 |
| probation | 64 |
| *(missing)* | 26,001 |

### Gender Distribution

| Gender | Cases |
|--------|-------|
| male | 43,896 |
| female | 7,458 |
| *(missing)* | 29,473 |

### Age Distribution

- Count: 41,490 cases with valid age
- Range: 10-87 years
- Mean: 35.2 years

## File Inventory

```
data/
├── case_ids.json           # 584 KB - Enumerated IDs {"ids": [...], "last_page": 4063}
├── scrape_progress.json    # Progress tracker with final counts
├── raw/                    # 2.9 GB - 80,827 JSON files
│   ├── {case_id}.json      # {"table_html": "...", "text": "..."}
│   └── ...
├── pilot/                  # 47 MB - 500 HTML files (original pilot)
│   ├── {case_id}.html
│   └── ...
└── processed/
    └── extracted.json      # 207 MB - Extracted structured data
```

## Reproducibility

### To reproduce enumeration:
```bash
cd /home/ritz/projects/research/sentencing-bias
python3 scripts/collect_all_cases.py --step enumerate
```

**Note:** Results may differ if the database has been updated since 2026-02-04.

### To reproduce scraping:
```bash
python3 scripts/collect_all_cases.py --step scrape
```

**Note:** Scraping skips existing files, so re-running will only fetch new cases.

### To reproduce extraction:
```bash
python3 scripts/collect_all_cases.py --step extract
```

### Full pipeline:
```bash
tmux new-session -d -s sentencing "bash scripts/run_collection.sh"
```

### Key parameters (in `src/scraper.py`):
- `DEFAULT_DATERANGE = "2020/01/01 - 2026/02/04"` — Fixed study population
- `MIN_DELAY = 1.5`, `MAX_DELAY = 3.0` — Rate limiting (seconds)
- Timeout: 60 seconds per request
- Retries: 3 attempts per request

## Known Issues

1. **Empty decision cases (2,715):** These cases have metadata but no decision text at the source. Flagged with `data_quality_issue = "empty_decision"`. Should be excluded from analysis.

2. **Short text cases (144):** Minimal content, likely incomplete uploads. Flagged with `data_quality_issue = "short_text"`. Should be excluded from analysis.

3. **Court name changes:** Some courts appear with different names after 2025 reorganization (e.g., "2025 - Баянзүрх, Сүхбаатар, Чингэлтэй дүүргийн..."). May need normalization.

4. **Crime article formatting:** 2,085 unique article strings due to inconsistent formatting. Will need standardization for analysis.

## Changelog

| Date | Event |
|------|-------|
| 2026-02-04 | Enumeration started |
| 2026-02-05 | Enumeration complete (80,827 IDs) |
| 2026-02-05 | Scraping started |
| 2026-02-08 | Scraping complete (4 failures) |
| 2026-02-08 | Extraction complete |
| 2026-02-09 | 4 failed cases retried and recovered |
| 2026-02-09 | Documentation complete |

---

*Generated: 2026-02-09*
*Code version: git commit [to be added]*
