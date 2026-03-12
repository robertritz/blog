# Codebook: Sentencing Bias Dataset

**Version:** 2.0
**Last Updated:** 2026-02-09
**Source of Truth:** `src/grok_extractor.py` (CaseExtraction Pydantic model)

This codebook documents all variables in the sentencing bias dataset. Variables are extracted via LLM (Grok) from Mongolian court case text, with structured fields parsed from HTML tables.

> **Field Availability:**
> - **Available** — Fields currently extracted via regex from all 80,827 cases
> - **Planned (v2.0)** — Fields requiring LLM extraction, validated on 80-case pilot but not yet applied to full dataset. Coverage rates for planned fields are estimates from the pilot.

---

## Data Sources

| Source | Variables | Method |
|--------|-----------|--------|
| Structured (HTML table) | case_id, case_index, court, judge, prosecutor, case_date, crime_article | Regex parsing |
| LLM Extraction | All variables below | Grok 4.1 + structured outputs |

---

## Variable Reference

### Defendant Demographics **(Available)**

| Variable | Type | Values | Description | Mongolian Terms |
|----------|------|--------|-------------|-----------------|
| `gender` | string | male, female | Defendant's gender | эрэгтэй, эмэгтэй |
| `age` | integer | 10-100 | Defendant's age at case date | N настай |
| `education` | string | primary, basic, secondary, vocational, higher | Highest education level | бага, суурь, бүрэн дунд, тусгай дунд, дээд |
| `employed` | boolean | true, false | Currently employed | ажилтай, ажилгүй |
| `occupation` | string | free text | Defendant's occupation | мэргэжил |
| `family_size` | integer | 1+ | Household size | ам бүл N |
| `prior_criminal` | boolean | true, false | Has prior criminal conviction | урьд ял шийтгэл |

### Victim Characteristics **(Planned -- v2.0)**

| Variable | Type | Values | Description | Expected Coverage |
|----------|------|--------|-------------|-------------------|
| `victim_relationship` | string | family, spouse, acquaintance, colleague, stranger | Victim's relationship to defendant | ~75% |
| `victim_minor` | boolean | true, false | Victim is under 18 years old | ~25% (null when unknown) |

### Crime Characteristics **(Planned -- v2.0)**

| Variable | Type | Values | Description | Expected Coverage |
|----------|------|--------|-------------|-------------------|
| `crime_amount_mnt` | float | 0+ | Monetary value stolen/damaged (MNT) | ~75% for property crimes |
| `injury_severity` | string | light, moderate, serious | Medical assessment of injury | ~90% for violent crimes |
| `intoxicated_at_crime` | boolean | true, false | Defendant intoxicated during crime | ~60% |

### Case Procedure **(Planned -- v2.0)**

| Variable | Type | Values | Description | Expected Coverage |
|----------|------|--------|-------------|-------------------|
| `has_lawyer` | boolean | true, false | Defendant had legal representation | ~50% (null when unclear) |
| `plea_agreement` | boolean | true, false | Resolved via simplified procedure | ~40% |
| `plea_guilty` | boolean | true, false | Defendant admitted guilt | ~80% |
| `restitution_paid` | boolean | true, false | Defendant compensated victim | ~60% |
| `time_served_days` | integer | 0+ | Days in pre-trial custody | ~30% |

### Sentencing Factors **(Planned -- v2.0)**

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `aggravating_factors` | list[string] | free text | Factors cited against defendant |
| `mitigating_factors` | list[string] | free text | Factors cited in defendant's favor |

**Common Aggravating Factors:**
- intoxicated, used violence, serious injury, child victim, accomplices, repeat offense

**Common Mitigating Factors:**
- admitted guilt, paid restitution, first offense, has dependents, elderly, health condition

### Sentence Outcome **(Available)**

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `sentence_type` | string | fine, imprisonment, suspended, probation, community_service | Primary sentence type |
| `sentence_months` | float | 0+ | Total imprisonment (months) |
| `sentence_suspended_months` | float | 0+ | Portion of sentence suspended *(Planned -- v2.0)* |
| `sentence_fine_mnt` | float | 0+ | Fine amount in MNT |

**Derived Variable:**
- `sentence_actual_months` = `sentence_months` - `sentence_suspended_months`

### Data Quality **(Planned -- v2.0)**

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `extraction_quality` | enum | complete, partial, unreliable | Overall extraction quality |
| `quality_issues` | list[string] | see below | Specific issues encountered |

**Quality Issue Codes:**
- `redacted_bio` - Defendant info redacted with ***
- `multiple_defendants` - Multiple defendants (first extracted)
- `missing_bio_section` - No biography section found
- `missing_sentence` - No ТОГТООХ section
- `minimal_text` - Very short document
- `acquittal` - Case dismissed, no sentence

---

## Structured Fields (from HTML)

These variables come from the case listing table, not LLM extraction:

| Variable | Type | Description |
|----------|------|-------------|
| `case_id` | integer | Unique case identifier (shuukh.mn ID) |
| `case_index` | string | Official case index (e.g., "166/2024/0413/Э") |
| `court` | string | Court name |
| `judge` | string | Judge name |
| `prosecutor` | string | Prosecutor name |
| `case_date` | date | Case decision date |
| `crime_article` | string | Criminal code article (e.g., "11.6.1") |

---

## Education Level Encoding

| Mongolian | English | Ordinal Code |
|-----------|---------|--------------|
| бага | primary | 1 |
| суурь | basic | 2 |
| бүрэн бус дунд | incomplete secondary | 3 |
| бүрэн дунд | secondary | 3 |
| тусгай дунд | vocational | 4 |
| дээд | higher | 5 |

---

## Missing Data

Expected coverage rates based on 80-case pilot validation. Rates for Available fields reflect actual full-dataset extraction; rates for Planned fields are pilot estimates:

| Field | Expected Coverage | Notes |
|-------|-------------------|-------|
| gender | 65% | Redaction varies by court |
| age | 55% | Often redacted |
| education | 60% | Usually in bio section |
| sentence_type | 70% | Missing if no ТОГТООХ |
| prior_criminal | 80% | Explicitly stated |
| victim_relationship | 75% | Inferred from context |
| crime_amount_mnt | 75% | Property crimes only |
| has_lawyer | 50% | Often not mentioned |

---

## Changelog

- **v2.0 (2026-02-09):** Added 9 new fields from schema validation: victim_relationship, victim_minor, crime_amount_mnt, injury_severity, intoxicated_at_crime, has_lawyer, plea_agreement, time_served_days, sentence_suspended_months
- **v1.0 (2026-02-04):** Initial schema with demographics + sentencing
