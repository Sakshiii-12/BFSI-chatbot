# agents/utils.py
import math, datetime, json, os
from pathlib import Path

def calc_emi(P: float, annual_rate_pct: float, tenure_months: int) -> float:
    if tenure_months <= 0:
        raise ValueError("tenure_months must be > 0")
    r = annual_rate_pct / 12.0 / 100.0
    n = tenure_months
    if r == 0:
        return round(P / n, 2)
    emi = P * r * (1 + r)**n / ((1 + r)**n - 1)
    return round(emi, 2)

def decide_loan(applicant: dict, requested_amount: float,
                annual_rate_pct: float = 12.0, tenure_months: int = 60):
    details = {}
    emi = calc_emi(requested_amount, annual_rate_pct, tenure_months)
    details["EMI"] = emi
    salary = applicant.get("salary") or 1
    details["EMI_pct_salary"] = round(100 * emi / salary, 2) if salary else 999.0
    credit_score = applicant.get("credit_score")
    pre_approved = applicant.get("pre_approved_limit", 0)

    rules_fired = []
    def push(txt):
        if txt not in rules_fired:
            rules_fired.append(txt)

    if credit_score is not None and credit_score < 700:
        push("Credit score below 700 → REJECT")
        decision = "REJECTED"
    elif requested_amount > 2 * pre_approved:
        push("Requested amount > 2× pre-approved → REJECT")
        decision = "REJECTED"
    elif requested_amount <= pre_approved:
        push("Requested amount ≤ pre-approved → Fast-path check")
        if details["EMI_pct_salary"] <= 50:
            push("EMI ≤ 50% of salary → APPROVE")
            decision = "APPROVED"
        else:
            push("EMI > 50% of salary → CONDITIONAL (require salary slip)")
            decision = "CONDITIONAL"
    elif requested_amount <= 2 * pre_approved:
        push("Requested amount ≤ 2× pre-approved → CONDITIONAL (salary slip required)")
        decision = "CONDITIONAL"
    else:
        push("Unhandled case → REJECT")
        decision = "REJECTED"

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    details["timestamp"] = utc_now.isoformat()
    details["rules_fired"] = rules_fired
    details["final_decision"] = decision
    details["requested_amount"] = requested_amount
    details["tenure_months"] = tenure_months
    details["annual_rate_pct"] = annual_rate_pct
    return decision, details

def save_decision_trace(trace: dict, path="outputs/decision_traces.jsonl"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace, ensure_ascii=False) + "\n")
