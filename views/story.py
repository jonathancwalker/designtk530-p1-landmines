"""The story: question -> three findings -> what people write -> what to do about it. Kept short on purpose."""

import plotly.graph_objects as go
import streamlit as st

from common import (
    ASSETS, BLUE, BLUE_RAMP, ORANGE, FIRST_YEAR, INK, INK_2, LAST_FULL_YEAR, LAST_YEAR, MUTED, eyebrow,
    expected_found, lede, load_tables, overall_hazard_share, plain, quote, show, style,
)

counts, severity, hazards, recalls, meta = load_tables()
rec_counts = counts[counts["source"] == "recalls"]
inc_counts = counts[counts["source"] == "incidents"]
rec_hz = hazards[hazards["source"] == "recalls"]

# ---------- numbers (all computed) ----------
rec_by_year = rec_counts.groupby("year")["n"].sum()
n_now = int(rec_by_year[LAST_YEAR])
first_rec_year = int(rec_by_year.index.min())
by_cat_year = rec_counts.pivot_table(index="category", columns="year", values="n", fill_value=0)
movers = (by_cat_year[LAST_YEAR] - by_cat_year[LAST_YEAR - 2]).sort_values(ascending=False).head(2).index

rec_share = rec_counts[rec_counts["year"].between(FIRST_YEAR, LAST_YEAR)].groupby("category")["n"].sum()
rec_pct = rec_share / rec_share.sum() * 100
inc_pct = inc_counts.groupby("category")["n"].sum()
inc_pct = inc_pct / inc_pct.sum() * 100
sev = severity.set_index("category")
most_severe = sev[sev["n_with_severity"] >= 200]["pct_severe"].sort_values(ascending=False)
most_reported = inc_pct.idxmax()

hz = rec_hz.pivot(index="category", columns="hazard", values="pct").fillna(0)


def top_hazard(cat):
    row = hz.loc[cat].drop(["none stated", "regulatory violation"], errors="ignore")
    return row.idxmax(), row.max()


reg_overall = overall_hazard_share(hazards, "recalls").get("regulatory violation", 0)
SHORT = {  # shorter category names for tight spots
    "Furniture, Furnishings & Decorations": "Furniture",
    "Home Maintenance and Structures": "Home maintenance",
    "Sports and Recreation": "Sports & rec",
    "Clothing and Accessories": "Clothing",
    "Fuel, Lighters and Fireworks": "Fuel, lighters & fireworks",
    "Toys & Children": "Toys",
}
short = lambda c: SHORT.get(c, c)

# ======================================================================
st.title("Know the landmines before you launch")
lede("How can past product failures help us plan well today?")

with st.form("hook", border=False):
    c_in, c_btn = st.columns([4, 1], vertical_alignment="bottom")
    hook_q = c_in.text_input("What are you building?", placeholder="e.g. kids dresser")
    if c_btn.form_submit_button("Check it →", width="stretch") and hook_q.strip():
        st.switch_page("views/check_product.py", query_params={"q": hook_q.strip()})

k1, k2, k3 = st.columns(3)
h_e, p_e = top_hazard("Electronics")
with k1.container(border=True):
    st.metric(f"recalls in {LAST_YEAR}", f"{n_now:,}")
    st.caption("Biggest year so far (3 months left btw)")
with k2.container(border=True):
    st.metric(f"of reports are {most_reported.lower()} products", f"{inc_pct[most_reported]:.0f}%")
    st.caption(f"Only {sev.loc[most_reported, 'pct_severe']}% of them were serious.")
with k3.container(border=True):
    st.metric("of electronics recalls involve fire", f"{p_e:.0f}%")
    st.caption("Every product has a villain.")

