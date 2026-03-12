#!/usr/bin/env python3
"""
Step 3: Coefficient Plot (Forest Plot) for primary model + robustness.

Figure 5: Forest plot comparing hypothesis variable coefficients across specs.
Table 6: Complete robustness summary.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy import stats

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
FIGURES = PROJECT / "figures"
TABLES = PROJECT / "tables"

df = pd.read_parquet(DATA / "sentencing_clean.parquet")

# ============================================================
# PREPARE SAMPLES AND RUN ALL MODELS
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

base_formula = ("sev ~ female + age + age_sq + education_level + employed + "
                "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
                "aggravating_count + mitigating_count + C(year) + C(court_id)")

# 1. Primary OLS
m1 = smf.ols(base_formula, data=sa).fit(cov_type="HC3")

# 2. Log-severity
sa_log = sa[sa["sev"] > 0].copy()
sa_log["log_sev"] = np.log(sa_log["sev"])
log_formula = base_formula.replace("sev ~", "log_sev ~")
m2 = smf.ols(log_formula, data=sa_log).fit(cov_type="HC3")

# 3. No court FE
no_court_formula = base_formula.replace(" + C(court_id)", "")
m3 = smf.ols(no_court_formula, data=sa).fit(cov_type="HC3")

# 4. Sample B (no age)
sb_vars = ["female", "crime_category", "prior_criminal", "severity"]
sb = df.dropna(subset=sb_vars + ["employed", "education_level"]).copy()
sb["sev"] = sb["severity_winsorized"]
sb["female"] = sb["female"].astype(int)
sb["education_level"] = sb["education_level"].astype(float)
sb["employed"] = sb["employed"].astype(int)
sb["prior_criminal"] = sb["prior_criminal"].astype(int)
sb_formula = ("sev ~ female + education_level + employed + "
              "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
              "aggravating_count + mitigating_count + C(year) + C(court_id)")
m4 = smf.ols(sb_formula, data=sb).fit(cov_type="HC3")

# ============================================================
# FIGURE 5: FOREST PLOT
# ============================================================
hyp_vars = ["female", "education_level", "employed"]
hyp_labels = ["Female\n(H1)", "Education level\n(H2)", "Employed\n(H4)"]

models = [
    ("Primary OLS\n(N=29,847)", m1),
    ("No court FE\n(N=29,847)", m3),
    ("Sample B\n(N=36,829)", m4),
]

fig, ax = plt.subplots(figsize=(10, 6))

y_positions = np.arange(len(hyp_vars))
n_models = len(models)
height = 0.8 / n_models
colors = ["#4C72B0", "#55A868", "#DD8452", "#C44E52"]

for i, (model_name, model) in enumerate(models):
    offsets = y_positions + (i - n_models/2 + 0.5) * height
    for j, var in enumerate(hyp_vars):
        if var in model.params.index:
            coef = model.params[var]
            ci = model.conf_int().loc[var]
            ax.errorbar(coef, offsets[j], xerr=[[coef - ci[0]], [ci[1] - coef]],
                       fmt="o", color=colors[i], capsize=4, markersize=6,
                       label=model_name if j == 0 else "")

ax.axvline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
ax.set_yticks(y_positions)
ax.set_yticklabels(hyp_labels)
ax.set_xlabel("Coefficient (severity month-equivalents)")
ax.set_title("Figure 5: Hypothesis Variable Coefficients Across Specifications", fontweight="bold")
ax.legend(loc="lower left", fontsize=9)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(FIGURES / "fig5_coefficient_plot.png", bbox_inches="tight", dpi=150)
print(f"Saved {FIGURES / 'fig5_coefficient_plot.png'}")
plt.close()

# ============================================================
# TABLE 6: COMPLETE ROBUSTNESS SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("TABLE 6: ROBUSTNESS SUMMARY")
print("=" * 100)

all_models = {
    "Primary OLS": m1,
    "Log-severity": m2,
    "No court FE": m3,
    "Sample B": m4,
}

all_vars = ["female", "age", "age_sq", "education_level", "employed",
            "prior_criminal", "aggravating_count", "mitigating_count"]

header = f"{'Variable':<22}"
for name in all_models:
    header += f" {name:>16}"
print(header)
print("-" * (22 + 17 * len(all_models)))

for var in all_vars:
    row = f"{var:<22}"
    for name, model in all_models.items():
        if var in model.params.index:
            coef = model.params[var]
            p = model.pvalues[var]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            row += f" {coef:>12.4f}{sig:>3s}"
        else:
            row += f" {'—':>15s}"
    print(row)

# R² row
row = f"{'R²':<22}"
for name, model in all_models.items():
    row += f" {model.rsquared:>15.4f}"
print(row)

# N row
row = f"{'N':<22}"
for name, model in all_models.items():
    row += f" {model.nobs:>15,.0f}"
print(row)

# Export
rows = []
for var in all_vars:
    r = {"variable": var}
    for name, model in all_models.items():
        if var in model.params.index:
            r[f"{name}_coef"] = model.params[var]
            r[f"{name}_p"] = model.pvalues[var]
    rows.append(r)

pd.DataFrame(rows).to_csv(TABLES / "table6_robustness.csv", index=False)
print(f"\nSaved to {TABLES / 'table6_robustness.csv'}")

# ============================================================
# SUMMARY: HYPOTHESIS SUPPORT
# ============================================================
print("\n" + "=" * 100)
print("FINAL HYPOTHESIS ASSESSMENT")
print("=" * 100)

print("""
H1 (Gender → lower severity for females):
  Primary model: β = -0.49, p = 0.074 — NOT significant
  Log model:     β = -0.14, p < 0.001 — significant (−13.4%)
  Sample B:      β = -0.49, p = 0.042 — significant
  Two-stage:     Stage 1 OR = 0.59 (p < 0.001), Stage 2 β = +4.0 (p = 0.003)
  VERDICT: MIXED. Direction consistent, significance depends on specification.
           Strong gender effect on imprisonment decision, reversed for sentence length.

H2 (Education → lower severity):
  Primary model: β = -0.20, p = 0.053 — NOT significant
  Log model:     β = +0.02, p < 0.001 — REVERSED
  Sample B:      β = -0.10, p = 0.267 — NOT significant
  VERDICT: NOT SUPPORTED. Effect is small and not robust to specification.

H3 (Age non-linear → inverted U-shape):
  Primary model: age² = -0.0007, p = 0.409 — NOT significant
  Log model:     age² = -0.0001, p = 0.092 — NOT significant
  VERDICT: NOT SUPPORTED. Linear age effect exists but no curvature.

H4 (Employment → lower severity):
  Primary model: β = -3.74, p < 0.001 — significant
  Log model:     β = -0.21, p < 0.001 — significant (−18.7%)
  Sample B:      β = -3.73, p < 0.001 — significant
  Two-stage:     Stage 1 OR = 0.43 (p < 0.001), Stage 2 β = -2.23 (p = 0.021)
  VERDICT: STRONGLY SUPPORTED across all specifications.
""")
