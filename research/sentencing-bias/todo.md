# Sentencing Bias Project - Todo List

## Phase 1: Setup & Pre-registration
- [x] Create OSF account at osf.io
- [x] Create OSF project "Sentencing Bias Mongolia"
- [x] Submit pre-registration (embargo until June 2026)
- [x] Document hypotheses H1-H4 formally
- [x] Set up Python environment (`pip install -r requirements.txt`)

## Phase 2: Pilot Data Collection
- [x] Build scraper for shuukh.mn API
- [x] Scrape 500 pilot cases
- [x] Build extraction pipeline (structured fields)
- [x] Build extraction pipeline (free-text fields via regex)
- [x] Manual validation of 200 cases
- [x] Calculate extraction accuracy rates
- [x] Refine extraction if accuracy <90%

## Phase 3: Full Data Collection
- [x] Enumerate all available case IDs (80,827 cases)
- [x] Scrape all cases (with rate limiting)
- [x] Run extraction pipeline on full dataset
- [x] Data quality audit (2,859 cases flagged as unusable)
- [x] Document collection process
- [x] Export to Parquet (after cleaning)

## Phase 4: Analysis
- [x] Data cleaning and export to parquet (75,323 cases, 48 cols)
- [x] Descriptive statistics and visualizations (Tables 1-3, Figures 1-4)
- [x] Primary regression model (OLS with HC3 robust SE, Sample A N=29,847)
- [x] Multilevel model (court random intercepts, ICC=0.8%)
- [x] Two-stage selection model (logit imprisonment + OLS months)
- [x] Log-severity robustness (R²=0.37, addresses skewness)
- [x] Sample B robustness (N=36,829 without age)
- [x] Coefficient plot (Figure 5) and stability table
- [x] Analysis results documented (docs/analysis_results.md)
- [ ] Additional robustness: temporal stability, subgroup by crime type
- [ ] Additional robustness: alternative fine conversion rates

## Phase 5: Writing
- [ ] Draft introduction
- [ ] Draft literature review
- [ ] Draft methodology section
- [ ] Draft results section
- [ ] Draft discussion and limitations
- [ ] Create tables and figures
- [ ] Internal review and revision

## Phase 6: Submission
- [ ] Format for Asian Journal of Criminology
- [ ] Write cover letter
- [ ] Submit

## Phase 7: Public Repository & Documentation
Prepare the repo for public release — findable, clear, and useful to the research community.

### 7.1 Restructure files (separate internal from public)
- [ ] Move internal docs out of public view:
  - [ ] Add `CLAUDE.md` to `.gitignore` (internal dashboard with API paths)
  - [ ] Add `todo.md` to `.gitignore` (internal tracking)
  - [ ] Add `idea.md` to `.gitignore` (superseded by methodology.md)
  - [ ] Add `journal-recommendations.md` to `.gitignore` (private submission strategy)
- [ ] Move `methodology.md` → `docs/methodology.md`
- [ ] Move `preregistration-draft.md` → `docs/preregistration.md`
- [ ] Move `docs/CODEBOOK.md` → `data/CODEBOOK.md` (lives with data it describes)
- [ ] Rename `docs/data_collection_report.md` → `docs/data_collection.md`
- [ ] Rename `drafts/` → `paper/`

### 7.2 Create missing standard files
- [ ] Create `README.md` — the public entry point:
  - Title, one-paragraph abstract
  - Status badge (Data Collection Complete | Analysis In Progress)
  - Key numbers (80,827 cases, 2020–2026, 49 courts)
  - Quick start (load sample data in 3 lines of Python)
  - Project structure table
  - Data access (OSF/Zenodo link)
  - Reproduction steps (from scratch)
  - Citation (bibtex)
  - License
  - Links to methodology, codebook, datasheet, pre-registration
- [ ] Create `LICENSE` — dual license:
  - MIT for code
  - CC-BY-4.0 for data
- [ ] Create `CITATION.cff` — machine-readable citation (GitHub "Cite this repo" button)
- [ ] Create `data/sample/` — 100 stratified cases for immediate reproduction
  - Script to generate the sample (stratified by crime type, gender, court)
  - Include `data/sample/README.md` explaining sampling method

