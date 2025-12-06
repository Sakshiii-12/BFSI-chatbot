# agents/underwriting_agent.py
from agents.utils import decide_loan

def evaluate(applicant, requested_amount, annual_rate_pct=12.0, tenure_months=60):
    decision, details = decide_loan(applicant, requested_amount, annual_rate_pct, tenure_months)
    return {"decision": decision, "details": details}
