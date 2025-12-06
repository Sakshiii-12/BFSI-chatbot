# agents/sanction_agent.py
import os
from services.report_generator import generate_exec_summary

def generate_sanction_pdf(applicant: dict, trace: dict, out_folder: str = "outputs/sanction_letters"):
    """
    Generate and return path to sanction letter PDF only if decision is APPROVED.
    Returns None otherwise.
    """
    decision = trace.get("decision_details", {}).get("final_decision")
    if decision != "APPROVED":
        return None

    os.makedirs(out_folder, exist_ok=True)
    # The report_generator expects the 'trace' first (based on your code)
    try:
        path = generate_exec_summary(trace, out_folder=out_folder)
        return path
    except Exception as e:
        # bubble up or return None — UI handles exceptions when reading file
        raise