st.space("medium")
hyp_l, hyp_r = st.columns([3, 2], gap="large", vertical_alignment="center")
with hyp_l:
    st.html(
        "<div class='eyebrow'>My hypothesis</div>"
        "<div style='font-size:2.2rem;font-weight:700;line-height:1.2;letter-spacing:-0.01em;color:#0b0b0b;"
        "margin:0.5rem 0 1rem 0;max-width:38rem'>Recalls are going down, and kids' products get recalled the most.</div>"
        "<div style='font-size:1.6rem;font-weight:600;color:#52514e'>Reality: nope, and nope.</div>"
    )
with hyp_r:
    st.image(str(ASSETS / "hypothesis_bird.png"), width="stretch")

walkthrough = ASSETS / "walkthrough.mp4"
if walkthrough.exists():
    with st.expander("▶ Watch the walkthrough"):
        st.video(str(walkthrough))

st.space("large")

# ======================================================================
f_left, f_right = st.columns([2, 3], gap="large")
with f_left:
    eyebrow("Finding 1")
    st.header("Recalls... are not going down")
    st.markdown(
        f"About {int(rec_by_year.loc[FIRST_YEAR:2020].median())} a year for a decade. Then {int(rec_by_year[2021])} "
        f"in 2021 → **{n_now} by September {LAST_YEAR}**."
    )
    st.markdown(
        f"Most of the jump: **{short(movers[0]).lower()}** ({int(by_cat_year.loc[movers[0], LAST_YEAR - 2])} → "
        f"{int(by_cat_year.loc[movers[0], LAST_YEAR])}) and **{short(movers[1]).lower()}** "
        f"({int(by_cat_year.loc[movers[1], LAST_YEAR - 2])} → {int(by_cat_year.loc[movers[1], LAST_YEAR])}) since {LAST_YEAR - 2}."
    )
with f_right:
    yrs = rec_by_year.loc[FIRST_YEAR:LAST_YEAR]
    done = yrs.loc[:LAST_FULL_YEAR]
    fig = go.Figure()
    fig.add_scatter(x=done.index, y=done.values, mode="lines+markers", line=dict(color=BLUE, width=2),
                    marker=dict(size=8, color=BLUE), hovertemplate="%{x}: %{y} recalls<extra></extra>")
    fig.add_scatter(x=[LAST_FULL_YEAR, LAST_YEAR], y=yrs.loc[[LAST_FULL_YEAR, LAST_YEAR]].values, mode="lines",
                    line=dict(color=BLUE, width=2, dash="dot"), hoverinfo="skip")
    fig.add_scatter(x=[LAST_YEAR], y=[n_now], mode="markers", marker=dict(size=10, color="white", line=dict(color=BLUE, width=2)),
                    hovertemplate="%{x} (Jan–Sep): %{y} recalls<extra></extra>")
    fig.add_annotation(x=LAST_YEAR, y=n_now, text=f"{n_now}<br><span style='font-size:11px;color:{MUTED}'>Jan–Sep</span>",
                       showarrow=False, xanchor="right", xshift=-12, font=dict(color=BLUE, size=14))
    fig.add_annotation(x=2021, y=int(rec_by_year[2021]), text=str(int(rec_by_year[2021])), showarrow=False,
                       yshift=-16, font=dict(color=INK_2, size=12))
    fig.update_yaxes(rangemode="tozero", title_text="Recalls per year")
    fig.update_xaxes(dtick=2)
    show(style(fig, 360))

st.space("large")

# ======================================================================
eyebrow("Finding 2")
st.header("Three lists that don't match")


def top3(series, fmt, note=None):
    for i, (cat, v) in enumerate(series.head(3).items(), 1):
        extra = f" <span style='color:{MUTED}'>{note(cat)}</span>" if note else ""
        st.html(f"<div style='font-size:1.05rem;margin:0.35rem 0'><b>{i}.</b> {short(cat)} "
                f"<b style='color:{BLUE}'>{fmt(v)}</b>{extra}</div>")


l1, l2, l3 = st.columns(3, gap="medium")
with l1.container(border=True, height="stretch"):
    st.markdown("**Most complained-about products**")
    top3(inc_pct.sort_values(ascending=False), lambda v: f"{v:.0f}%")
    st.caption("% of incident reports")
