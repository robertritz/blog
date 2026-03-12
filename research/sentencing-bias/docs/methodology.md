# Methodology: Demographic Bias in Criminal Sentencing in Mongolia

## Research Design

- **Approach:** Quantitative
- **Type:** Observational (retrospective analysis of court records)
- **Temporality:** Cross-sectional with temporal controls (all available cases, with year fixed effects)

## Research Questions & Hypotheses

### Primary Question
Is there systematic disparity in criminal sentencing in Mongolia based on defendant demographics, controlling for legally relevant factors?

### Pre-registered Hypotheses

**H1 (Gender):** Female defendants receive less severe sentences than male defendants for equivalent offenses.

**H2 (Education):** Defendants with higher education receive less severe sentences than those with lower education.

**H3 (Age):** Sentencing severity varies non-linearly with age, with leniency for younger (<25) and older (>60) defendants.

**H4 (Employment):** Employed defendants receive less severe sentences than unemployed defendants.

*Note: These are directional hypotheses based on prior literature (Starr 2012, Mustard 2001). We test for disparity, not discrimination - causal claims require stronger identification.*

## Data Collection

### Source
- **Primary source:** shuukh.mn (Supreme Court of Mongolia public database)
- **Access method:** API endpoint (`/site/case_ajax`) + individual case page scraping (`/single_case/{id}`)
- **Authentication:** None required (public data)
- **Headers required:** `x-requested-with: XMLHttpRequest`

### Population & Sample
- **Population:** All criminal court of first instance decisions in Mongolia
- **Sample:** All cases available on shuukh.mn (N = 80,827)
- **Time period:** 2020-01-01 to 2026-02-04 (query cutoff date)
- **Actual date distribution:** 2020 (13,267), 2021 (12,082), 2022 (13,277), 2023 (13,121), 2024 (14,131), 2025 (14,682), 2026 (263)
- **Courts:** 49 unique courts (6 Ulaanbaatar district courts + 21 aimag courts + consolidated courts)
- **Exclusions:**
  - Cases with missing dependent variable (no sentence recorded) — ~26,000 cases
  - Cases with >50% missing demographic variables
  - Juvenile cases (different legal framework)

### Data Collection Protocol

1. **Discovery phase:** Query API to enumerate all available case IDs for criminal first instance
2. **Scraping phase:** Fetch each case page, extract HTML
3. **Parsing phase:** Extract structured and free-text fields
4. **Validation phase:** Manual verification of 200-case pilot sample

### Variables

#### Dependent Variable

| Variable | Type | Source | Description | Notes |
|----------|------|--------|-------------|-------|
| `sentence_severity` | Numeric (continuous) | Derived | Unified severity score in "imprisonment-month equivalents" | Primary DV |
| `sentence_type` | Categorical | Extracted | Type: imprisonment, suspended, probation, fine, community service, other | For subgroup analysis |
| `sentence_months` | Numeric | Extracted | Raw imprisonment duration in months | For imprisonment-only models |
| `sentence_fine_mnt` | Numeric | Extracted | Fine amount in MNT | For fine-only models |

**Severity Scale Construction:**

| Sentence Type | Conversion to Month-Equivalents | Rationale |
|---------------|--------------------------------|-----------|
| Imprisonment | 1.0 × months | Baseline |
| Suspended sentence | 0.5 × months | Partial incapacitation |
| Probation | 0.3 × months | Supervision only |
| Fine | f(amount) based on legal conversion | Use Criminal Code conversion rates |
| Community service | hours / 160 | ~1 month = 160 hours |

*Sensitivity analysis will test alternative weights (0.3-0.7 for suspended, 0.1-0.5 for probation).*

#### Independent Variables (Demographics)

| Variable | Type | Source | Description | Notes |
|----------|------|--------|-------------|-------|
| `gender` | Binary | Extracted (эмэгтэй/эрэгтэй) | Defendant gender | Primary predictor |
| `age` | Numeric | Derived from birth date | Age at case date | Will also test age² for non-linearity |
| `education` | Ordinal | Extracted | Education level (бага, суурь, бүрэн дунд, тусгай дунд, дээд) | Code as ordinal 1-5 |
| `employed` | Binary | Extracted | Currently employed | May need inference from occupation field |
| `occupation` | Categorical | Extracted | Occupation type | Collapse into meaningful categories |
| `family_size` | Numeric | Extracted | Number of dependents | Control variable |
| `residence_ub` | Binary | Derived | Ulaanbaatar vs. aimag | Urban/rural proxy |

