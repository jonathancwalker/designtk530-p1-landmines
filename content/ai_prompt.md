I'm presenting a data project and want an honest critique. Please poke holes in it.

TOPIC & QUESTION
Consumer product safety in the US. Main question: How have product recalls and consumer-reported incidents changed over time across product categories, and what can past recalls and incidents tell a small/mid-sized company building a new product about the hazards to plan for?
Audience: small and mid-sized product teams without an in-house safety department.

DATA (CPSC / SaferProducts.gov public database, downloaded 9/29/2026)
- 70,000 consumer incident reports, 2011–Sep 2026 (exactly 70,000 rows, so probably a truncated export). Fields: product category, severity, victim age, free-text description.
- 10,027 CPSC recalls, 1973–Sep 2026. Only title, date and summary text: no category or hazard columns.

METHODS
- Recall categories predicted with TF-IDF + logistic regression trained on the incident reports' own categories: 93% accuracy on held-out incident reports; in a hand check of 40 recalls about 33 looked right. Keeping only predictions with ≥50% confidence (85% of recalls) doesn't change the top six recall categories (largest share shift 1.4 points).
- Hazard types tagged with keyword patterns (78% of recalls and 84% of reports get at least one tag).
- No formal statistical tests (not required for this assignment).

FINDINGS
1. Recalls held at ~240–330/year from 2011–2020, hit a low of 219 in 2021, then rose to 420 in 2025 and 459 in Jan–Sep 2026 — the most of any year since 1973. Most of the recent rise is Furniture (43 → 97 recalls, 2024 → 2026) and Toys & Children (25 → 77). Incident reports fell from 6,837 (2012) to 3,033 (2019) and were back to 4,595 in 2025.
2. Three lists don't match. Kitchen products are 36% of incident reports but 5% of recalls, and only 0.4% of Kitchen reports were serious (hospital or death). Sports & Recreation is 22% of recalls but 6% of reports. Most serious by share: Clothing & Accessories 8.4% (156 of 1,850), Fuel/Lighters/Fireworks 7.5%, Sports & Recreation 6.7%. Overall ~2% of reports with known severity were serious.
3. I expected children's products to be recalled most. They're mid-pack (Toys & Children 9% of recalls, Baby 6%), but 83% of Baby/Toys reports that give an age involve a child under 5.
4. Hazards differ by product type (% of each category's recalls, 2011–2026): Electronics 72% fire/burn; Home Maintenance 50% fire; Toys & Children 59% choking/ingestion; Furniture 36% falls/tip-over; Sports & Rec 27% falls and 26% crash/impact; Clothing 49% regulatory violation and 48% fire. About 20% of all recalls since 2011 cite a broken safety standard (lead paint, flammability, child-resistant packaging).
5. Recalls vs. reports talk about different hazards: reports mention fire 45%, parts breaking 27%, explosions 16%; recalls mention fire 33%, choking 10%, parts breaking 2%.

QUALITATIVE (random sample of 60 records: 30 recalls, 30 reports)
Themes: (a) fire and heat from everyday electronics/appliances ("The phone blew up and caught on fire."); (b) things giving way in normal use ("The plastic hinge on it snapped"); (c) a recall isn't the end of the story — about 1 in 7 reports mention a recall, e.g. "the recall did not cover my specific model" and recall replacement bolts that later snapped. Counterexamples: a children's loungewear recall for flammability (fire isn't only gadgets); "Onewheel ejected me when I tried to stop" (an injury with nothing breaking).

PROPOSED A/B TEST
Small/mid companies submitting a new product to a testing lab are randomly assigned (by company): A = normal submission; B = same plus a panel showing the closest past recalls and their hazards. Main measure: passing safety review on the first try within 90 days. Meaningful: +10 points (e.g. 60% → 70%). Guardrail: days to clearance. Risks: reviewers knowing the group (keep blind); A companies finding recalls on CPSC's site anyway.

PLEASE ANSWER
1. Do my conclusions follow from this evidence? Which claims are strongest and which are overstated?
2. What alternative explanations should I consider (especially for the recall increase and the Kitchen mismatch)?
3. Are the qualitative themes well supported, or could they be artifacts of my sampling or keyword methods?
4. What are the biggest weaknesses in the A/B test design?
5. What one additional analysis would most change or strengthen my conclusions?
Be specific about where you agree and where you'd push back.
