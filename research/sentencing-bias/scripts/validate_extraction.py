"""
Validation script for automated data extraction pipeline.

Independently extracts key fields from raw HTML files using BeautifulSoup + regex,
then compares against the automated extraction in extracted.json.

Usage:
    python scripts/validate_extraction.py

Output:
    data/pilot/validation_results.json
    Per-field accuracy summary printed to stdout
"""

import json
import os
import re
import random
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

# Paths
BASE_DIR = Path("/home/ritz/projects/research/sentencing-bias")
EXTRACTED_JSON = BASE_DIR / "data" / "pilot" / "extracted.json"
HTML_DIR = BASE_DIR / "data" / "pilot"
OUTPUT_JSON = BASE_DIR / "data" / "pilot" / "validation_results.json"

SEED = 42
SAMPLE_SIZE = 200


def load_extracted_data():
    """Load the automated extraction results."""
    with open(EXTRACTED_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def get_html_text(case_id):
    """Read HTML file and return plain text via BeautifulSoup."""
    html_path = HTML_DIR / f"{case_id}.html"
    if not html_path.exists():
        return None
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator=" ")


def extract_gender(text):
    """
    Extract gender by searching for 'эрэгтэй' or 'эмэгтэй' in the bio section.
    We look specifically in the biographical context (near 'настай' or 'боловсролтой')
    to avoid false positives from witness descriptions.
    """
    if not text:
        return None

    # Try to find bio section first
    bio_section = None
    bio_patterns = [
        r"биеийн байцаалт:?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ|Гэм буруугийн)",
        r"Монгол\s*[Уу]лсын\s*иргэн[,.]?\s*(.*?)(?:овогт|/РД:|\.\.\.)",
    ]
    for pat in bio_patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            bio_section = m.group(1)
            break

    search_text = bio_section if bio_section else text

    # If we have a bio section, simple keyword search works
    if bio_section:
        if "эрэгтэй" in search_text:
            return "male"
        if "эмэгтэй" in search_text:
            return "female"
        return None

    # Without a bio section, look for gender near age/education keywords
    # to avoid matching witness descriptions
    for keyword in ["настай", "боловсролтой", "мэргэжилтэй", "мэргэжилгүй"]:
        idx = text.find(keyword)
        if idx >= 0:
            # Search within 200 chars before the keyword
            window = text[max(0, idx - 200):idx + 50]
            if "эрэгтэй" in window:
                return "male"
            if "эмэгтэй" in window:
                return "female"

    return None


def extract_age(text):
    """
    Extract age by searching for 'N настай' pattern.
    Focus on the bio section to avoid matching victim ages.
    """
    if not text:
        return None

    # Try bio section first
    bio_section = None
    bio_patterns = [
        r"биеийн байцаалт:?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ|Гэм буруугийн)",
        r"Монгол\s*[Уу]лсын\s*иргэн[,.]?\s*(.*?)(?:овогт|/РД:|\.\.\.)",
    ]
    for pat in bio_patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            bio_section = m.group(1)
            break

    search_text = bio_section if bio_section else text

    # Look for "N настай" pattern
    if bio_section:
        match = re.search(r"(\d{1,3})\s*настай", search_text)
        if match:
            age = int(match.group(1))
            if 10 <= age <= 100:
                return age
        return None

    # Without bio section, find the first "N настай" near bio keywords
    # This is the defendant's age (first occurrence in typical bio paragraph)
    matches = list(re.finditer(r"(\d{1,3})\s*настай", text))
    if matches:
        # Use the first match, which is typically in the bio section
        age = int(matches[0].group(1))
        if 10 <= age <= 100:
            return age

    return None


