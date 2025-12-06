# agents/verification_agent.py

from services.crm_mock import get_kyc_for_id
from services.doc_intel import extract_pan, extract_large_number_as_salary
from services.fraud_detection import simple_doc_anomaly


class VerificationAgent:
    """
    Performs KYC verification using CRM data + uploaded salary slip/PAN text.
    Produces a verification report used by MasterAgent + Underwriting.
    """

    def __init__(self):
        pass

    def verify(self, applicant: dict, crm_record: dict, docs_payload: dict):
        """
        applicant      -> dict with id, name, salary, etc.
        crm_record     -> CRM KYC details (PAN, phone, address, salary)
        docs_payload   -> {"pan_text": "...", "salary_text": "..."} or {}

        Returns:
            {
              "status": "PASSED" | "FAILED",
              "crm_record": {...},
              "pan_extracted": "...",
              "crm_match": True/False,
              "salary_extracted": number or None,
              "notes": [...]
            }
        """
        if crm_record is None:
            crm_record = {}

        notes = []
        pan_extracted = None
        salary_extracted = None
        crm_match = True

        # --- PAN extraction from uploaded docs ---
        if docs_payload:
            pan_text = docs_payload.get("pan_text", "")
            if pan_text:
                pan_extracted = extract_pan(pan_text)
                if pan_extracted:
                    notes.append(f"Extracted PAN: {pan_extracted}")

        # --- Salary extraction from uploaded documents ---
        if docs_payload:
            salary_text = docs_payload.get("salary_text", "")
            if salary_text:
                salary_extracted = extract_large_number_as_salary(salary_text)
                if salary_extracted:
                    notes.append(f"Extracted salary: {salary_extracted}")

        # --- Compare PAN with CRM ---
        crm_pan = crm_record.get("pan")
        if pan_extracted and crm_pan:
            if pan_extracted != crm_pan:
                crm_match = False
                notes.append("PAN mismatch between document and CRM")
            else:
                notes.append("PAN matches CRM")

        # --- Fraud anomaly detection ---
        if simple_doc_anomaly(pan_extracted, crm_pan):
            notes.append("Fraud anomaly detected")

        # --- Decide PASS/FAIL ---
        status = "PASSED"
        if crm_match is False:
            status = "FAILED"

        return {
            "status": status,
            "crm_record": crm_record,
            "pan_extracted": pan_extracted,
            "crm_match": crm_match,
            "salary_extracted": salary_extracted,
            "notes": notes
        }
