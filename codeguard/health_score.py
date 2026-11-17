"""Deterministic advisory code-health scores; not a security certification."""
from codeguard.issue_formatter import calculate_priority

PENALTIES = {"High": 15, "Medium": 7, "Low": 2, "Review": 7}


def score_file(review):
    if review.get("status") == "error" or any((review.get(c) or {}).get("status") == "error" for c in ("syntax", "quality", "security")):
        return None
    scores = {}
    for category in ("syntax", "quality", "security"):
        detail = review.get(category) or {}
        if category == "syntax":
            penalty = 25 if detail.get("status") == "failed" else 0
        else:
            penalty = sum(PENALTIES.get(calculate_priority(issue, category), 7) for issue in detail.get("issues", []))
        scores[category] = max(0, 100 - penalty)
    combined_penalty = sum(100 - score for score in scores.values())
    return {"overall": max(0, 100 - combined_penalty), **scores}


def score_review(result):
    per_file = [{"file": r.get("file", "Unknown"), "scores": score_file(r)} for r in result.get("reviews", [])]
    valid = [entry["scores"] for entry in per_file if entry["scores"] is not None]
    overall = round(sum(s["overall"] for s in valid) / len(valid), 1) if valid else None
    breakdown = {k: (round(sum(s[k] for s in valid) / len(valid), 1) if valid else None) for k in ("quality", "security", "syntax")}
    return {"overall": overall, **breakdown, "per_file": per_file, "policy": "100 minus 15/high, 7/medium, 2/low, 7/review and 25/syntax failure; clamp 0-100; mean of valid files. Analyzer errors are unscored."}
