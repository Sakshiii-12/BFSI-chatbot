# services/doc_intel.py
import re
PAN_RE = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", re.I)
MONEY_RE = re.compile(r"\b(?:Rs\.?|INR)?\s?([0-9]{1,3}(?:[,0-9]{3})*(?:\.\d{1,2})?)\b")

def extract_pan(text: str):
    if not text:
        return None
    m = PAN_RE.search(text)
    if m:
        return m.group(1).upper()
    return None

def extract_large_number_as_salary(text: str):
    if not text:
        return None
    nums = []
    for n in MONEY_RE.findall(text):
        try:
            nums.append(float(n.replace(",", "")))
        except:
            pass
    if not nums:
        return None
    return max(nums)