### 7.3 Fix content issues
- [ ] Reconcile coverage numbers across docs — standardize on valid N=77,968
  - `data/README.md` (currently valid N)
  - `data/DATASHEET.md` (currently total N)
  - `docs/data_collection.md` (reports both)
  - Pick one frame, use consistently, note denominator explicitly
- [ ] Flag v2.0 codebook fields as "planned" vs "available now"
  - Currently lists victim_relationship, injury_severity, etc. as if they exist
  - Add availability column or separate into "Current fields" / "Planned fields (v2.0)"
- [ ] Add "Ethical Considerations" section to `data/DATASHEET.md`
  - Public government records, no re-identification attempts
  - Aggregate analysis only, no individual prediction
  - No personally identifiable information beyond what's publicly published
- [ ] Add header cells to each notebook: purpose, inputs, outputs, runtime estimate
- [ ] Rename `data_collection_report.md` → `data_collection.md`

### 7.4 Git hygiene
- [ ] Commit Phase 3 work (currently uncommitted since Feb 5-9)
- [ ] Commit documentation restructure
- [ ] Push to GitHub (public or private, decide)
- [ ] Tag releases: `v0.1-pilot` (Phase 2), `v0.2-collection` (Phase 3)

### 7.5 External hosting (when data is ready for release)
- [ ] Zenodo deposit for full dataset (gets DOI, versioned, citable)
- [ ] OSF project page linking pre-registration + data + code
- [ ] GitHub release tagged to paper submission (v1.0)

---

## Current Focus

**Phase 4 analysis complete** (2026-02-12). Key result: only H4 (employment) supported. See `docs/analysis_results.md`.

**Next action:** Phase 5 — Paper writing (or additional robustness checks if desired)

---

## Phase 3.6: Batch LLM Extraction (IN PROGRESS)

Extracting all 77,968 valid cases using xAI Batch API for consistent methodology.

### Scripts Created

- `scripts/llm_batch_extraction.py` — Batch orchestration (create, monitor, retrieve)
- `scripts/merge_llm_results.py` — Merge LLM results into extracted.json

### Usage

```bash
# Set API key
export XAI_API_KEY="$(age -d -i ~/.age/key.txt ~/projects/perspective/.xai-api-key.age)"

# Create test batch (10 cases)
python scripts/llm_batch_extraction.py --test --no-wait

# Check status
python scripts/llm_batch_extraction.py --status

# Wait for completion and retrieve results
python scripts/llm_batch_extraction.py --resume

# Full extraction (all 78K cases)
python scripts/llm_batch_extraction.py

# Merge results
python scripts/merge_llm_results.py
```

### Progress

- [x] Create batch extraction script
- [x] Create merge results script
- [x] Test batch API with 10 cases
- [x] Verify structured outputs work correctly
- [x] Schema validation (80 cases across 4 Explore agents)
- [x] Expand schema to v2.0 (25 fields total, +9 new fields)
- [x] Create docs/CODEBOOK.md documentation
- [x] Run full extraction with v2.0 schema (78 batches of 1000)
- [x] Merge results (77,364 succeeded, 4 errors)
- [x] Verify improved coverage (prior_criminal 22%→88%, sentence_type 70%→98%)

### Schema v2.0 New Fields (validated 2026-02-09)

| Field | Coverage | Purpose |
|-------|----------|---------|
| victim_relationship | 75% | Control for victim-defendant relationship |
| victim_minor | 25% | Child victim flag |
| crime_amount_mnt | 75% | Property crime severity |
| injury_severity | 90% | Violent crime severity (light/moderate/serious) |
| intoxicated_at_crime | 60% | Aggravating factor |
| has_lawyer | 50% | Procedural control |
| plea_agreement | 40% | Simplified procedure flag |
| time_served_days | 30% | Pre-trial custody |
| sentence_suspended_months | 50% | Actual vs nominal sentence |

### Cost

- Actual: ~$161 total (78 batches × ~$2.07/batch)
- Cases averaged ~33KB / ~8K tokens (larger than estimated)
- Batch API 50% discount applied

---

## Phase 3.5: LLM Extraction Pilot ✅ COMPLETE

