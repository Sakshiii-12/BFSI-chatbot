# services/report_generator.py
from fpdf import FPDF
import os, re

def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name)

def generate_exec_summary(trace: dict, out_folder="outputs/executive_reports"):
    os.makedirs(out_folder, exist_ok=True)
    app = trace.get("applicant", {})
    ts = trace.get("decision_details", {}).get("timestamp", "ts")
    fname = f"exec_summary_{slugify(app.get('name','app'))}_{ts.replace(':','-')}.pdf"
    path = os.path.join(out_folder, fname)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Executive Summary — Loan Decision", ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, f"Applicant: {app.get('name')} ({app.get('city')})")
    pdf.multi_cell(0, 8, f"Requested Amount: ₹{trace['decision_details'].get('requested_amount')}")
    pdf.multi_cell(0, 8, f"Decision: {trace['decision_details'].get('final_decision')}")
    pdf.multi_cell(0, 8, f"Risk Score: {trace.get('risk_score')}")
    pdf.ln(4)
    pdf.multi_cell(0, 8, "Decision Rationale / Rules fired:")
    for r in trace['decision_details'].get('rules_fired', []):
        pdf.multi_cell(0, 8, f"- {r}")
    pdf.ln(6)
    pdf.multi_cell(0, 8, "Conversation Transcript:")
    for s in trace.get("transcript", []):
        speaker, text = s
        pdf.multi_cell(0, 6, f"{speaker.upper()}: {text}")
    pdf.output(path)
    return path
