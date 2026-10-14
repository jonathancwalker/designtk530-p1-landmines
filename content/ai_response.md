# Critical review: Consumer Product Safety Analysis

My assessment: this is a promising descriptive research project with a genuinely useful product idea, but several of your most interesting conclusions are currently stronger than your evidence supports.

The central issue isn't your lack of statistical tests. It's measurement validity: whether the categories, hazards, time trends, and outcomes you've constructed actually represent what you think they represent.

I would push you hardest on four things:

1. The recall classification model. Your 93% accuracy doesn't establish 93% accuracy on recalls, and the hand check suggests substantial domain-transfer error.
2. The comparison between recalls and consumer incidents. These are different observation processes, not interchangeable measurements of danger.
3. Your interpretation of the 2026 surge. The rise deserves attention, but the mechanisms driving it are not established.
4. The A/B test's causal logic. You're measuring successful passage through a review process, but your stated objective is preventing safety hazards.

There's also a major opportunity: your research could become something much more actionable than a dashboard of historical safety trends. You could demonstrate how historical recall evidence helps product teams identify hazards they would otherwise overlook.

## 1. Do your conclusions follow from the evidence?

| Finding | Rating |
|---|---|
| 1: Recall counts have increased recently | Strong descriptively. The counts show an increase, assuming consistent inclusion criteria, but they don't establish that products have become more dangerous or explain why recalls increased. |
| 2: Recalls, reports, and severe incidents differ by category | Partially supported. Denominators, classification errors, and differences in reporting mechanisms are major limitations. |
| 3: Children's products are not the most recalled | Mixed. Grouping Baby and Toys & Children changes the interpretation. The age finding is plausible but much less surprising than it appears. |
| 4: Different categories have different hazard profiles | Promising, needs validation. Probably your most actionable finding, but it relies heavily on keyword tagging and the semantics of recall descriptions. |
| 5: Reports and recalls emphasize different hazards | Most vulnerable. Keyword differences could partly reflect how narratives are written, rather than differences in underlying hazards. |

### Finding 1: The recall increase

I agree that the recent increase is significant enough to investigate. However, I would not present 2026 as having the most recalls since 1973 without verifying historical completeness and consistent counting rules. While an independent recall tracker also reports 420 CPSC records for 2025, your historical comparison needs an audit.

More importantly, an increase in recalls does not necessarily mean an increase in unsafe products. The causal chain is approximately: unsafe products → detection → investigation → recall. Changes anywhere along that chain can increase recall counts: more hazardous products, but also improved surveillance, more aggressive enforcement, more voluntary corrective actions, or changes in how recalls are recorded.

There's another issue: saying Furniture increased from 43 to 97 between 2024 and 2026 partly depends on an imperfect category model. If I were reviewing this presentation, I'd ask: how do you know the increase in furniture recalls is real, rather than a consequence of your classifier making different mistakes across years?

### Finding 2: The Kitchen mismatch

This is interesting, but I would challenge any suggestion that Kitchen products are unusually safe merely because they have high report volume and low recall volume.

| Measure | What it actually represents |
|---|---|
| 36% of incident reports | Share of published reports in your dataset classified as Kitchen |
| 5% of recalls | Share of recall records predicted as Kitchen |
| 0.4% serious reports | Share classified as serious among Kitchen reports, subject to how missing severity is handled |

None measures the probability that a Kitchen product will injure its user. For that, you'd ideally need an exposure denominator, such as products in use or hours of product use. An everyday kitchen appliance used twice daily for ten years has substantially more opportunities to generate reports than an infrequently used consumer product.

I would also investigate why only 0.4% of Kitchen reports are serious. That might reflect genuinely lower injury severity, but it could reflect reporting behavior, severity coding, missing data, or the composition of Kitchen reports. A product can present a severe potential hazard without having caused a recorded injury; CPSC explicitly accepts reports about risks of injury even when no actual injury occurred.

So your defensible conclusion is:

> Kitchen products occupy a much larger share of published incident reports than predicted recalls, demonstrating that report frequency and recall frequency capture different aspects of product safety.