def extract_education(text):
    """
    Extract education level by searching for 'боловсролтой' keywords.
    Returns the education level string matching the automated extraction categories.
    """
    if not text:
        return None

    # Try bio section first
    bio_section = None
    bio_patterns = [
        r"биеийн байцаалт:?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ|Гэм буруугийн)",
        r"Монгол\s*[Уу]лсын\s*иргэн[,.]?\s*(.*?)(?:овогт|/РД:|\.\.\.)",
    ]
    for pat in bio_patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            bio_section = m.group(1)
            break

    search_text = (bio_section if bio_section else text).lower()

    # Check from longest to shortest pattern to get the most specific match
    education_map = [
        ("бүрэн дунд боловсролтой", "бүрэн дунд"),
        ("бүрэн бус дунд боловсролтой", "бүрэн дунд"),  # variant
        ("тусгай дунд боловсролтой", "тусгай дунд"),
        ("дээд боловсролтой", "дээд"),
        ("суурь боловсролтой", "суурь"),
        ("бага боловсролтой", "бага"),
        # Shorter forms (without боловсролтой suffix but near context)
        ("бүрэн дунд", "бүрэн дунд"),
        ("тусгай дунд", "тусгай дунд"),
        ("дээд", "дээд"),
        ("суурь", "суурь"),
        ("бага", "бага"),
    ]

    for pattern, label in education_map:
        if pattern in search_text:
            # For short patterns, verify they're near 'боловсрол' to avoid false matches
            if "боловсролтой" not in pattern:
                idx = search_text.find(pattern)
                # Check if 'боловсрол' is within 30 chars after the pattern
                nearby = search_text[idx:idx + len(pattern) + 40]
                if "боловсрол" not in nearby:
                    continue
            return label

    return None


def extract_sentence_type(text):
    """
    Extract sentence type from the sentencing section.
    Look for ТОГТООХ section first, then fall back to full text.

    Categories:
    - 'fine' if 'торгох ял' found
    - 'imprisonment' if 'хорих ял' found (not just 'хорих ялаар солих')
    - 'community_service' if 'нийтэд тустай' found
    - 'suspended' if imprisonment + 'тэнссэн/тэнсэн/тэнсэж/хойшлуулж' found
    """
    if not text:
        return None

    # Try to find sentencing section
    sentence_section = None
    m = re.search(r"ТОГТООХ нь:?\s*(.*?)(?:ДАРГАЛАГЧ|$)", text, re.DOTALL)
    if m:
        sentence_section = m.group(1)

    search_text = sentence_section if sentence_section else text

    # Check for community service first (most specific)
    if re.search(r"нийтэд\s*тустай\s*ажил", search_text):
        return "community_service"

    # Check for imprisonment
    has_imprisonment = False
    imprisonment_patterns = [
        r"\d+\s*(?:\([^)]*\)\s*)?сар\S*\s+хорих\s*ял",
        r"\d+\s*(?:\([^)]*\)\s*)?жил\S*\s+хорих\s*ял",
        r"хугацаагаар\s*хорих",
        r"хорих\s*ял\s*(?:оногдуулж|шийтгэ)",
        # Also catch "N сарын хугацаагаар хорих"
        r"\d+\s*сар(?:ын)?\s*(?:хугацаагаар\s*)?хорих",
        r"\d+\s*жил(?:ийн)?\s*(?:хугацаагаар\s*)?хорих",
    ]
    for pat in imprisonment_patterns:
        if re.search(pat, search_text):
            has_imprisonment = True
            break

    # Check for suspended sentence (тэнссэн/тэнсэн/тэнсэж/хойшлуулж)
    has_suspended = bool(re.search(r"тэнсс?эн|хойшлуулж|тэнсэж", search_text))

    if has_imprisonment and has_suspended:
        return "suspended"

    if has_imprisonment:
        # Make sure it's not just "торгох ялаар ... хорих ялаар солих" (conversion warning)
        # Check if there's a fine sentence as the primary
        if re.search(r"торгох\s*ял\s*(?:шийтг|оногдуул)", search_text):
            # Primary sentence is fine, "хорих" is just the conversion warning
            # But only if imprisonment wasn't independently assigned
            fine_pos = None
            imp_pos = None
            fine_m = re.search(r"торгох\s*ял", search_text)
            imp_m = re.search(r"хорих\s*ял", search_text)
            if fine_m:
                fine_pos = fine_m.start()
            if imp_m:
                imp_pos = imp_m.start()
            if fine_pos is not None and (imp_pos is None or fine_pos < imp_pos):
                # Check if "хорих ялаар солих" is the context
                for imp_match in re.finditer(r"хорих\s*ял", search_text):
                    nearby_after = search_text[imp_match.start():imp_match.start() + 60]
                    if "солих" not in nearby_after:
                        return "imprisonment"
                return "fine"
        return "imprisonment"

    # Check for fine
    if re.search(r"торгох\s*ял", search_text):
        return "fine"
    if re.search(r"төгрөгөөр\s*(?:буюу\s*)?торгох", search_text):
        return "fine"
    if re.search(r"нэгжтэй\s*тэнцэх.*торгох", search_text, re.DOTALL):
        return "fine"

    return None


