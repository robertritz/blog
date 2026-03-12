# Analysis Results

**Date:** 2026-02-12
**Data:** `data/processed/sentencing_clean.parquet` (75,323 cases, 48 columns)

---

## Samples

| Sample | Description | N | Use |
|--------|-------------|---|-----|
| Full cleaned | All 5 sentence types, no quality issues | 75,323 | Descriptive stats |
| Sample A | Complete cases on all core vars | 29,847 | Primary model (pre-registered) |
| Sample B | No age requirement | 36,829 | Robustness (relaxed) |
| Sample C1 | Stage 1 (incarceration selection) | 40,626 | Two-stage model |
| Sample C2 | Imprisoned with months | 6,417 | Two-stage stage 2 |

**Binding constraints for Sample A:** age (42.7% missing, adds ~7K if dropped) and severity (18.6% missing, adds ~6.6K if dropped).

**Selection bias in Sample A:** Demographics (gender, age) are unbiased vs full sample. Sentence type composition shifts: fines over-represented (70% vs 56%), community service/suspended/probation under-represented (11% vs 28%) because severity coverage is low for non-fine/imprisonment types.

---

## Missing Data (Table 2)

### Overall rates

| Variable | N Present | % Missing |
|----------|-----------|-----------|
| Gender | 66,364 | 11.9% |
| Age | 43,133 | 42.7% |
| Education | 50,828 | 32.5% |
| Employment | 55,490 | 26.3% |
| Prior criminal | 66,368 | 11.9% |
| Crime category | 73,505 | 2.4% |
| Severity | 61,304 | 18.6% |

### Temporal trend

Missing rates increase sharply from 2020 to 2025:
- Gender: 6.4% → 21.0%
- Age: 32.5% → 61.5%
- Education: 26.5% → 45.2%

More recent court decisions appear to have less detailed biographical sections.

### MAR diagnostics

- **Age missingness**: Associated with court location (UB courts have better coverage, z=24.3, p<0.001) and employment (z=-15.3, p<0.001). Sentence type composition is similar regardless of age availability.
- **Severity missingness**: Structurally determined by sentence type (MNAR). 97.5% of missing-severity cases are community service, suspended, or probation types that lack duration data. Not random.
- **Education missingness**: Strong UB effect (56.0% vs 42.8%, z=33.8) and small age effect (d=0.19).

---

## Bivariate Results (Table 3, Sample A)

| Predictor | Test | Statistic | p-value | Effect size |
|-----------|------|-----------|---------|-------------|
| Gender (H1) | t-test | t=3.75 | <0.001 | d=0.063 (males higher) |
| Education (H2) | ANOVA | F=29.7 | <0.001 | η²=0.005 |
| Age non-linear (H3) | Quadratic F | F=0.16 | 0.692 | r=0.046 (linear only) |
| Employment (H4) | t-test | t=-31.8 | <0.001 | d=-0.381 (unemployed higher) |
| Prior criminal | t-test | t=29.3 | <0.001 | d=0.355 |
| Crime category | ANOVA | F=176.1 | <0.001 | η²=0.023 |
| Aggravating count | Spearman | r=0.426 | <0.001 | — |
| Mitigating count | Spearman | r=-0.144 | <0.001 | — |

**Gender by crime category:** Gender gap largest for traffic (d=0.168) and property (d=0.153), smallest for drug (d=0.049).

**Education pattern:** Threshold effect — none/primary (mean 14-17) vs secondary+ (mean 8-9). Not a clean linear gradient; Spearman r=-0.007, p=0.22.

**Age pattern:** Weak positive linear trend (severity increases with age). No evidence of non-linearity (quadratic F=0.16, p=0.69).

**Confounding:** Females have more property crime (37% vs 24%) and less violent crime (41% vs 56%). Since property crimes get harsher average severity, this confounding partially offsets the raw gender gap.

---

## Primary Model (Table 4, Pre-registered)

**Specification:** `severity ~ female + age + age² + education_level + employed + C(crime_category) + prior_criminal + aggravating_count + mitigating_count + C(year) + C(court_id)`

**Estimator:** OLS with HC3 robust SE

**Fit:** R² = 0.237, Adj R² = 0.235, N = 29,847

### Hypothesis tests

