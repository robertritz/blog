# Research Idea: Demographic Bias in Criminal Sentencing in Mongolia

## The Spark

Mongolia's court system publishes all criminal case decisions publicly on shuukh.mn. Each case includes detailed defendant demographics (age, gender, education, occupation) alongside sentencing outcomes. This creates a unique opportunity to study whether demographic factors influence sentencing independently of crime severity and circumstances.

## Research Question

Is there systematic bias in criminal sentencing in Mongolia based on defendant demographics (age, gender, education, occupation), controlling for crime type, severity, and prior criminal history?

## Why It Matters

- **Justice system accountability:** If bias exists, it undermines equal treatment under law
- **Policy implications:** Data-driven evidence for judicial training or reform
- **Comparative criminology:** First large-scale quantitative study of Mongolian sentencing
- **Transparency:** Demonstrates value of public court records

## Hypothesis

Based on criminology literature from other countries:
- Gender effect: Women may receive lighter sentences for equivalent crimes
- Education effect: Higher education may correlate with lighter sentences
- Age effect: Younger and elderly defendants may receive different treatment
- Occupation effect: Employed defendants may receive more lenient sentences

## Data

- **Source:** shuukh.mn (Supreme Court of Mongolia public database)
- **Availability:** Publicly accessible, no authentication required
- **Format:** HTML pages with structured tables + free text case descriptions
- **Approximate volume:** 200+ cases/month in criminal first instance alone; potentially thousands historically
- **Access method:** API endpoint (case_ajax) + individual case page scraping

### Variables Available
**Demographics (from Биеийн байцаалт section):**
- Birth date / age
- Gender (эмэгтэй/эрэгтэй)
- Education level (бүрэн дунд, дээд, etc.)
- Occupation/profession
- Employment status
- Family size / dependents
- Residence district
- Prior criminal history

**Case characteristics:**
- Criminal code article (crime type)
- Court and judge
- Prosecutor
- Date

**Sentencing:**
- Sentence type (fine, imprisonment, probation, etc.)
- Amount/duration
- Aggravating/mitigating factors

## Rough Methodology

1. **Data collection:** Scrape all available criminal first instance cases
2. **Feature extraction:** Parse demographics and sentencing from case text (rule-based NLP + LLM for complex fields)
3. **Descriptive analysis:** Sentencing patterns by demographic groups
4. **Regression analysis:** Model sentence severity controlling for crime type, prior offenses, court/judge effects
5. **Robustness checks:** Alternative specifications, subgroup analyses

## Potential Obstacles

- **Data quality:** Missing or inconsistent demographic information in some cases
- **Extraction accuracy:** Free-text demographics may be hard to parse reliably
- **Confounders:** Unobserved case characteristics that correlate with demographics
- **Sample selection:** Only completed cases visible; dropped/dismissed cases not included
- **Language:** All data in Mongolian requires careful NLP handling

## Related Work

- Gender disparities in sentencing (Starr 2012, "Estimating Gender Disparities in Federal Criminal Cases")
- Race and sentencing in US courts (extensive literature)
- Limited quantitative research on Mongolian justice system
- Court transparency and accountability studies

## Target Audience

- **Primary:** Academic criminology/law journals
- **Secondary:** Mongolian policy makers, judicial training institutions
- **Tertiary:** Comparative law researchers interested in Central Asia

## Notes

- shuukh.mn API requires specific headers (x-requested-with: XMLHttpRequest)
- Case IDs are numeric, accessible via `/single_case/{id}`
- Data is in Mongolian; extraction will need Mongolian NLP handling
- Ethical consideration: Data is public record, but will use aggregates only, no individual identification

---
*Created: 2026-02-03*
*Status: Brainstorm*
