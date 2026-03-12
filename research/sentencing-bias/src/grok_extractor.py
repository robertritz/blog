"""
Grok API extraction for Mongolian court cases.

Uses xAI's Grok API with OpenAI SDK compatibility for structured output extraction.
This module is designed to fill gaps where regex extraction failed.
"""

from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional, List
from enum import Enum
import os
import time


class ExtractionQuality(str, Enum):
    """Quality assessment of extraction."""
    COMPLETE = "complete"      # All key fields extractable, high confidence
    PARTIAL = "partial"        # Some fields missing but usable
    UNRELIABLE = "unreliable"  # Too much missing/redacted, exclude from study


class CaseExtraction(BaseModel):
    """Structured extraction from Mongolian court case.

    Schema version: 2.0 (2026-02-09)
    See docs/CODEBOOK.md for full variable documentation.
    """
    # ===== DEFENDANT DEMOGRAPHICS =====
    gender: Optional[str] = Field(None, description="male or female")
    age: Optional[int] = Field(None, description="Defendant age at time of case (10-100)")
    education: Optional[str] = Field(None, description="Education level: primary, basic, secondary, vocational, higher")
    employed: Optional[bool] = Field(None, description="Whether defendant is employed")
    occupation: Optional[str] = Field(None, description="Defendant occupation/trade")
    family_size: Optional[int] = Field(None, description="Household size")
    prior_criminal: Optional[bool] = Field(None, description="Has prior criminal history")

    # ===== VICTIM CHARACTERISTICS =====
    victim_relationship: Optional[str] = Field(
        None,
        description="Relationship to defendant: family, spouse, acquaintance, colleague, stranger"
    )
    victim_minor: Optional[bool] = Field(None, description="Victim is under 18 years old")

    # ===== CRIME CHARACTERISTICS =====
    crime_amount_mnt: Optional[float] = Field(
        None,
        description="Monetary value of theft/damage in MNT (property crimes only)"
    )
    injury_severity: Optional[str] = Field(
        None,
        description="Injury level: light, moderate, serious (violent crimes only)"
    )
    intoxicated_at_crime: Optional[bool] = Field(
        None,
        description="Defendant was intoxicated during crime"
    )

    # ===== CASE PROCEDURE =====
    has_lawyer: Optional[bool] = Field(None, description="Defendant had legal representation")
    plea_agreement: Optional[bool] = Field(
        None,
        description="Case resolved via simplified/plea procedure (хялбаршуулсан журам)"
    )
    plea_guilty: Optional[bool] = Field(None, description="Defendant admitted guilt")
    restitution_paid: Optional[bool] = Field(None, description="Defendant paid compensation to victim")
    time_served_days: Optional[int] = Field(
        None,
        description="Days in pre-trial custody (цагдан хорих)"
    )

    # ===== SENTENCING FACTORS =====
    aggravating_factors: List[str] = Field(
        default_factory=list,
        description="List of aggravating circumstances cited by court"
    )
    mitigating_factors: List[str] = Field(
        default_factory=list,
        description="List of mitigating circumstances cited by court"
    )

    # ===== SENTENCE OUTCOME =====
    sentence_type: Optional[str] = Field(
        None,
        description="Primary sentence: fine, imprisonment, suspended, probation, community_service"
    )
    sentence_months: Optional[float] = Field(None, description="Imprisonment duration in months")
    sentence_suspended_months: Optional[float] = Field(
        None,
        description="Months of sentence suspended (тэнсэх). Actual = sentence_months - suspended"
    )
    sentence_fine_mnt: Optional[float] = Field(None, description="Fine amount in MNT")

    # ===== DATA QUALITY =====
    extraction_quality: ExtractionQuality = Field(
        ExtractionQuality.COMPLETE,
        description="Overall quality: complete, partial, unreliable"
    )
    quality_issues: List[str] = Field(
        default_factory=list,
        description="List of extraction issues encountered"
    )


