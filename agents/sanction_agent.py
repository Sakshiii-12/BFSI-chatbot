# agents/sanction_agent.py
from fpdf import FPDF
import os, re
from math import ceil

def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name)

def safe_timestamp(ts: str) -> str:
    return ts.replace(":", "-").replace("+", "plus").replace("/", "-")

def amortization_schedule(P: float, annual_rate_pct: float, months: int):
    r = annual_rate_pct / 12.0 / 100.0
    if r == 0:
        emi = P / months
    else:
        emi = P * r * (1 + r)**months / ((1 + r)**months - 1)
    emi = round(emi, 2)
    schedule = []
    balance = P
    for m in range(1, months+1):
        if r == 0:
            interest = 0
            principal = emi
        else:
            interest = round(balance * r, 2)
            principal = round(emi - interest, 2)
        balance = round(max(0, balance - principal), 2)
        schedule.append({"month": m, "emi": emi, "principal": principal, "interest": interest, "balance": balance})
    return schedule

def _safe_text(t: str) -> str:
    """Return text safe for FPDF latin-1 encoding (avoid non-latin1 chars)."""
    if not isinstance(t, str):
        t = str(t)
    # replace rupee symbol and any other potentially problematic characters
    t = t.replace("₹", "Rs ")
    # optionally remove other unicode chars that FPDF may choke on
    return t.encode("latin-1", errors="replace").decode("latin-1")

def generate_sanction_pdf(applicant: dict, trace: dict, out_folder="outputs/sanction_letters", include_schedule_months=12):
    os.makedirs(out_folder, exist_ok=True)
    raw_ts = trace["decision_details"]["timestamp"]
    safe_ts = safe_timestamp(raw_ts)
    fname = f"sanction_{slugify(applicant.get('name','app'))}_{safe_ts}.pdf"
    path = os.path.join(out_folder, fname)

    P = trace["decision_details"]["requested_amount"]
    rate = trace["decision_details"].get("annual_rate_pct", 12.0)
    months = trace["decision_details"].get("tenure_months", 60)
    schedule = amortization_schedule(P, rate, months)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, _safe_text("Personal Loan Sanction Letter"), ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, _safe_text(f"Applicant: {applicant.get('name', 'N/A')} ({applicant.get('city', '')})"))
    pdf.multi_cell(0, 8, _safe_text(f"Requested Amount: Rs {P}"))
    pdf.multi_cell(0, 8, _safe_text(f"Decision: {trace['decision_details']['final_decision']}"))
    pdf.ln(4)
    pdf.multi_cell(0, 8, _safe_text("Decision Rationale:"))
    for r in trace['decision_details'].get('rules_fired', []):
        pdf.multi_cell(0, 8, _safe_text(f"- {r}"))
    pdf.ln(4)
    emi = trace['decision_details'].get('EMI')
    emi_pct = trace['decision_details'].get('EMI_pct_salary')
    pdf.multi_cell(0, 8, _safe_text(f"EMI: Rs {emi} / month (~ {emi_pct}% of salary)"))
    pdf.ln(6)

    pdf.multi_cell(0, 8, _safe_text(f"Amortization (first {include_schedule_months} months):"))
    pdf.ln(2)
    pdf.set_font("Arial", size=9)
    pdf.cell(20, 6, _safe_text("M"), border=1)
    pdf.cell(35, 6, _safe_text("EMI (Rs)"), border=1)
    pdf.cell(35, 6, _safe_text("Principal"), border=1)
    pdf.cell(35, 6, _safe_text("Interest"), border=1)
    pdf.cell(40, 6, _safe_text("Balance"), border=1)
    pdf.ln()
    for row in schedule[:include_schedule_months]:
        pdf.cell(20, 6, _safe_text(str(row["month"])), border=1)
        pdf.cell(35, 6, _safe_text(str(row["emi"])), border=1)
        pdf.cell(35, 6, _safe_text(str(row["principal"])), border=1)
        pdf.cell(35, 6, _safe_text(str(row["interest"])), border=1)
        pdf.cell(40, 6, _safe_text(str(row["balance"])), border=1)
        pdf.ln()

    pdf.ln(6)
    pdf.multi_cell(0, 8, _safe_text("This is a demo sanction letter created by the BFSi Chatbot demo."))
    pdf.output(path)
    return path
