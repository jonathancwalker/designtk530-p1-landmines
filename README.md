# Know the Landmines (dashboard)

**Live:** https://designtk530-p1-landmines.streamlit.app/

Streamlit dashboard for DESIGNTK530 Project 1. It presents the whole project in six tabs:

- **The story**: the question, my hypothesis, four findings (recalls aren't going down; three lists that don't match; every product has its own villain; what people write) and what it means for a product team.
- **Check your product**: type what you're building and see the most similar past recalls and what went wrong with them.
- **What I'd test next**: the A/B test proposal, plus how well the category prediction holds up on examples it never saw.
- **AI critique**: what an AI tool said about the project, and what I took from it.
- **Appendix**: explore the trend with filters, the full charts, data, cleaning, methods, design changes and limits.
- **Video walkthrough**: a ~4-minute screen recording of the dashboard.

The walkthrough video lives at `assets/walkthrough.mp4` (compressed to 1080p H.264 so it streams in any browser).

## Run it

From the `P1` folder:

```bash
python -m venv .venv && source .venv/bin/activate      # skip if you already have the P1 venv
pip install -r dashboard/requirements.txt
cd dashboard
streamlit run app.py
```

It opens at http://localhost:8501. Run it from inside `dashboard/` so the theme in `.streamlit/config.toml` is picked up.

A search can be shared as a link: `http://localhost:8501/check_product?q=space%20heater`.

## Rebuilding the data

The app reads small pre-built files in `dashboard/data/` and the embedding model in `dashboard/model/`.
To rebuild them after re-running the notebook (which writes `Data/incidents_clean.csv` and `Data/recalls_clean.csv`):

```bash
python dashboard/build_data.py
python dashboard/validate_model.py   # the 'never seen' check on the test-next tab
```

## How the search works

Each recall's product (pulled from its title plus its "This recall involves..." sentence, leaving out the company
and the hazard) is embedded once with the [model2vec](https://github.com/MinishLab/model2vec) `potion-base-8M` model.
A query is ranked by a 50/50 blend of embedding similarity and TF-IDF keyword similarity: embeddings catch different
wording (hoverboard ~ self-balancing scooter), keywords catch exact product names. If nothing scores above 0.55
embedding similarity, the page says there's no close match. Everything runs locally; no text is sent anywhere.
