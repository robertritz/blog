# Datasheet: Mongolian Criminal Sentencing Dataset

Following the framework from Gebru et al. (2021), "Datasheets for Datasets."

---

## Motivation

### For what purpose was the dataset created?

This dataset was created to study demographic disparities in criminal sentencing in Mongolia. Specifically, it enables quantitative analysis of whether defendant characteristics (gender, age, education, employment) are associated with sentencing outcomes after controlling for legally relevant factors.

### Who created the dataset and on behalf of which entity?

The dataset was created by Robert Ritz for academic research purposes. The work is independent and not funded by any external organization.

### Who funded the creation of the dataset?

No external funding. Personal research project.

---

## Composition

### What do the instances represent?

Each instance represents a single criminal court decision from a Court of First Instance in Mongolia. This includes the case metadata, defendant demographics (when available), and sentencing outcome.

### How many instances are there in total?

80,827 cases total. Of these, 77,968 (96.5%) contain valid decision text and are suitable for analysis. The remaining 2,859 cases have data quality issues (2,715 empty decisions, 144 short text) and should be excluded.

### Does the dataset contain all possible instances or is it a sample?

The dataset aims to be a census of all criminal first instance decisions available on shuukh.mn (the Supreme Court of Mongolia's public database) within the query date range (2020-01-01 to 2026-02-04). It is not a sample.

However, this represents only *publicly available* completed cases. It does not include:
- Dismissed cases
- Acquittals (if not published)
- Cases under appeal (if not yet published)
- Juvenile cases (separate system)
- Cases from before 2020 (if not digitized or published)

### What data does each instance consist of?

Each instance contains:

1. **Case identifiers:** case_id, case_index, case_number
2. **Case metadata:** court, judge, prosecutor, case_date, crime_article
3. **Defendant demographics:** gender, age, birth_date, education, occupation, employment status, family size, residence, prior criminal history
4. **Sentencing outcome:** sentence_type (fine/imprisonment/suspended/probation/community_service), duration, fine amount, etc.

Full schema is documented in `README.md`.

### Is there a label or target associated with each instance?

For the sentencing bias study, the target variable is `sentence_severity` (to be derived from sentence_type, sentence_months, sentence_fine_mnt, etc. using a conversion scale).

### Is any information missing from individual instances?

Yes. Extraction coverage varies by field:

All coverage rates use valid cases (N=77,968) as denominator unless noted.

| Field | Count | Coverage |
|-------|-------|----------|
| court, judge | 77,968 | 100.0% |
| crime_article | 76,188 | 97.7% |
| sentence_type | 54,828 | 70.3% |
| gender | 51,355 | 65.9% |
| education | 48,372 | 62.0% |
| age | 41,493 | 53.2% |
| prior_criminal | 17,381 | 22.3% |

Missing data arises from:
- Cases without standard biographical sections
- Multi-defendant cases where extraction targets wrong defendant
- Non-standard document formatting
- Incomplete records in source database

### Are relationships between individual instances made explicit?

No. Each case is treated independently. Related cases (e.g., co-defendants, appeals) are not linked.

### Are there recommended data splits?

No pre-defined splits. For analysis, researchers may consider:
- Temporal splits (e.g., pre/post 2022)
- Geographic splits (Ulaanbaatar vs. aimag courts)
- Crime category splits

### Are there any errors, sources of noise, or redundancies?

1. **Empty decision cases (2,715):** Some cases in the source database have metadata but no decision text. These are flagged with `data_quality_issue = "empty_decision"` and should be excluded from analysis.
2. **Short text cases (144):** Minimal content, flagged with `data_quality_issue = "short_text"`.
3. **Extraction errors:** Regex-based extraction may misparse non-standard text
4. **Multi-defendant cases:** May extract data from wrong defendant
5. **Court name inconsistency:** Same courts have different names after 2025 reorganization
6. **Crime article formatting:** 2,085 unique strings for crime articles due to punctuation variations

### Is the dataset self-contained?

Yes. The extracted.json file contains all structured data needed for analysis. Raw files are included for verification and re-extraction.

---

## Collection Process

### How was the data associated with each instance acquired?

Data was scraped from the public shuukh.mn website. Each case page was fetched via HTTP request, and structured/semi-structured fields were extracted using BeautifulSoup (HTML parsing) and regex patterns (text extraction).

### What mechanisms or procedures were used to collect the data?

1. **Enumeration:** API requests to discover all case IDs
2. **Scraping:** HTTP requests to fetch individual case pages
3. **Extraction:** Automated parsing (no manual coding for main dataset)
4. **Validation:** 200-case pilot sample manually verified

See `../docs/data_collection.md` for detailed methodology.

### If the dataset is a sample, what was the sampling strategy?

N/A - This is a census, not a sample.

### Who was involved in the data collection process?

Data collection was fully automated. Code was written by Robert Ritz. No crowdworkers or manual annotators were used for the main dataset.

### Over what timeframe was the data collected?

- **Data source timeframe:** 2020-01-01 to 2026-02-04 (cases in database)
- **Collection period:** 2026-02-04 to 2026-02-09 (5 days)

### Were any ethical review processes conducted?

No formal IRB review was conducted. This is secondary analysis of public court records, which does not constitute human subjects research under most institutional definitions.

### Did you collect the data from the individuals in question directly?

No. Data was collected from public government records, not from individuals.

---

## Preprocessing/Cleaning/Labeling

### Was any preprocessing/cleaning/labeling of the data done?

1. **HTML stripping:** Raw HTML (~64-165 KB) was reduced to JSON with table_html + text (~10-50 KB)
2. **Field extraction:** Regex patterns extracted structured fields from Mongolian text
3. **Value normalization:** Education levels mapped to ordinal scale; gender mapped to "male"/"female"

No manual labeling was performed on the main dataset.

### Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?

Yes. Both are available:
- `data/raw/{id}.json` — Stripped HTML (table + text)
- `data/processed/extracted.json` — Extracted structured fields

The original full HTML was not retained (to save space), but can be re-fetched from shuukh.mn.

### Is the software used to preprocess/clean/label the data available?

Yes. All code is in the repository:
- `src/scraper.py` — Data collection
- `src/extractor.py` — Field extraction
- `scripts/collect_all_cases.py` — Orchestration

---

## Uses

### Has the dataset been used for any tasks already?

Not yet. This is a new dataset created for the sentencing bias study.

### Is there a repository that links to any or all papers or systems that use the dataset?

Not yet. Will be updated after publication.

### What (other) tasks could the dataset be used for?

- Analysis of crime patterns in Mongolia
- Study of judicial decision-making
- Legal NLP research (Mongolian language)
- Court efficiency studies
- Temporal trends in criminal justice

### Is there anything about the composition of the dataset or the way it was collected that might impact future uses?

1. **Mongolian language:** All text is in Mongolian Cyrillic script
2. **Legal context:** Interpretation requires knowledge of Mongolian criminal law
3. **Temporal scope:** Reflects 2020-2026 period; laws/practices may change
4. **Selection bias:** Only published, completed cases; not representative of all criminal proceedings

### Are there tasks for which the dataset should not be used?

- **Individual prediction:** Should not be used to predict outcomes for individual defendants
- **Causal claims:** Observational data; cannot establish discrimination vs. disparity
- **Re-identification:** Should not attempt to identify individual defendants

---

## Ethical Considerations

### Data Sensitivity

This dataset contains public court records that include demographic information about criminal defendants. While these records are publicly accessible through shuukh.mn, they describe sensitive personal information in the context of criminal proceedings.

### Consent

Informed consent was not sought from individuals in the dataset. These are public government records published by the Supreme Court of Mongolia under Mongolian law. Court decisions are made publicly available as a matter of judicial transparency.

### Potential for Harm

- **Re-identification:** Although names are not included in the extracted dataset, combinations of court, date, crime article, and demographic information could potentially identify individuals. Researchers should report only aggregate statistics.
- **Algorithmic prediction:** This dataset should not be used to build predictive models for individual sentencing outcomes.
- **Political misuse:** Findings about demographic disparities could be misrepresented to undermine public trust in the judiciary. Researchers should carefully distinguish disparity (statistical pattern) from discrimination (intentional bias).

### IRB Status

This research involves secondary analysis of public government records and does not constitute human subjects research under standard institutional definitions. No IRB review was conducted.

### Best Practices for Use

- Report aggregate statistics only; do not highlight individual cases
- Frame findings as disparity, not discrimination, unless causal evidence supports stronger claims
- Acknowledge limitations of observational data
- Credit shuukh.mn and the Supreme Court of Mongolia as the data source

---

## Distribution

### Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?

Dataset will be published as supplementary material with the research paper and/or on OSF.

### How will the dataset be distributed?

- GitHub repository (code + small files)
- OSF or Zenodo (full dataset)

### When will the dataset be released?

After paper acceptance or preprint posting.

### Will the dataset be distributed under a copyright or other intellectual property (IP) license?

The source data is public government records. The derived dataset will be released under CC-BY 4.0 or similar open license.

### Have any third parties imposed IP-based or other restrictions on the data?

No. Data is from public court records.

---

## Maintenance

### Who is supporting/hosting/maintaining the dataset?

Robert Ritz (dataset creator).

### How can the owner/curator/manager of the dataset be contacted?

Via GitHub issues on the project repository.

### Will the dataset be updated?

No regular updates planned. The study population is fixed at the 2026-02-04 cutoff. Future researchers could extend the collection to later dates.

### If the dataset relates to people, are there applicable limits on the retention of the data?

The data is from public court records. No special retention limits apply. However, if Mongolia's data protection laws change, compliance will be reviewed.

### Will older versions of the dataset continue to be supported/hosted/maintained?

Initial release will be archived on Zenodo with DOI for permanent availability.

### If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?

Yes. The collection code is fully documented and reproducible. Others can:
1. Extend the date range
2. Add new extraction fields
3. Improve extraction accuracy
4. Add manual annotations

Contributions can be submitted via pull request.

---

## References

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86-92.

---

*Created: 2026-02-09*
