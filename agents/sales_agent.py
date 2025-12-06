# agents/sales_agent.py
from typing import Dict, Any, List

OFFERS = [
    {"id": "O1", "tier": "Standard", "max_amount": 200000, "rate": 14.0, "tenure_options": [36, 60]},
    {"id": "O2", "tier": "Silver", "max_amount": 350000, "rate": 12.0, "tenure_options": [48, 60, 84]},
    {"id": "O3", "tier": "Gold", "max_amount": 500000, "rate": 10.5, "tenure_options": [60, 84]},
]

def get_personalized_offers(applicant: Dict[str, Any]) -> List[Dict]:
    score = applicant.get("credit_score", 700)
    salary = applicant.get("salary", 30000)
    offers = []
    for o in OFFERS:
        # simple heuristics
        if score >= 750 or salary >= 80000:
            offers.append(o)
        elif score >= 700 and salary >= 40000 and o["max_amount"] <= 400000:
            offers.append(o)
        elif o["max_amount"] <= applicant.get("pre_approved_limit", 200000):
            offers.append(o)
    offers = sorted(offers, key=lambda x: x["max_amount"], reverse=True)
    return offers

def propose_offer(applicant: Dict):
    offers = get_personalized_offers(applicant)
    top = offers[0] if offers else {"max_amount": applicant.get("pre_approved_limit", 0), "rate": 12.0, "id": "fallback"}
    msg = f"Hi {applicant.get('name')}, based on your profile we can offer up to ₹{top['max_amount']} at {top.get('rate')}% p.a. Would you like to see EMI options?"
    return {"offers": offers, "top_offer": top, "message": msg}