- [x] Create `src/grok_extractor.py` — Grok API integration with structured outputs
- [x] Create `scripts/llm_pilot.py` — 50-case pilot orchestration
- [x] Set `XAI_API_KEY` environment variable (age-encrypted at perspective/.xai-api-key.age)
- [x] Run pilot and validate results
- [x] Fix truncation bug (was cutting off ТОГТООХ section)
- [x] Add quality assessment flags (complete/partial/unreliable)
- [x] Validate with 10 parallel agents
- [x] Decision: **PROCEED to full LLM extraction**

### Final Results (2026-02-09)

| Metric | Value |
|--------|-------|
| Sample size | 50 cases |
| API success | 100% |
| Accuracy | ~95% on verifiable fields |
| Gap-fill rate | **65.8%** |

| Field | Regex | LLM | Gap Filled | Agreement |
|-------|-------|-----|------------|-----------|
| prior_criminal | 3 | 39 | **+36** | 100% |
| sentence_fine_mnt | 12 | 30 | **+19** | 100% |
| sentence_type | 38 | 49 | +11 | 89% |
| gender | 30 | 34 | +5 | 100% |

### Data Quality Assessment

| Quality | Count | Action |
|---------|-------|--------|
| Complete | 25 (50%) | Use in study |
| Partial | 25 (50%) | Use with caution |
| Unreliable | 0 (0%) | Exclude |

### Key Findings

1. **Root cause fixed:** Original code truncated at 8K chars, cutting off sentencing section in 92% of cases
2. **Quality flags added:** Cases now tagged with issues (redacted_bio, multiple_defendants, etc.)
3. **Multi-defendant handling:** LLM correctly focuses on first defendant
4. **Regex disagreements investigated:** LLM was correct in all 4 cases

See `data/pilot/validation_report.md` for full details.

---

## Phase 2 Results

**Pilot sample:** 500 cases scraped from shuukh.mn (criminal court of first instance)

**Extraction method:** Regex-only (`use_llm=False`) — no API key needed

**Validation:** 200-case random sample (seed=42), independent regex validator vs automated pipeline

| Field | Match | Mismatch | Auto-only | Manual-only | Both-null | Accuracy |
|-------|-------|----------|-----------|-------------|-----------|----------|
| gender | 149 | 3 | 3 | 3 | 42 | **94.3%** |
| age | 131 | 0 | 1 | 3 | 65 | **97.0%** |
| education | 140 | 2 | 0 | 2 | 56 | **97.2%** |
| sentence_type | 163 | 3 | 0 | 11 | 23 | **92.1%** |
| sentence_fine_mnt | 59 | 0 | 2 | 1 | 138 | **95.2%** |

All fields >90% threshold. Gate passed.

**Field coverage (500 cases):**
- Gender: 330/500 (66%)
- Sentence type: 354/500 (70.8%)
- Sentence fine (MNT): cases with fine amounts extracted where applicable

**Gender distribution:** 276 male, 54 female, 170 null

**Sentence type distribution:** 282 fine, 35 imprisonment, 33 community_service, 4 suspended, 146 null

---

---

## Phase 3 Results

**Full dataset:** 80,827 cases scraped from shuukh.mn (2020-01-01 to 2026-02-04)

**Data quality audit:**
- Valid content: 77,968 (96.5%)
- Empty decision (source issue): 2,715 (3.4%) — flagged, exclude from analysis
- Short text: 144 (0.2%) — flagged, exclude from analysis

**Extraction coverage (valid cases only, N=77,968, post-LLM merge):**

| Field | Regex | Post-LLM | Coverage |
|-------|-------|----------|----------|
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

**Distributions:**
- Years: 2020 (13,267), 2021 (12,082), 2022 (13,277), 2023 (13,121), 2024 (14,131), 2025 (14,682), 2026 (263)
- Courts: 49 unique
- Gender: 43,896 male, 7,458 female, 29,473 null
- Sentence types: fine (42,339), imprisonment (6,209), community_service (5,165), suspended (1,049), probation (64)

---

## Notes

- Pilot before committing to full scrape
- Pre-register before looking at any data
- Keep extraction prompts versioned
- Gender extraction required bio-section isolation to handle multi-defendant cases
- Education extraction needs proximity check for short patterns near "боловсрол"
- Age extraction needs 10-100 range filter to exclude victim ages and artifacts
- 2,859 cases have no decision text at source — data quality issue, not scraping error
