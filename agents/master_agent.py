# agents/master_agent.py
import os, json
from agents.sales_agent import propose_offer
from agents.verification_agent import verify_kyc
from agents.underwriting_agent import evaluate
from agents.sanction_agent import generate_sanction_pdf
from agents.utils import save_decision_trace

class MasterAgent:
    def __init__(self, ab_variant="A"):
        self.ab_variant = ab_variant

    def start_chat(self, applicant, requested_amount,
                   annual_rate_pct=12.0, tenure_months=60,
                   out_folder="outputs", docs_payload=None, session_id=None, transcript=None):
        """
        Orchestrates Sales -> Verification -> Underwriting -> Sanction -> Trace saving
        Returns: (decision, trace, pdf_path_or_None)
        """
        # Sales
        offer_ctx = propose_offer(applicant)

        # Verification
        verification = verify_kyc(applicant, provided_docs=docs_payload)

        # Underwriting
        uw = evaluate(applicant, requested_amount, annual_rate_pct, tenure_months)
        decision = uw["details"]["final_decision"]

        # Optional doc-intel & XAI placeholders
        doc_report = verification.get("doc_report", {}) if isinstance(verification, dict) else (docs_payload or {})
        risk_score = None
        risk_breakdown = {}

        # Build trace
        trace = {
            "applicant": {
                "id": applicant.get("id"),
                "name": applicant.get("name"),
                "credit_score": applicant.get("credit_score"),
                "salary": applicant.get("salary"),
                "pre_approved_limit": applicant.get("pre_approved_limit"),
                "city": applicant.get("city")
            },
            "offer_ctx": offer_ctx,
            "verification": verification,
            "underwriting": uw,
            "decision_details": uw["details"],
            "doc_report": doc_report,
            "risk_score": risk_score,
            "risk_breakdown": risk_breakdown,
            "ab_variant": self.ab_variant
        }

        # ensure outputs folder
        os.makedirs(out_folder, exist_ok=True)

        # Save trace to audit log
        save_decision_trace(trace, path=os.path.join(out_folder, "decision_traces.jsonl"))

        pdf_path = None
        if decision == "APPROVED":
            try:
                pdf_path = generate_sanction_pdf(applicant, trace, out_folder=os.path.join(out_folder, "sanction_letters"))
            except Exception:
                pdf_path = None

        # If conditional, add to manual review queue
        if decision == "CONDITIONAL":
            qpath = os.path.join(out_folder, "manual_review.jsonl")
            with open(qpath, "a", encoding="utf-8") as qf:
                qf.write(json.dumps(trace, ensure_ascii=False) + "\n")

        return decision, trace, pdf_path
