# chat/nlu.py
import re

def detect_intent(text: str):
    """
    Very small NLU:
    - request_amount -> extracts first large numeric (>=1000)
    - loan_reason -> matches words like 'medical', 'wedding', etc.
    - clear -> 'clear' or 'reset'
    - fallback -> unknown
    """
    if not text:
        return {"intent":"fallback"}

    t = text.lower()
    if any(k in t for k in ["clear", "reset", "start over"]):
        return {"intent":"clear"}
    # reason
    for kw in ["medical", "wedding", "education", "home", "travel"]:
        if kw in t:
            return {"intent":"loan_reason", "reason": kw}
    # extract number >= 1000
    m = re.search(r"(\d{3,9})", t.replace(",", ""))
    if m:
        try:
            amt = int(m.group(1))
            if amt >= 1000:
                return {"intent":"request_amount", "amount": amt}
        except:
            pass
    return {"intent":"fallback"}
