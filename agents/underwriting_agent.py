# agents/underwriting_agent.py
from agents.utils import decide_loan

class UnderwritingAgent:
    def __init__(self):
        pass

    def evaluate(self, applicant: dict, requested_amount: float, annual_rate_percent: float, tenure_months: int):
        """
        Returns a tuple: (decision_label, details_dict)
        details_dict format is produced by decide_loan(...)
        """
        return decide_loan(applicant, requested_amount, annual_rate_percent, tenure_months)