#### Control Variables (Legally Relevant)

| Variable | Type | Source | Description | Notes |
|----------|------|--------|-------------|-------|
| `crime_article` | Categorical | Structured | Criminal code article number | Primary crime type control |
| `crime_category` | Categorical | Derived | Collapsed crime categories (violent, property, drug, etc.) | For interpretability |
| `prior_criminal` | Binary/Numeric | Extracted | Prior criminal history | May be binary (yes/no) or count |
| `aggravating_count` | Numeric | Extracted | Number of aggravating factors mentioned | |
| `mitigating_count` | Numeric | Extracted | Number of mitigating factors mentioned | |
| `case_year` | Categorical | Structured | Year of decision | Year fixed effects |
| `court_id` | Categorical | Structured | Court identifier | For random effects |
| `judge_id` | Categorical | Structured | Judge name/ID | For random effects (if sufficient variation) |

### Data Extraction Approach

**Structured fields (direct parsing):**
- Case ID, date, court, judge, prosecutor, criminal code article
- Parsed from HTML `<table>` element on each case page

**Semi-structured fields (rule-based/regex extraction):**
- Биеийн байцаалт (biographical) section → gender, age, education, occupation, family
- ТОГТООХ (decision) section → sentence type, duration, fine amount
- Prior criminal history (ял шийтгэлгүй / presence of prior record)

**Extraction pipeline:**
1. BeautifulSoup for HTML parsing
2. Section isolation via regex (bio section, sentencing section)
3. Field-specific regex patterns for Mongolian terms (see `data/pilot/pilot_report.md` for full pattern catalog)
4. Validation via independent re-extraction on 200-case sample

*Initial pilot testing showed regex-only extraction achieved >90% accuracy on 5 validated fields. However, coverage was limited (especially prior_criminal at 22%), so LLM extraction was subsequently used to improve coverage and add new fields.*

**LLM extraction (full dataset):**
- **Model:** Grok 4.1 Fast (non-reasoning) via xAI Batch API (`xai-sdk`)
- **Method:** Structured outputs with Pydantic schema (25 fields), 78 batches of 1000 cases
- **Results:** 77,364 succeeded (99.2% of valid cases), 4 errors
- **Cost:** ~$161 (batch API 50% discount)
- **Quality:** 56.2% complete, 43.7% partial, 0.1% unreliable

**Full dataset extraction coverage (post-LLM merge):**

| Field | Regex | Post-LLM | Coverage |
|-------|-------|----------|----------|
| court, judge | 80,827 | 80,827 | 100% |
| crime_article | 78,920 | 78,920 | 97.6% |
| sentence_type | 54,422 | 76,513 | 98.2% |
| prior_criminal | 17,289 | 68,402 | 87.7% |
| gender | 51,024 | 68,473 | 87.8% |
| employed | — | 56,606 | 72.6% |
| education | 48,063 | 52,448 | 67.3% |
| family_size | — | 50,509 | 64.8% |
| occupation | — | 46,778 | 60.0% |
| age | 41,310 | 44,654 | 57.3% |
| sentence_fine_mnt | — | 42,871 | 55.0% |
| sentence_months | — | 15,010 | 19.3% |

LLM extraction substantially improved coverage on key variables (prior_criminal 22%→88%, sentence_type 68%→98%) and added 6 new fields not extractable by regex (employed, occupation, family_size, sentence_months, plus v2.0 fields like victim_relationship, injury_severity, etc.).

### Data Cleaning Protocol

1. **Missing data:**
   - Detection: Count nulls per variable; flag cases with >50% missing
   - Handling:
     - Primary analysis: Complete case analysis for core variables (gender, age, crime type, sentence)
     - Sensitivity: Multiple imputation for education/occupation if missing <20%
   - Report: Missing data table by variable and by year

2. **Outliers:**
   - Detection: Sentences >99th percentile; age <16 or >90
   - Handling: Winsorize at 99th percentile; flag but retain extreme ages
   - Report: Distribution plots pre/post winsorization

