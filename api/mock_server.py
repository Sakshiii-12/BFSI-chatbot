# api/mock_server.py
from flask import Flask, jsonify
import json
from pathlib import Path

app = Flask("mock_api")

DEMO_PATH = Path("data/demo_customers.json")
KYC_PATH = Path("data/kyc_data.json")

@app.route("/credit-score/<int:cid>")
def credit_score(cid):
    if DEMO_PATH.exists():
        customers = json.loads(DEMO_PATH.read_text(encoding="utf-8"))
        for c in customers:
            if c["id"] == cid:
                return jsonify({"score": c.get("credit_score", 700)})
    return jsonify({"score": 700})

@app.route("/crm/<int:cid>")
def crm_lookup(cid):
    if KYC_PATH.exists():
        data = json.loads(KYC_PATH.read_text(encoding="utf-8"))
        return jsonify(data.get(str(cid), {}))
    return jsonify({})

@app.route("/offer-mart")
def offer_mart():
    from services.offer_mart import OFFERS
    return jsonify({"offers": OFFERS})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