with l2.container(border=True, height="stretch"):
    st.markdown("**Most recalled products**")
    top3(rec_pct.sort_values(ascending=False), lambda v: f"{v:.0f}%")
    st.caption(f"% of recalls, {FIRST_YEAR}–{LAST_YEAR}")
with l3.container(border=True, height="stretch"):
    st.markdown("**Products with the most serious injuries**")
    top3(most_severe, lambda v: f"{v}%")
    st.caption("% of reports ending in hospital or death")

gap_rows = list(rec_pct.sort_values().index)
inc_aligned = inc_pct.reindex(gap_rows).fillna(0)
gap = (inc_aligned - rec_pct.reindex(gap_rows)).abs()
callouts = list(gap.sort_values(ascending=False).index[:2])          # Kitchen and Sports & rec
labels = [short(c) for c in gap_rows]
fig = go.Figure()
for c, lab in zip(gap_rows, labels):
    hot = c in callouts
    fig.add_scatter(x=[rec_pct[c], inc_aligned[c]], y=[lab, lab], mode="lines", hoverinfo="skip", showlegend=False,
                    line=dict(color=INK_2 if hot else "#d9d8d2", width=3 if hot else 2))
fig.add_scatter(x=rec_pct.reindex(gap_rows).values, y=labels, mode="markers", name="Recalls",
                marker=dict(size=11, color=BLUE, line=dict(color="white", width=2)),
                hovertemplate="%{y}: %{x:.0f}% of recalls<extra></extra>")
fig.add_scatter(x=inc_aligned.values, y=labels, mode="markers", name="Incident reports",
                marker=dict(size=11, color=ORANGE, line=dict(color="white", width=2)),
                hovertemplate="%{y}: %{x:.0f}% of reports<extra></extra>")
for c in callouts:
    right = max(rec_pct[c], inc_aligned[c])
    fig.add_annotation(x=right, y=short(c), xanchor="left", xshift=12, showarrow=False, font=dict(size=13, color=INK),
                       text=f"<b>{inc_aligned[c]:.0f}%</b> of reports vs <b>{rec_pct[c]:.0f}%</b> of recalls")
fig.update_xaxes(ticksuffix="%", rangemode="tozero", range=[0, inc_aligned.max() * 1.55], title_text="")
fig.update_yaxes(showgrid=False)
show(style(fig, 470, legend=True))

st.markdown(
    f"Kids' products? Mid-pack: toys are {rec_pct['Toys & Children']:.0f}% of recalls, baby {rec_pct['Baby']:.0f}%. "
    f"But **{meta['kids_under5_pct']:.0f}%** of their reports are about a kid under 5."
)

st.space("large")

# ======================================================================
eyebrow("Finding 3")
st.header("Every product has its own villain")
h_t, p_t = top_hazard("Toys & Children")
h_f, p_f = top_hazard("Furniture, Furnishings & Decorations")
st.markdown("Products seem to have predictable failure modes depending on their category.")

MIN_RECALLS, TOP_PER_CATEGORY, BLANK_BELOW = 100, 3, 5
hm = rec_hz[(rec_hz["n_in_category"] >= MIN_RECALLS) & (rec_hz["hazard"] != "none stated")]
z = hm.pivot(index="category", columns="hazard", values="pct").fillna(0)
keep = sorted({h for _, row in z.iterrows() for h in row.nlargest(TOP_PER_CATEGORY).index})
z = z[z[keep].mean().sort_values(ascending=False).index]
n_cat = hm.groupby("category")["n_in_category"].first()
z = z.loc[n_cat.sort_values().index]
zmax = float(z.values.max())
ylabels = [short(c) for c in z.index]
xlabels = [plain(h).replace("broken safety standards", "broke a standard") for h in z.columns]

