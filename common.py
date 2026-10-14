"""Shared data loading, styling, chart helpers and search for the dashboard pages."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from model2vec import StaticModel
from sklearn.feature_extraction.text import TfidfVectorizer

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
MODEL_DIR = HERE / "model"
ASSETS = HERE / "assets"

# ---------- palette (validated default; blue/orange pass the CVD + contrast checks) ----------
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE = "#2a78d6"     # recalls
ORANGE = "#eb6834"   # incident reports
SMALL_N = "#c3c2b7"  # bars resting on too few reports
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

FIRST_YEAR, LAST_YEAR = 2011, 2026     # window the two sources share
LAST_FULL_YEAR = 2025
PARTIAL_YEAR_NOTE = "2026 runs Jan–Sep"

CSS = """
<style>
/* readable line length for prose; charts keep the full column */
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { font-size: 1.02rem; line-height: 1.6; max-width: 46rem; }
[data-testid="stCaptionContainer"] p { max-width: 46rem; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { font-size: 2.6rem !important; line-height: 1.15 !important; font-weight: 650; }
h1 { letter-spacing: -0.02em; }
h2 { letter-spacing: -0.01em; padding-top: 0.2rem; }
.eyebrow { color: #2a78d6; font-size: 1.2rem; font-weight: 700; letter-spacing: 0.01em; margin-bottom: -0.5rem; }
.lede { font-size: 1.2rem !important; color: #52514e; line-height: 1.55; max-width: 48rem; }
.ef { display: grid; grid-template-columns: auto 1fr; gap: 0.25rem 0.75rem; padding: 0.75rem 1rem; border-radius: 0.5rem;
      background: #f3f2ee; margin: 0.5rem 0 1rem 0; max-width: 46rem; font-size: 0.95rem; }
.ef b { color: #52514e; font-weight: 600; }
.big-claim { font-size: 2.1rem !important; font-weight: 700; line-height: 1.2 !important; letter-spacing: -0.01em;
             color: #0b0b0b; margin: 0.4rem 0 0.8rem 0; max-width: 38rem !important; }
.big-verdict { font-size: 1.5rem !important; font-weight: 600; color: #52514e; margin: 0; }
.quote { border-left: 3px solid #c3c2b7; padding: 0.15rem 0 0.15rem 0.9rem; margin: 0.6rem 0; color: #0b0b0b; font-size: 0.98rem; }
.quote small { display: block; color: #898781; font-size: 0.8rem; margin-top: 0.15rem; }
</style>
"""


def inject_css() -> None:
    st.html(CSS)


def eyebrow(text: str) -> None:
    st.html(f'<div class="eyebrow">{text}</div>')


def lede(text: str) -> None:
    st.html(f'<p class="lede">{text}</p>')


def expected_found(expected: str, found: str) -> None:
    st.html(f'<div class="ef"><b>I expected</b><span>{expected}</span><b>I found</b><span>{found}</span></div>')


def quote(text: str, ref: str) -> None:
    st.html(f'<div class="quote">“{text}”<small>{ref}</small></div>')


# ---------- charts ----------
def style(fig: go.Figure, height: int, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=24, t=48 if legend else 16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK_2, size=13),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, color=INK, size=13)),
        showlegend=legend,
        legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom", title_text="", font_color=INK_2),
        barcornerradius=4,
    )
    axes = dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, automargin=True,
                tickfont=dict(color=INK_2, size=12), title_font_color=INK_2)
    fig.update_xaxes(**axes)
    fig.update_yaxes(**axes)
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


def dumbbell(rows: list[str], a: pd.Series, b: pd.Series, a_name: str, b_name: str, x_title: str,
             height: int) -> go.Figure:
    """One row per item, two dots joined by a line. The gap between the dots is the story."""
    fig = go.Figure()
    xs, ys = [], []
    for r in rows:
        xs += [a[r], b[r], None]
        ys += [r, r, None]
    fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=AXIS, width=2), hoverinfo="skip", showlegend=False)
    fig.add_scatter(x=[a[r] for r in rows], y=rows, mode="markers", name=a_name,
                    marker=dict(size=11, color=BLUE, line=dict(color="white", width=2)),
                    hovertemplate="%{y}<br>%{x:.1f}% of " + a_name.lower() + "<extra></extra>")
    fig.add_scatter(x=[b[r] for r in rows], y=rows, mode="markers", name=b_name,
                    marker=dict(size=11, color=ORANGE, line=dict(color="white", width=2)),
                    hovertemplate="%{y}<br>%{x:.1f}% of " + b_name.lower() + "<extra></extra>")
    fig.update_xaxes(title_text=x_title, ticksuffix="%", rangemode="tozero")
    fig.update_yaxes(showgrid=False)
    return style(fig, height, legend=True)


# Hazard tags as they read in a sentence
PLAIN = {
    "fire / burn": "fire and burns",
    "electric shock": "electric shock",
    "laceration / cut": "cuts",
    "choking / ingestion": "choking and swallowing",
    "strangulation / entrapment": "strangulation and entrapment",
    "suffocation": "suffocation",
    "fall / tip-over": "falls and tip-overs",
    "drowning": "drowning",
    "poison / chemical / lead": "poisoning, chemicals and lead",
    "explosion / rupture": "explosions",
    "crash / impact": "crashes and impacts",
    "mechanical failure / breakage": "parts breaking",
    "regulatory violation": "broken safety standards",
}


def plain(hazard: str) -> str:
    return PLAIN.get(hazard, hazard)


def split_hazards(s) -> list[str]:
    return [h.strip() for h in s.split(";")] if isinstance(s, str) and s.strip() else ["none stated"]


# ---------- data ----------
@st.cache_data
def load_tables():
    counts = pd.read_csv(DATA / "counts_by_category_year.csv")
    severity = pd.read_csv(DATA / "severity_by_category.csv")
    hazards = pd.read_csv(DATA / "hazards_by_category.csv")
    recalls = pd.read_csv(DATA / "recalls.csv", dtype={"recall_no": str})
    recalls["hazard_list"] = recalls["hazards"].map(split_hazards)
    meta = json.loads((DATA / "meta.json").read_text())
    return counts, severity, hazards, recalls, meta


def overall_hazard_share(hazards: pd.DataFrame, source: str) -> pd.Series:
    """% of all records (across categories) in a source that mention each hazard."""
    h = hazards[hazards["source"] == source]
    total = h.groupby("category")["n_in_category"].first().sum()
    return h.groupby("hazard")["n_with_hazard"].sum() / total * 100


# ---------- search ----------
CLOSE, RELATED = 0.75, 0.55   # embedding similarity cut-offs, set from test queries


@st.cache_resource
def load_search():
    _, _, _, recalls, _ = load_tables()
    model = StaticModel.from_pretrained(str(MODEL_DIR))
    emb = np.load(DATA / "recall_embeddings.npy")
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    X = vec.fit_transform(recalls["product_text"].fillna(""))
    return model, emb, vec, X


def similarities(query: str) -> tuple[np.ndarray, np.ndarray]:
    """Embedding and keyword (TF-IDF) similarity of every recall to the query."""
    model, emb, vec, X = load_search()
    q = model.encode([query])[0]
    q = q / max(np.linalg.norm(q), 1e-9)
    return emb @ q, (X @ vec.transform([query]).T).toarray().ravel()


def search(query: str, min_year: int, k: int = 10) -> pd.DataFrame:
    """Rank recalls by a 50/50 blend of embedding and keyword similarity.

    Embeddings catch different wording (hoverboard ~ self-balancing scooter); keywords
    catch exact product names the small embedding model blurs (power bank, teething toy).
    """
    _, _, _, recalls, _ = load_tables()
    sim_emb, sim_kw = similarities(query)
    out = recalls.assign(similarity=sim_emb, score=0.5 * sim_emb + 0.5 * sim_kw)
    out = out[out["year"] >= min_year].nlargest(k, "score")
    out["closeness"] = np.select(
        [out["similarity"] >= CLOSE, out["similarity"] >= RELATED],
        ["Very similar", "Similar"],
        default="Loosely related",
    )
    return out
