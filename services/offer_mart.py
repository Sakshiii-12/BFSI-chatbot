# services/offer_mart.py
OFFERS = [
    {"id": "O1", "tier": "Standard", "max_amount": 200000, "rate": 14.0, "tenure_options": [36, 60]},
    {"id": "O2", "tier": "Silver", "max_amount": 350000, "rate": 12.0, "tenure_options": [48, 60, 84]},
    {"id": "O3", "tier": "Gold", "max_amount": 500000, "rate": 10.5, "tenure_options": [60, 84]},
]

def get_offers_for_applicant(applicant: dict):
    """
    Dynamically adjust offers: if salary high and credit score strong, boost Gold offer max_amount.
    """
    offers = []
    for o in OFFERS:
        copy = dict(o)
        if applicant.get("salary",0) >= 80000 and applicant.get("credit_score",0) >= 750:
            if copy["id"] == "O3":
                copy["max_amount"] = int(copy["max_amount"] * 1.2)
        offers.append(copy)
    return offers
