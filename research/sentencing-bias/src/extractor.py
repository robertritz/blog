"""
Extract structured data from shuukh.mn case HTML.

Handles:
- Structured fields (direct parsing from metadata table)
- Semi-structured fields (regex patterns for Mongolian demographics)
- Free-text fields (Claude API for complex extraction)
"""

import re
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict, field
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


@dataclass
class CaseData:
    """Extracted case data."""
    # Identifiers
    case_id: int
    case_index: Optional[str] = None

    # Case metadata (from structured table)
    court: Optional[str] = None
    judge: Optional[str] = None
    prosecutor: Optional[str] = None
    case_date: Optional[str] = None
    case_number: Optional[str] = None
    crime_article: Optional[str] = None

    # Demographics (from bio section)
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    age: Optional[int] = None
    education: Optional[str] = None
    education_level: Optional[int] = None
    occupation: Optional[str] = None
    employed: Optional[bool] = None
    employment_detail: Optional[str] = None
    family_size: Optional[int] = None
    num_children: Optional[int] = None
    birth_place: Optional[str] = None
    residence: Optional[str] = None
    prior_criminal: Optional[bool] = None
    prior_criminal_detail: Optional[str] = None

    # Sentencing (from decision section)
    sentence_type: Optional[str] = None
    sentence_months: Optional[float] = None
    sentence_fine_mnt: Optional[float] = None
    sentence_fine_units: Optional[int] = None
    sentence_community_hours: Optional[float] = None
    sentence_suspended: Optional[bool] = None
    sentence_rights_deprived: Optional[str] = None
    sentence_raw: Optional[str] = None

    # Full text sections for LLM
    bio_text: Optional[str] = None
    sentence_text: Optional[str] = None
    full_text: Optional[str] = None

    # Metadata
    extraction_method: Optional[str] = None
    extraction_notes: Optional[str] = None


# === Mongolian patterns ===

GENDER_PATTERNS = {
    "эрэгтэй": "male",
    "эмэгтэй": "female",
}

EDUCATION_LEVELS = {
    "бага боловсролтой": ("бага", 1),
    "суурь боловсролтой": ("суурь", 2),
    "бүрэн дунд боловсролтой": ("бүрэн дунд", 3),
    "бүрэн бус дунд боловсролтой": ("бүрэн дунд", 3),  # variant
    "тусгай дунд боловсролтой": ("тусгай дунд", 4),
    "дээд боловсролтой": ("дээд", 5),
    # Shorter forms (check after longer ones)
    "бага": ("бага", 1),
    "суурь": ("суурь", 2),
    "бүрэн дунд": ("бүрэн дунд", 3),
    "тусгай дунд": ("тусгай дунд", 4),
    "дээд": ("дээд", 5),
}

EMPLOYMENT_PATTERNS = {
    # Unemployed patterns
    "ажилгүй": (False, "ажилгүй"),
    "эрхэлсэн тодорхой ажилгүй": (False, "эрхэлсэн тодорхой ажилгүй"),
    "тодорхой ажилгүй": (False, "тодорхой ажилгүй"),
    # Employed patterns
    "хувиараа хөдөлмөр эрхэлдэг": (True, "хувиараа"),
    "хувиараа": (True, "хувиараа"),
    "малчин": (True, "малчин"),
    "тэтгэвэрт": (None, "тэтгэвэрт"),  # Retired - ambiguous
    "оюутан": (None, "оюутан"),  # Student
    "суралцдаг": (None, "оюутан"),
    "албан хаагч": (True, "албан хаагч"),  # Civil servant
}


def parse_html(html: str) -> BeautifulSoup:
    """Parse HTML content."""
    return BeautifulSoup(html, "html.parser")


def extract_structured_fields(soup: BeautifulSoup, case_id: int) -> CaseData:
    """Extract directly parseable fields from the metadata table."""
    data = CaseData(case_id=case_id)

    # The metadata is in the first <table> on the page
    table = soup.find("table")
    if not table:
        return data

    # Map Mongolian labels to our fields
    label_map = {
        "Шүүх": "court",
        "Шүүгч": "judge",
        "Хэргийн индекс": "case_index",
        "Дугаар": "case_number",
        "Огноо": "case_date",
        "Зүйл хэсэг": "crime_article",
        "Улсын яллагч": "prosecutor",
    }

    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            field_name = label_map.get(label)
            if field_name and value:
                setattr(data, field_name, value)

    return data