SYSTEM_PROMPT = """Extract defendant demographics, victim info, crime details, and sentencing from this Mongolian court case.

## 1. DEFENDANT DEMOGRAPHICS (look in "биеийн байцаалт" or "Монгол Улсын иргэн" section)
- **gender**: эрэгтэй = male, эмэгтэй = female
- **age**: "N настай" where N is the age (defendant's age, NOT victim's)
- **education** (боловсрол):
  - бага = primary
  - суурь = basic
  - бүрэн бус дунд / бүрэн дунд = secondary
  - тусгай дунд = vocational
  - дээд = higher
- **employed**: ажилтай = true, ажилгүй = false
- **occupation**: мэргэжил field (e.g., жолооч, тогооч, оюутан)
- **family_size**: ам бүл N = household of N
- **prior_criminal**:
  - false: "урьд ял шийтгэлгүй", "эрүүгийн хариуцлага хүлээж байгаагүй"
  - true: explicit mention of prior court case/conviction
  - null: if not mentioned or unclear

## 2. VICTIM CHARACTERISTICS
- **victim_relationship**: Infer from context:
  - "гэр бүлийн хүчирхийлэл", "эхнэр", "нөхөр", "хүүхэд", "эгч", "ах", "дүү" = family
  - "эхнэр", "нөхөр" specifically = spouse
  - "хамтран ажилладаг", "ажлын дарга" = colleague
  - "танил" = acquaintance
  - street crime, theft from store, no relationship mentioned = stranger
- **victim_minor**: true if victim explicitly under 18 ("насанд хүрээгүй", "хүүхэд", age < 18)

## 3. CRIME CHARACTERISTICS
- **crime_amount_mnt**: For theft/property crimes, extract monetary value:
  - Look for "N төгрөгийн хохирол" (N tugrik damage)
  - Or valuation amounts in expert reports
  - null for violent crimes without property element
- **injury_severity**: For assault/violent crimes:
  - "хөнгөн хохирол" / "хөнгөн зэргийн гэмтэл" = light
  - "дунд зэргийн гэмтэл" = moderate
  - "хүндэвтэр хохирол" / "хүнд гэмтэл" = serious
  - null for non-violent crimes
- **intoxicated_at_crime**: true if defendant was drunk/high during crime:
  - "архи согтууруулах ундаа хэрэглэсэн", "согтуу үедээ", "согтууруулах ундааны..."

## 4. CASE PROCEDURE
- **has_lawyer**: true if defense lawyer mentioned ("өмгөөлөгч"), false if "өөрийгөө өмгөөлж" (self-represented)
- **plea_agreement**: true if "хялбаршуулсан журмаар" (simplified procedure)
- **plea_guilty**: true if "гэм буруугаа хүлээсэн", "хүлээн зөвшөөрсөн"
- **restitution_paid**: true if "хохирлыг нөхөн төлсөн", "хохирлоо барагдуулсан"
- **time_served_days**: Days in pre-trial custody ("цагдан хорих" section, or "N хоног цагдан хоригдсон")

## 5. SENTENCING FACTORS
- **aggravating_factors**: List factors court cited against defendant:
  - intoxicated, used violence, serious injury, child victim, accomplices, repeat offense, etc.
- **mitigating_factors**: List factors court cited in defendant's favor:
  - admitted guilt, paid restitution, first offense, has dependents, elderly, health issues, etc.

## 6. SENTENCE OUTCOME (look in ТОГТООХ section)
- **sentence_type**: Primary sentence type:
  - торгох = fine
  - хорих = imprisonment
  - тэнсэн/тэнссэн = suspended
  - нийтэд тустай ажил = community_service
  - хянан харгалзах = probation
- **sentence_months**: Total imprisonment in months (convert years: 1 жил = 12 months)
- **sentence_suspended_months**: If part suspended, how many months suspended ("N сар/жил тэнсэж")
- **sentence_fine_mnt**: Fine amount in MNT (may be stated as "N нэгж" = N × 1000 MNT)

## 7. DATA QUALITY
- **extraction_quality**:
  - "complete": All key fields extractable
  - "partial": Some gaps but usable (gender + sentence clear)
  - "unreliable": Major issues, exclude from study
- **quality_issues** (list all that apply):
  - "redacted_bio": Key info replaced with ***
  - "multiple_defendants": 2+ defendants (extracted first only)
  - "missing_bio_section": No defendant biography found
  - "missing_sentence": No ТОГТООХ section
  - "minimal_text": Very short document
  - "acquittal": Case dismissed, no sentence

Return null for fields not found. Focus on FIRST defendant if multiple mentioned."""


def extract_with_grok(
    text: str,
    model: str = "grok-4-1-fast",  # REST API model name
    timeout: float = 60.0,
) -> tuple[CaseExtraction, float]:
    """Extract case data using Grok API with structured output.

    Args:
        text: Case text to extract from
        model: Grok model to use (grok-4-1-fast or grok-4-fast)
        timeout: Request timeout in seconds

    Returns:
        Tuple of (CaseExtraction, latency_seconds)

    Raises:
        ValueError: If XAI_API_KEY environment variable is not set
        Exception: If API call fails
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable not set")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
        timeout=timeout,
    )

    start_time = time.time()

    # Use beta.chat.completions.parse() with Pydantic model for structured output
    # Grok 4.1 Fast has 2M token context - send full text, no truncation
    # Flag cases over 500K chars (~167K tokens) as too large
    if len(text) > 500000:
        raise ValueError(f"Case text too large: {len(text)} chars. Flag for manual review.")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        response_format=CaseExtraction,
    )

    latency = time.time() - start_time

    return completion.choices[0].message.parsed, latency


def test_connection() -> bool:
    """Test that the Grok API is accessible with valid credentials."""
    try:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            print("Error: XAI_API_KEY not set")
            return False

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=10.0,
        )

        # Simple test request
        response = client.chat.completions.create(
            model="grok-4-1-fast",
            messages=[{"role": "user", "content": "Hello, respond with 'OK'"}],
            max_tokens=10,
        )

        print(f"API connection successful: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection when run directly
    test_connection()
