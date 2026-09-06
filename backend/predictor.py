"""
predictor.py

Core prediction logic — kept independent of any UI/API layer so it can
be tested and reused directly.
"""

from sqlalchemy.orm import Session
from models import Cutoff, Branch, College


def get_predictions(
    session: Session,
    percentile: float = None,
    rank: int = None,
    category: str = "General",
    branch_name: str = None,
):
    """
    Return probable colleges/branches for a given percentile or rank,
    grouped by round, based on historical cutoff data.

    A student "probably" gets a seat where their percentile/rank was
    equal to or better than the historical cutoff for that round.
    """
    if percentile is None and rank is None:
        raise ValueError("Provide either percentile or rank.")

    query = (
        session.query(Cutoff, Branch, College)
        .join(Branch, Cutoff.branch_id == Branch.id)
        .join(College, Branch.college_id == College.id)
        .filter(Cutoff.category == category)
    )

    if branch_name:
        query = query.filter(Branch.name.ilike(f"%{branch_name}%"))

    if percentile is not None:
        query = query.filter(Cutoff.percentile <= percentile)
    else:
        query = query.filter(Cutoff.rank >= rank)

    results = query.all()

    predictions = {}
    for cutoff, branch, college in results:
        key = (college.name, branch.name)
        predictions.setdefault(key, []).append({
            "round": cutoff.round,
            "year": cutoff.year,
            "cutoff_rank": cutoff.rank,
            "cutoff_percentile": cutoff.percentile,
        })

    return predictions


if __name__ == "__main__":
    # Quick manual test scaffold — wire up a real session once the DB has data.
    print("predictor.py loaded — call get_predictions(session, percentile=..., category=...)")
