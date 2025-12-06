# services/fraud_detection.py
def simple_doc_anomaly(pan_extracted: str, crm_pan: str):
    return pan_extracted is not None and crm_pan is not None and pan_extracted != crm_pan

def fraud_score_simple(verification: dict):
    """
    Return a simple fraud score 0-100 based on anomalies found in verification.
    """
    score = 0
    notes = verification.get("notes", [])
    if verification.get("status") != "PASSED":
        score += 30
    if verification.get("pan_extracted") and not verification.get("crm_match"):
        score += 20
    for n in notes:
        if "mismatch" in n.lower() or "anomaly" in n.lower():
            score += 15
    score = min(100, score)
    return {"score": score, "notes": notes}
