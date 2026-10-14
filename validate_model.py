"""How well does the recall-category model do on examples it never saw?

Same model as the notebook (TF-IDF + logistic regression on product description + the start of the
incident story), tested two ways:
  1. random: hold out 20% of incident reports at random
  2. newest: train on 2011-2023 reports, test on 2024-2026 (does it hold up on newer products?)
Plus the hand check of 40 recalls from the notebook, with a 95% Wilson interval.

    python dashboard/validate_model.py   ->  dashboard/data/validation.json
"""

import json
from math import sqrt
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
HAND_RIGHT, HAND_N = 33, 40   # notebook: hand check of 40 sampled recalls


def fit_and_score(train, test):
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=3, sublinear_tf=True)
    clf = LogisticRegression(C=10, max_iter=300, class_weight="balanced")
    clf.fit(vec.fit_transform(train["text"]), train["category"])
    pred = clf.predict(vec.transform(test["text"]))
    per_cat = f1_score(test["category"], pred, average=None, labels=sorted(test["category"].unique()))
    return {
        "n_train": int(len(train)), "n_test": int(len(test)),
        "accuracy": round(float(accuracy_score(test["category"], pred)) * 100, 1),
        "macro_f1": round(float(f1_score(test["category"], pred, average="macro")), 3),
        "f1_by_category": {c: round(float(f), 3) for c, f in zip(sorted(test["category"].unique()), per_cat)},
        "n_test_by_category": test["category"].value_counts().to_dict(),
    }


def wilson(k, n, z=1.96):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round((centre - half) * 100), round((centre + half) * 100)


def main():
    df = pd.read_csv(HERE.parent / "Data" / "incidents_clean.csv",
                     usecols=["product_desc", "incident_text", "category", "year"]).dropna(subset=["category"])
    df["text"] = df["product_desc"].fillna("") + " . " + df["incident_text"].fillna("").str[:400]

    tr, te = train_test_split(df, test_size=0.2, random_state=0, stratify=df["category"])
    random_split = fit_and_score(tr, te)
    newest_split = fit_and_score(df[df["year"] <= 2023], df[df["year"] >= 2024])

    lo, hi = wilson(HAND_RIGHT, HAND_N)
    out = {
        "random": random_split,
        "newest": newest_split,
        "hand_check": {"right": HAND_RIGHT, "n": HAND_N, "pct": round(HAND_RIGHT / HAND_N * 100, 1), "ci_low": lo, "ci_high": hi},
    }
    (HERE / "data" / "validation.json").write_text(json.dumps(out, indent=2))
    print(f"random: {random_split['accuracy']}% | newest: {newest_split['accuracy']}% "
          f"(train {newest_split['n_train']:,}, test {newest_split['n_test']:,}) | hand check {HAND_RIGHT}/{HAND_N} ({lo}-{hi}%)")


if __name__ == "__main__":
    main()
