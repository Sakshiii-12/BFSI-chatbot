# tests/test_utils.py
from agents.utils import calc_emi, decide_loan

def test_calc_emi_zero_rate():
    assert calc_emi(120000, 0, 12) == 10000.0

def test_decide_loan_reject_low_score():
    applicant = {"id": 99, "salary": 50000, "credit_score": 650, "pre_approved_limit": 100000}
    dec, details = decide_loan(applicant, 50000, 12, 60)
    assert details["final_decision"] == "REJECTED" or dec == "REJECTED"
