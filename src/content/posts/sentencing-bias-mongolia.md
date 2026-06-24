---
title: "Are Mongolian Courts Biased? 75,000 Criminal Cases Say Mostly No"
description: "I analyzed every criminal court decision on Mongolia's judicial database. Employment status, not gender, is the biggest demographic predictor of sentence severity."
pubDate: 2026-03-12
heroImage: "/images/sentencing-bias/employment_gap.png"
tags: ["Mongolia", "data", "courts", "criminal justice"]
author: "Robert Ritz"
---

#### But your employment status still matters more than it should.

International criminology research has consistently found that demographics influence criminal sentencing. In the United States, Sonja Starr's 2012 study found that men receive 63% longer federal sentences than women, even after controlling for the offense. Studies from Russia, Poland, and elsewhere have documented similar patterns with gender, education, and socioeconomic status. The general finding across countries: who you are affects how you're sentenced, even when it shouldn't.

Mongolia publishes all of its court decisions online at [shuukh.mn](https://shuukh.mn), a public database maintained by the judiciary. Every criminal case, with the full text of the decision, is there for anyone to read. I've lived in Mongolia since 2012 and have spent a lot of time digging into Mongolian data for this blog. So I wanted to test a simple question: does the same pattern of demographic bias show up in Mongolian criminal courts?

I collected and analyzed 75,323 decisions from Mongolia's Criminal Court of First Instance, covering 2020 to early 2026. Let's take a look at what the data says.

## What's in the data

Each case on shuukh.mn is a full court decision written in Mongolian. [Here's an example](https://shuukh.mn/single_case/104176?daterange=2026/01/01%20-%202026/03/12%20&id=1&court_cat=2&bb=1): a 41-year-old male herder from Tuv Province, primary education, family of 5, no prior record. He stole 700,000 MNT (about $200 USD) from an acquaintance, pled guilty, paid restitution, and was fined 500,000 MNT.

That single decision contains most of the variables I extracted: demographics (gender, age, education, employment status), the crime (Criminal Code article, category), and the outcome (sentence type, amount, aggravating and mitigating factors). Not every decision has every field. Age, for example, is missing from 42.7% of cases. But across 75,323 decisions, the coverage is good enough to work with.

Here are a few more cases to give you a sense of the range:

- [Case 84144](https://shuukh.mn/single_case/84144?daterange=2026/01/01%20-%202026/03/12%20&id=1&court_cat=2&bb=1): A 39-year-old employed woman in Nalaikh (Ulaanbaatar), secondary education, convicted of seriously injuring her spouse with a knife while intoxicated. 3 aggravating factors, 5 mitigating factors. Sentenced to 41 months imprisonment.
- [Case 44606](https://shuukh.mn/single_case/44606?daterange=2026/01/01%20-%202026/03/12%20&id=1&court_cat=2&bb=1): A 24-year-old self-employed man in Khan-Uul district, secondary education, convicted of a traffic offense that caused serious injury. No aggravating factors, 4 mitigating. Given a 12-month suspended sentence.

The defendants are overwhelmingly male (86%), with a median age of 34. Most have a secondary education.

## What Mongolian criminal justice looks like

The picture is pretty different from what you'd see in the U.S. or Europe.

![Sentence type distribution](/images/sentencing-bias/sentence_types.png)

Fines are the dominant outcome. Out of 75,323 cases, 42,517 (56%) resulted in a fine. Imprisonment is a distant second at 11,859 cases (16%), followed by community service, suspended sentences, and probation. Mongolian courts are not sending most convicted defendants to prison.

![Crime type distribution](/images/sentencing-bias/crime_types.png)

Over half of all cases (53%) involve violent crime, which under Mongolia's Criminal Code covers chapters 10 through 13 (assault, domestic violence, robbery, etc.). Property crime is the next largest category at 25%, followed by traffic offenses at 13%. Drug cases are relatively rare at just 2% of the total.

I converted all sentence types to a common scale of "month-equivalents" so I could compare across fines, imprisonment, and other sentence types. Fines were converted using the Criminal Code's own formula (15,000 MNT per day, or about 450,000 MNT per month). This gives us a single severity measure that works across the full range of outcomes.

## The employment surprise

In the international literature, gender and race are the usual suspects for sentencing bias. Mongolia doesn't have the racial diversity that drives disparities in places like the U.S., so the question here is about gender, education, age, and employment.

Employment status turned out to be the standout finding. It's the only demographic variable that survives rigorous statistical correction across all model specifications.

![Employment gap in sentencing](/images/sentencing-bias/employment_gap.png)

Unemployed defendants receive an average of 13.9 month-equivalents in sentence severity, compared to 6.8 for employed defendants. That gap of about 7 months in the raw data shrinks to 3.7 months after controlling for crime type, criminal history, and aggravating and mitigating factors, but it remains highly significant (p < 0.001). It's consistent across every model I ran: OLS, multilevel, log-transformed, different sample definitions. Employment status is the one demographic variable that keeps showing up.

To put that 3.7-month effect in perspective: the average fine in the dataset is about 1.3 month-equivalents. So the employment penalty is roughly equivalent to moving from a typical fine to a sentence that's nearly three times as severe. Employment status is not a legally prescribed sentencing factor in Mongolia's Criminal Code. It shouldn't matter. But it does.

## Gender: more complicated than it looks

Gender is where a simple analysis would give you the wrong answer.

If you run a straightforward regression with all 29,847 complete cases, the gender coefficient is small and doesn't reach statistical significance (p = 0.074). You might conclude that Mongolian courts treat men and women roughly the same. That would be partially right and partially wrong.

![Gender paradox in sentencing](/images/sentencing-bias/gender_paradox.png)

A two-stage model tells a different story. In stage one, looking at whether a defendant is imprisoned at all (N = 40,626), women are 41% less likely to be imprisoned than men with similar cases (odds ratio = 0.59). That's a large effect. But in stage two, looking only at defendants who were actually imprisoned (N = 5,578), women receive sentences about 4 months longer than comparable men (p = 0.003).

This is a classic Simpson's paradox. The overall average hides two opposite effects that cancel each other out. Women get lighter treatment at the imprisonment decision stage, but the women who do end up in prison tend to have committed more serious offenses (they had to clear a higher bar to get there), and they receive correspondingly longer sentences.

So gender does matter in Mongolian sentencing, but it operates through the imprisonment decision, not through sentence length.

## What actually drives sentencing

The most reassuring finding from this analysis is about what happens when you decompose what's actually driving sentencing variation. I ran a sequential regression, adding blocks of variables one at a time to see how much each group contributes.

![Variance explained by different factors](/images/sentencing-bias/variance_explained.png)

Aggravating and mitigating circumstances (things like whether the defendant confessed, compensated the victim, or committed the crime while on probation) explain 16.2% of sentencing variance. Demographics explain 3.7%. Crime type adds 3.1%. Court effects and year effects are basically noise at 0.5% and 0.2%.

In other words, the legally prescribed sentencing factors explain more than four times as much variance as all demographic variables combined. Mongolian judges are, for the most part, following the law. The system isn't perfect (that employment gap is real), but it's not driven by demographics in the way that research from other countries might lead you to expect.

## What the data doesn't tell us

I should be upfront about the limitations. Age data is missing for 42.7% of cases, and that rate is getting worse over time (32.5% missing in 2020, 61.5% by 2025). More recent court decisions appear to have shorter biographical sections. The primary analysis uses complete cases only (29,847 of the 75,323 total), though the results hold up when I relax the age requirement and use a larger sample of 36,829.

The severity measure for non-imprisonment sentences (community service, suspended sentences, probation) is approximate. I used the fine-to-months conversion from the Criminal Code, but reasonable people could argue for different conversion rates. I ran sensitivity checks with both conservative and liberal conversion rates, and the key findings hold.

And of course, there are things the data simply can't capture: quality of legal representation, the specifics of each case beyond what's coded, and whether plea bargaining plays a role that isn't visible in the final decision text.

## What this tells us

Mongolia's criminal courts are not primarily driven by demographic bias. Legal factors dominate sentencing, and court-to-court variation is minimal (courts explain less than 1% of variance after case-level controls). That's genuinely good news, and it's worth saying clearly.

But the employment gap is a real problem. A 3.7-month penalty for being unemployed, after controlling for everything else, means that economic status is influencing outcomes in ways the law doesn't intend. Whether this reflects conscious bias, unconscious assumptions about defendants' "stability" or risk of reoffending, or some unmeasured confound, the data can't say. But the pattern is consistent and substantial.

The fact that we can even have this conversation is thanks to shuukh.mn publishing every court decision. That level of judicial transparency is more than most countries offer. Mongolia doesn't always get credit for the things it does well in governance, but open court records is one of them.

If you're interested in the details, the full analysis code and notebooks are available [on GitHub](https://github.com/robertritz/blog/tree/main/research/sentencing-bias).
