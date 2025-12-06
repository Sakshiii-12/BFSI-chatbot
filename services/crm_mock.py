# services/crm_mock.py
import json
from pathlib import Path

_KYC_DATA = None

def _load_data(path="data/kyc_data.json"):
    global _KYC_DATA
    if _KYC_DATA is None:
        p = Path(path)
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as f:
                    _KYC_DATA = json.load(f)
            except Exception:
                _KYC_DATA = {}
        else:
            _KYC_DATA = {}
    return _KYC_DATA

def get_kyc_for_id(applicant_id, path="data/kyc_data.json"):
    data = _load_data(path)
    k = str(applicant_id)
    return data.get(k)
