# services/credit_bureau.py
import random
import time

# Simple mock credit bureau client. Returns 600-850 score deterministically
# based on applicant id when possible.

def get_credit_score(applicant_id: int, applicant: dict = None):
    """
    Return a mock credit score between 600-850.
    If applicant has credit_score set, return that (priority).
    Otherwise, deterministic random based on id for reproducible demos.
    """
    if applicant and "credit_score" in applicant and applicant["credit_score"] is not None:
        return applicant["credit_score"]
    if applicant_id:
        random.seed(applicant_id)
        return random.randint(620, 820)
    random.seed(int(time.time()))
    return random.randint(600, 850)
