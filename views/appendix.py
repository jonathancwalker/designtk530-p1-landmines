"""Appendix: explore the data yourself, plus the fine print (data, methods, design changes, limits)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (
    AXIS, BLUE, FIRST_YEAR, INK_2, LAST_FULL_YEAR, LAST_YEAR, ORANGE, PARTIAL_YEAR_NOTE, SMALL_N, dumbbell,
    eyebrow, lede, load_tables, show, similarities, style,
)

counts, severity, hazards, recalls, meta = load_tables()
rec_counts = counts[counts["source"] == "recalls"]
inc_counts = counts[counts["source"] == "incidents"]

st.title("The fine print")
lede("Dig into the data.")

# ======================================================================
st.header("Explore the trend")
all_cats = sorted(counts["category"].unique())
fc1, fc2 = st.columns([3, 2])
with fc1:
    use_all = st.toggle("All categories", value=True)
    picked = all_cats if use_all else st.multiselect("Categories", all_cats, default=[], placeholder="Pick one or more")
with fc2:
    y0, y1 = st.slider("Years", FIRST_YEAR, LAST_YEAR, (FIRST_YEAR, LAST_YEAR))


def per_year(df):
    sel = df[df["category"].isin(picked) & df["year"].between(y0, y1)]
    return sel.groupby("year")["n"].sum().reindex(range(y0, y1 + 1), fill_value=0)


if not picked:
    st.warning("No categories picked. Choose at least one (or flip on *All categories*).")
elif y1 - y0 < 2:
    st.warning("Pick at least three years to see a trend.")
else:
    rec_y, inc_y = per_year(rec_counts), per_year(inc_counts)
    if rec_y.iloc[0] == 0 or inc_y.iloc[0] == 0:
        st.warning(f"No recalls or no reports for this pick in {y0}, so there's nothing to compare against. "
                   "Try an earlier start year or more categories.")
    else:
        end = min(y1, LAST_FULL_YEAR)
        st.markdown(f"**{'All categories' if use_all else ', '.join(picked)}**, {y0}–{y1}: "
                    f"**{int(rec_y.sum()):,} recalls** and **{int(inc_y.sum()):,} incident reports**.")
        fig = go.Figure()
        for s, color, name in [(rec_y, BLUE, "Recalls"), (inc_y, ORANGE, "Incident reports")]:
            idx = s / s.iloc[0] * 100
            done = idx[idx.index <= LAST_FULL_YEAR]
            fig.add_scatter(x=done.index, y=done.values, mode="lines+markers", name=name,
                            line=dict(color=color, width=2), marker=dict(size=8, color=color),
                            customdata=s.loc[done.index].values,
                            hovertemplate=f"{name}, %{{x}}: %{{customdata:,}}<extra></extra>")
            if LAST_YEAR in idx.index and LAST_FULL_YEAR in idx.index:
                fig.add_scatter(x=[LAST_FULL_YEAR, LAST_YEAR], y=idx.loc[[LAST_FULL_YEAR, LAST_YEAR]].values, mode="lines",
                                line=dict(color=color, width=2, dash="dot"), hoverinfo="skip", showlegend=False)
                fig.add_scatter(x=[LAST_YEAR], y=[idx.loc[LAST_YEAR]], mode="markers", showlegend=False,
                                marker=dict(size=9, color="white", line=dict(color=color, width=2)),
                                customdata=[s.loc[LAST_YEAR]], hovertemplate=f"{name}, %{{x}} (Jan–Sep): %{{customdata:,}}<extra></extra>")
            if end in idx.index:
                fig.add_annotation(x=end, y=idx.loc[end], text=f"{idx.loc[end] - 100:+.0f}%", showarrow=False,
                                   xanchor="right", xshift=-10, yshift=10, font=dict(color=color, size=13))
        fig.add_hline(y=100, line=dict(color=AXIS, width=1))
        fig.update_yaxes(title_text=f"Index ({y0} = 100)")
        fig.update_xaxes(dtick=1 if y1 - y0 <= 8 else 2)
        show(style(fig, 380, legend=True))
        st.caption(f"Both lines scaled so {y0} = 100, so they can share an axis. {PARTIAL_YEAR_NOTE} (hollow point).")
        with st.expander("Numbers"):
            st.dataframe(pd.DataFrame({"recalls": rec_y, "incident reports": inc_y}).T, width="stretch")

# ======================================================================
st.header("The three lists, in full")
rec_share = rec_counts[rec_counts["year"].between(FIRST_YEAR, LAST_YEAR)].groupby("category")["n"].sum()
inc_share = inc_counts.groupby("category")["n"].sum()
rec_pct, inc_pct = rec_share / rec_share.sum() * 100, inc_share / inc_share.sum() * 100
a, b = st.columns(2, gap="large")
with a:
    st.markdown("**Recalls vs. complaints**")
    rows = list(rec_pct.sort_values().index)
    show(dumbbell(rows, rec_pct, inc_pct.reindex(rows).fillna(0), "Recalls", "Incident reports", "% of all records", 520))
    st.caption(f"{int(rec_share.sum()):,} recalls ({FIRST_YEAR}–{LAST_YEAR}) vs. {int(inc_share.sum()):,} reports. Long line = big mismatch.")
with b:
    st.markdown("**How serious**")
    s = severity.sort_values("pct_severe")
    small = s["n_with_severity"] < 200
    fig = go.Figure(go.Bar(
        y=s["category"], x=s["pct_severe"], orientation="h", marker_color=np.where(small, SMALL_N, BLUE),
        text=[f"{p}%  ({n:,} of {d:,})" for p, n, d in zip(s["pct_severe"], s["n_severe"], s["n_with_severity"])],
        textposition="outside", textfont=dict(color=INK_2, size=12), cliponaxis=False,
        hovertemplate="%{y}: %{x}% hospital or death<extra></extra>",
    ))
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(title_text="% of reports ending in hospital or death", ticksuffix="%", range=[0, s["pct_severe"].max() * 1.6])
    show(style(fig, 520))
    st.caption("Gray = fewer than 200 reports, so read loosely.")

# ======================================================================
st.header("The data")
st.markdown(
    f"""