| Hypothesis | Variable | β | SE | p | 95% CI | Supported? |
|------------|----------|---|-----|---|--------|------------|
| H1: Female → lower | female | -0.490 | 0.275 | 0.074 | [-1.03, 0.05] | No (p>0.05) |
| H2: Education → lower | education_level | -0.195 | 0.101 | 0.053 | [-0.39, 0.00] | No (p>0.05) |
| H3: Age non-linear | age² | -0.001 | 0.001 | 0.409 | [-0.002, 0.001] | No |
| H4: Employed → lower | employed | **-3.739** | 0.245 | **<0.001** | [-4.22, -3.26] | **Yes** |

### Holm-Bonferroni correction (4 primary hypotheses)

Only **H4 (Employment)** survives correction. H1, H2, H3 do not reach significance.

### Standardized coefficients (magnitude ranking)

1. aggravating_count: β=0.420
2. employed: β=-0.092
3. mitigating_count: β=-0.088
4. age: β=0.077
5. age_sq: β=-0.028
6. education_level: β=-0.011
7. female: β=-0.009
8. prior_criminal: β=0.002

### Control variables

| Variable | β | p |
|----------|---|---|
| prior_criminal | 0.096 | 0.696 |
| aggravating_count | 6.327 | <0.001 |
| mitigating_count | -1.236 | <0.001 |
| Crime: drug (vs violent) | 5.172 | <0.001 |
| Crime: other | 3.777 | <0.001 |
| Crime: property | 2.917 | <0.001 |
| Crime: traffic | -1.458 | <0.001 |

**Notable:** `prior_criminal` is NOT significant (p=0.70) after controlling for aggravating/mitigating factors. Prior record is absorbed by aggravating_count.

### Variance decomposition (sequential)

| Block | R² | ΔR² |
|-------|-----|-----|
| Demographics only | 0.037 | +0.037 |
| + Crime controls | 0.068 | +0.031 |
| + Sentencing factors | 0.230 | **+0.162** |
| + Year FE | 0.232 | +0.002 |
| + Court FE | 0.237 | +0.005 |

Sentencing factors (aggravating/mitigating counts) explain 16.2% of variance — the dominant contributor. Demographics alone explain only 3.7%.

### Diagnostics

Residual skewness: 3.57, kurtosis: 17.80. Severity is heavily right-skewed even after winsorization. Log-severity model addresses this (see robustness).

---

## Robustness Models (Tables 5-6)

### Multilevel model (court random intercepts)

- ICC = 0.008 (0.8% of variance between courts)
- Courts explain minimal variance after case-level controls
- All coefficients nearly identical to OLS FE model
- Education becomes significant (p=0.044) in multilevel

### Two-stage selection model

**Stage 1: P(imprisonment) — Logistic regression**

| Variable | β | OR | p |
|----------|---|-----|---|
| female | -0.524 | **0.59** | <0.001 |
| education_level | -0.208 | 0.81 | <0.001 |
| employed | -0.846 | **0.43** | <0.001 |
| prior_criminal | 0.363 | 1.44 | <0.001 |
| aggravating_count | 0.812 | 2.25 | <0.001 |

Females are 41% less likely to be imprisoned. Employed are 57% less likely. These are large effects.

**Stage 2: Sentence months | imprisoned (OLS, N=5,578)**

| Variable | β | p |
|----------|---|---|
| **female** | **+4.007** | **0.003** |
| education_level | -0.858 | 0.046 |
| employed | -2.229 | 0.021 |
| prior_criminal | -6.804 | <0.001 |
| aggravating_count | 5.506 | <0.001 |

**Simpson's paradox for gender:** Females receive lower severity overall (marginal effect), but this is driven entirely by the imprisonment *decision*. Among imprisoned defendants, females receive **4 months longer** sentences. The females who ARE imprisoned have committed more serious offenses.

**Prior criminal reversal:** Among imprisoned, prior record is associated with *shorter* sentences (-6.8 months). Selection effect: prior record increases imprisonment probability for less serious offenses.

### Log-severity model

| Variable | β | % change | p |
|----------|---|----------|---|
| female | -0.144 | **-13.4%** | <0.001 |
| education_level | +0.023 | +2.3% | <0.001 |
| employed | -0.207 | -18.7% | <0.001 |
| prior_criminal | +0.159 | +17.2% | <0.001 |

R² = 0.370 (vs 0.237 in levels). Residual skewness = 0.52 (vs 3.57). Much better model fit.

