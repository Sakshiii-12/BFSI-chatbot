# ui/customer_page.py
import streamlit as st
from ui.theme import render_css
import pandas as pd
from agents.master_agent import MasterAgent
from chat.chat_ui import render_chat_page
from services.audit import read_traces
from agents.sanction_agent import generate_sanction_pdf
import plotly.express as px

def _kpi_donut(traces):
    counts = {"APPROVED":0, "CONDITIONAL":0, "REJECTED":0}
    for t in traces:
        d = t.get("decision_details",{}).get("final_decision","UNKNOWN")
        if d in counts:
            counts[d] += 1
    labels = list(counts.keys())
    values = list(counts.values())
    if sum(values) == 0:
        st.info("No runs yet to show KPIs.")
        return
    fig = px.pie(names=labels, values=values, hole=0.55,
                 color=labels,
                 color_discrete_map={"APPROVED":"#c6d3e3","CONDITIONAL":"#FCEFB4","REJECTED":"#E03A3A"})
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=260, showlegend=True)
    st.plotly_chart(fig, use_container_width=False)

def _render_decision_card(trace):
    d = trace.get("decision_details", {})
    dec = d.get("final_decision", "UNKNOWN")
    emi = d.get("EMI")
    emi_pct = d.get("EMI_pct_salary")
    rules = d.get("rules_fired", [])
    crm = trace.get("verification", {}).get("crm_record", {})
    doc = trace.get("verification", {}).get("doc_report", {}) or trace.get("doc_report", {})

    badge_map = {"APPROVED": "#113382", "CONDITIONAL": "#FCEFB4", "REJECTED": "#E03A3A"}
    color = badge_map.get(dec, "#666666")
    badge = dec

    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center'>", unsafe_allow_html=True)
    st.markdown(f"<div><h3 style='margin:0'>{badge}</h3><div style='color:#555;margin-top:6px'>Decision details</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{color};color:#000;padding:8px 12px;border-radius:10px;font-weight:700'>{badge}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
    st.markdown(f"<div><strong>EMI:</strong> Rs {emi}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><strong>EMI % of salary:</strong> {emi_pct}%</div>", unsafe_allow_html=True)
    if rules:
        st.markdown("<div style='margin-top:8px'><strong>Rules fired:</strong></div>", unsafe_allow_html=True)
        for r in rules:
            st.markdown(f"- {r}", unsafe_allow_html=True)

    if crm:
        st.markdown("<div style='margin-top:8px'><strong>CRM record:</strong></div>", unsafe_allow_html=True)
        for k,v in crm.items():
            st.markdown(f"- {k}: {v}", unsafe_allow_html=True)
    if doc:
        st.markdown("<div style='margin-top:8px'><strong>Doc report:</strong></div>", unsafe_allow_html=True)
        for k,v in doc.items():
            st.markdown(f"- {k}: {v}", unsafe_allow_html=True)

    if dec == "APPROVED":
        try:
            pdf_path = generate_sanction_pdf(trace.get("applicant", {}), trace, out_folder="outputs/sanction_letters")
            with open(pdf_path, "rb") as pf:
                pdf_bytes = pf.read()
            st.download_button("Download sanction letter (PDF)", pdf_bytes, file_name=pdf_path.split("/")[-1], mime="application/pdf")
        except Exception as e:
            st.warning(f"Could not generate PDF: {e}")

    st.markdown("</div></div>", unsafe_allow_html=True)

def render_customer_ui(demo_customers):
    render_css()

    # Sidebar only here (no duplication)
    st.sidebar.markdown("<div class='sidebar-header'>MENU</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div class='sidebar-sub'>Signed in as<br><strong>customer</strong></div>", unsafe_allow_html=True)
    nav = st.sidebar.radio("", ["Overview", "Compare", "Simulate", "Chat"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Sign out"):
        st.session_state['role'] = None
        st.session_state['email'] = None
        try:
            st.experimental_rerun()
        except Exception:
            pass

    left, right = st.columns([2.6, 1], gap="large")
    with left:
        st.title("Personal Loan Assistant")
        st.caption("Conversational advisory and loan simulation — clear, fast and explainable.")

        if not demo_customers:
            demo_customers = [{"id":0,"name":"Demo User","city":"","pre_approved_limit":100000,"salary":30000,"credit_score":700}]

        if nav == "Overview":
            profile = demo_customers[0]
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(profile.get("name"))
            st.write(f"{profile.get('city')} • Salary: Rs {profile.get('salary')} • Credit score: {profile.get('credit_score')}")
            st.markdown("</div>", unsafe_allow_html=True)

            traces = read_traces(limit=200)
            st.subheader("Portfolio snapshot")
            _kpi_donut(traces)

            st.subheader("Recent activity (you)")
            filtered = []
            for t in traces:
                applicant = t.get("applicant",{}).get("name","")
                if applicant == profile.get("name"):
                    d = t.get("decision_details",{})
                    filtered.append({
                        "time": d.get("timestamp","")[:19],
                        "decision": d.get("final_decision"),
                        "amount": d.get("requested_amount"),
                        "EMI": d.get("EMI")
                    })
            if filtered:
                st.table(pd.DataFrame(filtered[-8:]))
            else:
                st.info("No recent runs for this user. Use Simulate or Chat to create activity.")

        elif nav == "Compare":
            st.header("Scenario Comparison")
            names = [c["name"] for c in demo_customers]
            sel = st.selectbox("Applicant", names)
            applicant = next(c for c in demo_customers if c["name"] == sel)
            c1, c2 = st.columns(2)
            with c1:
                a1 = st.number_input("Scenario A amount (Rs)", value=applicant["pre_approved_limit"], step=10000, key="cmp_a1")
                t1 = st.selectbox("Tenure A (months)", [12,24,36,48,60,84], index=4, key="cmp_t1")
            with c2:
                a2 = st.number_input("Scenario B amount (Rs)", value=int(applicant["pre_approved_limit"]*1.5), step=10000, key="cmp_a2")
                t2 = st.selectbox("Tenure B (months)", [12,24,36,48,60,84], index=4, key="cmp_t2")
            if st.button("Run comparison"):
                agent = MasterAgent()
                dec1, trace1, _ = agent.start_chat(applicant, a1, 12.0, t1, out_folder="outputs")
                dec2, trace2, _ = agent.start_chat(applicant, a2, 12.0, t2, out_folder="outputs")
                colA, colB = st.columns(2)
                with colA:
                    _render_decision_card(trace1)
                with colB:
                    _render_decision_card(trace2)

        elif nav == "Simulate":
            st.header("Simulation")
            names = [c["name"] for c in demo_customers]
            sel = st.selectbox("Applicant", names)
            app = next(c for c in demo_customers if c["name"] == sel)
            amt = st.number_input("Requested amount (Rs)", value=app.get("pre_approved_limit"), step=10000)
            tenure = st.selectbox("Tenure (months)", [12,24,36,48,60,84], index=4)
            pan = st.text_input("PAN (optional)")
            salary_text = st.text_area("Salary slip text (optional)")
            if st.button("Run decision"):
                agent = MasterAgent()
                dec, trace, pdf = agent.start_chat(app, amt, 12.0, tenure, out_folder="outputs", docs_payload={"pan_text": pan, "salary_text": salary_text})
                _render_decision_card(trace)

        elif nav == "Chat":
            render_chat_page(demo_customers)

    with right:
        st.markdown("<div class='micro-card'>", unsafe_allow_html=True)
        st.markdown("### Quick help")
        st.markdown("- **Simulate** — Run structured loan checks: enter amount, tenure, optional PAN or salary slip text.")
        st.markdown("- **Chat** — Describe your need in natural language (e.g. 'I need 3 lakh for medical'). The assistant will compute EMI and explain the decision.")
        st.markdown("- **Compare** — Run two scenarios to compare EMI, EMI% of salary, and decision outcome.")
        st.markdown("- **Tips:** Use longer tenure to reduce EMI; lower requested amount to improve approval chances; provide salary slip text when asked.")
        st.markdown("</div>", unsafe_allow_html=True)