def extract_sentence_fine_mnt(text):
    """
    Extract fine amount in MNT by looking for digit patterns near 'төгрөг'.

    Common patterns:
    - "N,NNN,NNN төгрөгөөр торгох"
    - "буюу N төгрөгөөр торгох"
    - "N төгрөгийн торгууль"
    """
    if not text:
        return None

    # Try to find sentencing section
    sentence_section = None
    m = re.search(r"ТОГТООХ нь:?\s*(.*?)(?:ДАРГАЛАГЧ|$)", text, re.DOTALL)
    if m:
        sentence_section = m.group(1)

    search_text = sentence_section if sentence_section else text

    # Patterns for fine amounts in MNT
    fine_patterns = [
        # "N төгрөгөөр торгох"
        r"(\d[\d,.\s]*)\s*төгрөгөөр\s*(?:буюу\s*)?торгох",
        # "буюу N төгрөгөөр торгох"
        r"буюу\s*(\d[\d,.\s]*)\s*төгрөгөөр\s*торгох",
        # "буюу N төгрөгөөр" (general)
        r"буюу\s*(\d[\d,.\s]*)\s*төгрөгөөр",
        # "N төгрөгийн торгууль"
        r"(\d[\d,.\s]*)\s*төгрөгийн\s*торгууль",
    ]

    for pattern in fine_patterns:
        match = re.search(pattern, search_text)
        if match:
            mnt_str = match.group(1).replace(",", "").replace(".", "").replace(" ", "")
            if mnt_str.isdigit():
                val = float(mnt_str)
                # Sanity check: fines are typically 100,000 - 50,000,000 MNT
                if 1000 <= val <= 100_000_000:
                    return val

    return None


def compare_field(auto_val, manual_val):
    """
    Compare two extracted values.
    Returns: 'match', 'mismatch', 'both_null', 'auto_only', 'manual_only'
    """
    auto_none = auto_val is None
    manual_none = manual_val is None

    if auto_none and manual_none:
        return "both_null"
    if auto_none and not manual_none:
        return "manual_only"
    if not auto_none and manual_none:
        return "auto_only"

    # Both have values -- compare
    # For numeric fields, allow small tolerance
    if isinstance(auto_val, (int, float)) and isinstance(manual_val, (int, float)):
        if abs(auto_val - manual_val) < 0.01:
            return "match"
        return "mismatch"

    # String comparison (case-insensitive)
    if str(auto_val).strip().lower() == str(manual_val).strip().lower():
        return "match"
    return "mismatch"


