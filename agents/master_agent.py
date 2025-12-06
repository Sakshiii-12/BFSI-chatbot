# agents/master_agent.py
import traceback
from datetime import datetime
from agents.verification_agent import VerificationAgent
from agents.underwriting_agent import UnderwritingAgent
try:
    from agents.sales_agent import SalesAgent
except Exception:
    SalesAgent = None
from agents.sanction_agent import generate_sanction_pdf
from services.credit_bureau import get_credit_score
from services.offer_mart import get_offers_for_applicant
from services.recommender import recommend_offers
from services.xai import compute_risk_score
from services.audit import append_trace, queue_manual_review
from services.crm_mock import get_kyc_for_id

class MasterAgent:
    def __init__(self):
        self.verifier = VerificationAgent()
        self.underwriter = UnderwritingAgent()
        self.sales = SalesAgent() if SalesAgent else None

    def start_chat(self, applicant: dict, requested_amount: float, annual_rate_percent: float, tenure_months: int, out_folder="outputs", docs_payload=None):
        """
        Orchestrates the workflow:
        - (optional) Sales agent to negotiate/offer
        - Verification agent to confirm KYC & docs
        - Credit bureau check
        - Underwriting agent for decision
        - Sanction letter generation if APPROVED
        - Audit logging and queueing conditional items for manual review

        Returns: (decision_label, trace_dict, pdf_path_or_None)
        """
        transcript = []
        try:
            # 1) Sales (optional) - produce a short sales transcript and recommended offers
            offers = get_offers_for_applicant(applicant)
            recommended = recommend_offers(applicant, offers)
            if self.sales:
                try:
                    sales_resp = self.sales.negotiate(applicant, requested_amount, recommended)
                    # sales_resp expected to be dict with "transcript" optional
                    if isinstance(sales_resp, dict):
                        sales_text = sales_resp.get("summary") or sales_resp.get("message") or "Discussed offer options."
                    else:
                        sales_text = str(sales_resp)
                except Exception:
                    sales_text = "Sales agent suggested offers."
            else:
                sales_text = f"Suggested offers: {', '.join(o['id'] for o in recommended[:2])}"
            transcript.append(("sales_agent", sales_text))

            # 2) Verification
            # Fetch CRM record (mock)
            kyc = get_kyc_for_id(applicant.get("id"))
            # Allow doc payload overrides (pan_text and salary_text) from UI simulation
            docs = docs_payload or {}
            verification_report = self.verifier.verify(applicant, kyc, docs)
            transcript.append(("verification_agent", f"Verification result: {verification_report.get('status')}"))

            # integrate verified salary into applicant copy if doc provided
            applicant_copy = dict(applicant)  # shallow copy
            # Prefer CRM salary if exists, else extracted from docs
            if verification_report.get("salary_extracted"):
                applicant_copy["salary"] = verification_report["salary_extracted"]
            elif applicant_copy.get("salary") is None and kyc and kyc.get("salary"):
                applicant_copy["salary"] = kyc.get("salary")

            # 3) Credit bureau
            if not applicant_copy.get("credit_score"):
                try:
                    score = get_credit_score(applicant.get("id"), applicant_copy)
                    applicant_copy["credit_score"] = score
                except Exception:
                    applicant_copy["credit_score"] = applicant_copy.get("credit_score", 700)

            transcript.append(("credit_bureau", f"Credit score: {applicant_copy.get('credit_score')}"))

            # 4) Underwriting decision
            decision_label, decision_details = self.underwriter.evaluate(applicant_copy, requested_amount, annual_rate_percent, tenure_months)
            transcript.append(("underwriting_agent", f"Decision: {decision_details.get('final_decision')}"))

            # 5) XAI / risk scoring
            try:
                risk = compute_risk_score(applicant_copy, decision_details)
            except Exception:
                risk = {"score": None, "breakdown": {}}

            # Assemble trace
            trace = {
                "applicant": applicant_copy,
                "transcript": transcript,
                "verification": verification_report,
                "decision_details": decision_details,
                "risk_score": risk.get("score"),
                "xai": risk.get("breakdown")
            }

            # 6) Persist trace to audit log
            try:
                append_trace(trace)
            except Exception:
                # swallow to avoid breaking UI; but include in trace an audit_error
                trace["_audit_error"] = "failed to append trace"

            # 7) If conditional, queue for manual review
            if decision_details.get("final_decision") == "CONDITIONAL":
                try:
                    queue_manual_review(trace)
                except Exception:
                    trace["_manual_queue_error"] = "failed to queue for manual review"

            # 8) If approved, produce sanction document
            pdf_path = None
            if decision_details.get("final_decision") == "APPROVED":
                try:
                    pdf_path = generate_sanction_pdf(applicant_copy, trace, out_folder=out_folder)
                except Exception as e:
                    # bubble up on PDF generation (UI will show message). store exception in trace
                    trace["_pdf_error"] = str(e)

            return decision_label, trace, pdf_path

        except Exception as e:
            # In case of unexpected error, return a rejected trace and raise for UI to show
            tb = traceback.format_exc()
            trace = {
                "applicant": applicant,
                "transcript": transcript,
                "decision_details": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "final_decision": "ERROR",
                    "requested_amount": requested_amount
                },
                "error": str(e),
                "traceback": tb
            }
            try:
                append_trace(trace)
            except Exception:
                pass
            raise
