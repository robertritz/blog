# Government Macro Assumptions (Extracted Snapshot)

Source output:

- `data/derived/government_macro_assumptions_2026_2028.csv`

Extractor:

- `tools/extract_government_macro_assumptions.py`

## What was extracted directly

From Lawforum attachment #4981 (`https://lawforum.parliament.mn/files/4981/?d=1`):

- Inflation (annual average, %): 2026 `7.0`, 2027 `6.4`, 2028 `6.0`
- Total exports (USD bn): 2026 `18.0`, 2027 `18.3`, 2028 `19.2`
- Total imports (USD bn): 2026 `14.2`, 2028 `16.4`
- Total imports (USD bn, inferred for the missing middle year): 2027 `15.3`
- Trade balance (average over 2026-2028, USD bn): `3.2`

From Parliament macro attachment (`https://www.parliament.mn/files/5a772a2a054f45d3bc5988e4a82accfa/?d=1`):

- USD/MNT narrative point: end-period exchange rate reaches about `4000` by the end of horizon (captured as 2028 end-period point).

## What was derived

The same Lawforum explanatory document includes TSBZ assumptions and explicit differences versus the government budget-framework assumptions.  
The extractor computes implied government assumptions for:

- Coal export price/volume
- Copper concentrate export price/volume
- Gold export price/volume
- Iron ore export price/volume

These rows are marked with:

- `extraction_method = derived_from_TSBZ_comparison_text`

## Caveats

- `total_imports` for 2027 is not explicitly present in machine-extractable text. The current CSV includes an inferred `2027 = 15.3` based on the 2026 and 2028 endpoints plus the text saying medium-term import growth averages about 8 percent.
- The USD/MNT value is from narrative text (chart commentary), not a dedicated annual table row in the extractable layer.
- Keep manual visual verification before publication if citing these as definitive policy assumptions.
