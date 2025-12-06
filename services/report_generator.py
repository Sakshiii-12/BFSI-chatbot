# services/report_generator.py
from fpdf import FPDF
import os
import re
import unicodedata

FONT_DIR = "fonts"
UTF_FONT_FILENAME = "DejaVuSans.ttf"  # place this file at fonts/DejaVuSans.ttf for full unicode support

def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", name)

# --- Utilities for safe text output ---

def _normalize_unicode_to_ascii(s: str) -> str:
    """
    Attempt to make a readable ascii-safe version of Unicode string:
    - Replace common typographic unicode characters with ASCII equivalents.
    - Use NFKD normalization and strip diacritics as fallback.
    """
    if not isinstance(s, str):
        return str(s or "")

    # Common replacements
    replacements = {
        "\u2014": " - ",   # em dash
        "\u2013": " - ",   # en dash
        "\u2018": "'",     # left single quote
        "\u2019": "'",     # right single quote
        "\u201c": '"',     # left double quote
        "\u201d": '"',     # right double quote
        "\u2026": "...",   # ellipsis
        "\u00a0": " ",     # non-breaking space
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # NFKD normalize and drop remaining diacritics (best-effort)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))

    # Remove any control characters
    s = "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    return s

def _get_font_path():
    """
    Return path to TTF font if present in fonts directory.
    """
    font_path = os.path.join(FONT_DIR, UTF_FONT_FILENAME)
    return font_path if os.path.exists(font_path) else None

# --- PDF generation ---

def _write_multiline(pdf: FPDF, text: str, width=0):
    """
    Write multi-line text to PDF. pdf must have its font set already.
    We accept that the font may not support some characters; upstream we make best-effort conversions.
    """
    if text is None:
        return
    # Ensure string
    text = str(text)
    pdf.multi_cell(width, 8, text)

def generate_exec_summary(trace: dict, out_folder="outputs/executive_reports"):
    """
    Create an executive summary PDF for a decision trace.
    Tries to use a Unicode TTF font (if fonts/DejaVuSans.ttf exists).
    Otherwise sanitizes unicode characters to ascii-friendly equivalents.
    Returns path to generated PDF file.
    """
    os.makedirs(out_folder, exist_ok=True)
    app = trace.get("applicant", {})
    ts = trace.get("decision_details", {}).get("timestamp", "ts")
    fname = f"exec_summary_{slugify(app.get('name','app'))}_{ts.replace(':','-')}.pdf"
    path = os.path.join(out_folder, fname)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()

    # Try to use TTF Unicode font if available
    font_path = _get_font_path()
    using_unicode_font = False
    if font_path:
        try:
            # register font for unicode support (fpdf/pyfpdf supports uni=True)
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
            using_unicode_font = True
        except Exception:
            # Fall back; we'll sanitize text below
            using_unicode_font = False

    # If no unicode font available, use built-in (latin-1) Arial and sanitize text
    if not using_unicode_font:
        pdf.set_font("Arial", size=12)

    # Header
    header = "Executive Summary — Loan Decision"
    if not using_unicode_font:
        header = _normalize_unicode_to_ascii(header)
    pdf.set_font_size(14)
    pdf.cell(0, 10, header, ln=True, align="C")
    pdf.ln(6)
    pdf.set_font_size(10)

    # Helper to get sanitized text depending on font availability
    def safe(s):
        if s is None:
            return ""
        s = str(s)
        if using_unicode_font:
            return s
        return _normalize_unicode_to_ascii(s)

    # Applicant block
    pdf.set_font_size(10)
    _write_multiline(pdf, safe(f"Applicant: {app.get('name')} ({app.get('city')})"))
    _write_multiline(pdf, safe(f"Requested Amount: ₹{trace.get('decision_details', {}).get('requested_amount')}"))
    _write_multiline(pdf, safe(f"Decision: {trace.get('decision_details', {}).get('final_decision')}"))
    _write_multiline(pdf, safe(f"Risk Score: {trace.get('risk_score')}"))
    pdf.ln(4)

    # Rules fired
    pdf.set_font_size(10)
    pdf.multi_cell(0, 8, safe("Decision Rationale / Rules fired:"))
    for r in trace.get('decision_details', {}).get('rules_fired', []):
        pdf.multi_cell(0, 8, safe(f"- {r}"))
    pdf.ln(6)

    # Conversation transcript
    pdf.multi_cell(0, 8, safe("Conversation Transcript:"))
    for s in trace.get("transcript", []):
        try:
            speaker, text = s
        except Exception:
            # fallback: render the whole line
            text = str(s)
            speaker = ""
        line = f"{speaker.upper()}: {text}" if speaker else text
        pdf.multi_cell(0, 6, safe(line))

    # Save PDF
    # Ensure the directory exists
    try:
        pdf.output(path)
    except Exception as e:
        # Last-resort: try to write after aggressively sanitizing everything
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            # Aggressively sanitize entire text
            agg = []
            agg.append(_normalize_unicode_to_ascii(header))
            agg.append(_normalize_unicode_to_ascii(f"Applicant: {app.get('name')} ({app.get('city')})"))
            agg.append(_normalize_unicode_to_ascii(f"Requested Amount: ₹{trace.get('decision_details', {}).get('requested_amount')}"))
            agg.append(_normalize_unicode_to_ascii(f"Decision: {trace.get('decision_details', {}).get('final_decision')}"))
            agg.append(_normalize_unicode_to_ascii(f"Risk Score: {trace.get('risk_score')}"))
            agg.append(_normalize_unicode_to_ascii("Decision Rationale / Rules fired:"))
            for r in trace.get('decision_details', {}).get('rules_fired', []):
                agg.append(_normalize_unicode_to_ascii(f"- {r}"))
            agg.append(_normalize_unicode_to_ascii("Conversation Transcript:"))
            for s in trace.get("transcript", []):
                try:
                    sp, tx = s
                    agg.append(_normalize_unicode_to_ascii(f"{sp.upper()}: {tx}"))
                except Exception:
                    agg.append(_normalize_unicode_to_ascii(str(s)))
            for line in agg:
                pdf.multi_cell(0, 6, line)
            pdf.output(path)
        except Exception as e2:
            # re-raise a helpful error
            raise RuntimeError(f"Failed to generate PDF. First error: {e}; Fallback error: {e2}")

    return path
