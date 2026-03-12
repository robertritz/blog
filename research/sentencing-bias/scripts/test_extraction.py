#!/usr/bin/env python3
"""
Quick test script for iterating on LLM extraction prompts.

Usage:
    # Test a single case with current approach
    python scripts/test_extraction.py 117098

    # Test with new section-based approach
    python scripts/test_extraction.py 117098 --sections

    # Compare approaches
    python scripts/test_extraction.py 117098 --compare
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional


class CaseExtraction(BaseModel):
    """Structured extraction from Mongolian court case."""
    gender: Optional[str] = Field(None, description="male or female")
    age: Optional[int] = Field(None, description="Defendant age (10-100)")
    education: Optional[str] = Field(None, description="бага, суурь, бүрэн дунд, тусгай дунд, дээд")
    prior_criminal: Optional[bool] = Field(None, description="Has prior criminal record")
    sentence_type: Optional[str] = Field(None, description="fine, imprisonment, suspended, probation, community_service")
    sentence_fine_mnt: Optional[float] = Field(None, description="Fine amount in MNT")


# Original prompt
PROMPT_V1 = """Extract defendant demographics and sentencing information from this Mongolian court case.

Key Mongolian terms:
- Gender: эрэгтэй = male, эмэгтэй = female
- Age: N настай = N years old
- Education: боловсрол (бага=primary, суурь=basic, бүрэн дунд=secondary, тусгай дунд=vocational, дээд=higher)
- Prior record: урьд ял шийтгэлгүй = no prior, урьд ял = has prior
- Sentence: ТОГТООХ section contains verdict
  - торгох = fine (amount in төгрөг)
  - хорих = imprisonment
  - тэнсэн = suspended

Return null for any field not found in the text. Focus on the first defendant if multiple are mentioned."""


# Improved prompt with explicit patterns
PROMPT_V2 = """Extract defendant demographics and sentencing from this Mongolian court case.

## DEMOGRAPHICS (look in defendant biography section)
- Gender: эрэгтэй = male, эмэгтэй = female
- Age: Look for "N настай" where N is the age
- Education levels (боловсрол):
  - бага = primary
  - суурь = basic
  - бүрэн бус дунд = incomplete secondary
  - бүрэн дунд = secondary
  - тусгай дунд = vocational
  - дээд = higher

## PRIOR CRIMINAL RECORD (урьд ял)
CRITICAL: Only look for explicit statements about prior record.
- NO PRIOR: "урьд ял шийтгэлгүй", "ял шийтгүүлж байгаагүй", "эрүүгийн хариуцлага хүлээж байгаагүй"
- HAS PRIOR: Explicit mention of prior court date/case number (e.g., "урьд 2019 оны ... шүүхийн ... тогтоолоор")
- If unclear or not mentioned, return null

## SENTENCE (look in ТОГТООХ section)
- торгох = fine (look for "N төгрөгөөр торгох")
- хорих = imprisonment
- тэнсэн/тэнссэн = suspended
- нийтэд тустай ажил = community_service

Return null for fields not explicitly found. Do not infer."""


def extract_bio_section(text: str) -> Optional[str]:
    """Extract defendant biography section."""
    patterns = [
        r"биеийн байцаалт:?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ|Гэм буруугийн)",
        r"Монгол\s*[Уу]лсын\s*иргэн[,.]?\s*(.*?)(?:холбогдсон хэрэг|ТОДОРХОЙЛОХ|гэмт хэрэг)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()[:2000]

    # Fallback: find paragraph with "настай"
    age_match = re.search(r'.{0,500}\d{1,2}\s*настай.{0,300}', text)
    if age_match:
        return age_match.group(0)

    return None


def extract_sentence_section(text: str) -> Optional[str]:
    """Extract sentencing decision section."""
    match = re.search(r"ТОГТООХ\s*(?:нь)?:?\s*(.*?)(?:ДАРГАЛАГЧ|Шүүгч|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()[:2000]
    return None


def build_llm_input_v1(text: str) -> str:
    """Original: naive truncation."""
    return text[:8000]


def build_llm_input_v2(text: str) -> str:
    """Improved: section-based extraction."""
    bio = extract_bio_section(text)
    sentence = extract_sentence_section(text)

    parts = []
    if bio:
        parts.append(f"=== DEFENDANT BIOGRAPHY ===\n{bio}")
    if sentence:
        parts.append(f"=== COURT VERDICT ===\n{sentence}")

    if not parts:
        # Fallback to truncation if sections not found
        return text[:8000]

    return "\n\n".join(parts)


def call_grok(prompt: str, user_content: str, model: str = "grok-4-1-fast") -> CaseExtraction:
    """Call Grok API with structured output."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        # Try to decrypt from perspective
        import subprocess
        try:
            result = subprocess.run(
                ["age", "-d", "-i", os.path.expanduser("~/.age/key.txt"),
                 os.path.expanduser("~/projects/perspective/.xai-api-key.age")],
                capture_output=True, text=True, check=True
            )
            api_key = result.stdout.strip()
        except:
            raise ValueError("XAI_API_KEY not set and could not decrypt")

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1", timeout=60.0)

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ],
        response_format=CaseExtraction,
    )

    return completion.choices[0].message.parsed


