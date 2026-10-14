"""What I'd test next: the A/B test proposal, and how well the category prediction holds up on unseen examples."""

import json

import plotly.graph_objects as go
import streamlit as st

from common import BLUE, DATA, INK_2, lede, load_tables, overall_hazard_share, show, style

counts, severity, hazards, recalls, meta = load_tables()
reg = overall_hazard_share(hazards, "recalls").get("regulatory violation", 0)
val = json.loads((DATA / "validation.json").read_text())

st.title("Does seeing past recalls actually help?")
lede("Will the horse drink if we lead it to the water?")

a, b = st.columns(2, gap="medium")
with a.container(border=True, height="stretch"):
    st.markdown("##### A · Today")
    st.markdown("A company sends its new product to a testing lab. Normal process.")
with b.container(border=True, height="stretch"):
    st.markdown("##### B · With past recalls")
    st.markdown("Same thing, plus a panel of the closest past recalls and their hazards (aka the *Check your product* tab).")

st.html(
    "<div style='border-left:4px solid #2a78d6;padding:0.4rem 0 0.4rem 1.1rem;margin:1.2rem 0;max-width:52rem'>"
    "<div class='eyebrow' style='margin-bottom:0.3rem'>The bet</div>"
    "<div style='font-size:1.5rem;font-weight:600;line-height:1.35;color:#0b0b0b'>"
    "Showing companies past recalls for similar products will lead to more products passing safety review the "
    "first time, because they can fix known problems early.</div></div>"
)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown(
        """
**Who** · Small and mid-sized companies, randomly put in A or B (by company), both running at the same time.

**Measure** · Passed review on the first try, within 90 days. Sign-ups stop 90 days before results, so everyone gets the full window.

**Worth it if** · ~10 more first-time passes per 100 (60 → 70).
"""
    )
with c2:
    st.markdown(
        """
**Watch out for** · Days to clearance. B could help pass rates but slow launches if teams get lost in old recalls.

**Could fool me** · Reviewers knowing who got B (keep them blind). A companies finding the recalls anyway (so the result is a minimum).

**If B wins** · Check the groups matched and it's not one category. Adopt B if it doesn't slow things down; rethink if only the people who opened the panel improved.
"""
    )

st.subheader("Why not just look at the data?")
st.markdown(
    f"Because companies pick themselves. The careful ones probably look up past recalls more *and* already ship safer "
    f"products, so comparing lookers to non-lookers would just measure carefulness. Randomly assigning who sees the "
    f"panel is the only clean way to tell whether the recalls themselves help ({reg:.0f}% of recalls broke a rule "
    f"that already existed, so there's room to help)."
)
st.markdown(
    "Two honest caveats: this kicks in late (a team that catches a hazard might need more than 90 days to redesign, "
    "so version 2 would show the panel at the design stage), and it might not hold for big companies with their own "
    "safety teams."
)

st.space("large")

# ======================================================================
st.header("How well does the prediction do on stuff it's never seen?")
st.markdown("Recalls don't come with a category, so the tool guesses one. Before trusting it, I tested it on examples "
            "it never trained on.")

r, n, h = val["random"], val["newest"], val["hand_check"]
m1, m2, m3 = st.columns(3)
with m1.container(border=True):
    st.metric("right on random reports it never saw", f"{r['accuracy']:.0f}%")
    st.caption(f"{r['n_test']:,} held-out incident reports")
with m2.container(border=True):
    st.metric("right on the newest reports", f"{n['accuracy']:.0f}%")
    st.caption(f"Trained on 2011–2023, tested on {n['n_test']:,} reports from 2024–26")
with m3.container(border=True):
    st.metric("right on recalls I checked by hand", f"{h['pct']:.0f}%")
    st.caption(f"{h['right']} of {h['n']}, so realistically {h['ci_low']}–{h['ci_high']}%")

f1 = dict(sorted(n["f1_by_category"].items(), key=lambda kv: kv[1]))
SHORT = {"Furniture, Furnishings & Decorations": "Furniture", "Home Maintenance and Structures": "Home maintenance",
         "Sports and Recreation": "Sports & rec", "Clothing and Accessories": "Clothing",
         "Fuel, Lighters and Fireworks": "Fuel, lighters & fireworks", "Products at Public Facilities": "Public facilities"}
labels = [SHORT.get(c, c) for c in f1]
fig = go.Figure(go.Bar(
    y=labels, x=list(f1.values()), orientation="h", marker_color=BLUE,
    text=[f"{v:.2f}" for v in f1.values()], textposition="outside", textfont=dict(color=INK_2, size=12), cliponaxis=False,
    customdata=[n["n_test_by_category"].get(c, 0) for c in f1],
    hovertemplate="%{y}: F1 %{x:.2f} (%{customdata:,} test reports)<extra></extra>",
))
fig.update_layout(bargap=0.3)
fig.update_xaxes(range=[0, 1.12], title_text="F1 on the newest reports (1 = always right)")
show(style(fig, 470))
st.caption("By category, on the 2024–26 reports. Weakest where there's little training data (public facilities, hobby).")

st.markdown(
    "**Next check:** compare against CPSC's own recall labels (their recall API has product type and hazard) on "
    "~200 recalls, category by category. That's the real test, since recall text reads differently from consumer reports."
)
