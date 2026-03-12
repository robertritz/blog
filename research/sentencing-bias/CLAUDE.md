# Sentencing Bias in Mongolian Criminal Courts

## Data Status

**COLLECTION & EXTRACTION COMPLETE** (as of 2026-02-11)

| Metric | Value |
|--------|-------|
| Total cases | 80,827 |
| Valid for analysis | 77,968 (96.5%) |
| LLM extracted | 77,364 (99.2% of valid) |
| LLM errors | 4 (0.005%) |
| Data quality issues | 2,859 (3.5%) — flagged, exclude |
| Raw data | 2.9 GB |
| Extracted data | 207 MB |

**Extraction method:** Dual — regex baseline + Grok 4.1 Fast LLM (xAI Batch API, 78 batches)
- LLM values are primary in `extracted.json`; regex values preserved as `regex_*` columns
- LLM cost: ~$161 (batch API with 50% discount)
- Model: `grok-4-1-fast-non-reasoning` via `xai-sdk`

**Field coverage (post-LLM merge):**

| Field | Coverage | Source |
|-------|----------|--------|
| sentence_type | 76,513 (98.2%) | LLM |
| prior_criminal | 68,402 (87.7%) | LLM (was 22% regex) |
| gender | 68,473 (87.8%) | LLM |
| employed | 56,606 (72.6%) | LLM (new) |
| education | 52,448 (67.3%) | LLM |
| family_size | 50,509 (64.8%) | LLM (new) |
| occupation | 46,778 (60.0%) | LLM (new) |
| age | 44,654 (57.3%) | LLM |
| sentence_fine_mnt | 42,871 (55.0%) | LLM |
| sentence_months | 15,010 (19.3%) | LLM (new) |

**Data quality flags** (in `extracted.json`):
- `data_quality_issue = null` → Valid, use for analysis
- `data_quality_issue = "empty_decision"` → No text at source (2,715)
- `data_quality_issue = "short_text"` → Minimal content (144)
- `extraction_quality = "complete" | "partial" | "unreliable"` → LLM confidence

**Key files:**
- `data/processed/extracted.json` — All extracted data (LLM primary, regex backup)
- `data/processed/llm_extraction_results.json` — Raw LLM outputs (77,364 results)
- `data/batch_progress.json` — Batch tracking (78 batches)
- `data/scrape_audit.json` — Quality audit results
- `docs/data_collection_report.md` — Technical documentation

**Date range:** 2020-01-01 to 2026-02-04 (fixed study population)

## Task Tracking

Primary tracker: **`todo.md`** in this directory. High-level milestones also tracked in todo.robertritz.com (project: sentencing-bias).

## Paper Info

- **Slug:** sentencing-bias
- **Working Title:** Demographic Bias in Criminal Sentencing: Evidence from Mongolian Courts
- **Created:** 2026-02-03
- **Status:** Analysis Complete, ready for writing

## Research Question

Is there systematic bias in criminal sentencing in Mongolia based on defendant demographics (age, gender, education, occupation)?

## Data Source

- **URL:** https://shuukh.mn/cases/2/1 (Criminal Court of First Instance)
- **API:** `GET https://shuukh.mn/site/case_ajax`
- **Target:** All criminal first instance cases (cutoff: 2026-02-04)

## Journal Target

**Primary:** Asian Journal of Criminology (IF 1.4, Q1, Springer)

**Submission Strategy:**
1. Start with: Asian Journal of Criminology
2. If rejected: International Journal of Comparative and Applied Criminal Justice
3. Safety option: Quality & Quantity

See `journal-recommendations.md` for full analysis.

## Decision Log