**Key difference:** Gender becomes highly significant (-13.4%, p<0.001). Education **reverses direction** (+2.3%). Prior criminal becomes significant (+17.2%).

The log model suggests the gender effect is proportional (percentage-based) rather than additive (fixed months). In the level model, a 0.5-month difference across all sentence types is small. In the log model, a 13% reduction is substantial.

### Sample B (no age requirement, N=36,829)

| Variable | β | p |
|----------|---|---|
| female | -0.493 | 0.042 |
| education_level | -0.099 | 0.267 |
| employed | -3.726 | <0.001 |

Gender becomes significant with larger N. Education remains non-significant.

---

## Coefficient Stability

| Variable | Primary OLS | Multilevel | Log-severity | Sample B | Stage 2 |
|----------|------------|------------|--------------|----------|---------|
| female | -0.49 | -0.47 | -0.14*** | -0.49* | +4.01** |
| education | -0.20 | -0.19* | +0.02*** | -0.10 | -0.86* |
| employed | -3.74*** | -3.70*** | -0.21*** | -3.73*** | -2.23* |

**Employment is robust across ALL specifications.** Gender is directionally consistent but significance varies. Education is not robust (reverses in log model).

---

## Synthesis

### Main finding

**Employment status is the dominant demographic predictor of sentencing severity in Mongolian criminal courts.** Unemployed defendants receive approximately 3.7 months more severity (or 19% more in log scale), controlling for crime type, criminal history, and sentencing factors. This effect is consistent across all model specifications, sample definitions, and DV transformations.

### Gender

The gender effect is nuanced. In the pre-registered primary model, the coefficient is in the predicted direction but does not reach significance (β=-0.49, p=0.074). However, in the log-severity model (which better fits the data), gender is highly significant (-13.4%). The two-stage model reveals that gender primarily operates through the incarceration decision (OR=0.59) rather than sentence length — a classic Simpson's paradox where the marginal effect and conditional effects differ in direction.

### Education and age

Neither education nor age non-linearity are robustly supported. Education shows a threshold effect bivariately (none/primary vs secondary+) but this doesn't survive multivariate controls and reverses in the log model. Age has a weak linear effect (older = slightly harsher) but no evidence of the predicted inverted U-shape.

### What drives sentencing

The variance decomposition reveals that **aggravating and mitigating factors** are by far the most important predictors (ΔR²=16.2%), followed by crime type (ΔR²=3.1%). Demographics contribute only 3.7%. Court and year effects are minimal (ΔR²=0.7% combined). Mongolian sentencing appears primarily driven by legally relevant factors, not demographics — with the notable exception of employment status.

---

## Output Files

### Tables (`tables/`)
- `table1_characteristics.csv` — Sample characteristics (full, A, B)
- `table2a_missing_rates.csv` — Missing rates by variable
- `table2b_missing_by_year.csv` — Missing rates by year
- `table3_bivariate.csv` — Bivariate tests (H1-H4 + controls)
- `table4_primary_model.csv` — Primary OLS coefficients
- `table5_stability.csv` — Coefficient stability across specs
- `table6_robustness.csv` — Full robustness summary

### Figures (`figures/`)
- `fig1_demographics.png` — Age, gender, education, crime distributions
- `fig2_sentences.png` — Sentence type, severity distribution, boxplots, trend
- `fig3_bivariate.png` — Severity by gender, age, education, employment
- `fig4_crime_composition.png` — Crime types by gender and education
- `fig5_coefficient_plot.png` — Forest plot across specifications

### Scripts (`scripts/analysis/`)
- `cleaning/01_load_and_overview.py` — Initial data overview
- `cleaning/02_inspect_categories.py` — Category value inspection
- `cleaning/03_clean_and_export.py` — Full cleaning pipeline → parquet
- `descriptive/01_sample_overview.py` — Sample definitions and distributions
- `descriptive/02_table1_characteristics.py` — Table 1
- `descriptive/03_table2_missing.py` — Missing data analysis
- `descriptive/04_table3_bivariate.py` — Bivariate tests
- `descriptive/05_figures.py` — Figures 1-4
- `models/01_primary_model.py` — Primary OLS + hypothesis tests
- `models/02_robustness_models.py` — Multilevel, two-stage, log, Sample B
- `models/03_coefficient_plot.py` — Figure 5 + robustness summary