3. **Validation checks:**
   - [ ] Age range (16-100)
   - [ ] Sentence duration non-negative
   - [ ] Gender is binary (flag non-binary if encountered)
   - [ ] Crime article exists in Criminal Code
   - [ ] Date is valid and within expected range
   - [ ] Cross-check: sentence type matches sentence details

4. **Pilot validation:**
   - Manually code 200 randomly selected cases
   - Compare automated extraction to manual coding
   - Report accuracy rates per variable
   - Threshold: >90% accuracy for inclusion in analysis

## Analysis Plan

### Software & Packages

```python
# Data collection
requests, beautifulsoup4, asyncio/aiohttp

# Data processing
pandas, numpy

# NLP/extraction
re (regex), anthropic (Claude API for complex extraction)

# Analysis
statsmodels  # OLS, robust SE
scipy.stats  # Statistical tests
linearmodels  # Panel/multilevel models (alternative)

# Visualization
matplotlib, seaborn

# Reporting
jupyter, pandas-profiling
```

### Descriptive Analysis

1. **Sample characteristics:**
   - N cases by year, court, crime category
   - Demographic distributions (age, gender, education, employment)
   - Sentence distributions by type and severity

2. **Bivariate relationships:**
   - Mean severity by gender (t-test)
   - Mean severity by education level (ANOVA)
   - Severity vs. age (scatter + LOESS)
   - Cross-tabulations: demographics × crime type

3. **Missing data analysis:**
   - Missing rates by variable
   - Comparison of cases with/without missing data

### Inferential Analysis

#### Primary Model: OLS with Robust Standard Errors

```
sentence_severity ~ gender + age + age² + education + employed +
                    crime_category + prior_criminal +
                    aggravating_count + mitigating_count +
                    year_FE + court_FE + ε
```

- Robust (HC3) standard errors to address heteroskedasticity
- Year and court fixed effects
- Report coefficients, 95% CIs, p-values

#### Alternative Model: Multilevel (Random Effects)

```
Level 1 (case): severity ~ demographics + case_controls
Level 2 (court): random intercept for court
Level 2 (judge): random intercept for judge (if sufficient n per judge)
```

- Accounts for clustering within courts/judges
- Compare to fixed effects model via Hausman test

#### Two-Stage Selection Model (Robustness)

Stage 1: Logit model for P(imprisonment vs. non-incarceration)
Stage 2: OLS for sentence length | imprisoned

- Addresses selection into imprisonment
- Heckman correction if appropriate

### Robustness Checks

1. **Alternative DV specifications:**
   - Imprisonment months only (conditional on imprisonment)
   - Binary: imprisonment vs. non-custody
   - Alternative severity weights (vary suspended/probation discounts)

2. **Alternative model specifications:**
   - No court fixed effects (if small courts dominate)
   - Crime-article fixed effects instead of category
   - Interaction: gender × crime category

3. **Sensitivity to outliers:**
   - Exclude top/bottom 1% of sentences
   - Exclude cases with imputed data

4. **Temporal stability:**
   - Pre/post 2017 Criminal Code comparison (if data spans)
   - Rolling 3-year windows

### Subgroup Analyses

1. **By crime category:** Separate models for violent, property, drug offenses
2. **By court location:** Ulaanbaatar vs. aimag courts
3. **By gender:** Interaction effects (e.g., does education effect differ by gender?)

### Effect Size Interpretation

- Report unstandardized coefficients (month-equivalents)
- Report standardized coefficients (for comparability across predictors)
- Compare to Starr (2012) finding of ~60% gender gap
- Discuss practical significance, not just statistical significance

## Validation Strategy

### Internal Validity

| Threat | Mitigation |
|--------|------------|
| Omitted variable bias | Include legally-relevant controls; acknowledge unobserved case severity |
| Selection bias (only completed cases) | Note limitation; cannot generalize to dismissed/acquitted |
| Measurement error in extraction | Pilot validation; report accuracy; sensitivity analysis |
| Reverse causality | Not applicable (demographics precede sentencing) |

### External Validity

- **To Mongolia:** High (population of court decisions)
- **To other countries:** Limited (different legal systems, cultures)
- **Temporal:** May not generalize to future if laws/norms change

### Replication

- All code published on GitHub/OSF
- Raw data retained (public records, no privacy concern)
- Extraction prompts documented
- Random seed set for reproducibility

## Pre-Registration

**Platform:** Open Science Framework (OSF)

**Timing:** Before data collection begins

