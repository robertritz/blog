#!/usr/bin/env python3
"""
Step 3: Clean data and export to parquet.

Transforms:
- Filter to valid cases
- Normalize sentence types (39 -> 5 main + exclude)
- Normalize education (mixed EN/MN -> ordinal 0-5)
- Parse crime articles -> crime categories (5 pre-registered)
- Derive variables (female, age_sq, aggravating_count, etc.)
- Calculate severity scores
- Validate and export
"""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
sys.path.insert(0, str(PROJECT / "src"))

# ============================================================
# LOAD
# ============================================================
print("Loading extracted.json...")
with open(DATA / "extracted.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

df = pd.DataFrame(raw)
print(f"Total: {len(df)}")

# Filter to valid
df = df[df["data_quality_issue"].isna()].copy()
print(f"Valid (no quality issues): {len(df)}")

# ============================================================
# SENTENCE TYPE NORMALIZATION
# ============================================================
print("\n--- Sentence Type Normalization ---")

MAIN_TYPES = {"fine", "imprisonment", "community_service", "suspended", "probation"}

# Map all variants
SENTENCE_MAP = {}
# Acquittals
for v in ["acquittal", "acquitted", "dismissed", "amnesty", "pardon", "diversion"]:
    SENTENCE_MAP[v] = "_exclude_acquittal"
# Driving/movement restrictions (supplementary penalties)
for v in [
    "driving_ban", "driving ban", "driving_restriction", "driving_restricted",
    "driving_privilege_suspension", "driving_privileges_suspended",
    "driving_privileges_restricted", "driving_privilege_restriction",
    "driving_license_suspension", "driving_ban_restriction",
    "driving_ban_and_travel_restriction",
    "travel_restriction", "restricted_travel",
    "movement_restriction", "restricted_movement",
    "right_restriction", "rights_restriction", "public_office_ban",
]:
    SENTENCE_MAP[v] = "_exclude_supplementary"
# Medical
for v in [
    "compulsory_medical_treatment", "medical_compulsory_treatment",
    "involuntary_treatment", "medical_treatment",
    "involuntary_medical_treatment", "medical_compulsion",
    "involuntary_commitment", "hospitalization",
]:
    SENTENCE_MAP[v] = "_exclude_medical"
# Other
SENTENCE_MAP["other"] = "_exclude_other"
SENTENCE_MAP["none"] = None

# Apply mapping
def normalize_sentence_type(st):
    if st is None or pd.isna(st):
        return None
    if st in MAIN_TYPES:
        return st
    return SENTENCE_MAP.get(st, f"_unknown:{st}")

df["sentence_type_clean"] = df["sentence_type"].apply(normalize_sentence_type)

# Report
st_counts = df["sentence_type_clean"].value_counts(dropna=False)
print("\nCleaned sentence types:")
for t, c in st_counts.items():
    print(f"  {str(t):35s} {c:>6}")

# Filter to main types only
n_before = len(df)
df = df[df["sentence_type_clean"].isin(MAIN_TYPES)].copy()
df["sentence_type"] = df["sentence_type_clean"]
df.drop(columns=["sentence_type_clean"], inplace=True)
print(f"\nKept {len(df)} cases with main sentence types (dropped {n_before - len(df)})")

# ============================================================
# EDUCATION NORMALIZATION
# ============================================================
print("\n--- Education Normalization ---")

EDUCATION_MAP = {
    # English (from LLM)
    "primary": ("primary", 1),
    "basic": ("basic", 2),
    "secondary": ("secondary", 3),
    "incomplete secondary": ("secondary", 3),
    "vocational": ("vocational", 4),
    "higher": ("higher", 5),
    "none": ("none", 0),
    "illiterate": ("none", 0),
    # Mongolian (from regex fallback)
    "бага": ("primary", 1),
    "суурь": ("basic", 2),
    "бүрэн дунд": ("secondary", 3),
    "тусгай дунд": ("vocational", 4),
    "дээд": ("higher", 5),
    "боловсролгүй": ("none", 0),
    # Ambiguous
    "боловсролтой": None,  # "educated" - too vague
}

def normalize_education(edu):
    if edu is None or (isinstance(edu, float) and np.isnan(edu)):
        return None, None
    result = EDUCATION_MAP.get(edu)
    if result is None:
        return None, None
    return result

edu_results = df["education"].apply(normalize_education)
df["education_clean"] = edu_results.apply(lambda x: x[0])
df["education_level"] = edu_results.apply(lambda x: x[1])

edu_counts = df["education_clean"].value_counts(dropna=False)
print("\nCleaned education:")
for e, c in edu_counts.items():
    print(f"  {str(e):20s} {c:>6}")

# ============================================================
# CRIME CATEGORY MAPPING
# ============================================================
print("\n--- Crime Category Mapping ---")

CRIME_CATEGORY_MAP = {
    10: "violent",    # homicide
    11: "violent",    # assault/bodily harm
    12: "violent",    # sexual offenses
    13: "violent",    # against liberty
    17: "property",   # theft, fraud, embezzlement
    18: "property",   # economic crimes
    20: "drug",       # drug offenses
    27: "traffic",    # DUI, traffic
    # Everything else -> other (ch 14-16, 19, 21-26, 28, old code 80+)
}

def parse_crime(art):
    """Parse primary article and map to category."""
    if art is None or (isinstance(art, float) and np.isnan(art)):
        return None, None, None
    first = str(art).split(",")[0].strip().rstrip(".")
    parts = first.split(".")
    try:
        chapter = int(parts[0])
        category = CRIME_CATEGORY_MAP.get(chapter, "other")
        return first, chapter, category
    except (ValueError, IndexError):
        return first, None, None

crime_results = df["crime_article"].apply(parse_crime)
df["primary_article"] = crime_results.apply(lambda x: x[0])
df["crime_chapter"] = crime_results.apply(lambda x: x[1])
df["crime_category"] = crime_results.apply(lambda x: x[2])

cat_counts = df["crime_category"].value_counts(dropna=False)
print("\nCrime categories:")
for c, n in cat_counts.items():
    print(f"  {str(c):15s} {n:>6}")

# ============================================================
# DERIVED VARIABLES
# ============================================================
print("\n--- Derived Variables ---")

# Female binary
df["female"] = (df["gender"] == "female").astype("Int64")
df.loc[df["gender"].isna(), "female"] = pd.NA

# Clean invalid ages (< 14 are victim ages or parsing errors)
n_invalid_age = (df["age"] < 14).sum()
df.loc[df["age"] < 14, "age"] = pd.NA
print(f"Set {n_invalid_age} ages < 14 to NA (victim ages / parsing errors)")

# Age squared
df["age_sq"] = df["age"].astype("Int64") ** 2

# Aggravating/mitigating counts
df["aggravating_count"] = df["aggravating_factors"].apply(
    lambda x: len(x) if isinstance(x, list) else 0
)
df["mitigating_count"] = df["mitigating_factors"].apply(
    lambda x: len(x) if isinstance(x, list) else 0
)

# Year
df["year"] = pd.to_datetime(df["case_date"]).dt.year

# Court location (UB vs aimag)
UB_KEYWORDS = [
    "Баянзүрх", "Баянгол", "Сүхбаатар дүүрг", "Чингэлтэй",
    "Хан-Уул", "Сонгинохайрхан", "Налайх", "Багануур", "Багахангай",
]
df["is_ub"] = df["court"].apply(
    lambda x: int(any(kw in str(x) for kw in UB_KEYWORDS))
)

# Court ID (shortened)
court_names = df["court"].unique()
court_id_map = {name: f"court_{i:02d}" for i, name in enumerate(sorted(court_names))}
df["court_id"] = df["court"].map(court_id_map)

print(f"Female: {df['female'].sum()} / {df['female'].notna().sum()} with gender")
print(f"Age available: {df['age'].notna().sum()}")
print(f"UB courts: {df['is_ub'].sum()} ({df['is_ub'].mean()*100:.1f}%)")
print(f"Unique courts: {df['court_id'].nunique()}")
print(f"\nAggravating count distribution:")
print(df["aggravating_count"].value_counts().sort_index().head(8).to_string())
print(f"\nMitigating count distribution:")
print(df["mitigating_count"].value_counts().sort_index().head(8).to_string())
print(f"\nYear distribution:")
print(df["year"].value_counts().sort_index().to_string())

# ============================================================
# SEVERITY CALCULATION
# ============================================================
print("\n--- Severity Calculation ---")

from severity_scale import calculate_severity, DEFAULT_WEIGHTS

# Check current severity_scale implementation
print("Testing severity_scale.calculate_severity()...")
test_cases = [
    ("imprisonment", 12, None, None, "12 months imprisonment"),
    ("suspended", 24, None, None, "24 months suspended"),
    ("probation", 12, None, None, "12 months probation"),
    ("fine", None, 450000, None, "450K MNT fine"),
    ("community_service", None, None, 320, "320 hours community service"),
]
for st, months, fine, hours, desc in test_cases:
    try:
        sev = calculate_severity(st, months, fine, hours)
        print(f"  {desc:35s} -> severity = {sev}")
    except Exception as e:
        print(f"  {desc:35s} -> ERROR: {e}")

# Apply severity to all cases
def compute_severity(row):
    return calculate_severity(
        sentence_type=row["sentence_type"],
        sentence_months=row.get("sentence_months"),
        sentence_fine_mnt=row.get("sentence_fine_mnt"),
        community_service_hours=row.get("sentence_community_hours"),
    )

df["severity"] = df.apply(compute_severity, axis=1)

print(f"\nSeverity coverage: {df['severity'].notna().sum()} / {len(df)} ({df['severity'].notna().mean()*100:.1f}%)")
print(f"\nSeverity by sentence type:")
for st in MAIN_TYPES:
    mask = df["sentence_type"] == st
    sev = df.loc[mask, "severity"]
    coverage = sev.notna().sum() / mask.sum() * 100
    print(f"  {st:20s}: N={mask.sum():>6}, severity coverage={coverage:.1f}%, "
          f"mean={sev.mean():.2f}, median={sev.median():.2f}, max={sev.max():.1f}")

# Winsorize at 99th percentile
p99 = df["severity"].quantile(0.99)
print(f"\n99th percentile: {p99:.2f}")
df["severity_winsorized"] = df["severity"].clip(upper=p99)
df["severity_outlier"] = df["severity"] > p99

# ============================================================
# VALIDATION
# ============================================================
print("\n--- Validation Checks ---")

checks = {
    "age_valid": ((df["age"] >= 14) & (df["age"] <= 100)) | df["age"].isna(),
    "severity_non_negative": (df["severity"] >= 0) | df["severity"].isna(),
    "gender_binary": df["gender"].isin(["male", "female"]) | df["gender"].isna(),
    "date_in_range": (df["case_date"] >= "2020-01-01") & (df["case_date"] <= "2026-02-04"),
    "crime_article_exists": df["crime_article"].notna(),
}

for name, check in checks.items():
    failed = (~check).sum()
    print(f"  {name}: {failed} failures ({failed/len(df)*100:.2f}%)")

# ============================================================
# MISSING DATA ANALYSIS
# ============================================================
print("\n--- Missing Data Summary ---")

core_vars = ["female", "age", "education_level", "employed", "prior_criminal",
             "crime_category", "severity", "aggravating_count", "mitigating_count"]

print(f"\n{'Variable':<25} {'N Present':>10} {'N Missing':>10} {'% Missing':>10}")
print("-" * 57)
for var in core_vars:
    present = df[var].notna().sum()
    missing = df[var].isna().sum()
    pct = missing / len(df) * 100
    print(f"{var:<25} {present:>10} {missing:>10} {pct:>9.1f}%")

# ============================================================
# ANALYSIS SAMPLES
# ============================================================
print("\n--- Analysis Samples ---")

# Sample A: Primary model (all core vars)
sample_a_vars = ["female", "age", "education_level", "employed",
                 "crime_category", "prior_criminal", "severity"]
sample_a = df.dropna(subset=sample_a_vars)
print(f"Sample A (primary model, all core vars): {len(sample_a)}")

# What's the binding constraint?
for var in sample_a_vars:
    remaining = df.dropna(subset=[v for v in sample_a_vars if v != var])
    print(f"  Without {var} requirement: {len(remaining)} (+{len(remaining) - len(sample_a)})")

# Sample B: Gender-focused (relaxed)
sample_b = df.dropna(subset=["female", "crime_category", "prior_criminal", "severity"])
print(f"\nSample B (gender-focused): {len(sample_b)}")

# Sample C: Two-stage
sample_c1 = df.dropna(subset=["female", "age", "crime_category", "prior_criminal"])
sample_c2 = sample_c1[sample_c1["sentence_type"] == "imprisonment"]
sample_c2_with_months = sample_c2.dropna(subset=["sentence_months"])
print(f"Sample C stage 1 (incarceration selection): {len(sample_c1)}")
print(f"Sample C stage 2 (imprisoned): {len(sample_c2)}")
print(f"Sample C stage 2 (with months): {len(sample_c2_with_months)}")

# ============================================================
# EXPORT
# ============================================================
print("\n--- Export ---")

# Select columns for parquet
export_cols = [
    # IDs and metadata
    "case_id", "case_index", "case_number", "case_date", "year",
    "court", "court_id", "is_ub", "judge", "prosecutor",
    # Crime
    "crime_article", "primary_article", "crime_chapter", "crime_category",
    # Demographics
    "gender", "female", "age", "age_sq",
    "education_clean", "education_level",
    "employed", "occupation", "family_size",
    "prior_criminal",
    # Sentence
    "sentence_type", "sentence_months", "sentence_fine_mnt",
    "sentence_community_hours", "sentence_suspended_months",
    "severity", "severity_winsorized", "severity_outlier",
    # Sentencing factors
    "aggravating_factors", "mitigating_factors",
    "aggravating_count", "mitigating_count",
    # v2 controls
    "victim_relationship", "victim_minor",
    "crime_amount_mnt", "injury_severity", "intoxicated_at_crime",
    "has_lawyer", "plea_agreement", "plea_guilty", "restitution_paid",
    "time_served_days",
    # Quality
    "extraction_quality", "extraction_method",
]

# Only include columns that exist
export_cols = [c for c in export_cols if c in df.columns]
df_export = df[export_cols].copy()

output_path = DATA / "sentencing_clean.parquet"
df_export.to_parquet(output_path, index=False)
print(f"Exported {len(df_export)} cases to {output_path}")
print(f"File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
print(f"Columns: {len(export_cols)}")
