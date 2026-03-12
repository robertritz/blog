#!/usr/bin/env python3
"""Step 2: Inspect categorical fields that need normalization."""

import json
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"

with open(DATA / "extracted.json", "r", encoding="utf-8") as f:
    raw = json.load(f)
valid = [c for c in raw if c.get("data_quality_issue") is None]

# --- Sentence type (all values) ---
print("=" * 60)
print("SENTENCE TYPE VALUES")
print("=" * 60)
st = Counter(c.get("sentence_type") for c in valid)
for t, count in st.most_common():
    print(f"  {t!r:45s} {count:>6}")

# --- Education values ---
print("\n" + "=" * 60)
print("EDUCATION VALUES")
print("=" * 60)
edu = Counter(c.get("education") for c in valid)
for e, count in edu.most_common():
    print(f"  {e!r:45s} {count:>6}")

# Also check education_level (the ordinal from regex)
print("\nEDUCATION_LEVEL (ordinal from regex):")
el = Counter(c.get("education_level") for c in valid)
for e, count in el.most_common():
    print(f"  {e!r:45s} {count:>6}")

# --- Crime article chapters ---
print("\n" + "=" * 60)
print("CRIME ARTICLE - TOP 30 ARTICLES")
print("=" * 60)
articles = Counter()
for c in valid:
    art = c.get("crime_article")
    if art:
        first = art.split(",")[0].strip().rstrip(".")
        articles[first] += 1
for a, count in articles.most_common(30):
    print(f"  {a:20s} {count:>6}")

# --- Crime chapters ---
print("\n" + "=" * 60)
print("CRIME CHAPTERS")
print("=" * 60)
chapters = Counter()
for c in valid:
    art = c.get("crime_article")
    if art:
        first = art.split(",")[0].strip().rstrip(".")
        parts = first.split(".")
        try:
            ch = int(parts[0])
            chapters[ch] += 1
        except ValueError:
            chapters[f"invalid:{parts[0]}"] += 1
for ch, count in sorted(chapters.items(), key=lambda x: -x[1]):
    print(f"  Chapter {str(ch):>5s}: {count:>6}")

# --- Court names ---
print("\n" + "=" * 60)
print("COURTS (TOP 20)")
print("=" * 60)
courts = Counter(c.get("court") for c in valid)
for court, count in courts.most_common(20):
    print(f"  {court[:60]:60s} {count:>6}")
print(f"\nTotal unique courts: {len(courts)}")

# --- Gender values ---
print("\n" + "=" * 60)
print("GENDER VALUES")
print("=" * 60)
gen = Counter(c.get("gender") for c in valid)
for g, count in gen.most_common():
    print(f"  {g!r:30s} {count:>6}")

# --- Employed values ---
print("\n" + "=" * 60)
print("EMPLOYED VALUES")
print("=" * 60)
emp = Counter()
for c in valid:
    v = c.get("employed")
    emp[repr(v)] += 1
for e, count in emp.most_common():
    print(f"  {e:30s} {count:>6}")

# --- Aggravating/mitigating factor counts ---
print("\n" + "=" * 60)
print("AGGRAVATING FACTOR COUNTS")
print("=" * 60)
agg = Counter()
for c in valid:
    af = c.get("aggravating_factors")
    if isinstance(af, list):
        agg[len(af)] += 1
    else:
        agg["not_list"] += 1
for n, count in sorted(agg.items()):
    print(f"  {str(n):>10s}: {count:>6}")

print("\nMITIGATING FACTOR COUNTS")
mit = Counter()
for c in valid:
    mf = c.get("mitigating_factors")
    if isinstance(mf, list):
        mit[len(mf)] += 1
    else:
        mit["not_list"] += 1
for n, count in sorted(mit.items()):
    print(f"  {str(n):>10s}: {count:>6}")
