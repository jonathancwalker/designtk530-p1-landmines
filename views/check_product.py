"""Check your product: find the most similar past recalls and show what went wrong with them."""

import plotly.graph_objects as go
import streamlit as st

from common import plain, BLUE, FIRST_YEAR, INK_2, LAST_YEAR, RELATED, eyebrow, lede, load_tables, search, show, style

counts, severity, hazards, recalls, meta = load_tables()
K = 10
EXAMPLES = ["baby stroller", "space heater", "kids dresser with drawers", "lithium power bank", "hoverboard", "pressure cooker"]

st.title("Check your product")
lede("Type what you're building. See what went wrong for products like it.")

# filter first, then the search
first_year = int(recalls["year"].min())
f_col, _ = st.columns([2, 3])
min_year = f_col.slider("Only include recalls from", first_year, LAST_YEAR, first_year)

# search bar look: big label + tall input; examples small and quiet underneath
st.html("""<style>
.st-key-search input { font-size: 1.3rem !important; padding: 0.85rem 1rem !important; min-height: 3.4rem !important; }
.st-key-examples [data-testid="stWidgetLabel"] p { font-size: 0.8rem !important; color: #898781 !important; }
.st-key-examples button { min-height: 1.6rem !important; padding: 0.05rem 0.6rem !important; }
.st-key-examples button p { font-size: 0.78rem !important; }
</style>""")
st.html("<div style='font-size:1.6rem;font-weight:700;color:#0b0b0b;margin:0.8rem 0 0.2rem 0'>What are you building?</div>")

# ?q=... in the URL pre-fills the search, so a result can be shared as a link
query = st.text_input("What are you building?", value=st.query_params.get("q", ""), key="search",
                      placeholder="e.g. kids dresser with drawers", label_visibility="collapsed").strip()
example = st.pills("Or try an example", EXAMPLES, selection_mode="single", key="examples")
if not query and example:
    query = example

if not query:          # nothing typed yet: leave the page blank below the search bar
    st.stop()

results = search(query, min_year, k=K)
if results.empty:
    st.warning(f"No recalls from {min_year} on to compare against. Try an earlier year.")
    st.stop()

if results["similarity"].max() < RELATED:
    st.warning(
        f"Nothing really like “{query}” in the recall history. Closest stuff is below, but take it with a grain of salt. "
        "Try a more common name (*stroller*, not *pram*)."
    )

st.space("small")
st.header(f"What went wrong for the {len(results)} closest matches")

hz = results["hazard_list"].explode()
hz = hz[hz != "none stated"].value_counts().sort_values()
no_named = int(results["hazard_list"].map(lambda h: h == ["none stated"]).sum())

left, right = st.columns([3, 2], gap="large")
with left:
    if hz.empty:
        st.info("None of these name a specific hazard. Just 'injury hazard'.")
    else:
        fig = go.Figure(go.Bar(
            y=hz.index, x=hz.values, orientation="h", marker_color=BLUE,
            text=[f"{v} of {len(results)}" for v in hz.values], textposition="outside",
            textfont=dict(color=INK_2, size=12), cliponaxis=False,
            hovertemplate="%{y}: %{x} of " + str(len(results)) + " recalls<extra></extra>",
        ))
        fig.update_layout(bargap=0.35)
        fig.update_xaxes(title_text=f"of the {len(results)} closest recalls",
                         range=[0, max(hz.max() * 1.3, 1)], dtick=1 if hz.max() <= 10 else None)
        show(style(fig, 70 + 42 * len(hz)))
        if no_named:
            st.caption(f"{no_named} don't name a hazard. Some name more than one.")

with right:
    main_cat = results["category"].mode().iloc[0]
    with st.container(border=True):
        st.markdown(f"**Mostly {main_cat}.** Across that category:")
        cat_hz = hazards[(hazards["source"] == "recalls") & (hazards["category"] == main_cat)
                         & (hazards["hazard"] != "none stated")].nlargest(3, "pct")
        n_cat = int(cat_hz["n_in_category"].iloc[0]) if len(cat_hz) else 0
        for _, row in cat_hz.iterrows():
            st.markdown(f"- {row['pct']:.0f}% of recalls mention **{plain(row['hazard'])}**")
        sev = severity[severity["category"] == main_cat]
        if len(sev):
            s = sev.iloc[0]
            st.markdown(f"- {s['pct_severe']}% of reports were serious (hospital or death)")
        st.caption(f"{n_cat:,} recalls, {FIRST_YEAR}–{LAST_YEAR}. Categories are predicted.")

st.subheader("The matches")
st.dataframe(
    results[["closeness", "year", "title", "hazards", "recall_url"]],
    hide_index=True, width="stretch",
    column_config={
        "closeness": st.column_config.TextColumn("How close", width="small"),
        "year": st.column_config.NumberColumn("Year", format="%d", width="small"),
        "title": st.column_config.TextColumn("Recall", width="large"),
        "hazards": st.column_config.TextColumn("Hazards"),
        "recall_url": st.column_config.LinkColumn("CPSC page", display_text="Open"),
    },
)
st.caption(
    "Similar ≠ doomed. It's what tends to go wrong, so skim the titles to make sure they're actually like yours. "
    "How it works: Appendix."
)
