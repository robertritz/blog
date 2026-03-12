#!/usr/bin/env python3
"""
Step 2: Robustness Models (PRE-REGISTERED).

1. Multilevel model with court random intercepts (ICC)
2. Two-stage selection model (Heckman-like)
3. Log-severity OLS (address skewness)
4. Sample B (without age, larger N)
5. Coefficient stability across specifications
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
TABLES = PROJECT / "tables"

df = pd.read_parquet(DATA / "sentencing_clean.parquet")

# ============================================================
# PREPARE SAMPLES
# ============================================================
sa_vars = ["female", "age", "education_level", "employed",
           "crime_category", "prior_criminal", "severity"]
sa = df.dropna(subset=sa_vars).copy()
sa["sev"] = sa["severity_winsorized"]
sa["female"] = sa["female"].astype(int)
sa["age"] = sa["age"].astype(float)
sa["age_sq"] = sa["age_sq"].astype(float)
sa["education_level"] = sa["education_level"].astype(float)
sa["employed"] = sa["employed"].astype(int)
sa["prior_criminal"] = sa["prior_criminal"].astype(int)

# Sample B: no age requirement
sb_vars = ["female", "crime_category", "prior_criminal", "severity"]
sb = df.dropna(subset=sb_vars + ["employed", "education_level"]).copy()
sb["sev"] = sb["severity_winsorized"]
sb["female"] = sb["female"].astype(int)
sb["education_level"] = sb["education_level"].astype(float)
sb["employed"] = sb["employed"].astype(int)
sb["prior_criminal"] = sb["prior_criminal"].astype(int)

print(f"Sample A: N = {len(sa):,}")
print(f"Sample B (no age): N = {len(sb):,}")

# ============================================================
# 1. MULTILEVEL MODEL (court random intercepts)
# ============================================================
print("\n" + "=" * 70)
print("ROBUSTNESS 1: MULTILEVEL MODEL (Court Random Intercepts)")
print("=" * 70)

# MixedLM formula (no court FE, court as random intercept)
ml_formula = ("sev ~ female + age + age_sq + education_level + employed + "
              "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
              "aggravating_count + mitigating_count + C(year)")

print(f"\nFormula: {ml_formula}")
print("Random effect: (1 | court_id)\n")

ml_model = smf.mixedlm(ml_formula, data=sa, groups=sa["court_id"]).fit(reml=True)

# ICC
var_court = ml_model.cov_re.iloc[0, 0]
var_resid = ml_model.scale
icc = var_court / (var_court + var_resid)
print(f"Court random intercept variance: {var_court:.4f}")
print(f"Residual variance: {var_resid:.4f}")
print(f"ICC: {icc:.4f} ({icc*100:.1f}% of variance between courts)")

# Key coefficients
print(f"\n{'Variable':<25} {'Coeff':>8} {'SE':>8} {'p':>10}")
print("-" * 55)
for var in ["female", "age", "age_sq", "education_level", "employed",
            "prior_criminal", "aggravating_count", "mitigating_count"]:
    coef = ml_model.fe_params[var]
    se = ml_model.bse_fe[var]
    z = coef / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    print(f"{var:<25} {coef:>8.4f} {se:>8.4f} {p:>10.6f}")

# ============================================================
# 2. TWO-STAGE SELECTION MODEL
# ============================================================
print("\n" + "=" * 70)
print("ROBUSTNESS 2: TWO-STAGE SELECTION MODEL")
print("=" * 70)

# Stage 1: P(imprisonment) among all Sample A cases
sa["imprisoned"] = (sa["sentence_type"] == "imprisonment").astype(int)
print(f"\nImprisoned: {sa['imprisoned'].sum()} / {len(sa)} ({sa['imprisoned'].mean()*100:.1f}%)")

logit_formula = ("imprisoned ~ female + age + age_sq + education_level + employed + "
                 "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
                 "aggravating_count + mitigating_count + C(year)")

logit = smf.logit(logit_formula, data=sa).fit(disp=0)

print(f"\nStage 1: Logistic regression for P(imprisonment)")
print(f"Pseudo R²: {logit.prsquared:.4f}")

# Key coefficients (odds ratios)
print(f"\n{'Variable':<25} {'Coeff':>8} {'OR':>8} {'p':>10}")
print("-" * 55)
for var in ["female", "age", "age_sq", "education_level", "employed",
            "prior_criminal", "aggravating_count", "mitigating_count"]:
    coef = logit.params[var]
    or_val = np.exp(coef)
    p = logit.pvalues[var]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"{var:<25} {coef:>8.4f} {or_val:>8.4f} {p:>10.6f} {sig}")

# Stage 2: OLS for sentence_months | imprisoned
sa_imp = sa[(sa["imprisoned"] == 1) & (sa["sentence_months"].notna())].copy()
sa_imp["months"] = sa_imp["sentence_months"].astype(float)
print(f"\nStage 2: OLS for sentence_months | imprisoned")
print(f"N = {len(sa_imp):,}")
print(f"Months: mean={sa_imp['months'].mean():.1f}, median={sa_imp['months'].median():.1f}")

if len(sa_imp) >= 100:
    ols2_formula = ("months ~ female + age + age_sq + education_level + employed + "
                    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
                    "aggravating_count + mitigating_count + C(year)")

    ols2 = smf.ols(ols2_formula, data=sa_imp).fit(cov_type="HC3")

    print(f"R²: {ols2.rsquared:.4f}")
    print(f"\n{'Variable':<25} {'Coeff':>8} {'SE':>8} {'p':>10}")
    print("-" * 55)
    for var in ["female", "age", "age_sq", "education_level", "employed",
                "prior_criminal", "aggravating_count", "mitigating_count"]:
        coef = ols2.params[var]
        se = ols2.bse[var]
        p = ols2.pvalues[var]
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{var:<25} {coef:>8.4f} {se:>8.4f} {p:>10.6f} {sig}")

# ============================================================
# 3. LOG-SEVERITY MODEL (address skewness)
# ============================================================
print("\n" + "=" * 70)
print("ROBUSTNESS 3: LOG-SEVERITY MODEL")
print("=" * 70)

sa_log = sa[sa["sev"] > 0].copy()
sa_log["log_sev"] = np.log(sa_log["sev"])
print(f"N (sev > 0): {len(sa_log):,}")
print(f"log(severity): mean={sa_log['log_sev'].mean():.2f}, SD={sa_log['log_sev'].std():.2f}")

log_formula = ("log_sev ~ female + age + age_sq + education_level + employed + "
               "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
               "aggravating_count + mitigating_count + C(year) + C(court_id)")

log_model = smf.ols(log_formula, data=sa_log).fit(cov_type="HC3")
print(f"R²: {log_model.rsquared:.4f}")
print(f"Residual skewness: {log_model.resid.skew():.2f} (vs 3.57 in level model)")

print(f"\n{'Variable':<25} {'Coeff':>8} {'SE':>8} {'p':>10} {'% change':>10}")
print("-" * 67)
for var in ["female", "age", "age_sq", "education_level", "employed",
            "prior_criminal", "aggravating_count", "mitigating_count"]:
    coef = log_model.params[var]
    se = log_model.bse[var]
    p = log_model.pvalues[var]
    pct = (np.exp(coef) - 1) * 100
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"{var:<25} {coef:>8.4f} {se:>8.4f} {p:>10.6f} {pct:>+9.1f}% {sig}")

# ============================================================
# 4. SAMPLE B (WITHOUT AGE, LARGER N)
# ============================================================
print("\n" + "=" * 70)
print("ROBUSTNESS 4: SAMPLE B (without age, N={:,})".format(len(sb)))
print("=" * 70)

sb_formula = ("sev ~ female + education_level + employed + "
              "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
              "aggravating_count + mitigating_count + C(year) + C(court_id)")

sb_model = smf.ols(sb_formula, data=sb).fit(cov_type="HC3")
print(f"R²: {sb_model.rsquared:.4f}")

print(f"\n{'Variable':<25} {'Coeff':>8} {'SE':>8} {'p':>10}")
print("-" * 55)
for var in ["female", "education_level", "employed", "prior_criminal",
            "aggravating_count", "mitigating_count"]:
    coef = sb_model.params[var]
    se = sb_model.bse[var]
    p = sb_model.pvalues[var]
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"{var:<25} {coef:>8.4f} {se:>8.4f} {p:>10.6f} {sig}")

# ============================================================
# 5. COEFFICIENT STABILITY TABLE
# ============================================================
print("\n" + "=" * 70)
print("COEFFICIENT STABILITY ACROSS SPECIFICATIONS")
print("=" * 70)

# Collect key coefficients across models
models_summary = {
    "Primary OLS": {},
    "Multilevel": {},
    "Log-severity": {},
    "Sample B": {},
    "Stage 2 (imprison.)": {},
}

# Primary OLS (re-run quickly for this table)
primary_formula = ("sev ~ female + age + age_sq + education_level + employed + "
                   "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
                   "aggravating_count + mitigating_count + C(year) + C(court_id)")
primary = smf.ols(primary_formula, data=sa).fit(cov_type="HC3")

for var in ["female", "education_level", "employed"]:
    models_summary["Primary OLS"][var] = (primary.params[var], primary.pvalues[var])
    if var in ml_model.fe_params.index:
        z = ml_model.fe_params[var] / ml_model.bse_fe[var]
        p_ml = 2 * (1 - stats.norm.cdf(abs(z)))
        models_summary["Multilevel"][var] = (ml_model.fe_params[var], p_ml)
    if var in log_model.params.index:
        models_summary["Log-severity"][var] = (log_model.params[var], log_model.pvalues[var])
    if var in sb_model.params.index:
        models_summary["Sample B"][var] = (sb_model.params[var], sb_model.pvalues[var])
    if len(sa_imp) >= 100 and var in ols2.params.index:
        models_summary["Stage 2 (imprison.)"][var] = (ols2.params[var], ols2.pvalues[var])

print(f"\n{'Variable':<20}", end="")
for model_name in models_summary:
    print(f" {model_name:>22}", end="")
print()
print("-" * (20 + 23 * len(models_summary)))

for var in ["female", "education_level", "employed"]:
    print(f"{var:<20}", end="")
    for model_name, coeffs in models_summary.items():
        if var in coeffs:
            coef, p = coeffs[var]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f" {coef:>18.4f}{sig:>3s}", end="")
        else:
            print(f" {'—':>21s}", end="")
    print()

# Export stability table
stability_rows = []
for var in ["female", "education_level", "employed"]:
    row = {"variable": var}
    for model_name, coeffs in models_summary.items():
        if var in coeffs:
            coef, p = coeffs[var]
            row[f"{model_name}_coef"] = coef
            row[f"{model_name}_p"] = p
    stability_rows.append(row)

stability_df = pd.DataFrame(stability_rows)
stability_df.to_csv(TABLES / "table5_stability.csv", index=False)
print(f"\nSaved to {TABLES / 'table5_stability.csv'}")
