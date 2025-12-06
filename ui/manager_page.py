# ui/manager_page.py
import streamlit as st
from ui.theme import render_css
import pandas as pd
from services.audit import read_traces, read_manual_queue, remove_manual_item, append_trace, traces_to_csv_bytes
import datetime
import os
import plotly.express as px

def _kpi_bar_plot(traces):
    total = len(traces)
    approvals = sum(1 for t in traces if t.get("decision_details",{}).get("final_decision") == "APPROVED")
    cond = sum(1 for t in traces if t.get("decision_details",{}).get("final_decision") == "CONDITIONAL")
    rej = sum(1 for t in traces if t.get("decision_details",{}).get("final_decision") == "REJECTED")
    if total == 0:
        st.info("No data yet")
        return
    df = pd.DataFrame({
        "status":["APPROVED","CONDITIONAL","REJECTED"],
        "count":[approvals, cond, rej]
    })
    fig = px.bar(df, x="status", y="count", color="status",
                 color_discrete_map={"APPROVED":"#113382","CONDITIONAL":"#FCEFB4","REJECTED":"#E03A3A"})
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=260, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def _render_review_item(item, idx):
    a = item.get("applicant", {})
    d = item.get("decision_details", {})
    badge_map = {"APPROVED": "#113382", "CONDITIONAL": "#FCEFB4", "REJECTED": "#E03A3A"}
    color = badge_map.get(d.get("final_decision","UNKNOWN"), "#666666")
    st.markdown(f"<div style='border:1px solid rgba(0,0,0,0.06);padding:12px;border-radius:10px;margin-bottom:8px;background:#fff'>", unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center'>", unsafe_allow_html=True)
    st.markdown(f"<div><strong>{a.get('name','Unknown')}</strong><div style='color:#666;font-size:13px'>Rs {d.get('requested_amount')}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{color};color:#000;padding:6px 10px;border-radius:8px;font-weight:700'>{d.get('final_decision')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:8px'>EMI: Rs {d.get('EMI')} ({d.get('EMI_pct_salary')}% of salary)</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:6px;font-weight:600'>Rules fired:</div>", unsafe_allow_html=True)
    for r in d.get("rules_fired", []):
        st.markdown(f"- {r}", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("Approve", key=f"mgr_app_{idx}"):
            item["manager_action"] = {"action": "APPROVED_BY_MANAGER", "by": st.session_state.get("email","manager"), "ts": datetime.datetime.utcnow().isoformat()}
            append_trace(item)
            remove_manual_item(lambda t, id=item.get("applicant",{}).get("id"): t.get("applicant",{}).get("id") == id)
            st.success("Approved and logged.")
            st.experimental_rerun()
    with col2:
        if st.button("Reject", key=f"mgr_rej_{idx}"):
            item["manager_action"] = {"action": "REJECTED_BY_MANAGER", "by": st.session_state.get("email","manager"), "ts": datetime.datetime.utcnow().isoformat()}
            append_trace(item)
            remove_manual_item(lambda t, id=item.get("applicant",{}).get("id"): t.get("applicant",{}).get("id") == id)
            st.warning("Rejected and logged.")
            st.experimental_rerun()
    with col3:
        if st.button("View JSON", key=f"mgr_view_{idx}"):
            st.json(item)
    st.markdown("</div>", unsafe_allow_html=True)

def render_manager_ui():
    render_css()
    st.sidebar.markdown("<div class='sidebar-header'>MENU</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-sub'>Signed in as<br><strong>manager</strong></div>", unsafe_allow_html=True)
    nav = st.sidebar.radio("Manager Navigation", ["Overview", "Audit", "Manual Reviews"], label_visibility="collapsed")
    st.sidebar.markdown("---")
    if st.sidebar.button("Sign out"):
        st.session_state['role'] = None
        st.session_state['email'] = None
        try:
            st.experimental_rerun()
        except Exception:
            pass

    st.title("Manager Dashboard")
    # Use a container to ensure layout won't get collapsed
    main = st.container()

    if nav == "Overview":
        with main:
            traces = read_traces(limit=500) or []
            total = len(traces)
            approvals = sum(1 for t in traces if t.get("decision_details",{}).get("final_decision") == "APPROVED")
            avg_emi_pct = round(sum((t.get("decision_details",{}).get("EMI_pct_salary") or 0) for t in traces) / (total or 1), 2)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Runs", total)
            c2.metric("Approvals", approvals)
            c3.metric("Avg EMI % salary", f"{avg_emi_pct}%")
            st.markdown("---")
            st.subheader("Operational breakdown")
            _kpi_bar_plot(traces)

            # Export controls
            st.markdown("---")
            st.subheader("Export audit log")
            if not traces:
                st.info("No traces to export")
            else:
                csv_bytes = traces_to_csv_bytes(traces)
                col1, col2 = st.columns([1,1])
                with col1:
                    st.download_button(label="Download CSV of traces", data=csv_bytes, file_name="decision_traces.csv", mime="text/csv")
                with col2:
                    jl_path = "outputs/decision_traces.jsonl"
                    if os.path.exists(jl_path):
                        with open(jl_path, "rb") as f:
                            raw = f.read()
                        st.download_button("Download JSONL (raw)", raw, file_name="decision_traces.jsonl", mime="application/json")

    elif nav == "Audit":
        with main:
            st.subheader("Audit Explorer (recent decisions)")
            traces = read_traces(limit=500) or []
            rows = []
            for t in traces[-200:]:
                d = t.get("decision_details",{}); a = t.get("applicant",{})
                rows.append({
                    "timestamp": (d.get("timestamp") or "")[:19],
                    "applicant": a.get("name"),
                    "decision": d.get("final_decision"),
                    "amount": d.get("requested_amount"),
                    "EMI": d.get("EMI"),
                    "rules": "; ".join(d.get("rules_fired",[]))
                })
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, height=420)
            else:
                st.info("No traces yet. Run simulations from the Customer side to populate the audit log.")

    elif nav == "Manual Reviews":
        with main:
            st.subheader("Manual Review Queue (Conditional cases)")
            queue = read_manual_queue() or []
            if not queue:
                st.info("No manual review items.")
            else:
                for idx, item in enumerate(queue):
                    _render_review_item(item, idx)