Your less defensible conclusion would be:

> Kitchen products are frequently reported but relatively safe.

The latter requires evidence you don't have.

### Finding 3: Children's products

I would push back on the framing of this as a surprising finding. Toys & Children (9%) and Baby (6%) together are 15%, potentially a much more prominent category than either appears individually. Other categories are similarly broad: Sports & Recreation might encompass everything from bicycles to recreational vehicles. You're comparing categories of unequal conceptual size.

The 83% under-five figure also needs context. Baby products are largely designed for very young children, so you should expect the affected population to skew young. I'd ask for the under-five percentage separately for Baby and Toys & Children, and the fraction with a recorded age in each category.

Your stronger takeaway is not that children's products are unexpectedly uncommon in recalls. It's that product categories, intended user populations, and hazard mechanisms need to be considered together.

### Finding 4: Category-specific hazards

This is where I think you have the strongest connection to your audience. If I'm a small company building a new piece of furniture, knowing that tip-over and fall hazards repeatedly appear in recalls is potentially useful.

But the percentages need careful interpretation. For example, 72% of Electronics recalls involve fire or burns. Does that mean (1) the recalled electronics overwhelmingly experienced fire-related failures, (2) recall summaries disproportionately describe fire-related risks, or (3) your keywords are more effective at detecting thermal hazards than electrical, mechanical, or chemical hazards? Your current method cannot fully distinguish these.

There is also a labeling problem with your regulatory-violation category. A regulatory violation is not necessarily a hazard mechanism. Flammability, toxicity from lead, and failure of child-resistant packaging are different hazards, even if each violates a safety standard. I'd use two separate dimensions: hazard mechanism (thermal, electrical, choking, entrapment, instability, chemical exposure, etc.) and regulatory dimension (whether a particular mandatory standard was cited, and which one).

### Finding 5: Different hazards in recalls and reports

Here I'd be most skeptical. Parts breaking appears in 27% of reports but only 2% of recalls. Consider:

- Incident report: "The metal bracket snapped, and the shelf fell off the wall."
- Recall summary: "The wall-mounted shelf can detach, posing an impact hazard."

Both could describe the same underlying failure. A keyword system might tag the first as breaking and the second as impact. This is not random measurement error; it's systematic measurement bias arising from document type. Consumer reports describe events and observed failures. Recall notices tend to describe hazards and potential consequences.

I would avoid saying "Reports identify problems that recalls overlook." Instead say: "Consumer narratives and recall notices emphasize different aspects of product failure, which may make their combination useful for hazard discovery."

## 2. Alternative explanations you should consider

### An important data-source discovery