def main():
    print("=" * 70)
    print("VALIDATION: Automated Data Extraction Pipeline")
    print("=" * 70)

    # Load automated extraction
    data = load_extracted_data()
    print(f"Loaded {len(data)} cases from extracted.json")

    # Filter to cases with at least gender OR sentence_type extracted
    eligible = [
        c for c in data
        if c.get("gender") is not None or c.get("sentence_type") is not None
    ]
    print(f"Eligible cases (gender OR sentence_type not null): {len(eligible)}")

    # Random sample
    random.seed(SEED)
    sample = random.sample(eligible, min(SAMPLE_SIZE, len(eligible)))
    print(f"Sampled {len(sample)} cases (seed={SEED})")

    # Track per-field results
    fields = ["gender", "age", "education", "sentence_type", "sentence_fine_mnt"]
    field_results = {f: defaultdict(int) for f in fields}
    case_details = []

    # Process each case
    for i, case in enumerate(sample):
        case_id = case["case_id"]
        text = get_html_text(case_id)

        if text is None:
            print(f"  WARNING: HTML file not found for case_id={case_id}")
            continue

        # Independent extraction
        manual = {
            "gender": extract_gender(text),
            "age": extract_age(text),
            "education": extract_education(text),
            "sentence_type": extract_sentence_type(text),
            "sentence_fine_mnt": extract_sentence_fine_mnt(text),
        }

        # Compare each field
        case_result = {
            "case_id": case_id,
            "fields": {},
        }

        for field in fields:
            auto_val = case.get(field)
            manual_val = manual[field]
            result = compare_field(auto_val, manual_val)
            field_results[field][result] += 1
            case_result["fields"][field] = {
                "auto": auto_val,
                "manual": manual_val,
                "result": result,
            }

        case_details.append(case_result)

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(sample)} cases...")

    print(f"\nProcessed all {len(sample)} cases.")

    # Calculate per-field accuracy
    # Accuracy = matches / (total cases where field was found by EITHER method)
    # i.e., we exclude "both_null" from the denominator
    summary = {}
    print("\n" + "=" * 70)
    print(f"{'FIELD':<22} {'MATCH':>6} {'MISMATCH':>9} {'AUTO_ONLY':>10} {'MAN_ONLY':>10} {'BOTH_NULL':>10} {'ACCURACY':>10}")
    print("-" * 70)

    for field in fields:
        counts = field_results[field]
        matches = counts["match"]
        mismatches = counts["mismatch"]
        auto_only = counts["auto_only"]
        manual_only = counts["manual_only"]
        both_null = counts["both_null"]

        # Denominator: cases where at least one method found a value
        denominator = matches + mismatches + auto_only + manual_only
        accuracy = matches / denominator if denominator > 0 else None

        accuracy_str = f"{accuracy:.1%}" if accuracy is not None else "N/A"

        print(
            f"{field:<22} {matches:>6} {mismatches:>9} {auto_only:>10} "
            f"{manual_only:>10} {both_null:>10} {accuracy_str:>10}"
        )

        summary[field] = {
            "match": matches,
            "mismatch": mismatches,
            "auto_only": auto_only,
            "manual_only": manual_only,
            "both_null": both_null,
            "denominator": denominator,
            "accuracy": round(accuracy, 4) if accuracy is not None else None,
        }

    print("=" * 70)

    # List mismatches for investigation
    mismatch_details = []
    for case_result in case_details:
        for field in fields:
            fr = case_result["fields"][field]
            if fr["result"] == "mismatch":
                mismatch_details.append({
                    "case_id": case_result["case_id"],
                    "field": field,
                    "auto": fr["auto"],
                    "manual": fr["manual"],
                })

    if mismatch_details:
        print(f"\nMISMATCHES ({len(mismatch_details)} total):")
        print("-" * 70)
        for md in mismatch_details:
            print(
                f"  case_id={md['case_id']:<8} field={md['field']:<22} "
                f"auto={md['auto']!r:<20} manual={md['manual']!r}"
            )

    # Also show auto_only and manual_only for understanding extraction gaps
    auto_only_details = []
    manual_only_details = []
    for case_result in case_details:
        for field in fields:
            fr = case_result["fields"][field]
            if fr["result"] == "auto_only":
                auto_only_details.append({
                    "case_id": case_result["case_id"],
                    "field": field,
                    "auto": fr["auto"],
                })
            elif fr["result"] == "manual_only":
                manual_only_details.append({
                    "case_id": case_result["case_id"],
                    "field": field,
                    "manual": fr["manual"],
                })

    if auto_only_details:
        print(f"\nAUTO-ONLY ({len(auto_only_details)} total - automated found value, validator did not):")
        print("-" * 70)
        for d in auto_only_details[:20]:  # limit output
            print(f"  case_id={d['case_id']:<8} field={d['field']:<22} auto={d['auto']!r}")
        if len(auto_only_details) > 20:
            print(f"  ... and {len(auto_only_details) - 20} more")

    if manual_only_details:
        print(f"\nMANUAL-ONLY ({len(manual_only_details)} total - validator found value, automated did not):")
        print("-" * 70)
        for d in manual_only_details[:20]:  # limit output
            print(f"  case_id={d['case_id']:<8} field={d['field']:<22} manual={d['manual']!r}")
        if len(manual_only_details) > 20:
            print(f"  ... and {len(manual_only_details) - 20} more")

    # Save results
    output = {
        "metadata": {
            "seed": SEED,
            "sample_size": len(sample),
            "total_cases": len(data),
            "eligible_cases": len(eligible),
            "fields_validated": fields,
        },
        "summary": summary,
        "mismatches": mismatch_details,
        "auto_only": auto_only_details,
        "manual_only": manual_only_details,
        "case_details": case_details,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