fig = go.Figure(go.Heatmap(
    z=z.where(z >= BLANK_BELOW).values, x=xlabels, y=ylabels,
    colorscale=[[i / (len(BLUE_RAMP) - 1), c] for i, c in enumerate(BLUE_RAMP)], zmin=0, zmax=zmax,
    xgap=3, ygap=3, hoverongaps=False, showscale=False,
    customdata=[[n_cat[c]] * len(z.columns) for c in z.index],
    hovertemplate="%{y}: %{z:.0f}% of %{customdata:,} recalls mention %{x}<extra></extra>",
))
for cat, ylab in zip(z.index, ylabels):
    for h, xlab in zip(z.columns, xlabels):
        v = z.loc[cat, h]
        if v >= BLANK_BELOW:
            fig.add_annotation(x=xlab, y=ylab, text=f"{v:.0f}%", showarrow=False,
                               font=dict(size=12, color="white" if v > zmax * 0.5 else INK))
fig.update_xaxes(side="top", showgrid=False)
fig.update_yaxes(showgrid=False)
fig = style(fig, 80 + 44 * len(z))
fig.update_layout(margin=dict(t=60))
show(fig)
st.caption(f"% of each category's recalls mentioning the hazard, {FIRST_YEAR}–{LAST_YEAR}. Blank = under {BLANK_BELOW}%.")

st.space("large")

# ======================================================================
eyebrow("Finding 4")
st.header("In their own words")
st.markdown("I read 60 random records (30 recalls, 30 reports). Three things kept coming up.")
pct_recall_mention = meta["n_mention_recall"] / meta["n_incident_texts"] * 100

t1, t2, t3 = st.columns(3, gap="medium")
with t1.container(border=True, height="stretch"):
    st.markdown("##### Stuff catches fire")
    quote("The phone blew up and caught on fire.", "Report 20260305-EFE89")
    quote("Product wiring has caught in fire twice", "Report 20130429-065B2 · a stove")
with t2.container(border=True, height="stretch"):
    st.markdown("##### Stuff gives way")
    quote("The plastic hinge on it snapped", "Report 20250827-BF7E8 · a child carrier")
    quote("gave it a light tug … and the strap pulled off", "Report 20221205-3D459 · a ski helmet")
    st.caption("But: not every injury is a defect. “Onewheel ejected me when I tried to stop.”")
with t3.container(border=True, height="stretch"):
    st.markdown("##### Recalls don't end it")
    st.markdown(f"**1 in {round(100 / pct_recall_mention)}** of all {meta['n_incidents']:,} reports mention a recall.")
    quote("the recall did not cover my specific model.", "Report 20250827-BF7E8")
    quote("the recall replacement bolts … one bolt had unknowingly snapped", "Report 20231207-85207 · an office chair")

st.space("large")

# ======================================================================
eyebrow("What does this mean??")
st.header("Before you launch")
m1, m2, m3 = st.columns(3, gap="medium")
with m1.container(border=True, height="stretch"):
    st.markdown("##### 1 · Know your villain")
    st.markdown(f"Fire for electronics, {plain(h_t)} for toys, {plain(h_f)} for furniture. Test for that first.")
with m2.container(border=True, height="stretch"):
    st.markdown("##### 2 · Check the rules early")
    st.markdown(f"{reg_overall:.0f}% of recalls broke a standard that already existed. That's a free win.")
with m3.container(border=True, height="stretch"):
    st.markdown("##### 3 · Reports are not recalls")
    st.markdown(f"{most_reported} is {inc_pct[most_reported]:.0f}% of reports but {rec_pct[most_reported]:.0f}% of recalls. A pile of complaints isn't a recall, and a quiet category isn't a safe one.")

st.space("small")
st.page_link("views/check_product.py", label="**Try it with your product →**")

st.space("large")
st.caption("Data: CPSC · SaferProducts.gov, pulled 9/29/2026. Self-reported, not failure rates. Fine print in the Appendix.")
