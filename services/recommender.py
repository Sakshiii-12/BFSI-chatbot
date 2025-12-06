# services/recommender.py
def recommend_offers(applicant, offers):
    """
    Rank offers with a score combining max_amount and inverse of rate.
    """
    score = applicant.get("credit_score", 700) or 700
    def score_fn(o):
        base = o["max_amount"] - (o["rate"] * 1000)
        if score >= 750:
            base += 50000
        return base
    return sorted(offers, key=score_fn, reverse=True)
