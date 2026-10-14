"""Build the small data files the dashboard reads.

Run from anywhere after the notebook has written Data/incidents_clean.csv and
Data/recalls_clean.csv:

    python dashboard/build_data.py

Writes to dashboard/data/ and saves the embedding model to dashboard/model/,
so the app never loads the 100 MB incident file or re-embeds 10,000 recalls.
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from model2vec import StaticModel

HERE = Path(__file__).resolve().parent
DATA_IN = HERE.parent / "Data"
OUT = HERE / "data"
MODEL_DIR = HERE / "model"
MODEL_NAME = "minishlab/potion-base-8M"

SEVERE = {"Injury, Hospital Admission", "Death"}


# ---------- product text for the "check your product" search ----------

# Cut points that end the product phrase in a recall title
_TITLE_END = re.compile(
    r"\s+(?:due to|because|after|posing|that could|which|sold (?:exclusively )?(?:at|by|on|through|online)|"
    r"recalled|repaired by|to repair|to replace)\b|[;(:]",
    re.I,
)


def product_phrase(title: str) -> str:
    """Pull the product out of a recall title, leaving out company and hazard.

    "Walmart Recalls Camp Axes Due to Injury Hazard" -> "Camp Axes"
    "Bicycle Pedals Recalled by Performance Inc. Due to Fall Hazard" -> "Bicycle Pedals"
    """
    t = re.sub(r"\(recall alert\)", "", title, flags=re.I).strip()
    m = re.match(r"(.*?)\s+recalled\b", t, re.I)
    if m:
        phrase = m.group(1)
    else:
        m = re.search(r"\brecall(?:s|ing)?\s+(?:to (?:repair|replace)\s+|of\s+)?(.*)$", t, re.I)
        phrase = m.group(1) if m else t
    phrase = _TITLE_END.split(phrase, maxsplit=1)[0]
    return phrase.strip(" ,.-") or t


def involves_sentence(summary) -> str:
    """The 'This recall involves ...' sentence, which describes the product."""
    if not isinstance(summary, str):
        return ""
    m = re.search(r"\b(?:this|the) recall (?:involves|includes)\s+(.*?)(?:\.\s|$)", summary, re.I | re.S)
    return m.group(1).strip()[:250] if m else ""


def fix_encoding(s):
    """The raw CSVs are Windows-1252 but were read as Latin-1, which turns curly quotes into
    invisible control characters ("Children\x92s"). Re-decode them."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("cp1252")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def split_hazards(s) -> list[str]:
    return [h.strip() for h in s.split(";")] if isinstance(s, str) and s.strip() else ["none stated"]


def main() -> None:
    OUT.mkdir(exist_ok=True)

    inc = pd.read_csv(
        DATA_IN / "incidents_clean.csv",
        usecols=["report_no", "category", "severity", "year", "hazards"],
    )
    rec = pd.read_csv(DATA_IN / "recalls_clean.csv", dtype={"recall_no": str})
    for col in ["title", "summary"]:
        rec[col] = rec[col].map(fix_encoding)
    print(f"Read {len(inc):,} incident reports and {len(rec):,} recalls")

    # 1. Counts by source, category and year
    counts = pd.concat([
        rec.groupby(["category", "year"]).size().rename("n").reset_index().assign(source="recalls"),
        inc.groupby(["category", "year"]).size().rename("n").reset_index().assign(source="incidents"),
    ])[["source", "category", "year", "n"]]
    counts.to_csv(OUT / "counts_by_category_year.csv", index=False)

    # 2. Severity by category (incident reports only; blank severity = not on the scale)
    sev = (
        inc.assign(has_sev=inc["severity"].notna(), severe=inc["severity"].isin(SEVERE))
        .groupby("category")
        .agg(n_reports=("report_no", "size"), n_with_severity=("has_sev", "sum"), n_severe=("severe", "sum"))
        .reset_index()
    )
    sev["pct_severe"] = (sev["n_severe"] / sev["n_with_severity"] * 100).round(1)
    sev.to_csv(OUT / "severity_by_category.csv", index=False)

    # 3. Hazard shares by category, recalls since 2011 and all incident reports
    def hazard_shares(df, source):
        d = df.assign(hz=df["hazards"].map(split_hazards))
        n_cat = d.groupby("category").size().rename("n_in_category")
        # Each record's tags are already unique, so a plain explode counts records per hazard
        long = d[["category", "hz"]].explode("hz")
        out = long.groupby(["category", "hz"]).size().rename("n_with_hazard").reset_index()
        out = out.join(n_cat, on="category").rename(columns={"hz": "hazard"})
        out["pct"] = (out["n_with_hazard"] / out["n_in_category"] * 100).round(1)
        return out.assign(source=source)

    rec_since = rec[rec["year"].between(2011, 2026)]
    hz = pd.concat([hazard_shares(rec_since, "recalls"), hazard_shares(inc, "incidents")])
    hz.to_csv(OUT / "hazards_by_category.csv", index=False)

    # 4. Recalls table for the search page, with the product text we embed
    rec["product_text"] = [
        (product_phrase(t) + ". " + involves_sentence(s)).strip(". ")
        for t, s in zip(rec["title"].fillna(""), rec["summary"])
    ]
    keep = ["recall_no", "title", "date", "year", "category", "category_conf", "hazards", "recall_url", "product_text"]
    rec[keep].to_csv(OUT / "recalls.csv", index=False)

    # 5. Embeddings (saved once; the app only embeds the user's query)
    model = StaticModel.from_pretrained(MODEL_NAME)
    model.save_pretrained(str(MODEL_DIR))
    emb = model.encode(rec["product_text"].tolist())
    emb = emb / np.clip(np.linalg.norm(emb, axis=1, keepdims=True), 1e-9, None)
    np.save(OUT / "recall_embeddings.npy", emb.astype(np.float32))

    # 6. How many incident reports talk about a recall (leaving out "I don't recall" style uses)
    text = pd.read_csv(DATA_IN / "incidents_clean.csv", usecols=["incident_text"])["incident_text"].dropna()
    mentions = text.str.contains(r"\brecall", case=False)
    verb_only = text.str.contains(r"\b(?:i|we|don'?t|do not|can'?t|cannot|didn'?t|did not)\s+recall\b", case=False) & ~text.str.contains(
        r"\b(?:a|the|this|that|safety|product|voluntary|on|under|any|no)\s+recall|\brecalls\b|\brecalled\b", case=False)
    n_recall_mentions = int((mentions & ~verb_only).sum())

    # 7. Who gets hurt by children's products: share of Baby + Toys reports (with an age) about a child under 5
    ages = pd.read_csv(DATA_IN / "incidents_clean.csv", usecols=["category", "victim_age"]).dropna()
    kids = ages[ages["category"].isin(["Baby", "Toys & Children"])]

    meta = {
        "model": MODEL_NAME,
        "n_incidents": int(len(inc)),
        "n_recalls": int(len(rec)),
        "incident_date_range": "2011-03 to 2026-09",
        "recall_date_max": str(rec["date"].max()),
        "n_incident_texts": int(len(text)),
        "n_mention_recall": n_recall_mentions,
        "kids_reports_with_age": int(len(kids)),
        "kids_under5_pct": round(float((kids["victim_age"] < 5).mean() * 100), 1),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))

    for f in sorted(OUT.iterdir()):
        print(f"  {f.name:32s} {f.stat().st_size / 1e6:6.2f} MB")


if __name__ == "__main__":
    main()
