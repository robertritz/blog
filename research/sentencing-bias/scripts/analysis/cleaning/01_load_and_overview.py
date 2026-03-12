#!/usr/bin/env python3
"""Step 1: Load extracted.json, filter to valid cases, print overview."""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"

print("Loading extracted.json...")
with open(DATA / "extracted.json", "r", encoding="utf-8") as f:
    raw = json.load(f)
print(f"Total cases: {len(raw)}")

# Data quality breakdown
quality_issues = Counter(c.get("data_quality_issue") for c in raw)
print("\nData quality breakdown:")
for issue, count in quality_issues.most_common():
    label = issue if issue else "valid"
    print(f"  {label}: {count}")

# Filter to valid
valid = [c for c in raw if c.get("data_quality_issue") is None]
print(f"\nValid cases: {len(valid)}")

# Extraction quality
eq = Counter(c.get("extraction_quality") for c in valid)
print("\nExtraction quality (LLM):")
for q, count in eq.most_common():
    print(f"  {q}: {count}")

# Field coverage
fields = [
    "gender", "age", "education", "employed", "occupation",
    "family_size", "prior_criminal", "sentence_type",
    "sentence_months", "sentence_fine_mnt",
    "aggravating_factors", "mitigating_factors",
    "victim_relationship", "victim_minor",
    "crime_amount_mnt", "injury_severity", "intoxicated_at_crime",
    "has_lawyer", "plea_agreement", "plea_guilty", "restitution_paid",
    "time_served_days", "sentence_suspended_months",
    "crime_article", "court", "judge", "case_date",
]

print(f"\nField coverage (N={len(valid)}):")
print(f"{'Field':<30} {'Count':>8} {'Coverage':>10}")
print("-" * 50)
for field in fields:
    count = sum(1 for c in valid if c.get(field) is not None)
    pct = count / len(valid) * 100
    print(f"{field:<30} {count:>8} {pct:>9.1f}%")

# Sentence type distribution
print("\nSentence type distribution:")
st = Counter(c.get("sentence_type") for c in valid)
for t, count in st.most_common(20):
    print(f"  {t}: {count}")

# Quick look at first case fields
print("\nSample case fields:")
sample = valid[0]
for k, v in sorted(sample.items()):
    val_str = repr(v)[:80]
    print(f"  {k}: {val_str}")
