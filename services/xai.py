# services/xai.py
def compute_risk_score(applicant: dict, details: dict):
    score = 50
    breakdown = {}
    credit = applicant.get("credit_score") or 700
    if credit < 700:
        penalty = (700 - credit) // 2
        score += penalty
        breakdown["credit_score"] = f"penalty {penalty}"
    else:
        bonus = (credit - 700) // 5
        score -= bonus
        breakdown["credit_score"] = f"bonus {bonus}"

    emi_pct = details.get("EMI_pct_salary", 999)
    if emi_pct > 50:
        score += 20
        breakdown["emi_pct_salary"] = "high EMI% penalty +20"
    elif emi_pct <= 20:
        score -= 10
        breakdown["emi_pct_salary"] = "low EMI% bonus -10"

    score = max(0, min(100, int(score)))
    breakdown["final_note"] = "lower is better (0 low risk)"
    return {"score": score, "breakdown": breakdown}

def counterfactual_salary_needed(applicant: dict, details: dict):
    """
    Return guessed salary needed to reach EMI_pct <= 50.
    EMI is fixed; salary_needed = EMI / 0.5
    """
    emi = details.get("EMI", 0)
    if emi <= 0:
        return None
    needed = int((emi / 0.5))
    return {"salary_needed": needed, "current_salary": applicant.get("salary")}