| Date | Decision Type | Decision | Rationale |
|------|--------------|----------|-----------|
| 2026-02-03 | Project Setup | Created paper folder structure | Starting sentencing bias research |
| 2026-02-03 | Evaluation | Proceed | Novel (first Mongolian study), feasible (public data), moderate-high significance. Key precedent: Zhuchkova/Kazun 2023 Russia study. |
| 2026-02-03 | Journal | Selected Asian Journal of Criminology as primary target | Best scope fit (Asia-focused criminology), Q1 quartile, explicit interest in quantitative empirical research, no APC for standard submission |
| 2026-02-03 | Methodology | OLS with robust SE + multilevel robustness | Continuous severity scale DV, Python stack, OSF pre-registration, all available cases |
| 2026-02-03 | Pre-registration | Submitted to OSF (embargo until June 2026) | H1-H4 locked in before data collection |
| 2026-02-04 | Extraction | Gender fix: bio-section isolation for multi-defendant cases | Naive full-text search misclassified 14/500 cases; isolating first defendant's paragraph fixed it |
| 2026-02-04 | Extraction | Age range filter (10-100) | Excluded victim ages and parsing artifacts (0, 1, 5, 9) |
| 2026-02-04 | Extraction | Education proximity check for short patterns | Short patterns like "дээд" required nearby "боловсрол" to avoid false matches |
| 2026-02-04 | Extraction | Added "бүрэн бус дунд боловсролтой" variant | Variant form found in real data, maps to "бүрэн дунд" |
| 2026-02-04 | Validation | 200-case validation passed all fields >90% | gender 94.3%, age 97.0%, education 97.2%, sentence_type 92.1%, fine 95.2% |
| 2026-02-04 | Extraction | Regex-only sufficient — no LLM needed | All accuracy thresholds met without Claude API calls |
| 2026-02-04 | Storage | JSON format instead of raw HTML | 70% size savings (33MB→10MB for 500 cases); stores table_html + text only |
| 2026-02-04 | Collection | Full pipeline: enumerate→scrape→extract | 80,827 total cases; resumable enumeration and scraping; API ~40s/page |
| 2026-02-09 | Collection | Data collection complete | 80,827 cases scraped and extracted; 4 initially failed cases recovered; full documentation in docs/ |
| 2026-02-09 | Schema | Expanded LLM extraction schema to v2.0 (25 fields) | Added 9 new fields after 80-case validation: victim_relationship, victim_minor, crime_amount_mnt, injury_severity, intoxicated_at_crime, has_lawyer, plea_agreement, time_served_days, sentence_suspended_months |
| 2026-02-10 | Extraction | Full LLM batch extraction (78 batches, 77,968 cases) | xAI Batch API, grok-4-1-fast-non-reasoning, ~$161 total cost, 77,364 succeeded, 4 errors |
| 2026-02-11 | Extraction | LLM results merged into extracted.json | prior_criminal 22%→88%, sentence_type 70%→98%, gender 66%→88%; 6 new fields added |
| 2026-02-11 | Analysis | Complete case primary model (N≈30K), robustness at larger N | Age missing 42.6% → complete case drops to 30K (38% of valid). Pre-registration specifies complete case for core vars including age. 30K still strong (Zhuchkova/Kazun used 20.5K). Three prominent robustness checks: (1) without age N≈37K, (2) binary imprisonment DV N≈48K, (3) MAR analysis comparing missing vs present demographics. Stable coefficients across samples is more convincing than single imputed model. |
| 2026-02-11 | Analysis | Fine-to-months conversion: 450,000 MNT = 1 month | Criminal Code 5.3.5: 15,000 MNT = 1 day. Sensitivity with 300K (conservative) and 600K (liberal) in robustness. |
| 2026-02-11 | Analysis | Sentence types: keep 5 main, exclude acquittals + supplementary | 75,323 cases with main types (fine 42K, imprisonment 12K, community_service 8K, suspended 7.5K, probation 5.8K). Excluded 769 acquittals, 400 supplementary penalties (driving bans, travel restrictions, medical). |
| 2026-02-11 | Analysis | Crime categories: 5 per pre-registration | Ch 10-13→violent (39K), Ch 17-18→property (19K), Ch 27→traffic (9K), Ch 20→drug (1.4K), rest→other (5K). Multi-article cases use first article. |
| 2026-02-12 | Cleaning | Cleaned ages < 14 → NA | 105 cases with ages 1-13 are victim ages or parsing errors. Mongolia criminal responsibility starts at 14. |
| 2026-02-12 | Analysis | Primary model results: only H4 (employment) significant | H1 gender p=0.074, H2 education p=0.053, H3 age² p=0.409, H4 employed β=-3.74 p<0.001. After Holm-Bonferroni, only H4 survives. |
| 2026-02-12 | Analysis | Gender Simpson's paradox in two-stage model | Females 41% less likely to be imprisoned (OR=0.59), but get +4.0 months longer if imprisoned (p=0.003). Gender operates through incarceration decision, not length. |
| 2026-02-12 | Analysis | Log-severity model better fit (R²=0.37 vs 0.24) | Gender becomes significant (-13.4%), education reverses (+2.3%). Suggests gender effect is proportional, not additive. Residual skewness drops 3.57→0.52. |
| 2026-02-12 | Analysis | ICC = 0.8% — courts explain minimal variance | Multilevel model confirms court effects are negligible after case-level controls. Coefficients stable vs OLS FE. |
| 2026-02-12 | Analysis | Aggravating factors dominate (std β=0.42, ΔR²=16.2%) | Sentencing factors explain 4x more variance than demographics (3.7%). Legally relevant factors drive sentencing in Mongolia. |

