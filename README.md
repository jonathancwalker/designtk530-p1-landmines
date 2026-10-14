# Product Safety Explorer (dashboard)

Streamlit dashboard for DESIGNTK530 Project 1. It presents the whole project, in three pages:

- **The story**: one scrolling page from the question, through five findings (trend, where, how serious, what goes wrong, and the text analysis), to what a product team should do, the proposed A/B test, and limits and next steps.
- **Check your product**: type a product description and see the most similar past recalls and what went wrong with them.
- **Data & methods**: sources, cleaning, the recall category classifier, hazard tagging, how the search works (with a live comparison of methods) and how the dashboard design changed.

To add the screen-recorded walkthrough, save it as `dashboard/assets/walkthrough.mp4`; it shows up on the story and methods pages automatically.

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
```

## How the search works

Each recall's product (pulled from its title plus its "This recall involves..." sentence, leaving out the company
and the hazard) is embedded once with the [model2vec](https://github.com/MinishLab/model2vec) `potion-base-8M` model.
A query is ranked by a 50/50 blend of embedding similarity and TF-IDF keyword similarity: embeddings catch different
wording (hoverboard ~ self-balancing scooter), keywords catch exact product names. If nothing scores above 0.55
embedding similarity, the page says there's no close match. Everything runs locally; no text is sent anywhere.