def load_case(case_id: int) -> dict:
    """Load raw case data."""
    path = Path(f"data/raw/{case_id}.json")
    if not path.exists():
        raise FileNotFoundError(f"Case {case_id} not found")
    return json.loads(path.read_text())


def load_pilot_result(case_id: int) -> Optional[dict]:
    """Load pilot result for comparison."""
    path = Path("data/pilot/llm_pilot_results.json")
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    for r in data["results"]:
        if r["case_id"] == case_id:
            return r
    return None


def show_case_info(case_id: int, text: str):
    """Show case structure info."""
    print(f"\n{'='*60}")
    print(f"CASE {case_id}")
    print(f"{'='*60}")
    print(f"Total length: {len(text):,} chars")

    bio_idx = text.find("биеийн байцаалт")
    togtooh_idx = text.find("ТОГТООХ")

    print(f"\nSection positions:")
    print(f"  биеийн байцаалт: {bio_idx if bio_idx >= 0 else 'NOT FOUND'}")
    print(f"  ТОГТООХ: {togtooh_idx if togtooh_idx >= 0 else 'NOT FOUND'}")

    if togtooh_idx > 8000:
        print(f"  ⚠️  ТОГТООХ is BEYOND 8000 char truncation!")


def main():
    parser = argparse.ArgumentParser(description="Test LLM extraction on a single case")
    parser.add_argument("case_id", type=int, help="Case ID to test")
    parser.add_argument("--sections", action="store_true", help="Use section-based input (v2)")
    parser.add_argument("--compare", action="store_true", help="Compare v1 vs v2")
    parser.add_argument("--model", default="grok-4-1-fast", help="Model to use")
    parser.add_argument("--show-input", action="store_true", help="Show LLM input text")
    args = parser.parse_args()

    # Load case
    case_data = load_case(args.case_id)
    text = case_data.get("text", "")

    show_case_info(args.case_id, text)

    # Load previous result if available
    pilot_result = load_pilot_result(args.case_id)
    if pilot_result:
        print(f"\n--- Previous Pilot Result ---")
        for field in ["gender", "age", "education", "prior_criminal", "sentence_type", "sentence_fine_mnt"]:
            llm_val = pilot_result.get(f"llm_{field}")
            regex_val = pilot_result.get(f"regex_{field}")
            print(f"  {field}: LLM={llm_val}, regex={regex_val}")

    if args.compare:
        print(f"\n{'='*60}")
        print("COMPARING V1 (truncation) vs V2 (sections)")
        print(f"{'='*60}")

        # V1: Original
        input_v1 = build_llm_input_v1(text)
        print(f"\nV1 input length: {len(input_v1)} chars")
        result_v1 = call_grok(PROMPT_V1, input_v1, args.model)
        print(f"V1 result: {result_v1}")

        # V2: Sections
        input_v2 = build_llm_input_v2(text)
        print(f"\nV2 input length: {len(input_v2)} chars")
        if args.show_input:
            print(f"V2 input:\n{input_v2[:2000]}...")
        result_v2 = call_grok(PROMPT_V2, input_v2, args.model)
        print(f"V2 result: {result_v2}")

        # Compare
        print(f"\n--- Comparison ---")
        for field in ["gender", "age", "education", "prior_criminal", "sentence_type", "sentence_fine_mnt"]:
            v1_val = getattr(result_v1, field)
            v2_val = getattr(result_v2, field)
            match = "✓" if v1_val == v2_val else "≠"
            print(f"  {field}: v1={v1_val}, v2={v2_val} {match}")

    else:
        # Single run
        if args.sections:
            llm_input = build_llm_input_v2(text)
            prompt = PROMPT_V2
            version = "V2 (sections)"
        else:
            llm_input = build_llm_input_v1(text)
            prompt = PROMPT_V1
            version = "V1 (truncation)"

        print(f"\n--- Running {version} ---")
        print(f"Input length: {len(llm_input)} chars")

        if args.show_input:
            print(f"\nLLM Input:\n{llm_input[:3000]}...")

        result = call_grok(prompt, llm_input, args.model)
        print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