## Key Files

- `todo.md` - **Project task list** (check here for current focus)
- `docs/analysis_results.md` - **Full analysis results** (all models, tables, figures, synthesis)
- `docs/CODEBOOK.md` - **Data dictionary** (variable definitions, valid values)
- `docs/preregistration.md` - OSF pre-registration content
- `methodology.md` - Research plan and analysis spec
- `idea.md` - Initial brainstorm
- `journal-recommendations.md` - Journal targeting analysis

## Project Structure

```
sentencing-bias/
├── CLAUDE.md              # This file
├── todo.md                # Task tracking
├── idea.md                # Research idea
├── methodology.md         # Detailed methodology
├── requirements.txt       # Python dependencies
├── references.bib         # BibTeX references
│
├── data/
│   ├── case_ids.json      # All enumerated case IDs {"ids": [...], "last_page": N}
│   ├── raw/               # Full dataset as JSON (table_html + text per case)
│   ├── processed/         # Extracted JSON + Parquet
│   ├── scrape_progress.json # Live scraping progress
│   └── pilot/             # Pilot sample (500 HTML files)
│
├── notebooks/
│   ├── 01_scraping.ipynb      # Data collection
│   ├── 02_extraction.ipynb    # Parse HTML → structured data
│   ├── 03_cleaning.ipynb      # Validation & cleaning
│   ├── 04_descriptive.ipynb   # Summary stats & viz
│   ├── 05_analysis.ipynb      # Regression models
│   └── 06_robustness.ipynb    # Sensitivity checks
│
├── scripts/
│   ├── collect_all_cases.py    # Orchestrates enumerate → scrape → extract
│   ├── run_collection.sh       # Shell wrapper for full pipeline in tmux
│   ├── validate_extraction.py  # Pilot validation
│   ├── llm_pilot.py            # LLM extraction pilot (50 cases)
│   ├── llm_batch_extraction.py # Full batch LLM extraction (78 batches)
│   ├── merge_llm_results.py    # Merge LLM results into extracted.json
│   └── run_batch_extraction.sh # Wrapper for nohup batch runs
│
├── src/
│   ├── scraper.py         # shuukh.mn scraping (JSON output, resumable)
│   ├── extractor.py       # Data extraction (supports HTML + JSON input)
│   ├── grok_extractor.py  # Grok API extraction (xAI, structured outputs)
│   └── severity_scale.py  # Sentence severity conversion
│
├── logs/                  # Collection logs
├── drafts/                # Paper drafts (markdown)
├── figures/               # Output figures
└── tables/                # Output tables
```

## Key Related Work

- **Zhuchkova & Kazun (2023)** - Gender bias in Russian homicide sentencing using text mining on 20,531 court decisions. Direct methodological template.
- **Starr (2012)** - Gender disparities in US federal criminal cases. Foundational paper.
- **Mamak et al. (2022)** - Poland sentencing disparity study; notes scarcity of post-communist research.

## Key Concerns to Address

1. **Data extraction accuracy** - Free-text parsing in Mongolian; need pilot with manual verification
2. **Unobserved confounders** - Case severity within crime type, legal representation quality, victim characteristics
3. **Selection bias** - Only completed cases visible; dismissals/acquittals not in data
4. **Small subgroup samples** - Cell sizes may get thin when stratifying by multiple demographics
5. **Judge/court effects** - Include as random effects in multilevel model

## API Keys

- **xAI (Grok):** age-encrypted at `/home/ritz/projects/perspective/.xai-api-key.age`
  - Decrypt: `age -d -i ~/.age/key.txt /home/ritz/projects/perspective/.xai-api-key.age`
  - Used by: `src/grok_extractor.py` for LLM extraction

## Notes

Data fields available from shuukh.mn:
- Structured: Court, Judge, Case index, Date, Criminal code article, Prosecutor
- Extractable: Birth date, Gender, Education, Occupation, Family size, Prior history
- Sentence: Type (fine/imprisonment/probation), Amount/duration, Factors