CPSC already provides structured product and hazard information for recalls through its API. The official developer FAQ lists fields including Product Type, Product Description, Hazard, Recall Date, and Recall Number, and CPSC's recall dashboard supports filtering and downloads by category and hazard. Your current recall dataset is missing information that may be recoverable. I'd investigate the [CPSC Recalls Dashboard](https://www.cpsc.gov/Recalls) and the [CPSC Recalls API documentation](https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information) before doing anything else. The official product types and hazards may not align one-to-one with your incident-category taxonomy, but they should be your first point of reference.

### Alternative explanations for the recall increase

| Hypothesis | How it could explain the increase | What would test it |
|---|---|---|
| Regulatory changes | New mandatory standards create additional violations and enforcement opportunities | Separate recalls citing mandatory standards and examine trends around effective dates |
| Enforcement and surveillance | CPSC becomes more effective at identifying products that violate standards | Examine changes in violation-related recalls, enforcement information, and product sourcing |
| E-commerce and imports | More products from unfamiliar manufacturers enter US markets | Compare company, import, and marketplace information across years |
| Product-market changes | More products are sold, or the mix shifts toward frequently recalled categories | Normalize by sales, import, or product-market data |
| Historical data consistency | Changes in archive coverage or record inclusion make comparisons misleading | Compare annual totals against official annual publications |
| Category-model drift | The classifier labels newer products differently from older ones | Manually validate recent and historical recall categories separately |

One concrete example: the STURDY Act, governing clothing storage units, could be relevant to furniture recalls; recent CPSC recall notices explicitly reference violations of that standard. I would explore whether recent furniture recalls are concentrated in clothing storage units rather than a broad range of furniture products. "A substantial part of the rise in furniture recalls may be concentrated in products covered by newer stability requirements" is a more useful hypothesis for a company designing a dresser, provided your data support it. Don't interpret the increase until you decompose it by product subtype and recall reason.

### Alternative explanations for the Kitchen mismatch

1. Exposure frequency: kitchen products are common and regularly used, so there are more opportunities to observe failures.
2. Reporting propensity: a broken refrigerator or overheating appliance may motivate a complaint even if no one is injured.
3. Distinct thresholds for recalls: a recall depends on identifying a defect, substantial hazard, or noncompliance; repeated complaints aren't automatically sufficient.
4. Your taxonomy: a recalled kitchen appliance could be classified under Electronics or Home Maintenance.
5. Missingness and selection: exactly 70,000 incident rows raises a serious completeness concern. If the export contains only the first 70,000 matching records under some ordering, proportions and time trends may be biased.

There's also independent historical evidence that Kitchen dominated early SaferProducts.gov reporting (a 2012 congressional record reported about one-third of incident reports in that category), so the Kitchen pattern isn't necessarily unique to your export.

### The subtle issue: you're comparing different populations

Imagine every product category has exactly the same underlying defect rate. You could still observe very different recall and report distributions if consumers report certain defects more often, manufacturers find defects through their own testing, regulators target certain categories, some hazards trigger mandatory action without reported injuries, or some dangerous products stay in use for years before the problem is identified. Differences between the two datasets can arise even without differences in underlying safety, and this needs to be explicit in your presentation.

## 3. Are your qualitative themes well supported?

Broadly plausible, but I'd treat them as illustrative observations, not confirmed recurring patterns across the population.

- **Theme A (fire and heat):** reasonably supported as an example, not as a prevalence claim. Your keyword tagging and qualitative reading may not be independent evidence if both respond to the same words ("caught fire").
- **Theme B (things giving way in normal use):** potentially your most interesting theme: ordinary use can reveal failure mechanisms design teams underestimate. But a short narrative ("the hinge snapped") might not establish that use was normal. I'd code use context separately: normal, foreseeable misuse, abnormal, or unknown.
- **Theme C (recalls don't resolve the problem):** interesting but weakly supported as a frequency finding. About one in seven of 30 reports means roughly four reports, a very small numerator. You can say "Several reports in our sample raised concerns about recall coverage or remedy effectiveness," but not "One in seven consumers experience problems with recalls." The research direction (remedies that fail, exclude a model, or create a new failure mode) is more novel than cataloging recall hazards.

**Method suggestion:** use a small, reproducible coding protocol (category, injury vs. potential harm, failure mechanism, use conditions, cited hazard, recall/remedy mention), allow multiple codes per record, and use a stratified sample across categories and severity levels for comparing themes, keeping a simple random sample for prevalence.

## 4. The A/B test: good idea, design needs work

1. **You're intervening too late.** By the time a product goes to a testing lab, the design, components and manufacturing are mostly locked. If the panel surfaces a hazard and the team redesigns, clearance could be delayed: the treatment could improve real safety while hurting your primary metric. Move the intervention earlier, before the design is frozen.
2. **Passing a safety review isn't the same as being safe.** Better outcomes: whether teams identify hazards before testing, identify the right standards, have fewer critical nonconformities, and make design changes before certification. First-pass approval is an operational outcome and an imperfect safety proxy.
3. **No power calculation.** 60% → 70% at 80% power and α = 0.05 needs roughly 350–360 submissions per group (~700 total), before accounting for company-level clustering. That may be very hard to recruit among small and mid-sized manufacturers.
4. **It mixes mechanisms.** Awareness of requirements, hazard identification, test preparation, extra review time and liability concern could each explain a win. The current control can't separate "historical recalls helped" from "any structured safety guidance helped."
5. **The 90-day window creates censoring.** If careful teams don't finish within 90 days, counting them as failures penalizes caution, and excluding them biases the result. Define this in advance.

**Redesign:** intervene at the design-review stage; randomize by company, stratified by category; give both arms equal general guidance; primary outcome = share of independently identified critical hazards the team recognized and addressed (blinded rubric); secondary = first-pass compliance and critical nonconformities; guardrail = time and cost to clearance. Better still, three arms: A standard preparation, B structured checklist + standards guidance, C = B + relevant historical recalls. C vs. B isolates the value of recall evidence. A smaller first step: a randomized study with mock product-design briefs, scored by blinded experts.

## 5. The one additional analysis I'd prioritize

Validate the recall category and hazard labels against authoritative information, then recompute the headline findings. Your 93% is in-domain; 33/40 on recalls is about 82.5%, with a rough 95% Wilson interval of 68%–91%. The confidence-threshold check shows stability, not correctness: a classifier can make the same mistake at high confidence.

Workflow: (1) recover official recall metadata via CPSC's API/downloads; (2) map it into a common taxonomy, keeping ambiguous cases explicit; (3) hand-validate a stratified set of ~150–250 recalls; (4) report precision and recall for the categories driving your story (Kitchen, Furniture, Toys & Children, Baby, Electronics); (5) recompute the category shares, recent increases, Kitchen gap and hazard distributions.

## 6. Additional issues a tough reviewer might catch

- **The exactly-70,000-row incident file** may be your biggest data-integrity threat. If you can't verify completeness, don't present annual incident counts as complete annual totals.
- **Severity denominators:** check that every category percentage uses the same definition of "known severity," report missingness by category, and separate reported injury severity from potential hazard severity.
- **Keyword coverage:** 22% of recalls and 16% of reports are untagged. Check untagged and multi-tag rates by category; uneven coverage could distort category hazard rankings.
- **One recall isn't one product or one unit:** a recall can cover millions of units or a few hundred. Recall counts identify recurring failure types, not risk.

## 7. Suggested presentation structure

1. Why small product teams need better safety intelligence
2. What historical safety data reveal (recalls and reports show different patterns)
3. What hazards deserve attention by product type
4. What this analysis cannot tell us
5. A possible solution: contextual recall intelligence, surfaced while designers are still making decisions
6. How we'd test whether it helps

The data analysis becomes evidence supporting a design intervention, rather than an attempt to infer the true safety of product categories from imperfect administrative records.

## 8. Questions I'd ask in Q&A

1. How can we trust the recall categories when your classifier was trained on a different type of document?
2. Why does a high proportion of Kitchen incident reports imply anything about product safety without data on how often Kitchen products are used?
3. Could the recent recall increase reflect changes in enforcement or mandatory standards rather than more dangerous products?
4. How do you know your differences in hazard types aren't just differences between the language consumers and regulators use?
5. If the recall tool causes a company to find a hazard, redesign its product, and miss the 90-day approval deadline, would you call that a failure?

## Final verdict

| Dimension | Assessment |
|---|---|
| Research question | Strong and relevant |
| Data selection | Appropriate sources, serious completeness concern |
| Predictive classification | Sensible baseline, insufficient target-domain validation |
| Hazard analysis | Useful direction, potential systematic measurement bias |
| Qualitative work | Good illustrations, insufficient for prevalence claims |
| Causal interpretation | Needs restraint |
| A/B test hypothesis | Compelling |
| A/B test implementation | Needs substantial redesign |
| Practical value | Potentially high if translated into actionable hazard guidance |

Stop trying to establish which product categories are truly most dangerous from recall counts and self-selected reports. Focus instead on: **can historical product failures help designers identify relevant safety hazards before those failures recur?** That's a question your datasets can support, and it's directly relevant to your audience.

*(Condensed for this page: same points, mostly the AI's own wording, with some sections shortened. The full original response is in the notebook appendix.)*