**Contents to register:**
1. Research questions and hypotheses (H1-H4)
2. Sample definition and exclusion criteria
3. Variable operationalization (especially severity scale)
4. Primary model specification
5. Robustness checks planned

**Exploratory analyses:** Clearly labeled as exploratory in paper
- Judge gender effects (if identifiable)
- Prosecutor effects
- Temporal trends

## Limitations (Anticipated)

1. **Unobserved case characteristics:** Cannot control for demeanor, quality of evidence, victim preferences. This is a limitation shared with all observational sentencing studies.

2. **Selection into sample:** Only completed cases; dismissals/acquittals not observed. Findings apply to convicted defendants only.

3. **Extraction accuracy:** NLP on Mongolian text may introduce noise. Mitigated by pilot validation and reporting accuracy rates.

4. **Severity scale assumptions:** Conversion factors for non-imprisonment sentences are somewhat arbitrary. Addressed via sensitivity analysis.

5. **Disparity ≠ discrimination:** Finding demographic disparity does not prove intentional bias. Unobserved legally-relevant factors may explain differences.

6. **Generalizability:** Results specific to Mongolia's legal and cultural context.

## Ethical Considerations

- **Data sensitivity:** Low - all data is public court records
- **IRB required:** No - secondary analysis of public records, no human subjects
- **Consent:** Not applicable
- **Privacy:** Aggregated analysis only; no individual cases highlighted in paper
- **Potential harm:** Findings could be misused politically; will emphasize limitations and avoid causal language

## Timeline

| Phase | Tasks | Output |
|-------|-------|--------|
| **1. Setup** | Set up project repo, OSF pre-registration | Pre-registration, empty notebooks |
| **2. Pilot** | Scrape 500 cases, manual validation of 200 | Accuracy report, extraction refinement |
| **3. Full collection** | Scrape all available cases | Raw data files |
| **4. Cleaning** | Parse, extract, validate, clean | Processed dataset (Parquet) |
| **5. Descriptive** | Summary stats, visualizations | Descriptive tables, figures |
| **6. Analysis** | Run models, robustness checks | Regression tables |
| **7. Writing** | Draft all sections | Full draft v1 |
| **8. Review** | Internal review, revision | Draft v2 |
| **9. Submission** | Format for target journal | Submission package |

## File Structure

```
sentencing-bias/
├── README.md                  # Public entry point
├── LICENSE                    # MIT (code) + CC-BY-4.0 (data)
├── CITATION.cff               # Machine-readable citation
├── requirements.txt
├── references.bib
├── data/
│   ├── README.md              # Dataset documentation
│   ├── CODEBOOK.md            # Variable definitions
│   ├── DATASHEET.md           # Gebru et al. datasheet
│   ├── case_ids.json
│   ├── sample/                # 100-case stratified sample
│   │   ├── sample_100.json
│   │   ├── generate_sample.py
│   │   └── README.md
│   ├── raw/                   # 80,827 JSON files (2.9 GB, gitignored)
│   ├── processed/             # extracted.json (207 MB, gitignored)
│   └── pilot/                 # 500 HTML files (47 MB)
├── docs/
│   ├── methodology.md         # This file
│   ├── preregistration.md     # OSF pre-registration content
│   └── data_collection.md     # Technical collection report
├── scripts/
│   ├── collect_all_cases.py
│   ├── run_collection.sh
│   └── validate_extraction.py
├── notebooks/
│   ├── 01_scraping.ipynb
│   ├── 02_extraction.ipynb
│   ├── 03_cleaning.ipynb
│   ├── 04_descriptive.ipynb
│   ├── 05_analysis.ipynb
│   └── 06_robustness.ipynb
├── src/
│   ├── scraper.py
│   ├── extractor.py
│   ├── grok_extractor.py
│   └── severity_scale.py
├── paper/                     # Paper drafts
├── figures/                   # Output figures
└── tables/                    # Output tables
```

---

*Created: 2026-02-03*
*Updated: 2026-02-04 (pilot results incorporated)*
*Updated: 2026-02-09 (full data collection complete)*
*Updated: 2026-02-10 (documentation restructured for public release)*
*Updated: 2026-02-11 (LLM extraction complete, coverage tables updated)*
*Status: Data collection & extraction complete (N=80,827, 77,364 LLM-extracted), ready for cleaning and analysis*
