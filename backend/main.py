"""
main.py

FastAPI entrypoint exposing the predictor as an API.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, Query
from typing import Optional

from models import init_db, get_session
from predictor import get_predictions

app = FastAPI(title="Counselling Predictor API")

engine = init_db()


@app.get("/")
def root():
    return {"status": "ok", "message": "Counselling Predictor API is running"}


@app.get("/predict")
def predict(
    percentile: Optional[float] = Query(None),
    rank: Optional[int] = Query(None),
    category: str = Query("General"),
    branch: Optional[str] = Query(None),
):
    session = get_session(engine)
    try:
        results = get_predictions(
            session,
            percentile=percentile,
            rank=rank,
            category=category,
            branch_name=branch,
        )
        # Convert tuple keys to a JSON-friendly structure
        formatted = [
            {"college": college, "branch": branch_name, "history": history}
            for (college, branch_name), history in results.items()
        ]
        return {"count": len(formatted), "results": formatted}
    finally:
        session.close()