Both from the CPSC's [SaferProducts.gov public database](https://www.saferproducts.gov/PublicSearch), pulled 9/29/2026.

| | Incident reports | Recalls |
|---|---|---|
| Rows | {meta['n_incidents']:,} | {meta['n_recalls']:,} |
| One row | one report from a consumer, doctor, etc. | one recall announcement |
| Years | Mar 2011 – Sep 2026 | 1973 – Sep 2026 |
| Category / hazard | category given, hazard from text | neither, both predicted from text |
"""
)

st.header("Cleaning")
st.markdown(
    """
- Both files open with a disclaimer line; the recall file has one broken first record (2015 IKEA MALM recall), dropped.
- Incident file: 40 → 18 columns. Dropped the mostly-empty stuff (UPC, date manufactured) and things the questions don't need (serial number, ZIP).
- "Unspecified" and "[REDACTED]" count as missing. Victim age is missing for 38% of reports.
- No repeated report or recall numbers, so nothing deleted. 118 reports share identical text, including 23 copy-paste Stihl chainsaw reports filed the same day.
- Severity on an ordered scale. "Serious" = hospital or death. 3,470 reports with unknown severity (~5%) left out of severity numbers.
"""
)

st.header("Guessing recall categories")
st.markdown(
    """
Recalls don't come with a category. So I trained a text classifier (TF-IDF + logistic regression) on the incident reports, which *do*, and let it label the recalls.

- **93%** right on incident reports it hadn't seen (macro F1 0.88).
- **~33 of 40** recalls looked right when I checked by hand. The misses were mostly low-confidence guesses.
- **Does it matter?** Keeping only guesses it was 50%+ sure about (85% of recalls), the top six categories don't change and nothing moves more than ~1.5 points.
"""
)

st.header("Tagging hazards")
st.markdown(
    """
Keyword patterns (fire, tip-over, choking...), several tags allowed per record. For recalls, only the title and hazard sentences get searched, because product descriptions cause false hits (a top with "cut-out shoulders" isn't a laceration hazard). 78% of recalls and 84% of reports get a tag. It misses weird phrasings ("Onewheel ejected me") and sometimes misfires ("hands break out" ≠ breakage), so treat the shares as ballpark.
"""
)

st.header("The search, and how it changed")
st.markdown(
    """
**Plan:** embed every recalled product with a small local language model ([model2vec](https://github.com/MinishLab/model2vec)), return the closest. Only the *product* gets embedded (title + "This recall involves..." sentence), not the company or hazard.

**Problem:** testing a dozen queries, embeddings got different wording right but fumbled exact names. Keyword matching did the opposite.

**Fix:** a 50/50 blend. Live comparison:
"""
)
TESTS = ["hoverboard", "pressure cooker", "lithium power bank", "teething toy for infants", "pram for a newborn"]
rows = []
for q in TESTS:
    sim_emb, sim_kw = similarities(q)
    top = lambda sc: recalls["product_text"].iloc[int(np.argmax(sc))].split(". ")[0] if sc.max() > 0 else "(nothing)"
    rows.append({"Query": q, "Embeddings": top(sim_emb), "Keywords": top(sim_kw), "Blend (used)": top(0.5 * sim_emb + 0.5 * sim_kw)})
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
st.caption("Nobody gets 'pram'. When nothing's close (similarity < 0.55), the tool says so. Runs locally; nothing leaves the app.")

st.header("How this dashboard changed")
st.markdown(
    """
**v1** was every chart I'd made on one page: long caveat box, two trend charts, a 13-column hazard grid. Accurate, but you'd get lost in the sauce.

**v2** turned it into a story: headings that say the finding, caveats tucked away, one dot chart instead of grouped bars, trends on one axis.

**v3 (this one):** one idea per tab. The story tab is three findings + quotes + takeaways, no filters. Everything you can poke at lives here.
"""
)

st.header("Limits")
st.markdown(
    """
- Self-reported, no sales data. Counts, not rates.
- The incident file is probably a partial export (exactly 70,000 rows).
- Recall categories and all hazard tags are educated guesses from text.
- 2026 is Jan–Sep only.
- Can't say *why* recalls are rising: less safe products, stricter enforcement and more online sellers all fit.
"""
)

st.header("Next time")
st.markdown(
    """
- Add sales data to turn counts into rates.
- Link reports to recalls by brand/model to see which complaints come *before* a recall.
- Get the full incident export.
- Stronger language model for the search (hi, *pram*).
- Actually run the A/B test.
"""
)

st.header("Tools & AI use")
st.markdown(
    "Python (pandas, scikit-learn, model2vec), Plotly, Streamlit. I used Claude (Anthropic) for help with code and "
    "drafting; every number on here is computed from the data, and I checked the quotes against the source records."
)