def extract_bio_section(text: str) -> Optional[str]:
    """Extract the defendant biography section from case text."""
    # Try multiple section header patterns
    bio_patterns = [
        r"Шүүгдэгчийн биеийн байцаалт:?\s*(.*?)(?:Шүүгдэгчийн холбогдсон хэрэг|ТОДОРХОЙЛОХ|Гэм буруугийн талаар)",
        r"биеийн байцаалт:?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ)",
    ]

    for pattern in bio_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

    return None


def extract_sentence_section(text: str) -> Optional[str]:
    """Extract the sentencing decision section."""
    match = re.search(r"ТОГТООХ нь:?\s*(.*?)(?:ДАРГАЛАГЧ|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _extract_gender_from_text(bio_text: Optional[str], full_text: str) -> Optional[str]:
    """Extract gender by isolating the bio section and checking keywords.

    Multi-defendant cases can have both "эрэгтэй" and "эмэгтэй" in the bio
    section. We isolate the first defendant's paragraph and check for gender
    keywords there. Falls back to context-window search around demographic
    keywords if no bio section is found.
    """
    # Strategy 1: Find the "биеийн байцаалт" section and take the first paragraph
    bio_section = None
    for pat in [
        r"биеийн байцаалт:?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ|Гэм буруугийн)",
        r"Монгол\s*[Уу]лсын\s*иргэн[,.]?\s*(.*?)(?:овогт|/РД:|\.\.\.)",
    ]:
        m = re.search(pat, full_text, re.DOTALL)
        if m:
            bio_section = m.group(1)
            break

    if bio_section:
        # Isolate first defendant: take text up to the first "настай" + ~50 chars
        # This avoids bleeding into co-defendant descriptions
        first_age = re.search(r"\d{1,3}\s*настай", bio_section)
        if first_age:
            # Take from start up through ~100 chars past "настай" for gender keyword
            end = min(first_age.end() + 100, len(bio_section))
            first_defendant = bio_section[:end]
        else:
            # No age keyword found, use first 300 chars
            first_defendant = bio_section[:300]

        # Check male first (эрэгтэй before эмэгтэй) to avoid substring false positive
        if "эрэгтэй" in first_defendant:
            return "male"
        if "эмэгтэй" in first_defendant:
            return "female"

    # Strategy 2: Context-window search around demographic keywords
    search_text = bio_text if bio_text else full_text
    for keyword in ["настай", "боловсролтой", "мэргэжилтэй", "мэргэжилгүй"]:
        idx = search_text.find(keyword)
        if idx >= 0:
            window = search_text[max(0, idx - 200):idx + 50]
            if "эрэгтэй" in window:
                return "male"
            if "эмэгтэй" in window:
                return "female"

    return None


def extract_demographics_regex(text: str, data: CaseData) -> CaseData:
    """Extract demographics using regex patterns from the bio section."""

    # Prefer the formal bio section, but fall back to searching the full text
    # for the "Монгол Улсын иргэн" paragraph (common pattern even without formal section)
    bio = data.bio_text
    if not bio:
        # Try to find the "Монгол Улсын иргэн" paragraph
        # Use \s* between words to handle no-space text variants
        citizen_match = re.search(
            r"Монгол\s*[Уу]лсын\s*иргэн[,.]?\s*(.*?)(?:овогт|овгийн|\.\.\.|/РД:)",
            text, re.DOTALL,
        )
        if citizen_match:
            bio = "Монгол Улсын иргэн, " + citizen_match.group(1).strip()
        else:
            return data

    # Gender - use bio-section-isolation approach to handle multi-defendant cases
    data.gender = _extract_gender_from_text(bio, text)

    # Age - validate range 10-100 to exclude victim ages and parsing artifacts
    age_match = re.search(r"(\d{1,3})\s*настай", bio)
    if age_match:
        age_val = int(age_match.group(1))
        if 10 <= age_val <= 100:
            data.age = age_val

    # Birth date - Mongolian format: "YYYY оны MM дүгээр/дугаар сарын DD"
    # Note: both "дүгээр" and "дугаар" are valid Mongolian ordinal forms
    birth_patterns = [
        r"(\d{4})\s*оны\s*(\d{1,2})\s*д\S+р\s*сарын\s*(\d{1,2})",
        r"(\d{4})\.(\d{2})\.(\d{2})",
    ]
    for pattern in birth_patterns:
        match = re.search(pattern, bio)
        if match:
            y, m, d = match.group(1), match.group(2), match.group(3)
            data.birth_date = f"{y}-{int(m):02d}-{int(d):02d}"
            break

    # Birth place - look for "X хотод/аймагт төрсөн"
    place_match = re.search(
        r"((?:\S+\s+)?(?:хот|аймаг)\S*)\s*(?:д|т)\s*төрсөн", bio
    )
    if place_match:
        place = place_match.group(1).strip().rstrip(",")
        if 2 < len(place) < 100:
            data.birth_place = place

    # Education - check longer patterns first, verify short patterns are near "боловсрол"
    bio_lower = bio.lower()
    for pattern, (edu_name, edu_level) in sorted(
        EDUCATION_LEVELS.items(), key=lambda x: -len(x[0])
    ):
        idx = bio_lower.find(pattern)
        if idx >= 0:
            # Short patterns (without "боловсролтой") need proximity check
            if "боловсролтой" not in pattern:
                nearby = bio_lower[idx:idx + len(pattern) + 40]
                if "боловсрол" not in nearby:
                    continue
            data.education = edu_name
            data.education_level = edu_level
            break

    # Occupation
    occ_match = re.search(r"(\S+)\s*мэргэжилтэй", bio)
    if occ_match:
        data.occupation = occ_match.group(1).strip(",")
    elif "мэргэжилгүй" in bio:
        data.occupation = "мэргэжилгүй"

    # Employment
    for pattern, (employed, detail) in sorted(
        EMPLOYMENT_PATTERNS.items(), key=lambda x: -len(x[0])
    ):
        if pattern in bio.lower():
            data.employed = employed
            data.employment_detail = detail
            break

    # Family size
    family_match = re.search(r"ам\s*бүл\s*(\d+)", bio)
    if family_match:
        data.family_size = int(family_match.group(1))

    # Number of children
    children_match = re.search(r"(\d+)\s*хүүхд", bio)
    if children_match:
        data.num_children = int(children_match.group(1))

    # Prior criminal history
    if "урьд ял шийтгэлгүй" in bio or "ял шийтгэлгүй" in bio:
        data.prior_criminal = False
    elif re.search(r"урьд\s*-?\s*(?:Улаанбаатар|шүүхийн|хорих|торгох)", bio):
        data.prior_criminal = True
        # Try to extract detail
        prior_match = re.search(r"урьд\s*-?\s*(.*?)(?:овогт|\.\.\.)", bio, re.DOTALL)
        if prior_match:
            data.prior_criminal_detail = prior_match.group(1).strip()[:500]

    # Residence - look for "X дүүрэг/аймаг ... оршин суу"
    res_match = re.search(
        r"((?:\S+\s+)?(?:дүүрэг|аймаг)\S*\s+\S+(?:\s+\S+){0,5})\s*(?:оршин\s*суу|тоотод)", bio
    )
    if res_match:
        data.residence = res_match.group(1).strip().rstrip(",")[:200]

    return data


def extract_sentence_regex(text: str, data: CaseData) -> CaseData:
    """Extract sentencing information using regex patterns."""

    sentence = data.sentence_text or text

    # Fine in MNT (төгрөг) - multiple patterns
    fine_mnt_patterns = [
        # "N төгрөгөөр торгох"
        r"(\d[\d,.\s]*)\s*төгрөгөөр\s*(?:буюу\s*)?торгох",
        # "буюу N төгрөгөөр торгох"
        r"буюу\s*(\d[\d,.\s]*)\s*төгрөгөөр\s*торгох",
        # "буюу N,NNN төгрөгөөр"
        r"буюу\s*(\d[\d,.\s]*)\s*төгрөгөөр",
        # "N төгрөгийн торгууль"
        r"(\d[\d,.\s]*)\s*төгрөгийн\s*торгууль",
    ]
    for pattern in fine_mnt_patterns:
        match = re.search(pattern, sentence)
        if match:
            mnt_str = match.group(1).replace(",", "").replace(".", "").replace(" ", "")
            if mnt_str.isdigit():
                data.sentence_fine_mnt = float(mnt_str)
                data.sentence_type = "fine"
                break

    # Fine in units (нэгж) - multiple patterns
    fine_units_patterns = [
        # "N нэгжтэй тэнцэх"
        r"(\d[\d,\s]*)\s*нэгжтэй\s*тэнцэх",
        # Word form + "буюу N нэгж" (e.g., "дөрвөн зуун тавин нэгжтэй")
        r"нэгжтэй.*?буюу\s*(\d[\d,\s]*)\s*төгрөг",
    ]
    for pattern in fine_units_patterns:
        match = re.search(pattern, sentence)
        if match:
            units_str = match.group(1).replace(",", "").replace(" ", "")
            if units_str.isdigit():
                data.sentence_fine_units = int(units_str)
                if data.sentence_type is None:
                    data.sentence_type = "fine"
                break

    # If we found "торгох" (fine) keyword but no amount, still mark as fine
    if data.sentence_type is None and re.search(r"торгох\s*ял", sentence):
        data.sentence_type = "fine"

    # Imprisonment in months - multiple patterns
    prison_month_patterns = [
        r"(\d+)\s*(?:\([^)]*\)\s*)?\s*сар(?:ын хугацаагаар)?\s*хорих",
        r"(\d+)\s*(?:\([^)]*\)\s*)?сар\S*\s+хорих",
    ]
    for pattern in prison_month_patterns:
        match = re.search(pattern, sentence)
        if match:
            data.sentence_months = float(match.group(1))
            data.sentence_type = "imprisonment"
            break

    # Imprisonment in years
    prison_year_patterns = [
        r"(\d+)\s*(?:\([^)]*\)\s*)?\s*жил\s*(\d+)\s*(?:\([^)]*\)\s*)?\s*сар\S*\s+хорих",
        r"(\d+)\s*(?:\([^)]*\)\s*)?\s*жил(?:ийн хугацаагаар)?\s*хорих",
        r"(\d+)\s*(?:\([^)]*\)\s*)?жил\S*\s+хорих",
    ]
    for pattern in prison_year_patterns:
        match = re.search(pattern, sentence)
        if match:
            years = float(match.group(1))
            months = float(match.group(2)) if match.lastindex >= 2 else 0
            data.sentence_months = years * 12 + months
            data.sentence_type = "imprisonment"
            break

    # Community service (нийтэд тустай ажил)
    community_patterns = [
        r"(\d+)\s*(?:\([^)]*\)\s*)?цаг\S*\s+нийтэд\s*тустай",
        r"нийтэд\s*тустай\s*ажил.*?(\d+)\s*цаг",
    ]
    for pattern in community_patterns:
        match = re.search(pattern, sentence)
        if match:
            data.sentence_community_hours = float(match.group(1))
            data.sentence_type = "community_service"
            break

    # Suspended sentence (тэнссэн / хойшлуулж)
    if re.search(r"тэнсс?эн|хойшлуулж|тэнсэж", sentence):
        data.sentence_suspended = True
        if data.sentence_type == "imprisonment":
            data.sentence_type = "suspended"

    # Rights deprivation (эрхийг хасаж)
    rights_match = re.search(
        r"(\S+)\s*эрх(?:ийг|ийг нь)\s*(\d+)\s*(?:\([^)]*\)\s*)?жил.*?хас", sentence
    )
    if rights_match:
        data.sentence_rights_deprived = f"{rights_match.group(1)} эрхийг {rights_match.group(2)} жил хасах"

    # Probation (хянан харгалзах)
    if re.search(r"хянан\s*харгалзах", sentence):
        data.sentence_type = "probation"

    # Store raw sentence for verification
    if data.sentence_text:
        data.sentence_raw = data.sentence_text[:1000]

    return data


def extract_with_llm(text: str, data: CaseData) -> CaseData:
    """Use Claude API for complex free-text extraction.

    Only used when regex extraction is incomplete.
    """
    try:
        import anthropic
    except ImportError:
        data.extraction_notes = (data.extraction_notes or "") + "; anthropic not installed"
        return data

    # Only call LLM if we're missing key fields
    missing = []
    if data.gender is None:
        missing.append("gender")
    if data.sentence_type is None:
        missing.append("sentence_type")
    if data.prior_criminal is None:
        missing.append("prior_criminal")

    if not missing:
        return data

    prompt = f"""Extract the following information from this Mongolian court case decision.
Return a JSON object with these fields (use null if not found in the text):

- gender: "male" or "female" (эрэгтэй = male, эмэгтэй = female)
- age: integer
- education: string (бага, суурь, бүрэн дунд, тусгай дунд, дээд)
- employed: boolean
- occupation: string
- family_size: integer (ам бүл count)
- prior_criminal: boolean (true if prior convictions mentioned, false if "ял шийтгэлгүй")
- sentence_type: "fine", "imprisonment", "suspended", "probation", "community_service", or "other"
- sentence_months: number (imprisonment months, null if fine only)
- sentence_fine_mnt: number (fine in MNT, null if not a fine)
- sentence_fine_units: integer (fine in units/нэгж)

Court case text (truncated):
{text[:6000]}

Return only valid JSON, no explanation."""

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        result = json.loads(response.content[0].text)

        # Only fill in missing fields
        if data.gender is None and result.get("gender"):
            data.gender = result["gender"]
        if data.age is None and result.get("age"):
            data.age = result["age"]
        if data.education is None and result.get("education"):
            data.education = result["education"]
        if data.employed is None and result.get("employed") is not None:
            data.employed = result["employed"]
        if data.occupation is None and result.get("occupation"):
            data.occupation = result["occupation"]
        if data.family_size is None and result.get("family_size"):
            data.family_size = result["family_size"]
        if data.prior_criminal is None and result.get("prior_criminal") is not None:
            data.prior_criminal = result["prior_criminal"]
        if data.sentence_type is None and result.get("sentence_type"):
            data.sentence_type = result["sentence_type"]
        if data.sentence_months is None and result.get("sentence_months"):
            data.sentence_months = result["sentence_months"]
        if data.sentence_fine_mnt is None and result.get("sentence_fine_mnt"):
            data.sentence_fine_mnt = result["sentence_fine_mnt"]
        if data.sentence_fine_units is None and result.get("sentence_fine_units"):
            data.sentence_fine_units = result["sentence_fine_units"]

        data.extraction_method = (data.extraction_method or "regex") + "+llm"

    except Exception as e:
        data.extraction_notes = (data.extraction_notes or "") + f"; LLM failed: {e}"

    return data


def extract_case(source: str | dict, case_id: int, use_llm: bool = False) -> CaseData:
    """Full extraction pipeline for a single case.

    Args:
        source: Either raw HTML string (legacy) or dict with
                {"table_html": ..., "text": ...} (new JSON format)
        case_id: Numeric case identifier
        use_llm: Whether to use LLM for missing fields
    """
    if isinstance(source, dict):
        # New JSON format: table_html + text already extracted
        table_html = source.get("table_html", "")
        text = source.get("text", "")

        # Parse table HTML for structured fields
        if table_html:
            table_soup = parse_html(table_html)
            data = extract_structured_fields(table_soup, case_id)
        else:
            data = CaseData(case_id=case_id)
    else:
        # Legacy: full HTML
        soup = parse_html(source)
        data = extract_structured_fields(soup, case_id)
        text = soup.get_text()

    data.full_text = text

    bio = extract_bio_section(text)
    if bio:
        data.bio_text = bio

    sentence = extract_sentence_section(text)
    if sentence:
        data.sentence_text = sentence

    # Step 3: Regex patterns for demographics
    data = extract_demographics_regex(text, data)
    data.extraction_method = "regex"

    # Step 4: Regex patterns for sentencing
    data = extract_sentence_regex(text, data)

    # Step 5: LLM for missing fields (optional)
    if use_llm:
        data = extract_with_llm(text, data)

    return data


def process_batch(
    input_dir: Path,
    output_path: Path,
    use_llm: bool = False,
) -> list[dict]:
    """Process all cases in a directory.

    Supports both .html (legacy pilot) and .json (new stripped format) files.
    """
    results = []
    # Collect both formats, dedup by case_id (prefer .json if both exist)
    # Only include files with numeric stems (skip pilot_ids.json, extracted.json, etc.)
    json_files = {f.stem: f for f in input_dir.glob("*.json") if f.stem.isdigit()}
    html_files = {f.stem: f for f in input_dir.glob("*.html") if f.stem.isdigit()}
    # Merge: json takes precedence
    all_files = {**html_files, **json_files}
    case_files = sorted(all_files.values(), key=lambda f: int(f.stem))
    total = len(case_files)

    logger.info(f"Processing {total} cases from {input_dir} ({len(json_files)} json, {len(html_files)} html)")

    for i, case_file in enumerate(case_files):
        case_id = int(case_file.stem)

        if case_file.suffix == ".json":
            source = json.loads(case_file.read_text(encoding="utf-8"))
        else:
            source = case_file.read_text(encoding="utf-8")

        data = extract_case(source, case_id, use_llm=use_llm)

        # Don't store full text in output (too large)
        result = asdict(data)
        result.pop("full_text", None)
        result.pop("bio_text", None)
        result.pop("sentence_text", None)
        results.append(result)

        if (i + 1) % 500 == 0 or (i + 1) == total:
            logger.info(f"Extracted {i + 1}/{total} cases")

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(results)} cases to {output_path}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Run from notebook or use process_batch() directly")
