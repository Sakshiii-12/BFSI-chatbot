# tests/test_underwriting.py
from agents.utils import calc_emi, decide_loan

def test_calc_emi_zero_rate():
    assert calc_emi(120000, 0, 12) == 10000.0

def test_reject_low_credit_score():
    applicant = {"id": 99, "salary": 50000, "credit_score": 650, "pre_approved_limit": 100000}
    dec, details = decide_loan(applicant, 50000, 12, 60)
    assert details["final_decision"] == "REJECTED"

def test_approve_within_preapproval():
    applicant = {"id": 1, "salary": 70000, "credit_score": 750, "pre_approved_limit": 150000}
    dec, details = decide_loan(applicant, 120000, 12, 60)
    assert details["final_decision"] == "APPROVED"

def test_conditional_requires_salary_slip():
    applicant = {"id": 2, "credit_score": 750, "pre_approved_limit": 100000}
    dec, details = decide_loan(applicant, 150000, 12, 60)
    assert details["final_decision"] == "CONDITIONAL"
