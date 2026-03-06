#!/usr/bin/env python3
"""
Extract 2026-2028 government macro assumptions from Parliament/Lawforum sources.

Outputs:
- data/derived/government_macro_assumptions_2026_2028.csv
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import re
import subprocess
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
DERIVED_DIR = ROOT / "data" / "derived"
OUTPUT_CSV = DERIVED_DIR / "government_macro_assumptions_2026_2028.csv"

LAWFORUM_4981_URL = "https://lawforum.parliament.mn/files/4981/?d=1"
PARLIAMENT_MACRO_URL = "https://www.parliament.mn/files/5a772a2a054f45d3bc5988e4a82accfa/?d=1"


@dataclass
class AssumptionRow:
    source_doc: str
    source_url: str
    source_publication_date: str
    vintage: str
    assumption_group: str
    variable: str
    year: int
    value: Optional[float]
    unit: str
    extraction_method: str
    note: str


def download_file(url: str, output_path: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Codex Research Extractor)",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response, output_path.open("wb") as out:
        out.write(response.read())


def extract_pdf_text(pdf_path: Path) -> str:
    parts: List[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            parts.append(txt)
    return "\n".join(parts)


def pdf_creation_date_iso(pdf_path: Path) -> str:
    with pdfplumber.open(str(pdf_path)) as pdf:
        raw = (pdf.metadata or {}).get("CreationDate") or ""
    # Example: D:20250430111418+08'00'
    m = re.search(r"(\d{4})(\d{2})(\d{2})", raw)
    if not m:
        return ""
    y, mo, d = map(int, m.groups())
    return dt.date(y, mo, d).isoformat()


def _to_float(x: str) -> float:
    return float(x.replace(",", "").strip())


def _search(text: str, pattern: str, flags: int = 0) -> re.Match[str]:
    m = re.search(pattern, text, flags)
    if not m:
        raise ValueError(f"Pattern not found: {pattern}")
    return m


def parse_lawforum_4981(text: str, source_date: str) -> List[AssumptionRow]:
    rows: List[AssumptionRow] = []

    inflation = _search(
        text,
        r"инфляц[^\n]*?дунджаар\s*2026 онд\s*([0-9]+(?:\.[0-9]+)?)\s*хувь,\s*2027 онд\s*([0-9]+(?:\.[0-9]+)?)\s*хувь,\s*2028 онд\s*([0-9]+(?:\.[0-9]+)?)\s*хувь",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for year, val in zip([2026, 2027, 2028], inflation.groups()):
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="headline_macro",
                variable="inflation_cpi_avg",
                year=year,
                value=_to_float(val),
                unit="percent",
                extraction_method="regex_from_pdf_text",
                note="Direct text in the explanatory document",
            )
        )

    exports = _search(
        text,
        r"Нийт экспорт 2026 онд\s*([0-9]+(?:\.[0-9]+)?)\s*тэрбум ам\.доллар,\s*2027 онд\s*([0-9]+(?:\.[0-9]+)?)\s*тэрбум ам\.доллар,\s*2028\s*онд\s*([0-9]+(?:\.[0-9]+)?)\s*тэрбум ам\.доллар",
        flags=re.DOTALL,
    )
    for year, val in zip([2026, 2027, 2028], exports.groups()):
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="external_sector",
                variable="total_exports",
                year=year,
                value=_to_float(val),
                unit="USD_billion",
                extraction_method="regex_from_pdf_text",
                note="Direct text in section 1.2.6",
            )
        )

    imports = _search(
        text,
        r"Нийт импорт 2026 онд\s*([0-9]+(?:\.[0-9]+)?)\s*тэрбум.*?2028 онд.*?([0-9]+(?:\.[0-9]+)?)\s*тэрбум ам\.долларт хүрэхээр",
        flags=re.DOTALL,
    )
    import_2026 = _to_float(imports.group(1))
    import_2028 = _to_float(imports.group(2))
    rows.append(
        AssumptionRow(
            source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
            source_url=LAWFORUM_4981_URL,
            source_publication_date=source_date,
            vintage="2026 budget framework statement",
            assumption_group="external_sector",
            variable="total_imports",
            year=2026,
            value=import_2026,
            unit="USD_billion",
            extraction_method="regex_from_pdf_text",
            note="Direct text in section 1.2.6",
        )
    )
    inferred_2027_import = round((import_2026 * import_2028) ** 0.5, 1)
    rows.append(
        AssumptionRow(
            source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
            source_url=LAWFORUM_4981_URL,
            source_publication_date=source_date,
            vintage="2026 budget framework statement",
            assumption_group="external_sector",
            variable="total_imports",
            year=2027,
            value=inferred_2027_import,
            unit="USD_billion",
            extraction_method="inferred_from_endpoints_and_avg_growth_text",
            note="Inferred from 2026=14.2, 2028=16.4, and text stating average import growth of about 8 percent in the medium term",
        )
    )
    rows.append(
        AssumptionRow(
            source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
            source_url=LAWFORUM_4981_URL,
            source_publication_date=source_date,
            vintage="2026 budget framework statement",
            assumption_group="external_sector",
            variable="total_imports",
            year=2028,
            value=import_2028,
            unit="USD_billion",
            extraction_method="regex_from_pdf_text",
            note="Direct text in section 1.2.6; 2027 not explicitly stated in extractable text",
        )
    )

    trade_balance = _search(
        text,
        r"гадаад худалдааны тэнцэл 2026-2028 онд дунджаар\s*([0-9]+(?:\.[0-9]+)?)\s*орчим тэрбум",
    )
    rows.append(
        AssumptionRow(
            source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
            source_url=LAWFORUM_4981_URL,
            source_publication_date=source_date,
            vintage="2026 budget framework statement",
            assumption_group="external_sector",
            variable="trade_balance_avg_2026_2028",
            year=2026,
            value=_to_float(trade_balance.group(1)),
            unit="USD_billion",
            extraction_method="regex_from_pdf_text",
            note="Average over 2026-2028 stated directly",
        )
    )

    # Derive government assumptions from TSBZ values + stated deviations.
    # Coal export price
    council_coal_price = _search(
        text,
        r"нүүрсний экспортын үнийг тонн тутамд 2026\s*онд\s*([0-9]+)\s*ам\.доллар,\s*2027 онд\s*([0-9]+)\s*ам\.доллар,\s*2028 онд\s*([0-9]+)\s*ам\.доллар",
        flags=re.IGNORECASE,
    )
    coal_diff = _search(
        text,
        r"2026 оны хувьд\s*([0-9]+)\s*ам\.доллароор,\s*2027 онд\s*([0-9]+)\s*ам\.доллароор,\s*2028 онд\s*([0-9]+)\s*ам\.доллароор тус тус өндөр",
    )
    for year, c_val, diff in zip([2026, 2027, 2028], council_coal_price.groups(), coal_diff.groups()):
        gov_val = _to_float(c_val) - _to_float(diff)
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="coal_export_price",
                year=year,
                value=gov_val,
                unit="USD_per_ton",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value minus stated positive gap",
            )
        )

    # Copper concentrate export price
    council_copper_price = _search(
        text,
        r"зэсийн баяжмалын үнийг тонн тутамд 2026 онд\s*([0-9,]+)\s*ам\.доллар,\s*2027 онд\s*([0-9,]+)\s*ам\.доллар,\s*2028 онд\s*([0-9,]+)\s*ам\.доллар",
    )
    copper_diff = _search(
        text,
        r"2026 оны хувьд\s*([0-9,]+)\s*ам\.доллароор,\s*2027 онд\s*([0-9,]+)\s*ам\.доллароор,\s*2028 онд\s*([0-9,]+)\s*ам\.доллароор тус тус бага",
    )
    for year, c_val, diff in zip([2026, 2027, 2028], council_copper_price.groups(), copper_diff.groups()):
        gov_val = _to_float(c_val) + _to_float(diff)
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="copper_concentrate_export_price",
                year=year,
                value=gov_val,
                unit="USD_per_ton",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value plus stated negative gap",
            )
        )

    # Gold export price
    council_gold_price = _search(
        text,
        r"Алтны үнийг унц тутамд 2026 онд\s*([0-9,]+)\s*ам\.доллар,\s*2027 онд\s*([0-9,]+)\s*ам\.доллар,\s*2028 онд\s*([0-9,]+)\s*ам\.доллар",
    )
    # There are multiple "...тус тус бага" sections; anchor by nearby text.
    # Use the last match in context that follows the gold sentence.
    gold_section = text[text.find(council_gold_price.group(0)) :]
    gold_diff2 = _search(
        gold_section,
        r"2026 оны хувьд\s*([0-9,]+)\s*ам\.доллароор,\s*2027 онд\s*([0-9,]+)\s*ам\.доллароор,\s*2028 онд\s*([0-9,]+)\s*ам\.доллароор тус тус бага",
    )
    for year, c_val, diff in zip([2026, 2027, 2028], council_gold_price.groups(), gold_diff2.groups()):
        gov_val = _to_float(c_val) + _to_float(diff)
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="gold_export_price",
                year=year,
                value=gov_val,
                unit="USD_per_troy_ounce",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value plus stated negative gap",
            )
        )

    # Iron ore export price
    council_iron_price = _search(
        text,
        r"Төмрийн хүдрийн үнийг тонн тутамд 2026 онд\s*([0-9,]+)\s*ам\.доллар,\s*2027 онд\s*([0-9,]+)\s*ам\.доллар,\s*2028 онд\s*([0-9,]+)\s*ам\.доллар",
    )
    iron_section = text[text.find(council_iron_price.group(0)) :]
    iron_diff = _search(
        iron_section,
        r"2026 оны хувьд\s*([0-9,]+)\s*ам\.доллароор,\s*2027 онд\s*([0-9,]+)\s*ам\.доллароор,\s*2028 онд\s*([0-9,]+)\s*ам\.доллароор тус тус бага",
    )
    for year, c_val, diff in zip([2026, 2027, 2028], council_iron_price.groups(), iron_diff.groups()):
        gov_val = _to_float(c_val) + _to_float(diff)
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="iron_ore_export_price",
                year=year,
                value=gov_val,
                unit="USD_per_ton",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value plus stated negative gap",
            )
        )

    # Coal export volume
    council_coal_vol = _search(
        text,
        r"нүүрсний экспортын биет хэмжээг 2026 онд\s*([0-9,]+)\s*сая тонн,\s*2027 онд\s*([0-9,]+)\s*сая тонн,\s*2028 онд\s*([0-9,]+)\s*сая тонн",
    )
    coal_section = text[text.find(council_coal_vol.group(0)) :]
    coal_2026_gap = _search(
        coal_section,
        r"2026 оны хувьд\s*([0-9,]+)\s*сая тонноор\s*бага",
    )
    coal_gov = [
        _to_float(council_coal_vol.group(1)) + _to_float(coal_2026_gap.group(1)),
        _to_float(council_coal_vol.group(2)),
        _to_float(council_coal_vol.group(3)),
    ]
    for year, gov_val in zip([2026, 2027, 2028], coal_gov):
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="coal_export_volume",
                year=year,
                value=gov_val,
                unit="million_tons",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value and stated gap (2027-2028 stated as aligned)",
            )
        )

    # Copper concentrate export volume
    council_copper_vol = _search(
        text,
        r"Зэсийн баяжмалын хувьд экспортын биет хэмжээг 2026 онд\s*([0-9,]+)\s*мянган тонн,\s*2027\s*онд\s*([0-9,]+)\s*мянган тонн,\s*2028 онд\s*([0-9,]+)\s*мянган тонн",
    )
    copper_vol_section = text[text.find(council_copper_vol.group(0)) :]
    copper_vol_diff = _search(
        copper_vol_section,
        r"2026 оны хувьд\s*([0-9,]+)\s*мянган тонн,\s*2027 оны хувьд\s*([0-9,]+)\s*мянган тонн,\s*2028 онд\s*([0-9,]+)\s*мянган тонноор тус тус их",
    )
    for year, c_val, diff in zip([2026, 2027, 2028], council_copper_vol.groups(), copper_vol_diff.groups()):
        gov_val = _to_float(c_val) - _to_float(diff)
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="copper_concentrate_export_volume",
                year=year,
                value=gov_val,
                unit="thousand_tons",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value minus stated positive gap",
            )
        )

    # Gold export volume
    council_gold_vol = _search(
        text,
        r"алтны экспортын биет хэмжээг 2026 онд\s*([0-9]+(?:\.[0-9]+)?)\s*тонн,\s*2027 онд\s*([0-9]+(?:\.[0-9]+)?)\s*тонн,\s*2028 онд\s*([0-9]+(?:\.[0-9]+)?)\s*тонн",
        flags=re.IGNORECASE,
    )
    gold_vol_section = text[text.find(council_gold_vol.group(0)) :]
    gold_vol_diff = _search(
        gold_vol_section,
        r"2026 оны хувьд\s*([0-9]+(?:\.[0-9]+)?)\s*тонн,\s*2027-2028 оны хувьд\s*([0-9]+(?:\.[0-9]+)?)\s*тонноор тус тус бага",
    )
    gold_diff_2026 = _to_float(gold_vol_diff.group(1))
    gold_diff_2728 = _to_float(gold_vol_diff.group(2))
    gold_gov = [
        _to_float(council_gold_vol.group(1)) + gold_diff_2026,
        _to_float(council_gold_vol.group(2)) + gold_diff_2728,
        _to_float(council_gold_vol.group(3)) + gold_diff_2728,
    ]
    for year, gov_val in zip([2026, 2027, 2028], gold_gov):
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="gold_export_volume",
                year=year,
                value=gov_val,
                unit="tons",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value plus stated negative gap",
            )
        )

    # Iron ore export volume
    council_iron_vol = _search(
        text,
        r"төмрийн хүдрийн экспортын биет хэмжээг 2026 онд\s*([0-9,]+)\s*мянган тонн,\s*2027 онд\s*([0-9,]+)\s*мянган тонн,\s*2028 онд\s*([0-9,]+)\s*мянган тонн",
        flags=re.IGNORECASE,
    )
    iron_vol_section = text[text.find(council_iron_vol.group(0)) :]
    iron_vol_diff = _search(
        iron_vol_section,
        r"2026 оны хувьд\s*([0-9,]+)\s*мянган тонн,\s*2027 оны хувьд\s*([0-9,]+)\s*мянган тонн,\s*2028 онд\s*([0-9,]+)\s*мянган тонноор тус тус бага",
    )
    for year, c_val, diff in zip([2026, 2027, 2028], council_iron_vol.groups(), iron_vol_diff.groups()):
        gov_val = _to_float(c_val) + _to_float(diff)
        rows.append(
            AssumptionRow(
                source_doc="Lawforum attachment #4981 (Detailed explanatory note)",
                source_url=LAWFORUM_4981_URL,
                source_publication_date=source_date,
                vintage="2026 budget framework statement",
                assumption_group="commodity_assumptions",
                variable="iron_ore_export_volume",
                year=year,
                value=gov_val,
                unit="thousand_tons",
                extraction_method="derived_from_TSBZ_comparison_text",
                note="Derived from council value plus stated negative gap",
            )
        )

    return rows


def parse_parliament_macro_for_fx(text: str, source_date: str) -> List[AssumptionRow]:
    rows: List[AssumptionRow] = []
    m = re.search(r"4000 төгрөгт хүрэхээр", text)
    if m:
        rows.append(
            AssumptionRow(
                source_doc="Parliament attachment (Fiscal Stability Council macro report)",
                source_url=PARLIAMENT_MACRO_URL,
                source_publication_date=source_date,
                vintage="2026-2028 macro package",
                assumption_group="fx_path",
                variable="usd_mnt_end_period",
                year=2028,
                value=4000.0,
                unit="MNT_per_USD",
                extraction_method="regex_from_pdftotext_output",
                note="Narrative sentence says end-period exchange rate reaches 4000 by the end of horizon",
            )
        )
    return rows


def run_pdftotext(pdf_path: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        out = Path(tmp.name)
    try:
        subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), str(out)],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.read_text(encoding="utf-8", errors="ignore")
    finally:
        out.unlink(missing_ok=True)


def write_csv(rows: List[AssumptionRow], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_doc",
        "source_url",
        "source_publication_date",
        "vintage",
        "assumption_group",
        "variable",
        "year",
        "value",
        "unit",
        "extraction_method",
        "note",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r.variable, r.year, r.source_url)):
            writer.writerow(
                {
                    "source_doc": row.source_doc,
                    "source_url": row.source_url,
                    "source_publication_date": row.source_publication_date,
                    "vintage": row.vintage,
                    "assumption_group": row.assumption_group,
                    "variable": row.variable,
                    "year": row.year,
                    "value": "" if row.value is None else row.value,
                    "unit": row.unit,
                    "extraction_method": row.extraction_method,
                    "note": row.note,
                }
            )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        law_pdf = tmp / "lawforum_4981.pdf"
        parliament_pdf = tmp / "parliament_macro.pdf"

        download_file(LAWFORUM_4981_URL, law_pdf)
        law_text = extract_pdf_text(law_pdf)
        law_date = pdf_creation_date_iso(law_pdf)
        rows = parse_lawforum_4981(law_text, law_date)

        # Optional extra FX point from the macro attachment.
        try:
            download_file(PARLIAMENT_MACRO_URL, parliament_pdf)
            parliament_text = run_pdftotext(parliament_pdf)
            parliament_date = pdf_creation_date_iso(parliament_pdf)
            rows.extend(parse_parliament_macro_for_fx(parliament_text, parliament_date))
        except Exception as exc:  # noqa: BLE001
            rows.append(
                AssumptionRow(
                    source_doc="Parliament attachment (Fiscal Stability Council macro report)",
                    source_url=PARLIAMENT_MACRO_URL,
                    source_publication_date="",
                    vintage="2026-2028 macro package",
                    assumption_group="fx_path",
                    variable="usd_mnt_end_period",
                    year=2028,
                    value=None,
                    unit="MNT_per_USD",
                    extraction_method="not_extracted",
                    note=f"Could not parse FX path from attachment automatically: {exc}",
                )
            )

    write_csv(rows, OUTPUT_CSV)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
