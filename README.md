# Counselling Predictor

A website to help students navigate the confusion of centralized admission counselling — combining an FAQ on how counselling rounds actually work with a percentile/rank-based predictor for likely colleges and branches.

## Problem

Counselling cutoffs shift unpredictably round to round. Students with a given percentile/rank often have no clear sense of which colleges and branches are realistically within reach, or how much movement to expect between rounds. This project aims to fix that with data-backed predictions and clear explanations of the process.

## Features (planned)

- [ ] FAQ section covering counselling round mechanics, document verification, seat acceptance/withdrawal, category/reservation rules, and common mistakes
- [ ] Percentile/rank-based predictor showing probable colleges and branches, with round-wise historical trends
- [ ] College detail pages: placements, infrastructure, branch strength, location
- [ ] Feedback loop for users to report actual outcomes and improve future predictions

## Tech Stack (in progress)

- **Backend:** Python (FastAPI)
- **Predictor logic:** pandas-based filtering over historical cutoff data
- **Data:** Scraped/compiled from official round-wise cutoff PDFs
- **Database:** SQLite (v1), Postgres later if needed
- **Frontend:** Streamlit (v1 prototype), React/Next.js (later)

## Project Structure

```
counselling-predictor/
├── data/
│   ├── raw/            # untouched source PDFs/CSVs
│   └── processed/      # cleaned data ready for DB load
├── scraper/
│   └── scrape_cutoffs.py
├── backend/
│   ├── main.py          # API/app entrypoint
│   ├── models.py        # DB schema
│   └── predictor.py     # core prediction logic
├── frontend/            # separate frontend, if/when split from backend
├── requirements.txt
└── README.md
```

## Status

🚧 Actively building — currently in the data collection phase.

## License

MIT
