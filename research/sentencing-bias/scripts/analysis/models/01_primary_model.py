#!/usr/bin/env python3
"""
Step 1: Primary OLS Model (PRE-REGISTERED, CONFIRMATORY).

Pre-registered specification (OSF):
  severity ~ female + age + age_sq + education_level + employed +
             C(crime_category) + prior_criminal +
             aggravating_count + mitigating_count +
             C(year) + C(court_id)

OLS with HC3 robust standard errors.
Sample A: complete cases on all core variables.

Outputs:
- Console: full regression table, hypothesis tests
- tables/table4_primary_model.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
TABLES = PROJECT / "tables"
TABLES.mkdir(exist_ok=True)

# ============================================================
# LOAD & PREPARE SAMPLE A
# ============================================================
df = pd.read_parquet(DATA / "sentencing_clean.parquet")

sample_a_vars = ["female", "age", "education_level", "employed",
                 "crime_category", "prior_criminal", "severity"]
sa = df.dropna(subset=sample_a_vars).copy()

# Use winsorized severity as DV
sa["sev"] = sa["severity_winsorized"]

# Ensure types
sa["female"] = sa["female"].astype(int)
sa["age"] = sa["age"].astype(float)
sa["age_sq"] = sa["age_sq"].astype(float)
sa["education_level"] = sa["education_level"].astype(float)
sa["employed"] = sa["employed"].astype(int)
sa["prior_criminal"] = sa["prior_criminal"].astype(int)
sa["aggravating_count"] = sa["aggravating_count"].astype(int)
sa["mitigating_count"] = sa["mitigating_count"].astype(int)

print(f"Sample A: N = {len(sa):,}")
print(f"DV (severity winsorized): mean={sa['sev'].mean():.2f}, SD={sa['sev'].std():.2f}")
print(f"Courts: {sa['court_id'].nunique()}, Years: {sorted(sa['year'].unique())}")

# ============================================================
# PRIMARY MODEL
# ============================================================
print("\n" + "=" * 70)
print("PRIMARY MODEL (PRE-REGISTERED)")
print("=" * 70)

formula = ("sev ~ female + age + age_sq + education_level + employed + "
           "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
           "aggravating_count + mitigating_count + "
           "C(year) + C(court_id)")

print(f"\nFormula: {formula}")
print("Estimator: OLS with HC3 robust SE\n")

model = smf.ols(formula, data=sa).fit(cov_type="HC3")

# Print key results (not the full summary with 47 court dummies)
print(f"R-squared: {model.rsquared:.4f}")
print(f"Adj R-squared: {model.rsquared_adj:.4f}")
print(f"F-statistic: {model.fvalue:.2f} (p = {model.f_pvalue:.2e})")
print(f"N: {model.nobs:.0f}")
print(f"Parameters: {model.df_model:.0f}")

# ============================================================
# HYPOTHESIS VARIABLES
# ============================================================
print("\n" + "=" * 70)
print("HYPOTHESIS TEST RESULTS")
print("=" * 70)

hypothesis_vars = {
    "H1 (Gender → Female)": "female",
    "H2 (Education level)": "education_level",
    "H3a (Age)": "age",
    "H3b (Age²)": "age_sq",
    "H4 (Employed)": "employed",
}

# Expected directions from pre-registration:
# H1: female < 0 (females get less severe)
# H2: education < 0 (more educated get less severe)
# H3: age_sq < 0 (inverted U)
# H4: employed < 0 (employed get less severe)

h_results = []
print(f"\n{'Hypothesis':<25} {'Coeff':>8} {'SE':>8} {'t':>8} {'p':>10} {'95% CI':>20} {'Direction':>12}")
print("-" * 95)

for h_name, var_name in hypothesis_vars.items():
    coef = model.params[var_name]
    se = model.bse[var_name]
    t_val = model.tvalues[var_name]
    p_val = model.pvalues[var_name]
    ci = model.conf_int().loc[var_name]

    direction = "as predicted" if coef < 0 else "OPPOSITE"
    if "Age²" not in h_name and "Age)" not in h_name:
        pass  # keep direction logic
    else:
        if "Age²" in h_name:
            direction = "inverted-U" if coef < 0 else "U-shape"

    print(f"{h_name:<25} {coef:>8.4f} {se:>8.4f} {t_val:>8.3f} {p_val:>10.6f} [{ci[0]:>8.4f}, {ci[1]:>8.4f}] {direction:>12}")

    h_results.append({
        "hypothesis": h_name,
        "variable": var_name,
        "coefficient": coef,
        "se": se,
        "t": t_val,
        "p": p_val,
        "ci_low": ci[0],
        "ci_high": ci[1],
    })

# ============================================================
# HOLM-BONFERRONI CORRECTION
# ============================================================
print("\n" + "=" * 70)
print("HOLM-BONFERRONI CORRECTION (4 primary hypotheses)")
print("=" * 70)

# Use H1, H2, H3b (age_sq for non-linearity), H4
primary_tests = [
    ("H1 (Gender)", "female"),
    ("H2 (Education)", "education_level"),
    ("H3 (Age non-linear)", "age_sq"),
    ("H4 (Employment)", "employed"),
]

p_values = [(name, model.pvalues[var]) for name, var in primary_tests]
p_sorted = sorted(p_values, key=lambda x: x[1])

print(f"\n{'Hypothesis':<25} {'p-value':>12} {'Threshold':>12} {'Reject H0?':>12}")
print("-" * 65)
k = len(primary_tests)
for i, (name, p) in enumerate(p_sorted):
    threshold = 0.05 / (k - i)
    reject = "YES" if p < threshold else "NO"
    print(f"{name:<25} {p:>12.6f} {threshold:>12.6f} {reject:>12}")

# ============================================================
# CONTROL VARIABLES
# ============================================================
print("\n" + "=" * 70)
print("CONTROL VARIABLE COEFFICIENTS")
print("=" * 70)

control_vars = [
    "prior_criminal", "aggravating_count", "mitigating_count",
]
crime_cats = [p for p in model.params.index if "crime_category" in p]

print(f"\n{'Variable':<50} {'Coeff':>8} {'SE':>8} {'p':>10}")
print("-" * 80)

for var in control_vars:
    coef = model.params[var]
    se = model.bse[var]
    p = model.pvalues[var]
    print(f"{var:<50} {coef:>8.4f} {se:>8.4f} {p:>10.6f}")

for var in crime_cats:
    coef = model.params[var]
    se = model.bse[var]
    p = model.pvalues[var]
    # Clean label
    label = var.replace("C(crime_category, Treatment(reference='violent'))", "").strip("[]T.")
    print(f"Crime: {label:<43} {coef:>8.4f} {se:>8.4f} {p:>10.6f}")

# ============================================================
# STANDARDIZED COEFFICIENTS
# ============================================================
print("\n" + "=" * 70)
print("STANDARDIZED COEFFICIENTS (for magnitude comparison)")
print("=" * 70)

# Standardize all continuous/ordinal variables
std_vars = ["female", "age", "age_sq", "education_level", "employed",
            "prior_criminal", "aggravating_count", "mitigating_count"]

sa_std = sa.copy()
for var in std_vars:
    sa_std[var] = (sa_std[var] - sa_std[var].mean()) / sa_std[var].std()

# Also standardize DV
sa_std["sev"] = (sa_std["sev"] - sa_std["sev"].mean()) / sa_std["sev"].std()

model_std = smf.ols(formula, data=sa_std).fit(cov_type="HC3")

print(f"\n{'Variable':<25} {'Std. Coeff':>12} {'Rank':>6}")
print("-" * 45)

std_results = []
for var in std_vars:
    beta = model_std.params[var]
    std_results.append((var, abs(beta), beta))

std_results.sort(key=lambda x: x[1], reverse=True)
for rank, (var, abs_beta, beta) in enumerate(std_results, 1):
    print(f"{var:<25} {beta:>12.4f} {rank:>6}")

# ============================================================
# MODEL FIT DIAGNOSTICS
# ============================================================
print("\n" + "=" * 70)
print("MODEL DIAGNOSTICS")
print("=" * 70)

residuals = model.resid
print(f"\nResidual stats: mean={residuals.mean():.6f}, SD={residuals.std():.2f}")
print(f"Skewness: {residuals.skew():.2f}")
print(f"Kurtosis: {residuals.kurtosis():.2f}")

# Variance explained by each group of variables
# (partial R² approximation via sequential models)
print("\n--- Variance Decomposition (sequential) ---")

formulas = [
    ("Demographics only", "sev ~ female + age + age_sq + education_level + employed"),
    ("+ Crime controls", "sev ~ female + age + age_sq + education_level + employed + "
     "C(crime_category, Treatment(reference='violent')) + prior_criminal"),
    ("+ Sentencing factors", "sev ~ female + age + age_sq + education_level + employed + "
     "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
     "aggravating_count + mitigating_count"),
    ("+ Year FE", "sev ~ female + age + age_sq + education_level + employed + "
     "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
     "aggravating_count + mitigating_count + C(year)"),
    ("+ Court FE (full)", formula),
]

prev_r2 = 0
for name, f in formulas:
    m = smf.ols(f, data=sa).fit()
    delta = m.rsquared - prev_r2
    print(f"  {name:<30}: R²={m.rsquared:.4f} (Δ={delta:+.4f})")
    prev_r2 = m.rsquared

# ============================================================
# EXPORT
# ============================================================
print("\n--- Exporting results ---")

# Full coefficient table for hypothesis vars + controls
rows = []
for var in list(hypothesis_vars.values()) + control_vars:
    rows.append({
        "variable": var,
        "coefficient": model.params[var],
        "se": model.bse[var],
        "t": model.tvalues[var],
        "p": model.pvalues[var],
        "ci_low": model.conf_int().loc[var][0],
        "ci_high": model.conf_int().loc[var][1],
        "std_coeff": model_std.params.get(var, np.nan),
    })

results_df = pd.DataFrame(rows)
results_df.to_csv(TABLES / "table4_primary_model.csv", index=False)
print(f"Saved to {TABLES / 'table4_primary_model.csv'}")
