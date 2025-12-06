# agents/utils.py
import math
from datetime import datetime

def calc_emi(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    """
    Calculate monthly EMI. If annual_rate_percent == 0 -> simple division.
    Returns EMI rounded to 2 decimal places.
    """
    try:
        principal = float(principal)
        r = float(annual_rate_percent)
        n = int(tenure_months)
    except Exception:
        raise ValueError("Invalid inputs for EMI calculation")

    if n <= 0:
        raise ValueError("Tenure must be positive months")
    if r == 0:
        emi = principal / n
        return round(emi, 2)

    monthly_rate = (r / 100.0) / 12.0
    emi = principal * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)
    return round(emi, 2)


def decide_loan(applicant: dict, requested_amount: float, annual_rate_percent: float, tenure_months: int):
    """
    Underwriting decision logic matching the problem statement:
    - If credit_score < 700 -> REJECT
    - If requested_amount <= pre_approved_limit -> APPROVED
    - If requested_amount <= 2 * pre_approved_limit:
        -> If salary missing -> CONDITIONAL (salary_slip_required)
        -> Else compute EMI and EMI_pct_salary (EMI / salary_monthly * 100)
           If EMI_pct_salary <= 50 -> APPROVED
           Else -> REJECT
    - If requested_amount > 2 * pre_approved_limit -> REJECT

    Returns: (decision_label, details_dict)
    details_dict contains keys: final_decision, EMI, EMI_pct_salary, requested_amount, rules_fired, timestamp
    """
    rules_fired = []
    ts = datetime.utcnow().isoformat()
    pre_limit = applicant.get("pre_approved_limit", 0) or 0
    credit_score = applicant.get("credit_score", None)
    salary = applicant.get("salary", None)  # expected monthly salary (document your dataset to be monthly)

    requested_amount = float(requested_amount)
    emi = calc_emi(requested_amount, annual_rate_percent, tenure_months)

    emi_pct_salary = None
    if salary and salary > 0:
        try:
            emi_pct_salary = round((emi / float(salary)) * 100.0, 2)
        except Exception:
            emi_pct_salary = None

    # Rule: credit score
    if credit_score is not None and credit_score < 700:
        rules_fired.append("credit_score_below_700 -> REJECT")
        details = {
            "timestamp": ts,
            "final_decision": "REJECTED",
            "requested_amount": requested_amount,
            "EMI": emi,
            "EMI_pct_salary": emi_pct_salary,
            "rules_fired": rules_fired
        }
        return "REJECTED", details

    # Rule: within pre-approved limit
    if requested_amount <= pre_limit:
        rules_fired.append("requested <= pre_approved_limit -> APPROVE")
        details = {
            "timestamp": ts,
            "final_decision": "APPROVED",
            "requested_amount": requested_amount,
            "EMI": emi,
            "EMI_pct_salary": emi_pct_salary,
            "rules_fired": rules_fired
        }
        return "APPROVED", details

    # Rule: <= 2x pre-approved -> require salary slip and EMI <= 50% salary
    if requested_amount <= (2 * pre_limit):
        rules_fired.append("requested <= 2x pre_approved_limit -> require_salary_slip")
        # If salary not present, we cannot compute EMI% -> conditional/manual
        if not salary:
            details = {
                "timestamp": ts,
                "final_decision": "CONDITIONAL",
                "requested_amount": requested_amount,
                "EMI": emi,
                "EMI_pct_salary": emi_pct_salary,
                "reason": "salary_slip_required",
                "rules_fired": rules_fired
            }
            return "CONDITIONAL", details

        # With salary present, check EMI% <= 50
        if emi_pct_salary is not None and emi_pct_salary <= 50.0:
            rules_fired.append("emi_within_50pct_salary -> APPROVE")
            details = {
                "timestamp": ts,
                "final_decision": "APPROVED",
                "requested_amount": requested_amount,
                "EMI": emi,
                "EMI_pct_salary": emi_pct_salary,
                "rules_fired": rules_fired
            }
            return "APPROVED", details
        else:
            rules_fired.append("emi_above_50pct_salary -> REJECT")
            details = {
                "timestamp": ts,
                "final_decision": "REJECTED",
                "requested_amount": requested_amount,
                "EMI": emi,
                "EMI_pct_salary": emi_pct_salary,
                "rules_fired": rules_fired
            }
            return "REJECTED", details

    # Rule: over 2x pre-approved -> reject
    rules_fired.append("requested > 2x pre_approved_limit -> REJECT")
    details = {
        "timestamp": ts,
        "final_decision": "REJECTED",
        "requested_amount": requested_amount,
        "EMI": emi,
        "EMI_pct_salary": emi_pct_salary,
        "rules_fired": rules_fired
    }
    return "REJECTED", details
