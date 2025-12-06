# agents/verification_agent.py
from services.crm_mock import get_kyc_for_id
from services.doc_intel import extract_pan, extract_large_number_as_salary

def verify_kyc(applicant: dict, provided_docs: dict = None):
    """
    Verification that uses CRM mock file (data/kyc_data.json) and doc intel.
    Returns status, notes, crm_record, doc_report.
    """
    notes = []
    crm_record = get_kyc_for_id(applicant.get("id"))
    if not applicant.get("phone"):
        notes.append("Missing phone in profile.")
    if not applicant.get("city") and not (crm_record and crm_record.get("address")):
        notes.append("Missing city/address information.")

    crm_match = bool(crm_record)
    if not crm_match:
        notes.append("CRM record not found — manual check suggested.")
    else:
        appl_phone = applicant.get("phone")
        crm_phone = crm_record.get("phone")
        if appl_phone and crm_phone and str(appl_phone) != str(crm_phone):
            notes.append("Phone mismatch with CRM record.")
        if not crm_record.get("verified"):
            notes.append("CRM record not flagged as verified.")

    doc_report = {}
    if provided_docs:
        pan_text = provided_docs.get("pan_text") or provided_docs.get("pan", "")
        salary_text = provided_docs.get("salary_text") or provided_docs.get("salary", "")
        pan = extract_pan(pan_text)
        salary_extracted = extract_large_number_as_salary(salary_text)
        if pan:
            doc_report["pan_extracted"] = pan
        if salary_extracted:
            doc_report["salary_extracted"] = salary_extracted

        if crm_record and crm_record.get("pan") and pan and crm_record.get("pan").upper() != pan.upper():
            notes.append("PAN mismatch with CRM record.")

    status = "PASSED" if not notes and crm_match else "REQUIRES_MANUAL"
    return {"status": status, "notes": notes, "crm_record": crm_record or {}, "doc_report": doc_report}
